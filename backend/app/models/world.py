from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorldState(Base):
    __tablename__ = "world_states"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), unique=True, index=True)
    seed: Mapped[int] = mapped_column(Integer)
    rules_version: Mapped[int] = mapped_column(Integer, default=1)
    rules_fingerprint: Mapped[str] = mapped_column(String(32), default="legacy")
    total_ticks: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_simulated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WorldNpc(Base):
    __tablename__ = "world_npcs"
    __table_args__ = (UniqueConstraint("world_id", "key", name="world_npc_key_once"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("world_states.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500))
    spiritual_root: Mapped[str] = mapped_column(String(80))
    realm_key: Mapped[str] = mapped_column(String(80), default="qi_refining")
    stage: Mapped[int] = mapped_column(Integer)
    cultivation_exp: Mapped[float] = mapped_column(Float, default=0)
    cultivation_rate: Mapped[float] = mapped_column(Float)
    activity: Mapped[str] = mapped_column(String(30), default="cultivating")
    location: Mapped[str] = mapped_column(String(120), default="Thanh Vân Sơn")
    portrait_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    injured_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class WorldEvent(Base):
    __tablename__ = "world_events"
    __table_args__ = (UniqueConstraint("world_id", "tick_index", "source_key", "sequence", name="world_event_once"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("world_states.id", ondelete="CASCADE"), index=True)
    tick_index: Mapped[int] = mapped_column(Integer)
    source_key: Mapped[str] = mapped_column(String(80))
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    kind: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(String(500))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WorldReport(Base):
    __tablename__ = "world_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("world_states.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_ticks: Mapped[int] = mapped_column(Integer, default=0)
    skipped_seconds: Mapped[int] = mapped_column(Integer, default=0)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    npc_updates: Mapped[int] = mapped_column(Integer, default=0)
    rules_version: Mapped[int] = mapped_column(Integer, default=1)
    rules_fingerprint: Mapped[str] = mapped_column(String(32), default="legacy")
    npc_keys: Mapped[list[str]] = mapped_column(JSONB, default=list)
    summary: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    pending: Mapped[bool] = mapped_column(Boolean, default=True)
