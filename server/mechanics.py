import random
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class RandomnessMode(Enum):
    SECURE = "secure"
    DETERMINISTIC = "det"
    WEIGHTED = "weighted"
    LINEAR = "linear"


@dataclass
class RollResult:
    total: int
    rolls: List[int]
    modifier: float
    natural_roll: int
    is_critical: bool = False


class DiceSystem:
    """3d6 resolution core with modifier caps."""

    def __init__(self, mode: RandomnessMode = RandomnessMode.SECURE, seed: Optional[str] = None):
        self.mode = mode
        if mode == RandomnessMode.DETERMINISTIC and seed:
            random.seed(seed)

    def roll_3d6(self) -> Tuple[int, List[int]]:
        if self.mode == RandomnessMode.SECURE:
            rolls = [secrets.randbelow(6) + 1 for _ in range(3)]
        elif self.mode == RandomnessMode.DETERMINISTIC:
            rolls = [random.randint(1, 6) for _ in range(3)]
        elif self.mode == RandomnessMode.WEIGHTED:
            rolls = [self._weighted_d6() for _ in range(3)]
        else:
            rolls = [3, 4, 3]

        return sum(rolls), rolls

    def _weighted_d6(self) -> int:
        r = secrets.randbelow(100)
        if r < 20:
            return 1
        if r < 40:
            return 6
        return secrets.choice([2, 3, 4, 5])

    def resolve(
        self,
        base_modifier: float = 0,
        positives: Optional[List[float]] = None,
        negatives: Optional[List[float]] = None,
    ) -> RollResult:
        positives = sorted(positives or [], reverse=True)[:3]
        negatives = sorted(negatives or [], reverse=True)[:3]

        total_modifier = base_modifier + sum(positives) - sum(negatives)
        total_modifier = max(-3.0, min(3.0, total_modifier))

        natural_total, rolls = self.roll_3d6()
        final_total = int(round(natural_total + total_modifier))
        is_critical = natural_total in (3, 18)

        return RollResult(
            total=final_total,
            rolls=rolls,
            modifier=total_modifier,
            natural_roll=natural_total,
            is_critical=is_critical,
        )


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
        legacy_features = banked_xp // 1000

        return {
            "banked_xp": banked_xp,
            "multiplier": multiplier,
            "legacy_features": legacy_features,
            "remaining_xp": banked_xp % 1000,
        }


dice = DiceSystem()


def quick_resolve(
    base_modifier: float = 0,
    positives: Optional[List[float]] = None,
    negatives: Optional[List[float]] = None,
) -> RollResult:
    return dice.resolve(base_modifier, positives, negatives)
