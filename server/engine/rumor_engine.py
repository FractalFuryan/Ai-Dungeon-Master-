from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session


class RumorEngine:
    """Minimal rumor progression engine for world ticks and success outcomes."""

    def __init__(self, db: Session, world_id: str):
        self.db = db
        self.world_id = world_id

    def ripen_rumors(self, delta: float = 0.2) -> Dict[str, object]:
        from server.persistence.models import WorldEvent

        event = WorldEvent(
            world_id=self.world_id,
            event_type="rumor_ripen",
            description=f"Rumors ripened by {delta}",
            payload={"delta": delta, "timestamp": datetime.utcnow().isoformat()},
        )
        self.db.add(event)
        self.db.commit()
        return {"delta": delta, "recorded": True}
