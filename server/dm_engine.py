import logging
import math
from typing import Dict, Any, List
from .memory import SessionMemory, cleanup_old_sessions
from .character import init_character, update_from_action
from .resonance import analyze_imagination
from .frame_engine import select_frame, FRAME_LIBRARY
from .ethics import detect_railroading, validate_player_input
from .hybrid_engine import generate_narrative  # NEW: Hybrid system
from .config import settings

logger = logging.getLogger(__name__)


def _ensure_geomancer_state(memory: Dict[str, Any]) -> Dict[str, Any]:
    geomancer = memory.setdefault("geomancer", {})
    geomancer.setdefault("C", 0.0)
    geomancer.setdefault("D", 0.0)
    geomancer.setdefault("T", 0.0)
    geomancer.setdefault("H", 0.0)
    geomancer.setdefault("drift", 0.0)
    geomancer.setdefault("equilibrium", 1.0)
    geomancer.setdefault("instability", 0.0)
    geomancer.setdefault("history", [])
    memory.setdefault("geomancer_enabled", True)
    return geomancer


def classify_action(text: str):
    text = text.lower()

    coop_markers = ["help", "assist", "support", "together", "protect"]
    chaos_markers = ["kill", "burn", "explode", "betray", "steal"]

    C_i = sum(1 for w in coop_markers if w in text)
    D_i = sum(1 for w in chaos_markers if w in text)

    if C_i > D_i:
        return "coop", C_i, D_i
    if D_i > C_i:
        return "disrupt", C_i, D_i
    return "neutral", C_i, D_i


def update_geomancer(mem: Dict[str, Any], text: str) -> float:
    g = _ensure_geomancer_state(mem)

    action_type, C_i, D_i = classify_action(text)

    # Relevance (scene overlap)
    scene_words = set(mem.get("scene", "").lower().split())
    text_words = text.lower().split()
    R_i = sum(1 for w in text_words if w in scene_words)

    alpha, beta, gamma = 1.0, 1.2, 1.5
    U = alpha * R_i + gamma * C_i - beta * D_i

    # Update C and D (slow accumulation)
    g["C"] = 0.8 * g["C"] + C_i
    g["D"] = 0.8 * g["D"] + D_i

    # Update tension
    lambda_decay, delta_disruption, mu_coop = 0.85, 0.5, 0.4
    g["T"] = lambda_decay * g["T"] + delta_disruption * g["D"] - mu_coop * g["C"]

    # Track history for entropy
    g["history"].append(action_type)
    g["history"] = g["history"][-20:]

    counts = {
        "coop": g["history"].count("coop"),
        "disrupt": g["history"].count("disrupt"),
        "neutral": g["history"].count("neutral"),
    }
    total = sum(counts.values())
    H = 0.0
    if total > 0:
        for v in counts.values():
            if v > 0:
                p = v / total
                H -= p * math.log(p)
    g["H"] = H

    # Long-term campaign drift and party equilibrium/instability
    eta = 0.05
    g["drift"] += eta * (g["C"] - g["D"])
    balance_gap = abs(g["C"] - g["D"])
    g["equilibrium"] = 1.0 / (1.0 + balance_gap)
    g["instability"] = max(0.0, g["D"] - g["C"]) + max(0.0, g["T"]) + g["H"]

    return U

def process_roll20_event(
    session_id: str,
    player_name: str,
    text: str,
    selected: List[str]
) -> Dict[str, Any]:
    """
    Process a single Roll20 event and generate response.
    Returns dict with 'chat' and/or 'roll' keys.
    """
    # Clean up old sessions periodically
    if hash(session_id) % 10 == 0:  # Roughly 10% of calls
        cleanup_old_sessions()
    
    # Validate input
    validation = validate_player_input(text)
    if not validation["valid"]:
        logger.warning(f"Invalid input from {player_name}: {validation['issues']}")
        return {
            "chat": f"⚠️ <i>Input issue: {validation['issues'][0]}</i>",
            "debug": {"validation_issues": validation["issues"]}
        }
    
    text = validation["sanitized"]
    session = SessionMemory(session_id)
    memory = session.get()
    _ensure_geomancer_state(memory)
    
    # Handle special commands
    if text.lower().startswith("persona "):
        new_persona = text.split(" ", 1)[1].strip()
        if new_persona in ["classic", "gothic", "whimsical", "scifi"]:
            memory["persona"] = new_persona
            return {
                "chat": f"🎭 <b>Persona switched to {new_persona}</b>",
                "debug": {"persona_changed": new_persona}
            }
        else:
            return {
                "chat": "⚠️ <i>Unknown persona. Use: classic, gothic, whimsical, scifi</i>",
                "debug": {"invalid_persona": new_persona}
            }
    
    if text.lower().startswith("roll "):
        # Simple dice roll command
        roll_cmd = text[5:].strip()
        # Basic sanitization for roll commands
        safe_roll = "".join(c for c in roll_cmd if c.isalnum() or c in "d+-*/ ()")
        return {
            "roll": f"/roll {safe_roll}",
            "debug": {"roll_command": safe_roll}
        }

    if text.lower().startswith("geomancer"):
        parts = text.lower().split()
        if len(parts) == 1 or parts[1] == "status":
            geom = memory["geomancer"]
            enabled = memory.get("geomancer_enabled", True)
            return {
                "chat": (
                    f"🧭 <b>Geomancer:</b> {'ON' if enabled else 'OFF'} | "
                    f"C={geom['C']:.2f}, D={geom['D']:.2f}, T={geom['T']:.2f}, H={geom['H']:.2f}, "
                    f"Drift={geom['drift']:.2f}, Eq={geom['equilibrium']:.2f}, Instab={geom['instability']:.2f}"
                ),
                "debug": {"geomancer": geom, "geomancer_enabled": enabled}
            }

        if parts[1] in ["on", "off"]:
            enabled = parts[1] == "on"
            memory["geomancer_enabled"] = enabled
            return {
                "chat": f"🧭 <b>Geomancer Full Mode {'enabled' if enabled else 'disabled'}</b>",
                "debug": {"geomancer_enabled": enabled}
            }

        return {
            "chat": "⚠️ <i>Usage: geomancer [on|off|status]</i>",
            "debug": {"invalid_geomancer_command": text}
        }
    
    if text.lower() == "myturn":
        # Utility-weighted turn management
        turn_queue = memory.get("turn_queue", [])
        turn_scores = memory.setdefault("turn_scores", {})
        if player_name not in turn_queue:
            turn_queue.append(player_name)

        utility = update_geomancer(memory, text) if memory.get("geomancer_enabled", True) else 0.0
        turn_scores[player_name] = utility
        turn_queue = sorted(turn_queue, key=lambda p: turn_scores.get(p, 0.0), reverse=True)

        memory["turn_queue"] = turn_queue
        memory["active_player"] = turn_queue[0] if turn_queue else None
        return {
            "chat": f"<b>Turn order:</b> {', '.join(turn_queue)}",
            "debug": {
                "turn_queued": player_name,
                "turn_queue": turn_queue,
                "turn_scores": {k: round(v, 2) for k, v in turn_scores.items()}
            }
        }
    
    if text.lower() == "scene":
        # Return current scene
        return {
            "chat": f"📜 <b>Current Scene:</b> {memory['scene'][:200]}...",
            "debug": {"scene_request": True}
        }
    
    # Normal action processing
    players = memory["players"]
    if player_name not in players:
        players[player_name] = init_character(player_name)
    
    # Analyze imagination
    imagination_score, imagination_signals = analyze_imagination(text)

    geom_score = None
    if memory.get("geomancer_enabled", True):
        geom_score = update_geomancer(memory, text)

    geom = memory["geomancer"]
    tone_modifier = ""
    if geom["T"] > 5:
        tone_modifier = "The world feels unstable, tension crackling in the air."
    elif geom["C"] > geom["D"] * 2 and geom["C"] > 0:
        tone_modifier = "The party moves with rare unity and confidence."
    elif geom["H"] > 1.0:
        tone_modifier = "Events feel unpredictable, the future uncertain."
    
    # Update character stats
    update_from_action(players[player_name], imagination_score, imagination_signals)
    
    # Detect railroading
    rail_analysis = detect_railroading(
        memory.get("recent_actions", []),
        memory.get("recent_outcomes", [])
    )
    
    # Select narrative frame
    player_momentum = players[player_name].get("narrative_momentum", 0.0)
    selected_frame = select_frame(
        memory,
        player_momentum,
        imagination_score,
        rail_analysis["detected"]
    )
    
    # Build LLM prompt
    prompt = f"""
SCENE: {memory['scene']}
PLAYER ACTION: {text}
PLAYER STYLE: {', '.join(imagination_signals) if imagination_signals else 'direct action'}
FRAME: {selected_frame['name']} - {selected_frame['description']}
FRAME HINT: {selected_frame['prompt_hint']}
TONE MODIFIER: {tone_modifier or 'none'}

{"⚠️ GM NOTE: Recent actions have shown creative variety - ensure outcomes match this creativity." if rail_analysis["detected"] else ""}

Narrate what happens next. Then offer 2-4 meaningful choices for the players.
Write in the style of a {memory['persona']} dungeon master.
"""
    
    # Generate response using hybrid engine (templates or LLM based on config)
    response_text = generate_narrative(
        frame_key=selected_frame["key"],
        tone=memory["persona"],
        scene_context=f"{memory['scene']}\n\n{tone_modifier}" if tone_modifier else memory["scene"],
        player_action=text,
        imagination_signals=imagination_signals
    )
    
    # Update memory with this interaction
    memory["recent_actions"].append(text[:100])  # Store truncated
    memory["recent_outcomes"].append(selected_frame["key"])
    session.update_scene(f"After '{text[:50]}...': {response_text[:100]}...")
    
    # Record stats
    session.record_action(player_name, text, selected_frame["key"], imagination_score)
    
    # Prepare response
    response = {
        "chat": f"<b>🎭 {selected_frame['name']}:</b> {response_text}"
    }

    if tone_modifier:
        response["chat"] += f"\n\n<i>{tone_modifier}</i>"
    
    # Add debug info for GM
    debug_info = {
        "imagination_score": round(imagination_score, 2),
        "imagination_signals": imagination_signals,
        "frame_selected": selected_frame["key"],
        "frame_score": round(selected_frame.get("selection_score", 0), 2),
        "player_momentum": round(player_momentum, 2),
        "rail_detected": rail_analysis["detected"],
        "session_actions": memory["session_stats"]["total_actions"],
        "avg_imagination": round(memory["session_stats"]["avg_imagination"], 2),
        "geomancer_enabled": memory.get("geomancer_enabled", True),
        "geomancer_utility": round(geom_score, 2) if geom_score is not None else None,
        "geomancer_C": round(geom["C"], 2),
        "geomancer_D": round(geom["D"], 2),
        "geomancer_T": round(geom["T"], 2),
        "geomancer_H": round(geom["H"], 2),
        "geomancer_drift": round(geom["drift"], 2),
        "geomancer_equilibrium": round(geom["equilibrium"], 2),
        "geomancer_instability": round(geom["instability"], 2)
    }
    
    if rail_analysis["detected"]:
        debug_info["rail_warning"] = rail_analysis["warning"]
        response["chat"] += f"\n\n⚠️ <i>GM Note: {rail_analysis['warning']}</i>"
    
    response["debug"] = debug_info
    
    return response


# Legacy compatibility
TURN_CLAIM_PHRASES = ["my turn", "me", "i go", "next", "i'm next", "i act", "my action"]

def is_turn_claim(text: str) -> bool:
    lower = text.lower().strip()
    return any(phrase in lower for phrase in TURN_CLAIM_PHRASES)

def process_action(session_id: str, player_name: str, action_text: str):
    """
    Legacy compatibility function for websocket-based processing.
    For Roll20 integration, use process_roll20_event instead.
    """
    from .llm import generate_narration_with_persona
    from .memory import get_memory, update_memory

    # Import here to avoid circular imports
    from .main import sessions, connections
    
    state = sessions[session_id]["state"]
    memory = get_memory(session_id)
    persona_key = memory.get("persona", "classic")
    
    active = state.get("active_player")
    queue = state.get("turn_queue", [])

    # Check if player is claiming turn
    if is_turn_claim(action_text):
        if player_name not in queue and player_name != active:
            queue.append(player_name)
            state["turn_queue"] = queue
            
            # Auto-advance if queue was empty and no one active
            if not active and queue:
                new_active = queue.pop(0)
                state["active_player"] = new_active
                state["turn_queue"] = queue
                
                # Notify all
                import asyncio
                async def broadcast_turn():
                    for conn in connections.get(session_id, []):
                        try:
                            await conn.send_json({
                                "type": "turn_update",
                                "active_player": new_active,
                                "queue": queue[:5],
                                "text": f"It's {new_active}'s turn!"
                            })
                        except:
                            pass
                
                # Safe async call
                try:
                    asyncio.create_task(broadcast_turn())
                except:
                    pass
                
                return {
                    "type": "system",
                    "text": f"{new_active}, you're up!"
                }
            
            return {
                "type": "system",
                "text": f"{player_name} added to turn queue (#{len(queue)})."
            }

    # Only active player gets full narration
    if active and player_name != active:
        return {
            "type": "whisper",
            "text": f"(Noted, {player_name}. Waiting for {active}'s action...)"
        }

    # Active player action (or freeform if no one has turn)
    recent = memory.get("recent_actions", [])[-4:]
    players = ", ".join(memory.get("players", [])) or "The heroes"
    
    prompt = f"""
Current scene: {memory.get("scene", "A mysterious tavern")}
Players: {players}
Active player: {active or "anyone"}
Recent actions: {" | ".join(recent) if recent else "None yet"}
{player_name} says: "{action_text}"

Narrate the outcome in character. Keep under 100 words.
"""
    
    result = generate_narration_with_persona(session_id, prompt, persona_key)
    
    # Update recent actions
    new_actions = recent + [f"{player_name}: {action_text}"]
    memory["recent_actions"] = new_actions[-5:]
    update_memory(session_id, "recent_actions", memory["recent_actions"])

    return {
        "type": "narration",
        "text": result["text"],
        "audio_base64": result["audio_base64"],
        "active_player": active,
        "persona_name": result["persona_name"]
    }
