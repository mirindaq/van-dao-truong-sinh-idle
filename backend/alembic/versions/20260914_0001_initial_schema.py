"""initial schema

Revision ID: 20260914_0001
Revises:
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260914_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "realms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("rank_order", sa.Integer(), nullable=False, unique=True),
        sa.Column("max_stage", sa.Integer(), nullable=False),
        sa.Column("base_required_exp", sa.Integer(), nullable=False),
        sa.Column("growth_factor", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_realms_key", "realms", ["key"])

    op.create_table(
        "spiritual_roots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("elements", postgresql.ARRAY(sa.String(length=40)), nullable=False),
        sa.Column("quality", sa.String(length=60), nullable=False),
        sa.Column("cultivation_modifier", sa.Float(), nullable=False),
        sa.Column("breakthrough_modifier", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_spiritual_roots_key", "spiritual_roots", ["key"])

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("realm_id", sa.Integer(), sa.ForeignKey("realms.id"), nullable=False),
        sa.Column("spiritual_root_id", sa.Integer(), sa.ForeignKey("spiritual_roots.id"), nullable=False),
        sa.Column("stage", sa.Integer(), nullable=False),
        sa.Column("cultivation_exp", sa.Float(), nullable=False),
        sa.Column("spirit_stones", sa.Integer(), nullable=False),
        sa.Column("qi_gathering_pills", sa.Integer(), nullable=False),
        sa.Column("combat_power", sa.Integer(), nullable=False),
        sa.Column("manual_key", sa.String(length=120), nullable=False),
        sa.Column("current_activity", sa.String(length=120), nullable=False),
        sa.Column("last_cultivation_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_players_realm_id", "players", ["realm_id"])
    op.create_index("ix_players_spiritual_root_id", "players", ["spiritual_root_id"])

    op.create_table(
        "game_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scope", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_game_logs_created_at", "game_logs", ["created_at"])
    op.create_index("ix_game_logs_scope", "game_logs", ["scope"])


def downgrade() -> None:
    op.drop_table("game_logs")
    op.drop_table("players")
    op.drop_table("spiritual_roots")
    op.drop_table("realms")
