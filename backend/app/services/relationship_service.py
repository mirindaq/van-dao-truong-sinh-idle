from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.game_rules import GameRules, game_rules
from app.game.data.relationships import address_for, prompt_for
from app.models.player import Player
from app.models.relationship import NpcInteractionReceipt, NpcRelationship
from app.models.world import WorldNpc, WorldState
from app.schemas.relationship import (
    InteractionChoiceRead,
    InteractionPromptRead,
    InteractionReceiptRead,
    InteractionRequest,
    InteractionResponse,
    RelationshipProfileRead,
)
from app.services.game_state_service import GameError, GameStateService
from app.services.world_service import WorldService


class RelationshipService:
    def __init__(
        self,
        session: AsyncSession,
        now: datetime | None = None,
        rules: GameRules = game_rules,
    ):
        self.session = session
        self.now = now
        self.rules = rules
        self.game = GameStateService(session, rules=rules)

    def _now(self) -> datetime:
        return self.now or datetime.now(timezone.utc)

    async def get_profile(self, npc_key: str) -> RelationshipProfileRead:
        player, npc, relationship = await self._context(npc_key, lock=True)
        result = await self._profile(relationship, npc, self._now())
        await self.session.commit()
        return result

    async def open_prompt(self, npc_key: str) -> RelationshipProfileRead:
        _, npc, relationship = await self._context(npc_key, lock=True)
        now = self._now()
        if relationship.active_prompt_key is None:
            if relationship.next_available_at is not None and now < relationship.next_available_at:
                raise GameError("interaction_cooldown")
            prompt = prompt_for(npc_key, npc.activity)
            relationship.active_prompt_key = prompt.key
            relationship.active_prompt_version = prompt.version
            relationship.active_prompt_text = prompt.text
            relationship.active_prompt_choices = prompt.snapshot_choices()
            relationship.active_prompt_created_at = now
            await self.session.flush()
        result = await self._profile(relationship, npc, now)
        await self.session.commit()
        return result

    async def interact(self, npc_key: str, request: InteractionRequest) -> InteractionResponse:
        player = await self.game._load()
        await self.session.scalar(select(Player).where(Player.id == player.id).with_for_update())
        existing = await self._receipt(player.id, request.request_id)
        if existing is not None:
            return await self._replay(existing, npc_key, request)
        npc, relationship = await self._npc_and_relationship(player.id, npc_key, lock=True)
        existing = await self._receipt(player.id, request.request_id)
        if existing is not None:
            return await self._replay(existing, npc_key, request)
        if relationship.active_prompt_key is None:
            raise GameError("interaction_unavailable")
        if (
            relationship.active_prompt_key != request.prompt_key
            or relationship.active_prompt_version != request.prompt_version
        ):
            raise GameError("prompt_conflict")
        choice = next(
            (
                item
                for item in relationship.active_prompt_choices or []
                if item["key"] == request.choice_key
            ),
            None,
        )
        if choice is None:
            raise GameError("invalid_choice")
        now = self._now()
        previous_affinity = relationship.affinity
        relationship.affinity = min(
            self.rules.relationship_affinity_max,
            max(
                self.rules.relationship_affinity_min,
                relationship.affinity + int(choice["affinity_delta"]),
            ),
        )
        applied_delta = relationship.affinity - previous_affinity
        receipt = NpcInteractionReceipt(
            player_id=player.id,
            relationship_id=relationship.id,
            npc_key=npc_key,
            request_id=str(request.request_id),
            prompt_key=relationship.active_prompt_key,
            prompt_version=relationship.active_prompt_version,
            prompt_text=relationship.active_prompt_text,
            choice_key=choice["key"],
            choice_text=choice["text"],
            response_text=choice["response"],
            affinity_delta=applied_delta,
            resulting_affinity=relationship.affinity,
            created_at=now,
        )
        self.session.add(receipt)
        relationship.last_interaction_at = now
        relationship.next_available_at = now + timedelta(
            hours=self.rules.relationship_cooldown_hours
        )
        self._clear_prompt(relationship)
        await self.session.flush()
        profile = await self._profile(relationship, npc, now)
        await self.session.commit()
        return InteractionResponse(
            profile=profile,
            interaction=self._receipt_read(receipt),
        )

    async def get_interaction(self, request_id: UUID) -> InteractionResponse:
        player = await self.game._load()
        receipt = await self._receipt(player.id, request_id)
        if receipt is None:
            raise GameError("interaction_not_found", 404)
        npc, relationship = await self._npc_and_relationship(
            player.id, receipt.npc_key, lock=False
        )
        return InteractionResponse(
            profile=await self._profile(relationship, npc, self._now()),
            interaction=self._receipt_read(receipt),
        )

    async def _context(
        self, npc_key: str, lock: bool
    ) -> tuple[Player, WorldNpc, NpcRelationship]:
        player = await self.game._load()
        await self.session.scalar(select(Player).where(Player.id == player.id).with_for_update())
        npc, relationship = await self._npc_and_relationship(player.id, npc_key, lock)
        return player, npc, relationship

    async def _npc_and_relationship(
        self, player_id: int, npc_key: str, lock: bool
    ) -> tuple[WorldNpc, NpcRelationship]:
        world = await self.session.scalar(select(WorldState).where(WorldState.player_id == player_id))
        if world is None:
            world = await WorldService(
                self.session, now=self._now(), rules=self.rules
            )._ensure_world(player_id, self._now())
        npc = await self.session.scalar(
            select(WorldNpc).where(WorldNpc.world_id == world.id, WorldNpc.key == npc_key)
        )
        if npc is None:
            raise GameError("npc_not_found", 404)
        query = select(NpcRelationship).where(
            NpcRelationship.player_id == player_id,
            NpcRelationship.npc_key == npc_key,
        )
        if lock:
            query = query.with_for_update()
        relationship = await self.session.scalar(query)
        if relationship is None:
            relationship = NpcRelationship(
                player_id=player_id,
                npc_key=npc_key,
                affinity=self.rules.relationship_affinity_initial,
            )
            self.session.add(relationship)
            await self.session.flush()
        return npc, relationship

    async def _receipt(
        self, player_id: int, request_id: UUID
    ) -> NpcInteractionReceipt | None:
        return await self.session.scalar(
            select(NpcInteractionReceipt).where(
                NpcInteractionReceipt.player_id == player_id,
                NpcInteractionReceipt.request_id == str(request_id),
            )
        )

    async def _replay(
        self,
        receipt: NpcInteractionReceipt,
        npc_key: str,
        request: InteractionRequest,
    ) -> InteractionResponse:
        if (
            receipt.npc_key != npc_key
            or receipt.prompt_key != request.prompt_key
            or receipt.prompt_version != request.prompt_version
            or receipt.choice_key != request.choice_key
        ):
            raise GameError("interaction_request_conflict")
        npc, relationship = await self._npc_and_relationship(
            receipt.player_id, receipt.npc_key, lock=False
        )
        return InteractionResponse(
            profile=await self._profile(relationship, npc, self._now()),
            interaction=self._receipt_read(receipt),
        )

    async def _profile(
        self, relationship: NpcRelationship, npc: WorldNpc, now: datetime
    ) -> RelationshipProfileRead:
        rows = list(
            (
                await self.session.scalars(
                    select(NpcInteractionReceipt)
                    .where(NpcInteractionReceipt.relationship_id == relationship.id)
                    .order_by(desc(NpcInteractionReceipt.id))
                    .limit(10)
                )
            ).all()
        )
        prompt = None
        if relationship.active_prompt_key is not None:
            prompt = InteractionPromptRead(
                key=relationship.active_prompt_key,
                version=relationship.active_prompt_version,
                text=relationship.active_prompt_text,
                choices=[
                    InteractionChoiceRead(key=item["key"], text=item["text"])
                    for item in relationship.active_prompt_choices or []
                ],
                created_at=relationship.active_prompt_created_at,
            )
        return RelationshipProfileRead(
            npc_key=npc.key,
            npc_name=npc.name,
            affinity=relationship.affinity,
            address=address_for(relationship.affinity),
            last_interaction_at=relationship.last_interaction_at,
            next_available_at=relationship.next_available_at,
            can_interact=(
                relationship.active_prompt_key is not None
                or relationship.next_available_at is None
                or now >= relationship.next_available_at
            ),
            prompt=prompt,
            history=[self._receipt_read(row) for row in rows],
        )

    @staticmethod
    def _receipt_read(receipt: NpcInteractionReceipt) -> InteractionReceiptRead:
        return InteractionReceiptRead.model_validate(receipt, from_attributes=True)

    @staticmethod
    def _clear_prompt(relationship: NpcRelationship) -> None:
        relationship.active_prompt_key = None
        relationship.active_prompt_version = None
        relationship.active_prompt_text = None
        relationship.active_prompt_choices = None
        relationship.active_prompt_created_at = None
