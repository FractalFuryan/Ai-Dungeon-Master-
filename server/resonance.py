import re
from typing import List, Tuple

def analyze_imagination(text: str) -> Tuple[float, List[str]]:
    """Analyze text for creative/imaginative elements"""
    text_lower = text.lower()
    score = 0.0
    signals = []
    
    # Length indicates elaboration
    if len(text) > 100:
        score += 0.3
        signals.append("detailed")
    elif len(text) > 60:
        score += 0.2
        signals.append("elaborate")
    
    # Creative signals
    creative_phrases = [
        (["what if", "imagine", "suppose"], 0.4, "hypothetical"),
        (["instead of", "rather than", "alternative"], 0.3, "alternative"),
        (["because", "so that", "in order to"], 0.2, "purposeful"),
        (["risk", "gamble", "bet"], 0.3, "risky"),
        (["improv", "adapt", "wing it"], 0.4, "adaptive"),
        (["hidden", "secret", "concealed"], 0.3, "discovery"),
        (["decoy", "distract", "misdirect"], 0.4, "tactical"),
        (["hack", "bypass", "workaround"], 0.3, "clever")
    ]
    
    for phrases, points, signal in creative_phrases:
        if any(phrase in text_lower for phrase in phrases):
            score += points
            if signal not in signals:
                signals.append(signal)
    
    # Metaphor/simile detection
    metaphor_patterns = [r"like a", r"as if", r"as though", r"similar to"]
    for pattern in metaphor_patterns:
        if re.search(pattern, text_lower):
            score += 0.5
            if "metaphoric" not in signals:
                signals.append("metaphoric")
            break
    
    # Dialogue inclusion
    if '"' in text or "'" in text:
        score += 0.2
        signals.append("dialogue")
    
    # Question asking
    if text.strip().endswith("?"):
        score += 0.1
        signals.append("inquisitive")
    
    # Cap at 1.0
    score = min(score, 1.0)
    
    # Ensure at least basic score for participation
    if score < 0.1 and len(text.strip()) > 5:
        score = 0.1
        signals.append("participatory")
    
    return score, signals
