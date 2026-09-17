from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.game.data.items import ITEM_DEFINITIONS, MANUAL_KEY, PILL_KEY
from app.models.item import Item, OwnedItem


class InventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def grant_initial(self, player_id: int) -> None:
        for definition in ITEM_DEFINITIONS:
            if await self.session.get(Item, definition["key"]) is None:
                self.session.add(Item(**definition))
        await self.session.flush()
        self.session.add_all([
            OwnedItem(player_id=player_id, item_key=PILL_KEY, quantity=3),
            OwnedItem(player_id=player_id, item_key=MANUAL_KEY, quantity=1),
        ])
        await self.session.flush()

    async def list(self, player_id: int) -> list[OwnedItem]:
        result = await self.session.execute(
            select(OwnedItem).where(OwnedItem.player_id == player_id).order_by(OwnedItem.item_key)
        )
        return list(result.scalars())

    async def get(self, player_id: int, item_key: str) -> OwnedItem | None:
        return await self.session.get(OwnedItem, (player_id, item_key))
