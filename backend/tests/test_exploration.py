import asyncio
from uuid import uuid4
from unittest.mock import Mock
import pytest
from sqlalchemy import select, func
from tests.test_game_api import game  # noqa: F401
from app.models.exploration import ExplorationRun
from app.models.game_log import GameLog
from app.models.item import OwnedItem
from app.game.random_service import RandomService
from app.game.data.items import PILL_KEY
from app.repositories.player_repository import PlayerRepository
from app.services.exploration_service import ExplorationService
from app.schemas.exploration import ExplorationRequest
from app.core.game_rules import game_rules


async def new_game(client):
    await client.post('/game/new', json={'name': 'Thám Vân'})


async def test_victory_reward_atomic_and_replay(game):
    client, sessions = game
    await new_game(client)
    await client.post('/equipment/claim')
    await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': 'items/bamboo_sword'})
    request_id = str(uuid4())
    async with sessions() as session:
        rng = Mock(); rng.roll = Mock(side_effect=[.9, .1]); rng.randint = Mock(return_value=0)
        response = await ExplorationService(session, rng).run(ExplorationRequest(request_id=request_id))
    assert response.exploration.state == 'victory'
    assert response.exploration.reward_stones == 10
    assert response.exploration.reward_pills == 1
    replay = await client.post('/exploration/run', json={'request_id': request_id})
    assert replay.json()['exploration'] == response.exploration.model_dump(mode='json')
    state = (await client.get('/game/state')).json()
    assert state['player']['spirit_stones'] == 20
    assert next(i['quantity'] for i in state['inventory'] if i['key'] == PILL_KEY) == 4
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(ExplorationRun)) == 1
        run = await session.scalar(select(ExplorationRun))
        assert run.combat_snapshot["enemy"]["name"] == "Dã Lang"
        assert run.combat_snapshot["player"]["attack"] == 13
        assert await session.scalar(select(func.count()).select_from(GameLog).where(GameLog.scope == "exploration")) == 1


async def test_empty_run_has_no_battle_or_reward(game):
    client, _ = game
    await new_game(client)
    response = await client.post('/exploration/run', json={'request_id': str(uuid4())})
    assert response.json()['exploration']['state'] in ('empty', 'victory', 'defeat')
    if response.json()['exploration']['state'] == 'empty':
        assert response.json()['exploration']['battle_log'] == []
        assert response.json()['exploration']['reward_stones'] == 0


async def test_defeat_has_log_without_reward(game):
    client, sessions = game
    await new_game(client)
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.combat_power = -20
        await session.commit()
        rng = Mock(); rng.roll = Mock(side_effect=[.9, .99]); rng.randint = Mock(return_value=0)
        response = await ExplorationService(session, rng).run(ExplorationRequest(request_id=str(uuid4())))
    assert response.exploration.state == 'defeat'
    assert response.exploration.reward_stones == 0 and response.exploration.battle_log


async def test_duplicate_and_concurrent_request_one_reward(game):
    client, _ = game
    await new_game(client)
    request_id = str(uuid4())
    responses = await asyncio.gather(*[client.post('/exploration/run', json={'request_id': request_id}) for _ in range(2)])
    assert all(r.status_code == 200 for r in responses)
    assert responses[0].json()['exploration']['id'] == responses[1].json()['exploration']['id']
    assert (await client.get('/game/state')).json()['player']['spirit_stones'] in (10, 20)


async def test_invalid_location_and_missing_run(game):
    client, _ = game
    await new_game(client)
    assert (await client.post('/exploration/run', json={'request_id': str(uuid4()), 'location_key': 'unknown'})).json()['detail'] == 'location_unavailable'
    assert (await client.get(f'/exploration/run/{uuid4()}')).status_code == 404


async def test_exploration_override_is_saved_and_replayed_after_rules_change(game):
    client, sessions = game
    await new_game(client)
    request_id = uuid4()
    rules = game_rules.model_copy(update={
        "rules_version": game_rules.rules_version + 1,
        "exploration_empty_chance": 0,
        "exploration_reward_stones": 37,
        "exploration_reward_pills": 2,
    })
    async with sessions() as session:
        rng = Mock(); rng.roll = Mock(return_value=.9); rng.randint = Mock(return_value=0)
        receipt = await ExplorationService(session, rng, rules).run(ExplorationRequest(request_id=request_id))
    assert receipt.exploration.reward_stones == 37
    assert receipt.exploration.reward_pills == 2
    assert receipt.exploration.rules_version == rules.rules_version
    replay = (await client.get(f"/exploration/run/{request_id}")).json()["exploration"]
    assert replay["reward_stones"] == 37
    assert replay["rules_fingerprint"] == rules.fingerprint


async def test_journeys_wait_for_server_time_then_grant_one_reward(game):
    from datetime import datetime, timedelta, timezone
    from app.game.data.items import HERB_KEY
    from app.game.data.journeys import COMMON_WEAPON, LINH_MACH_WEAPON
    client, sessions = game
    await new_game(client)
    start = datetime(2026, 9, 22, tzinfo=timezone.utc)
    cases = (
        ("hau_son", 5, HERB_KEY),
        ("ngoai_vi", 10, COMMON_WEAPON),
        ("linh_mach", 15, LINH_MACH_WEAPON),
    )
    for location, minutes, item_key in cases:
        request_id = uuid4()
        async with sessions() as session:
            started = await ExplorationService(session, now=lambda: start).run(
                ExplorationRequest(request_id=request_id, location_key=location))
        assert started.exploration.state == "traveling"
        assert started.exploration.reward_item_quantity == 0
        instant = await client.post("/exploration/run", json={"request_id": str(uuid4())})
        assert instant.status_code == 200
        assert instant.json()["exploration"]["state"] in ("empty", "victory", "defeat")
        async with sessions() as session:
            early = await ExplorationService(session, now=lambda: start + timedelta(minutes=minutes - 1)).get(request_id)
        assert early.exploration.state == "traveling"
        rng = Mock(); rng.roll = Mock(side_effect=[.9, .1]); rng.randint = Mock(return_value=0)
        async with sessions() as session:
            service = ExplorationService(session, rng, now=lambda: start + timedelta(minutes=minutes))
            done = await service.get(request_id)
            again = await service.get(request_id)
        assert done.exploration.state == "victory"
        assert done.exploration.reward_item_key == item_key
        assert done.exploration.reward_item_quantity == 1
        assert again.exploration.reward_item_quantity == 1
        state = (await client.get("/game/state")).json()
        assert next(item["quantity"] for item in state["inventory"] if item["key"] == item_key) == 1


async def test_journey_request_conflict_and_second_journey_rejected(game):
    from datetime import datetime, timezone
    client, sessions = game
    await new_game(client)
    start = datetime(2026, 9, 22, tzinfo=timezone.utc)
    request_id = uuid4()
    async with sessions() as session:
        await ExplorationService(session, now=lambda: start).run(
            ExplorationRequest(request_id=request_id, location_key="hau_son"))
        with pytest.raises(Exception) as error:
            await ExplorationService(session, now=lambda: start).run(
                ExplorationRequest(request_id=request_id, location_key="linh_mach"))
        assert error.value.code == "request_conflict"
        with pytest.raises(Exception) as blocked:
            await ExplorationService(session, now=lambda: start).run(
                ExplorationRequest(request_id=uuid4(), location_key="ngoai_vi"))
        assert blocked.value.code == "journey_in_progress"


async def test_failed_resolve_keeps_the_journey_and_grants_nothing(game, monkeypatch):
    from datetime import datetime, timedelta, timezone
    from app.game.battle import BattleEngine
    from app.game.data.items import HERB_KEY
    client, sessions = game
    await new_game(client)
    start = datetime(2026, 9, 22, tzinfo=timezone.utc)
    request_id = uuid4()
    async with sessions() as session:
        await ExplorationService(session, now=lambda: start).run(
            ExplorationRequest(request_id=request_id, location_key="hau_son"))
    monkeypatch.setattr(BattleEngine, "resolve", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    rng = Mock(); rng.roll = Mock(return_value=.9); rng.randint = Mock(return_value=0)
    async with sessions() as session:
        with pytest.raises(RuntimeError):
            await ExplorationService(session, rng, now=lambda: start + timedelta(minutes=5)).get(request_id)
    async with sessions() as session:
        kept = await ExplorationService(session, now=lambda: start).get(request_id)
    assert kept.exploration.state == "traveling"
    state = (await client.get("/game/state")).json()
    assert all(item["key"] != HERB_KEY for item in state["inventory"])


async def test_defeat_and_changed_catalog_do_not_rewrite_the_receipt(game):
    from datetime import datetime, timedelta, timezone
    client, sessions = game
    await new_game(client)
    start = datetime(2026, 9, 22, tzinfo=timezone.utc)
    request_id = uuid4()
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.combat_power = -20
        await session.commit()
        await ExplorationService(session, now=lambda: start).run(
            ExplorationRequest(request_id=request_id, location_key="linh_mach"))
        rng = Mock(); rng.roll = Mock(side_effect=[.9, .99]); rng.randint = Mock(return_value=0)
        defeated = await ExplorationService(session, rng, now=lambda: start + timedelta(minutes=15)).get(request_id)
    assert defeated.exploration.state == "defeat"
    assert defeated.exploration.reward_item_quantity == 0
    rules = game_rules.model_copy(update={"journey_material_quantity": 9, "rules_version": game_rules.rules_version + 1})
    async with sessions() as session:
        reread = await ExplorationService(session, rules=rules, now=lambda: start + timedelta(minutes=30)).get(request_id)
    assert reread.exploration.reward_item_quantity == 0
    assert reread.exploration.state == "defeat"
