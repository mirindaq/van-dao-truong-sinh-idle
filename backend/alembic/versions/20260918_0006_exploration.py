"""Persist immediate exploration runs and battle logs."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260918_0006'
down_revision = '20260917_0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('exploration_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('request_id', sa.String(36), nullable=False),
        sa.Column('location_key', sa.String(80), nullable=False),
        sa.Column('state', sa.String(20), nullable=False),
        sa.Column('message', sa.String(500), nullable=False),
        sa.Column('victory', sa.Boolean(), nullable=True),
        sa.Column('reward_stones', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reward_pills', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('battle_log', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('combat_snapshot', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('player_id', 'request_id', name='exploration_request_once'))


def downgrade():
    op.drop_table('exploration_runs')
