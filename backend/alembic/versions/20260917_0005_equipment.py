"""Equipment definitions, one-time pack claim and persisted slots."""
from alembic import op
import sqlalchemy as sa

revision = '20260917_0005'
down_revision = '20260916_0004'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('players', sa.Column('equipment_pack_claimed', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('items', sa.Column('equipment_slot', sa.String(20), nullable=True))
    op.add_column('items', sa.Column('combat_bonus', sa.Integer(), nullable=False, server_default='0'))
    items = sa.table('items', sa.column('key', sa.String), sa.column('name', sa.String),
                     sa.column('category', sa.String), sa.column('description', sa.String),
                     sa.column('asset_key', sa.String), sa.column('equipment_slot', sa.String),
                     sa.column('combat_bonus', sa.Integer))
    op.bulk_insert(items, [
        dict(key='items/bamboo_sword', name='Thanh Trúc Kiếm', category='equipment',
             description='Kiếm trúc nhẹ, cộng 5 chiến lực khi trang bị.', asset_key='items/bamboo_sword', equipment_slot='weapon', combat_bonus=5),
        dict(key='items/cloth_robe', name='Vải Thô Đạo Bào', category='equipment',
             description='Đạo bào giản dị, cộng 3 chiến lực khi trang bị.', asset_key='items/cloth_robe', equipment_slot='body', combat_bonus=3),
        dict(key='items/wood_amulet', name='Thanh Mộc Ngọc Bội', category='equipment',
             description='Ngọc bội mộc sắc, cộng 2 chiến lực khi trang bị.', asset_key='items/wood_amulet', equipment_slot='amulet', combat_bonus=2),
    ])
    op.create_table('equipped_items',
        sa.Column('player_id', sa.Integer(), primary_key=True),
        sa.Column('slot', sa.String(20), primary_key=True),
        sa.Column('item_key', sa.String(120), nullable=False),
        sa.ForeignKeyConstraint(['player_id', 'item_key'], ['owned_items.player_id', 'owned_items.item_key'], ondelete='CASCADE'),
        sa.UniqueConstraint('player_id', 'item_key', name='equipped_item_once'),
        sa.CheckConstraint("slot IN ('weapon','head','body','feet','ring','amulet')", name='equipment_slot_valid'))


def downgrade():
    op.drop_table('equipped_items')
    op.execute("DELETE FROM owned_items WHERE item_key IN ('items/bamboo_sword','items/cloth_robe','items/wood_amulet')")
    op.execute("DELETE FROM items WHERE key IN ('items/bamboo_sword','items/cloth_robe','items/wood_amulet')")
    op.drop_column('items', 'combat_bonus')
    op.drop_column('items', 'equipment_slot')
    op.drop_column('players', 'equipment_pack_claimed')
