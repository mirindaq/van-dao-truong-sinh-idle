from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.game.cultivation import CultivationEngine, CultivationInput
from app.game.data.realms import REALM_DEFINITIONS, required_exp_for_stage
from app.models.player import Player
from app.models.realm import Realm
from app.models.spiritual_root import SpiritualRoot
from app.repositories.game_log_repository import GameLogRepository
from app.repositories.player_repository import PlayerRepository
from app.repositories.realm_repository import RealmRepository
from app.schemas.game_state import (
    CultivationRead,
    GameLogRead,
    GameStateRead,
    PlayerRead,
    RealmRead,
    SpiritualRootRead,
)

INITIAL_ROOT = {
    "key": "wood_common",
    "name": "Mộc Linh Căn",
    "elements": ["wood"],
    "quality": "common",
    "cultivation_modifier": 1.08,
    "breakthrough_modifier": 1.02,
}


class GameStateService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.players = PlayerRepository(session)
        self.realms = RealmRepository(session)
        self.logs = GameLogRepository(session)
        self.cultivation_engine = CultivationEngine()

    async def get_state(self) -> GameStateRead:
        await self._ensure_seed_data()
        player = await self.players.get_first()
        if player is None:
            player = await self._create_initial_player()

        now = datetime.now(timezone.utc)
        required_exp = required_exp_for_stage(
            player.realm.base_required_exp,
            player.realm.growth_factor,
            player.stage,
        )
        progress = self.cultivation_engine.apply_offline_progress(
            CultivationInput(
                cultivation_exp=player.cultivation_exp,
                last_cultivation_at=player.last_cultivation_at,
                current_time=now,
                base_rate_per_minute=self._base_rate_per_minute(player),
                root_modifier=player.spiritual_root.cultivation_modifier,
            )
        )

        player.cultivation_exp = progress.cultivation_exp
        player.last_cultivation_at = now
        await self.session.commit()

        recent_logs = await self.logs.recent()

        return GameStateRead(
            player=PlayerRead(
                id=player.id,
                name=player.name,
                spirit_stones=player.spirit_stones,
                qi_gathering_pills=player.qi_gathering_pills,
                combat_power=player.combat_power,
                manual_key=player.manual_key,
                current_activity=player.current_activity,
            ),
            realm=RealmRead(
                key=player.realm.key,
                name=player.realm.name,
                stage=player.stage,
                max_stage=player.realm.max_stage,
            ),
            spiritual_root=SpiritualRootRead(
                key=player.spiritual_root.key,
                name=player.spiritual_root.name,
                elements=player.spiritual_root.elements,
                quality=player.spiritual_root.quality,
                cultivation_modifier=player.spiritual_root.cultivation_modifier,
                breakthrough_modifier=player.spiritual_root.breakthrough_modifier,
            ),
            cultivation=CultivationRead(
                current_exp=player.cultivation_exp,
                required_exp=required_exp,
                rate_per_minute=progress.rate_per_minute,
                seconds_until_next_stage=self.cultivation_engine.seconds_until_next_stage(
                    player.cultivation_exp,
                    required_exp,
                    progress.rate_per_minute,
                ),
                last_cultivation_at=player.last_cultivation_at,
            ),
            active_pet=None,
            dao_partner=None,
            recent_logs=[
                GameLogRead(
                    id=log.id,
                    scope=log.scope,
                    message=log.message,
                    created_at=log.created_at,
                )
                for log in recent_logs
            ],
        )

    async def _ensure_seed_data(self) -> None:
        for definition in REALM_DEFINITIONS:
            existing = await self.realms.get_realm_by_key(definition["key"])
            if existing is None:
                await self.realms.add_realm(Realm(**definition))

        existing_root = await self.realms.get_root_by_key(INITIAL_ROOT["key"])
        if existing_root is None:
            await self.realms.add_root(SpiritualRoot(**INITIAL_ROOT))

        await self.session.commit()

    async def _create_initial_player(self) -> Player:
        realm = await self.realms.get_realm_by_key("qi_refining")
        root = await self.realms.get_root_by_key(INITIAL_ROOT["key"])
        if realm is None or root is None:
            raise RuntimeError("Seed data is missing after initialization")

        now = datetime.now(timezone.utc)
        player = await self.players.add(
            Player(
                name="Vô Danh",
                realm=realm,
                spiritual_root=root,
                stage=1,
                cultivation_exp=0,
                spirit_stones=10,
                qi_gathering_pills=3,
                combat_power=12,
                manual_key="manual/qing_mu_jue",
                current_activity="cultivating",
                last_cultivation_at=now,
            )
        )
        await self.logs.create(
            "player",
            "Bạn tìm thấy động phủ bỏ hoang dưới chân Thanh Vân Sơn.",
        )
        await self.logs.create(
            "player",
            "Di vật còn lại gồm Thanh Mộc Quyết, 10 Linh Thạch và 3 Tụ Khí Đan.",
        )
        await self.session.commit()
        return player

    def _base_rate_per_minute(self, player: Player) -> float:
        realm_bonus = 1 + (player.realm.rank_order * 0.15)
        stage_bonus = 1 + ((player.stage - 1) * 0.04)
        return 1.2 * realm_bonus * stage_bonus
