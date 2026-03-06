"""add shards table

Revision ID: 20260306_0002
Revises: 20260306_0001
Create Date: 2026-03-06 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260306_0002"
down_revision: Union[str, None] = "20260306_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists("shards"):
        return

    op.create_table(
        "shards",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("world_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("memythic_charge", sa.Float(), nullable=True),
        sa.Column("stability", sa.String(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shards_world_id", "shards", ["world_id"], unique=False)


def downgrade() -> None:
    if not _table_exists("shards"):
        return

    op.drop_index("ix_shards_world_id", table_name="shards")
    op.drop_table("shards")
