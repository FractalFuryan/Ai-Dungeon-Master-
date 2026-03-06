from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random
from typing import Any, Dict, List, Optional, Tuple
import uuid

from sqlalchemy.orm import Session


class VeilState(Enum):
    QUIET = "quiet"
    RUMOR = "rumor"
    DISAPPEARANCE = "disappearance"
    ENCOUNTER = "encounter"
    HUNGER = "hunger"
    COLLAPSE = "collapse"


@dataclass
class HungerVeil:
    location_id: str
    hunger_level: float = 0.0
    consumed_elements: List[str] = field(default_factory=list)
    last_meal: Optional[datetime] = None
    preferred_prey: Optional[str] = None


@dataclass
class VeilNodeState:
    node_id: str
    silence_level: float
    active: bool
    threshold: float
    trigger_count: int
    last_trigger: Optional[datetime]


class VeilNode:
    def __init__(self, location_id: str, node_type: str = "generic", node_id: Optional[str] = None):
        self.id = node_id or str(uuid.uuid4())
        self.location_id = location_id
        self.node_type = node_type
        self.silence_level: float = 0.0
        self.active: bool = True
        self.hunger: Optional[HungerVeil] = None
        self.thresholds = {
            VeilState.RUMOR: 1.0,
            VeilState.DISAPPEARANCE: 2.0,
            VeilState.ENCOUNTER: 3.0,
            VeilState.HUNGER: 4.0,
            VeilState.COLLAPSE: 5.0,
        }
        self.current_state: VeilState = VeilState.QUIET
        self.trigger_history: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
        self.last_propagation: Optional[datetime] = None

    def make_hungry(self, initial_hunger: float = 0.0, preferred_prey: Optional[str] = None) -> None:
        self.node_type = "hunger"
        self.hunger = HungerVeil(
            location_id=self.location_id,
            hunger_level=initial_hunger,
            preferred_prey=preferred_prey,
        )

    def propagate(self, delta: float = 0.1) -> Tuple[VeilState, Optional[Dict[str, Any]]]:
        if not self.active:
            return self.current_state, None

        old_level = self.silence_level
        self.silence_level += float(delta)
        self.last_propagation = datetime.utcnow()

        new_state = self._determine_state()
        trigger_event: Optional[Dict[str, Any]] = None
        if new_state != self.current_state:
            trigger_event = {
                "node_id": self.id,
                "old_state": self.current_state.value,
                "new_state": new_state.value,
                "silence_level": self.silence_level,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if self.hunger and new_state == VeilState.HUNGER:
                trigger_event["hunger"] = self._activate_hunger()

            self.trigger_history.append(trigger_event)
            self.current_state = new_state
            if new_state == VeilState.COLLAPSE:
                self.active = False

        return self.current_state, trigger_event

    def _determine_state(self) -> VeilState:
        if self.silence_level >= self.thresholds[VeilState.COLLAPSE]:
            return VeilState.COLLAPSE
        if self.silence_level >= self.thresholds[VeilState.HUNGER]:
            return VeilState.HUNGER
        if self.silence_level >= self.thresholds[VeilState.ENCOUNTER]:
            return VeilState.ENCOUNTER
        if self.silence_level >= self.thresholds[VeilState.DISAPPEARANCE]:
            return VeilState.DISAPPEARANCE
        if self.silence_level >= self.thresholds[VeilState.RUMOR]:
            return VeilState.RUMOR
        return VeilState.QUIET

    def _activate_hunger(self) -> Dict[str, Any]:
        if not self.hunger:
            return {}
        self.hunger.hunger_level = self.silence_level - 3.0
        prey_options = ["memories", "names", "identities", "emotions", "physical forms"]
        prey = self.hunger.preferred_prey or random.choice(prey_options)
        return {
            "hunger_level": self.hunger.hunger_level,
            "hunting": prey,
            "consumed": self.hunger.consumed_elements[-3:],
        }

    def consume(self, target: str) -> bool:
        if not self.hunger or self.current_state != VeilState.HUNGER:
            return False
        self.hunger.consumed_elements.append(target)
        self.hunger.last_meal = datetime.utcnow()
        self.hunger.hunger_level = max(0.0, self.hunger.hunger_level - 0.5)
        return True

    def get_state_description(self) -> str:
        descriptions = {
            VeilState.QUIET: "The area feels normal, if a bit quiet.",
            VeilState.RUMOR: "Whispers echo at the edge of hearing. Something is wrong here.",
            VeilState.DISAPPEARANCE: "Things vanish. Time feels strange. The veil is thinning.",
            VeilState.ENCOUNTER: "The silence has weight. You are not alone in this quiet.",
            VeilState.HUNGER: "The emptiness hungers. It wants to consume what you are.",
            VeilState.COLLAPSE: "Reality tears. The veil has consumed itself.",
        }
        base = descriptions.get(self.current_state, "")
        if self.hunger and self.current_state == VeilState.HUNGER:
            base += f" It hungers for {self.hunger.preferred_prey or 'everything'}."
        return base


class VeilEngine:
    """Enhanced veil engine with hunger states and compatibility helpers."""

    def __init__(self, db: Session, world_id: str):
        self.db = db
        self.world_id = world_id
        self.nodes: Dict[str, VeilNode] = {}

    def create_node(self, location_id: str, initial_silence: float = 0.0, node_type: str = "generic") -> str:
        from server.persistence.models import VeilNodeV2

        node = VeilNode(location_id=location_id, node_type=node_type)
        node.silence_level = float(initial_silence)
        node.current_state = node._determine_state()

        db_node = VeilNodeV2(
            id=node.id,
            world_id=self.world_id,
            location_id=location_id,
            node_type=node_type,
            silence_level=node.silence_level,
            active=node.active,
            payload={},
        )
        self.db.add(db_node)
        self.db.commit()
        self.nodes[node.id] = node
        return node.id

    def _load_nodes(self) -> None:
        from server.persistence.models import VeilNodeV2

        rows = self.db.query(VeilNodeV2).filter(VeilNodeV2.world_id == self.world_id).all()
        for row in rows:
            if row.id in self.nodes:
                continue
            node = VeilNode(location_id=row.location_id, node_type=row.node_type or "generic", node_id=row.id)
            node.silence_level = float(row.silence_level)
            node.active = bool(row.active)
            node.current_state = node._determine_state()
            self.nodes[row.id] = node

    def propagate_all(self, delta: float = 0.1) -> List[Dict[str, Any]]:
        from server.persistence.models import VeilNodeV2, WorldEvent

        self._load_nodes()
        triggers: List[Dict[str, Any]] = []

        for node_id, node in self.nodes.items():
            if not node.active:
                continue

            _state, trigger = node.propagate(delta)

            db_node = self.db.query(VeilNodeV2).filter(VeilNodeV2.id == node_id).first()
            if db_node:
                db_node.silence_level = node.silence_level
                db_node.active = node.active

            if trigger:
                trigger["effect"] = trigger["new_state"]
                trigger["description"] = node.get_state_description()
                triggers.append(trigger)
                self.db.add(
                    WorldEvent(
                        world_id=self.world_id,
                        location_id=node.location_id,
                        event_type=f"veil_{trigger['new_state']}",
                        description=node.get_state_description(),
                        payload=trigger,
                    )
                )

        self.db.commit()
        return triggers

    # Compatibility alias used by existing code/tests.
    def propagate_silence(self, delta: float = 0.1) -> List[Dict[str, Any]]:
        return self.propagate_all(delta)

    def add_silence(self, node_id: str, amount: float) -> float:
        self._load_nodes()
        node = self.nodes.get(node_id)
        if not node:
            return 0.0
        node.silence_level += float(amount)
        node.current_state = node._determine_state()

        from server.persistence.models import VeilNodeV2

        db_node = self.db.query(VeilNodeV2).filter(VeilNodeV2.id == node_id).first()
        if db_node:
            db_node.silence_level = node.silence_level
        self.db.commit()
        return node.silence_level

    def get_node_state(self, node_id: str) -> Optional[VeilNodeState]:
        from server.persistence.models import VeilNodeV2, WorldEvent

        row = self.db.query(VeilNodeV2).filter(VeilNodeV2.id == node_id).first()
        if not row:
            return None

        trigger_count = (
            self.db.query(WorldEvent)
            .filter(WorldEvent.world_id == self.world_id, WorldEvent.event_type.like("veil_%"))
            .count()
        )
        return VeilNodeState(
            node_id=row.id,
            silence_level=float(row.silence_level),
            active=bool(row.active),
            threshold=self.get_current_threshold(float(row.silence_level)),
            trigger_count=trigger_count,
            last_trigger=row.updated_at,
        )

    def get_node_state_detail(self, node_id: str) -> Optional[Dict[str, Any]]:
        self._load_nodes()
        node = self.nodes.get(node_id)
        if not node:
            return None
        return {
            "id": node.id,
            "location_id": node.location_id,
            "node_type": node.node_type,
            "state": node.current_state.value,
            "silence_level": node.silence_level,
            "active": node.active,
            "description": node.get_state_description(),
            "hunger": {
                "level": node.hunger.hunger_level if node.hunger else None,
                "consumed": node.hunger.consumed_elements if node.hunger else [],
                "preferred_prey": node.hunger.preferred_prey if node.hunger else None,
            }
            if node.hunger
            else None,
            "recent_triggers": node.trigger_history[-3:],
        }

    def nodes_in_state(self, state: VeilState) -> List[VeilNode]:
        self._load_nodes()
        return [n for n in self.nodes.values() if n.current_state == state and n.active]

    def get_current_threshold(self, silence_level: float) -> float:
        thresholds = [1.0, 2.0, 3.0, 4.0, 5.0]
        for threshold in thresholds:
            if silence_level < threshold:
                return threshold
        return float("inf")
