from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import logging
import uuid
import os
import pathlib
from dotenv import load_dotenv
from .llm import generate_narration, PERSONAS
from .dice import roll_dice
from .memory import get_memory, update_memory
from .dm_engine import process_action
from .database import init_db, save_campaign, load_campaign, list_campaigns
from .roll20_adapter import router
from .config import settings

load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VoiceDM Roll20 Harmony",
    description="Adaptive AI Dungeon Master for Roll20",
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# === Initialize database on startup ===
@app.on_event("startup")
async def startup_event():
    init_db()

# In-memory sessions for WebSocket support (legacy)
sessions = {}
connections = {}  # session_id -> list of websockets

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the relay interface"""
    html_content = """
    <!doctype html>
    <html>
    <head>
        <title>VoiceDM Roll20 Relay</title>
        <style>
            body {
                background: #0f0f12;
                color: #eaeaf0;
                font-family: 'Segoe UI', system-ui, sans-serif;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #333;
                padding-bottom: 20px;
            }
            .card {
                background: #15151b;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid #333;
            }
            textarea, input {
                width: 100%;
                background: #1a1a22;
                color: #eaeaf0;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Monaco', 'Menlo', monospace;
            }
            button {
                padding: 12px 24px;
                border-radius: 8px;
                background: #4a4aff;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: background 0.2s;
            }
            button:hover {
                background: #5a5aff;
            }
            pre {
                white-space: pre-wrap;
                background: #1a1a22;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #333;
                max-height: 500px;
                overflow-y: auto;
            }
            .status {
                padding: 10px;
                border-radius: 6px;
                margin: 10px 0;
            }
            .status.ok {
                background: #1a331a;
                border: 1px solid #2a5a2a;
            }
            .status.error {
                background: #331a1a;
                border: 1px solid #5a2a2a;
            }
            code {
                background: #2a2a33;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Monaco', 'Menlo', monospace;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚔️ VoiceDM Roll20 Relay</h1>
            <p>Adaptive AI Dungeon Master Interface</p>
        </div>
        
        <div class="card">
            <h3>📤 Process Roll20 Queue</h3>
            <p>Backend URL:</p>
            <input id="backend" value="http://localhost:8000/api/v1/roll20/command_batch">
            
            <p>Paste AIDM_QUEUE JSON:</p>
            <textarea id="queue" rows="6" placeholder='[{"campaign_id": "...", "player_name": "...", "text": "..."}]'></textarea>
            
            <div style="margin: 15px 0;">
                <button onclick="processQueue()">Process Queue</button>
                <button onclick="testConnection()" style="background: #333; margin-left: 10px;">Test Connection</button>
            </div>
            
            <div id="status"></div>
        </div>
        
        <div class="card">
            <h3>📝 Output (Copy to Roll20)</h3>
            <pre id="output">Output will appear here...</pre>
        </div>
        
        <div class="card">
            <h3>ℹ️ How to Use</h3>
            <ol>
                <li>In Roll20, players use <code>!aidm [action]</code></li>
                <li>GM uses <code>!aidm_dump</code> to get JSON</li>
                <li>Paste JSON above and click Process</li>
                <li>Copy output back to Roll20 chat</li>
            </ol>
            <p><small>Version 1.2.0 | Session-aware | Anti-railroad detection</small></p>
        </div>
        
        <script>
            async function testConnection() {
                const backend = document.getElementById('backend').value;
                const status = document.getElementById('status');
                
                try {
                    const response = await fetch(backend.replace('/command_batch', '/health'));
                    if (response.ok) {
                        status.innerHTML = '<div class="status ok">✅ Backend connected successfully</div>';
                    } else {
                        status.innerHTML = '<div class="status error">❌ Backend error: ' + response.status + '</div>';
                    }
                } catch (error) {
                    status.innerHTML = '<div class="status error">❌ Cannot connect to backend: ' + error.message + '</div>';
                }
            }
            
            async function processQueue() {
                const backend = document.getElementById('backend').value;
                const queueInput = document.getElementById('queue').value;
                const output = document.getElementById('output');
                const status = document.getElementById('status');
                
                output.textContent = 'Processing...';
                status.innerHTML = '';
                
                try {
                    const events = JSON.parse(queueInput);
                    
                    const response = await fetch(backend, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ events })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    
                    // Format output
                    let formattedOutput = '';
                    data.outputs.forEach(item => {
                        if (typeof item === 'object' && item.chat) {
                            formattedOutput += item.chat + '\\n\\n';
                            if (item.debug) {
                                formattedOutput += '--- DEBUG ---\\n';
                                formattedOutput += JSON.stringify(item.debug, null, 2) + '\\n\\n';
                            }
                        } else {
                            formattedOutput += item + '\\n\\n';
                        }
                    });
                    
                    output.textContent = formattedOutput || 'No output generated';
                    status.innerHTML = '<div class="status ok">✅ Processed ' + events.length + ' events</div>';
                    
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                    status.innerHTML = '<div class="status error">❌ Processing failed</div>';
                    console.error('Processing error:', error);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from .hybrid_engine import get_narration_stats
    
    narration_info = get_narration_stats()
    
    return {
        "status": "healthy",
        "service": "VoiceDM Roll20 Harmony",
        "version": "1.3.0",  # Bumped for featherweight update
        "narration_mode": narration_info["mode"],
        "dependencies": {
            "openai": narration_info["llm_available"],
            "templates": True,
            "total_required": narration_info["dependencies_required"]
        },
        "default_persona": settings.default_persona,
        "template_library": {
            "frames": narration_info["template_stats"]["frames"],
            "tones": narration_info["template_stats"]["tones"],
            "variations": narration_info["template_stats"]["total_text_variations"]
        }
    }

@app.get("/stats")
async def get_stats():
    """Get service statistics (protected in production)"""
    from .memory import _MEM
    return {
        "active_sessions": len(_MEM),
        "session_ids": list(_MEM.keys())[:10]  # First 10 only
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# === Legacy WebSocket Support (for non-Roll20 clients) ===

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
