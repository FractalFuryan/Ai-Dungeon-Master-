from datetime import datetime, timedelta

from server.engine.ghoul_veil_engine import GhoulAspect, GhoulVeilEngine, VeilNodeState


def test_coast_ink_and_rumor_progression():
    veil = GhoulVeilEngine("w-ghoul", anchor_map_id="orphans_coast")

    node = veil.coast_ink_ritual(
        player_id="p1",
        character_name="Nyra",
        location_name="Broken Causeway",
        description="She heard marsh birds cut out at dusk.",
        coordinates=(12.5, 44.2),
    )
    assert node.state == VeilNodeState.DORMANT

    # Force state transitions by aging the node.
    node.inked_at = datetime.utcnow() - timedelta(days=10)
    result = veil.rumor_fulcrum_opening(days_silent=3)

    assert len(result["updates"]) >= 1
    assert veil.nodes[node.id].state in {VeilNodeState.WHISPERING, VeilNodeState.STALKING, VeilNodeState.HUNGRY}


def test_imagination_encounter_and_daylight_burn_resolution():
    veil = GhoulVeilEngine("w-ghoul", anchor_map_id="orphans_coast")
    node = veil.coast_ink_ritual(
        player_id="p1",
        character_name="Nyra",
        location_name="Old Shrine Road",
        description="The silence drips from the trees.",
        coordinates=(1.0, 2.0),
    )

    node.state = VeilNodeState.HUNGRY

    vision = veil.imagination_completion(
        player_id="p1",
        character_name="Nyra",
        aspect=GhoulAspect.FACE,
        description="Its face is my own, but empty-eyed.",
        node_id=node.id,
    )
    assert vision.aspect == GhoulAspect.FACE

    encounter = veil.trigger_encounter(node.id, ["p1"])
    assert encounter.resolved is False

    resolved = veil.daylight_burn(
        encounter_id=encounter.id,
        player_id="p1",
        vulnerability="fear of abandonment",
        pay_with_reverence=True,
    )
    assert resolved["resolved"] is True
    assert resolved["cost_type"] == "reverence"


def test_unanswered_hungry_nodes_ripen_to_grim_reminders():
    veil = GhoulVeilEngine("w-ghoul", anchor_map_id="orphans_coast")
    node = veil.coast_ink_ritual(
        player_id="p2",
        character_name="Tarin",
        location_name="Fen Mile",
        description="No frogs, no wind, no birds.",
        coordinates=(7.0, 9.0),
    )

    node.state = VeilNodeState.HUNGRY
    node.inked_at = datetime.utcnow() - timedelta(days=7)
    node.last_activity = datetime.utcnow() - timedelta(days=4)

    first = veil.unanswered_ripening()
    second = veil.unanswered_ripening()
    third = veil.unanswered_ripening()
    fourth = veil.unanswered_ripening()

    # Ripening increments by 0.2, so a reminder appears by the 4th pass.
    assert len(first) + len(second) + len(third) + len(fourth) >= 1
    assert veil.nodes[node.id].grim_reminder is not None
