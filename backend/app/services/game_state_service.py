from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.game.breakthrough import BreakthroughEngine
from app.game.cultivation import CultivationEngine, CultivationInput
from app.game.data.realms import REALM_DEFINITIONS, required_exp_for_stage
from app.game.random_service import RandomService
from app.models.player import Player
from app.models.realm import Realm
from app.models.spiritual_root import SpiritualRoot
from app.repositories.game_log_repository import GameLogRepository
from app.repositories.player_repository import PlayerRepository
from app.repositories.realm_repository import RealmRepository
from app.schemas.game_state import (
    BreakthroughRead, BreakthroughRequest, BreakthroughResult, CultivationRead,
    GameLogRead, GameStateRead, OfflineRead, PlayerRead, RealmRead, SpiritualRootRead,
)

INITIAL_ROOT = {
    "key": "wood_common", "name": "Mộc Linh Căn", "elements": ["wood"],
    "quality": "common", "cultivation_modifier": 1.08, "breakthrough_modifier": 1.02,
}


class GameError(Exception):
    def __init__(self, code: str, status: int = 409):
        self.code = code
        self.status = status


class GameStateService:
    def __init__(self, session: AsyncSession, rng: RandomService | None = None) -> None:
        self.session = session
        self.players = PlayerRepository(session)
        self.realms = RealmRepository(session)
        self.logs = GameLogRepository(session)
        self.cultivation_engine = CultivationEngine()
        self.breakthrough_engine = BreakthroughEngine()
        self.rng = rng or RandomService()

    async def _load(self) -> Player:
        await self.players.lock_save()
        player = await self.players.get_first()
        if player is None:
            raise GameError("no_save", 404)
        return player

    async def get_state(self) -> GameStateRead:
        player = await self._load()
        await self._apply_progress(player)
        state = await self._state(player)
        await self.session.commit()
        return state

    async def new_game(self, name: str) -> GameStateRead:
        await self.players.lock_save()
        if await self.players.get_first() is not None:
            raise GameError("save_exists")
        await self._ensure_seed_data()
        realm = await self.realms.get_realm_by_key("qi_refining")
        root = await self.realms.get_root_by_key(INITIAL_ROOT["key"])
        if realm is None or root is None:
            raise RuntimeError("Seed data missing")
        player = await self.players.add(Player(
            name=name, realm=realm, spiritual_root=root, stage=1, cultivation_exp=0,
            spirit_stones=10, qi_gathering_pills=3, combat_power=12,
            manual_key="manual/qing_mu_jue", current_activity="cultivating",
            last_cultivation_at=datetime.now(timezone.utc),
        ))
        await self.logs.create("player", "Bạn tìm thấy động phủ bỏ hoang dưới chân Thanh Vân Sơn.")
        await self.logs.create("player", "Di vật còn lại gồm Thanh Mộc Quyết, 10 Linh Thạch và 3 Tụ Khí Đan.")
        state = await self._state(player)
        await self.session.commit()
        return state

    async def acknowledge_offline(self, report_id: int) -> None:
        await self._load()
        report = await self.logs.pending_offline()
        if report is not None and report.id == report_id:
            report.log_metadata = {**report.log_metadata, "pending": False}
        await self.session.commit()

    async def preview(self) -> BreakthroughRead:
        player = await self._load()
        await self._apply_progress(player)
        preview = await self._preview(player)
        await self.session.commit()
        return preview

    async def attempt(self, request: BreakthroughRequest) -> BreakthroughResult:
        player = await self._load()
        receipt = await self.logs.attempt_receipt(str(request.request_id))
        if receipt is not None:
            result = BreakthroughResult.model_validate(receipt.log_metadata["result"])
            await self.session.commit()
            return result
        if request.revision != player.last_cultivation_at:
            raise GameError("stale_preview")
        await self._apply_progress(player)
        preview = await self._preview(player)
        if preview.target is None:
            raise GameError("max_realm")
        if not preview.available:
            raise GameError("insufficient_cultivation")
        odds = self.breakthrough_engine.preview(
            major=player.stage == player.realm.max_stage,
            root_modifier=player.spiritual_root.breakthrough_modifier,
            required_exp=preview.required_exp,
        )
        success = self.breakthrough_engine.attempt(odds, self.rng)
        lost = 0.0
        if success:
            target_realm = await self.realms.get_realm_by_key(preview.target.key)
            if target_realm is None:
                raise GameError("realm_unavailable")
            player.realm = target_realm
            player.stage = preview.target.stage
            player.cultivation_exp -= preview.required_exp
            player.combat_power = round(player.combat_power * 1.15) + 2
            message = f"Đột phá thành công: {target_realm.name} tầng {player.stage}."
        else:
            lost = min(player.cultivation_exp, odds.failure_loss)
            player.cultivation_exp -= lost
            message = f"Đột phá thất bại. Tổn thất {lost:g} tu vi. Hãy tĩnh tâm tu luyện."
        result = BreakthroughResult(
            success=success, message=message, cultivation_lost=lost, realm=self._realm_read(player),
        )
        player.last_cultivation_at = max(datetime.now(timezone.utc), player.last_cultivation_at + timedelta(microseconds=1))
        log = await self.logs.create("breakthrough", message)
        log.log_metadata = {"request_id": str(request.request_id), "result": result.model_dump(mode="json")}
        await self.session.commit()
        return result

    async def _apply_progress(self, player: Player) -> None:
        now = datetime.now(timezone.utc)
        progress = self.cultivation_engine.apply_offline_progress(CultivationInput(
            cultivation_exp=player.cultivation_exp, last_cultivation_at=player.last_cultivation_at,
            current_time=now, base_rate_per_minute=self._base_rate_per_minute(player),
            root_modifier=player.spiritual_root.cultivation_modifier,
        ))
        player.cultivation_exp = progress.cultivation_exp
        # Preserve fractional seconds and never move a future timestamp backwards.
        player.last_cultivation_at += timedelta(seconds=progress.elapsed_seconds)
        if progress.elapsed_seconds >= 60 and progress.earned_exp > 0:
            report = await self.logs.pending_offline()
            previous = report.log_metadata if report else {}
            if report is None:
                report = await self.logs.create("cultivation", "Bế quan kết thúc.")
            report.log_metadata = {
                "pending": True,
                "elapsed_seconds": previous.get("elapsed_seconds", 0) + progress.elapsed_seconds,
                "earned_exp": previous.get("earned_exp", 0) + progress.earned_exp,
            }
            report.message = f"Bế quan kết thúc. Nhận {report.log_metadata['earned_exp']:.2f} tu vi."

    async def _preview(self, player: Player) -> BreakthroughRead:
        required = required_exp_for_stage(player.realm.base_required_exp, player.realm.growth_factor, player.stage)
        target = None
        if player.stage < player.realm.max_stage:
            target = self._realm_read(player).model_copy(update={"stage": player.stage + 1})
        else:
            definition = next((r for r in REALM_DEFINITIONS if r["rank_order"] == player.realm.rank_order + 1), None)
            if definition:
                realm = await self.realms.get_realm_by_key(definition["key"])
                if realm:
                    target = RealmRead(key=realm.key, name=realm.name, stage=1, max_stage=realm.max_stage)
        odds = self.breakthrough_engine.preview(
            major=player.stage == player.realm.max_stage,
            root_modifier=player.spiritual_root.breakthrough_modifier, required_exp=required,
        )
        return BreakthroughRead(
            available=target is not None and player.cultivation_exp >= required,
            target=target, required_exp=required, base_chance=odds.base,
            root_bonus=odds.root_bonus, final_chance=odds.total,
            failure_loss=odds.failure_loss, revision=player.last_cultivation_at,
        )

    async def _state(self, player: Player) -> GameStateRead:
        preview = await self._preview(player)
        base = self._base_rate_per_minute(player)
        rate = base * player.spiritual_root.cultivation_modifier
        report = await self.logs.pending_offline()
        return GameStateRead(
            player=PlayerRead.model_validate(player, from_attributes=True),
            realm=self._realm_read(player),
            spiritual_root=SpiritualRootRead.model_validate(player.spiritual_root, from_attributes=True),
            cultivation=CultivationRead(
                current_exp=player.cultivation_exp, required_exp=preview.required_exp,
                rate_per_minute=rate, base_rate_per_minute=base, root_bonus_per_minute=rate-base,
                seconds_until_next_stage=self.cultivation_engine.seconds_until_next_stage(player.cultivation_exp, preview.required_exp, rate),
                last_cultivation_at=player.last_cultivation_at,
            ),
            active_pet=None, dao_partner=None,
            recent_logs=[GameLogRead.model_validate(log, from_attributes=True) for log in await self.logs.recent()],
            server_time=datetime.now(timezone.utc), breakthrough=preview,
            offline_report=OfflineRead(id=report.id, **report.log_metadata) if report else None,
        )

    async def _ensure_seed_data(self) -> None:
        for definition in REALM_DEFINITIONS:
            if await self.realms.get_realm_by_key(definition["key"]) is None:
                await self.realms.add_realm(Realm(**definition))
        if await self.realms.get_root_by_key(INITIAL_ROOT["key"]) is None:
            await self.realms.add_root(SpiritualRoot(**INITIAL_ROOT))

    @staticmethod
    def _realm_read(player: Player) -> RealmRead:
        return RealmRead(key=player.realm.key, name=player.realm.name, stage=player.stage, max_stage=player.realm.max_stage)

    @staticmethod
    def _base_rate_per_minute(player: Player) -> float:
        return 1.2 * (1 + player.realm.rank_order * 0.15) * (1 + (player.stage - 1) * 0.04)
