from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class ShardStability(Enum):
    STABLE = "stable"
    DREAMING = "dreaming"
    FRACTURED = "fractured"
    COLLAPSED = "collapsed"


@dataclass
class Symbol:
    id: str
    name: str
    archetype: Optional[str]
    charge: float = 0.0
    manifestations: List[str] = field(default_factory=list)
    first_appeared: datetime = field(default_factory=datetime.utcnow)
    last_manifested: Optional[datetime] = None

    def manifest(self, description: str) -> None:
        self.manifestations.append(description)
        self.charge += 0.1
        self.last_manifested = datetime.utcnow()


@dataclass
class MemythicEvent:
    id: str
    event_type: str
    description: str
    impact: float
    symbols_involved: List[str]
    location_id: Optional[str]
    character_id: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class Shard:
    """Container reality for a world/campaign."""

    def __init__(self, name: str, world_id: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.world_id = world_id
        self.memythic_charge: float = 0.0
        self.symbols: Dict[str, Symbol] = {}
        self.events: List[MemythicEvent] = []
        self.stability: ShardStability = ShardStability.STABLE
        self.dream_logic_threshold: float = 3.0
        self.created_at = datetime.utcnow()
        self.last_dream_event: Optional[datetime] = None

    def register_event(self, event: MemythicEvent) -> None:
        self.events.append(event)
        self.memythic_charge += float(event.impact)
        for symbol_name in event.symbols_involved:
            if symbol_name in self.symbols:
                self.symbols[symbol_name].charge += float(event.impact) * 0.5
        self._update_stability()

    def add_symbol(self, name: str, archetype: Optional[str] = None) -> Symbol:
        if name in self.symbols:
            return self.symbols[name]

        symbol = Symbol(id=str(uuid.uuid4()), name=name, archetype=archetype)
        self.symbols[name] = symbol
        self.memythic_charge += 0.3
        self._update_stability()
        return symbol

    def get_active_symbols(self, min_charge: float = 0.0) -> List[Symbol]:
        return [s for s in self.symbols.values() if s.charge >= min_charge]

    def _update_stability(self) -> None:
        if self.memythic_charge > 10.0:
            self.stability = ShardStability.COLLAPSED
        elif self.memythic_charge > 7.0:
            self.stability = ShardStability.FRACTURED
        elif self.memythic_charge > 3.0:
            self.stability = ShardStability.DREAMING
        else:
            self.stability = ShardStability.STABLE

    def apply_dream_logic(self, physics_result: Dict[str, Any]) -> Dict[str, Any]:
        if self.memythic_charge < self.dream_logic_threshold:
            return physics_result

        active_symbols = self.get_active_symbols(min_charge=1.0)
        if not active_symbols:
            return physics_result

        primary_symbol = max(active_symbols, key=lambda s: s.charge)
        modified = physics_result.copy()
        modified["dream_influence"] = {
            "symbol": primary_symbol.name,
            "archetype": primary_symbol.archetype,
            "charge": primary_symbol.charge,
        }

        if primary_symbol.archetype == "death":
            modified["total"] = max(3, int(modified.get("total", 10)) - 2)
        elif primary_symbol.archetype == "rebirth":
            modified["total"] = min(18, int(modified.get("total", 10)) + 2)
        elif primary_symbol.archetype == "hunger":
            modified["description"] = "A consuming emptiness affects the outcome."

        self.last_dream_event = datetime.utcnow()
        return modified

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "world_id": self.world_id,
            "memythic_charge": self.memythic_charge,
            "stability": self.stability.value,
            "symbols": [
                {
                    "name": s.name,
                    "archetype": s.archetype,
                    "charge": s.charge,
                    "manifestations": s.manifestations[-3:],
                }
                for s in self.symbols.values()
            ],
            "event_count": len(self.events),
            "dream_logic_active": self.memythic_charge >= self.dream_logic_threshold,
        }


class ShardEngine:
    """Loads/stores shard state and provides in-memory runtime state."""

    def __init__(self, db_session):
        self.db = db_session
        self.active_shards: Dict[str, Shard] = {}

    def create_shard(self, name: str, world_id: str) -> Shard:
        from server.persistence.models import Shard as ShardModel

        shard = Shard(name=name, world_id=world_id)
        db_shard = ShardModel(
            id=shard.id,
            world_id=world_id,
            name=name,
            memythic_charge=shard.memythic_charge,
            stability=shard.stability.value,
            payload={},
        )
        self.db.add(db_shard)
        self.db.commit()
        self.active_shards[shard.id] = shard
        return shard

    def get_shard(self, shard_id: str) -> Optional[Shard]:
        if shard_id in self.active_shards:
            return self.active_shards[shard_id]

        from server.persistence.models import Shard as ShardModel

        db_shard = self.db.query(ShardModel).filter(ShardModel.id == shard_id).first()
        if not db_shard:
            return None

        shard = Shard(db_shard.name, db_shard.world_id)
        shard.id = db_shard.id
        shard.memythic_charge = float(db_shard.memythic_charge)
        shard.stability = ShardStability(db_shard.stability)
        self.active_shards[shard.id] = shard
        return shard

    def get_or_create_shard_for_world(self, world_id: str) -> Shard:
        from server.persistence.models import Shard as ShardModel

        db_shard = self.db.query(ShardModel).filter(ShardModel.world_id == world_id).first()
        if db_shard:
            shard = self.get_shard(db_shard.id)
            if shard:
                return shard

        return self.create_shard(name=f"World {world_id} Shard", world_id=world_id)

    def persist_runtime_state(self, shard: Shard) -> None:
        from server.persistence.models import Shard as ShardModel

        db_shard = self.db.query(ShardModel).filter(ShardModel.id == shard.id).first()
        if not db_shard:
            return

        db_shard.memythic_charge = shard.memythic_charge
        db_shard.stability = shard.stability.value
        db_shard.payload = {
            "symbol_count": len(shard.symbols),
            "event_count": len(shard.events),
            "last_dream_event": shard.last_dream_event.isoformat() if shard.last_dream_event else None,
        }
        self.db.commit()
