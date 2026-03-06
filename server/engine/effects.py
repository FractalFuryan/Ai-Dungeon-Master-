from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BondEventType(str, Enum):
    TRAUMA = "trauma"
    VICTORY = "victory"
    RITUAL = "ritual"
    SACRIFICE = "sacrifice"
    BETRAYAL = "betrayal"
    FAILURE = "failure"
    SUCCESS = "success"


class ThreadType(str, Enum):
    COMPETENCE = "competence"
    IDENTITY = "identity"
    PURPOSE = "purpose"
    BOND = "bond"
    CUSTOM = "custom"


@dataclass
class PartyEffectResult:
    bond_change: int = 0
    strain_change: float = 0.0
    reverence_token_id: Optional[str] = None
    legendary_moment: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class EngineEffects:
    modifiers: List[float] = field(default_factory=list)
    bond_events: List[Dict[str, Any]] = field(default_factory=list)
    reverence_events: List[Dict[str, Any]] = field(default_factory=list)
    thread_events: List[Dict[str, Any]] = field(default_factory=list)
    artifact_events: List[Dict[str, Any]] = field(default_factory=list)
    world_events: List[Dict[str, Any]] = field(default_factory=list)

    def merge(self, other: "EngineEffects") -> "EngineEffects":
        self.modifiers.extend(other.modifiers)
        self.bond_events.extend(other.bond_events)
        self.reverence_events.extend(other.reverence_events)
        self.thread_events.extend(other.thread_events)
        self.artifact_events.extend(other.artifact_events)
        self.world_events.extend(other.world_events)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modifiers": self.modifiers,
            "bond_events": self.bond_events,
            "reverence_events": self.reverence_events,
            "thread_events": self.thread_events,
            "artifact_events": self.artifact_events,
            "world_events": self.world_events,
        }
