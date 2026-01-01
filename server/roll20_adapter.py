"""
Roll20 Integration Adapter

This module handles commands from Roll20 games via the relay pattern.
Provides AI narration while respecting Roll20's dice authority.

Key principles:
- Roll20 owns dice, sheets, tokens, and turn tracker
- AI DM provides narration, memory, personas, and turn discipline
- All communication via chat commands (!aidm)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

router = APIRouter()


class Roll20Event(BaseModel):
    """Incoming command from Roll20 via relay"""
    campaign_id: str
    player_name: str
    player_id: str | None = None
    text: str
    selected: list[str] = []
    ts: int | None = None


def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize player input to prevent prompt injection and spam.
    
    Args:
        text: Raw player input
        max_length: Maximum allowed length
        
    Returns:
        Cleaned text safe for prompts
    """
    if len(text) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")
    
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    return text.strip()


@router.post("/roll20/command")
async def roll20_command(evt: Roll20Event):
    """
    Process a command from Roll20.
    
    Returns:
        - chat: Text to post in Roll20 chat
        - roll: Roll20-native roll command (e.g., "/roll 1d20+5")
        - whisper: GM-only message
    """
    
    # Create namespaced session ID for Roll20 campaigns
    session_id = f"roll20:{evt.campaign_id}"
    
    # Sanitize input
    try:
        clean_text = sanitize_input(evt.text)
    except ValueError as e:
        return {
            "chat": f"<b>Error:</b> {str(e)}"
        }
    
    # Import here to avoid circular dependencies
    from .memory import get_memory, update_memory
    from .llm import generate_narration_with_persona
    
    memory = get_memory(session_id)
    
    # === PERSONA COMMAND ===
    if clean_text.startswith("persona"):
        parts = clean_text.split(maxsplit=1)
        if len(parts) < 2:
            return {
                "chat": "<b>Usage:</b> !aidm persona [name] (e.g., classic, gothic, whimsical)"
            }
        
        persona = parts[1].lower()
        valid_personas = ["classic", "gothic", "whimsical", "noir", "cosmic", "tavern"]
        
        if persona not in valid_personas:
            return {
                "chat": f"<b>Unknown persona.</b> Try: {', '.join(valid_personas)}"
            }
        
        memory["persona"] = persona
        update_memory(session_id, memory)
        
        return {
            "chat": f"<b>🎭 DM persona changed to <em>{persona}</em></b>"
        }
    
    # === ROLL COMMAND ===
    if clean_text.startswith("roll"):
        skill = clean_text.replace("roll", "").strip()
        
        # If token selected, use its stats
        if evt.selected:
            token_id = evt.selected[0]
            skill_attr = skill.lower().replace(" ", "_") if skill else "dexterity"
            return {
                "roll": f"/roll 1d20 + @{{{token_id}|{skill_attr}_mod}} for {skill or 'check'}"
            }
        
        # Generic roll without token
        return {
            "roll": f"/roll 1d20 for {skill or 'check'}"
        }
    
    # === TURN QUEUE COMMAND ===
    if clean_text in ["myturn", "my turn"]:
        turn_queue = memory.get("turn_queue", [])
        
        if evt.player_name not in turn_queue:
            turn_queue.append(evt.player_name)
            memory["turn_queue"] = turn_queue
            update_memory(session_id, memory)
            
            position = len(turn_queue)
            return {
                "chat": f"<b>✋ {evt.player_name}</b> added to turn queue (position {position})"
            }
        else:
            return {
                "chat": f"<b>{evt.player_name}</b> is already in the queue"
            }
    
    # === NEXT TURN COMMAND (GM only - could add permission check) ===
    if clean_text == "next":
        turn_queue = memory.get("turn_queue", [])
        
        if not turn_queue:
            return {
                "chat": "<em>Turn queue is empty</em>"
            }
        
        current_speaker = turn_queue.pop(0)
        memory["turn_queue"] = turn_queue
        update_memory(session_id, memory)
        
        remaining = f" ({len(turn_queue)} remaining)" if turn_queue else ""
        return {
            "chat": f"<b>🎤 {current_speaker}'s turn</b>{remaining}"
        }
    
    # === NARRATIVE COMMAND (default) ===
    # Generate AI narration for player action
    persona = memory.get("persona", "classic")
    
    # Build context-aware prompt
    prompt = f"""You are narrating a Roll20 tabletop RPG game.

Player: {evt.player_name}
Action: "{clean_text}"

Provide vivid narration in response. Keep it under 80 words.

IMPORTANT:
- Do NOT roll dice (Roll20 handles that)
- Do NOT make mechanical decisions
- Focus on narrative description, atmosphere, and consequences
- Respect player agency
"""
    
    try:
        result = generate_narration_with_persona(session_id, prompt, persona)
        
        # Style the response for Roll20 chat
        narration = result.get('text', '')
        styled_narration = f"<div style='font-style: italic; color: #8B4513; padding: 8px; background: rgba(139,69,19,0.1); border-left: 3px solid #8B4513;'>{narration}</div>"
        
        return {
            "chat": styled_narration
        }
        
    except Exception as e:
        return {
            "chat": f"<b>AI DM Error:</b> {str(e)}",
            "whisper": f"Technical details: {repr(e)}"
        }


@router.get("/roll20/health")
async def health_check():
    """Simple health check endpoint for Roll20 integration"""
    return {
        "status": "ok",
        "integration": "roll20",
        "version": "1.0.0"
    }
