from typing import List, Optional

from .dice import DiceEngine, RandomnessMode, RollResult


class DiceSystem(DiceEngine):
    """Backward-compatible API for legacy tests/routes."""

    def roll_3d6(self):
        rolls = super().roll_3d6()
        return sum(rolls), rolls


class Governors:
    @staticmethod
    def check_2_to_1_anchor(recent_mundane_anchors: int) -> bool:
        return recent_mundane_anchors >= 2

    @staticmethod
    def propagate_silence(veil_nodes: List[dict], delta: float) -> List[dict]:
        for node in veil_nodes:
            node["silence_level"] = float(node.get("silence_level", 0.0)) + delta
        return veil_nodes

    @staticmethod
    def ripen_currents(open_currents: List[dict], delta: float = 0.1) -> List[dict]:
        ripened = []
        for current in open_currents:
            current["intensity"] = float(current.get("intensity", 0.0)) + delta
            if current["intensity"] >= 1.0 and not current.get("triggered"):
                current["triggered"] = True
                ripened.append(current)
        return ripened

    @staticmethod
    def calculate_retirement_multiplier(xp: int, is_underdog: bool = False, is_gifted: bool = False) -> dict:
        if is_underdog:
            multiplier = 1.2
        elif is_gifted:
            multiplier = 0.8
        else:
            multiplier = 1.0
        banked_xp = int(xp * multiplier)
        return {
            "banked_xp": banked_xp,
            "multiplier": multiplier,
            "legacy_features": banked_xp // 1000,
            "remaining_xp": banked_xp % 1000,
        }


_dice = DiceEngine()


def quick_resolve(
    base_modifier: float = 0,
    positives: Optional[List[float]] = None,
    negatives: Optional[List[float]] = None,
) -> RollResult:
    # Preserve old signature while using the new engine.
    int_pos = [int(p) for p in (positives or [])]
    int_neg = [int(n) for n in (negatives or [])]
    return _dice.resolve(int(base_modifier), int_pos, int_neg)


dice = _dice

__all__ = [
    "DiceSystem",
    "DiceEngine",
    "RandomnessMode",
    "RollResult",
    "Governors",
    "quick_resolve",
    "dice",
]
