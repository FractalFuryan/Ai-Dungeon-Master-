from typing import Any, Dict, List


class FactionEngine:
    def __init__(self, world_state: Dict[str, Any]):
        self.world = world_state
        self.factions = world_state.setdefault("factions", {})
        self.world.setdefault("faction_log", [])

    def apply_event_impact(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update factions based on player action and return a delta log."""
        deltas: List[Dict[str, Any]] = []

        for faction_id, faction in self.factions.items():
            impact = self._calculate_faction_impact(event, faction)
            if impact == 0:
                continue

            current_power = float(faction.get("power", 5.0))
            faction["power"] = max(1.0, min(10.0, current_power + impact))

            attitude = faction.setdefault("attitude", {})
            current_players = float(attitude.get("players", 0.0))
            attitude["players"] = max(-1.0, min(1.0, current_players + impact * 0.1))

            delta = {
                "faction": faction_id,
                "impact": round(impact, 3),
                "power": round(faction["power"], 3),
                "attitude_players": round(attitude["players"], 3),
                "event": event.get("action_text", ""),
            }
            deltas.append(delta)
            self._log_faction_event(delta)

        return deltas

    def update_power_balance(self) -> Dict[str, float]:
        """Simple balance snapshot useful for debugging and hooks."""
        if not self.factions:
            return {"min": 0.0, "max": 0.0, "spread": 0.0, "avg": 0.0}

        powers = [float(v.get("power", 0.0)) for v in self.factions.values()]
        minimum = min(powers)
        maximum = max(powers)
        avg = sum(powers) / len(powers)
        spread = maximum - minimum

        snapshot = {
            "min": round(minimum, 3),
            "max": round(maximum, 3),
            "spread": round(spread, 3),
            "avg": round(avg, 3),
        }
        self.world["faction_balance"] = snapshot
        return snapshot

    def _calculate_faction_impact(self, event: Dict[str, Any], faction: Dict[str, Any]) -> float:
        action_type = event.get("action_type", "neutral")
        action_text = event.get("action_text", "").lower()
        location = event.get("location", "").lower()

        faction_name = str(faction.get("name", "")).lower()
        territories = [str(t).lower() for t in faction.get("territory", [])]
        goals = [str(g).lower() for g in faction.get("goals", [])]

        impact = 0.0

        # Direct mentions
        if faction_name and faction_name in action_text:
            if action_type == "disrupt":
                impact -= 0.3
            elif action_type == "coop":
                impact += 0.2

        # Territory pressure
        if location and location in territories and action_type == "disrupt":
            impact -= 0.1

        # Goal alignment
        for goal in goals:
            if goal and goal in action_text:
                impact += 0.15
                break

        # General geomancer influence
        C = float(event.get("C", 0.0))
        D = float(event.get("D", 0.0))
        impact += (C - D) * 0.03

        # Clamp to lightweight bounded effect
        if impact > 0.4:
            impact = 0.4
        if impact < -0.4:
            impact = -0.4

        return round(impact, 3)

    def _log_faction_event(self, delta: Dict[str, Any]) -> None:
        log = self.world.setdefault("faction_log", [])
        log.append(delta)
        if len(log) > 50:
            self.world["faction_log"] = log[-50:]
