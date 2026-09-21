from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.game_state import GameStateRead


class ExplorationRequest(BaseModel):
    request_id: UUID
    location_key: str = Field(default="qingyun_mountain", pattern=r"^[a-z_]+$")


class ExplorationRead(BaseModel):
    id: int
    request_id: UUID
    location_key: str
    state: str
    message: str
    victory: bool | None
    reward_stones: int
    reward_pills: int
    battle_log: list[dict]
    combat_snapshot: dict
    rules_version: int
    rules_fingerprint: str
    created_at: datetime


class ExplorationResponse(BaseModel):
    state: GameStateRead
    exploration: ExplorationRead
