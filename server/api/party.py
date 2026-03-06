from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.bond_engine import BondEventType
from server.engine.party_origin_engine import LitanyCut
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/party", tags=["party"])


@router.post("/create")
async def create_party(
    litany_cut: str,
    party_name: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        cut = LitanyCut(litany_cut)
        party = world_engine.party_origin.create_party(cut, party_name)
        return party.get_state()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{party_id}")
async def get_party(party_id: str, world_engine: WorldEngine = Depends(get_world_engine)):
    party = world_engine.party_origin.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party.get_state()


@router.post("/{party_id}/thread")
async def record_thread(
    party_id: str,
    thread: str,
    player_id: str,
    note: str,
    session_id: str | None = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        return world_engine.party_origin.record_thread(party_id, thread, player_id, note, session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{party_id}/threads")
async def get_threads(party_id: str, world_engine: WorldEngine = Depends(get_world_engine)):
    party = world_engine.party_origin.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    return {
        "threads": party.tested_threads,
        "summary": {
            "total": len(party.tested_threads),
            "distinct": len({t["thread"] for t in party.tested_threads}),
        },
    }


@router.post("/{party_id}/bond")
async def update_bond(
    party_id: str,
    event_type: str,
    description: str,
    characters: List[str],
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        event = BondEventType(event_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = world_engine.bond_system.process_custom_event(
        party_id=party_id,
        event_type=event,
        description=description,
        characters=characters,
    )
    return result


@router.get("/{party_id}/bond")
async def get_bond(party_id: str, world_engine: WorldEngine = Depends(get_world_engine)):
    party = world_engine.party_origin.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    bond = world_engine.bond_system.get_bond_engine(party_id, initial_value=party.bond.value)
    return {
        "value": bond.bond_value,
        "bonuses": bond.get_bond_bonuses(),
        "narrative": bond.get_bond_narrative(),
        "memories": bond.get_shared_memories(),
    }


@router.post("/{party_id}/reverence/token")
async def add_reverence_token(
    party_id: str,
    character_id: str,
    description: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    party = world_engine.party_origin.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    token = party.add_reverence_token(character_id, description)
    world_engine.party_origin.tokens.create(party_id, character_id, description, token.earned_at)
    return {
        "token_id": token.id,
        "character_id": token.character_id,
        "description": token.description,
        "earned_at": token.earned_at.isoformat(),
    }


@router.post("/{party_id}/reverence/use")
async def use_reverence_token(
    party_id: str,
    token_id: str,
    token_type: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    party = world_engine.party_origin.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    used = party.use_reverence_token(token_id) or world_engine.party_origin.tokens.mark_used(token_id, used_at=datetime.utcnow())
    if not used:
        raise HTTPException(status_code=400, detail="Token not found or already used")

    try:
        return world_engine.reverence.process_reverence_token(token_id, token_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
