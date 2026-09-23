"""Save one alchemy receipt per craft request."""

from alembic import op
import sqlalchemy as sa


revision = "20260923_0012"
down_revision = "20260923_0011"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "alchemy_receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("recipe_key", sa.String(80), nullable=False),
        sa.Column("ingredient_key", sa.String(120), nullable=False),
        sa.Column("ingredient_quantity", sa.Integer(), nullable=False),
        sa.Column("result_key", sa.String(120), nullable=False),
        sa.Column("result_quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("player_id", "request_id", name="alchemy_request_once"),
    )
    op.create_index("ix_alchemy_receipts_player_id", "alchemy_receipts", ["player_id"])


def downgrade():
    op.drop_index("ix_alchemy_receipts_player_id", table_name="alchemy_receipts")
    op.drop_table("alchemy_receipts")
