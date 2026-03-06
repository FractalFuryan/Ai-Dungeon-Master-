from dataclasses import asdict
from typing import Any, Dict, Optional

from server.engine.effects import EngineEffects
from server.engine.memythic_engine import SymbolInjection
from server.engine.party_origin_engine import PartyOrigin
from server.engine.reverence_engine import CharacterStatsView


class PartyService:
    def __init__(self, world_engine: Any):
        self.world = world_engine

    def apply(self, context: Dict[str, Any], roll_result: Any) -> Dict[str, Any]:
        updates: Dict[str, Any] = {}
        effects = EngineEffects()

        if not self.world.party:
            return {"updates": updates, "effects": effects}

        character = context.get("character")
        party = self.world.party

        if getattr(roll_result, "is_critical_failure", False):
            outcome = party.process_failure(character, roll_result, context)
            updates["failure"] = asdict(outcome)

            if context.get("party_action"):
                bond_result = self.world.bond_system.process_shared_failure(
                    party.id,
                    context.get("characters", []),
                    context.get("action", "unknown"),
                    roll_result,
                )
                effects.bond_events.append(bond_result)

            thread_name = "competence"
            session_id = context.get("session_id")
            if context.get("character_id"):
                thread_record = self.world.party_origin.record_thread(
                    party_id=party.id,
                    thread=thread_name,
                    player_id=context.get("character_id"),
                    note=f"Failed at {context.get('action', 'unknown')}",
                    session_id=session_id,
                )
                effects.thread_events.append(thread_record)

        elif getattr(roll_result, "is_critical_success", False):
            outcome = party.process_success(character, roll_result, context)
            updates["success"] = asdict(outcome)

            if context.get("party_action"):
                bond_result = self.world.bond_system.process_shared_victory(
                    party.id,
                    context.get("characters", []),
                    context.get("action", "unknown"),
                    roll_result,
                )
                effects.bond_events.append(bond_result)

        if character:
            stats = CharacterStatsView.from_character(character)
            action_context = dict(context)
            action_context["critical_success"] = bool(getattr(roll_result, "is_critical_success", False))
            action_context["active_symbols"] = len(self.world.shard_state.symbols)
            strain = self.world.strain.calculate_strain(action_context, stats)
            if strain > 0:
                updates["strain"] = party.add_memythic_strain(strain)
                outcome = self.world.strain.check_thresholds(party.memythic_strain)
                if outcome:
                    updates["strain_effects"] = self.world.strain.apply_strain_effects(party.memythic_strain)

        if context.get("artifact_used"):
            artifact_result = self.world.artifact_engine.use_artifact(
                context["artifact_used"],
                context.get("character_id", "unknown"),
                context,
            )
            updates["artifact"] = artifact_result
            effects.artifact_events.append(artifact_result)

            injection = SymbolInjection(
                symbol=artifact_result["symbol"],
                archetype=self.world.artifact_engine.artifacts[context["artifact_used"]].archetype,
                context=f"Artifact used: {artifact_result['artifact']}",
                intensity=0.5,
            )
            self.world.memythic.inject_symbol(injection)

        self.world.party_origin.persist_party_state(party)
        return {"updates": updates, "effects": effects}


class WorldService:
    def __init__(self, world_engine: Any):
        self.world = world_engine

    def apply(self, context: Dict[str, Any], roll_result: Any) -> Dict[str, Any]:
        updates = self.world._apply_world_updates(roll_result, context)
        effects = EngineEffects(world_events=[{"type": "world_updates", "count": len(updates)}])
        return {"updates": updates, "effects": effects}


class NarrativeService:
    def __init__(self, world_engine: Any):
        self.world = world_engine

    def describe(self, roll_result: Any, context: Dict[str, Any], world_updates: Dict[str, Any], director_move: Optional[Dict[str, Any]]) -> str:
        return self.world._generate_narrative(roll_result, context, world_updates, director_move)
