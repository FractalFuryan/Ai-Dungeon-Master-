from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from server.api import dependencies as api_dependencies
from server.api import legacy as legacy_api
from server.api import myth_graph as myth_graph_api
from server.database import Base
from server.engine.myth_graph_engine import EdgeType, MythGraphEngine, NodeType
from server.main import app
from server.models import Character, Cycle, World


class _HttpFakeAnchor:
    def __init__(self):
        self._state = {"recent_mundane_count": 0, "can_use_fantastic": False}

    def get_anchor_state(self) -> Dict[str, Any]:
        return self._state

    def reset_session(self) -> None:
        self._state = {"recent_mundane_count": 0, "can_use_fantastic": True}


class _HttpFakeRetirement:
    def preview_retirement(self, character: Any) -> Dict[str, Any]:
        return {"character": character.name, "eligible": int(character.xp or 0) >= 1000}


class _HttpFakeLedgerAudit:
    def get_audit_state(self) -> Dict[str, Any]:
        return {"last_audit": None, "ledger_state": {"total_retirements": 0}}


class _HttpFakeWorldEngine:
    def __init__(self):
        self.anchor = _HttpFakeAnchor()
        self.retirement = _HttpFakeRetirement()
        self.ledger_audit = _HttpFakeLedgerAudit()
        self.myth_graph = MythGraphEngine("w-http")

    def perform_retirement(
        self,
        character: Any,
        player_id: str,
        final_act: str,
        feature_type: str | None = None,
        chosen_location: str | None = None,
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "character": character.name,
            "player_id": player_id,
            "final_act": final_act,
            "feature_type": feature_type,
            "chosen_location": chosen_location,
        }

    def audit_ledger(self) -> str:
        return "THE LEGACY LEDGER"

    def get_legacy_state(self) -> Dict[str, Any]:
        return {
            "ledger": {"total_retirements": 0},
            "anchor": self.anchor.get_anchor_state(),
            "myth_graph": {"nodes": len(self.myth_graph.nodes), "edges": len(self.myth_graph.edges)},
        }

    def report_vector(self, player_id: str, description: str, context: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
        if "trigger" in description:
            return {"action": "introduce_mundane_complication", "player_id": player_id}
        return None

    def add_to_myth_graph(
        self,
        name: str,
        node_type: str,
        properties: Dict[str, Any] | None = None,
        connections: list[Dict[str, Any]] | None = None,
    ):
        node = self.myth_graph.add_node(name=name, node_type=NodeType(node_type), properties=properties)
        for conn in connections or []:
            self.myth_graph.add_edge(
                source_id=node.id,
                target_id=conn["target_id"],
                edge_type=EdgeType(conn["edge_type"]),
                properties=conn.get("properties", {}),
            )
        return node

    def get_myth_narrative(self, node_id: str) -> str:
        return self.myth_graph.generate_myth_narrative(node_id)


@pytest.fixture
def http_client() -> Generator[tuple[TestClient, str], None, None]:
    # Shared in-memory SQLite DB across threads for TestClient.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db: Session = TestingSessionLocal()
    world = World(name="HTTP Test World")
    db.add(world)
    db.commit()

    cycle = Cycle(world_id=world.id, name="HTTP Cycle")
    db.add(cycle)
    db.commit()

    character = Character(cycle_id=cycle.id, name="Arin", xp=1300)
    db.add(character)
    db.commit()
    character_id = character.id
    db.close()

    fake_engine = _HttpFakeWorldEngine()

    def override_get_db() -> Generator[Session, None, None]:
        local = TestingSessionLocal()
        try:
            yield local
        finally:
            local.close()

    def override_get_world_engine() -> _HttpFakeWorldEngine:
        return fake_engine

    app.dependency_overrides[legacy_api.get_db] = override_get_db
    app.dependency_overrides[api_dependencies.get_world_engine] = override_get_world_engine
    app.dependency_overrides[legacy_api.get_world_engine] = override_get_world_engine
    app.dependency_overrides[myth_graph_api.get_world_engine] = override_get_world_engine

    client = TestClient(app)
    try:
        yield client, character_id
    finally:
        app.dependency_overrides.clear()


def test_legacy_endpoints_http(http_client):
    client, character_id = http_client

    retire = client.post(
        "/api/legacy/retire",
        params={
            "world_id": "w-http",
            "character_id": character_id,
            "player_id": "p-http",
            "final_act": "I stand as the dawn rises.",
            "feature_type": "artifact",
        },
    )
    assert retire.status_code == 200
    assert retire.json()["success"] is True

    preview = client.post(
        "/api/legacy/retire/preview",
        params={"world_id": "w-http", "character_id": character_id},
    )
    assert preview.status_code == 200
    assert preview.json()["eligible"] is True

    vector = client.post(
        "/api/legacy/vector/report",
        params={
            "world_id": "w-http",
            "player_id": "p-http",
            "description": "trigger correction",
        },
    )
    assert vector.status_code == 200
    assert vector.json()["reported"] is True
    assert vector.json()["correction"]["action"] == "introduce_mundane_complication"

    reset = client.post("/api/legacy/anchor/reset", params={"world_id": "w-http"})
    assert reset.status_code == 200
    assert reset.json()["reset"] is True


def test_myth_graph_endpoints_http(http_client):
    client, _character_id = http_client

    node_a = client.post(
        "/api/myth-graph/nodes",
        params={"world_id": "w-http", "name": "Arin", "node_type": "character"},
        json={"rank": "captain"},
    )
    assert node_a.status_code == 200
    a_id = node_a.json()["id"]

    node_b = client.post(
        "/api/myth-graph/nodes",
        params={"world_id": "w-http", "name": "Skyhold", "node_type": "location"},
    )
    assert node_b.status_code == 200
    b_id = node_b.json()["id"]

    edge = client.post(
        "/api/myth-graph/edges",
        params={
            "world_id": "w-http",
            "source_id": a_id,
            "target_id": b_id,
            "edge_type": "died_at",
        },
    )
    assert edge.status_code == 200
    assert edge.json()["type"] == "died_at"

    nodes = client.get(
        "/api/myth-graph/nodes",
        params={"world_id": "w-http", "node_type": "character"},
    )
    assert nodes.status_code == 200
    assert len(nodes.json()) == 1

    narrative = client.get(f"/api/myth-graph/narrative/{a_id}", params={"world_id": "w-http"})
    assert narrative.status_code == 200
    assert "MYTH" in narrative.json()["narrative"]

    state = client.get("/api/myth-graph/state", params={"world_id": "w-http"})
    assert state.status_code == 200
    assert state.json()["stats"]["total_nodes"] == 2
    assert state.json()["stats"]["total_edges"] == 1


def test_myth_graph_invalid_node_type_http(http_client):
    client, _character_id = http_client

    invalid = client.post(
        "/api/myth-graph/nodes",
        params={"world_id": "w-http", "name": "Invalid", "node_type": "not_a_node"},
    )
    assert invalid.status_code == 400
    assert "Invalid node_type" in invalid.json()["error"]
