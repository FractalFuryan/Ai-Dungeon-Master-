from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session


@dataclass
class LegacyFeature:
    feature_id: str
    character_name: str
    feature_type: str
    description: str
    mechanical_effect: Dict
    location_id: Optional[str]


class LegacyEngine:
    """Manages retirement banking and active legacy features."""

    def __init__(self, db: Session, world_id: str):
        self.db = db
        self.world_id = world_id
        self.xp_per_legacy = 1000
        self.underdog_multiplier = 1.2
        self.gifted_multiplier = 0.8

    def calculate_retirement(self, xp: int, is_underdog: bool = False, is_gifted: bool = False) -> Dict:
        multiplier = 1.0
        if is_underdog:
            multiplier = self.underdog_multiplier
        elif is_gifted:
            multiplier = self.gifted_multiplier

        banked_xp = int(xp * multiplier)
        return {
            "banked_xp": banked_xp,
            "multiplier": multiplier,
            "legacy_features": banked_xp // self.xp_per_legacy,
            "remaining_xp": banked_xp % self.xp_per_legacy,
        }

    def create_legacy(
        self,
        character_id: str,
        feature_type: str,
        description: str,
        location_id: Optional[str] = None,
    ) -> str:
        from server.models import Character, Cycle
        from server.persistence.models import LegacyLedgerV2

        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")

        cycle = self.db.query(Cycle).filter(Cycle.id == character.cycle_id).first()
        world_id = cycle.world_id if cycle else self.world_id

        retirement = self.calculate_retirement(
            int(character.xp or 0),
            is_underdog=bool(getattr(character, "is_underdog", False)),
            is_gifted=bool(getattr(character, "is_gifted", False)),
        )
        if retirement["legacy_features"] < 1:
            raise ValueError(f"Character needs {self.xp_per_legacy} XP for a legacy feature")

        legacy = LegacyLedgerV2(
            world_id=world_id,
            character_id=character_id,
            entry_type=feature_type,
            description=description,
            location_id=location_id,
            active=True,
            mechanical_effect={
                "feature_type": feature_type,
                "xp_contributed": retirement["banked_xp"],
                "features_created": retirement["legacy_features"],
            },
        )
        self.db.add(legacy)

        # Compatible retirement markers with existing schema.
        character.status = "retired"
        if hasattr(character, "retired_at"):
            character.retired_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(legacy)
        return legacy.id

    def get_active_legacies(self, location_id: Optional[str] = None) -> List[LegacyFeature]:
        from server.models import Character
        from server.persistence.models import LegacyLedgerV2

        query = (
            self.db.query(LegacyLedgerV2, Character)
            .join(Character, LegacyLedgerV2.character_id == Character.id)
            .filter(LegacyLedgerV2.world_id == self.world_id, LegacyLedgerV2.active.is_(True))
        )
        if location_id:
            query = query.filter(LegacyLedgerV2.location_id == location_id)

        output: List[LegacyFeature] = []
        for legacy, character in query.all():
            output.append(
                LegacyFeature(
                    feature_id=legacy.id,
                    character_name=character.name,
                    feature_type=legacy.entry_type,
                    description=legacy.description,
                    mechanical_effect=legacy.mechanical_effect or {},
                    location_id=legacy.location_id,
                )
            )
        return output

    def apply_legacy_effects(self, character_id: str, action_context: Dict) -> Dict:
        from server.models import Character
        from server.persistence.models import LegacyLedgerV2

        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return {"applied_effects": []}

        location_id = action_context.get("location_id")
        query = self.db.query(LegacyLedgerV2).filter(
            LegacyLedgerV2.world_id == self.world_id,
            LegacyLedgerV2.active.is_(True),
        )
        if location_id:
            query = query.filter(LegacyLedgerV2.location_id == location_id)

        effects = []
        for legacy in query.all():
            if self._is_relevant(legacy, action_context):
                effects.append(self._apply_effect(legacy, action_context))

        return {"applied_effects": effects}

    def _is_relevant(self, legacy: object, context: Dict) -> bool:
        return True

    def _apply_effect(self, legacy: object, context: Dict) -> Dict:
        return {"legacy_id": legacy.id, "effect": legacy.mechanical_effect or {}}
