from datetime import datetime, timedelta

from server.engine.lattice_director_engine import LatticeDirectorEngine
from server.engine.lattice_engine import RipenessLevel
from server.engine.peripheral_lattice_engine import PeripheralLatticeEngine


class _LegacyStub:
    pass


def test_offer_decline_and_tick_to_burst():
    lattice = PeripheralLatticeEngine("world-test", _LegacyStub())

    offered = lattice.offer_choices(
        [
            {
                "name": "Protect the bridge",
                "description": "Bandits threaten the trade route.",
                "pressure_type": "time",
                "pressure": "They strike before dawn",
                "mundane_anchors": ["Scout", "Ask locals"],
            }
        ]
    )
    assert len(offered) == 1

    current = lattice.decline_choice(offered[0].id, "Need to prioritize another front")
    assert current.ripeness == RipenessLevel.FRESH

    # Force burst by simulating elapsed time.
    current.created_at = datetime.utcnow() - timedelta(days=6)
    changed = lattice.tick()

    assert len(changed) == 1
    assert changed[0]["new_ripeness"] == RipenessLevel.BURST.value
    assert current.burst_at is not None
    assert current.burst_description is not None


def test_director_grim_reminder_and_close_with_reverence():
    lattice = PeripheralLatticeEngine("world-test", _LegacyStub())
    director = LatticeDirectorEngine(lattice)

    offered = lattice.offer_choices(
        [
            {
                "name": "Answer the shrine call",
                "description": "The shrine bells ring nightly.",
                "pressure_type": "moral",
                "pressure": "Villagers are afraid",
                "mundane_anchors": ["Observe shrine", "Question elder"],
            }
        ]
    )
    current = lattice.decline_choice(offered[0].id)

    grim = director.introduce_grim_reminder(current.id)
    assert grim["move"] == "grim_reminder"
    assert lattice.open_currents[current.id].environmental_modifier is not None

    closed = director.close_with_reverence(current.id, "p1", "I restore the shrine by hand")
    assert closed["move"] == "close_with_reverence"
    assert lattice.open_currents[current.id].burst_at is not None


def test_session_reading_and_player_goal_weaving():
    lattice = PeripheralLatticeEngine("world-test", _LegacyStub())
    director = LatticeDirectorEngine(lattice)

    lattice.start_session("s-1")
    offered = lattice.offer_choices(
        [
            {
                "name": "Help Ironwatch",
                "description": "Ironwatch requests aid against smugglers.",
                "pressure_type": "cost",
                "pressure": "Supplies are dwindling",
                "mundane_anchors": ["Count supplies", "Inspect route"],
            }
        ]
    )
    current = lattice.decline_choice(offered[0].id)

    # Make it significant enough to appear in opening read.
    current.last_touched = datetime.utcnow() - timedelta(days=3)
    lattice.tick()

    opening = director.read_open_current_aloud()
    assert opening["move"] == "read_current"
    assert "message" in opening

    goal = lattice.add_player_nominated_goal("p1", "I want to stop the smugglers at Ironwatch")
    weaving = director.weave_player_goal(goal.description, "p1")
    assert weaving["move"] == "weave_goal"
