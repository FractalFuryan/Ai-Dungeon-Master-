from datetime import datetime, timedelta
from enum import Enum
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    MUNDANE = "mundane"
    FANTASTICAL = "fantastical"
    RITUAL = "ritual"
    VECTOR = "vector"


class AnchorViolation(Exception):
    """Raised when anchor enforcement fails."""


class EnvironmentMemory:
    def __init__(self):
        self.mundane_details: List[str] = []
        self.last_mundane_time: Optional[datetime] = None

    def add_detail(self, detail: str) -> None:
        self.mundane_details.append(detail)
        self.last_mundane_time = datetime.utcnow()

    def get_recent_context(self, minutes: int = 10) -> str:
        if not self.mundane_details:
            return "The environment feels neutral, waiting to be defined."
        recent = self.mundane_details[-3:]
        return "The environment remembers: " + "; ".join(recent)


class VectorDetectionEngine:
    def __init__(self):
        self.vectors: List[Dict[str, Any]] = []
        self.threshold = 2
        self.last_correction: Optional[datetime] = None

    def report_vector(self, player_id: str, description: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        vector = {
            "player": player_id,
            "description": description,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.vectors.append(vector)
        logger.warning("Vector detected: %s - %s", player_id, description)

        if self.check_vector_threshold():
            return self.apply_correction()
        return None

    def check_vector_threshold(self) -> bool:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent = [v for v in self.vectors if datetime.fromisoformat(v["timestamp"]) > one_hour_ago]
        return len(recent) >= self.threshold

    def apply_correction(self) -> Dict[str, Any]:
        self.last_correction = datetime.utcnow()
        correction = {
            "action": "introduce_mundane_complication",
            "reason": "vector detection triggered",
            "vectors_triggered": len(self.vectors),
            "suggestion": "A mundane detail interrupts: rain starts, a merchant demands payment, or a child asks a direct question.",
            "timestamp": self.last_correction.isoformat(),
        }
        logger.info("Vector correction applied: %s", correction)

        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        self.vectors = [v for v in self.vectors if datetime.fromisoformat(v["timestamp"]) < one_hour_ago]
        return correction

    def reset(self) -> None:
        self.vectors = []
        logger.info("Vector detection reset")


class AnchorEngine:
    """Enforces a 2:1 mundane-to-fantastical pacing rule."""

    def __init__(self, db: Session, world_id: str):
        self.db = db
        self.world_id = world_id
        self.recent_mundane: List[datetime] = []
        self.mundane_events = 0
        self.fantastical_events = 0
        self.ritual_events = 0
        self.environment = EnvironmentMemory()
        self.vector_detection = VectorDetectionEngine()
        self.action_history: List[Dict[str, Any]] = []

    def _prune(self) -> None:
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.recent_mundane = [t for t in self.recent_mundane if t > cutoff]

    def record_action(self, action_type: str, timestamp: Optional[datetime] = None) -> None:
        from server.persistence.models import WorldEvent

        ts = timestamp or datetime.utcnow()
        event = WorldEvent(
            world_id=self.world_id,
            event_type=f"action_{action_type}",
            description=f"Recorded {action_type} action",
            payload={"action_type": action_type, "timestamp": ts.isoformat()},
        )
        self.db.add(event)

        if action_type == "mundane":
            self.recent_mundane.append(ts)
            self._prune()

        self.db.commit()

    def register_action(self, action_type: ActionType, description: str, context: Optional[Dict[str, Any]] = None) -> None:
        event: Dict[str, Any] = {
            "type": action_type.value,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
        }

        self.action_history.append(event)

        if action_type == ActionType.MUNDANE:
            self.mundane_events += 1
            self.environment.add_detail(description)
            self.record_action("mundane")
        elif action_type == ActionType.FANTASTICAL:
            self.fantastical_events += 1
            self.record_action("fantastical")
        elif action_type == ActionType.RITUAL:
            self.ritual_events += 1
            self.record_action("ritual")
        elif action_type == ActionType.VECTOR:
            correction = self.vector_detection.report_vector(
                (context or {}).get("player_id", "unknown"),
                description,
                context,
            )
            if correction:
                event["correction"] = correction

    def enforce_anchor(self, action_is_fantastical: bool, context: Optional[Dict[str, Any]] = None) -> bool:
        if not action_is_fantastical:
            self.register_action(
                ActionType.MUNDANE,
                (context or {}).get("description", "mundane action"),
                context,
            )
            return True

        self._prune()
        mundane_count = len(self.recent_mundane)
        if mundane_count < 2:
            raise AnchorViolation(
                f"Need 2 mundane actions before fantastic. Current mundane count: {mundane_count}\n"
                f"Environment context: {self.environment.get_recent_context()}"
            )

        self.register_action(
            ActionType.FANTASTICAL,
            (context or {}).get("description", "fantastical action"),
            context,
        )
        return True

    def register_ritual(self, description: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.register_action(ActionType.RITUAL, description, context)

    def reset_session(self) -> None:
        self.mundane_events = 0
        self.fantastical_events = 0
        self.ritual_events = 0
        self.action_history = []
        self.vector_detection.reset()
        self.recent_mundane = []
        logger.info("Anchor engine reset for new session")

    def get_anchor_state(self) -> dict:
        self._prune()
        count = len(self.recent_mundane)
        ratio = (self.mundane_events / self.fantastical_events) if self.fantastical_events > 0 else float("inf")
        return {
            "recent_mundane_count": count,
            "needed_for_fantastic": max(0, 2 - count),
            "can_use_fantastic": count >= 2,
            "mundane_count": self.mundane_events,
            "fantastical_count": self.fantastical_events,
            "ritual_count": self.ritual_events,
            "ratio": round(ratio, 2) if ratio != float("inf") else "infinite",
            "environment_context": self.environment.get_recent_context(),
            "vector_state": {
                "recent_vectors": len(self.vector_detection.vectors),
                "threshold": self.vector_detection.threshold,
                "needs_correction": self.vector_detection.check_vector_threshold(),
            },
            "recent_actions": self.action_history[-5:],
        }
