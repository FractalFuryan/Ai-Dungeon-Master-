from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.api.dependencies import get_world_engine
from server.engine.legacy_ledger_engine import LegacyFeatureType
from server.engine.world_engine import WorldEngine
from server.models import Character
from server.persistence.database import get_db

router = APIRouter(prefix="/api/legacy", tags=["legacy"])


@router.post("/retire")
async def retire_character(
    world_id: str,
    character_id: str,
    player_id: str,
    final_act: str,
    feature_type: Optional[str] = None,
    chosen_location: Optional[str] = None,
    db: Session = Depends(get_db),
    world_engine: WorldEngine = Depends(get_world_engine),
):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if feature_type:
        try:
            LegacyFeatureType(feature_type)
        except ValueError as exc:
            valid = ", ".join([ft.value for ft in LegacyFeatureType])
            raise HTTPException(status_code=400, detail=f"Invalid feature_type: {feature_type}. Valid values: {valid}") from exc

    try:
        return world_engine.perform_retirement(
            character=character,
            player_id=player_id,
            final_act=final_act,
            feature_type=feature_type,
            chosen_location=chosen_location,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/retire/preview")
async def preview_retirement(
    world_id: str,
    character_id: str,
    db: Session = Depends(get_db),
    world_engine: WorldEngine = Depends(get_world_engine),
):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return world_engine.retirement.preview_retirement(character)


@router.get("/audit")
async def get_ledger_audit(world_engine: WorldEngine = Depends(get_world_engine)):
    return {
        "audit": world_engine.audit_ledger(),
        "audit_state": world_engine.ledger_audit.get_audit_state(),
    }


@router.get("/state")
async def get_legacy_state(world_engine: WorldEngine = Depends(get_world_engine)):
    return world_engine.get_legacy_state()


@router.post("/vector/report")
async def report_vector(
    world_id: str,
    player_id: str,
    description: str,
    context: Optional[Dict[str, Any]] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    correction = world_engine.report_vector(player_id=player_id, description=description, context=context)
    return {
        "reported": True,
        "correction": correction,
        "anchor_state": world_engine.anchor.get_anchor_state(),
    }


@router.post("/anchor/reset")
async def reset_anchor(world_engine: WorldEngine = Depends(get_world_engine)):
    world_engine.anchor.reset_session()
    return {"reset": True, "anchor_state": world_engine.anchor.get_anchor_state()}
