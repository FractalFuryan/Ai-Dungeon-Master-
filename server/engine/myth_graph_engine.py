from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    ARTIFACT = "artifact"
    EVENT = "event"
    BLOODLINE = "bloodline"
    SYMBOL = "symbol"
    LEGACY_FEATURE = "legacy_feature"
    FACTION = "faction"


class EdgeType(str, Enum):
    FOUNDED = "founded"
    DIED_AT = "died_at"
    WIELDED = "wielded"
    PARTICIPATED_IN = "participated_in"
    DESCENDED_FROM = "descended_from"
    RESONATES_WITH = "resonates_with"
    FEARS = "fears"
    ALLIED_WITH = "allied_with"
    CREATED = "created"
    DESTROYED = "destroyed"


@dataclass
class MythNode:
    id: str
    name: str
    node_type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    weight: float = 1.0


@dataclass
class MythEdge:
    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    weight: float = 1.0


class MythGraphEngine:
    def __init__(self, world_id: str):
        self.world_id = world_id
        self.nodes: Dict[str, MythNode] = {}
        self.edges: Dict[str, MythEdge] = {}
        self.adjacency: Dict[str, Set[str]] = {}

    def add_node(self, name: str, node_type: NodeType, properties: Optional[Dict[str, Any]] = None) -> MythNode:
        node_id = str(uuid.uuid4())
        node = MythNode(id=node_id, name=name, node_type=node_type, properties=properties or {})
        self.nodes[node_id] = node
        self.adjacency[node_id] = set()
        logger.info("Added node to myth graph: %s (%s)", name, node_type.value)
        return node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> MythEdge:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node not found")

        edge_id = str(uuid.uuid4())
        edge = MythEdge(
            id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            properties=properties or {},
        )
        self.edges[edge_id] = edge
        self.adjacency[source_id].add(edge_id)
        self.adjacency[target_id].add(edge_id)
        logger.info(
            "Added edge: %s -> %s (%s)",
            self.nodes[source_id].name,
            self.nodes[target_id].name,
            edge_type.value,
        )
        return edge

    def get_node(self, node_id: str) -> Optional[MythNode]:
        return self.nodes.get(node_id)

    def find_nodes(self, node_type: Optional[NodeType] = None, name_contains: Optional[str] = None) -> List[MythNode]:
        results: List[MythNode] = []
        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue
            if name_contains and name_contains.lower() not in node.name.lower():
                continue
            results.append(node)
        return results

    def get_connections(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[Tuple[MythNode, MythEdge]]:
        if node_id not in self.adjacency:
            return []

        connections: List[Tuple[MythNode, MythEdge]] = []
        for edge_id in self.adjacency[node_id]:
            edge = self.edges[edge_id]
            if edge_type and edge.edge_type != edge_type:
                continue

            other_id = edge.target_id if edge.source_id == node_id else edge.source_id
            other_node = self.nodes[other_id]
            connections.append((other_node, edge))
        return connections

    def calculate_mythic_weight(self, node_id: str) -> float:
        if node_id not in self.nodes:
            return 0.0

        weight = self.nodes[node_id].weight
        for _other_node, edge in self.get_connections(node_id):
            age_factor = 1.0 + (datetime.utcnow() - edge.created_at).days * 0.01
            weight += edge.weight * age_factor
        return weight

    def find_mythic_clusters(self, min_weight: float = 5.0) -> List[List[MythNode]]:
        visited: Set[str] = set()
        clusters: List[List[MythNode]] = []

        for node_id in self.nodes:
            if node_id in visited:
                continue

            queue = [node_id]
            cluster: List[MythNode] = []

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                if self.calculate_mythic_weight(current) >= min_weight:
                    cluster.append(self.nodes[current])

                for other_node, _edge in self.get_connections(current):
                    if other_node.id not in visited:
                        queue.append(other_node.id)

            if cluster:
                clusters.append(cluster)

        return clusters

    def evolve(self) -> None:
        logger.info("Evolving myth graph for world %s", self.world_id)
        for node_id in list(self.nodes.keys()):
            node = self.nodes[node_id]
            age_days = (datetime.utcnow() - node.created_at).days
            if age_days > 30:
                node.weight *= 1.01

            if node.weight > 10 and len(self.adjacency.get(node_id, set())) < 3:
                potential = self.find_nodes(node_type=NodeType.SYMBOL)
                if potential:
                    import random

                    target = random.choice(potential)
                    self.add_edge(
                        node_id,
                        target.id,
                        EdgeType.RESONATES_WITH,
                        {"spontaneous": True, "reason": "mythic evolution"},
                    )

        logger.info("Myth graph evolved: %s nodes, %s edges", len(self.nodes), len(self.edges))

    def get_graph_state(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.node_type.value,
                    "weight": n.weight,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type.value,
                    "weight": e.weight,
                }
                for e in self.edges.values()
            ],
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": {
                    nt.value: len([n for n in self.nodes.values() if n.node_type == nt]) for nt in NodeType
                },
            },
        }

    def generate_myth_narrative(self, node_id: str) -> str:
        if node_id not in self.nodes:
            return "Unknown"

        node = self.nodes[node_id]
        connections = self.get_connections(node_id)
        if not connections:
            return f"{node.name} stands alone in the mythic tapestry."

        lines = [f"THE MYTH OF {node.name.upper()}", ""]
        by_type: Dict[EdgeType, List[Tuple[MythNode, MythEdge]]] = {}
        for other, edge in connections:
            by_type.setdefault(edge.edge_type, []).append((other, edge))

        for et, conns in by_type.items():
            if et == EdgeType.FOUNDED:
                lines.append(f"Founded: {', '.join([c[0].name for c in conns])}")
            elif et == EdgeType.DIED_AT:
                lines.append(f"Death place: {conns[0][0].name}")
            elif et == EdgeType.WIELDED:
                lines.append(f"Wielded: {conns[0][0].name}")
            elif et == EdgeType.DESCENDED_FROM:
                lines.append(f"Descended from: {conns[0][0].name}")
            elif et == EdgeType.RESONATES_WITH:
                lines.append(f"Resonates with: {', '.join([c[0].name for c in conns])}")
            else:
                lines.append(f"{et.value}: {', '.join([c[0].name for c in conns])}")

        lines.append("")
        lines.append(f"Total mythic weight: {self.calculate_mythic_weight(node_id):.1f}")
        return "\n".join(lines)
