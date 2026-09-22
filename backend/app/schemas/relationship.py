from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InteractionChoiceRead(BaseModel):
    key: str
    text: str


class InteractionPromptRead(BaseModel):
    key: str
    version: int
    text: str
    choices: list[InteractionChoiceRead]
    created_at: datetime


class InteractionReceiptRead(BaseModel):
    request_id: UUID
    npc_key: str
    prompt_key: str
    prompt_version: int
    prompt_text: str
    choice_key: str
    choice_text: str
    response_text: str
    affinity_delta: int
    resulting_affinity: int
    created_at: datetime


class RelationshipProfileRead(BaseModel):
    npc_key: str
    npc_name: str
    affinity: int
    address: str
    last_interaction_at: datetime | None
    next_available_at: datetime | None
    can_interact: bool
    prompt: InteractionPromptRead | None
    history: list[InteractionReceiptRead]


class InteractionRequest(BaseModel):
    request_id: UUID
    prompt_key: str = Field(min_length=1, max_length=120)
    prompt_version: int = Field(gt=0)
    choice_key: str = Field(min_length=1, max_length=80)


class InteractionResponse(BaseModel):
    profile: RelationshipProfileRead
    interaction: InteractionReceiptRead

