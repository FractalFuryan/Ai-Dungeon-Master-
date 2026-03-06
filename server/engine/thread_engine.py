from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.orm import Session


@dataclass
class NarrativeThreadState:
    id: str
    title: str
    weight: float
    location_id: Optional[str]
    resolved: bool


class ThreadEngine:
    """Manages unresolved narrative threads that ripen over time."""

    def __init__(self, db: Session, world_id: str):
        self.db = db
        self.world_id = world_id
        self.session_threads: List[Dict[str, Any]] = []

    def create_thread(self, title: str, description: str, location_id: Optional[str] = None, weight: float = 0.4) -> str:
        from server.persistence.models import NarrativeThread

        thread = NarrativeThread(
            id=str(uuid.uuid4()),
            world_id=self.world_id,
            title=title,
            description=description,
            location_id=location_id,
            weight=max(0.0, float(weight)),
            resolved=False,
            payload={},
        )
        self.db.add(thread)
        self.db.commit()
        return thread.id

    def ripen(self, delta: float = 0.1, trigger_threshold: float = 1.0) -> Dict[str, Any]:
        from server.persistence.models import NarrativeThread, WorldEvent

        rows = (
            self.db.query(NarrativeThread)
            .filter(NarrativeThread.world_id == self.world_id, NarrativeThread.resolved.is_(False))
            .all()
        )

        triggered: List[Dict[str, Any]] = []
        for row in rows:
            row.weight = float(row.weight) + float(delta)
            if row.weight >= trigger_threshold:
                triggered.append({
                    "thread_id": row.id,
                    "title": row.title,
                    "weight": row.weight,
                    "location_id": row.location_id,
                })
                self.db.add(
                    WorldEvent(
                        world_id=self.world_id,
                        location_id=row.location_id,
                        event_type="thread_trigger",
                        description=f"Narrative thread triggered: {row.title}",
                        payload={"thread_id": row.id, "weight": row.weight},
                    )
                )

        self.db.commit()
        return {
            "updated_count": len(rows),
            "triggered": triggered,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def list_threads(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        from server.persistence.models import NarrativeThread

        query = self.db.query(NarrativeThread).filter(NarrativeThread.world_id == self.world_id)
        if not include_resolved:
            query = query.filter(NarrativeThread.resolved.is_(False))

        out = []
        for row in query.order_by(NarrativeThread.weight.desc()).all():
            out.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "weight": row.weight,
                    "location_id": row.location_id,
                    "resolved": row.resolved,
                }
            )
        return out

    def resolve_thread(self, thread_id: str, resolution: str) -> bool:
        from server.persistence.models import NarrativeThread

        row = self.db.query(NarrativeThread).filter(NarrativeThread.id == thread_id).first()
        if not row:
            return False

        row.resolved = True
        row.resolved_at = datetime.utcnow()
        row.resolution = resolution
        self.db.commit()
        return True

    # Party/session-facing thread tracking methods.
    def record_test(
        self,
        thread_name: str,
        player_id: str,
        note: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
            "thread": thread_name,
            "player_id": player_id,
            "note": note,
            "context": context or {},
            "session_id": session_id,
        }
        self.session_threads.append(record)
        return record

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        session_tests = [t for t in self.session_threads if t.get("session_id") == session_id]
        return {
            "session_id": session_id,
            "threads_tested": len(session_tests),
            "threads": [
                {
                    "thread": t["thread"],
                    "player": t["player_id"],
                    "note": t["note"],
                }
                for t in session_tests
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }
