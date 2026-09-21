import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app.core.game_rules import game_rules
from app.models.world import WorldEvent, WorldNpc, WorldReport, WorldState
from app.services.world_service import WorldService
from tests.test_game_api import game  # noqa: F401


async def test_world_initializes_once_without_past_events(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    first = (await client.get("/world/state")).json()
    second = (await client.get("/world/state")).json()
    assert [npc["name"] for npc in first["npcs"]] == ["Tạ Vô Trần", "Lạc Thanh Hàn", "Tán Tu Vô Danh"]
    assert first["events"] == [] and first["report"] is None
    assert first["rules_version"] == game_rules.rules_version
    assert first["rules_fingerprint"] == game_rules.fingerprint
    assert second["updated_at"] == first["updated_at"]
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(WorldState)) == 1
        assert await session.scalar(select(func.count()).select_from(WorldNpc)) == 3


async def test_world_rule_change_only_affects_future_ticks_and_keeps_old_report(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    start = datetime(2026, 9, 21, tzinfo=timezone.utc)
    async with sessions() as session:
        initial = await WorldService(session, now=start).get_state()
        world = await session.scalar(select(WorldState))
        original_rates = {
            npc.key: npc.cultivation_rate
            for npc in (await session.scalars(select(WorldNpc))).all()
        }
        assert initial.report is None
        first = await WorldService(session, now=start + timedelta(minutes=10)).get_state()
        first_report_id = first.report.id
        first_report_fingerprint = first.report.rules_fingerprint

    boosted_npcs = dict(game_rules.npc_rules)
    boosted_npcs["xie_wuchen"] = boosted_npcs["xie_wuchen"].model_copy(
        update={"cultivation_rate": 999}
    )
    new_rules = game_rules.model_copy(update={
        "rules_version": game_rules.rules_version + 1,
        "world_cultivate_continue_chance": 1,
        "npc_rules": boosted_npcs,
    })
    async with sessions() as session:
        current = await WorldService(
            session,
            now=start + timedelta(minutes=20),
            rules=new_rules,
        ).get_state()
        old_report = await session.get(WorldReport, first_report_id)
        current_rates = {
            npc.key: npc.cultivation_rate
            for npc in (await session.scalars(select(WorldNpc))).all()
        }
        world = await session.scalar(select(WorldState))

    assert current.rules_version == new_rules.rules_version
    assert current.rules_fingerprint == new_rules.fingerprint
    assert current.report.rules_version == new_rules.rules_version
    assert current.report.rules_fingerprint == new_rules.fingerprint
    assert old_report.rules_fingerprint == first_report_fingerprint
    assert old_report.processed_ticks == 1
    assert current_rates == original_rates
    assert world.total_ticks == 2


async def test_world_advances_once_concurrently_and_report_ack_is_idempotent(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = datetime.now(timezone.utc) - timedelta(minutes=20)
        await session.commit()
    responses = await asyncio.gather(client.get("/world/state"), client.get("/world/state"))
    states = [response.json() for response in responses]
    assert all(response.status_code == 200 for response in responses)
    assert states[0]["updated_at"] == states[1]["updated_at"]
    report = states[0]["report"] or states[1]["report"]
    assert report["processed_ticks"] == 2 and report["npc_updates"] == 3
    for _ in range(2):
        assert (await client.post(f'/world/report/{report["id"]}/ack')).status_code == 204
    assert (await client.get("/world/state")).json()["report"] is None
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        assert world.total_ticks == 2
        assert await session.scalar(select(func.count()).select_from(WorldReport)) == 1


async def test_world_cap_filter_and_player_resources_are_unchanged(game):
    client, sessions = game
    initial = (await client.post("/game/new", json={"name": "Quan Sơn"})).json()
    await client.get("/world/state")
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = datetime.now(timezone.utc) - timedelta(hours=25, minutes=5)
        await session.commit()
    result = (await client.get("/world/state?filter=world")).json()
    assert result["report"]["processed_ticks"] == 144
    assert result["report"]["skipped_seconds"] >= 3600
    assert all(event["source_key"] == "world" for event in result["events"])
    first_page = (await client.get("/world/state")).json()
    assert first_page["next_cursor"] is not None
    second_page = (await client.get(f'/world/events?before_id={first_page["next_cursor"]}')).json()
    assert {event["id"] for event in first_page["events"]}.isdisjoint(event["id"] for event in second_page["events"])
    current = (await client.get("/game/state")).json()
    assert current["player"]["spirit_stones"] == initial["player"]["spirit_stones"]
    assert current["inventory"] == initial["inventory"]


async def test_world_state_survives_new_session_and_events_are_stable(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = datetime.now(timezone.utc) - timedelta(hours=3)
        await session.commit()
    first = (await client.get("/world/state")).json()
    second = (await client.get("/world/state")).json()
    assert second["events"] == first["events"]
    assert second["npcs"] == first["npcs"]
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(WorldEvent)) == len(first["events"])


async def test_world_rolls_back_failed_tick_and_retry_replays(monkeypatch, game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    now = datetime.now(timezone.utc)
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = now - timedelta(minutes=10)
        await session.commit()
        baseline = {npc.key: npc.cultivation_exp for npc in (await session.scalars(select(WorldNpc))).all()}
        service = WorldService(session, now=now)
        monkeypatch.setattr(service.engine, "world_event", lambda *args: (_ for _ in ()).throw(RuntimeError("rng failed")))
        with pytest.raises(RuntimeError, match="rng failed"):
            await service.get_state()
        await session.rollback()
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        assert world.total_ticks == 0
        assert await session.scalar(select(func.count()).select_from(WorldReport)) == 0
        assert {npc.key: npc.cultivation_exp for npc in (await session.scalars(select(WorldNpc))).all()} == baseline
        retried = await WorldService(session, now=now).get_state()
        assert retried.report.processed_ticks == 1


async def test_world_service_split_sync_matches_single_sync(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    start = datetime(2026, 9, 18, tzinfo=timezone.utc)
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = start
        world.started_at = start
        npcs = list((await session.scalars(select(WorldNpc).order_by(WorldNpc.id))).all())
        baseline = [(npc.id, npc.realm_key, npc.stage, npc.cultivation_exp, npc.activity, npc.location, npc.injured_until, npc.updated_at) for npc in npcs]
        await session.commit()
    for minutes in (10, 20, 30, 40):
        async with sessions() as session:
            await WorldService(session, now=start + timedelta(minutes=minutes)).get_state()
    async with sessions() as session:
        split_npcs = [(npc.realm_key, npc.stage, npc.cultivation_exp, npc.activity, npc.location, npc.injured_until) for npc in (await session.scalars(select(WorldNpc).order_by(WorldNpc.id))).all()]
        split_events = [(event.tick_index, event.source_key, event.kind, event.message) for event in (await session.scalars(select(WorldEvent).order_by(WorldEvent.id))).all()]
        await session.execute(WorldEvent.__table__.delete())
        await session.execute(WorldReport.__table__.delete())
        world = await session.scalar(select(WorldState))
        world.total_ticks = 0; world.last_simulated_at = start
        for saved, npc in zip(baseline, (await session.scalars(select(WorldNpc).order_by(WorldNpc.id))).all(), strict=True):
            _, npc.realm_key, npc.stage, npc.cultivation_exp, npc.activity, npc.location, npc.injured_until, npc.updated_at = saved
        await session.commit()
    async with sessions() as session:
        await WorldService(session, now=start + timedelta(minutes=40)).get_state()
        single_npcs = [(npc.realm_key, npc.stage, npc.cultivation_exp, npc.activity, npc.location, npc.injured_until) for npc in (await session.scalars(select(WorldNpc).order_by(WorldNpc.id))).all()]
        single_events = [(event.tick_index, event.source_key, event.kind, event.message) for event in (await session.scalars(select(WorldEvent).order_by(WorldEvent.id))).all()]
    assert split_npcs == single_npcs
    assert split_events == single_events


async def test_world_does_not_create_empty_report_when_all_npcs_are_still_injured(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    now = datetime.now(timezone.utc)
    async with sessions() as session:
        world = await session.scalar(select(WorldState)); world.last_simulated_at = now - timedelta(minutes=10)
        for npc in (await session.scalars(select(WorldNpc))).all():
            npc.activity = "injured"; npc.injured_until = now + timedelta(hours=1)
        await session.commit()
    assert (await client.get("/world/state")).json()["report"] is None


async def test_world_tick_boundaries_and_backward_clock(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    now = datetime.now(timezone.utc)
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = now + timedelta(minutes=1)
        await session.commit()
        assert (await WorldService(session, now=now).get_state()).report is None
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = now - timedelta(minutes=9, seconds=59)
        await session.commit()
        assert (await WorldService(session, now=now).get_state()).report is None
    async with sessions() as session:
        world = await session.scalar(select(WorldState))
        world.last_simulated_at = now - timedelta(minutes=10)
        await session.commit()
        assert (await WorldService(session, now=now).get_state()).report.processed_ticks == 1
