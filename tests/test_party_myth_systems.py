from server.engine.artifact_engine import ArtifactEngine
from server.engine.bond_engine import BondEventType, PartyBondSystem
from server.engine.litany_oracle import LitanyWeightedOracle
from server.engine.oracle_engine import OracleEngine, OracleIntent
from server.engine.party_origin_engine import LitanyCut, PartyOriginEngine
from server.engine.reverence_engine import CharacterStatsView, ReverenceEngine, StrainEngine


class _Roll:
    def __init__(self, crit_fail=False, crit_success=False):
        self.is_critical_failure = crit_fail
        self.is_critical_success = crit_success


class _Char:
    def __init__(self, cid="c1", name="Arin"):
        self.id = cid
        self.name = name
        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.charisma = 10


def test_party_origin_creation_and_thread_persistence(db_session):
    engine = PartyOriginEngine(db_session, "world-1")
    party = engine.create_party(LitanyCut.NO_PATRON, "The Unbound")

    assert party.get_state()["litany_cut"] == "no_patron"

    rec = engine.record_thread(party.id, "competence", "player-1", "failed the gate", session_id="s1")
    assert rec["session_id"] == "s1"

    loaded = engine.get_party(party.id)
    assert loaded is not None
    assert len(loaded.tested_threads) == 1


def test_party_effects_typed_results(db_session):
    engine = PartyOriginEngine(db_session, "world-1")
    party = engine.create_party(LitanyCut.GLORY_NOT_BINDING, "Trauma Crew")

    result = party.process_failure(_Char(), _Roll(crit_fail=True), {"action": "climb"})
    assert result.bond_change == 2
    assert len(result.notes) > 0


def test_bond_system_records_custom_event(db_session):
    bonds = PartyBondSystem(db_session, "world-1")
    res = bonds.process_custom_event(
        party_id="party-1",
        event_type=BondEventType.RITUAL,
        description="Oath at the standing stones",
        characters=["c1", "c2"],
        context={},
    )
    assert res["bond_change"] >= 1


def test_artifact_discovery_and_usage(db_session):
    artifacts = ArtifactEngine(db_session, "world-1")
    found = artifacts.discover_artifact("troll", "loc-1")
    used = artifacts.use_artifact("troll", "c1", {"location_id": "loc-1"})

    assert found["artifact"] == "Troll's Heart"
    assert used["symbol"] == "regeneration"
    assert used["charge"] > 1.0


def test_litany_oracle_composition_draws_symbols():
    base = OracleEngine()

    class _Party:
        cut = LitanyCut.NO_PATRON

    oracle = LitanyWeightedOracle(base, _Party())
    draw = oracle.draw_symbol(OracleIntent.MYSTERY, "long context string for intensity")

    assert draw.symbol
    assert draw.intensity <= 1.0


def test_reverence_and_strain_views():
    rev = ReverenceEngine()
    stats = CharacterStatsView.from_character(_Char())
    xp, event = rev.calculate_xp_gain(stats, action_difficulty=1.0, success=True)
    assert xp >= 10
    assert event is not None

    strain_engine = StrainEngine()
    strain = strain_engine.calculate_strain(
        {
            "critical_success": True,
            "magic_item_used": True,
            "active_symbols": 4,
        },
        CharacterStatsView(16, 16, 16, 16, 16, 16),
    )
    assert strain > 0
