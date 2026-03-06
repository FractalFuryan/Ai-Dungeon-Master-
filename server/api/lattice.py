from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/lattice", tags=["lattice"])


@router.post("/session/start")
async def start_session(
    session_id: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.start_session_with_lattice(session_id)


@router.post("/session/offer")
async def offer_choices(
    motive_nodes: List[Dict[str, Any]],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    offered = world_engine.offer_session_choices(motive_nodes)
    return {"offered": offered, "count": len(offered)}


@router.post("/choice/accept/{node_id}")
async def accept_choice(
    node_id: str,
    player_ids: List[str],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.handle_choice(node_id, True, player_ids)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/choice/decline/{node_id}")
async def decline_choice(
    node_id: str,
    player_ids: List[str],
    world_id: str,
    reason: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.handle_choice(node_id, False, player_ids, reason)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/player/goal")
async def add_player_goal(
    player_id: str,
    goal: str,
    world_id: str,
    wyrd_thread_id: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.add_player_goal(player_id, goal, wyrd_thread_id)


@router.get("/currents")
async def get_open_currents(
    world_id: str,
    include_burst: bool = False,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    currents = []
    for current in world_engine.lattice.open_currents.values():
        if not include_burst and current.burst_at:
            continue
        currents.append(current.to_dict())

    return {
        "currents": currents,
        "total": len(currents),
        "active": len([c for c in world_engine.lattice.open_currents.values() if not c.burst_at]),
    }


@router.get("/currents/session-start")
async def get_currents_for_session(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    currents = world_engine.lattice.get_open_currents_for_session_start()
    return {
        "currents": currents,
        "reading": world_engine.lattice_director.read_open_current_aloud(),
    }


@router.post("/currents/touch/{current_id}")
async def touch_current(
    current_id: str,
    action: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    world_engine.lattice.touch_current(current_id, action)
    return {"touched": current_id, "action": action}


@router.post("/director/faction-response")
async def faction_response(
    faction_id: str,
    event: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.lattice_director.faction_response(faction_id, event)


@router.post("/director/grim-reminder/{current_id}")
async def introduce_grim_reminder(
    current_id: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.lattice_director.introduce_grim_reminder(current_id)


@router.post("/director/close-with-reverence/{current_id}")
async def close_with_reverence(
    current_id: str,
    player_id: str,
    action: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.lattice_director.close_with_reverence(current_id, player_id, action)


@router.post("/ritual/closing")
async def closing_ritual(
    player_answers: List[Dict[str, Any]],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.closing_ritual(player_answers)


@router.get("/wyrd-threads")
async def get_wyrd_threads(
    world_id: str,
    player_id: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    threads = []
    for thread in world_engine.lattice.wyrd_threads.values():
        if player_id and player_id not in thread.player_ids:
            continue
        threads.append(
            {
                "id": thread.id,
                "name": thread.name,
                "description": thread.description,
                "strength": thread.strength,
                "players": thread.player_ids,
                "last_tugged": thread.last_tugged.isoformat() if thread.last_tugged else None,
            }
        )

    return {"threads": threads, "count": len(threads)}


@router.get("/factions/{faction_id}")
async def get_faction_state(
    faction_id: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    rep_data = world_engine.lattice.faction_reputation.get(faction_id, {})
    benefits = world_engine.lattice.get_faction_benefits(faction_id)
    return {
        "faction_id": faction_id,
        "reputation": rep_data.get("reputation", 0),
        "history": rep_data.get("history", [])[-5:],
        "benefits": benefits,
    }


@router.post("/factions/{faction_id}/update")
async def update_faction_reputation(
    faction_id: str,
    event: str,
    players_involved: List[str],
    world_id: str,
    reputation_change: int = 1,
    reason: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    world_engine.lattice.update_faction_reputation(
        faction_id=faction_id,
        event=event,
        players_involved=players_involved,
        context={"reputation_change": reputation_change, "reason": reason or event},
    )

    rep_data = world_engine.lattice.faction_reputation[faction_id]
    return {
        "faction_id": faction_id,
        "new_reputation": rep_data["reputation"],
        "last_event": rep_data["history"][-1] if rep_data.get("history") else None,
    }
