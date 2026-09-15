from datetime import datetime

from pydantic import BaseModel


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

