import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from server.api.dependencies import get_world_engine
from server.engine.world_engine import WorldEngine
from server.persistence.database import get_db

router = APIRouter(prefix="/api/resolve", tags=["resolution"])
logger = logging.getLogger(__name__)


@router.post("/action")
async def resolve_action(action_data: Dict[str, Any], world_engine: WorldEngine = Depends(get_world_engine)):
    try:
        return world_engine.resolve_action(action_data)
    except Exception as exc:
        logger.error("Action resolution failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/world/{world_id}/tick")
async def trigger_world_tick(world_id: str, db: Session = Depends(get_db)):
    engine = WorldEngine(db, world_id)
    updates = engine.world_tick()
    return {"success": True, "updates": updates}


@router.websocket("/ws/{world_id}")
async def websocket_endpoint(websocket: WebSocket, world_id: str):
    await websocket.accept()

    # Use generator directly in websocket context.
    db_gen = get_db()
    db = next(db_gen)
    engine = WorldEngine(db, world_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "action":
                result = engine.resolve_action(message.get("data", {}))
                await websocket.send_json({"type": "resolution", "data": result})
            elif message.get("type") == "world_tick":
                updates = engine.world_tick()
                await websocket.send_json({"type": "world_update", "data": updates})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for world %s", world_id)
    finally:
        db.close()
