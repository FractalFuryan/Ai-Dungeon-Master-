from dataclasses import dataclass
from datetime import datetime
import random
from typing import Any, Dict, List, Optional

from server.engine.shard_engine import MemythicEvent, Shard


@dataclass
class SymbolInjection:
    symbol: str
    archetype: Optional[str]
    context: str
    intensity: float


class MemythicEngine:
    RESONANCE_PAIRS = {
        ("death", "rebirth"): 0.5,
        ("hunger", "consumption"): 0.4,
        ("shadow", "light"): 0.3,
        ("crown", "throne"): 0.6,
        ("blood", "bone"): 0.5,
    }

    DISSONANCE_PAIRS = {
        ("death", "life"): -0.3,
        ("order", "chaos"): -0.2,
    }

    def __init__(self, shard: Shard, db_session: Optional[Any] = None, world_id: Optional[str] = None):
        self.shard = shard
        self.db = db_session
        self.world_id = world_id or shard.world_id
        self.symbol_history: List[Dict[str, Any]] = []
        self.resonance_events: List[Dict[str, Any]] = []

    def inject_symbol(self, injection: SymbolInjection) -> Dict[str, Any]:
        if injection.symbol in self.shard.symbols:
            symbol = self.shard.symbols[injection.symbol]
            symbol.charge += float(injection.intensity)
            symbol.manifest(injection.context)
        else:
            symbol = self.shard.add_symbol(injection.symbol, injection.archetype)
            symbol.charge = float(injection.intensity)
            symbol.manifest(injection.context)

        resonances = self._check_resonances(injection)
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": injection.symbol,
            "archetype": injection.archetype,
            "intensity": injection.intensity,
            "context": injection.context,
            "resonances": resonances,
        }
        self.symbol_history.append(event)

        memythic_event = MemythicEvent(
            id=f"sym_{datetime.utcnow().timestamp()}",
            event_type="symbol_injection",
            description=f"Symbol {injection.symbol} manifests: {injection.context}",
            impact=float(injection.intensity) * 0.5,
            symbols_involved=[injection.symbol],
            location_id=None,
            character_id=None,
        )
        self.shard.register_event(memythic_event)

        return {
            "symbol": injection.symbol,
            "new_charge": symbol.charge,
            "resonances": resonances,
            "total_charge": self.shard.memythic_charge,
        }

    def _check_resonances(self, injection: SymbolInjection) -> List[Dict[str, Any]]:
        resonances: List[Dict[str, Any]] = []
        for existing_name, existing_symbol in self.shard.symbols.items():
            if existing_name == injection.symbol:
                continue

            for (arch1, arch2), value in self.RESONANCE_PAIRS.items():
                if (injection.archetype == arch1 and existing_symbol.archetype == arch2) or (
                    injection.archetype == arch2 and existing_symbol.archetype == arch1
                ):
                    existing_symbol.charge += value * float(injection.intensity)
                    entry = {
                        "with": existing_name,
                        "type": "resonance",
                        "value": value,
                        "description": f"{injection.symbol} resonates with {existing_name}",
                    }
                    resonances.append(entry)
                    self._record_resonance_event(injection.symbol, existing_name, entry)

            for (arch1, arch2), value in self.DISSONANCE_PAIRS.items():
                if (injection.archetype == arch1 and existing_symbol.archetype == arch2) or (
                    injection.archetype == arch2 and existing_symbol.archetype == arch1
                ):
                    existing_symbol.charge += value * float(injection.intensity)
                    entry = {
                        "with": existing_name,
                        "type": "dissonance",
                        "value": value,
                        "description": f"{injection.symbol} clashes with {existing_name}",
                    }
                    resonances.append(entry)
                    self._record_resonance_event(injection.symbol, existing_name, entry)

        return resonances

    def get_dominant_symbols(self, count: int = 3) -> List[Dict[str, Any]]:
        symbols = sorted(self.shard.symbols.values(), key=lambda s: s.charge, reverse=True)[:count]
        return [
            {
                "name": s.name,
                "archetype": s.archetype,
                "charge": s.charge,
                "recent_manifestations": s.manifestations[-2:],
            }
            for s in symbols
        ]

    def fluctuate(self) -> Dict[str, Any]:
        old_charge = self.shard.memythic_charge
        decay = 0.05 * len(self.shard.symbols)
        self.shard.memythic_charge = max(0.0, self.shard.memythic_charge - decay)

        for symbol in self.shard.symbols.values():
            symbol.charge = max(0.0, symbol.charge + random.uniform(-0.02, 0.02))
            if random.random() < 0.1:
                self._spontaneous_resonance(symbol)

        self.shard._update_stability()
        return {
            "old_charge": old_charge,
            "new_charge": self.shard.memythic_charge,
            "decay": decay,
            "dominant_symbols": self.get_dominant_symbols(),
        }

    def _spontaneous_resonance(self, symbol) -> None:
        others = [s for s in self.shard.symbols.values() if s.name != symbol.name]
        if not others:
            return

        other = random.choice(others)
        for (arch1, arch2), value in self.RESONANCE_PAIRS.items():
            if (symbol.archetype == arch1 and other.archetype == arch2) or (
                symbol.archetype == arch2 and other.archetype == arch1
            ):
                boost = value * 0.1
                symbol.charge += boost
                other.charge += boost
                self.resonance_events.append(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "symbols": [symbol.name, other.name],
                        "boost": boost,
                    }
                )
                break

    def _record_resonance_event(self, symbol_a: str, symbol_b: str, detail: Dict[str, Any]) -> None:
        if not self.db:
            return
        try:
            from server.persistence.models import WorldEvent

            self.db.add(
                WorldEvent(
                    world_id=self.world_id,
                    event_type="symbol_resonance",
                    description=detail["description"],
                    payload={"symbols": [symbol_a, symbol_b], "detail": detail},
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
