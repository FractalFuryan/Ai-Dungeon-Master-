import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class World(Base):
    __tablename__ = "worlds"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    entropy = Column(Float, default=0.0)
    reverence = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    cycles = relationship("Cycle", back_populates="world", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="world", cascade="all, delete-orphan")
    legacy_ledger = relationship("LegacyLedger", back_populates="world", cascade="all, delete-orphan")


class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)

    world = relationship("World", back_populates="cycles")
    sessions = relationship("Session", back_populates="cycle", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="cycle", cascade="all, delete-orphan")
    open_currents = relationship("OpenCurrent", back_populates="cycle", cascade="all, delete-orphan")
    map_inks = relationship("MapInk", back_populates="cycle", cascade="all, delete-orphan")
    veil_nodes = relationship("VeilNode", back_populates="cycle", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    cycle_id = Column(String, ForeignKey("cycles.id"), nullable=False)
    date = Column(DateTime, server_default=func.now())
    notes = Column(Text, default="")

    cycle = relationship("Cycle", back_populates="sessions")
    veil_descriptions = relationship("VeilDescription", back_populates="session", cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, default=generate_uuid)
    cycle_id = Column(String, ForeignKey("cycles.id"), nullable=False)
    name = Column(String, nullable=False)
    vector_type = Column(String, nullable=True)
    status = Column(String, default="active")
    reverence = Column(Float, default=0.0)
    xp = Column(Integer, default=0)

    cycle = relationship("Cycle", back_populates="characters")
    retirements = relationship("Retirement", back_populates="character", cascade="all, delete-orphan")
    perspective_vectors = relationship("PerspectiveVector", back_populates="character", cascade="all, delete-orphan")


class LegacyLedger(Base):
    __tablename__ = "legacy_ledger"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"), nullable=False)
    entry_type = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    mechanical_effect = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    world = relationship("World", back_populates="legacy_ledger")


class OpenCurrent(Base):
    __tablename__ = "open_currents"

    id = Column(String, primary_key=True, default=generate_uuid)
    cycle_id = Column(String, ForeignKey("cycles.id"), nullable=False)
    description = Column(Text, nullable=False)
    marker_type = Column(String, nullable=True)
    intensity = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    cycle = relationship("Cycle", back_populates="open_currents")


class Location(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, ForeignKey("worlds.id"), nullable=False)
    name = Column(String, nullable=False)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    type = Column(String, nullable=True)
    ecology_json = Column(JSON, default=dict)
    arcanology_json = Column(JSON, default=dict)
    history_json = Column(JSON, default=dict)

    world = relationship("World", back_populates="locations")
    map_inks = relationship("MapInk", back_populates="location", cascade="all, delete-orphan")
    veil_nodes = relationship("VeilNode", back_populates="location", cascade="all, delete-orphan")


class MapInk(Base):
    __tablename__ = "map_ink"

    id = Column(String, primary_key=True, default=generate_uuid)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    cycle_id = Column(String, ForeignKey("cycles.id"), nullable=False)
    player_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    mechanical_bonus = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    location = relationship("Location", back_populates="map_inks")
    cycle = relationship("Cycle", back_populates="map_inks")


class Retirement(Base):
    __tablename__ = "retirements"

    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    xp_banked = Column(Integer, default=0)
    deposit_multiplier = Column(Float, default=1.0)
    legacy_feature = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    character = relationship("Character", back_populates="retirements")


class VeilNode(Base):
    __tablename__ = "veil_nodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    cycle_id = Column(String, ForeignKey("cycles.id"), nullable=False)
    silence_level = Column(Float, default=0.0)
    active = Column(Boolean, default=True)

    location = relationship("Location", back_populates="veil_nodes")
    cycle = relationship("Cycle", back_populates="veil_nodes")
    descriptions = relationship("VeilDescription", back_populates="veil_node", cascade="all, delete-orphan")


class VeilDescription(Base):
    __tablename__ = "veil_descriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    veil_node_id = Column(String, ForeignKey("veil_nodes.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    player_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    scope = Column(String, default="session_only")

    veil_node = relationship("VeilNode", back_populates="descriptions")
    session = relationship("Session", back_populates="veil_descriptions")


class PerspectiveVector(Base):
    __tablename__ = "perspective_vectors"

    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    faction = Column(String, nullable=False)
    status = Column(String, default="free")
    institution_modifier = Column(Float, default=0.0)
    social_modifier = Column(Float, default=0.0)

    character = relationship("Character", back_populates="perspective_vectors")
