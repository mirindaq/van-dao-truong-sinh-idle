"""Persist NPC relationships, pending prompts and interaction receipts."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260921_0009"
down_revision = "20260921_0008"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "npc_relationships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("npc_key", sa.String(80), nullable=False),
        sa.Column("affinity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_available_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active_prompt_key", sa.String(120), nullable=True),
        sa.Column("active_prompt_version", sa.Integer(), nullable=True),
        sa.Column("active_prompt_text", sa.String(1000), nullable=True),
        sa.Column("active_prompt_choices", postgresql.JSONB(), nullable=True),
        sa.Column("active_prompt_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("player_id", "npc_key", name="npc_relationship_once"),
    )
    op.create_index("ix_npc_relationships_player_id", "npc_relationships", ["player_id"])
    op.create_table(
        "npc_interaction_receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("relationship_id", sa.Integer(), nullable=False),
        sa.Column("npc_key", sa.String(80), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("prompt_key", sa.String(120), nullable=False),
        sa.Column("prompt_version", sa.Integer(), nullable=False),
        sa.Column("prompt_text", sa.String(1000), nullable=False),
        sa.Column("choice_key", sa.String(80), nullable=False),
        sa.Column("choice_text", sa.String(500), nullable=False),
        sa.Column("response_text", sa.String(1000), nullable=False),
        sa.Column("affinity_delta", sa.Integer(), nullable=False),
        sa.Column("resulting_affinity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["relationship_id"], ["npc_relationships.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("player_id", "request_id", name="npc_interaction_request_once"),
    )
    op.create_index(
        "ix_npc_interaction_receipts_player_id",
        "npc_interaction_receipts",
        ["player_id"],
    )
    op.create_index(
        "ix_npc_interaction_receipts_relationship_id",
        "npc_interaction_receipts",
        ["relationship_id"],
    )


def downgrade():
    op.drop_index("ix_npc_interaction_receipts_relationship_id", table_name="npc_interaction_receipts")
    op.drop_index("ix_npc_interaction_receipts_player_id", table_name="npc_interaction_receipts")
    op.drop_table("npc_interaction_receipts")
    op.drop_index("ix_npc_relationships_player_id", table_name="npc_relationships")
    op.drop_table("npc_relationships")
