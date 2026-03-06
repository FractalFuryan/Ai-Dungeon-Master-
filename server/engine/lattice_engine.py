from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LatticeMarker(Enum):
    """The three types of lattice markers for open currents."""

    RUMOR = "rumor"
    FUTURE_SEED = "future_seed"
    GRIM_REMINDER = "grim_reminder"


class CurrentType(Enum):
    """Types of open currents."""

    UNANSWERED_QUEST = "unanswered_quest"
    DECLINED_PRESSURE = "declined_pressure"
    IGNORED_LOCATION = "ignored_location"
    BYPASSED_CHOICE = "bypassed_choice"
    FORGOTTEN_NPC = "forgotten_npc"
    ABANDONED_FACTION = "abandoned_faction"


class RipenessLevel(Enum):
    """How ripe an open current has become."""

    FRESH = "fresh"
    RIPENING = "ripening"
    FERMENTED = "fermented"
    BURST = "burst"


@dataclass
class WyrdThread:
    """A thread connecting players to the world."""

    id: str
    name: str
    description: str
    player_ids: List[str]
    npc_ids: List[str]
    strength: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_tugged: Optional[datetime] = None


@dataclass
class OpenCurrent:
    """An unanswered element that ripens independently."""

    id: str
    current_type: CurrentType
    description: str
    created_at: datetime
    last_touched: Optional[datetime]
    ripeness: RipenessLevel
    markers: List[LatticeMarker]
    location_id: Optional[str]
    faction_ids: List[str]
    npc_ids: List[str]
    wyrd_thread_ids: List[str]
    evolution_stage: int = 0
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    burst_at: Optional[datetime] = None
    burst_description: Optional[str] = None
    environmental_modifier: Optional[Dict[str, Any]] = None

    def add_marker(self, marker: LatticeMarker, context: str) -> None:
        self.markers.append(marker)
        self.evolution_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "marker_added",
                "marker": marker.value,
                "context": context,
            }
        )
        logger.debug("Marker %s added to current %s", marker.value, self.id)

    def ripen(self) -> bool:
        old_ripeness = self.ripeness
        if self.last_touched:
            days_ignored = (datetime.utcnow() - self.last_touched).days
        else:
            days_ignored = (datetime.utcnow() - self.created_at).days

        if days_ignored >= 5:
            self.ripeness = RipenessLevel.BURST
        elif days_ignored >= 3:
            self.ripeness = RipenessLevel.FERMENTED
        elif days_ignored >= 1:
            self.ripeness = RipenessLevel.RIPENING
        else:
            self.ripeness = RipenessLevel.FRESH

        if self.ripeness != old_ripeness:
            self.evolution_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": f"ripened_to_{self.ripeness.value}",
                    "days_ignored": days_ignored,
                }
            )
            logger.info("Current %s ripened to %s", self.id, self.ripeness.value)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.current_type.value,
            "description": self.description,
            "created": self.created_at.isoformat(),
            "last_touched": self.last_touched.isoformat() if self.last_touched else None,
            "ripeness": self.ripeness.value,
            "markers": [m.value for m in self.markers],
            "factions": self.faction_ids,
            "npcs": self.npc_ids,
            "wyrd_threads": self.wyrd_thread_ids,
            "evolution_stage": self.evolution_stage,
            "has_burst": self.burst_at is not None,
            "environmental_modifier": self.environmental_modifier,
        }


@dataclass
class MotiveNode:
    """A choice offered to players in a session."""

    id: str
    name: str
    description: str
    pressure_type: str
    pressure_description: str
    mundane_anchors: List[str]
    offered_at: datetime
    accepted: bool = False
    accepted_at: Optional[datetime] = None
    declined: bool = False
    declined_at: Optional[datetime] = None
    open_current_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "pressure_type": self.pressure_type,
            "pressure": self.pressure_description,
            "offered_at": self.offered_at.isoformat(),
            "accepted": self.accepted,
            "declined": self.declined,
            "open_current": self.open_current_id,
        }


class LatticeEngine:
    """Legacy DB-backed lattice currents engine kept for compatibility."""

    def __init__(self, db: Session, world_id: str):
        self.db = db
        self.world_id = world_id

    def tick(self, delta: float = 0.1) -> Dict[str, object]:
        from server.persistence.models import LatticeCurrent

        currents = (
            self.db.query(LatticeCurrent)
            .filter(LatticeCurrent.world_id == self.world_id, LatticeCurrent.resolved.is_(False))
            .all()
        )

        ripened = []
        for current in currents:
            current.intensity = float(current.intensity) + float(delta)
            if current.intensity >= 1.0:
                ripened.append(current.id)

        self.db.commit()
        return {"currents_updated": len(currents), "ripened": ripened, "timestamp": datetime.utcnow().isoformat()}

    def get_location_effects(self, location_id: Optional[str]) -> List[Dict[str, object]]:
        from server.persistence.models import LatticeCurrent

        if not location_id:
            return []

        rows = (
            self.db.query(LatticeCurrent)
            .filter(
                LatticeCurrent.world_id == self.world_id,
                LatticeCurrent.location_id == location_id,
                LatticeCurrent.resolved.is_(False),
            )
            .all()
        )
        return [{"current_id": row.id, "intensity": row.intensity, "type": row.current_type} for row in rows]
