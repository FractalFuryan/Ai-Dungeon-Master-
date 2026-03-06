from datetime import datetime
import random
from typing import Any, Dict, List, Optional

from server.engine.lattice_engine import LatticeMarker, RipenessLevel
from server.engine.peripheral_lattice_engine import PeripheralLatticeEngine


class LatticeDirectorEngine:
    """Director interventions that make peripheral lattice consequences visible."""

    def __init__(self, lattice: PeripheralLatticeEngine):
        self.lattice = lattice
        self.last_director_move: Optional[datetime] = None

    def read_open_current_aloud(self) -> Dict[str, Any]:
        currents = self.lattice.get_open_currents_for_session_start()
        if not currents:
            return {"move": "read_current", "message": "The lattice is quiet. For now."}

        current = currents[0]
        reading = self._dramatize_current(current)
        self.last_director_move = datetime.utcnow()
        return {
            "move": "read_current",
            "current": current,
            "reading": reading,
            "message": f"The director reads from the Legacy Ledger:\n\n{reading}",
        }

    def _dramatize_current(self, current: Dict[str, Any]) -> str:
        base = current["description"]
        ripeness = current["ripeness"]

        if ripeness == RipenessLevel.FERMENTED.value:
            return f"The old wound deepens. {base} The pressure mounts."
        if ripeness == RipenessLevel.RIPENING.value:
            return f"A thread pulls tight. {base} Something stirs in the periphery."
        return f"The world remembers: {base}"

    def faction_response(self, faction_id: str, event: str) -> Dict[str, Any]:
        self.lattice.update_faction_reputation(
            faction_id=faction_id,
            event="director_move",
            players_involved=[],
            context={"reason": event, "reputation_change": 1},
        )

        templates = [
            f"The {faction_id} takes notice of your wake. They {event}.",
            f"Word reaches the {faction_id}. They {event}.",
            f"The {faction_id} whispers among themselves: {event}",
        ]
        return {
            "move": "faction_response",
            "faction": faction_id,
            "event": event,
            "description": random.choice(templates),
        }

    def weave_player_goal(self, player_goal: str, player_id: str) -> Dict[str, Any]:
        best_current = None
        best_score = 0

        for current in self.lattice.open_currents.values():
            if current.burst_at:
                continue

            score = 0
            if current.ripeness in {RipenessLevel.FERMENTED, RipenessLevel.RIPENING}:
                score += 2

            goal_lower = player_goal.lower()
            current_lower = current.description.lower()
            for word in goal_lower.split():
                if len(word) > 3 and word in current_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_current = current

        if best_current and best_score >= 2:
            best_current.evolution_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "player_goal_woven",
                    "player": player_id,
                    "goal": player_goal,
                }
            )
            return {
                "move": "weave_goal",
                "woven": True,
                "current_id": best_current.id,
                "description": f"Your goal resonates with an open current: {best_current.description[:100]}...",
                "strength": best_score,
            }

        return {
            "move": "weave_goal",
            "woven": False,
            "description": "Your goal stands alone, waiting to create its own current.",
            "strength": 1,
        }

    def introduce_grim_reminder(self, current_id: str) -> Dict[str, Any]:
        current = self.lattice.open_currents.get(current_id)
        if not current:
            return {"error": "Current not found"}

        if LatticeMarker.GRIM_REMINDER not in current.markers:
            current.add_marker(LatticeMarker.GRIM_REMINDER, "director_introduced")
            current.environmental_modifier = {
                "type": "penalty",
                "value": -1,
                "description": f"The ignored {current.description[:50]} haunts this place.",
            }

        return {
            "move": "grim_reminder",
            "current_id": current_id,
            "description": f"The ignored becomes a grim reminder: {current.description}",
            "modifier": current.environmental_modifier,
        }

    def close_with_reverence(self, current_id: str, player_id: str, action: str) -> Dict[str, Any]:
        current = self.lattice.open_currents.get(current_id)
        if not current:
            return {"error": "Current not found"}

        current.evolution_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "closed_with_reverence",
                "player": player_id,
                "action": action,
            }
        )
        current.burst_at = datetime.utcnow()
        current.burst_description = f"Resolved with reverence by {player_id}: {action}"

        bonus = {
            "type": "reverence",
            "value": 1,
            "description": "Closed open current with creative action",
        }
        return {
            "move": "close_with_reverence",
            "current_id": current_id,
            "bonus": bonus,
            "description": "Your creative action weaves the current closed. The lattice remembers.",
        }

    def closing_ritual(self, player_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        ritual_record = {"timestamp": datetime.utcnow().isoformat(), "answers": player_answers}

        for answer in player_answers:
            player_id = answer.get("player_id", "unknown")
            choice_left = answer.get("choice_left_ripen")
            pressure_felt = answer.get("pressure_felt")
            goal_called = answer.get("goal_called")

            if choice_left:
                self.lattice.decline_choice(choice_left, f"Left to ripen: {pressure_felt}")
            if goal_called:
                self.weave_player_goal(str(goal_called), str(player_id))

        return {
            "move": "closing_ritual",
            "ritual": ritual_record,
            "message": "The open currents are spoken. The lattice breathes with your wake.",
        }
