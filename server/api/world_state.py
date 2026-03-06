from fastapi import APIRouter, Depends

from server.api.dependencies import get_world_engine
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/world", tags=["world-state"])


@router.get("/state")
async def get_world_state(world_engine: WorldEngine = Depends(get_world_engine)):
    return world_engine.get_world_state_snapshot()
