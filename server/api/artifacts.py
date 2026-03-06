from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


@router.get("/")
async def get_artifacts(
    discovered_only: bool = False,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.artifact_engine.get_all_artifacts(discovered_only)


@router.post("/{artifact_key}/discover")
async def discover_artifact(
    artifact_key: str,
    location_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.discover_artifact(artifact_key, location_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{artifact_key}/use")
async def use_artifact(
    artifact_key: str,
    user_id: str,
    context: Dict[str, Any],
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.artifact_engine.use_artifact(artifact_key, user_id, context)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{artifact_key}/transfer")
async def transfer_artifact(
    artifact_key: str,
    new_wielder: str,
    new_location: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.artifact_engine.transfer_artifact(artifact_key, new_wielder, new_location)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
