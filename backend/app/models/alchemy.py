from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlchemyReceipt(Base):
    __tablename__ = "alchemy_receipts"
    __table_args__ = (
        UniqueConstraint("player_id", "request_id", name="alchemy_request_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    request_id: Mapped[str] = mapped_column(String(36))
    recipe_key: Mapped[str] = mapped_column(String(80))
    ingredient_key: Mapped[str] = mapped_column(String(120))
    ingredient_quantity: Mapped[int] = mapped_column(Integer)
    result_key: Mapped[str] = mapped_column(String(120))
    result_quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
