from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Cycle, World
from ..schemas import Cycle as CycleSchema
from ..schemas import CycleCreate

router = APIRouter()


@router.post("/", response_model=CycleSchema)
def create_cycle(payload: CycleCreate, db: Session = Depends(get_db)):
    world = db.query(World).filter(World.id == payload.world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    active_cycles = db.query(Cycle).filter(Cycle.world_id == payload.world_id, Cycle.status == "active").all()
    for cycle in active_cycles:
        cycle.status = "archived"

    cycle = Cycle(world_id=payload.world_id, name=payload.name, status="active")
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.get("/", response_model=List[CycleSchema])
def list_cycles(world_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Cycle)
    if world_id:
        query = query.filter(Cycle.world_id == world_id)
    return query.order_by(Cycle.started_at.desc()).all()


@router.get("/{cycle_id}", response_model=CycleSchema)
def get_cycle(cycle_id: str, db: Session = Depends(get_db)):
    cycle = db.query(Cycle).filter(Cycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle


@router.post("/{cycle_id}/archive", response_model=CycleSchema)
def archive_cycle(cycle_id: str, db: Session = Depends(get_db)):
    cycle = db.query(Cycle).filter(Cycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    cycle.status = "archived"
    db.commit()
    db.refresh(cycle)
    return cycle
