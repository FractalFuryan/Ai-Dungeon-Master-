import pytest

from server.engine.veil_engine import VeilEngine


@pytest.fixture
def veil_engine(db_session):
    return VeilEngine(db_session, "test_world")


def test_create_veil_node(veil_engine):
    node_id = veil_engine.create_node("test_location")
    assert node_id is not None

    state = veil_engine.get_node_state(node_id)
    assert state is not None
    assert state.silence_level == 0.0
    assert state.active is True


def test_silence_propagation(veil_engine):
    node_id = veil_engine.create_node("test_location")
    _ = veil_engine.propagate_silence(delta=0.5)

    state = veil_engine.get_node_state(node_id)
    assert state is not None
    assert state.silence_level == 0.5


def test_threshold_triggers(veil_engine):
    _ = veil_engine.create_node("test_location", initial_silence=0.9)
    triggered = veil_engine.propagate_silence(delta=0.2)

    assert len(triggered) > 0
    assert triggered[0]["effect"] == "rumor"
    assert triggered[0]["silence_level"] == 1.1


def test_node_collapse(veil_engine):
    node_id = veil_engine.create_node("test_location", initial_silence=4.9)
    veil_engine.propagate_silence(delta=0.2)

    state = veil_engine.get_node_state(node_id)
    assert state is not None
    assert state.active is False
