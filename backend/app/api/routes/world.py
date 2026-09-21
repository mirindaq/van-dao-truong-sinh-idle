from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.world import WorldEventFilter, WorldEventPage, WorldRead
from app.services.world_service import WorldService

router = APIRouter()


@router.get("/state", response_model=WorldRead)
async def get_world_state(
    session: Annotated[AsyncSession, Depends(get_session)],
    event_filter: WorldEventFilter = Query(default="all", alias="filter"),
) -> WorldRead:
    return await WorldService(session).get_state(event_filter)


@router.get("/events", response_model=WorldEventPage)
async def get_world_events(
    session: Annotated[AsyncSession, Depends(get_session)],
    event_filter: WorldEventFilter = Query(default="all", alias="filter"),
    before_id: int | None = Query(default=None, ge=1),
) -> WorldEventPage:
    return await WorldService(session).get_events(event_filter, before_id)


@router.post("/report/{report_id}/ack", status_code=status.HTTP_204_NO_CONTENT)
async def acknowledge_world_report(report_id: int, session: Annotated[AsyncSession, Depends(get_session)]) -> Response:
    await WorldService(session).acknowledge(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
