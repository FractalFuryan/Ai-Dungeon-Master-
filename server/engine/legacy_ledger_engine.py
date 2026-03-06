from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)


class LegacyFeatureType(str, Enum):
    VILLAGE = "village"
    ARTIFACT = "artifact"
    CURSE = "curse"
    BLESSING = "blessing"
    BLOODLINE = "bloodline"
    LOCATION = "location"
    RITUAL = "ritual"
    TITLE = "title"
    LANDMARK = "landmark"
    TRADITION = "tradition"


@dataclass
class LegacyFeature:
    id: str
    character_name: str
    player_id: str
    feature_type: LegacyFeatureType
    name: str
    description: str
    mechanical_effect: Dict[str, Any]
    location_id: Optional[str]
    created_at: datetime
    active: bool = True
    referenced_in_campaigns: List[str] = field(default_factory=list)

    def reference(self, campaign_id: str) -> None:
        if campaign_id not in self.referenced_in_campaigns:
            self.referenced_in_campaigns.append(campaign_id)
            logger.debug("Legacy %s referenced in campaign %s", self.name, campaign_id)


@dataclass
class LedgerEntry:
    id: str
    character_name: str
    player_id: str
    xp_banked: int
    reverence_points: int
    features_created: List[LegacyFeature]
    multiplier: float
    final_act: str
    created_at: datetime
    campaign_id: str
    retired_at_level: int

    def summary(self) -> str:
        features_desc = ", ".join([f.name for f in self.features_created])
        return (
            f"{self.character_name} retired at level {self.retired_at_level} "
            f"with {self.reverence_points} acts of reverence, "
            f"leaving behind: {features_desc}"
        )


class LegacyLedgerEngine:
    FEATURE_XP_COST = 1000
    MAX_ACTIVE_FEATURES = 100

    def __init__(self, world_id: str):
        self.world_id = world_id
        self.entries: List[LedgerEntry] = []
        self.features: Dict[str, LegacyFeature] = {}
        self.bloodlines: Dict[str, List[str]] = {}

    def retire_character(
        self,
        character_name: str,
        player_id: str,
        xp_remaining: int,
        level: int,
        final_act: str,
        gifted: bool = False,
        underdog: bool = False,
        campaign_id: Optional[str] = None,
    ) -> LedgerEntry:
        logger.info("RETIREMENT RITUAL: %s retires with %s XP", character_name, xp_remaining)

        multiplier = self._deposit_multiplier(gifted, underdog)
        adjusted_xp = int(xp_remaining * multiplier)
        reverence_points = adjusted_xp // self.FEATURE_XP_COST

        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            character_name=character_name,
            player_id=player_id,
            xp_banked=adjusted_xp,
            reverence_points=reverence_points,
            features_created=[],
            multiplier=multiplier,
            final_act=final_act,
            created_at=datetime.utcnow(),
            campaign_id=campaign_id or "unknown",
            retired_at_level=level,
        )
        self.entries.append(entry)

        for i in range(reverence_points):
            feature = self._generate_legacy_feature(
                character_name=character_name,
                player_id=player_id,
                feature_index=i,
                entry_id=entry.id,
            )
            entry.features_created.append(feature)
            self.features[feature.id] = feature

        if len(self.features) > self.MAX_ACTIVE_FEATURES:
            # Graceful cap: deactivate oldest active features.
            active = [f for f in self.features.values() if f.active]
            active.sort(key=lambda f: f.created_at)
            overflow = len(active) - self.MAX_ACTIVE_FEATURES
            for f in active[: max(0, overflow)]:
                f.active = False

        self._record_retirement_ritual(entry)
        return entry

    def _deposit_multiplier(self, gifted: bool, underdog: bool) -> float:
        if underdog:
            return 1.2
        if gifted:
            return 0.8
        return 1.0

    def _generate_legacy_feature(
        self,
        character_name: str,
        player_id: str,
        feature_index: int,
        entry_id: str,
    ) -> LegacyFeature:
        import random

        feature_types = [
            LegacyFeatureType.VILLAGE,
            LegacyFeatureType.ARTIFACT,
            LegacyFeatureType.BLESSING,
            LegacyFeatureType.LANDMARK,
            LegacyFeatureType.TRADITION,
        ]
        feature_type = random.choice(feature_types)

        if feature_type == LegacyFeatureType.VILLAGE:
            name = f"{character_name}'s Rest"
            description = f"A small settlement founded where {character_name} spent their final days."
            effect = {"healing_bonus": 1, "safe_rest": True}
        elif feature_type == LegacyFeatureType.ARTIFACT:
            name = f"Relic of {character_name}"
            description = f"An item imbued with {character_name}'s essence."
            effect = {"legacy_bonus": 1, "skill_bonus": "relevant_skill"}
        elif feature_type == LegacyFeatureType.BLESSING:
            name = f"{character_name}'s Favor"
            description = f"Those who follow {character_name}'s path find unexpected aid."
            effect = {"luck_bonus": 1, "critical_range": 1}
        elif feature_type == LegacyFeatureType.LANDMARK:
            name = f"{character_name}'s Stand"
            description = f"The place where {character_name} made their final stand."
            effect = {"defensive_bonus": 2, "hallowed_ground": True}
        else:
            name = f"Way of {character_name}"
            description = f"A tradition passed down from {character_name}'s teachings."
            effect = {"xp_bonus": 0.1, "skill_proficiency": "relevant_skill"}

        return LegacyFeature(
            id=str(uuid.uuid4()),
            character_name=character_name,
            player_id=player_id,
            feature_type=feature_type,
            name=name,
            description=description,
            mechanical_effect=effect,
            location_id=None,
            created_at=datetime.utcnow(),
        )

    def _record_retirement_ritual(self, entry: LedgerEntry) -> None:
        ritual_record = {
            "type": "retirement",
            "character": entry.character_name,
            "final_act": entry.final_act,
            "features": [f.name for f in entry.features_created],
            "timestamp": entry.created_at.isoformat(),
        }
        logger.info("Ritual recorded: %s", ritual_record)

    def generate_world_features(self) -> List[str]:
        features: List[str] = []
        for entry in self.entries:
            for feature in entry.features_created:
                if feature.active:
                    features.append(f"{feature.name}: {feature.description}")
        return features

    def get_legacy_features_at_location(self, location_id: str) -> List[LegacyFeature]:
        return [f for f in self.features.values() if f.active and f.location_id == location_id]

    def get_bloodline_features(self, bloodline_name: str) -> List[LegacyFeature]:
        feature_ids = self.bloodlines.get(bloodline_name, [])
        return [self.features[fid] for fid in feature_ids if fid in self.features]

    def create_bloodline(self, bloodline_name: str, feature_ids: List[str]) -> None:
        self.bloodlines[bloodline_name] = feature_ids
        logger.info("Bloodline created: %s with %s features", bloodline_name, len(feature_ids))

    def get_ledger_state(self) -> Dict[str, Any]:
        active_features = [f for f in self.features.values() if f.active]
        return {
            "world_id": self.world_id,
            "total_retirements": len(self.entries),
            "total_reverence": sum(e.reverence_points for e in self.entries),
            "total_features": len(self.features),
            "active_features": len(active_features),
            "bloodlines": len(self.bloodlines),
            "features_by_type": {
                feature_type.value: len([f for f in self.features.values() if f.feature_type == feature_type])
                for feature_type in LegacyFeatureType
            },
            "recent_retirements": [
                {
                    "character": e.character_name,
                    "reverence_points": e.reverence_points,
                    "features": [f.name for f in e.features_created],
                    "final_act": e.final_act[:100] + "..." if len(e.final_act) > 100 else e.final_act,
                    "date": e.created_at.isoformat(),
                }
                for e in self.entries[-5:]
            ],
        }

    def audit(self) -> str:
        if not self.entries:
            return "The ledger is empty. Your story begins here."

        most_reverent = max(self.entries, key=lambda e: e.reverence_points)
        latest = self.entries[-1]

        narrative = ["THE LEGACY LEDGER", ""]
        narrative.append(f"Since the beginning, {len(self.entries)} heroes have retired into legend.")
        narrative.append("")
        narrative.append(
            f"The most revered was {most_reverent.character_name}, who left {most_reverent.reverence_points} marks upon the world."
        )
        narrative.append("")
        narrative.append(f"Most recently, {latest.character_name} retired with the act:")
        narrative.append(f'"{latest.final_act}"')
        narrative.append("")

        active = [f for f in self.features.values() if f.active][:5]
        if active:
            narrative.append("The world still bears these marks:")
            for feature in active:
                narrative.append(f"  - {feature.name}: {feature.description}")

        return "\n".join(narrative)


class LedgerAuditEngine:
    def __init__(self, ledger: LegacyLedgerEngine):
        self.ledger = ledger
        self.last_audit: Optional[datetime] = None

    def audit(self) -> str:
        self.last_audit = datetime.utcnow()
        return self.ledger.audit()

    def get_audit_state(self) -> Dict[str, Any]:
        return {
            "last_audit": self.last_audit.isoformat() if self.last_audit else None,
            "ledger_state": self.ledger.get_ledger_state(),
        }
