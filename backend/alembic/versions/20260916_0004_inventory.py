"""Persist inventory and transfer existing save quantities once."""
from alembic import op
import sqlalchemy as sa

revision = "20260916_0004"
down_revision = "20260916_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    items = op.create_table(
        "items",
        sa.Column("key", sa.String(120), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("asset_key", sa.String(120), nullable=False),
    )
    op.create_table(
        "owned_items",
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("item_key", sa.String(120), sa.ForeignKey("items.key"), primary_key=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint("quantity >= 0", name="owned_item_quantity_nonnegative"),
    )
    op.bulk_insert(items, [
        dict(key="items/qi_gathering_pill", name="Tụ Khí Đan", category="pill",
             asset_key="items/qi_gathering_pill",
             description="Dùng tối đa 1 viên khi đột phá. Tăng 10 điểm phần trăm cơ hội, tối đa 95%; tiêu hao cả khi thất bại."),
        dict(key="manual/qing_mu_jue", name="Thanh Mộc Quyết", category="manual",
             asset_key="manual/qing_mu_jue",
             description="Công pháp tìm thấy trong động phủ. Vật phẩm sở hữu, không tiêu hao; chưa có hiệu ứng cộng thêm."),
    ])
    # Preserve unknown legacy manual keys as owned records as well.
    op.execute("""INSERT INTO items (key, name, category, description, asset_key)
        SELECT DISTINCT manual_key, manual_key, 'manual', 'Công pháp đã sở hữu.', manual_key
        FROM players ON CONFLICT (key) DO NOTHING""")
    op.execute("""INSERT INTO owned_items (player_id, item_key, quantity)
        SELECT id, 'items/qi_gathering_pill', qi_gathering_pills FROM players""")
    op.execute("""INSERT INTO owned_items (player_id, item_key, quantity)
        SELECT id, manual_key, 1 FROM players""")
    op.drop_column("players", "qi_gathering_pills")


def downgrade() -> None:
    op.add_column("players", sa.Column("qi_gathering_pills", sa.Integer(), nullable=False, server_default="0"))
    op.execute("""UPDATE players SET qi_gathering_pills = owned_items.quantity
        FROM owned_items WHERE owned_items.player_id = players.id
        AND owned_items.item_key = 'items/qi_gathering_pill'""")
    op.drop_table("owned_items")
    op.drop_table("items")
