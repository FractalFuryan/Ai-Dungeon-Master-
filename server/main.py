from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uuid
import os
from dotenv import load_dotenv
from .llm import generate_narration
from .dice import roll_dice
from .memory import get_memory, update_memory
from .dm_engine import process_action
from .database import init_db, save_campaign, load_campaign, list_campaigns
from .roll20_adapter import router as roll20_router

load_dotenv()

app = FastAPI()

# === Roll20 Integration ===
app.include_router(roll20_router, prefix="/roll20", tags=["roll20"])

# === CORS for Codespaces (critical) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Initialize database on startup ===
@app.on_event("startup")
async def startup_event():
    init_db()

# In-memory sessions
sessions = {}
connections = {}  # session_id -> list of websockets

@app.post("/session/create")
async def create_session():
    session_id = str(uuid.uuid4())[:8]  # shorter for QR
    sessions[session_id] = {
        "memory": {
            "scene": "A dimly lit tavern filled with the murmur of adventurers.",
            "players": [],
            "recent_actions": [],
            "persona": "classic"
        },
        "state": {
            "active_player": None,
            "turn_queue": [],
            "phase": "exploration"
        }
    }
    connections[session_id] = []
    return {"session_id": session_id}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    if session_id not in sessions:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()
    connections[session_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "join":
                player_name = data.get("player_name", "Adventurer")
                sessions[session_id]["memory"]["players"].append(player_name)
            
            elif data["type"] == "voice_input":
                action_text = data["text"]
                player_name = data.get("player_name", "Unknown")
                
                result = process_action(session_id, player_name, action_text)
                
                # Broadcast to all players in session
                dead_connections = []
                for conn in connections[session_id]:
                    try:
                        await conn.send_json(result)
                    except:
                        dead_connections.append(conn)
                for dead in dead_connections:
                    connections[session_id].remove(dead)
    except WebSocketDisconnect:
        if websocket in connections.get(session_id, []):
            connections[session_id].remove(websocket)

@app.post("/session/set_persona")
async def set_persona(session_id: str, persona: str):
    if session_id not in sessions:
        return {"error": "Invalid session"}
    # Get valid personas from llm module
    from .llm import PERSONAS
    if persona not in PERSONAS:
        return {"error": "Invalid persona"}
    sessions[session_id]["memory"]["persona"] = persona
    # Broadcast update so clients can reflect it
    for conn in connections.get(session_id, []):
        try:
            await conn.send_json({"type": "persona_update", "persona": persona})
        except:
            pass
    return {"success": True}

@app.post("/session/next_turn")
async def next_turn(session_id: str, player_name: str = None):
    if session_id not in sessions:
        return {"error": "Invalid session"}
    
    queue = sessions[session_id]["state"]["turn_queue"]
    if player_name:
        if player_name not in queue:
            queue.append(player_name)
    
    # Advance to next
    if queue:
        new_active = queue.pop(0)
        sessions[session_id]["state"]["active_player"] = new_active
        sessions[session_id]["state"]["turn_queue"] = queue
        
        # Broadcast turn change
        for conn in connections.get(session_id, []):
            try:
                await conn.send_json({
                    "type": "turn_update",
                    "active_player": new_active,
                    "queue": queue[:5]
                })
            except:
                pass
        return {"active_player": new_active, "queue": queue}
    return {"active_player": None}

@app.post("/campaign/save")
async def save_campaign_endpoint(session_id: str, campaign_name: str):
    """Save current session state as a campaign"""
    if session_id not in sessions:
        return {"error": "Invalid session"}
    
    try:
        save_data = {
            "memory": sessions[session_id]["memory"],
            "state": sessions[session_id]["state"]
        }
        # Generate unique campaign ID (not the session ID) to support multiple sessions from one campaign
        campaign_id = f"cmp_{session_id}_{uuid.uuid4().hex[:4]}"
        save_campaign(campaign_id, campaign_name, save_data)
        
        # Broadcast save confirmation
        for conn in connections.get(session_id, []):
            try:
                await conn.send_json({"type": "system", "text": f"📜 Campaign saved as: {campaign_name}"})
            except:
                pass
        
        return {"success": True, "campaign_id": campaign_id, "campaign_name": campaign_name}
    except AssertionError as e:
        return {"error": f"Save failed: {str(e)}"}

@app.post("/campaign/load")
async def load_campaign_endpoint(campaign_id: str):
    """Load a saved campaign into a new live session"""
    data = load_campaign(campaign_id)
    if not data:
        return {"error": "Campaign not found"}
    
    try:
        # Create new live session from saved data
        new_session_id = str(uuid.uuid4())[:8]
        sessions[new_session_id] = {
            "memory": data.get("memory", {}),
            "state": data.get("state", {"active_player": None, "turn_queue": [], "phase": "exploration"})
        }
        connections[new_session_id] = []
        
        return {
            "session_id": new_session_id,
            "campaign_name": data.get("memory", {}).get("campaign_name", "Loaded Campaign")
        }
    except Exception as e:
        return {"error": f"Load failed: {str(e)}"}

@app.get("/campaign/list")
async def list_campaigns_endpoint():
    """List all saved campaigns"""
    campaigns = list_campaigns()
    return {"campaigns": campaigns}

@app.post("/dice/roll")
async def dice_roll(session_id: str, dice_type: str = "d20", modifier: int = 0):
    if session_id not in sessions:
        return {"error": "Invalid session"}
    result = roll_dice(dice_type, modifier)
    update_memory(session_id, "last_roll", result)
    return result

# Serve client statically from backend (best for Codespaces)
app.mount("/", StaticFiles(directory="../client", html=True), name="static")
