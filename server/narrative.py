import random
from enum import Enum
from typing import Dict, List, Optional


class NarrativeFrame(Enum):
    STRAIGHTFORWARD = "straightforward"
    UNEXPECTED_ALLY = "unexpected_ally"
    HIDDEN_COST = "hidden_cost"
    MORAL_INVERSION = "moral_inversion"
    FORESHADOWING = "foreshadowing"
    LAYERED_CONSEQUENCES = "layered_consequences"


class NarrativeEngine:
    def __init__(self):
        self.frames = list(NarrativeFrame)

    def select_frame(
        self,
        player_creativity: float = 0.5,
        world_entropy: float = 0.0,
        recent_frames: Optional[List[str]] = None,
    ) -> NarrativeFrame:
        recent_frames = recent_frames or []

        if player_creativity < 0.3 and world_entropy < 0.3:
            return NarrativeFrame.STRAIGHTFORWARD
        if player_creativity > 0.7:
            return random.choice([NarrativeFrame.FORESHADOWING, NarrativeFrame.LAYERED_CONSEQUENCES])
        if world_entropy > 0.6:
            return random.choice([NarrativeFrame.HIDDEN_COST, NarrativeFrame.MORAL_INVERSION])

        available = [f for f in self.frames if f.value not in recent_frames[-3:]]
        return random.choice(available) if available else random.choice(self.frames)

    async def process_rumor(self, description: str, intensity: float) -> Dict:
        branches = []
        if intensity > 0.7:
            branches = [
                {"variant": "true", "weight": 0.3},
                {"variant": "exaggerated", "weight": 0.5},
                {"variant": "corrupted", "weight": 0.2},
            ]
        elif intensity > 0.4:
            branches = [
                {"variant": "true", "weight": 0.4},
                {"variant": "exaggerated", "weight": 0.6},
            ]
        else:
            branches = [{"variant": "true", "weight": 1.0}]

        return {
            "original": description,
            "intensity": intensity,
            "branches": branches,
            "spread_chance": intensity * 0.3,
        }

    def check_world_stability(self, entropy: float, reverence: float) -> Dict:
        if entropy > reverence + 1.0:
            return {
                "stable": False,
                "event": "INSTABILITY_EVENT",
                "severity": "high",
                "description": "The world teeters on the brink of chaos...",
            }
        if entropy > reverence:
            return {
                "stable": False,
                "event": "INSTABILITY_WARNING",
                "severity": "medium",
                "description": "Dark omens gather on the horizon...",
            }
        if reverence > entropy + 2.0:
            return {
                "stable": True,
                "event": "HOPE_PERSISTS",
                "severity": "low",
                "description": "Stories of heroism spread like wildfire...",
            }
        return {
            "stable": True,
            "event": None,
            "severity": "none",
            "description": "The world holds its breath...",
        }


class LegacyLedger:
    def __init__(self):
        self.entries = []

    async def add_entry(
        self,
        world_id: str,
        entry_type: str,
        description: str,
        mechanical_effect: Optional[str] = None,
    ) -> Dict:
        entry = {
            "id": None,
            "world_id": world_id,
            "entry_type": entry_type,
            "description": description,
            "mechanical_effect": mechanical_effect,
            "created_at": None,
        }
        self.entries.append(entry)
        return entry

    def get_legacy_features(self, world_id: str) -> List[Dict]:
        return [entry for entry in self.entries if entry["world_id"] == world_id]
