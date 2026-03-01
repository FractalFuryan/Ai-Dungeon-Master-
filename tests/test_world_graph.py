from server.dm_engine import process_roll20_event
from server.memory import get_memory


def test_faction_and_npc_reactivity_pipeline():
    session_id = "world_graph_test"

    # Event 1: cooperative action helping merchant interests in shared district
    process_roll20_event(
        session_id=session_id,
        player_name="Aria",
        text="I help the merchant guild secure trade routes in the market_district and support the guards.",
        selected=[],
    )

    mem = get_memory(session_id)
    world = mem["world_graph"]

    assert "factions" in world
    assert "merchant_guild" in world["factions"]
    assert "city_guard" in world["factions"]

    merchant_attitude = world["factions"]["merchant_guild"]["attitude"]["players"]
    assert merchant_attitude >= 0.1  # Should not degrade from baseline after cooperative alignment

    # Event 2: direct disruptive action against Elara's faction to trigger memory update
    process_roll20_event(
        session_id=session_id,
        player_name="Aria",
        text="I betray the Shadow Exchange and burn their docks while guards close in on Elara.",
        selected=[],
    )

    mem2 = get_memory(session_id)
    world2 = mem2["world_graph"]

    assert len(world2.get("faction_log", [])) >= 1
    assert "elara" in world2.get("npcs", {})
    assert len(world2["npcs"]["elara"].get("memory", [])) >= 1

    # Hooks are deterministic; list can be empty depending on trust thresholds,
    # but pending_hooks key must always exist for next-session seed pipeline.
    assert "pending_hooks" in world2
    assert isinstance(world2["pending_hooks"], list)
