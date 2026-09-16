from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import BreakthroughRead, BreakthroughRequest, BreakthroughResult
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("/preview", response_model=BreakthroughRead)
async def preview(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).preview()


@router.post("/attempt", response_model=BreakthroughResult)
async def attempt(body: BreakthroughRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).attempt(body)
