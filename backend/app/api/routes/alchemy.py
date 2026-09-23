from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import AlchemyCatalogRead, CraftRequest, CraftResponse
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("", response_model=AlchemyCatalogRead)
async def list_alchemy(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).list_alchemy()


@router.post("/craft", response_model=CraftResponse)
async def craft(body: CraftRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).craft(body)