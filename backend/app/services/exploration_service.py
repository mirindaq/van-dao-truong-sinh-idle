from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.game_rules import GameRules, game_rules
from app.game.battle import BattleEngine, Combatant
from app.game.random_service import RandomService
from app.game.data.items import PILL_KEY
from app.models.exploration import ExplorationRun
from app.models.item import OwnedItem
from app.models.item import Item
from app.repositories.player_repository import PlayerRepository
from app.schemas.exploration import ExplorationRead, ExplorationRequest, ExplorationResponse
from app.services.game_state_service import GameError, GameStateService


class ExplorationService:
    def __init__(self, session: AsyncSession, rng: RandomService | None = None, rules: GameRules = game_rules):
        self.session, self.rng = session, rng or RandomService()
        self.rules = rules
        self.players = PlayerRepository(session)
        self.game = GameStateService(session, self.rng, rules)

    @staticmethod
    def _read(run: ExplorationRun) -> ExplorationRead:
        return ExplorationRead.model_validate(run, from_attributes=True)

    async def run(self, request: ExplorationRequest) -> ExplorationResponse:
        player = await self.game._load()
        existing = await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player.id, ExplorationRun.request_id == str(request.request_id)))
        if existing:
            return ExplorationResponse(state=await self.game._state(player), exploration=self._read(existing))
        if request.location_key != "qingyun_mountain":
            raise GameError("location_unavailable")
        run = ExplorationRun(player_id=player.id, request_id=str(request.request_id), location_key=request.location_key,
                             state="resolving", message="Đang dò đường Thanh Vân Sơn.", battle_log=[], combat_snapshot={},
                             rules_version=self.rules.rules_version, rules_fingerprint=self.rules.fingerprint)
        self.session.add(run)
        await self.session.flush()
        if self.rng.roll() < self.rules.exploration_empty_chance:
            run.state, run.victory, run.message = "empty", True, "Thanh Vân Sơn lặng gió; không gặp địch."
        else:
            equipped = await self.game.equipment.list(player.id)
            equipment_bonus = 0
            for equipped_item in equipped:
                item = await self.session.get(Item, equipped_item.item_key)
                if item is not None:
                    equipment_bonus += item.combat_bonus
            power = player.combat_power + equipment_bonus
            player_combatant = Combatant(
                player.name,
                self.rules.battle_player_hp_base + power,
                self.rules.battle_player_attack_base + power // self.rules.battle_player_attack_power_divisor,
                self.rules.battle_player_defense_base + power // self.rules.battle_player_defense_power_divisor,
                self.rules.battle_player_speed,
            )
            enemy_combatant = Combatant("Dã Lang", self.rules.battle_enemy_hp, self.rules.battle_enemy_attack,
                                        self.rules.battle_enemy_defense, self.rules.battle_enemy_speed)
            run.combat_snapshot = {"player": player_combatant.__dict__, "enemy": enemy_combatant.__dict__}
            result = BattleEngine(self.rules).resolve(
                player_combatant, enemy_combatant, self.rng)
            run.battle_log = result.turns
            run.victory = result.victory
            run.state = "victory" if result.victory else "defeat"
            run.message = "Bạn đánh bại Dã Lang." if result.victory else "Dã Lang đánh lui bạn."
            if result.victory:
                run.reward_stones = self.rules.exploration_reward_stones
                run.reward_pills = self.rules.exploration_reward_pills
                player.spirit_stones += self.rules.exploration_reward_stones
                pill = await self.session.get(OwnedItem, (player.id, PILL_KEY))
                if pill is None:
                    raise GameError("inventory_unavailable", 500)
                pill.quantity += self.rules.exploration_reward_pills
        log = await self.game.logs.create("exploration", run.message)
        log.log_metadata = {
            "run_id": run.id,
            "request_id": run.request_id,
            "location_key": run.location_key,
            "state": run.state,
            "victory": run.victory,
            "reward_stones": run.reward_stones,
            "reward_pills": run.reward_pills,
            "rules_version": run.rules_version,
            "rules_fingerprint": run.rules_fingerprint,
        }
        await self.session.flush()
        state = await self.game._state(player)
        await self.session.commit()
        return ExplorationResponse(state=state, exploration=self._read(run))

    async def get(self, request_id: UUID) -> ExplorationResponse:
        player = await self.game._load()
        run = await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player.id, ExplorationRun.request_id == str(request_id)))
        if run is None:
            raise GameError("exploration_not_found", 404)
        return ExplorationResponse(state=await self.game._state(player), exploration=self._read(run))

    async def latest(self) -> ExplorationResponse:
        player = await self.game._load()
        run = await self.session.scalar(select(ExplorationRun).where(
            ExplorationRun.player_id == player.id).order_by(ExplorationRun.id.desc()))
        if run is None:
            raise GameError("exploration_not_found", 404)
        return ExplorationResponse(state=await self.game._state(player), exploration=self._read(run))
