from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Literal
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
    revision: str
    item_key: str | None = None
    quantity: int = 0
    item_bonus: float = 0
    pills_owned: int = 0


class NewGameRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=40, pattern=r"^[^\x00-\x1f\x7f]+$")


class BreakthroughSelection(BaseModel):
    item_key: Literal["items/qi_gathering_pill"] | None = None
    quantity: int = Field(default=0, ge=0, le=1, strict=True)

    @model_validator(mode="after")
    def valid_selection(self):
        if (self.item_key is None) != (self.quantity == 0):
            raise ValueError("Item and quantity must match")
        return self


class BreakthroughRequest(BreakthroughSelection):
    request_id: UUID
    revision: str


class BreakthroughResult(BaseModel):
    success: bool
    message: str
    cultivation_lost: float
    realm: RealmRead
    item_key: str | None = None
    items_consumed: int = 0
    final_chance: float | None = None
    created_at: datetime | None = None


class PlayerRead(BaseModel):
    id: int
    name: str
    spirit_stones: int
    qi_gathering_pills: int
    combat_power: int
    base_combat_power: int
    equipment_bonus: int
    manual_key: str
    current_activity: str


class GameLogRead(BaseModel):
    id: int
    scope: str
    message: str
    created_at: datetime


class InventoryRead(BaseModel):
    key: str
    name: str
    category: str
    description: str
    asset_key: str
    quantity: int
    equipment_slot: str | None = None
    combat_bonus: int = 0


EquipmentSlot = Literal['weapon', 'head', 'body', 'feet', 'ring', 'amulet']


class EquipRequest(BaseModel):
    slot: EquipmentSlot
    item_key: str | None = Field(default=None, min_length=1, max_length=120)


class EquippedRead(BaseModel):
    slot: EquipmentSlot
    item_key: str


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
    inventory: list[InventoryRead]
    equipment: list[EquippedRead]
    equipment_pack_claimed: bool
