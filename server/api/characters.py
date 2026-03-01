from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Character, Cycle
from ..schemas import Character as CharacterSchema
from ..schemas import CharacterCreate

router = APIRouter()


@router.post("/", response_model=CharacterSchema)
def create_character(payload: CharacterCreate, db: Session = Depends(get_db)):
    cycle = db.query(Cycle).filter(Cycle.id == payload.cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    character = Character(cycle_id=payload.cycle_id, name=payload.name, vector_type=payload.vector_type)
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.get("/", response_model=List[CharacterSchema])
def list_characters(cycle_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Character)
    if cycle_id:
        query = query.filter(Character.cycle_id == cycle_id)
    return query.all()


@router.get("/{character_id}", response_model=CharacterSchema)
def get_character(character_id: str, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/{character_id}/xp", response_model=CharacterSchema)
def grant_xp(character_id: str, amount: int, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    character.xp = int(character.xp or 0) + amount
    db.commit()
    db.refresh(character)
    return character
