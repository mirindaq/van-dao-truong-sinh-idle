from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(String(500))
    asset_key: Mapped[str] = mapped_column(String(120))


class OwnedItem(Base):
    __tablename__ = "owned_items"
    __table_args__ = (CheckConstraint("quantity >= 0", name="owned_item_quantity_nonnegative"),)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    item_key: Mapped[str] = mapped_column(ForeignKey("items.key"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=0)
    item: Mapped[Item] = relationship(lazy="selectin")
