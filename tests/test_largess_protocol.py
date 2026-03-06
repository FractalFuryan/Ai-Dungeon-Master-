from server.engine.largess_bank_engine import LargessBankEngine
from server.engine.largess_engine import LargessType, ShardTransition
from server.engine.reweave_director_engine import ReweaveDirectorEngine


def test_close_shard_banks_open_currents_and_intents():
    bank = LargessBankEngine()

    grave = bank.close_shard(
        shard_name="Age of Smoke",
        campaign_id="w-1",
        legacy_ledger_id="ledger-1",
        final_ritual_words=["We leave the torch lit."],
        open_currents=[
            {"description": "Ignored bell tower call", "ripeness": "fermented", "type": "ignored_location"},
            {"description": "Unsettled bridge debt", "ripeness": 1.0, "type": "declined_pressure"},
        ],
        retired_characters=[{"name": "Arin", "reverence_points": 2}],
        player_intents=[{"player_id": "p1", "character_name": "Arin", "intent": "Return to the bell tower"}],
    )

    assert grave.total_retirements == 1
    assert grave.total_reverence == 2
    assert len(grave.largess_seeds) == 3
    assert len(bank.seeds) == 3


def test_dawn_generates_motive_nodes_and_seed_claim_updates_state():
    bank = LargessBankEngine()

    grave = bank.close_shard(
        shard_name="Age of Ash",
        campaign_id="w-2",
        legacy_ledger_id="ledger-2",
        final_ritual_words=["Ash remembers."],
        open_currents=[{"description": "Forgotten shrine warning", "ripeness": "ripening", "type": "forgotten_npc"}],
        retired_characters=[],
        player_intents=[],
    )

    dawn = bank.dawn_new_shard(
        name="Age of Root",
        transition_type=ShardTransition.REMIX,
        source_grave_id=grave.id,
        player_count=3,
    )

    assert dawn.transition_type == ShardTransition.REMIX
    assert len(dawn.starting_motive_nodes) >= 1

    seed_id = grave.largess_seeds[0].id
    claimed = bank.claim_seed(seed_id, "c-new", "p-new", "I reclaim the shrine line")
    assert claimed.claimed is True
    assert claimed.claimed_by == "c-new"


def test_reweave_director_rite_and_interview_flow():
    bank = LargessBankEngine()
    director = ReweaveDirectorEngine(bank)

    grave = bank.close_shard(
        shard_name="Age of Glass",
        campaign_id="w-3",
        legacy_ledger_id="ledger-3",
        final_ritual_words=["The mirror closes."],
        open_currents=[{"description": "Echo under the quay", "ripeness": "fresh", "type": "unanswered_quest"}],
        retired_characters=[],
        player_intents=[],
    )

    dawn_result = director.reweave_dawn_rite(
        shard_name="Age of Iron",
        transition_type=ShardTransition.FORWARD_FLOW,
        source_grave_id=grave.id,
        players=[{"id": "p1", "character_name": "Mara"}],
    )
    assert dawn_result["ritual"] == "reweave_dawn"

    prompts = bank.get_grave_interview_prompt(grave.id)
    assert len(prompts) >= 1

    interview = director.grave_interview(
        player_id="p1",
        character_name="Mara",
        seed_id=prompts[0]["seed_id"],
        intent="I will finish what they left undone",
    )
    assert interview["ritual"] == "grave_interview"

    # Closing ritual should include spoken words.
    closing = director.closing_largess_ritual(players=[{"id": "p1", "character_name": "Mara"}])
    assert closing["ritual"] == "closing_largess"
    assert len(closing["final_words"]) == 1


def test_calculate_starting_boons_includes_reverence_echo_bonus():
    bank = LargessBankEngine()
    grave = bank.close_shard(
        shard_name="Age of Tide",
        campaign_id="w-4",
        legacy_ledger_id="ledger-4",
        final_ritual_words=[],
        open_currents=[],
        retired_characters=[{"name": "Iven", "reverence_points": 6}],
        player_intents=[],
    )

    # Inject a reverence seed explicitly for boon coverage.
    reverence_seed = grave.largess_seeds
    assert isinstance(reverence_seed, list)

    # Manually create + claim one reverence seed for deterministic coverage.
    from datetime import datetime
    import uuid

    seed_id = str(uuid.uuid4())
    from server.engine.largess_engine import LargessSeed

    seed = LargessSeed(
        id=seed_id,
        seed_type=LargessType.REVERENCE_ECHO,
        description="A bell still hums with reverence.",
        source_character="Iven",
        source_player="p-iven",
        created_at=datetime.utcnow(),
        campaign_id="w-4",
    )
    bank.seeds[seed_id] = seed
    grave.largess_seeds.append(seed)

    bank.claim_seed(seed_id, "c-1", "p-1", "I inherit the bell")
    boons = bank.calculate_starting_boons(grave.id, [seed_id])
    assert boons["starting_xp_bonus"] >= 0
    assert boons.get("reverence_starting", 0) >= 1
