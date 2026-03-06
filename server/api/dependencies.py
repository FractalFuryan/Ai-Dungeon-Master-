from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from server.engine.world_engine import WorldEngine
from server.persistence.database import get_db
from server.persistence.models import World


async def get_world_engine(request: Request, db: Session = Depends(get_db)) -> WorldEngine:
    world_id = request.path_params.get("world_id")
    party_id = request.path_params.get("party_id")

    if not world_id:
        world_id = request.query_params.get("world_id")
    if not party_id:
        party_id = request.query_params.get("party_id")

    if not world_id and request.method in {"POST", "PUT", "PATCH"}:
        try:
            body = await request.json()
            world_id = body.get("world_id") if isinstance(body, dict) else None
            if isinstance(body, dict):
                party_id = party_id or body.get("party_id")
        except Exception:
            world_id = None

    if not world_id:
        raise HTTPException(status_code=400, detail="world_id required")

    return WorldEngine(db, world_id, party_id=party_id)


def get_current_world(world_id: str, db: Session = Depends(get_db)) -> World:
    world = db.query(World).filter(World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    return world
