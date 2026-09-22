"""Save timed journeys on exploration runs."""

from alembic import op
import sqlalchemy as sa


revision = "20260922_0010"
down_revision = "20260921_0009"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("exploration_runs", sa.Column("reward_item_key", sa.String(120), nullable=True))
    op.add_column("exploration_runs", sa.Column("reward_item_quantity", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("exploration_runs", sa.Column("available_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "one_traveling_journey",
        "exploration_runs",
        ["player_id"],
        unique=True,
        postgresql_where=sa.text("state = 'traveling'"),
    )


def downgrade():
    op.drop_index("one_traveling_journey", table_name="exploration_runs")
    op.drop_column("exploration_runs", "available_at")
    op.drop_column("exploration_runs", "reward_item_quantity")
    op.drop_column("exploration_runs", "reward_item_key")
