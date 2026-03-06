import pytest
from fastapi import HTTPException

from server.api.legacy import (
    get_ledger_audit,
    get_legacy_state,
    preview_retirement,
    report_vector,
    reset_anchor,
    retire_character,
)
from server.api.myth_graph import (
    create_edge,
    create_node,
    get_graph_state,
    get_node_narrative,
    list_nodes,
)
from server.engine.myth_graph_engine import EdgeType, MythGraphEngine, NodeType
from server.models import Character, Cycle, World


class _FakeAnchor:
    def __init__(self):
        self._state = {"recent_mundane_count": 0, "can_use_fantastic": False}

    def get_anchor_state(self):
        return self._state

    def reset_session(self):
        self._state = {"recent_mundane_count": 0, "can_use_fantastic": True}


class _FakeRetirementService:
    def preview_retirement(self, character):
        return {"character": character.name, "eligible": int(character.xp or 0) >= 1000}


class _FakeLedgerAudit:
    def get_audit_state(self):
        return {"last_audit": None, "ledger_state": {"total_retirements": 0}}


class _FakeWorldEngine:
    def __init__(self):
        self.anchor = _FakeAnchor()
        self.retirement = _FakeRetirementService()
        self.ledger_audit = _FakeLedgerAudit()
        self.myth_graph = MythGraphEngine("w1")

    def perform_retirement(self, character, player_id, final_act, feature_type=None, chosen_location=None):
        return {
            "success": True,
            "character": character.name,
            "player_id": player_id,
            "final_act": final_act,
            "feature_type": feature_type,
            "chosen_location": chosen_location,
        }

    def audit_ledger(self):
        return "THE LEGACY LEDGER"

    def get_legacy_state(self):
        return {"ledger": {"total_retirements": 0}, "anchor": self.anchor.get_anchor_state()}

    def report_vector(self, player_id, description, context=None):
        if "trigger" in description:
            return {"action": "introduce_mundane_complication", "player_id": player_id}
        return None

    def add_to_myth_graph(self, name, node_type, properties=None, connections=None):
        node = self.myth_graph.add_node(name=name, node_type=NodeType(node_type), properties=properties)
        for conn in connections or []:
            self.myth_graph.add_edge(
                source_id=node.id,
                target_id=conn["target_id"],
                edge_type=EdgeType(conn["edge_type"]),
                properties=conn.get("properties", {}),
            )
        return node

    def get_myth_narrative(self, node_id):
        return self.myth_graph.generate_myth_narrative(node_id)


@pytest.fixture
def seeded_character(db_session):
    world = World(name="Test World")
    db_session.add(world)
    db_session.commit()

    cycle = Cycle(world_id=world.id, name="Cycle 1")
    db_session.add(cycle)
    db_session.commit()

    character = Character(cycle_id=cycle.id, name="Arin", xp=1200)
    db_session.add(character)
    db_session.commit()
    return character


@pytest.mark.asyncio
async def test_legacy_retire_preview_and_state(db_session, seeded_character):
    engine = _FakeWorldEngine()

    retired = await retire_character(
        world_id="w1",
        character_id=seeded_character.id,
        player_id="p1",
        final_act="I stand my final watch.",
        db=db_session,
        world_engine=engine,
    )
    assert retired["success"] is True
    assert retired["character"] == "Arin"

    preview = await preview_retirement(
        world_id="w1",
        character_id=seeded_character.id,
        db=db_session,
        world_engine=engine,
    )
    assert preview["eligible"] is True

    audit = await get_ledger_audit(world_engine=engine)
    assert "audit" in audit
    assert "audit_state" in audit

    state = await get_legacy_state(world_engine=engine)
    assert "ledger" in state
    assert "anchor" in state


@pytest.mark.asyncio
async def test_legacy_retire_rejects_invalid_feature_type(db_session, seeded_character):
    engine = _FakeWorldEngine()

    with pytest.raises(HTTPException) as exc:
        await retire_character(
            world_id="w1",
            character_id=seeded_character.id,
            player_id="p1",
            final_act="I fade into legend.",
            feature_type="not_a_feature",
            db=db_session,
            world_engine=engine,
        )

    assert exc.value.status_code == 400
    assert "Invalid feature_type" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_legacy_vector_reporting_and_reset():
    engine = _FakeWorldEngine()

    vector = await report_vector(
        world_id="w1",
        player_id="p1",
        description="trigger correction",
        context={"scene": "market"},
        world_engine=engine,
    )
    assert vector["reported"] is True
    assert vector["correction"]["action"] == "introduce_mundane_complication"

    reset = await reset_anchor(world_engine=engine)
    assert reset["reset"] is True
    assert reset["anchor_state"]["can_use_fantastic"] is True


@pytest.mark.asyncio
async def test_myth_graph_create_list_edge_narrative_and_state():
    engine = _FakeWorldEngine()

    node_a = await create_node(
        world_id="w1",
        name="Arin",
        node_type="character",
        properties={"rank": "captain"},
        world_engine=engine,
    )
    node_b = await create_node(
        world_id="w1",
        name="Skyhold",
        node_type="location",
        world_engine=engine,
    )

    edge = await create_edge(
        world_id="w1",
        source_id=node_a["id"],
        target_id=node_b["id"],
        edge_type="died_at",
        world_engine=engine,
    )
    assert edge["type"] == "died_at"

    nodes = await list_nodes(world_id="w1", node_type="character", world_engine=engine)
    assert len(nodes) == 1
    assert nodes[0]["name"] == "Arin"

    narrative = await get_node_narrative(node_id=node_a["id"], world_engine=engine)
    assert narrative["node_id"] == node_a["id"]
    assert "MYTH" in narrative["narrative"]

    state = await get_graph_state(world_engine=engine)
    assert state["stats"]["total_nodes"] == 2
    assert state["stats"]["total_edges"] == 1


@pytest.mark.asyncio
async def test_myth_graph_rejects_invalid_node_type():
    engine = _FakeWorldEngine()

    with pytest.raises(HTTPException) as exc:
        await create_node(
            world_id="w1",
            name="Bad",
            node_type="not_a_node",
            world_engine=engine,
        )

    assert exc.value.status_code == 400
    assert "Invalid node_type" in str(exc.value.detail)
