from dataclasses import dataclass
import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CharacterStatsView:
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    @classmethod
    def from_character(cls, character: Any) -> "CharacterStatsView":
        # Legacy Character ORM does not yet enforce explicit stat fields.
        return cls(
            strength=int(getattr(character, "strength", 10)),
            dexterity=int(getattr(character, "dexterity", 10)),
            constitution=int(getattr(character, "constitution", 10)),
            intelligence=int(getattr(character, "intelligence", 10)),
            wisdom=int(getattr(character, "wisdom", 10)),
            charisma=int(getattr(character, "charisma", 10)),
        )

    def average(self) -> float:
        return (
            self.strength
            + self.dexterity
            + self.constitution
            + self.intelligence
            + self.wisdom
            + self.charisma
        ) / 6.0


class ReverenceEngine:
    BASE_XP = 1000
    GIFTED_THRESHOLD = 15
    UNDERDOG_THRESHOLD = 11

    def calculate_xp_required(self, character_stats: CharacterStatsView) -> int:
        if character_stats.average() >= self.GIFTED_THRESHOLD:
            return int(self.BASE_XP * 0.8)
        return self.BASE_XP

    def calculate_xp_gain(self, character_stats: CharacterStatsView, action_difficulty: float, success: bool) -> Tuple[int, Optional[Dict[str, Any]]]:
        xp = int(10 * float(action_difficulty))
        if success:
            xp = int(xp * 1.5)

        stat_avg = character_stats.average()
        event: Optional[Dict[str, Any]] = None

        if stat_avg <= self.UNDERDOG_THRESHOLD and success:
            xp = int(xp * 1.2)
            event = {
                "type": "underdog_success",
                "reverence_delta": 0.1,
                "description": "Against all odds, you succeed!",
            }
        elif stat_avg >= self.GIFTED_THRESHOLD and success and action_difficulty > 1.5:
            event = {
                "type": "gifted_strain",
                "reverence_delta": -0.2,
                "description": "Your gift exacts a toll.",
            }

        return xp, event

    def process_reverence_token(self, token_id: str, token_type: str) -> Dict[str, Any]:
        effects = {
            "reroll": "Reroll any dice",
            "plus_one": "+1 to any roll",
            "symbol_manifest": "Manifest a symbol in reality",
            "critical_shift": "Turn success into critical success",
        }

        if token_type not in effects:
            raise ValueError(f"Unknown token type: {token_type}")

        return {
            "token_id": token_id,
            "token_type": token_type,
            "effect": effects[token_type],
            "used": True,
        }

    def calculate_retirement_deposit(self, character_stats: CharacterStatsView, total_xp: int) -> Dict[str, Any]:
        stat_avg = character_stats.average()
        deposit = int(total_xp)

        if stat_avg <= self.UNDERDOG_THRESHOLD:
            multiplier = 1.2
            reason = "Underdog's struggle echoes through generations"
        elif stat_avg >= self.GIFTED_THRESHOLD:
            multiplier = 0.8
            reason = "Gifted power fades, leaving less mark on the world"
        else:
            multiplier = 1.0
            reason = "Standard legacy deposit"

        deposit = int(deposit * multiplier)
        return {
            "total_xp": total_xp,
            "deposit": deposit,
            "multiplier": multiplier,
            "legacy_features": deposit // 1000,
            "reason": reason,
        }


class StrainEngine:
    def __init__(self):
        self.strain_thresholds = {
            "veil_propagation": 3.0,
            "dream_logic": 5.0,
            "reality_break": 8.0,
        }

    def calculate_strain(self, action_context: Dict[str, Any], character_stats: CharacterStatsView) -> float:
        strain = 0.0

        if action_context.get("critical_success") and character_stats.average() >= 15:
            strain += 0.5
        if action_context.get("magic_item_used"):
            strain += 0.3
        if action_context.get("director_intervention"):
            strain += 1.0

        symbol_count = int(action_context.get("active_symbols", 0))
        if symbol_count > 2:
            strain += 0.2 * (symbol_count - 2)

        return strain

    def check_thresholds(self, current_strain: float) -> Dict[str, Dict[str, float]]:
        triggered: Dict[str, Dict[str, float]] = {}
        for effect, threshold in self.strain_thresholds.items():
            if current_strain >= threshold:
                triggered[effect] = {
                    "threshold": threshold,
                    "current": current_strain,
                }
        return triggered

    def apply_strain_effects(self, current_strain: float) -> Dict[str, Any]:
        effects: Dict[str, Any] = {}

        if current_strain >= self.strain_thresholds["veil_propagation"]:
            effects["veil_propagation_rate"] = 1.0 + (current_strain * 0.1)
            effects["veil_effect"] = "The veil thins as reality strains"
        if current_strain >= self.strain_thresholds["dream_logic"]:
            effects["dream_logic_active"] = True
            effects["dream_intensity"] = min(1.0, current_strain / 10.0)
        if current_strain >= self.strain_thresholds["reality_break"]:
            effects["reality_break_chance"] = 0.1 * (current_strain - 8.0)
            effects["reality_effect"] = "Reality fractures at the edges"

        return effects
