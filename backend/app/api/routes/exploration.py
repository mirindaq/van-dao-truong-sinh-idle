from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_session
from app.schemas.exploration import ExplorationRequest, ExplorationResponse
from app.services.exploration_service import ExplorationService

router = APIRouter()


@router.post('/run', response_model=ExplorationResponse)
async def run(body: ExplorationRequest, session: AsyncSession = Depends(get_session)):
    return await ExplorationService(session).run(body)


@router.get('/run/{request_id}', response_model=ExplorationResponse)
async def get_run(request_id: UUID, session: AsyncSession = Depends(get_session)):
    return await ExplorationService(session).get(request_id)


@router.get('/latest', response_model=ExplorationResponse)
async def latest(session: AsyncSession = Depends(get_session)):
    return await ExplorationService(session).latest()


@router.get('/journey', response_model=ExplorationResponse)
async def journey(session: AsyncSession = Depends(get_session)):
    return await ExplorationService(session).current_journey()
