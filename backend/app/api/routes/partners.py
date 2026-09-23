from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import GameStateRead, PartnerRequest, PartnerRosterRead
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("", response_model=PartnerRosterRead)
async def list_partners(session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).list_partners()


@router.post("/bond", response_model=GameStateRead)
async def bond(body: PartnerRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).bond_partner(body.npc_key)


@router.post("/dismiss", response_model=GameStateRead)
async def dismiss(body: PartnerRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).dismiss_partner(body.npc_key)