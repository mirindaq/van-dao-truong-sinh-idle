from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player


class PlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_first(self) -> Player | None:
        result = await self.session.execute(select(Player).order_by(Player.id).limit(1))
        return result.scalars().first()

    async def lock_save(self) -> None:
        # Serialize the single local save, including the first creation before a row exists.
        await self.session.execute(text("SELECT pg_advisory_xact_lock(7419021)"))

    async def add(self, player: Player) -> Player:
        self.session.add(player)
        await self.session.flush()
        return player
