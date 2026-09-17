from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.game_state import BreakthroughRead, BreakthroughRequest, BreakthroughResult, BreakthroughSelection
from app.services.game_state_service import GameStateService

router = APIRouter()


@router.get("/preview", response_model=BreakthroughRead)
async def preview(item_key: str | None = None, quantity: int = Query(0, ge=0, le=1), session: AsyncSession = Depends(get_session)):
    try:
        selection = BreakthroughSelection(item_key=item_key, quantity=quantity)
    except ValidationError:
        raise HTTPException(status_code=422, detail="invalid_item") from None
    return await GameStateService(session).preview(selection)


@router.post("/attempt", response_model=BreakthroughResult)
async def attempt(body: BreakthroughRequest, session: AsyncSession = Depends(get_session)):
    return await GameStateService(session).attempt(body)
