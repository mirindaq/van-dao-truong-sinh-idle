from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SpiritualRoot(Base, TimestampMixin):
    __tablename__ = "spiritual_roots"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    elements: Mapped[list[str]] = mapped_column(ARRAY(String(40)))
    quality: Mapped[str] = mapped_column(String(60))
    cultivation_modifier: Mapped[float] = mapped_column(default=1)
    breakthrough_modifier: Mapped[float] = mapped_column(default=1)
