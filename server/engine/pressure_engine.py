from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class PressureField:
    id: str
    name: str
    source_type: str
    source_id: str
    center_location: Optional[str]
    strength: float
    radius: float
    influence_type: str
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_pulse: Optional[datetime] = None

    def calculate_pull(self, distance: float) -> float:
        if distance > self.radius:
            return 0.0
        if distance < 1:
            return self.strength
        return self.strength / (distance * distance)

    def affect_entity(self, entity_type: str, entity_data: Dict[str, Any], distance: float) -> Dict[str, Any]:
        pull = self.calculate_pull(distance)
        if pull <= 0:
            return {}

        effect = {
            "field_id": self.id,
            "field_name": self.name,
            "pull_strength": pull,
            "influence_type": self.influence_type,
        }
        if self.influence_type == "attraction":
            effect["movement"] = f"Drawn toward {self.name}"
            effect["modifier"] = pull * 0.1
        elif self.influence_type == "repulsion":
            effect["movement"] = f"Pushed away from {self.name}"
            effect["modifier"] = -pull * 0.1
        elif self.influence_type == "transformation":
            effect["change"] = f"Subtly altered by the {self.name} field"
            effect["mutation_chance"] = pull * 0.05
        return effect


class NarrativePressureEngine:
    def __init__(self, db_session, world_id: str):
        self.db = db_session
        self.world_id = world_id
        self.fields: Dict[str, PressureField] = {}
        self.location_graph: Dict[str, List[str]] = {}

    def set_location_graph(self, graph: Dict[str, List[str]]) -> None:
        # Graph shape: {"location_a": ["location_b", ...], ...}
        self.location_graph = graph

    def graph_distance(self, start: Optional[str], target: Optional[str]) -> float:
        if not start or not target:
            return 5.0
        if start == target:
            return 0.5
        if not self.location_graph:
            return 10.0

        visited = {start}
        queue: List[tuple[str, int]] = [(start, 0)]
        while queue:
            node, dist = queue.pop(0)
            for nxt in self.location_graph.get(node, []):
                if nxt == target:
                    return float(dist + 1)
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, dist + 1))
        return 10.0

    def create_field(
        self,
        name: str,
        source_type: str,
        source_id: str,
        center_location: Optional[str],
        strength: float,
        radius: float,
        influence_type: str,
    ) -> str:
        field_id = str(uuid.uuid4())
        field = PressureField(
            id=field_id,
            name=name,
            source_type=source_type,
            source_id=source_id,
            center_location=center_location,
            strength=min(10.0, max(0.1, float(strength))),
            radius=float(radius),
            influence_type=influence_type,
        )
        self.fields[field_id] = field

        from server.persistence.models import WorldEvent

        event = WorldEvent(
            world_id=self.world_id,
            event_type="pressure_field_created",
            description=f"Pressure field '{name}' created ({influence_type})",
            payload={
                "field_id": field_id,
                "strength": field.strength,
                "radius": field.radius,
                "influence_type": influence_type,
            },
        )
        self.db.add(event)
        self.db.commit()
        return field_id

    def field_from_symbol(self, symbol_name: str, symbol_charge: float, location: Optional[str] = None) -> Optional[str]:
        if symbol_charge < 1.0:
            return None

        lower = symbol_name.lower()
        influence_type = "transformation"
        if "death" in lower or "hunger" in lower:
            influence_type = "attraction"
        elif "shadow" in lower:
            influence_type = "repulsion"

        return self.create_field(
            name=f"Field of {symbol_name}",
            source_type="symbol",
            source_id=symbol_name,
            center_location=location,
            strength=symbol_charge * 2,
            radius=symbol_charge * 5,
            influence_type=influence_type,
        )

    def pulse_all_fields(self) -> List[Dict[str, Any]]:
        pulses = []
        for field_id, field in self.fields.items():
            if not field.active:
                continue

            field.last_pulse = datetime.utcnow()
            field.strength += 0.1 * (0.5 - (datetime.utcnow().timestamp() % 1))
            field.strength = max(0.1, min(10.0, field.strength))
            pulses.append(
                {
                    "field_id": field_id,
                    "name": field.name,
                    "strength": field.strength,
                    "radius": field.radius,
                    "type": field.influence_type,
                    "timestamp": field.last_pulse.isoformat(),
                }
            )
        return pulses

    def get_fields_at_location(self, location_id: str) -> List[Dict[str, Any]]:
        affecting = []
        for field in self.fields.values():
            if not field.active:
                continue

            distance = self.graph_distance(field.center_location, location_id)

            pull = field.calculate_pull(distance)
            if pull > 0:
                affecting.append(
                    {
                        "field_id": field.id,
                        "name": field.name,
                        "pull": pull,
                        "type": field.influence_type,
                        "effect": field.affect_entity("location", {}, distance),
                    }
                )

        return sorted(affecting, key=lambda x: x["pull"], reverse=True)

    def field_collisions(self) -> List[Dict[str, Any]]:
        collisions: List[Dict[str, Any]] = []
        field_list = list(self.fields.values())

        for i in range(len(field_list)):
            for j in range(i + 1, len(field_list)):
                field1 = field_list[i]
                field2 = field_list[j]
                if not field1.active or not field2.active:
                    continue

                if field1.center_location == field2.center_location:
                    self._resolve_collision(field1, field2, collisions)
                elif abs(field1.strength - field2.strength) < 3.0:
                    if datetime.utcnow().timestamp() % 10 < 2:
                        self._resolve_collision(field1, field2, collisions)

        return collisions

    def _resolve_collision(self, field1: PressureField, field2: PressureField, collisions: List[Dict[str, Any]]) -> None:
        if field1.influence_type == field2.influence_type:
            boost = min(field1.strength, field2.strength) * 0.1
            field1.strength += boost
            field2.strength += boost
            collisions.append({"type": "reinforcement", "fields": [field1.name, field2.name], "boost": boost})
        else:
            reduction = min(field1.strength, field2.strength) * 0.15
            field1.strength = max(0.1, field1.strength - reduction)
            field2.strength = max(0.1, field2.strength - reduction)
            collisions.append({"type": "clash", "fields": [field1.name, field2.name], "reduction": reduction})
