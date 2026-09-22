from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.relationship import (
    InteractionRequest,
    InteractionResponse,
    RelationshipProfileRead,
)
from app.services.relationship_service import RelationshipService


router = APIRouter()


@router.get("/npcs/{npc_key}", response_model=RelationshipProfileRead)
async def get_profile(
    npc_key: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RelationshipProfileRead:
    return await RelationshipService(session).get_profile(npc_key)


@router.post("/npcs/{npc_key}/prompt", response_model=RelationshipProfileRead)
async def open_prompt(
    npc_key: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RelationshipProfileRead:
    return await RelationshipService(session).open_prompt(npc_key)


@router.post("/npcs/{npc_key}/interactions", response_model=InteractionResponse)
async def interact(
    npc_key: str,
    body: InteractionRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InteractionResponse:
    return await RelationshipService(session).interact(npc_key, body)


@router.get("/interactions/{request_id}", response_model=InteractionResponse)
async def get_interaction(
    request_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InteractionResponse:
    return await RelationshipService(session).get_interaction(request_id)

