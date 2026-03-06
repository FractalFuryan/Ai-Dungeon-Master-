from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_world_engine
from server.engine.myth_graph_engine import EdgeType, NodeType
from server.engine.world_engine import WorldEngine

router = APIRouter(prefix="/api/myth-graph", tags=["myth-graph"])


@router.post("/nodes")
async def create_node(
    world_id: str,
    name: str,
    node_type: str,
    properties: Optional[Dict[str, Any]] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        node = world_engine.add_to_myth_graph(
            name=name,
            node_type=NodeType(node_type).value,
            properties=properties,
        )
    except ValueError as exc:
        valid = ", ".join([nt.value for nt in NodeType])
        raise HTTPException(status_code=400, detail=f"Invalid node_type: {node_type}. Valid values: {valid}") from exc

    return {
        "id": node.id,
        "name": node.name,
        "type": node.node_type.value,
        "properties": node.properties,
        "weight": node.weight,
    }


@router.post("/edges")
async def create_edge(
    world_id: str,
    source_id: str,
    target_id: str,
    edge_type: str,
    properties: Optional[Dict[str, Any]] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        edge = world_engine.myth_graph.add_edge(
            source_id=source_id,
            target_id=target_id,
            edge_type=EdgeType(edge_type),
            properties=properties,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": edge.id,
        "source": edge.source_id,
        "target": edge.target_id,
        "type": edge.edge_type.value,
        "weight": edge.weight,
    }


@router.get("/nodes")
async def list_nodes(
    world_id: str,
    node_type: Optional[str] = None,
    name_contains: Optional[str] = None,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    try:
        parsed_type = NodeType(node_type) if node_type else None
    except ValueError as exc:
        valid = ", ".join([nt.value for nt in NodeType])
        raise HTTPException(status_code=400, detail=f"Invalid node_type: {node_type}. Valid values: {valid}") from exc

    nodes = world_engine.myth_graph.find_nodes(node_type=parsed_type, name_contains=name_contains)
    return [
        {
            "id": n.id,
            "name": n.name,
            "type": n.node_type.value,
            "properties": n.properties,
            "weight": n.weight,
        }
        for n in nodes
    ]


@router.get("/narrative/{node_id}")
async def get_node_narrative(node_id: str, world_engine: WorldEngine = Depends(get_world_engine)):
    node = world_engine.myth_graph.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"node_id": node_id, "narrative": world_engine.get_myth_narrative(node_id)}


@router.get("/clusters")
async def get_clusters(
    world_id: str,
    min_weight: float = 5.0,
    world_engine: WorldEngine = Depends(get_world_engine),
):
    clusters = world_engine.myth_graph.find_mythic_clusters(min_weight=min_weight)
    return {
        "count": len(clusters),
        "clusters": [[{"id": node.id, "name": node.name, "type": node.node_type.value} for node in cluster] for cluster in clusters],
    }


@router.post("/evolve")
async def evolve_graph(world_engine: WorldEngine = Depends(get_world_engine)):
    world_engine.myth_graph.evolve()
    return world_engine.myth_graph.get_graph_state()


@router.get("/state")
async def get_graph_state(world_engine: WorldEngine = Depends(get_world_engine)):
    return world_engine.myth_graph.get_graph_state()
