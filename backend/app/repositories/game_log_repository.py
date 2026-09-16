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

    async def pending_offline(self) -> GameLog | None:
        result = await self.session.execute(select(GameLog).where(
            GameLog.scope == "cultivation",
            GameLog.log_metadata["pending"].as_boolean() == True,  # noqa: E712
        ).order_by(GameLog.id).limit(1))
        return result.scalar_one_or_none()

    async def attempt_receipt(self, request_id: str) -> GameLog | None:
        result = await self.session.execute(select(GameLog).where(
            GameLog.scope == "breakthrough",
            GameLog.log_metadata["request_id"].as_string() == request_id,
        ).limit(1))
        return result.scalar_one_or_none()
