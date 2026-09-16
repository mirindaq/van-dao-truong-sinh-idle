from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import GameStateRead, NewGameRequest
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("/state", response_model=GameStateRead)
async def get_game_state(session: AsyncSession = Depends(get_session)) -> GameStateRead:
    service = GameStateService(session)
    return await service.get_state()


@router.post("/new", response_model=GameStateRead, status_code=201)
async def new_game(body: NewGameRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).new_game(body.name)


@router.post("/offline/{report_id}/ack", status_code=204)
async def acknowledge_offline(report_id: int, session: AsyncSession = Depends(get_session)):
    await GameStateService(session).acknowledge_offline(report_id)
    return Response(status_code=204)
