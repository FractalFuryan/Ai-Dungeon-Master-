from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
import uuid

from server.engine.legacy_ledger_engine import LegacyFeatureType, LegacyLedgerEngine

logger = logging.getLogger(__name__)


class RetirementEngine:
    def __init__(self, ledger_engine: LegacyLedgerEngine):
        self.ledger = ledger_engine
        self.retirement_history: List[Dict[str, Any]] = []

    def perform_retirement(
        self,
        character: Any,
        player_id: str,
        final_act_description: str,
        chosen_feature_type: Optional[LegacyFeatureType] = None,
        chosen_location: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.info("RETIREMENT RITUAL STARTED for %s", character.name)

        if int(getattr(character, "xp", 0)) < 1000:
            return {
                "success": False,
                "error": "Character needs at least 1000 XP to retire",
                "xp_needed": 1000 - int(getattr(character, "xp", 0)),
            }

        entry = self.ledger.retire_character(
            character_name=character.name,
            player_id=player_id,
            xp_remaining=int(getattr(character, "xp", 0)),
            level=int(getattr(character, "level", 1)),
            final_act=final_act_description,
            gifted=bool(getattr(character, "is_gifted", False)),
            underdog=bool(getattr(character, "is_underdog", False)),
            campaign_id=campaign_id,
        )

        if chosen_feature_type and entry.features_created:
            last_feature = entry.features_created[-1]
            last_feature.feature_type = chosen_feature_type
            if chosen_feature_type == LegacyFeatureType.VILLAGE:
                last_feature.name = f"{character.name}'s Haven"
            elif chosen_feature_type == LegacyFeatureType.ARTIFACT:
                last_feature.name = f"{character.name}'s Legacy"
            elif chosen_feature_type == LegacyFeatureType.BLOODLINE:
                last_feature.name = f"Bloodline of {character.name}"

        if chosen_location and entry.features_created:
            entry.features_created[0].location_id = chosen_location

        ritual_record = {
            "id": str(uuid.uuid4()),
            "character_name": character.name,
            "player_id": player_id,
            "final_act": final_act_description,
            "timestamp": datetime.utcnow().isoformat(),
            "features_created": len(entry.features_created),
            "ledger_entry_id": entry.id,
        }
        self.retirement_history.append(ritual_record)

        narrative = self._generate_ritual_narrative(character, entry, final_act_description)
        logger.info("RETIREMENT RITUAL COMPLETE for %s", character.name)

        return {
            "success": True,
            "ritual": "retirement",
            "character": character.name,
            "final_act": final_act_description,
            "ledger_entry": {
                "id": entry.id,
                "xp_banked": entry.xp_banked,
                "reverence_points": entry.reverence_points,
                "multiplier": entry.multiplier,
                "features": [
                    {
                        "name": f.name,
                        "type": f.feature_type.value,
                        "description": f.description,
                        "effect": f.mechanical_effect,
                    }
                    for f in entry.features_created
                ],
            },
            "narrative": narrative,
            "world_now_contains": len(self.ledger.features),
            "ritual_record": ritual_record,
        }

    def _generate_ritual_narrative(self, character: Any, entry: Any, final_act: str) -> str:
        lines = [f"THE RETIREMENT OF {character.name.upper()}", ""]
        lines.append(f"As the party gathers, {character.name} speaks their final words:")
        lines.append(f'"{final_act}"')
        lines.append("")

        if entry.reverence_points > 3:
            lines.append("The very fabric of reality shimmers as profound reverence is etched into memory.")
            lines.append("This legend will echo through generations.")
        elif entry.reverence_points > 1:
            lines.append("The world accepts this sacrifice, weaving it into the tapestry of myth.")
        else:
            lines.append("A quiet mark is left upon the world. Small, but permanent.")

        lines.append("")
        lines.append(f"LEDGER UPDATED: {entry.reverence_points} reverences recorded")
        lines.append("")
        lines.append("THE WORLD NOW CONTAINS:")
        for feature in entry.features_created:
            lines.append(f"  - {feature.name}: {feature.description}")

        return "\n".join(lines)

    def preview_retirement(self, character: Any) -> Dict[str, Any]:
        multiplier = self.ledger._deposit_multiplier(
            bool(getattr(character, "is_gifted", False)),
            bool(getattr(character, "is_underdog", False)),
        )
        current_xp = int(getattr(character, "xp", 0))
        adjusted_xp = int(current_xp * multiplier)
        reverence_points = adjusted_xp // self.ledger.FEATURE_XP_COST

        return {
            "character": getattr(character, "name", "unknown"),
            "current_xp": current_xp,
            "multiplier": multiplier,
            "banked_xp": adjusted_xp,
            "reverence_points": reverence_points,
            "features_will_create": reverence_points,
            "eligible": current_xp >= 1000,
        }

    def get_retirement_history(self, count: int = 10) -> List[Dict[str, Any]]:
        return self.retirement_history[-count:]
