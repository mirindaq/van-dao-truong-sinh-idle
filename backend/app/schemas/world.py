from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class WorldNpcRead(BaseModel):
    key: str
    name: str
    description: str
    spiritual_root: str
    realm_key: str
    realm_name: str
    stage: int
    cultivation_exp: float
    required_exp: int
    activity: str
    location: str
    portrait_key: str | None
    injured_until: datetime | None
    updated_at: datetime


class WorldEventRead(BaseModel):
    id: int
    kind: str
    source_key: str
    message: str
    occurred_at: datetime


class WorldReportRead(BaseModel):
    id: int
    started_at: datetime
    ended_at: datetime
    processed_ticks: int
    skipped_seconds: int
    event_count: int
    npc_updates: int
    rules_version: int
    rules_fingerprint: str
    summary: dict[str, int]
    pending: bool


class WorldRead(BaseModel):
    updated_at: datetime
    tick_minutes: int
    max_offline_hours: int
    rules_version: int
    rules_fingerprint: str
    npcs: list[WorldNpcRead]
    events: list[WorldEventRead]
    next_cursor: int | None
    report: WorldReportRead | None


class WorldEventPage(BaseModel):
    events: list[WorldEventRead]
    next_cursor: int | None


WorldEventFilter = Literal["all", "npc", "world"]
