"""Persist NPC simulation, world news and return reports."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260918_0007"
down_revision = "20260918_0006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("world_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("rules_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("total_ticks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_simulated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("player_id", name="world_state_player_once"))
    op.create_index("ix_world_states_player_id", "world_states", ["player_id"])
    op.create_table("world_npcs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("world_id", sa.Integer(), sa.ForeignKey("world_states.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(80), nullable=False), sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500), nullable=False), sa.Column("spiritual_root", sa.String(80), nullable=False),
        sa.Column("realm_key", sa.String(80), nullable=False, server_default="qi_refining"),
        sa.Column("stage", sa.Integer(), nullable=False), sa.Column("cultivation_exp", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cultivation_rate", sa.Float(), nullable=False), sa.Column("activity", sa.String(30), nullable=False, server_default="cultivating"),
        sa.Column("location", sa.String(120), nullable=False, server_default="Thanh Vân Sơn"),
        sa.Column("portrait_key", sa.String(120), nullable=True), sa.Column("injured_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("world_id", "key", name="world_npc_key_once"))
    op.create_index("ix_world_npcs_world_id", "world_npcs", ["world_id"])
    op.create_table("world_events",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("world_id", sa.Integer(), sa.ForeignKey("world_states.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tick_index", sa.Integer(), nullable=False), sa.Column("source_key", sa.String(80), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="0"), sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("message", sa.String(500), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("world_id", "tick_index", "source_key", "sequence", name="world_event_once"))
    op.create_index("ix_world_events_world_id", "world_events", ["world_id"])
    op.create_table("world_reports",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("world_id", sa.Integer(), sa.ForeignKey("world_states.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False), sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_ticks", sa.Integer(), nullable=False, server_default="0"), sa.Column("skipped_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("event_count", sa.Integer(), nullable=False, server_default="0"), sa.Column("npc_updates", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("npc_keys", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("summary", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("pending", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_world_reports_world_id", "world_reports", ["world_id"])


def downgrade():
    op.drop_table("world_reports")
    op.drop_table("world_events")
    op.drop_table("world_npcs")
    op.drop_index("ix_world_states_player_id", table_name="world_states")
    op.drop_table("world_states")
