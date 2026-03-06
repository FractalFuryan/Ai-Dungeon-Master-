from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/largess", tags=["largess"])


@router.post("/shard/close")
async def close_shard(
    shard_name: str,
    final_ritual_words: List[str],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.close_shard(shard_name, final_ritual_words)


@router.post("/shard/dawn")
async def dawn_new_shard(
    shard_name: str,
    transition_type: str,
    source_grave_id: str,
    players: List[Dict[str, Any]],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.dawn_new_shard(shard_name, transition_type, source_grave_id, players)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/graves")
async def get_graves(
    world_id: str,
    include_seeds: bool = False,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    graves = []
    for grave in world_engine.largess_bank.graves.values():
        grave_dict = grave.to_dict()
        if not include_seeds:
            grave_dict.pop("largess_seeds", None)
        graves.append(grave_dict)

    return {"graves": graves, "total": len(graves)}


@router.get("/grave/{grave_id}")
async def get_grave(
    grave_id: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    grave = world_engine.largess_bank.graves.get(grave_id)
    if not grave:
        raise HTTPException(status_code=404, detail="Grave not found")
    return grave.to_dict()


@router.get("/grave/{grave_id}/prompts")
async def get_grave_prompts(
    grave_id: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    prompts = world_engine.largess_bank.get_grave_interview_prompt(grave_id)
    return {"grave_id": grave_id, "prompts": prompts, "count": len(prompts)}


@router.post("/grave/interview")
async def grave_interview(
    player_id: str,
    character_name: str,
    seed_id: str,
    intent: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.grave_interview(player_id, character_name, seed_id, intent)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/seeds")
async def get_seeds(
    world_id: str,
    unclaimed_only: bool = True,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    seeds = []
    for seed in world_engine.largess_bank.seeds.values():
        if unclaimed_only and seed.claimed:
            continue
        seeds.append(seed.to_dict())

    return {
        "seeds": seeds,
        "total": len(seeds),
        "unclaimed": len([s for s in seeds if not s.get("claimed")]),
    }


@router.post("/seeds/{seed_id}/claim")
async def claim_seed(
    seed_id: str,
    character_id: str,
    player_id: str,
    intent: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        seed = world_engine.largess_bank.claim_seed(seed_id, character_id, player_id, intent)
        return seed.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/ritual/closing-arc")
async def closing_arc_rite(
    players: List[Dict[str, Any]],
    open_currents: List[Dict[str, Any]],
    retired_characters: List[Dict[str, Any]],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.reweave_director.closing_arc_rite(players, open_currents, retired_characters)


@router.post("/ritual/closing-largess")
async def closing_largess_ritual(
    players: List[Dict[str, Any]],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.closing_largess_ritual(players)


@router.get("/dawn/current")
async def get_current_dawn(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    director = world_engine.reweave_director
    if not director.current_dawn:
        return {"dawn": None}
    return {"dawn": director.current_dawn.to_dict()}


@router.get("/state")
async def get_largess_state(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.get_largess_state()
