from .llm import generate_narration_with_persona
from .memory import get_memory, update_memory

TURN_CLAIM_PHRASES = ["my turn", "me", "i go", "next", "i'm next", "i act", "my action"]

def is_turn_claim(text: str) -> bool:
    lower = text.lower().strip()
    return any(phrase in lower for phrase in TURN_CLAIM_PHRASES)

def process_action(session_id: str, player_name: str, action_text: str):
    """
    Process a player action with turn enforcement.
    - If player is claiming turn, add to queue
    - Only active player gets full narration
    - Others get whisper response
    """
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
