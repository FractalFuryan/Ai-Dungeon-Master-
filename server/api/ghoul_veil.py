from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/ghoul-veil", tags=["ghoul"])


@router.get("/sketch")
async def get_sketch(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    return world_engine.ghoul_veil.sketch


@router.post("/ink-ritual")
async def coast_ink_ritual(
    world_id: str,
    player_id: str,
    character_name: str,
    location_name: str,
    description: str,
    x: float,
    y: float,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    return world_engine.coast_ink_ritual(
        player_id=player_id,
        character_name=character_name,
        location_name=location_name,
        description=description,
        x=x,
        y=y,
    )


@router.get("/nodes")
async def get_veil_nodes(
    world_id: str,
    include_burst: bool = False,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    veil = world_engine.ghoul_veil
    nodes = []

    for node in veil.nodes.values():
        if not include_burst and node.state.value == "burst":
            continue
        nodes.append(node.to_dict())

    return {
        "nodes": nodes,
        "total": len(nodes),
        "active": len([n for n in veil.nodes.values() if n.state.value != "burst"]),
    }


@router.get("/nodes/{node_id}")
async def get_veil_node(
    node_id: str,
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    node = world_engine.ghoul_veil.nodes.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node.to_dict()


@router.post("/rumor-fulcrum")
async def rumor_fulcrum(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    return world_engine.rumor_fulcrum()


@router.post("/imagine")
async def imagine_ghoul(
    world_id: str,
    player_id: str,
    character_name: str,
    aspect: str,
    description: str,
    node_id: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    try:
        return world_engine.imagine_ghoul(
            player_id=player_id,
            character_name=character_name,
            aspect=aspect,
            description=description,
            node_id=node_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/encounter/trigger/{node_id}")
async def trigger_encounter(
    node_id: str,
    players: List[str],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    try:
        return world_engine.trigger_ghoul_encounter(node_id, players)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/encounter/resolve/{encounter_id}")
async def resolve_encounter(
    encounter_id: str,
    world_id: str,
    player_id: str,
    vulnerability: str,
    pay_with_reverence: bool = True,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    try:
        return world_engine.daylight_burn(
            encounter_id=encounter_id,
            player_id=player_id,
            vulnerability=vulnerability,
            pay_with_reverence=pay_with_reverence,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/hands-response/{node_id}")
async def hands_of_horne(
    node_id: str,
    world_id: str,
    arrive_in_time: bool = True,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    try:
        return world_engine.ghoul_veil.hands_of_horne_response(node_id, arrive_in_time)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/ritual/closing")
async def closing_ritual(
    players: List[Dict[str, Any]],
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    return world_engine.ghoul_closing_ritual(players)


@router.get("/grim-reminders")
async def get_grim_reminders(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    veil = world_engine.ghoul_veil
    reminders = []

    for node_id, node in veil.nodes.items():
        if node.grim_reminder:
            reminders.append(
                {
                    "node_id": node_id,
                    "location": node.location_name,
                    "reminder": node.grim_reminder,
                    "ripeness": node.ripeness,
                }
            )

    return {
        "reminders": reminders,
        "total": len(reminders),
    }


@router.get("/visions/session")
async def get_session_visions(
    world_id: str,
    player_id: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    visions = world_engine.ghoul_veil.session_visions
    if player_id:
        visions = [v for v in visions if v.player_id == player_id]

    return {
        "visions": [v.to_dict() for v in visions],
        "total": len(visions),
    }


@router.get("/state")
async def get_ghoul_state(
    world_id: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    del world_id
    return world_engine.get_ghoul_state()
