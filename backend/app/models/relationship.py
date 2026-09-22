from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NpcRelationship(Base):
    __tablename__ = "npc_relationships"
    __table_args__ = (
        UniqueConstraint("player_id", "npc_key", name="npc_relationship_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    npc_key: Mapped[str] = mapped_column(String(80))
    affinity: Mapped[int] = mapped_column(Integer, default=0)
    last_interaction_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_available_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    active_prompt_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    active_prompt_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_prompt_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    active_prompt_choices: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    active_prompt_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class NpcInteractionReceipt(Base):
    __tablename__ = "npc_interaction_receipts"
    __table_args__ = (
        UniqueConstraint("player_id", "request_id", name="npc_interaction_request_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    relationship_id: Mapped[int] = mapped_column(
        ForeignKey("npc_relationships.id", ondelete="CASCADE"), index=True
    )
    npc_key: Mapped[str] = mapped_column(String(80))
    request_id: Mapped[str] = mapped_column(String(36))
    prompt_key: Mapped[str] = mapped_column(String(120))
    prompt_version: Mapped[int] = mapped_column(Integer)
    prompt_text: Mapped[str] = mapped_column(String(1000))
    choice_key: Mapped[str] = mapped_column(String(80))
    choice_text: Mapped[str] = mapped_column(String(500))
    response_text: Mapped[str] = mapped_column(String(1000))
    affinity_delta: Mapped[int] = mapped_column(Integer)
    resulting_affinity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

