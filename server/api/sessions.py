from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..models import Cycle, Session
from ..schemas import Session as SessionSchema
from ..schemas import SessionCreate

router = APIRouter()


@router.post("/", response_model=SessionSchema)
def create_session(payload: SessionCreate, db: DBSession = Depends(get_db)):
    cycle = db.query(Cycle).filter(Cycle.id == payload.cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    session = Session(cycle_id=payload.cycle_id, notes=payload.notes)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=List[SessionSchema])
def list_sessions(cycle_id: str | None = None, db: DBSession = Depends(get_db)):
    query = db.query(Session)
    if cycle_id:
        query = query.filter(Session.cycle_id == cycle_id)
    return query.order_by(Session.date.desc()).all()


@router.get("/{session_id}", response_model=SessionSchema)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
