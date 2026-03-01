"""
VoiceDM Dice System

Implements standard RPG dice rolling with randomness integration.
"""

import re
from typing import Dict, List, Optional, Any
from enum import Enum
from .randomness import get_session_rng, RandomSource


class RollMode(str, Enum):
    """How to interpret dice rolls"""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"
    EXPLODING = "exploding"


class DiceResult:
    """Result of a dice roll with full detail"""
    
    def __init__(
        self,
        expression: str,
        total: int,
        rolls: List[int],
        faces: List[int],
        mode: RollMode = RollMode.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.expression = expression
        self.total = total
        self.rolls = rolls
        self.faces = faces
        self.mode = mode
        self.metadata = metadata or {}
        
        # Calculate statistics
        self.average = sum(rolls) / len(rolls) if rolls else 0
        self.min_roll = min(rolls) if rolls else 0
        self.max_roll = max(rolls) if rolls else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "expression": self.expression,
            "total": self.total,
            "rolls": self.rolls,
            "faces": self.faces,
            "mode": self.mode,
            "statistics": {
                "average": round(self.average, 2),
                "min": self.min_roll,
                "max": self.max_roll
            },
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        """Human-readable representation"""
        if len(self.rolls) == 1:
            return f"{self.total} (d{self.faces[0]})"
        
        rolls_str = ", ".join(str(r) for r in self.rolls)
        return f"{self.total} [{rolls_str}]"


class DiceSystem:
    """Main dice rolling system"""
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize dice system for a session"""
        self.session_id = session_id
        self.rng = get_session_rng(session_id) if session_id else RandomSource()
        self.roll_history: List[DiceResult] = []
    
    def roll_die(self, sides: int) -> int:
        """Roll a single die"""
        return self.rng.randint(1, sides)
    
    def roll(self, expression: str) -> DiceResult:
        """
        Roll dice based on expression.
        
        Supports: d20, 2d6+3, d20 advantage, etc.
        """
        expression = expression.lower().strip()
        
        # Detect roll mode
        mode = RollMode.NORMAL
        if "disadvantage" in expression:
            mode = RollMode.DISADVANTAGE
            expression = expression.replace("disadvantage", "").strip()
        elif "advantage" in expression:
            mode = RollMode.ADVANTAGE
            expression = expression.replace("advantage", "").strip()
        elif "disadv" in expression:
            mode = RollMode.DISADVANTAGE
            expression = expression.replace("disadv", "").strip()
        elif "adv" in expression:
            mode = RollMode.ADVANTAGE
            expression = expression.replace("adv", "").strip()
        
        # Parse dice expression: [count]d[sides][+/-modifier]
        expression = re.sub(r'\s+', '', expression)
        
        # Simple pattern: d20, 2d6, 3d8+2, etc.
        pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        match = re.match(pattern, expression)
        
        if not match:
            raise ValueError(f"Invalid dice expression: {expression}")
        
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Roll dice
        rolls = []
        faces = []
        
        if mode == RollMode.ADVANTAGE:
            # Roll twice, take higher
            roll1 = self.roll_die(sides)
            roll2 = self.roll_die(sides)
            rolls = [roll1, roll2]
            faces = [sides, sides]
            total = max(roll1, roll2) + modifier
        elif mode == RollMode.DISADVANTAGE:
            # Roll twice, take lower
            roll1 = self.roll_die(sides)
            roll2 = self.roll_die(sides)
            rolls = [roll1, roll2]
            faces = [sides, sides]
            total = min(roll1, roll2) + modifier
        else:
            # Normal roll
            for _ in range(count):
                roll = self.roll_die(sides)
                rolls.append(roll)
                faces.append(sides)
            total = sum(rolls) + modifier
        
        # Check for critical (d20 only)
        metadata = {}
        if sides == 20:
            if 20 in rolls:
                metadata["critical"] = True
                metadata["critical_type"] = "success"
            elif 1 in rolls:
                metadata["critical"] = True
                metadata["critical_type"] = "failure"
        
        result = DiceResult(
            expression=expression,
            total=total,
            rolls=rolls,
            faces=faces,
            mode=mode,
            metadata=metadata
        )
        
        self.roll_history.append(result)
        return result
    
    def get_history(self, limit: int = 10) -> List[DiceResult]:
        """Get recent roll history"""
        return self.roll_history[-limit:] if self.roll_history else []


def quick_roll(expression: str, session_id: Optional[str] = None) -> DiceResult:
    """Quick roll without creating DiceSystem instance"""
    dice_system = DiceSystem(session_id)
    return dice_system.roll(expression)


# Legacy function for backwards compatibility
def roll_dice(dice_type: str, modifier: int = 0) -> dict:
    """Legacy dice rolling function"""
    result = quick_roll(f"{dice_type}{modifier:+}" if modifier != 0 else dice_type)
    return {"roll": result.rolls[0] if result.rolls else 0, "total": result.total, "logged": True}

