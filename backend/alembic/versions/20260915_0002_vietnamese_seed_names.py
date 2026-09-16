"""Localize existing seed names without changing saved progression.

Revision ID: 20260915_0002
Revises: 20260914_0001
"""
from alembic import op
import sqlalchemy as sa

revision = "20260915_0002"
down_revision = "20260914_0001"
branch_labels = None
depends_on = None

NAMES = [
    ("mortal", "Pham Nhan", "Phàm Nhân"),
    ("qi_refining", "Luyen Khi", "Luyện Khí"),
    ("foundation_establishment", "Truc Co", "Trúc Cơ"),
    ("golden_core", "Kim Dan", "Kim Đan"),
    ("nascent_soul", "Nguyen Anh", "Nguyên Anh"),
    ("soul_formation", "Hoa Than", "Hóa Thần"),
    ("void_refinement", "Luyen Hu", "Luyện Hư"),
    ("body_integration", "Hop The", "Hợp Thể"),
    ("mahayana", "Dai Thua", "Đại Thừa"),
    ("tribulation", "Do Kiep", "Độ Kiếp"),
    ("human_immortal", "Nhan Tien", "Nhân Tiên"),
]
LOGS = [
    ("Ban tim thay dong phu bo hoang duoi chan Thanh Van Son.", "Bạn tìm thấy động phủ bỏ hoang dưới chân Thanh Vân Sơn."),
    ("Di vat con lai gom Thanh Moc Quyet, 10 Linh Thach va 3 Tu Khi Dan.", "Di vật còn lại gồm Thanh Mộc Quyết, 10 Linh Thạch và 3 Tụ Khí Đan."),
]


def upgrade():
    connection = op.get_bind()
    for key, old, new in NAMES:
        connection.execute(sa.text("UPDATE realms SET name=:new WHERE key=:key AND name=:old"), {"key": key, "old": old, "new": new})
    connection.execute(sa.text("UPDATE spiritual_roots SET name=:new WHERE key='wood_common' AND name='Moc Linh Can'"), {"new": "Mộc Linh Căn"})
    for old, new in LOGS:
        connection.execute(sa.text("UPDATE game_logs SET message=:new WHERE message=:old AND scope='player'"), {"old": old, "new": new})


def downgrade():
    # Display corrections are intentionally retained when rolling back the app.
    pass
