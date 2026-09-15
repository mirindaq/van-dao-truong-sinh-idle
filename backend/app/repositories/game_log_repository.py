from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game_log import GameLog


class GameLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, scope: str, message: str) -> GameLog:
        log = GameLog(scope=scope, message=message, log_metadata={})
        self.session.add(log)
        await self.session.flush()
        return log

    async def recent(self, limit: int = 10) -> list[GameLog]:
        result = await self.session.execute(
            select(GameLog).order_by(GameLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars())

