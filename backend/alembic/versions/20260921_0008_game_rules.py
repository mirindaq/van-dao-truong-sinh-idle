"""Track the game rules used by persisted receipts and reports."""
from alembic import op
import sqlalchemy as sa

revision = "20260921_0008"
down_revision = "20260918_0007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "game_rule_versions",
        sa.Column("version", sa.Integer(), primary_key=True),
        sa.Column("fingerprint", sa.String(32), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("exploration_runs", sa.Column("rules_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("exploration_runs", sa.Column("rules_fingerprint", sa.String(32), nullable=False, server_default="legacy"))
    op.add_column("world_states", sa.Column("rules_fingerprint", sa.String(32), nullable=False, server_default="legacy"))
    op.add_column("world_reports", sa.Column("rules_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("world_reports", sa.Column("rules_fingerprint", sa.String(32), nullable=False, server_default="legacy"))


def downgrade():
    op.drop_column("world_reports", "rules_fingerprint")
    op.drop_column("world_reports", "rules_version")
    op.drop_column("world_states", "rules_fingerprint")
    op.drop_column("exploration_runs", "rules_fingerprint")
    op.drop_column("exploration_runs", "rules_version")
    op.drop_table("game_rule_versions")
