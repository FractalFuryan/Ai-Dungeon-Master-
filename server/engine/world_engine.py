import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from server.config import config
from server.engine.artifact_engine import ArtifactEngine
from server.engine.anchor_engine import AnchorEngine
from server.engine.bond_engine import PartyBondSystem
from server.engine.director_engine import DirectorEngine
from server.engine.effects import EngineEffects
from server.engine.ghoul_veil_engine import GhoulAspect, GhoulVeilEngine, VeilNodeState
from server.engine.inversion_engine import InversionEngine
from server.engine.largess_bank_engine import LargessBankEngine
from server.engine.largess_engine import ShardTransition
from server.engine.lattice_director_engine import LatticeDirectorEngine
from server.engine.lattice_engine import LatticeEngine
from server.engine.lattice_engine import CurrentType, LatticeMarker, OpenCurrent, RipenessLevel
from server.engine.legacy_ledger_engine import LedgerAuditEngine, LegacyFeatureType, LegacyLedgerEngine
from server.engine.legacy_engine import LegacyEngine
from server.engine.litany_oracle import LitanyWeightedOracle
from server.engine.memythic_engine import MemythicEngine, SymbolInjection
from server.engine.myth_graph_engine import EdgeType, MythGraphEngine, NodeType
from server.engine.oracle_engine import OracleEngine, OracleIntent
from server.engine.party_origin_engine import PartyOriginEngine
from server.engine.peripheral_lattice_engine import PeripheralLatticeEngine
from server.engine.pressure_engine import NarrativePressureEngine
from server.engine.retirement_engine import RetirementEngine
from server.engine.reverence_engine import ReverenceEngine, StrainEngine
from server.engine.reweave_director_engine import ReweaveDirectorEngine
from server.engine.registry import EngineRegistry
from server.engine.rumor_engine import RumorEngine
from server.engine.shard_engine import MemythicEvent, ShardEngine
from server.engine.services import NarrativeService, PartyService, WorldService
from server.engine.thread_engine import ThreadEngine
from server.engine.veil_engine import VeilEngine
from server.mechanics.dice import DiceEngine, RandomnessMode

logger = logging.getLogger(__name__)


class WorldEngine:
    """Main orchestrator for myth-aware action resolution and world progression."""

    def __init__(self, db: Session, world_id: str, party_id: Optional[str] = None):
        self.db = db
        self.world_id = world_id
        self.dice = DiceEngine(mode=RandomnessMode(config.RANDOMNESS_MODE), seed=config.RANDOMNESS_SEED)

        self.registry = EngineRegistry()

        shard_engine = ShardEngine(db)
        self.registry.register("shard", shard_engine)
        self.shard = shard_engine
        self.shard_state = shard_engine.get_or_create_shard_for_world(world_id)

        base_oracle = OracleEngine()
        self.registry.register("oracle", base_oracle)
        self.oracle = self.registry.get("oracle")

        self.registry.register("memythic", MemythicEngine(self.shard_state, db_session=db, world_id=world_id))
        self.memythic = self.registry.get("memythic")

        self.registry.register("anchor", AnchorEngine(db, world_id))
        self.registry.register("veil", VeilEngine(db, world_id))
        self.registry.register("legacy", LegacyEngine(db, world_id))
        self.registry.register("lattice_currents", LatticeEngine(db, world_id))
        self.registry.register("rumor", RumorEngine(db, world_id))
        self.registry.register("inversion", InversionEngine(db))
        self.registry.register("pressure", NarrativePressureEngine(db, world_id))
        self.registry.register("threads", ThreadEngine(db, world_id))
        self.registry.register("director", DirectorEngine(db, world_id, self.shard, self.memythic))

        self.anchor = self.registry.get("anchor")
        self.veil = self.registry.get("veil")
        self.legacy = self.registry.get("legacy")
        self.lattice_currents = self.registry.get("lattice_currents")
        self.rumor = self.registry.get("rumor")
        self.inversion = self.registry.get("inversion")
        self.pressure = self.registry.get("pressure")
        self.threads = self.registry.get("threads")
        self.director = self.registry.get("director")

        # Party-origin systems.
        self.party_origin = PartyOriginEngine(db, world_id)
        self.party = self.party_origin.get_party(party_id) if party_id else None
        self.reverence = ReverenceEngine()
        self.strain = StrainEngine()
        self.bond_system = PartyBondSystem(db, world_id)
        self.artifact_engine = ArtifactEngine(db, world_id)

        # Legacy + ritual systems.
        self.ledger = LegacyLedgerEngine(world_id)
        self.ledger_audit = LedgerAuditEngine(self.ledger)
        self.retirement = RetirementEngine(self.ledger)

        # Peripheral Lattice Protocol.
        self.lattice = PeripheralLatticeEngine(world_id, self.ledger)
        self.lattice_director = LatticeDirectorEngine(self.lattice)

        # Largess + Reweave Protocol.
        self.largess_bank = LargessBankEngine(db_session=db, world_id=world_id)
        self.reweave_director = ReweaveDirectorEngine(self.largess_bank)

        # Myth graph system.
        self.myth_graph = MythGraphEngine(world_id)

        # Ghoul Hunger Veil.
        self.ghoul_veil = GhoulVeilEngine(world_id, anchor_map_id="orphans_coast")

        if self.party:
            self.oracle = LitanyWeightedOracle(base_oracle, self.party)

        self.party_service = PartyService(self)
        self.world_service = WorldService(self)
        self.narrative_service = NarrativeService(self)

        logger.info("Legacy systems initialized for world %s", world_id)
        logger.info("Peripheral lattice initialized for world %s", world_id)
        logger.info("Largess systems initialized for world %s", world_id)
        logger.info("Ghoul veil initialized for world %s", world_id)

    def resolve_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action_type = context.get("action_type", "mundane")
        is_fantastical = action_type == "fantastical"

        try:
            self.anchor.enforce_anchor(is_fantastical, context=context)
            modifiers = self._gather_modifiers(context)
            roll_result = self.dice.resolve(
                base_modifier=int(context.get("base_modifier", 0)),
                positives=modifiers.get("positives", []),
                negatives=modifiers.get("negatives", []),
                metadata={"action_id": context.get("action_id")},
            )

            if self.shard_state.memythic_charge >= self.shard_state.dream_logic_threshold:
                roll_result.metadata = self.shard_state.apply_dream_logic(roll_result.to_dict())

            if self._should_inject_symbol(roll_result, context):
                self._inject_symbol_from_action(roll_result, context)

            world_result = self.world_service.apply(context, roll_result)
            world_updates = world_result["updates"]
            party_result = self.party_service.apply(context, roll_result)
            party_updates = party_result["updates"]
            effects = EngineEffects().merge(world_result["effects"]).merge(party_result["effects"])
            director_move = self._check_director_intervention(context, world_updates)
            narrative = self.narrative_service.describe(roll_result, context, world_updates, director_move)
            self.shard.persist_runtime_state(self.shard_state)

            return {
                "success": True,
                "roll": roll_result.to_dict(),
                "world_updates": world_updates,
                "party_updates": party_updates,
                "effects": effects.to_dict(),
                "director_move": director_move,
                "narrative": narrative,
                "anchor_state": self.anchor.get_anchor_state(),
                "shard_state": self.shard_state.to_dict(),
                "party_state": self.party.get_state() if self.party else None,
            }
        except Exception as exc:
            logger.error("Action resolution failed: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "anchor_state": self.anchor.get_anchor_state(),
            }

    def _gather_modifiers(self, context: Dict[str, Any]) -> Dict[str, Any]:
        modifiers = {
            "positives": [int(v) for v in context.get("positives", [])],
            "negatives": [int(v) for v in context.get("negatives", [])],
        }

        character_id = context.get("character_id")
        if character_id:
            _ = self.legacy.apply_legacy_effects(character_id, context)

        location_id = context.get("location_id")
        if location_id:
            _ = self.lattice_currents.get_location_effects(location_id)
            fields = self.pressure.get_fields_at_location(location_id)
            for field in fields:
                if field["pull"] > 0.5:
                    if field["type"] == "attraction":
                        modifiers["positives"].append(int(field["pull"] * 0.1))
                    elif field["type"] == "repulsion":
                        modifiers["negatives"].append(int(field["pull"] * 0.1))

        return modifiers

    def _should_inject_symbol(self, roll_result: Any, context: Dict[str, Any]) -> bool:
        if roll_result.is_critical_success or roll_result.is_critical_failure:
            return True
        if self.shard_state.memythic_charge > 5.0:
            return random.random() < 0.3
        return False

    def _inject_symbol_from_action(self, roll_result: Any, context: Dict[str, Any]) -> None:
        intent = OracleIntent.CLARITY if roll_result.is_critical_success else OracleIntent.MYSTERY

        # Behavior-driven symbol overrides before oracle draw.
        explicit_symbol: Dict[str, Any] | None = None
        description = str(context.get("description", "")).lower()
        if "betray" in description:
            explicit_symbol = {"symbol": "mask", "archetype": "identity", "meaning": "A hidden face is revealed.", "intensity": 0.8}
        elif roll_result.total <= 6:
            explicit_symbol = {"symbol": "shadow", "archetype": "concealment", "meaning": "Failure feeds the dark edge of the story.", "intensity": 0.7}
        elif roll_result.total >= 16:
            explicit_symbol = {"symbol": "crown", "archetype": "authority", "meaning": "Victory claims symbolic weight.", "intensity": 0.7}

        if explicit_symbol is None:
            drawn = self.oracle.draw_symbol(intent, context.get("description"))
            symbol_data = {
                "symbol": drawn.symbol,
                "archetype": drawn.archetype,
                "meaning": drawn.meaning,
                "intensity": drawn.intensity,
            }
        else:
            symbol_data = explicit_symbol

        injection = SymbolInjection(
            symbol=symbol_data["symbol"],
            archetype=symbol_data["archetype"],
            context=symbol_data["meaning"],
            intensity=float(symbol_data["intensity"]) * (1.5 if roll_result.is_critical_success else 1.0),
        )
        self.memythic.inject_symbol(injection)

        event = MemythicEvent(
            id=f"sym_{datetime.utcnow().timestamp()}",
            event_type="symbol_injection",
            description=f"Symbol {symbol_data['symbol']} manifests: {symbol_data['meaning']}",
            impact=float(symbol_data["intensity"]),
            symbols_involved=[symbol_data["symbol"]],
            location_id=context.get("location_id"),
            character_id=context.get("character_id"),
        )
        self.shard_state.register_event(event)

    def _apply_world_updates(self, roll_result: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        # Keep action-time simulation light; heavy updates run in world_tick.
        updates: Dict[str, Any] = {}

        if roll_result.is_critical_failure:
            updates["veil_triggers"] = self.veil.propagate_all(delta=0.5)

        if roll_result.total > 15:
            updates["rumor"] = self.rumor.ripen_rumors(delta=0.3)

        updates["lattice"] = self.lattice_currents.tick(delta=0.02)
        self._record_world_event(context, roll_result, updates)
        return updates

    def _check_director_intervention(self, context: Dict[str, Any], world_updates: Dict[str, Any]) -> Any:
        world_state = {
            "tension": context.get("tension", 0.5),
            "memythic_charge": self.shard_state.memythic_charge,
            "recent_events": len(world_updates),
            "location_id": context.get("location_id"),
        }
        move_name = self.director.should_intervene(world_state)
        if move_name:
            return self.director.execute_move(move_name, context)
        return None

    def _generate_narrative(
        self,
        roll_result: Any,
        context: Dict[str, Any],
        world_updates: Dict[str, Any],
        director_move: Any,
    ) -> str:
        parts = []
        if roll_result.is_critical_success:
            parts.append("A spectacular success. The dice smile upon you.")
        elif roll_result.is_critical_failure:
            parts.append("Disaster strikes. The fates have turned against you.")
        else:
            parts.append(f"You roll {roll_result.rolls} for a total of {roll_result.total}.")

        if roll_result.metadata and isinstance(roll_result.metadata, dict) and "dream_influence" in roll_result.metadata:
            influence = roll_result.metadata["dream_influence"]
            parts.append(f"The {influence['symbol']} influences reality.")

        if "veil_triggers" in world_updates and world_updates["veil_triggers"]:
            parts.append("The veil shifts and silence deepens.")

        if director_move:
            parts.append(f"[DIRECTOR CUT: {director_move['description']}]")

        return " ".join(parts)

    def _record_world_event(self, context: Dict[str, Any], roll_result: Any, updates: Dict[str, Any]) -> None:
        from server.persistence.models import WorldEvent

        event = WorldEvent(
            world_id=self.world_id,
            session_id=context.get("session_id"),
            character_id=context.get("character_id"),
            location_id=context.get("location_id"),
            event_type="action_resolution",
            description=f"Action resolved with total {roll_result.total}",
            payload={
                "rolls": roll_result.rolls,
                "modifier": roll_result.modifier,
                "critical": roll_result.critical,
                "updates": updates,
                "context": context,
            },
        )
        self.db.add(event)
        self.db.commit()

    def world_tick(self) -> Dict[str, Any]:
        updates = {
            "veil_updates": self.veil.propagate_all(delta=0.1),
            "pressure_updates": self.pressure.pulse_all_fields(),
            "field_collisions": self.pressure.field_collisions(),
            "memythic_updates": self.memythic.fluctuate(),
            "lattice_updates": self.lattice_currents.tick(),
            "peripheral_lattice_updates": self.lattice_tick(),
            "thread_updates": self.threads.ripen(delta=0.1),
            "rumor_updates": self.rumor.ripen_rumors(delta=0.2),
            "timestamp": datetime.utcnow().isoformat(),
        }

        world_state = {
            "tension": 0.3,
            "memythic_charge": self.shard_state.memythic_charge,
            "recent_events": len(updates.get("veil_updates", [])),
        }
        move_name = self.director.should_intervene(world_state)
        if move_name:
            updates["director_move"] = self.director.execute_move(move_name, {"scope": "world_tick"})

        from server.persistence.models import WorldEvent

        event = WorldEvent(
            world_id=self.world_id,
            event_type="world_tick",
            description="World state advanced",
            payload=updates,
        )
        self.db.add(event)
        self.db.commit()
        self.shard.persist_runtime_state(self.shard_state)
        return updates

    def get_world_state_snapshot(self) -> Dict[str, Any]:
        self.veil._load_nodes()
        return {
            "world_id": self.world_id,
            "engines": self.registry.snapshot(),
            "shard": self.shard_state.to_dict(),
            "symbols": self.memythic.get_dominant_symbols(5),
            "veil": {node_id: self.veil.get_node_state_detail(node_id) for node_id in self.veil.nodes.keys()},
            "pressure": [
                {
                    "id": f.id,
                    "name": f.name,
                    "type": f.influence_type,
                    "strength": f.strength,
                    "radius": f.radius,
                }
                for f in self.pressure.fields.values()
            ],
            "threads": self.threads.list_threads(include_resolved=False),
            "director": self.director.get_recent_moves(5),
            "party": self.get_party_state(),
            "peripheral_lattice": self.get_lattice_state(),
        }

    def get_party_state(self) -> Dict[str, Any]:
        if not self.party:
            return {}

        return {
            "origin": self.party.get_state(),
            "bond": self.bond_system.get_bond_engine(self.party.id, initial_value=self.party.bond.value).get_shared_memories(),
            "threads": self.party.tested_threads,
            "artifacts": self.artifact_engine.get_all_artifacts(discovered_only=True),
            "strain": self.party.memythic_strain,
        }

    def record_session_thread(self, thread: str, player_id: str, note: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.party:
            return None
        return self.party_origin.record_thread(self.party.id, thread, player_id, note, session_id=session_id)

    def discover_artifact(self, artifact_key: str, location_id: str) -> Dict[str, Any]:
        return self.artifact_engine.discover_artifact(artifact_key, location_id)

    def perform_retirement(
        self,
        character: Any,
        player_id: str,
        final_act: str,
        feature_type: Optional[str] = None,
        chosen_location: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = self.retirement.perform_retirement(
            character=character,
            player_id=player_id,
            final_act_description=final_act,
            chosen_feature_type=LegacyFeatureType(feature_type) if feature_type else None,
            chosen_location=chosen_location,
            campaign_id=self.world_id,
        )

        if result.get("success"):
            self.anchor.register_ritual(
                description=f"Retirement ritual for {character.name}",
                context={"player_id": player_id, "final_act": final_act},
            )

            char_node = self.myth_graph.add_node(
                name=character.name,
                node_type=NodeType.CHARACTER,
                properties={"player": player_id, "level": int(getattr(character, "level", 1))},
            )

            for feature in result["ledger_entry"]["features"]:
                feature_node = self.myth_graph.add_node(
                    name=feature["name"],
                    node_type=NodeType.LEGACY_FEATURE,
                    properties={"description": feature["description"]},
                )
                self.myth_graph.add_edge(
                    source_id=char_node.id,
                    target_id=feature_node.id,
                    edge_type=EdgeType.CREATED,
                    properties={"final_act": final_act},
                )

            logger.info("Added retirement to myth graph for %s", character.name)

        return result

    def audit_ledger(self) -> str:
        return self.ledger_audit.audit()

    def report_vector(self, player_id: str, description: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        correction = self.anchor.vector_detection.report_vector(player_id, description, context)
        if correction:
            logger.warning("Vector correction needed: %s", correction)
        return correction

    def add_to_myth_graph(
        self,
        name: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
        connections: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
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

    def get_legacy_state(self) -> Dict[str, Any]:
        return {
            "ledger": self.ledger.get_ledger_state(),
            "anchor": self.anchor.get_anchor_state(),
            "myth_graph": {
                "nodes": len(self.myth_graph.nodes),
                "edges": len(self.myth_graph.edges),
            },
        }

    def start_session_with_lattice(self, session_id: str) -> Dict[str, Any]:
        self.lattice.start_session(session_id)
        return self.lattice_director.read_open_current_aloud()

    def offer_session_choices(self, motive_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        offered = self.lattice.offer_choices(motive_nodes)
        return [node.to_dict() for node in offered]

    def handle_choice(
        self,
        node_id: str,
        accept: bool,
        player_ids: List[str],
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        if accept:
            return self.lattice.accept_choice(node_id, player_ids)

        current = self.lattice.decline_choice(node_id, reason)
        if random.random() < 0.3:
            self.lattice_director.introduce_grim_reminder(current.id)

        return {
            "declined": True,
            "open_current": current.to_dict(),
        }

    def add_player_goal(self, player_id: str, goal: str, wyrd_thread_id: Optional[str] = None) -> Dict[str, Any]:
        node = self.lattice.add_player_nominated_goal(player_id, goal, wyrd_thread_id)
        weaving = self.lattice_director.weave_player_goal(goal, player_id)
        return {
            "goal": node.to_dict(),
            "weaving": weaving,
        }

    def lattice_tick(self) -> Dict[str, Any]:
        changed = self.lattice.tick()
        burst: List[Dict[str, Any]] = []

        for current_id, current in self.lattice.open_currents.items():
            if current.burst_at and current.burst_at > datetime.utcnow() - timedelta(minutes=5):
                burst.append(
                    {
                        "id": current_id,
                        "description": current.burst_description,
                        "type": "grim_reminder" if current.environmental_modifier else "event",
                    }
                )

        return {
            "changed_count": len(changed),
            "changed": changed,
            "burst": burst,
            "total_currents": len(self.lattice.open_currents),
        }

    def closing_ritual(self, player_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.lattice_director.closing_ritual(player_answers)

    def get_lattice_state(self) -> Dict[str, Any]:
        return self.lattice.get_lattice_state()

    def close_shard(self, shard_name: str, final_ritual_words: List[str]) -> Dict[str, Any]:
        open_currents: List[Dict[str, Any]] = []
        for current in self.lattice.open_currents.values():
            if current.burst_at:
                continue
            open_currents.append(
                {
                    "description": current.description,
                    "ripeness": current.ripeness.value,
                    "type": current.current_type.value,
                }
            )

        retired = [
            {
                "name": e.character_name,
                "reverence_points": e.reverence_points,
            }
            for e in self.ledger.entries
        ]

        player_intents: List[Dict[str, Any]] = []
        grave = self.largess_bank.close_shard(
            shard_name=shard_name,
            campaign_id=self.world_id,
            legacy_ledger_id=self.world_id,
            final_ritual_words=final_ritual_words,
            open_currents=open_currents,
            retired_characters=retired,
            player_intents=player_intents,
        )

        return {
            "grave": grave.to_dict(),
            "message": (
                f"The shard of {shard_name} is now a grave, seeded with "
                f"{len(grave.largess_seeds)} pieces of largess."
            ),
        }

    def dawn_new_shard(
        self,
        shard_name: str,
        transition_type: str,
        source_grave_id: str,
        players: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            transition = ShardTransition(transition_type)
        except ValueError as exc:
            raise ValueError(f"Invalid transition type: {transition_type}") from exc

        result = self.reweave_director.reweave_dawn_rite(
            shard_name=shard_name,
            transition_type=transition,
            source_grave_id=source_grave_id,
            players=players,
        )

        self.world_id = result["dawn"]["id"]
        return result

    def grave_interview(self, player_id: str, character_name: str, seed_id: str, intent: str) -> Dict[str, Any]:
        return self.reweave_director.grave_interview(
            player_id=player_id,
            character_name=character_name,
            seed_id=seed_id,
            intent=intent,
        )

    def get_grave_prompts(self, grave_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not grave_id and self.reweave_director.current_dawn:
            grave_id = self.reweave_director.current_dawn.source_grave_id

        if not grave_id:
            return []
        return self.largess_bank.get_grave_interview_prompt(grave_id)

    def closing_largess_ritual(self, players: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.reweave_director.closing_largess_ritual(players)

    def get_largess_state(self) -> Dict[str, Any]:
        return {
            "bank": self.largess_bank.get_bank_state(),
            "reweave": self.reweave_director.get_reweave_state(),
        }

    def coast_ink_ritual(
        self,
        player_id: str,
        character_name: str,
        location_name: str,
        description: str,
        x: float,
        y: float,
    ) -> Dict[str, Any]:
        node = self.ghoul_veil.coast_ink_ritual(
            player_id=player_id,
            character_name=character_name,
            location_name=location_name,
            description=description,
            coordinates=(x, y),
        )

        # Feed the new inked silence into peripheral lattice as an open current.
        if hasattr(self, "lattice"):
            current = OpenCurrent(
                id=f"ghoul_node_{node.id}",
                current_type=CurrentType.IGNORED_LOCATION,
                description=f"Inked ghoul sighting at {location_name}: {description}",
                created_at=datetime.utcnow(),
                last_touched=None,
                ripeness=RipenessLevel.FRESH,
                markers=[LatticeMarker.RUMOR],
                location_id=location_name,
                faction_ids=[],
                npc_ids=[],
                wyrd_thread_ids=[],
            )
            self.lattice.open_currents[current.id] = current

        return {
            "node": node.to_dict(),
            "message": f"The silence near {location_name} is now marked on the map. The veil grows thinner.",
        }

    def rumor_fulcrum(self) -> Dict[str, Any]:
        return self.ghoul_veil.rumor_fulcrum_opening()

    def imagine_ghoul(
        self,
        player_id: str,
        character_name: str,
        aspect: str,
        description: str,
        node_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            ghoul_aspect = GhoulAspect(aspect)
        except ValueError as exc:
            raise ValueError(f"Invalid aspect: {aspect}") from exc

        vision = self.ghoul_veil.imagination_completion(
            player_id=player_id,
            character_name=character_name,
            aspect=ghoul_aspect,
            description=description,
            node_id=node_id,
        )

        encounter = None
        if node_id and random.random() < 0.3:
            node = self.ghoul_veil.nodes.get(node_id)
            if node and node.state == VeilNodeState.HUNGRY:
                encounter = self.ghoul_veil.trigger_encounter(node_id=node_id, players=[player_id])

        return {
            "vision": vision.to_dict(),
            "encounter": encounter.to_dict() if encounter else None,
            "message": f"You see {description}. The blanks fill with your fear.",
        }

    def trigger_ghoul_encounter(self, node_id: str, players: List[str]) -> Dict[str, Any]:
        encounter = self.ghoul_veil.trigger_encounter(node_id, players)

        anchor_check = {}
        for player_id in players:
            player_nodes = [n for n in self.ghoul_veil.nodes.values() if n.inked_by == player_id]
            anchor_check[player_id] = {
                "has_anchors": len(player_nodes) >= 2,
                "anchor_count": len(player_nodes),
            }

        return {
            "encounter": encounter.to_dict(),
            "anchor_check": anchor_check,
            "message": "The sketch lies on the table. Silence. What do you see in the blanks?",
        }

    def daylight_burn(
        self,
        encounter_id: str,
        player_id: str,
        vulnerability: str,
        pay_with_reverence: bool = True,
    ) -> Dict[str, Any]:
        result = self.ghoul_veil.daylight_burn(
            encounter_id=encounter_id,
            player_id=player_id,
            vulnerability=vulnerability,
            pay_with_reverence=pay_with_reverence,
        )

        # Try to consume one available reverence token when paying with reverence.
        if pay_with_reverence and self.party:
            tokens = self.party.get_unused_tokens()
            if tokens:
                self.party.use_reverence_token(tokens[0].id)
                self.party_origin.tokens.mark_used(tokens[0].id, used_at=datetime.utcnow())

        return result

    def ghoul_closing_ritual(self, players: List[Dict[str, Any]]) -> Dict[str, Any]:
        answers = self.ghoul_veil.closing_ritual(players)
        return {
            "ritual": "ghoul_veil_closing",
            "answers": answers,
            "message": "The veil is spoken. The blanks remember what you saw.",
        }

    def get_ghoul_state(self) -> Dict[str, Any]:
        return self.ghoul_veil.get_veil_state()
