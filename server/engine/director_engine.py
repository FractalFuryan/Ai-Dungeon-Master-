from datetime import datetime
from typing import Any, Dict, List, Optional
import random
import uuid

from server.engine.oracle_engine import OracleEngine, OracleIntent


class DirectorMove:
    def __init__(self, name: str, description: str, move_type: str, intensity: float = 0.5):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.move_type = move_type
        self.intensity = intensity
        self.executed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None


class DirectorEngine:
    MOVES = {
        "fade_to_symbol": {
            "name": "Fade to Symbol",
            "description": "Reality dissolves into symbolic space",
            "type": "transition",
            "base_intensity": 0.6,
        },
        "shard_fracture": {
            "name": "Shard Fracture",
            "description": "Time breaks and reorders",
            "type": "disruption",
            "base_intensity": 0.8,
        },
        "memythic_surge": {
            "name": "Memythic Surge",
            "description": "Mythic energy floods the narrative",
            "type": "amplification",
            "base_intensity": 0.7,
        },
        "veil_thinning": {
            "name": "Veil Thins",
            "description": "The boundary between realities weakens",
            "type": "horror",
            "base_intensity": 0.5,
        },
        "symbol_eruption": {
            "name": "Symbol Eruption",
            "description": "A dominant symbol manifests physically",
            "type": "manifestation",
            "base_intensity": 0.9,
        },
        "legacy_echo": {
            "name": "Legacy Echo",
            "description": "Past characters resonate in the present",
            "type": "memory",
            "base_intensity": 0.4,
        },
        "fractal_narrative": {
            "name": "Fractal Narrative",
            "description": "Events begin repeating at different scales",
            "type": "pattern",
            "base_intensity": 0.7,
        },
        "hunger_awakening": {
            "name": "Hunger Awakens",
            "description": "The void becomes aware and hungry",
            "type": "horror",
            "base_intensity": 0.9,
        },
    }

    def __init__(self, db_session, world_id: str, shard_engine, memythic_engine):
        self.db = db_session
        self.world_id = world_id
        self.shard_engine = shard_engine
        self.memythic = memythic_engine
        self.executed_moves: List[DirectorMove] = []
        self.available_moves = self.MOVES.copy()

    def should_intervene(self, world_state: Dict[str, Any]) -> Optional[str]:
        shard = getattr(self.memythic, "shard", None)
        if shard and getattr(shard, "stability", None) and shard.stability.value == "fractured":
            return "shard_fracture"
        if shard and getattr(shard, "stability", None) and shard.stability.value == "collapsed":
            return "hunger_awakening"
        if shard and shard.memythic_charge > 8.0:
            return "shard_fracture"
        if shard and shard.memythic_charge > 5.0:
            return "memythic_surge"

        symbols = self.memythic.get_dominant_symbols(1)
        if symbols and symbols[0]["charge"] > 3.0:
            return "symbol_eruption"

        # Fallback random intervention is intentionally rare.
        tension = float(world_state.get("tension", 0.0))
        if tension >= 0.95 and random.random() < 0.03:
            return random.choice(list(self.available_moves.keys()))

        return None

    def execute_move(self, move_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if move_name not in self.available_moves:
            raise ValueError(f"Unknown director move: {move_name}")

        move_data = self.available_moves[move_name]
        move = DirectorMove(
            name=move_data["name"],
            description=move_data["description"],
            move_type=move_data["type"],
            intensity=move_data["base_intensity"] * float(context.get("intensity_multiplier", 1.0)),
        )

        result = self._execute_by_type(move, context)
        move.executed_at = datetime.utcnow()
        move.result = result
        self.executed_moves.append(move)

        from server.persistence.models import WorldEvent

        event = WorldEvent(
            world_id=self.world_id,
            event_type=f"director_{move.move_type}",
            description=move.description,
            payload={
                "move_name": move.name,
                "move_type": move.move_type,
                "intensity": move.intensity,
                "result": result,
            },
        )
        self.db.add(event)
        self.db.commit()

        return {
            "move": move.name,
            "description": self._generate_description(move, result),
            "type": move.move_type,
            "intensity": move.intensity,
            "result": result,
        }

    def _execute_by_type(self, move: DirectorMove, context: Dict[str, Any]) -> Dict[str, Any]:
        if move.name == "Fade to Symbol":
            return self._fade_to_symbol(context)
        if move.name == "Shard Fracture":
            return self._shard_fracture(context)
        if move.name == "Memythic Surge":
            return self._memythic_surge(context)
        if move.name == "Symbol Eruption":
            return self._symbol_eruption(context)
        if move.name == "Hunger Awakens":
            return self._hunger_awakening(context)

        return {"effect": f"The {move.name} manifests", "duration": move.intensity * 10, "scope": context.get("scope", "local")}

    def _fade_to_symbol(self, context: Dict[str, Any]) -> Dict[str, Any]:
        oracle = OracleEngine()
        symbol = oracle.draw_symbol(OracleIntent.MYSTERY, context.get("description"))
        return {
            "time_shift": random.randint(-5, 0),
            "symbol": symbol.symbol,
            "meaning": symbol.meaning,
            "description": f"Reality fades to {symbol.symbol}",
            "duration": 30,
        }

    def _shard_fracture(self, context: Dict[str, Any]) -> Dict[str, Any]:
        fracture_type = random.choice(["forward", "backward", "loop", "fragments"])
        effects = {
            "forward": {"time_shift": 5, "description": "The shard fractures forward in time"},
            "backward": {"time_shift": -5, "description": "The shard fractures backward in time"},
            "loop": {"time_shift": 0, "description": "The shard fractures into a temporal loop"},
            "fragments": {
                "time_shift": random.choice([-3, 3]),
                "description": "The shard fractures into multiple time streams",
            },
        }
        return effects[fracture_type]

    def _memythic_surge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        shard = getattr(self.memythic, "shard", None)
        if not shard:
            return {"description": "Memythic energy pulses through the narrative"}

        old_charge = shard.memythic_charge
        shard.memythic_charge += 2.0
        shard._update_stability()
        return {
            "old_charge": old_charge,
            "new_charge": shard.memythic_charge,
            "surge_amount": 2.0,
            "description": "Memythic energy surges through reality",
        }

    def _symbol_eruption(self, context: Dict[str, Any]) -> Dict[str, Any]:
        symbols = self.memythic.get_dominant_symbols(1)
        if not symbols:
            return {"symbol": "unknown", "manifestation": "An unknown symbol erupts into reality"}

        symbol = symbols[0]
        return {
            "symbol": symbol["name"],
            "archetype": symbol["archetype"],
            "manifestation": f"The {symbol['name']} takes physical form",
            "charge_consumed": symbol["charge"] * 0.5,
        }

    def _hunger_awakening(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "hunger_level": random.uniform(3.0, 5.0),
            "target": random.choice(["memories", "names", "identities", "emotions"]),
            "description": "The void hungers. It has become aware of you.",
            "warning_turns": 3,
        }

    def _generate_description(self, move: DirectorMove, result: Dict[str, Any]) -> str:
        base = f"The Director executes a {move.move_type} move: {move.name}. "
        if "description" in result:
            return base + str(result["description"])
        if "manifestation" in result:
            return base + str(result["manifestation"])
        return base + move.description

    def get_recent_moves(self, count: int = 5) -> List[Dict[str, Any]]:
        recent = self.executed_moves[-count:]
        return [
            {
                "name": m.name,
                "type": m.move_type,
                "executed_at": m.executed_at.isoformat() if m.executed_at else None,
                "result": m.result,
            }
            for m in recent
        ]
