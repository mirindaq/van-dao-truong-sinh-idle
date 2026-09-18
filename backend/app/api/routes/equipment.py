from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_session
from app.schemas.game_state import EquipRequest, GameStateRead
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.post('/claim', response_model=GameStateRead)
async def claim(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).claim_equipment_pack()


@router.post('/slot', response_model=GameStateRead)
async def equip(body: EquipRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).equip(body)
