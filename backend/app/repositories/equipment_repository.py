from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.game.data.equipment import EQUIPMENT_DEFINITIONS
from app.models.item import EquippedItem, Item, OwnedItem


class EquipmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def claim(self, player_id: int):
        for definition in EQUIPMENT_DEFINITIONS:
            if await self.session.get(Item, definition['key']) is None:
                self.session.add(Item(**definition))
        await self.session.flush()
        for definition in EQUIPMENT_DEFINITIONS:
            owned = await self.session.get(OwnedItem, (player_id, definition['key']))
            if owned is None:
                self.session.add(OwnedItem(player_id=player_id, item_key=definition['key'], quantity=1))
            else:
                owned.quantity += 1
        await self.session.flush()

    async def list(self, player_id: int) -> list[EquippedItem]:
        return list((await self.session.scalars(select(EquippedItem).where(EquippedItem.player_id == player_id))).all())

    async def set_slot(self, player_id: int, slot: str, item_key: str | None):
        equipped = await self.session.get(EquippedItem, (player_id, slot))
        if item_key is None:
            if equipped is not None:
                await self.session.delete(equipped)
        elif equipped is None:
            self.session.add(EquippedItem(player_id=player_id, slot=slot, item_key=item_key))
        else:
            equipped.item_key = item_key
        await self.session.flush()
