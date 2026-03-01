from typing import Any, Dict, List


class NPCEngine:
    def __init__(self, world_state: Dict[str, Any]):
        self.world = world_state
        self.npcs = world_state.setdefault("npcs", {})

    def recalculate_loyalties(self) -> Dict[str, Dict[str, float]]:
        """Update NPC trust based on faction attitude + remembered impact."""
        updates: Dict[str, Dict[str, float]] = {}
        factions = self.world.get("factions", {})

        for npc_id, npc in self.npcs.items():
            faction_id = npc.get("faction")
            faction = factions.get(faction_id, {})
            faction_attitude = float(faction.get("attitude", {}).get("players", 0.0))

            memory = npc.get("memory", [])
            if memory:
                memory_impact = sum(float(m.get("impact", 0.0)) for m in memory) / len(memory)
            else:
                memory_impact = 0.0

            trust_players = 0.7 * faction_attitude + 0.3 * memory_impact
            trust_players = max(-1.0, min(1.0, trust_players))

            trust = npc.setdefault("trust", {})
            trust["players"] = trust_players

            updates[npc_id] = {"trust_players": round(trust_players, 3)}

        return updates

    def record_event_memory(self, event: Dict[str, Any]) -> None:
        """NPCs store short memory entries when affected by player actions."""
        action_text = event.get("action_text", "").lower()
        action_type = event.get("action_type", "neutral")

        for npc_id, npc in self.npcs.items():
            relevant = npc_id.lower() in action_text
            npc_faction = str(npc.get("faction", "")).lower()
            if npc_faction and npc_faction in action_text:
                relevant = True

            if not relevant:
                continue

            impact = 0.0
            if action_type == "coop":
                impact = 0.15
            elif action_type == "disrupt":
                impact = -0.2

            entry = {
                "event": event.get("action_text", "")[:120],
                "impact": impact,
                "action_type": action_type,
            }
            memory = npc.setdefault("memory", [])
            memory.append(entry)
            if len(memory) > 12:
                npc["memory"] = memory[-12:]

    def find_active_hooks(self) -> List[Dict[str, str]]:
        """Return deterministic hook triggers from current NPC trust state."""
        active: List[Dict[str, str]] = []

        for npc_id, npc in self.npcs.items():
            trust = float(npc.get("trust", {}).get("players", 0.0))
            hooks = npc.get("hooks", {})

            fear_hook = hooks.get("fear")
            desire_hook = hooks.get("desire")
            debt_hook = hooks.get("debt")

            if trust < -0.5 and fear_hook:
                active.append(
                    {
                        "npc": npc_id,
                        "type": "fear",
                        "description": f"{npc_id} is afraid of the players and {fear_hook}",
                    }
                )

            if trust > 0.7 and desire_hook:
                active.append(
                    {
                        "npc": npc_id,
                        "type": "desire",
                        "description": f"{npc_id} trusts the players and wants {desire_hook}",
                    }
                )

            if trust > 0.5 and debt_hook:
                active.append(
                    {
                        "npc": npc_id,
                        "type": "debt",
                        "description": f"{npc_id} remembers owing the players and {debt_hook}",
                    }
                )

        return active
