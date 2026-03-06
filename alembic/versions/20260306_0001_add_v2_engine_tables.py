"""add v2 engine tables

Revision ID: 20260306_0001
Revises: 
Create Date: 2026-03-06 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260306_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _table_exists("world_events"):
        op.create_table(
            "world_events",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("session_id", sa.String(), nullable=True),
            sa.Column("character_id", sa.String(), nullable=True),
            sa.Column("location_id", sa.String(), nullable=True),
            sa.Column("event_type", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_world_events_world_id", "world_events", ["world_id"], unique=False)
        op.create_index("ix_world_events_event_type", "world_events", ["event_type"], unique=False)

    if not _table_exists("faction_state"):
        op.create_table(
            "faction_state",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("reputation", sa.Float(), nullable=True),
            sa.Column("influence", sa.Float(), nullable=True),
            sa.Column("military_power", sa.Float(), nullable=True),
            sa.Column("economic_power", sa.Float(), nullable=True),
            sa.Column("relationships", sa.JSON(), nullable=True),
            sa.Column("color", sa.String(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_faction_state_world_id", "faction_state", ["world_id"], unique=False)

    if not _table_exists("veil_nodes_v2"):
        op.create_table(
            "veil_nodes_v2",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("location_id", sa.String(), nullable=True),
            sa.Column("silence_level", sa.Float(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=True),
            sa.Column("node_type", sa.String(), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_veil_nodes_v2_world_id", "veil_nodes_v2", ["world_id"], unique=False)

    if not _table_exists("map_overlays"):
        op.create_table(
            "map_overlays",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("location_id", sa.String(), nullable=True),
            sa.Column("overlay_type", sa.String(), nullable=False),
            sa.Column("data", sa.JSON(), nullable=True),
            sa.Column("color", sa.String(), nullable=True),
            sa.Column("opacity", sa.Float(), nullable=True),
            sa.Column("z_index", sa.Float(), nullable=True),
            sa.Column("starts_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("permanent", sa.Boolean(), nullable=True),
            sa.Column("created_by", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_map_overlays_world_id", "map_overlays", ["world_id"], unique=False)

    if not _table_exists("lattice_currents"):
        op.create_table(
            "lattice_currents",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("current_type", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("intensity", sa.Float(), nullable=True),
            sa.Column("location_id", sa.String(), nullable=True),
            sa.Column("character_id", sa.String(), nullable=True),
            sa.Column("faction_id", sa.String(), nullable=True),
            sa.Column("resolved", sa.Boolean(), nullable=True),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
            sa.Column("resolution_description", sa.Text(), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_lattice_currents_world_id", "lattice_currents", ["world_id"], unique=False)

    if not _table_exists("legacy_ledger_v2"):
        op.create_table(
            "legacy_ledger_v2",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("character_id", sa.String(), nullable=False),
            sa.Column("entry_type", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("location_id", sa.String(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=True),
            sa.Column("mechanical_effect", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_legacy_ledger_v2_world_id", "legacy_ledger_v2", ["world_id"], unique=False)
        op.create_index("ix_legacy_ledger_v2_character_id", "legacy_ledger_v2", ["character_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order.
    if _table_exists("legacy_ledger_v2"):
        op.drop_index("ix_legacy_ledger_v2_character_id", table_name="legacy_ledger_v2")
        op.drop_index("ix_legacy_ledger_v2_world_id", table_name="legacy_ledger_v2")
        op.drop_table("legacy_ledger_v2")

    if _table_exists("lattice_currents"):
        op.drop_index("ix_lattice_currents_world_id", table_name="lattice_currents")
        op.drop_table("lattice_currents")

    if _table_exists("map_overlays"):
        op.drop_index("ix_map_overlays_world_id", table_name="map_overlays")
        op.drop_table("map_overlays")

    if _table_exists("veil_nodes_v2"):
        op.drop_index("ix_veil_nodes_v2_world_id", table_name="veil_nodes_v2")
        op.drop_table("veil_nodes_v2")

    if _table_exists("faction_state"):
        op.drop_index("ix_faction_state_world_id", table_name="faction_state")
        op.drop_table("faction_state")

    if _table_exists("world_events"):
        op.drop_index("ix_world_events_event_type", table_name="world_events")
        op.drop_index("ix_world_events_world_id", table_name="world_events")
        op.drop_table("world_events")
