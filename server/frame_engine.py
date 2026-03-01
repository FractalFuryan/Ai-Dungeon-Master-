from typing import List, Dict, Any
import random

FRAME_LIBRARY = {
    "straight": {
        "name": "Straightforward",
        "description": "The action proceeds as expected",
        "wonder": 0.2,
        "risk": 0.2,
        "momentum_cost": 0.0,
        "prompt_hint": "Narrate the straightforward outcome, then offer 2 logical next steps."
    },
    "hidden_cost": {
        "name": "Hidden Cost",
        "description": "Success comes with an unexpected price",
        "wonder": 0.4,
        "risk": 0.4,
        "momentum_cost": 0.1,
        "prompt_hint": "Reveal a complication or cost to the success. Offer 2-3 paths forward."
    },
    "unexpected_ally": {
        "name": "Unexpected Ally",
        "description": "Help arrives from an unexpected quarter",
        "wonder": 0.6,
        "risk": 0.3,
        "momentum_cost": 0.2,
        "prompt_hint": "Introduce a helpful NPC or circumstance. Show how they assist."
    },
    "moral_inversion": {
        "name": "Moral Inversion",
        "description": "The situation reveals an ethical complication",
        "wonder": 0.7,
        "risk": 0.5,
        "momentum_cost": 0.3,
        "prompt_hint": "Complicate the morality of the situation. Offer nuanced choices."
    },
    "foreshadowing": {
        "name": "Foreshadowing",
        "description": "A hint of future events or deeper truths",
        "wonder": 0.8,
        "risk": 0.2,
        "momentum_cost": 0.4,
        "prompt_hint": "Reveal a clue about larger events. Keep it mysterious but meaningful."
    },
    "lateral_escape": {
        "name": "Lateral Escape",
        "description": "A clever alternative to direct confrontation",
        "wonder": 0.5,
        "risk": 0.6,
        "momentum_cost": 0.2,
        "prompt_hint": "The situation allows for an unconventional solution. Describe it."
    }
}

def get_available_frames(session_memory: Dict[str, Any]) -> List[str]:
    """Get frames available based on session state"""
    available = list(FRAME_LIBRARY.keys())
    
    # Remove recently used frames to encourage variety
    recent_outcomes = session_memory.get("recent_outcomes", [])
    if len(recent_outcomes) >= 2:
        # Try to avoid repeating the last two frames
        for frame in recent_outcomes[-2:]:
            if frame in available and len(available) > 2:
                available.remove(frame)
    
    return available

def select_frame(
    session_memory: Dict[str, Any],
    player_momentum: float,
    imagination_score: float,
    rails_detected: bool
) -> Dict[str, Any]:
    """
    Select the most appropriate narrative frame.
    Returns the selected frame data.
    """
    available = get_available_frames(session_memory)
    
    # Score each available frame
    scored_frames = []
    for frame_key in available:
        frame = FRAME_LIBRARY[frame_key]
        
        # Base scoring formula
        score = 0.0
        
        # Player momentum favors high-wonder frames
        score += frame["wonder"] * (0.7 + player_momentum * 0.5)
        
        # Imagination favors riskier, more interesting frames
        score += frame["risk"] * imagination_score * 0.6
        
        # If railroading detected, favor high-wonder frames
        if rails_detected:
            score += frame["wonder"] * 1.2
        
        # Cost adjustment (higher cost frames are used less often)
        score -= frame["momentum_cost"] * 0.3
        
        # Random variation to prevent predictability
        score += random.uniform(-0.1, 0.1)
        
        scored_frames.append((score, frame_key, frame))
    
    # Select best frame
    scored_frames.sort(key=lambda x: x[0], reverse=True)
    _, best_key, best_frame = scored_frames[0]
    
    # Add metadata
    selected_frame = best_frame.copy()
    selected_frame["key"] = best_key
    selected_frame["selection_score"] = scored_frames[0][0]
    
    # Log selection rationale
    rationale = []
    if rails_detected:
        rationale.append("rails detected")
    if player_momentum > 0.7:
        rationale.append("high momentum")
    if imagination_score > 0.6:
        rationale.append("creative input")
    
    selected_frame["selection_rationale"] = ", ".join(rationale) if rationale else "balanced"
    
    return selected_frame
