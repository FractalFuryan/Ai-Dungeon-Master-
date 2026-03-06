from datetime import datetime
import logging
import random
from typing import Any, Dict, List, Optional
import uuid

from server.engine.lattice_engine import (
    CurrentType,
    LatticeMarker,
    MotiveNode,
    OpenCurrent,
    RipenessLevel,
    WyrdThread,
)

logger = logging.getLogger(__name__)


class PeripheralLatticeEngine:
    """Open-current lattice that evolves from ignored choices and peripheral pressure."""

    def __init__(self, world_id: str, legacy_ledger: Any):
        self.world_id = world_id
        self.legacy = legacy_ledger

        self.open_currents: Dict[str, OpenCurrent] = {}
        self.motive_nodes: Dict[str, MotiveNode] = {}
        self.wyrd_threads: Dict[str, WyrdThread] = {}
        self.faction_reputation: Dict[str, Dict[str, Any]] = {}

        self.current_session_id: Optional[str] = None
        self.session_offerings: List[str] = []

        logger.info("PeripheralLatticeEngine initialized for world %s", world_id)

    def start_session(self, session_id: str) -> None:
        self.current_session_id = session_id
        self.session_offerings = []
        logger.info("Session %s started in lattice engine", session_id)

    def offer_choices(self, motive_nodes: List[Dict[str, Any]]) -> List[MotiveNode]:
        offered: List[MotiveNode] = []
        for node_data in motive_nodes:
            anchors = list(node_data.get("mundane_anchors", []))
            if len(anchors) < 2:
                logger.warning("Motive node %s had insufficient anchors", node_data.get("name", "unnamed"))
                anchors = ["Observe the environment", "Talk to a local"]

            node = MotiveNode(
                id=str(uuid.uuid4()),
                name=str(node_data["name"]),
                description=str(node_data["description"]),
                pressure_type=str(node_data.get("pressure_type", "time")),
                pressure_description=str(node_data.get("pressure", "Time is running out")),
                mundane_anchors=anchors,
                offered_at=datetime.utcnow(),
                open_current_id=node_data.get("open_current_id"),
            )
            self.motive_nodes[node.id] = node
            self.session_offerings.append(node.id)
            offered.append(node)
            logger.info("Offered choice %s (%s)", node.name, node.pressure_type)

        return offered

    def accept_choice(self, node_id: str, player_ids: List[str]) -> Dict[str, Any]:
        if node_id not in self.motive_nodes:
            raise ValueError(f"Motive node {node_id} not found")

        node = self.motive_nodes[node_id]
        node.accepted = True
        node.accepted_at = datetime.utcnow()

        if node.open_current_id:
            self.touch_current(node.open_current_id, "accepted")

        thread = WyrdThread(
            id=str(uuid.uuid4()),
            name=f"Thread: {node.name}",
            description=f"Accepted quest: {node.description}",
            player_ids=player_ids,
            npc_ids=[],
            strength=1.0,
        )
        self.wyrd_threads[thread.id] = thread
        return {
            "node": node.to_dict(),
            "thread": {"id": thread.id, "name": thread.name, "strength": thread.strength},
        }

    def decline_choice(self, node_id: str, reason: Optional[str] = None) -> OpenCurrent:
        if node_id not in self.motive_nodes:
            raise ValueError(f"Motive node {node_id} not found")

        node = self.motive_nodes[node_id]
        node.declined = True
        node.declined_at = datetime.utcnow()

        current = OpenCurrent(
            id=str(uuid.uuid4()),
            current_type=CurrentType.DECLINED_PRESSURE,
            description=f"Declined: {node.name} - {node.description}",
            created_at=datetime.utcnow(),
            last_touched=None,
            ripeness=RipenessLevel.FRESH,
            markers=[LatticeMarker.RUMOR],
            location_id=None,
            faction_ids=[],
            npc_ids=[],
            wyrd_thread_ids=[],
            evolution_stage=0,
        )

        if node.open_current_id and node.open_current_id in self.open_currents:
            old_current = self.open_currents[node.open_current_id]
            current.evolution_stage = old_current.evolution_stage + 1
            current.evolution_history = old_current.evolution_history.copy()
            current.faction_ids = old_current.faction_ids.copy()
            current.npc_ids = old_current.npc_ids.copy()
            current.evolution_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "evolved_from_declined",
                    "previous_id": node.open_current_id,
                    "reason": reason or "choice declined",
                }
            )

        self.open_currents[current.id] = current
        logger.info("Choice declined %s -> current %s", node.name, current.id)
        return current

    def touch_current(self, current_id: str, action: str) -> None:
        current = self.open_currents.get(current_id)
        if not current:
            return

        current.last_touched = datetime.utcnow()
        current.ripeness = RipenessLevel.FRESH
        current.evolution_history.append(
            {
                "timestamp": current.last_touched.isoformat(),
                "event": "touched",
                "action": action,
            }
        )

    def add_player_nominated_goal(
        self,
        player_id: str,
        goal_description: str,
        wyrd_thread_id: Optional[str] = None,
    ) -> MotiveNode:
        linked_current: Optional[OpenCurrent] = None

        if wyrd_thread_id and wyrd_thread_id in self.wyrd_threads:
            for current in self.open_currents.values():
                if wyrd_thread_id in current.wyrd_thread_ids:
                    linked_current = current
                    break
        else:
            for current in self.open_currents.values():
                if current.ripeness in {RipenessLevel.RIPENING, RipenessLevel.FERMENTED} and not current.burst_at:
                    linked_current = current
                    break

        node = MotiveNode(
            id=str(uuid.uuid4()),
            name=f"Player Goal: {goal_description[:30]}...",
            description=goal_description,
            pressure_type="player_nominated",
            pressure_description="Self-appointed quest",
            mundane_anchors=["Observe", "Prepare"],
            offered_at=datetime.utcnow(),
            open_current_id=linked_current.id if linked_current else None,
        )

        if linked_current:
            node.description += f" (Tied to open current: {linked_current.description[:50]}...)"

        self.motive_nodes[node.id] = node
        logger.info("Player %s nominated goal %s", player_id, goal_description[:60])
        return node

    def tick(self) -> List[Dict[str, Any]]:
        changed: List[Dict[str, Any]] = []
        for current_id, current in self.open_currents.items():
            if current.burst_at:
                continue

            old_ripeness = current.ripeness
            if current.ripen():
                changed.append(
                    {
                        "current_id": current_id,
                        "old_ripeness": old_ripeness.value,
                        "new_ripeness": current.ripeness.value,
                        "description": current.description,
                    }
                )
                if current.ripeness == RipenessLevel.RIPENING:
                    current.add_marker(LatticeMarker.RUMOR, "ripening started")
                elif current.ripeness == RipenessLevel.FERMENTED:
                    current.add_marker(LatticeMarker.FUTURE_SEED, "fully fermented")
                elif current.ripeness == RipenessLevel.BURST:
                    self._burst_current(current_id)

        logger.info("Lattice tick changed %s currents", len(changed))
        return changed

    def _burst_current(self, current_id: str) -> None:
        current = self.open_currents[current_id]
        current.burst_at = datetime.utcnow()

        if LatticeMarker.GRIM_REMINDER in current.markers:
            current.burst_description = self._generate_grim_reminder(current)
            current.environmental_modifier = {"type": "penalty", "value": -1}
            burst_type = "grim_reminder"
        elif LatticeMarker.FUTURE_SEED in current.markers:
            current.burst_description = self._generate_future_seed(current)
            burst_type = "future_seed"
        else:
            current.burst_description = self._generate_rumor(current)
            burst_type = "rumor"

        current.evolution_history.append(
            {
                "timestamp": current.burst_at.isoformat(),
                "event": "burst",
                "burst_type": burst_type,
                "description": current.burst_description,
            }
        )

    def _generate_rumor(self, current: OpenCurrent) -> str:
        templates = [
            f"Whispers spread about {current.description[:50]}...",
            f"Travellers speak of {current.description[:50]}... in hushed tones.",
            f"A bard sings of {current.description[:50]}... though the details are wrong.",
        ]
        return random.choice(templates)

    def _generate_future_seed(self, current: OpenCurrent) -> str:
        templates = [
            f"What was ignored now grows. {current.description[:100]} will return as a greater threat.",
            f"The seeds of {current.description[:50]} have taken root. A new quest will emerge.",
            f"Something stirs where {current.description[:50]}. It remembers being ignored.",
        ]
        return random.choice(templates)

    def _generate_grim_reminder(self, current: OpenCurrent) -> str:
        templates = [
            f"The {current.description[:50]} now haunts this area.",
            f"A permanent shadow lies where {current.description[:50]}. -1 to all rolls here.",
            f"The ignored {current.description[:30]} has become a place of ill omen.",
        ]
        return random.choice(templates)

    def update_faction_reputation(
        self,
        faction_id: str,
        event: str,
        players_involved: List[str],
        context: Dict[str, Any],
    ) -> None:
        if faction_id not in self.faction_reputation:
            self.faction_reputation[faction_id] = {
                "reputation": 0,
                "history": [],
                "wyrd_threads": [],
            }

        rep_data = self.faction_reputation[faction_id]
        change = int(context.get("reputation_change", 1))
        reason = str(context.get("reason", event))

        rep_data["reputation"] += change
        rep_data["history"].append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": event,
                "change": change,
                "reason": reason,
                "players": players_involved,
            }
        )

        if abs(change) >= 2:
            thread = WyrdThread(
                id=str(uuid.uuid4()),
                name=f"Faction: {faction_id}",
                description=f"Reputation changed by {change} due to {reason}",
                player_ids=players_involved,
                npc_ids=[],
                strength=abs(change) * 0.5,
            )
            self.wyrd_threads[thread.id] = thread
            rep_data["wyrd_threads"].append(thread.id)

    def get_faction_benefits(self, faction_id: str) -> Dict[str, Any]:
        rep = int(self.faction_reputation.get(faction_id, {}).get("reputation", 0))
        if rep >= 5:
            return {"social_bonus": 2, "quests_available": True, "special_favor": True}
        if rep >= 3:
            return {"social_bonus": 1, "quests_available": True}
        if rep >= 1:
            return {"social_bonus": 1}
        return {}

    def get_open_currents_for_session_start(self) -> List[Dict[str, Any]]:
        significant: List[Dict[str, Any]] = []
        for current in self.open_currents.values():
            if current.burst_at:
                continue
            if current.ripeness in {RipenessLevel.FERMENTED, RipenessLevel.RIPENING}:
                significant.append(
                    {
                        "description": current.description,
                        "ripeness": current.ripeness.value,
                        "markers": [m.value for m in current.markers],
                        "id": current.id,
                    }
                )
        return significant[:3]

    def get_lattice_state(self) -> Dict[str, Any]:
        return {
            "open_currents": {
                "total": len(self.open_currents),
                "by_ripeness": {
                    level.value: len(
                        [
                            c
                            for c in self.open_currents.values()
                            if c.ripeness == level and not c.burst_at
                        ]
                    )
                    for level in RipenessLevel
                },
                "burst": len([c for c in self.open_currents.values() if c.burst_at]),
                "currents": [c.to_dict() for c in self.open_currents.values() if not c.burst_at][-10:],
            },
            "wyrd_threads": {
                "total": len(self.wyrd_threads),
                "threads": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "strength": t.strength,
                        "players": t.player_ids,
                    }
                    for t in self.wyrd_threads.values()
                ][-10:],
            },
            "faction_reputation": self.faction_reputation,
        }
