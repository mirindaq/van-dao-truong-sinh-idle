"""Save one dao-partner row per save and NPC."""

from alembic import op
import sqlalchemy as sa


revision = "20260923_0013"
down_revision = "20260923_0012"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "dao_partners",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("npc_key", sa.String(80), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("bonded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("player_id", "npc_key", name="dao_partner_once"),
    )
    op.create_index("ix_dao_partners_player_id", "dao_partners", ["player_id"])


def downgrade():
    op.drop_index("ix_dao_partners_player_id", table_name="dao_partners")
    op.drop_table("dao_partners")
