from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import GameStateRead, PetBondRequest, PetBondResponse, PetCatalogRead
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("", response_model=PetCatalogRead)
async def list_pets(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).list_pets()


@router.post("/bond", response_model=PetBondResponse)
async def bond(body: PetBondRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).bond_pet(body)


@router.post("/rest", response_model=GameStateRead)
async def rest(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).rest_pet()


@router.post("/recall", response_model=GameStateRead)
async def recall(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).recall_pet()
