import pytest
from datetime import datetime, timedelta

from server.engine.anchor_engine import AnchorEngine, AnchorViolation


@pytest.fixture
def anchor_engine(db_session):
    return AnchorEngine(db_session, "test_world")


def test_mundane_actions_always_allowed(anchor_engine):
    assert anchor_engine.enforce_anchor(False) is True


def test_fantastic_needs_anchors(anchor_engine):
    with pytest.raises(AnchorViolation):
        anchor_engine.enforce_anchor(True)

    anchor_engine.record_action("mundane")

    with pytest.raises(AnchorViolation):
        anchor_engine.enforce_anchor(True)

    anchor_engine.record_action("mundane")
    assert anchor_engine.enforce_anchor(True) is True


def test_anchor_state_reporting(anchor_engine):
    state = anchor_engine.get_anchor_state()
    assert state["recent_mundane_count"] == 0
    assert state["needed_for_fantastic"] == 2

    anchor_engine.record_action("mundane")
    state = anchor_engine.get_anchor_state()
    assert state["recent_mundane_count"] == 1
    assert state["needed_for_fantastic"] == 1


def test_mundane_history_expiry(anchor_engine):
    old_time = datetime.utcnow() - timedelta(hours=2)
    anchor_engine.record_action("mundane", timestamp=old_time)
    assert len(anchor_engine.recent_mundane) == 0
