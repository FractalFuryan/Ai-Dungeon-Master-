from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.oracle_engine import OracleIntent
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/myth", tags=["myth"])


@router.post("/oracle/draw")
async def draw_symbol(
    intent: Optional[str] = None,
    context: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    oracle_intent = OracleIntent(intent) if intent else None
    symbol = world_engine.oracle.draw_symbol(oracle_intent, context)
    return {
        "symbol": symbol.symbol,
        "archetype": symbol.archetype,
        "meaning": symbol.meaning,
        "resonance": symbol.resonance,
        "intensity": symbol.intensity,
    }


@router.post("/oracle/spread")
async def draw_spread(
    count: int = 3,
    intent: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    oracle_intent = OracleIntent(intent) if intent else None
    symbols = world_engine.oracle.get_spread(count, oracle_intent)
    interpretation = world_engine.oracle.interpret_spread(symbols)
    return {
        "symbols": [
            {
                "symbol": s.symbol,
                "archetype": s.archetype,
                "meaning": s.meaning,
                "resonance": s.resonance,
            }
            for s in symbols
        ],
        "interpretation": interpretation,
    }


@router.post("/inversion/generate")
async def generate_inversion(
    entity_type: str,
    entity_name: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    entity_id = f"{entity_type}_{entity_name}"
    world_engine.inversion.register_entity(entity_id, entity_type, entity_name)
    return world_engine.inversion.invert_assumption(entity_id)


@router.get("/inversion/state/{entity_id}")
async def get_inversion_state(entity_id: str, world_engine: WorldEngine = Depends(get_world_engine)):
    state = world_engine.inversion.get_entangled_state(entity_id)
    if not state:
        raise HTTPException(status_code=404, detail="Entity not found")
    return state


@router.post("/veil/propagate")
async def propagate_veil(delta: float = 0.1, world_engine: WorldEngine = Depends(get_world_engine)):
    triggers = world_engine.veil.propagate_all(delta)
    return {"triggers": triggers, "count": len(triggers)}


@router.get("/veil/nodes")
async def get_veil_nodes(
    location_id: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    world_engine.veil._load_nodes()
    if location_id:
        for node_id, node in world_engine.veil.nodes.items():
            if node.location_id == location_id:
                return world_engine.veil.get_node_state_detail(node_id)
        raise HTTPException(status_code=404, detail="No veil node at location")

    return {node_id: world_engine.veil.get_node_state_detail(node_id) for node_id in world_engine.veil.nodes}


@router.post("/pressure/field")
async def create_pressure_field(
    name: str,
    source_type: str,
    source_id: str,
    strength: float,
    radius: float,
    influence_type: str,
    center_location: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    field_id = world_engine.pressure.create_field(
        name=name,
        source_type=source_type,
        source_id=source_id,
        center_location=center_location,
        strength=strength,
        radius=radius,
        influence_type=influence_type,
    )
    return {"field_id": field_id, "name": name}


@router.get("/pressure/fields")
async def get_pressure_fields(
    location_id: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    if location_id:
        return world_engine.pressure.get_fields_at_location(location_id)

    return [
        {
            "id": f.id,
            "name": f.name,
            "type": f.influence_type,
            "strength": f.strength,
            "radius": f.radius,
        }
        for f in world_engine.pressure.fields.values()
    ]


@router.post("/director/intervene")
async def director_intervene(context: Dict[str, Any], world_engine: WorldEngine = Depends(get_world_engine)):
    move_name = world_engine.director.should_intervene(context)
    if move_name:
        return world_engine.director.execute_move(move_name, context)
    return {"message": "No intervention needed"}


@router.get("/director/moves")
async def get_director_moves(
    recent: bool = True,
    count: int = 5,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    if recent:
        return world_engine.director.get_recent_moves(count)
    return list(world_engine.director.available_moves.keys())


@router.get("/shard/state")
async def get_shard_state(world_engine: WorldEngine = Depends(get_world_engine)):
    return world_engine.shard_state.to_dict()


@router.post("/shard/symbol")
async def inject_symbol(
    symbol_name: str,
    archetype: Optional[str] = None,
    context: str = "",
    intensity: float = 0.5,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    from server.engine.memythic_engine import SymbolInjection

    injection = SymbolInjection(
        symbol=symbol_name,
        archetype=archetype,
        context=context,
        intensity=float(intensity),
    )
    result = world_engine.memythic.inject_symbol(injection)
    world_engine.shard.persist_runtime_state(world_engine.shard_state)
    return result


@router.post("/threads/create")
async def create_thread(
    title: str,
    description: str,
    location_id: Optional[str] = None,
    weight: float = 0.4,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    thread_id = world_engine.threads.create_thread(
        title=title,
        description=description,
        location_id=location_id,
        weight=weight,
    )
    return {"thread_id": thread_id, "title": title}


@router.post("/threads/ripen")
async def ripen_threads(
    delta: float = 0.1,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.threads.ripen(delta=delta)


@router.get("/threads")
async def list_threads(
    include_resolved: bool = False,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    return world_engine.threads.list_threads(include_resolved=include_resolved)


@router.post("/threads/resolve")
async def resolve_thread(
    thread_id: str,
    resolution: str,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    ok = world_engine.threads.resolve_thread(thread_id, resolution)
    if not ok:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"resolved": True, "thread_id": thread_id}
