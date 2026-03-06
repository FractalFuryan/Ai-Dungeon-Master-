from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class LargessType(Enum):
    """Types of largess that can be passed between shards."""

    WYRD_THREAD = "wyrd_thread"
    RUMOR = "rumor"
    RED_HERRING = "red_herring"
    VILLAGE_RUIN = "village_ruin"
    REVERENCE_ECHO = "reverence_echo"
    FORGOTTEN_SHRINE = "forgotten_shrine"
    CHARACTER_INTENT = "character_intent"
    OPEN_CURRENT = "open_current"
    RETIRED_LEGACY = "retired_legacy"


class ShardTransition(Enum):
    """How the shard transitions to the next cycle."""

    FORWARD_FLOW = "forward_flow"
    REWOUND = "rewound"
    REMIX = "remix"


@dataclass
class LargessSeed:
    """A piece of narrative potential banked for the next shard."""

    id: str
    seed_type: LargessType
    description: str
    source_character: Optional[str]
    source_player: str
    created_at: datetime
    campaign_id: str
    weight: float = 1.0
    claimed: bool = False
    claimed_by: Optional[str] = None
    claimed_at: Optional[datetime] = None
    original_trope: Optional[str] = None
    remixed_trope: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.seed_type.value,
            "description": self.description,
            "source_character": self.source_character,
            "source_player": self.source_player,
            "created": self.created_at.isoformat(),
            "weight": self.weight,
            "claimed": self.claimed,
            "claimed_by": self.claimed_by,
            "original_trope": self.original_trope,
            "remixed_trope": self.remixed_trope,
        }


@dataclass
class ShardGrave:
    """The grave of a completed shard - holds all its largess."""

    id: str
    shard_name: str
    completed_at: datetime
    campaign_id: str
    legacy_ledger_id: str
    largess_seeds: List[LargessSeed] = field(default_factory=list)
    final_ritual_words: List[str] = field(default_factory=list)
    total_retirements: int = 0
    total_reverence: int = 0
    major_plot: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "shard_name": self.shard_name,
            "completed_at": self.completed_at.isoformat(),
            "largess_seeds": [seed.to_dict() for seed in self.largess_seeds],
            "total_seeds": len(self.largess_seeds),
            "unclaimed_seeds": len([s for s in self.largess_seeds if not s.claimed]),
            "final_ritual": self.final_ritual_words,
            "stats": {
                "retirements": self.total_retirements,
                "reverence": self.total_reverence,
            },
        }


@dataclass
class NewShardDawn:
    """A new shard being born from the grave of the old."""

    id: str
    name: str
    transition_type: ShardTransition
    source_grave_id: str
    created_at: datetime
    claimed_seeds: List[str] = field(default_factory=list)
    player_intents: List[Dict[str, Any]] = field(default_factory=list)
    starting_motive_nodes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "transition": self.transition_type.value,
            "source_grave": self.source_grave_id,
            "created": self.created_at.isoformat(),
            "claimed_seeds": len(self.claimed_seeds),
            "player_intents": self.player_intents,
            "starting_motive_nodes": self.starting_motive_nodes,
        }
