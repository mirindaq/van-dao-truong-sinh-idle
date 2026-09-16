"""Localize the old default player name.

Revision ID: 20260916_0003
Revises: 20260915_0002
"""
from alembic import op
import sqlalchemy as sa

revision = "20260916_0003"
down_revision = "20260915_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().execute(
        sa.text("UPDATE players SET name='Vô Danh' WHERE name='Vo Danh'")
    )


def downgrade():
    # Display corrections are intentionally retained when rolling back the app.
    pass
