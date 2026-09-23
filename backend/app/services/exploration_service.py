from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.game_rules import GameRules, game_rules
from app.game.battle import BattleEngine, Combatant
from app.game.data.journeys import journey_definitions
from app.game.data.partners import partner_stack
from app.game.random_service import RandomService
from app.game.data.items import PILL_KEY
from app.models.exploration import ExplorationRun
from app.models.item import OwnedItem
from app.models.item import Item
from app.repositories.player_repository import PlayerRepository
from app.schemas.exploration import ExplorationRead, ExplorationRequest, ExplorationResponse
from app.services.game_state_service import GameError, GameStateService


def server_now() -> datetime:
    return ExplorationService.test_now or datetime.now(timezone.utc)


class ExplorationService:
    test_now: datetime | None = None
    test_rng_factory: Callable[[], RandomService] | None = None

    def __init__(self, session: AsyncSession, rng: RandomService | None = None, rules: GameRules = game_rules, now: Callable[[], datetime] | None = None):
        self.session = session
        self.rng = rng or (ExplorationService.test_rng_factory() if ExplorationService.test_rng_factory else RandomService())
        self.rules = rules
        self.now = now or (lambda: ExplorationService.test_now or datetime.now(timezone.utc))
        self.players = PlayerRepository(session)
        self.game = GameStateService(session, self.rng, rules)
        self.journeys = journey_definitions(rules)

    @staticmethod
    def _read(run: ExplorationRun) -> ExplorationRead:
        return ExplorationRead.model_validate(run, from_attributes=True)

    async def run(self, request: ExplorationRequest) -> ExplorationResponse:
        player = await self.game._load()
        existing = await self._by_request(player.id, str(request.request_id))
        if existing:
            if existing.location_key != request.location_key:
                raise GameError("request_conflict")
            return await self._finish_if_due(player, existing)
        if request.location_key == "qingyun_mountain":
            run = await self._begin(player, request, "Đang dò đường Thanh Vân Sơn.", None)
            await self._resolve(player, run, "Dã Lang", "Thanh Vân Sơn lặng gió; không gặp địch.", self.rules.exploration_reward_stones, self.rules.exploration_reward_pills, None, 0)
            return await self._commit_response(player, run)
        journey = self.journeys.get(request.location_key)
        if journey is None:
            raise GameError("location_unavailable")
        active = await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player.id, ExplorationRun.state == "traveling"))
        if active is not None:
            raise GameError("journey_in_progress")
        available = self.now() + timedelta(minutes=journey.minutes)
        run = await self._begin(player, request, f"Đang đi {journey.name}.", available)
        return await self._commit_response(player, run)

    async def get(self, request_id: UUID) -> ExplorationResponse:
        player = await self.game._load()
        run = await self._by_request(player.id, str(request_id))
        if run is None:
            raise GameError("exploration_not_found", 404)
        return await self._finish_if_due(player, run)

    async def latest(self) -> ExplorationResponse:
        player = await self.game._load()
        run = await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player.id).order_by(ExplorationRun.id.desc()))
        if run is None:
            raise GameError("exploration_not_found", 404)
        return await self._finish_if_due(player, run)

    async def current_journey(self) -> ExplorationResponse:
        player = await self.game._load()
        run = await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player.id, ExplorationRun.state == "traveling"))
        if run is None:
            run = await self.session.scalar(select(ExplorationRun).where(
                ExplorationRun.player_id == player.id, ExplorationRun.location_key != "qingyun_mountain",
            ).order_by(ExplorationRun.id.desc()))
        if run is None:
            raise GameError("exploration_not_found", 404)
        return await self._finish_if_due(player, run)

    async def _by_request(self, player_id: int, request_id: str) -> ExplorationRun | None:
        return await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player_id, ExplorationRun.request_id == request_id))

    async def _begin(self, player, request: ExplorationRequest, message: str, available_at: datetime | None) -> ExplorationRun:
        run = ExplorationRun(
            player_id=player.id, request_id=str(request.request_id), location_key=request.location_key,
            state="traveling" if available_at else "resolving", message=message, battle_log=[], combat_snapshot={},
            available_at=available_at, rules_version=self.rules.rules_version, rules_fingerprint=self.rules.fingerprint,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def _finish_if_due(self, player, run: ExplorationRun) -> ExplorationResponse:
        if run.state == "traveling" and run.available_at is not None and self.now() >= run.available_at:
            journey = self.journeys[run.location_key]
            await self._resolve(
                player, run, journey.enemy, f"{journey.name} lặng gió; không gặp địch.",
                0, 0, journey.item_key, journey.item_quantity,
            )
            return await self._commit_response(player, run)
        return ExplorationResponse(state=await self.game._state(player), exploration=self._read(run))

    async def _resolve(self, player, run: ExplorationRun, enemy: str, empty_message: str, stones: int, pills: int, item_key: str | None, item_quantity: int) -> None:
        if self.rng.roll() < self.rules.exploration_empty_chance:
            run.state, run.victory, run.message = "empty", True, empty_message
        else:
            equipped = await self.game.equipment.list(player.id)
            equipment_bonus = 0
            for equipped_item in equipped:
                item = await self.session.get(Item, equipped_item.item_key)
                if item is not None:
                    equipment_bonus += item.combat_bonus
            bond = await self.game._bond(player.id)
            partners = await self.game._active_partner_count(player.id)
            partner_bonus, _, _ = partner_stack(self.rules, partners)
            power = player.combat_power + equipment_bonus + self.game.pet_combat_bonus(bond) + partner_bonus
            player_combatant = Combatant(
                player.name,
                self.rules.battle_player_hp_base + power,
                self.rules.battle_player_attack_base + power // self.rules.battle_player_attack_power_divisor,
                self.rules.battle_player_defense_base + power // self.rules.battle_player_defense_power_divisor,
                self.rules.battle_player_speed,
            )
            enemy_combatant = Combatant(enemy, self.rules.battle_enemy_hp, self.rules.battle_enemy_attack,
                                        self.rules.battle_enemy_defense, self.rules.battle_enemy_speed)
            run.combat_snapshot = {"player": player_combatant.__dict__, "enemy": enemy_combatant.__dict__}
            result = BattleEngine(self.rules).resolve(player_combatant, enemy_combatant, self.rng)
            run.battle_log = result.turns
            run.victory = result.victory
            run.state = "victory" if result.victory else "defeat"
            run.message = f"Bạn đánh bại {enemy}." if result.victory else f"{enemy} đánh lui bạn."
            if result.victory:
                run.reward_stones = stones
                run.reward_pills = pills
                player.spirit_stones += stones
                if pills:
                    pill = await self.session.get(OwnedItem, (player.id, PILL_KEY))
                    if pill is None:
                        raise GameError("inventory_unavailable", 500)
                    pill.quantity += pills
                if item_key and item_quantity:
                    run.reward_item_key = item_key
                    run.reward_item_quantity = item_quantity
                    owned = await self.session.get(OwnedItem, (player.id, item_key))
                    if owned is None:
                        self.session.add(OwnedItem(player_id=player.id, item_key=item_key, quantity=item_quantity))
                    else:
                        owned.quantity += item_quantity
        log = await self.game.logs.create("exploration", run.message)
        log.log_metadata = {
            "run_id": run.id,
            "request_id": run.request_id,
            "location_key": run.location_key,
            "state": run.state,
            "victory": run.victory,
            "reward_stones": run.reward_stones,
            "reward_pills": run.reward_pills,
            "reward_item_key": run.reward_item_key,
            "reward_item_quantity": run.reward_item_quantity,
            "rules_version": run.rules_version,
            "rules_fingerprint": run.rules_fingerprint,
        }
        await self.session.flush()

    async def _commit_response(self, player, run: ExplorationRun) -> ExplorationResponse:
        state = await self.game._state(player)
        await self.session.commit()
        return ExplorationResponse(state=state, exploration=self._read(run))
