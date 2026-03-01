from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Cycle, LegacyLedger, World
from ..schemas import Cycle as CycleSchema
from ..schemas import World as WorldSchema
from ..schemas import WorldCreate

router = APIRouter()


@router.post("/", response_model=WorldSchema)
def create_world(world: WorldCreate, db: Session = Depends(get_db)):
    db_world = World(name=world.name)
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world


@router.get("/", response_model=List[WorldSchema])
def list_worlds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(World).offset(skip).limit(limit).all()


@router.get("/{world_id}", response_model=WorldSchema)
def get_world(world_id: str, db: Session = Depends(get_db)):
    world = db.query(World).filter(World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    return world


@router.get("/{world_id}/legacy")
def get_world_legacy(world_id: str, db: Session = Depends(get_db)):
    world = db.query(World).filter(World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    entries = (
        db.query(LegacyLedger)
        .filter(LegacyLedger.world_id == world_id)
        .order_by(LegacyLedger.created_at.desc())
        .all()
    )
    return entries


@router.post("/{world_id}/cycles", response_model=CycleSchema)
def start_new_cycle(world_id: str, name: str, db: Session = Depends(get_db)):
    world = db.query(World).filter(World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    active_cycles = db.query(Cycle).filter(Cycle.world_id == world_id, Cycle.status == "active").all()
    for cycle in active_cycles:
        cycle.status = "archived"

    new_cycle = Cycle(world_id=world_id, name=name, status="active")
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)
    return new_cycle
