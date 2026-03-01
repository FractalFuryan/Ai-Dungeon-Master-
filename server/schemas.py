from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WorldBase(BaseModel):
    name: str


class WorldCreate(WorldBase):
    pass


class World(WorldBase, ORMBase):
    id: str
    entropy: float = 0.0
    reverence: float = 0.0
    created_at: datetime


class CycleBase(BaseModel):
    world_id: str
    name: str


class CycleCreate(CycleBase):
    pass


class Cycle(CycleBase, ORMBase):
    id: str
    status: str = "active"
    started_at: datetime
    ended_at: Optional[datetime] = None


class CharacterBase(BaseModel):
    cycle_id: str
    name: str
    vector_type: Optional[str] = None


class CharacterCreate(CharacterBase):
    pass


class Character(CharacterBase, ORMBase):
    id: str
    status: str = "active"
    reverence: float = 0.0
    xp: int = 0


class SessionBase(BaseModel):
    cycle_id: str
    notes: str = ""


class SessionCreate(SessionBase):
    pass


class Session(SessionBase, ORMBase):
    id: str
    date: datetime


class LocationBase(BaseModel):
    world_id: str
    name: str
    x: Optional[float] = None
    y: Optional[float] = None
    type: str = "ruin"


class LocationCreate(LocationBase):
    pass


class Location(LocationBase, ORMBase):
    id: str
    ecology_json: Dict[str, Any] = Field(default_factory=dict)
    arcanology_json: Dict[str, Any] = Field(default_factory=dict)
    history_json: Dict[str, Any] = Field(default_factory=dict)


class MapInkBase(BaseModel):
    location_id: str
    cycle_id: str
    player_name: str
    description: str


class MapInkCreate(MapInkBase):
    mechanical_bonus: float = 0.0


class MapInk(MapInkBase, ORMBase):
    id: str
    mechanical_bonus: float = 0.0
    created_at: datetime


class OpenCurrentBase(BaseModel):
    cycle_id: str
    description: str
    marker_type: str


class OpenCurrentCreate(OpenCurrentBase):
    intensity: float = 0.0


class OpenCurrent(OpenCurrentBase, ORMBase):
    id: str
    intensity: float = 0.0
    active: bool = True
    created_at: datetime


class RollRequest(BaseModel):
    base_modifier: float = 0
    positives: List[float] = Field(default_factory=list)
    negatives: List[float] = Field(default_factory=list)


class RollResponse(BaseModel):
    total: int
    rolls: List[int]
    modifier: float
    natural: int
    critical: bool
