from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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
    def __init__(self, session: AsyncSession, rng: RandomService | None = None):
        self.session, self.rng = session, rng or RandomService()
        self.players = PlayerRepository(session)
        self.game = GameStateService(session, self.rng)

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
                             state="resolving", message="Đang dò đường Thanh Vân Sơn.", battle_log=[], combat_snapshot={})
        self.session.add(run)
        await self.session.flush()
        if self.rng.roll() < 0.2:
            run.state, run.victory, run.message = "empty", True, "Thanh Vân Sơn lặng gió; không gặp địch."
        else:
            equipped = await self.game.equipment.list(player.id)
            equipment_bonus = 0
            for equipped_item in equipped:
                item = await self.session.get(Item, equipped_item.item_key)
                if item is not None:
                    equipment_bonus += item.combat_bonus
            power = player.combat_power + equipment_bonus
            player_combatant = Combatant(player.name, 40 + power, 10 + power // 5, 3 + power // 10, 8)
            enemy_combatant = Combatant("Dã Lang", 30, 8, 2, 5)
            run.combat_snapshot = {"player": player_combatant.__dict__, "enemy": enemy_combatant.__dict__}
            result = BattleEngine().resolve(
                player_combatant, enemy_combatant, self.rng)
            run.battle_log = result.turns
            run.victory = result.victory
            run.state = "victory" if result.victory else "defeat"
            run.message = "Bạn đánh bại Dã Lang." if result.victory else "Dã Lang đánh lui bạn."
            if result.victory:
                run.reward_stones, run.reward_pills = 10, 1
                player.spirit_stones += 10
                pill = await self.session.get(OwnedItem, (player.id, PILL_KEY))
                if pill is None:
                    raise GameError("inventory_unavailable", 500)
                pill.quantity += 1
        log = await self.game.logs.create("exploration", run.message)
        log.log_metadata = {
            "run_id": run.id,
            "request_id": run.request_id,
            "location_key": run.location_key,
            "state": run.state,
            "victory": run.victory,
            "reward_stones": run.reward_stones,
            "reward_pills": run.reward_pills,
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
