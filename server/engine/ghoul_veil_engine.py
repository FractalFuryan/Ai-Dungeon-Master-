from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import random
from typing import Any, Dict, List, Optional, Tuple
import uuid

logger = logging.getLogger(__name__)


class GhoulAspect(Enum):
    """Aspects of ghouls that players can complete."""

    FACE = "face"
    SOUND = "sound"
    SMELL = "smell"
    MOVEMENT = "movement"
    HUNGER = "hunger"
    TASTE = "taste"
    FEAR = "fear"
    ORIGIN = "origin"


class VeilNodeState(Enum):
    """State of a ghoul veil node."""

    DORMANT = "dormant"
    WHISPERING = "whispering"
    STALKING = "stalking"
    HUNGRY = "hungry"
    BURST = "burst"


@dataclass
class PlayerVision:
    """A player-provided completion for a ghoul blank."""

    player_id: str
    character_name: str
    aspect: GhoulAspect
    description: str
    seen_at: datetime
    session_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player": self.player_id,
            "character": self.character_name,
            "aspect": self.aspect.value,
            "description": self.description,
            "seen_at": self.seen_at.isoformat(),
        }


@dataclass
class GhoulVeilNode:
    """A location where the ghoul veil is thin."""

    id: str
    location_name: str
    location_desc: str
    map_coordinates: Tuple[float, float]
    inked_by: str
    inked_at: datetime
    state: VeilNodeState
    silence_started: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    personal_trigger: str = ""
    player_visions: List[PlayerVision] = field(default_factory=list)
    ripeness: float = 0.0
    grim_reminder: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "location": self.location_name,
            "state": self.state.value,
            "inked_by": self.inked_by,
            "ripeness": self.ripeness,
            "silence_started": self.silence_started.isoformat() if self.silence_started else None,
            "grim_reminder": self.grim_reminder,
            "visions": [v.to_dict() for v in self.player_visions[-3:]],
        }


@dataclass
class GhoulEncounter:
    """A ghoul encounter triggered by a veil burst."""

    id: str
    node_id: str
    triggered_at: datetime
    players_involved: List[str]
    player_visions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_type: Optional[str] = None
    reverence_paid: int = 0
    blood_paid: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "triggered_at": self.triggered_at.isoformat(),
            "players": self.players_involved,
            "resolved": self.resolved,
            "reverence_paid": self.reverence_paid,
            "blood_paid": self.blood_paid,
        }


class GhoulVeilEngine:
    """Ghoul Hunger Veil where players complete the horror details."""

    def __init__(self, world_id: str, anchor_map_id: str):
        self.world_id = world_id
        self.anchor_map_id = anchor_map_id
        self.nodes: Dict[str, GhoulVeilNode] = {}
        self.encounters: Dict[str, GhoulEncounter] = {}
        self.sketch = {
            "name": "Ghoul Hunger Veil",
            "description": (
                "A rough, unfinished pencil-and-charcoal sketch. "
                "A hooded silhouette with too-wide eyes and too-long fingers. "
                "A second ghoul crawling from the undergrowth. "
                "A fallen armored corpse with sword still sheathed and shield askew."
            ),
            "placed_at": datetime.utcnow().isoformat(),
            "blanks": ["face", "fingers", "sound", "smell", "hunger"],
        }
        self.session_visions: List[PlayerVision] = []
        logger.info("GhoulVeilEngine initialized for world %s", world_id)

    def coast_ink_ritual(
        self,
        player_id: str,
        character_name: str,
        location_name: str,
        description: str,
        coordinates: Tuple[float, float],
    ) -> GhoulVeilNode:
        node = GhoulVeilNode(
            id=str(uuid.uuid4()),
            location_name=location_name,
            location_desc=description,
            map_coordinates=coordinates,
            inked_by=player_id,
            inked_at=datetime.utcnow(),
            state=VeilNodeState.DORMANT,
            personal_trigger=description,
        )
        self.nodes[node.id] = node

        vision = PlayerVision(
            player_id=player_id,
            character_name=character_name,
            aspect=GhoulAspect.ORIGIN,
            description=f"Inked at {location_name}: {description}",
            seen_at=datetime.utcnow(),
        )
        node.player_visions.append(vision)
        self.session_visions.append(vision)

        logger.info("Coast ink ritual: %s at %s", character_name, location_name)
        return node

    def rumor_fulcrum_opening(self, days_silent: int = 3) -> Dict[str, Any]:
        updates: List[Dict[str, Any]] = []
        now = datetime.utcnow()

        for node_id, node in self.nodes.items():
            if node.state == VeilNodeState.BURST:
                continue

            days_old = (now - node.inked_at).days
            if days_old >= days_silent and node.state == VeilNodeState.DORMANT:
                node.state = VeilNodeState.WHISPERING
                node.silence_started = now
                updates.append(
                    {
                        "node_id": node_id,
                        "location": node.location_name,
                        "new_state": VeilNodeState.WHISPERING.value,
                        "message": f"The wildlife near {node.location_name} has gone silent.",
                    }
                )
            elif days_old >= days_silent * 2 and node.state == VeilNodeState.WHISPERING:
                node.state = VeilNodeState.STALKING
                updates.append(
                    {
                        "node_id": node_id,
                        "location": node.location_name,
                        "new_state": VeilNodeState.STALKING.value,
                        "message": f"Something is watching from {node.location_name}.",
                    }
                )
            elif days_old >= days_silent * 3 and node.state == VeilNodeState.STALKING:
                node.state = VeilNodeState.HUNGRY
                updates.append(
                    {
                        "node_id": node_id,
                        "location": node.location_name,
                        "new_state": VeilNodeState.HUNGRY.value,
                        "message": f"The ghouls near {node.location_name} are hungry.",
                    }
                )

        question = {
            "prompt": (
                "For the last three nights, the shepherds say the goats refuse to graze after dusk. "
                "The wildlife has gone silent. The sketch lies on the table."
            ),
            "question": "How has your character been sleeping?",
            "affected_areas": [u["location"] for u in updates],
        }

        return {"updates": updates, "question": question}

    def anchor_enforcement(self, player_id: str, mundane_anchors: List[str]) -> bool:
        # The provided anchors represent the player's narrated mundane crossings.
        if len(mundane_anchors) < 2:
            return False

        player_nodes = [n for n in self.nodes.values() if n.inked_by == player_id and n.state != VeilNodeState.BURST]
        if len(player_nodes) < 2:
            return False

        recent_visits = [
            n for n in player_nodes if n.last_activity and (datetime.utcnow() - n.last_activity).days < 7
        ]
        return len(recent_visits) >= 2

    def imagination_completion(
        self,
        player_id: str,
        character_name: str,
        aspect: GhoulAspect,
        description: str,
        node_id: Optional[str] = None,
    ) -> PlayerVision:
        vision = PlayerVision(
            player_id=player_id,
            character_name=character_name,
            aspect=aspect,
            description=description,
            seen_at=datetime.utcnow(),
            session_only=True,
        )
        self.session_visions.append(vision)

        if node_id and node_id in self.nodes:
            self.nodes[node_id].player_visions.append(vision)
            self.nodes[node_id].last_activity = datetime.utcnow()

        return vision

    def trigger_encounter(self, node_id: str, players: List[str]) -> GhoulEncounter:
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        node = self.nodes[node_id]
        node.state = VeilNodeState.BURST
        node.last_activity = datetime.utcnow()

        encounter = GhoulEncounter(
            id=str(uuid.uuid4()),
            node_id=node_id,
            triggered_at=datetime.utcnow(),
            players_involved=players,
        )
        self.encounters[encounter.id] = encounter

        logger.info("Ghoul encounter triggered at %s", node.location_name)
        return encounter

    def daylight_burn(
        self,
        encounter_id: str,
        player_id: str,
        vulnerability: str,
        pay_with_reverence: bool = True,
    ) -> Dict[str, Any]:
        if encounter_id not in self.encounters:
            raise ValueError(f"Encounter {encounter_id} not found")

        encounter = self.encounters[encounter_id]

        vision = self.imagination_completion(
            player_id=player_id,
            character_name="Unknown",
            aspect=GhoulAspect.TASTE,
            description=f"The ghoul tasted my {vulnerability}",
        )
        encounter.player_visions[player_id] = {
            "vulnerability": vulnerability,
            "vision": vision.to_dict(),
        }

        if pay_with_reverence:
            encounter.reverence_paid += 1
            cost_type = "reverence"
        else:
            encounter.blood_paid = True
            cost_type = "blood"

        encounter.resolved = True
        encounter.resolved_at = datetime.utcnow()
        encounter.resolution_type = "daylight_burn"

        return {
            "encounter_id": encounter_id,
            "resolved": True,
            "cost_type": cost_type,
            "vulnerability": vulnerability,
            "message": f"The ghouls retreat from daylight, but they remember your {vulnerability}.",
        }

    def unanswered_ripening(self) -> List[Dict[str, Any]]:
        grim_reminders: List[Dict[str, Any]] = []
        now = datetime.utcnow()

        for node_id, node in self.nodes.items():
            if node.state == VeilNodeState.BURST:
                continue

            days_idle = (now - (node.last_activity or node.inked_at)).days
            if node.state == VeilNodeState.HUNGRY and days_idle > 2:
                node.ripeness = min(1.0, node.ripeness + 0.2)
                if node.ripeness >= 0.8 and not node.grim_reminder:
                    reminder = self._generate_grim_reminder(node)
                    node.grim_reminder = reminder
                    grim_reminders.append(
                        {
                            "node_id": node_id,
                            "location": node.location_name,
                            "reminder": reminder,
                        }
                    )
                    node.player_visions.append(
                        PlayerVision(
                            player_id="system",
                            character_name="System",
                            aspect=GhoulAspect.FEAR,
                            description=reminder,
                            seen_at=now,
                        )
                    )

        return grim_reminders

    def _generate_grim_reminder(self, node: GhoulVeilNode) -> str:
        templates = [
            f"Livestock near {node.location_name} were found with their faces missing. Just gone.",
            f"A hermit's hut near {node.location_name} stands empty. Scratch marks on the door.",
            f"The {node.location_name} road is empty. Travelers hear their own footsteps echo back wrong.",
            f"Wheel Warden patrol found a campsite near {node.location_name}. Occupants vanished.",
            f"The wildlife has not just gone silent near {node.location_name}. It is gone entirely.",
        ]
        return random.choice(templates)

    def hands_of_horne_response(self, node_id: str, arrive_in_time: bool = True) -> Dict[str, Any]:
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        node = self.nodes[node_id]
        if arrive_in_time:
            result = {
                "action": "arrived_in_time",
                "message": (
                    f"The Hands of Horne reach {node.location_name} just as the ghouls close in. "
                    "They save the village, but they are watching to see who led them here."
                ),
                "reputation_change": 1,
            }
        else:
            result = {
                "action": "arrived_too_late",
                "message": (
                    f"The Hands of Horne reach {node.location_name} to find only scratch marks and silence. "
                    "They remember who ignored this place."
                ),
                "reputation_change": -1,
            }

        node.last_activity = datetime.utcnow()
        return result

    def closing_ritual(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        answers: List[Dict[str, Any]] = []

        for player in players:
            player_id = player["id"]
            character_name = player.get("character_name", "Unknown")
            player_visions = [v for v in self.session_visions if v.player_id == player_id]

            if player_visions:
                latest = player_visions[-1]
                answer = {
                    "player_id": player_id,
                    "character": character_name,
                    "question": "What did I see in the ghoul's face that no one else did?",
                    "answer": latest.description,
                    "aspect": latest.aspect.value,
                }
            else:
                player_nodes = [n for n in self.nodes.values() if n.inked_by == player_id]
                if player_nodes:
                    node = random.choice(player_nodes)
                    answer = {
                        "player_id": player_id,
                        "character": character_name,
                        "question": "Where will I ink the next silence?",
                        "answer": f"Near {node.location_name}, where {node.personal_trigger}",
                        "location": node.location_name,
                    }
                else:
                    answer = {
                        "player_id": player_id,
                        "character": character_name,
                        "question": "What did the blanks show me?",
                        "answer": "Nothing yet. The veil is still thin, but I am watching.",
                    }

            answers.append(answer)

        logger.info("Ghoul closing ritual completed with %s answers", len(answers))
        return answers

    def get_veil_state(self) -> Dict[str, Any]:
        return {
            "sketch": self.sketch,
            "nodes": {
                "total": len(self.nodes),
                "by_state": {
                    state.value: len([n for n in self.nodes.values() if n.state == state])
                    for state in VeilNodeState
                },
                "active": [n.to_dict() for n in self.nodes.values() if n.state != VeilNodeState.BURST][-10:],
            },
            "encounters": {
                "total": len(self.encounters),
                "recent": [e.to_dict() for e in self.encounters.values()][-5:],
            },
            "session_visions": [v.to_dict() for v in self.session_visions[-10:]],
        }
