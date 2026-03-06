from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
import uuid

from server.engine.effects import BondEventType
from server.persistence.repositories import BondRepository

logger = logging.getLogger(__name__)


@dataclass
class BondEvent:
    id: str
    event_type: BondEventType
    description: str
    characters_involved: List[str]
    bond_change: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BondEngine:
    def __init__(self, party_id: str, initial_value: int = 0):
        self.party_id = party_id
        self.bond_value: int = initial_value
        self.events: List[BondEvent] = []
        self.shared_traumas: List[str] = []
        self.shared_victories: List[str] = []
        self.last_update: Optional[datetime] = None

    def process_event(self, event_type: BondEventType, description: str, characters: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        bond_change = self._calculate_bond_change(event_type, context)
        event = BondEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            description=description,
            characters_involved=characters,
            bond_change=bond_change,
        )

        self.events.append(event)
        self.bond_value += bond_change
        self.last_update = datetime.utcnow()

        if event_type == BondEventType.TRAUMA:
            self.shared_traumas.append(description)
        elif event_type == BondEventType.VICTORY:
            self.shared_victories.append(description)

        return {
            "event_id": event.id,
            "bond_change": bond_change,
            "new_bond": self.bond_value,
            "description": description,
            "event_type": event_type.value,
        }

    def _calculate_bond_change(self, event_type: BondEventType, context: Dict[str, Any]) -> int:
        base_changes = {
            BondEventType.TRAUMA: 2,
            BondEventType.VICTORY: 1,
            BondEventType.RITUAL: 1,
            BondEventType.SACRIFICE: 3,
            BondEventType.BETRAYAL: -3,
            BondEventType.FAILURE: 0,
            BondEventType.SUCCESS: 0,
        }

        change = base_changes.get(event_type, 0)
        if context.get("near_death"):
            change += 1
        if context.get("saved_someone"):
            change += 1
        if len(context.get("characters_involved", [])) > 2:
            change += 1
        return change

    def get_bond_bonuses(self) -> Dict[str, Any]:
        if self.bond_value >= 7:
            return {
                "group_saves": 2,
                "revive_per_session": 1,
                "telepathic_connection": True,
                "shared_initiative": True,
            }
        if self.bond_value >= 5:
            return {"group_saves": 2, "revive_per_session": 1}
        if self.bond_value >= 3:
            return {"group_saves": 1}
        return {}

    def get_bond_narrative(self) -> str:
        if self.bond_value >= 7:
            return "Your souls are intertwined. You move as one being."
        if self.bond_value >= 5:
            return "You would die for each other without hesitation."
        if self.bond_value >= 3:
            return "Trust has been forged in fire and blood."
        if self.bond_value >= 1:
            return "You've begun to trust each other."
        return "You're still learning to work together."

    def get_shared_memories(self) -> Dict[str, List[Dict[str, Any]] | List[str]]:
        return {
            "traumas": self.shared_traumas[-3:],
            "victories": self.shared_victories[-3:],
            "recent_events": [
                {
                    "type": e.event_type.value,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in self.events[-5:]
            ],
        }


class PartyBondSystem:
    def __init__(self, db_session, world_id: str):
        self.db = db_session
        self.world_id = world_id
        self.repo = BondRepository(db_session)
        self.active_bonds: Dict[str, BondEngine] = {}

    def get_bond_engine(self, party_id: str, initial_value: int = 0) -> BondEngine:
        if party_id not in self.active_bonds:
            engine = BondEngine(party_id, initial_value=initial_value)
            for row in self.repo.list_for_party(party_id):
                engine.process_event(
                    event_type=BondEventType(row.event_type),
                    description=row.description,
                    characters=row.characters_involved or [],
                    context=row.payload or {},
                )
            self.active_bonds[party_id] = engine
        return self.active_bonds[party_id]

    def process_shared_failure(self, party_id: str, character_ids: List[str], action: str, roll_result: Any) -> Dict[str, Any]:
        bond = self.get_bond_engine(party_id)
        context = {
            "near_death": bool(getattr(roll_result, "is_critical_failure", False)),
            "characters_involved": character_ids,
        }
        result = bond.process_event(BondEventType.TRAUMA, f"Shared failure: {action}", character_ids, context)
        self.repo.add_event(
            party_id=party_id,
            event_type=BondEventType.TRAUMA.value,
            description=result["description"],
            characters_involved=character_ids,
            bond_change=result["bond_change"],
            timestamp=datetime.utcnow(),
            payload=context,
        )
        return result

    def process_shared_victory(self, party_id: str, character_ids: List[str], action: str, roll_result: Any) -> Dict[str, Any]:
        bond = self.get_bond_engine(party_id)
        context = {"characters_involved": character_ids}
        result = bond.process_event(BondEventType.VICTORY, f"Shared victory: {action}", character_ids, context)
        self.repo.add_event(
            party_id=party_id,
            event_type=BondEventType.VICTORY.value,
            description=result["description"],
            characters_involved=character_ids,
            bond_change=result["bond_change"],
            timestamp=datetime.utcnow(),
            payload=context,
        )
        return result

    def process_custom_event(self, party_id: str, event_type: BondEventType, description: str, characters: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        bond = self.get_bond_engine(party_id)
        payload = context or {}
        result = bond.process_event(event_type, description, characters, payload)
        self.repo.add_event(
            party_id=party_id,
            event_type=event_type.value,
            description=description,
            characters_involved=characters,
            bond_change=result["bond_change"],
            timestamp=datetime.utcnow(),
            payload=payload,
        )
        return result
