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
