"""Save one spirit-pet bond and its bond receipt per save."""

from alembic import op
import sqlalchemy as sa


revision = "20260923_0011"
down_revision = "20260922_0010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "spirit_pet_bonds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("pet_key", sa.String(80), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("bonded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("player_id", name="spirit_pet_bond_once"),
    )
    op.create_index("ix_spirit_pet_bonds_player_id", "spirit_pet_bonds", ["player_id"])
    op.create_table(
        "spirit_pet_receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("pet_key", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("player_id", "request_id", name="spirit_pet_request_once"),
    )
    op.create_index("ix_spirit_pet_receipts_player_id", "spirit_pet_receipts", ["player_id"])


def downgrade():
    op.drop_index("ix_spirit_pet_receipts_player_id", table_name="spirit_pet_receipts")
    op.drop_table("spirit_pet_receipts")
    op.drop_index("ix_spirit_pet_bonds_player_id", table_name="spirit_pet_bonds")
    op.drop_table("spirit_pet_bonds")
