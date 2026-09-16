from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class RealmRead(BaseModel):
    key: str
    name: str
    stage: int
    max_stage: int


class SpiritualRootRead(BaseModel):
    key: str
    name: str
    elements: list[str]
    quality: str
    cultivation_modifier: float
    breakthrough_modifier: float


class CultivationRead(BaseModel):
    current_exp: float
    required_exp: int
    rate_per_minute: float
    seconds_until_next_stage: int | None
    last_cultivation_at: datetime
    base_rate_per_minute: float
    root_bonus_per_minute: float


class OfflineRead(BaseModel):
    id: int
    elapsed_seconds: int
    earned_exp: float


class BreakthroughRead(BaseModel):
    available: bool
    target: RealmRead | None
    required_exp: int
    base_chance: float
    root_bonus: float
    final_chance: float
    failure_loss: float
    revision: datetime


class NewGameRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=40, pattern=r"^[^\x00-\x1f\x7f]+$")


class BreakthroughRequest(BaseModel):
    request_id: UUID
    revision: datetime


class BreakthroughResult(BaseModel):
    success: bool
    message: str
    cultivation_lost: float
    realm: RealmRead


class PlayerRead(BaseModel):
    id: int
    name: str
    spirit_stones: int
    qi_gathering_pills: int
    combat_power: int
    manual_key: str
    current_activity: str


class GameLogRead(BaseModel):
    id: int
    scope: str
    message: str
    created_at: datetime


class GameStateRead(BaseModel):
    player: PlayerRead
    realm: RealmRead
    spiritual_root: SpiritualRootRead
    cultivation: CultivationRead
    active_pet: str | None
    dao_partner: str | None
    recent_logs: list[GameLogRead]
    server_time: datetime
    offline_report: OfflineRead | None
    breakthrough: BreakthroughRead
