from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SpiritPetBond(Base):
    __tablename__ = "spirit_pet_bonds"
    __table_args__ = (UniqueConstraint("player_id", name="spirit_pet_bond_once"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    pet_key: Mapped[str] = mapped_column(String(80))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    request_id: Mapped[str] = mapped_column(String(36))
    bonded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    state_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SpiritPetReceipt(Base):
    __tablename__ = "spirit_pet_receipts"
    __table_args__ = (
        UniqueConstraint("player_id", "request_id", name="spirit_pet_request_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    request_id: Mapped[str] = mapped_column(String(36))
    pet_key: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
