from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    realm_id: Mapped[int] = mapped_column(ForeignKey("realms.id"), index=True)
    spiritual_root_id: Mapped[int] = mapped_column(ForeignKey("spiritual_roots.id"), index=True)
    stage: Mapped[int] = mapped_column(default=1)
    cultivation_exp: Mapped[float] = mapped_column(default=0)
    spirit_stones: Mapped[int] = mapped_column(default=0)
    combat_power: Mapped[int] = mapped_column(default=1)
    equipment_pack_claimed: Mapped[bool] = mapped_column(default=False)
    manual_key: Mapped[str] = mapped_column(String(120), default="manual/qing_mu_jue")
    current_activity: Mapped[str] = mapped_column(String(120), default="cultivating")
    last_cultivation_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    realm: Mapped["Realm"] = relationship(lazy="selectin")
    spiritual_root: Mapped["SpiritualRoot"] = relationship(lazy="selectin")
