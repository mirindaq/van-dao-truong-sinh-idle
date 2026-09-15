from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Realm(Base, TimestampMixin):
    __tablename__ = "realms"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    rank_order: Mapped[int] = mapped_column(unique=True)
    max_stage: Mapped[int]
    base_required_exp: Mapped[int]
    growth_factor: Mapped[float]
