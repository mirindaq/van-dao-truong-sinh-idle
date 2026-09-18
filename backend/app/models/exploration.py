from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ExplorationRun(Base):
    __tablename__ = "exploration_runs"
    __table_args__ = (UniqueConstraint("player_id", "request_id", name="exploration_request_once"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    request_id: Mapped[str] = mapped_column(String(36))
    location_key: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(500))
    victory: Mapped[bool | None] = mapped_column(nullable=True)
    reward_stones: Mapped[int] = mapped_column(Integer, default=0)
    reward_pills: Mapped[int] = mapped_column(Integer, default=0)
    battle_log: Mapped[list] = mapped_column(JSONB, default=list)
    combat_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
