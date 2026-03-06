"""add largess protocol tables

Revision ID: 20260306_0005
Revises: 20260306_0004
Create Date: 2026-03-06 03:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260306_0005"
down_revision: Union[str, None] = "20260306_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _table_exists("shard_graves"):
        op.create_table(
            "shard_graves",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("shard_name", sa.String(), nullable=False),
            sa.Column("completed_at", sa.DateTime(), nullable=False),
            sa.Column("campaign_id", sa.String(), nullable=False),
            sa.Column("legacy_ledger_id", sa.String(), nullable=False),
            sa.Column("final_ritual_words", sa.JSON(), nullable=True),
            sa.Column("total_retirements", sa.Integer(), nullable=True),
            sa.Column("total_reverence", sa.Integer(), nullable=True),
            sa.Column("major_plot", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_shard_graves_world_id", "shard_graves", ["world_id"], unique=False)

    if not _table_exists("largess_seeds"):
        op.create_table(
            "largess_seeds",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("grave_id", sa.String(), nullable=True),
            sa.Column("seed_type", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("source_character", sa.String(), nullable=True),
            sa.Column("source_player", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("campaign_id", sa.String(), nullable=False),
            sa.Column("weight", sa.Float(), nullable=True),
            sa.Column("claimed", sa.Boolean(), nullable=True),
            sa.Column("claimed_by", sa.String(), nullable=True),
            sa.Column("claimed_at", sa.DateTime(), nullable=True),
            sa.Column("original_trope", sa.String(), nullable=True),
            sa.Column("remixed_trope", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_largess_seeds_world_id", "largess_seeds", ["world_id"], unique=False)
        op.create_index("ix_largess_seeds_grave_id", "largess_seeds", ["grave_id"], unique=False)

    if not _table_exists("shard_dawns"):
        op.create_table(
            "shard_dawns",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("world_id", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("transition_type", sa.String(), nullable=False),
            sa.Column("source_grave_id", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("claimed_seeds", sa.JSON(), nullable=True),
            sa.Column("player_intents", sa.JSON(), nullable=True),
            sa.Column("starting_motive_nodes", sa.JSON(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_shard_dawns_world_id", "shard_dawns", ["world_id"], unique=False)


def downgrade() -> None:
    if _table_exists("shard_dawns"):
        op.drop_index("ix_shard_dawns_world_id", table_name="shard_dawns")
        op.drop_table("shard_dawns")

    if _table_exists("largess_seeds"):
        op.drop_index("ix_largess_seeds_grave_id", table_name="largess_seeds")
        op.drop_index("ix_largess_seeds_world_id", table_name="largess_seeds")
        op.drop_table("largess_seeds")

    if _table_exists("shard_graves"):
        op.drop_index("ix_shard_graves_world_id", table_name="shard_graves")
        op.drop_table("shard_graves")
