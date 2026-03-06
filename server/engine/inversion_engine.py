from dataclasses import dataclass, field
from enum import Enum
import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InversionType(Enum):
    ARCHETYPE = "archetype"
    MOTIVATION = "motivation"
    ORIGIN = "origin"
    RELATIONSHIP = "relationship"
    POWER = "power"


@dataclass
class EntangledAssumptions:
    entity_id: str
    entity_type: str
    name: str
    assumptions: List[str] = field(default_factory=list)
    archetypes: List[str] = field(default_factory=list)
    tropes: List[str] = field(default_factory=list)

    def add_assumption(self, assumption: str) -> None:
        if assumption not in self.assumptions:
            self.assumptions.append(assumption)

    def add_trope(self, trope: str) -> None:
        if trope not in self.tropes:
            self.tropes.append(trope)


class InversionEngine:
    DEFAULT_ASSUMPTIONS = {
        "dragon": ["breathes fire", "hoards gold", "ancient and wise", "lair in mountains", "can fly"],
        "troll": [
            "stupid brute",
            "biological regeneration",
            "cave dweller",
            "turns to stone in sunlight",
            "smells terrible",
        ],
        "vampire": [
            "drinks blood",
            "weak to sunlight",
            "can't enter without invitation",
            "turns into bat",
            "immortal",
        ],
        "elf": ["graceful and elegant", "long-lived", "connected to nature", "skilled with bows", "magical affinity"],
        "dwarf": ["skilled miners", "live in mountains", "beards", "good with axes", "grudge-holders"],
    }

    INVERSION_TEMPLATES = {
        "biological regeneration": [
            "memythic reconstruction via blood memory",
            "regenerates through ancestral echoes",
            "healing requires consuming memories",
            "regeneration only in darkness",
        ],
        "breathes fire": [
            "breathes cold that burns memory",
            "fire comes from absorbed sorrow",
            "cannot create fire, only redirect it",
            "fire is actually light given form",
        ],
        "stupid brute": [
            "ancient intelligence trapped in brutish form",
            "acts stupid as defense mechanism",
            "brutishness is a cultural performance",
            "actually possesses forbidden knowledge",
        ],
    }

    def __init__(self, db_session):
        self.db = db_session
        self.entangled_entities: Dict[str, EntangledAssumptions] = {}

    def register_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        custom_assumptions: Optional[List[str]] = None,
    ) -> EntangledAssumptions:
        assumptions = custom_assumptions or self.DEFAULT_ASSUMPTIONS.get(
            entity_type.lower(), ["exists", "has purpose", "interacts with world"]
        )
        entangled = EntangledAssumptions(entity_id=entity_id, entity_type=entity_type, name=name, assumptions=assumptions)
        if entity_type.lower() in self.DEFAULT_ASSUMPTIONS:
            entangled.archetypes.append(entity_type.lower())

        self.entangled_entities[entity_id] = entangled
        return entangled

    def invert_assumption(self, entity_id: str, assumption_index: Optional[int] = None) -> Dict[str, Any]:
        if entity_id not in self.entangled_entities:
            raise ValueError(f"Entity {entity_id} not registered")

        entity = self.entangled_entities[entity_id]
        if not entity.assumptions:
            raise ValueError("No assumptions available for inversion")

        if assumption_index is None:
            assumption_index = random.randint(0, len(entity.assumptions) - 1)
        elif assumption_index >= len(entity.assumptions):
            assumption_index = len(entity.assumptions) - 1

        original_assumption = entity.assumptions[assumption_index]
        inversion = self._generate_inversion(original_assumption, entity)

        inverted_assumption = {
            "original": original_assumption,
            "inverted": inversion,
            "index": assumption_index,
            "active": True,
        }

        if not hasattr(entity, "inversions"):
            entity.inversions = []
        entity.inversions.append(inverted_assumption)

        return {
            "entity_id": entity_id,
            "entity_name": entity.name,
            "entity_type": entity.entity_type,
            "original_assumption": original_assumption,
            "inverted_assumption": inversion,
            "index": assumption_index,
            "all_assumptions": entity.assumptions,
            "all_inversions": getattr(entity, "inversions", []),
        }

    def _generate_inversion(self, assumption: str, entity: EntangledAssumptions) -> str:
        if assumption in self.INVERSION_TEMPLATES:
            return random.choice(self.INVERSION_TEMPLATES[assumption])

        if " can " in assumption:
            left, right = assumption.split(" can ", 1)
            return f"{left} cannot {right}, but instead can {self._get_opposite_ability(right)}"

        if "is " in assumption or "are " in assumption:
            return self._invert_identity(assumption)

        templates = [
            f"The opposite of {assumption} is true",
            f"{assumption}, but only in the context of memythic resonance",
            f"What seems like {assumption} is actually a manifestation of something else",
            f"{assumption} is a lie told by the {random.choice(['shard', 'symbols', 'ancient ones'])}",
        ]
        return random.choice(templates)

    def _get_opposite_ability(self, ability: str) -> str:
        opposites = {
            "fly": "sink through solid matter",
            "breathe fire": "absorb heat",
            "regenerate": "accelerate decay in others",
            "cast spells": "unravel magic",
            "hide": "be unforgettable",
        }
        return opposites.get(ability, f"do the opposite of {ability}")

    def _invert_identity(self, assumption: str) -> str:
        if "stupid" in assumption:
            return "Ancient intelligence trapped in form that appears brutish"
        if "wise" in assumption:
            return "Wisdom is inherited trauma playing out cyclically"
        if "evil" in assumption:
            return "Evil is a perspective; their actions serve cosmic balance"
        if "good" in assumption:
            return "Good intentions paved the road to the current crisis"
        return f"The assumption of {assumption} is a memythic echo, not reality"

    def get_entangled_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        if entity_id not in self.entangled_entities:
            return None

        entity = self.entangled_entities[entity_id]
        inversions = getattr(entity, "inversions", [])
        return {
            "entity_id": entity.entity_id,
            "name": entity.name,
            "type": entity.entity_type,
            "assumptions": entity.assumptions,
            "inversions": inversions,
            "inversion_count": len(inversions),
            "fully_inverted": len(inversions) >= len(entity.assumptions),
        }

    def apply_inversions_to_narrative(self, entity_id: str, narrative_context: Dict[str, Any]) -> Dict[str, Any]:
        state = self.get_entangled_state(entity_id)
        if not state or not state["inversions"]:
            return narrative_context

        narrative_context["entanglement"] = {
            "entity": state["name"],
            "active_inversions": state["inversions"],
            "inversion_count": state["inversion_count"],
        }
        narrative_context["twist"] = state["inversions"][-1]["inverted"]
        return narrative_context
