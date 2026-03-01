from typing import Dict, Any, List

def init_character(name: str) -> Dict[str, Any]:
    """Initialize a new character with default stats"""
    return {
        "name": name,
        "narrative_momentum": 0.0,
        "total_actions": 0,
        "creative_actions": 0,
        "imagination_history": [],
        "preferred_signals": {},
        "last_action_time": None
    }

def update_from_action(character: Dict[str, Any], imagination_score: float, signals: List[str]):
    """Update character stats based on their action"""
    character["total_actions"] += 1
    
    # Track imagination history (keep last 20)
    character["imagination_history"].append(imagination_score)
    if len(character["imagination_history"]) > 20:
        character["imagination_history"] = character["imagination_history"][-20:]
    
    # Update creative action count
    if imagination_score > 0.4:
        character["creative_actions"] += 1
    
    # Track preferred signals
    for signal in signals:
        character["preferred_signals"][signal] = character["preferred_signals"].get(signal, 0) + 1
    
    # Update narrative momentum (running average of recent imagination)
    recent = character["imagination_history"][-5:]  # Last 5 actions
    character["narrative_momentum"] = sum(recent) / len(recent) if recent else 0.0
