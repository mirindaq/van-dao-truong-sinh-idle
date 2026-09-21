from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.game_rules import GameRules, game_rules
from app.game.world import NpcSnapshot, WorldEngine
from app.models.world import WorldEvent, WorldNpc, WorldReport, WorldState
from app.schemas.world import WorldEventFilter, WorldEventPage, WorldEventRead, WorldNpcRead, WorldRead, WorldReportRead
from app.services.game_state_service import GameStateService


NPC_DEFINITIONS = (
    dict(key="xie_wuchen", name="Tạ Vô Trần", description="Kiếm tu trầm mặc, một lòng tìm kiếm đại đạo.",
         spiritual_root="Kim Linh Căn", portrait_key="npc/xie_wuchen"),
    dict(key="luo_qinghan", name="Lạc Thanh Hàn", description="Nữ tu hành tung khó đoán, thường lui tới Hàn Nguyệt Cốc.",
         spiritual_root="Băng Linh Căn", portrait_key="npc/luo_qinghan"),
    dict(key="wandering_cultivator", name="Tán Tu Vô Danh", description="Một tán tu bình thường đang tìm chỗ đứng dưới chân núi.",
         spiritual_root="Thổ Linh Căn", portrait_key=None),
)


class WorldService:
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
        self.engine = WorldEngine(rules)

    async def get_state(self, event_filter: WorldEventFilter = "all") -> WorldRead:
        player = await self.game._load()
        now = self.now or datetime.now(timezone.utc)
        world = await self._ensure_world(player.id, now)
        await self._simulate(world, now)
        result = await self._read(world, event_filter)
        await self.session.commit()
        return result

    async def get_events(self, event_filter: WorldEventFilter = "all", before_id: int | None = None) -> WorldEventPage:
        player = await self.game._load()
        world = await self.session.scalar(select(WorldState).where(WorldState.player_id == player.id))
        if world is None:
            return WorldEventPage(events=[], next_cursor=None)
        events, next_cursor = await self._event_page(world, event_filter, before_id)
        return WorldEventPage(events=events, next_cursor=next_cursor)

    async def acknowledge(self, report_id: int) -> None:
        player = await self.game._load()
        world = await self.session.scalar(select(WorldState).where(WorldState.player_id == player.id))
        if world is not None:
            report = await self.session.scalar(select(WorldReport).where(
                WorldReport.id == report_id, WorldReport.world_id == world.id, WorldReport.pending.is_(True)))
            if report is not None:
                report.pending = False
        await self.session.commit()

    async def _ensure_world(self, player_id: int, now: datetime) -> WorldState:
        world = await self.session.scalar(select(WorldState).where(WorldState.player_id == player_id))
        if world is not None:
            return world
        world = WorldState(player_id=player_id, seed=self.rules.world_seed_base + player_id,
                           rules_version=self.rules.rules_version, rules_fingerprint=self.rules.fingerprint,
                           total_ticks=0, started_at=now, last_simulated_at=now)
        self.session.add(world)
        await self.session.flush()
        for definition in NPC_DEFINITIONS:
            npc_rules = self.rules.npc_rules[definition["key"]]
            self.session.add(WorldNpc(
                world_id=world.id,
                activity="cultivating",
                location="Thanh Vân Sơn",
                stage=npc_rules.stage,
                cultivation_exp=npc_rules.cultivation_exp,
                cultivation_rate=npc_rules.cultivation_rate,
                **definition,
            ))
        await self.session.flush()
        return world

    async def _simulate(self, world: WorldState, now: datetime) -> None:
        world.rules_version = self.rules.rules_version
        world.rules_fingerprint = self.rules.fingerprint
        elapsed = max(0, int((now - world.last_simulated_at).total_seconds()))
        full_ticks = elapsed // (self.engine.tick_minutes * 60)
        if full_ticks == 0:
            return
        processed = min(full_ticks, self.engine.max_ticks)
        skipped_seconds = max(0, full_ticks - processed) * self.engine.tick_minutes * 60
        npcs = list((await self.session.scalars(select(WorldNpc).where(WorldNpc.world_id == world.id).order_by(WorldNpc.id))).all())
        changed: set[str] = set()
        created: list[WorldEvent] = []
        counts: Counter[str] = Counter()
        base_tick = world.total_ticks
        for offset in range(processed):
            tick_index = base_tick + offset + 1
            tick_time = world.last_simulated_at + timedelta(minutes=self.engine.tick_minutes * (offset + 1))
            for npc in npcs:
                before = self._snapshot(npc)
                result = self.engine.advance_npc(before, tick_index, tick_time, world.seed)
                if result.npc != before:
                    changed.add(npc.key)
                    self._apply_snapshot(npc, result.npc, tick_time)
                for sequence, event in enumerate(result.events):
                    row = WorldEvent(world_id=world.id, tick_index=tick_index, sequence=sequence,
                                     occurred_at=tick_time, **event)
                    self.session.add(row); created.append(row); counts[event["kind"]] += 1
            event = self.engine.world_event(tick_index, world.seed)
            if event is not None:
                row = WorldEvent(world_id=world.id, tick_index=tick_index, sequence=0,
                                 occurred_at=tick_time, **event)
                self.session.add(row); created.append(row); counts[event["kind"]] += 1
        previous_time = world.last_simulated_at
        world.total_ticks += full_ticks
        world.last_simulated_at += timedelta(minutes=self.engine.tick_minutes * full_ticks)
        if changed or created or skipped_seconds:
            report = await self.session.scalar(select(WorldReport).where(
                WorldReport.world_id == world.id,
                WorldReport.pending.is_(True),
                WorldReport.rules_version == self.rules.rules_version,
                WorldReport.rules_fingerprint == self.rules.fingerprint,
            ).order_by(desc(WorldReport.id)).limit(1))
            if report is None:
                report = WorldReport(world_id=world.id, started_at=previous_time, ended_at=world.last_simulated_at,
                                     processed_ticks=0, skipped_seconds=0, event_count=0, npc_updates=0,
                                     rules_version=self.rules.rules_version,
                                     rules_fingerprint=self.rules.fingerprint,
                                     npc_keys=[], summary={}, pending=True)
                self.session.add(report)
            old_summary = Counter(report.summary or {})
            npc_keys = set(report.npc_keys or ()) | changed
            report.ended_at = world.last_simulated_at
            report.processed_ticks += processed
            report.skipped_seconds += skipped_seconds
            report.event_count += len(created)
            report.npc_keys = sorted(npc_keys)
            report.npc_updates = len(npc_keys)
            report.summary = dict(old_summary + counts)
        await self.session.flush()

    async def _event_page(self, world: WorldState, event_filter: WorldEventFilter, before_id: int | None = None) -> tuple[list[WorldEventRead], int | None]:
        event_query = select(WorldEvent).where(WorldEvent.world_id == world.id)
        if before_id is not None:
            event_query = event_query.where(WorldEvent.id < before_id)
        if event_filter == "world":
            event_query = event_query.where(WorldEvent.source_key == "world")
        elif event_filter == "npc":
            event_query = event_query.where(WorldEvent.source_key != "world")
        page_size = 20
        rows = list((await self.session.scalars(event_query.order_by(desc(WorldEvent.id)).limit(page_size + 1))).all())
        events = rows[:page_size]
        return [WorldEventRead.model_validate(event, from_attributes=True) for event in events], events[-1].id if len(rows) > page_size else None

    async def _read(self, world: WorldState, event_filter: WorldEventFilter) -> WorldRead:
        npcs = list((await self.session.scalars(select(WorldNpc).where(WorldNpc.world_id == world.id).order_by(WorldNpc.id))).all())
        events, next_cursor = await self._event_page(world, event_filter)
        report = await self.session.scalar(select(WorldReport).where(
            WorldReport.world_id == world.id, WorldReport.pending.is_(True)).order_by(desc(WorldReport.id)).limit(1))
        return WorldRead(
            updated_at=world.last_simulated_at, tick_minutes=self.engine.tick_minutes,
            max_offline_hours=self.rules.world_max_offline_hours,
            rules_version=world.rules_version, rules_fingerprint=world.rules_fingerprint,
            npcs=[WorldNpcRead(
                key=n.key, name=n.name, description=n.description, spiritual_root=n.spiritual_root,
                realm_key=n.realm_key, realm_name=self.engine.realm_name(n.realm_key), stage=n.stage,
                cultivation_exp=n.cultivation_exp, required_exp=self.engine.required_exp(n.stage, n.realm_key),
                activity=n.activity, location=n.location, portrait_key=n.portrait_key,
                injured_until=n.injured_until, updated_at=n.updated_at,
            ) for n in npcs],
            events=events, next_cursor=next_cursor,
            report=WorldReportRead.model_validate(report, from_attributes=True) if report else None,
        )

    @staticmethod
    def _snapshot(npc: WorldNpc) -> NpcSnapshot:
        return NpcSnapshot(key=npc.key, name=npc.name, realm_key=npc.realm_key, stage=npc.stage,
                           cultivation_exp=npc.cultivation_exp, cultivation_rate=npc.cultivation_rate,
                           activity=npc.activity, location=npc.location, injured_until=npc.injured_until)

    @staticmethod
    def _apply_snapshot(npc: WorldNpc, snapshot: NpcSnapshot, tick_time: datetime) -> None:
        npc.stage = snapshot.stage
        npc.realm_key = snapshot.realm_key
        npc.cultivation_exp = snapshot.cultivation_exp
        npc.activity = snapshot.activity
        npc.location = snapshot.location
        npc.injured_until = snapshot.injured_until
        npc.updated_at = tick_time
