from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player


class PlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_first(self) -> Player | None:
        result = await self.session.execute(select(Player).order_by(Player.id).limit(1))
        return result.scalars().first()

    async def add(self, player: Player) -> Player:
        self.session.add(player)
        await self.session.flush()
        return player

