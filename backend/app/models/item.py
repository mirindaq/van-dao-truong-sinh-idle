from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(String(500))
    asset_key: Mapped[str] = mapped_column(String(120))
    equipment_slot: Mapped[str | None] = mapped_column(String(20), nullable=True)
    combat_bonus: Mapped[int] = mapped_column(default=0)


class OwnedItem(Base):
    __tablename__ = "owned_items"
    __table_args__ = (CheckConstraint("quantity >= 0", name="owned_item_quantity_nonnegative"),)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    item_key: Mapped[str] = mapped_column(ForeignKey("items.key"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=0)
    item: Mapped[Item] = relationship(lazy="selectin")


class EquippedItem(Base):
    __tablename__ = 'equipped_items'
    __table_args__ = (
        ForeignKeyConstraint(['player_id', 'item_key'], ['owned_items.player_id', 'owned_items.item_key'], ondelete='CASCADE'),
        UniqueConstraint('player_id', 'item_key', name='equipped_item_once'),
        CheckConstraint("slot IN ('weapon','head','body','feet','ring','amulet')", name='equipment_slot_valid'),
    )
    player_id: Mapped[int] = mapped_column(primary_key=True)
    slot: Mapped[str] = mapped_column(String(20), primary_key=True)
    item_key: Mapped[str] = mapped_column(String(120))
