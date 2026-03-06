"""add party and myth support tables

Revision ID: 20260306_0004
Revises: 20260306_0003
Create Date: 2026-03-06 02:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260306_0004"
down_revision: Union[str, None] = "20260306_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _table_exists("parties"):
        op.create_table(
            "parties",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("litany_cut", sa.String(), nullable=False),
            sa.Column("bond_value", sa.Integer(), nullable=True),
            sa.Column("memythic_strain", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_parties_world_id", "parties", ["world_id"], unique=False)

    if not _table_exists("tested_threads"):
        op.create_table(
            "tested_threads",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("party_id", sa.String(), nullable=False),
            sa.Column("session_id", sa.String(), nullable=True),
            sa.Column("player_id", sa.String(), nullable=False),
            sa.Column("thread", sa.String(), nullable=False),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_tested_threads_party_id", "tested_threads", ["party_id"], unique=False)

    if not _table_exists("reverence_tokens"):
        op.create_table(
            "reverence_tokens",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("party_id", sa.String(), nullable=False),
            sa.Column("character_id", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("used", sa.Boolean(), nullable=True),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("earned_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_reverence_tokens_party_id", "reverence_tokens", ["party_id"], unique=False)
        op.create_index("ix_reverence_tokens_character_id", "reverence_tokens", ["character_id"], unique=False)

    if not _table_exists("artifact_discoveries"):
        op.create_table(
            "artifact_discoveries",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("artifact_key", sa.String(), nullable=False),
            sa.Column("location_id", sa.String(), nullable=True),
            sa.Column("wielded_by", sa.String(), nullable=True),
            sa.Column("discovered_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.Column("charge", sa.Float(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_artifact_discoveries_world_id", "artifact_discoveries", ["world_id"], unique=False)
        op.create_index("ix_artifact_discoveries_artifact_key", "artifact_discoveries", ["artifact_key"], unique=False)

    if not _table_exists("bond_events"):
        op.create_table(
            "bond_events",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("party_id", sa.String(), nullable=False),
            sa.Column("event_type", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("characters_involved", sa.JSON(), nullable=True),
            sa.Column("bond_change", sa.Integer(), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_bond_events_party_id", "bond_events", ["party_id"], unique=False)


def downgrade() -> None:
    if _table_exists("bond_events"):
        op.drop_index("ix_bond_events_party_id", table_name="bond_events")
        op.drop_table("bond_events")

    if _table_exists("artifact_discoveries"):
        op.drop_index("ix_artifact_discoveries_artifact_key", table_name="artifact_discoveries")
        op.drop_index("ix_artifact_discoveries_world_id", table_name="artifact_discoveries")
        op.drop_table("artifact_discoveries")

    if _table_exists("reverence_tokens"):
        op.drop_index("ix_reverence_tokens_character_id", table_name="reverence_tokens")
        op.drop_index("ix_reverence_tokens_party_id", table_name="reverence_tokens")
        op.drop_table("reverence_tokens")

    if _table_exists("tested_threads"):
        op.drop_index("ix_tested_threads_party_id", table_name="tested_threads")
        op.drop_table("tested_threads")

    if _table_exists("parties"):
        op.drop_index("ix_parties_world_id", table_name="parties")
        op.drop_table("parties")
