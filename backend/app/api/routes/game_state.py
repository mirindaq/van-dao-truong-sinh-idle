from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import GameStateRead
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("/state", response_model=GameStateRead)
async def get_game_state(session: AsyncSession = Depends(get_session)) -> GameStateRead:
    service = GameStateService(session)
    return await service.get_state()

