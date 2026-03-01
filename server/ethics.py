import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def detect_railroading(actions: List[str], outcomes: List[str], threshold: int = 3) -> Dict[str, Any]:
    """
    Detect potential railroading patterns in recent actions/outcomes.
    Returns analysis dict with warnings if detected.
    """
    if len(actions) < threshold or len(outcomes) < threshold:
        return {"detected": False, "warning": None, "confidence": 0.0}
    
    # Check for repetitive outcomes despite varied actions
    recent_actions = actions[-threshold:]
    recent_outcomes = outcomes[-threshold:]
    
    unique_actions = len(set(recent_actions))
    unique_outcomes = len(set(recent_outcomes))
    
    # High action variety with low outcome variety suggests railroading
    action_variety = unique_actions / threshold
    outcome_variety = unique_outcomes / threshold
    
    confidence = (action_variety - outcome_variety) * 0.8
    
    if confidence > 0.3:
        warning = (
            f"⚠️ PATTERN DETECTED: Players tried {unique_actions} different approaches "
            f"but got only {unique_outcomes} distinct outcomes. "
            f"Consider offering more branching possibilities."
        )
        
        # Suggest specific improvements
        suggestions = [
            "Allow a 'yes, and...' outcome next time",
            "Introduce an unexpected consequence",
            "Reveal hidden information the players missed",
            "Let a failed roll lead to interesting complications"
        ]
        
        return {
            "detected": True,
            "warning": warning,
            "confidence": min(confidence, 1.0),
            "action_variety": action_variety,
            "outcome_variety": outcome_variety,
            "suggestions": suggestions[:2]
        }
    
    return {"detected": False, "warning": None, "confidence": 0.0}

def validate_player_input(text: str) -> Dict[str, Any]:
    """
    Validate player input for safety and appropriateness.
    Returns validation result dict.
    """
    issues = []
    
    # Basic validation
    if not text or len(text.strip()) == 0:
        return {"valid": False, "issues": ["Empty input"], "sanitized": ""}
    
    if len(text) > 500:
        issues.append(f"Input too long ({len(text)} chars, max 500)")
    
    # Check for potential issues (basic content moderation)
    problematic_patterns = [
        (r"\b(hack|exploit|cheat|bypass)\s+(system|game|dice|roll)", "Attempting to manipulate game systems"),
        (r"\b(dox|personal info|address|phone|real name)\b", "Sharing personal information"),
        (r"\b(racist|sexist|homophobic|transphobic)\b", "Discriminatory language"),
        (r"<script|javascript:|onload=|onerror=", "Potential XSS attempt"),
    ]
    
    for pattern, description in problematic_patterns:
        if re.search(pattern, text.lower()):
            issues.append(description)
    
    # Sanitize (basic)
    sanitized = text[:500].strip()  # Simple truncation for now
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "sanitized": sanitized
    }
