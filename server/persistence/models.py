import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.sql import func

from server.database import Base
from server.models import Character, Cycle, Location, Session, World


def generate_uuid() -> str:
    return str(uuid.uuid4())


class WorldEvent(Base):
    __tablename__ = "world_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True)
    character_id = Column(String, nullable=True)
    location_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    payload = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())


class FactionState(Base):
    __tablename__ = "faction_state"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    reputation = Column(Float, default=0.0)
    influence = Column(Float, default=0.0)
    military_power = Column(Float, default=0.0)
    economic_power = Column(Float, default=0.0)
    relationships = Column(JSON, default=dict)
    color = Column(String, default="#808080")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class VeilNodeV2(Base):
    __tablename__ = "veil_nodes_v2"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=True)
    silence_level = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    node_type = Column(String, default="generic")
    payload = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class MapOverlay(Base):
    __tablename__ = "map_overlays"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=True)
    overlay_type = Column(String, nullable=False)
    data = Column(JSON, default=dict)
    color = Column(String, default="#000000")
    opacity = Column(Float, default=1.0)
    z_index = Column(Float, default=0)
    starts_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    permanent = Column(Boolean, default=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class LatticeCurrent(Base):
    __tablename__ = "lattice_currents"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    current_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    intensity = Column(Float, default=0.0)
    location_id = Column(String, nullable=True)
    character_id = Column(String, nullable=True)
    faction_id = Column(String, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_description = Column(Text, nullable=True)
    payload = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class LegacyLedgerV2(Base):
    __tablename__ = "legacy_ledger_v2"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    character_id = Column(String, nullable=False, index=True)
    entry_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location_id = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    mechanical_effect = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())


class Shard(Base):
    __tablename__ = "shards"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    memythic_charge = Column(Float, default=0.0)
    stability = Column(String, default="stable")
    payload = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class NarrativeThread(Base):
    __tablename__ = "narrative_threads"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location_id = Column(String, nullable=True)
    weight = Column(Float, default=0.0)
    resolved = Column(Boolean, default=False)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    payload = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Party(Base):
    __tablename__ = "parties"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    litany_cut = Column(String, nullable=False)
    bond_value = Column(Integer, default=0)
    memythic_strain = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class TestedThread(Base):
    __tablename__ = "tested_threads"

    id = Column(String, primary_key=True, default=generate_uuid)
    party_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True)
    player_id = Column(String, nullable=False)
    thread = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())


class ReverenceTokenModel(Base):
    __tablename__ = "reverence_tokens"

    id = Column(String, primary_key=True, default=generate_uuid)
    party_id = Column(String, nullable=False, index=True)
    character_id = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    earned_at = Column(DateTime, server_default=func.now())


class ArtifactDiscoveryModel(Base):
    __tablename__ = "artifact_discoveries"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    artifact_key = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=True)
    wielded_by = Column(String, nullable=True)
    discovered_at = Column(DateTime, server_default=func.now())
    last_used_at = Column(DateTime, nullable=True)
    charge = Column(Float, default=1.0)


class BondEventModel(Base):
    __tablename__ = "bond_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    party_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    characters_involved = Column(JSON, default=list)
    bond_change = Column(Integer, default=0)
    payload = Column("metadata", JSON, default=dict)
    timestamp = Column(DateTime, server_default=func.now())


class ShardGraveModel(Base):
    __tablename__ = "shard_graves"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    shard_name = Column(String, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    campaign_id = Column(String, nullable=False)
    legacy_ledger_id = Column(String, nullable=False)
    final_ritual_words = Column(JSON, default=list)
    total_retirements = Column(Integer, default=0)
    total_reverence = Column(Integer, default=0)
    major_plot = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())


class LargessSeedModel(Base):
    __tablename__ = "largess_seeds"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    grave_id = Column(String, nullable=True, index=True)
    seed_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    source_character = Column(String, nullable=True)
    source_player = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    campaign_id = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    claimed = Column(Boolean, default=False)
    claimed_by = Column(String, nullable=True)
    claimed_at = Column(DateTime, nullable=True)
    original_trope = Column(String, nullable=True)
    remixed_trope = Column(String, nullable=True)


class ShardDawnModel(Base):
    __tablename__ = "shard_dawns"

    id = Column(String, primary_key=True, default=generate_uuid)
    world_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    transition_type = Column(String, nullable=False)
    source_grave_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    claimed_seeds = Column(JSON, default=list)
    player_intents = Column(JSON, default=list)
    starting_motive_nodes = Column(JSON, default=list)
