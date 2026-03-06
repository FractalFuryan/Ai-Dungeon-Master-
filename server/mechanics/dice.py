import logging
import random
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RandomnessMode(Enum):
    SECURE = "secure"
    DETERMINISTIC = "det"
    WEIGHTED = "weighted"
    LINEAR = "linear"


@dataclass
class RollResult:
    """Structured result object for 3d6 resolution."""

    rolls: List[int]
    total: int
    modifier: int
    critical: bool
    mode: RandomnessMode
    metadata: Optional[dict] = None

    @property
    def natural_total(self) -> int:
        return sum(self.rolls)

    @property
    def natural_roll(self) -> int:
        # Backward-compatible alias used by existing endpoints/tests.
        return self.natural_total

    @property
    def is_critical_success(self) -> bool:
        return self.rolls == [6, 6, 6]

    @property
    def is_critical_failure(self) -> bool:
        return self.rolls == [1, 1, 1]

    @property
    def is_critical(self) -> bool:
        # Backward-compatible alias used by existing endpoints/tests.
        return self.critical

    def to_dict(self) -> Dict[str, object]:
        return {
            "rolls": self.rolls,
            "total": self.total,
            "modifier": self.modifier,
            "critical": self.critical,
            "mode": self.mode.value,
            "natural_total": self.natural_total,
        }


class DiceEngine:
    """Core 3d6 engine with multiple randomness modes."""

    def __init__(self, mode: RandomnessMode = RandomnessMode.SECURE, seed: Optional[str] = None):
        self.mode = mode
        self.seed = seed
        self._rng = random.Random(seed) if mode == RandomnessMode.DETERMINISTIC else random.Random()
        if mode == RandomnessMode.DETERMINISTIC:
            logger.info("Initialized deterministic RNG")

    def roll_3d6(self) -> List[int]:
        if self.mode == RandomnessMode.SECURE:
            return [secrets.randbelow(6) + 1 for _ in range(3)]
        if self.mode == RandomnessMode.DETERMINISTIC:
            return [self._rng.randint(1, 6) for _ in range(3)]
        if self.mode == RandomnessMode.WEIGHTED:
            return self._weighted_roll()
        return [self._rng.randint(1, 6) for _ in range(3)]

    def _weighted_roll(self) -> List[int]:
        # Light bell-curve weight on sums 3..9 then mirrored to 18.
        weights = [1, 2, 3, 4, 3, 2, 1]
        target_sum = random.choices(range(3, 10), weights=weights, k=1)[0]
        mirror = secrets.randbelow(2) == 1
        if mirror:
            target_sum = 21 - target_sum
        return self._decompose_sum(target_sum)

    def _decompose_sum(self, target_sum: int) -> List[int]:
        remaining = target_sum
        rolls: List[int] = []
        for idx in range(2):
            min_val = max(1, remaining - 6 * (2 - idx))
            max_val = min(6, remaining - (2 - idx))
            if min_val > max_val:
                return [self._rng.randint(1, 6) for _ in range(3)]
            value = self._rng.randint(min_val, max_val)
            rolls.append(value)
            remaining -= value
        if 1 <= remaining <= 6:
            rolls.append(remaining)
            return rolls
        return [self._rng.randint(1, 6) for _ in range(3)]

    def calculate_modifier(
        self,
        base_modifier: int,
        positives: List[int],
        negatives: List[int],
        max_mod: int = 3,
        min_mod: int = -3,
    ) -> int:
        raw = int(base_modifier + sum(positives) - sum(negatives))
        return max(min_mod, min(max_mod, raw))

    def resolve(
        self,
        base_modifier: int = 0,
        positives: Optional[List[int]] = None,
        negatives: Optional[List[int]] = None,
        metadata: Optional[dict] = None,
    ) -> RollResult:
        positives = positives or []
        negatives = negatives or []
        rolls = self.roll_3d6()
        modifier = self.calculate_modifier(base_modifier, positives, negatives)
        total = sum(rolls) + modifier
        result = RollResult(
            rolls=rolls,
            total=total,
            modifier=modifier,
            critical=(rolls == [1, 1, 1] or rolls == [6, 6, 6]),
            mode=self.mode,
            metadata=metadata,
        )
        logger.debug("Roll resolved: %s", result.to_dict())
        return result
