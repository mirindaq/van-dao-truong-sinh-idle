import pytest
import asyncio
from uuid import uuid4
from unittest.mock import Mock
from sqlalchemy.exc import IntegrityError

from tests.test_game_api import game  # noqa: F401
from app.game.data.items import MANUAL_KEY, PILL_KEY
from app.models.item import OwnedItem
from app.services.game_state_service import GameStateService
from app.schemas.game_state import BreakthroughRequest
from app.repositories.player_repository import PlayerRepository
from app.models.game_log import GameLog
from app.models.realm import Realm
from app.game.data.realms import REALM_DEFINITIONS
from app.services.game_state_service import GameError
from sqlalchemy import select, func


async def prepare(client, sessions, quantity=3):
    created = (await client.post('/game/new', json={'name': 'Thanh Vân'})).json()
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.cultivation_exp = 2000
        pill = await session.get(OwnedItem, (player.id, PILL_KEY))
        pill.quantity = quantity
        await session.commit()
    return created['player']['id']


async def pill_request(client):
    preview = (await client.get('/breakthrough/preview', params={'item_key': PILL_KEY, 'quantity': 1})).json()
    return dict(request_id=str(uuid4()), revision=preview['revision'], item_key=PILL_KEY, quantity=1)


async def test_inventory_initial_grant_and_reopen(game):
    client, sessions = game
    assert (await client.get('/game/state')).status_code == 404
    created = (await client.post('/game/new', json={'name': 'Thanh Vân'})).json()
    assert {i['key']: i['quantity'] for i in created['inventory']} == {PILL_KEY: 3, MANUAL_KEY: 1}
    assert (await client.post('/game/new', json={'name': 'Khác'})).status_code == 409
    async with sessions() as session:
        pill = await session.get(OwnedItem, (created['player']['id'], PILL_KEY))
        pill.quantity = 0
        await session.commit()
    for _ in range(2):
        async with sessions() as session:
            state = await GameStateService(session).get_state()
            assert state.player.qi_gathering_pills == 0
            assert {i.key: i.quantity for i in state.inventory} == {PILL_KEY: 0, MANUAL_KEY: 1}


async def test_inventory_database_rejects_negative_quantity(game):
    client, sessions = game
    created = (await client.post('/game/new', json={'name': 'Thanh Vân'})).json()
    async with sessions() as session:
        pill = await session.get(OwnedItem, (created['player']['id'], PILL_KEY))
        pill.quantity = -1
        with pytest.raises(IntegrityError):
            await session.commit()


@pytest.mark.parametrize('roll,success', [(0.1, True), (0.99, False)])
async def test_pill_result_replay_conflict_and_quantity(game, roll, success):
    client, sessions = game
    await prepare(client, sessions)
    payload = await pill_request(client)
    rng = Mock()
    rng.roll.return_value = roll
    async with sessions() as session:
        result = await GameStateService(session, rng).attempt(BreakthroughRequest(**payload))
    assert result.success is success
    assert result.items_consumed == 1
    assert result.final_chance == 0.95
    assert result.cultivation_lost == (0 if success else 12)
    replay = await client.post('/breakthrough/attempt', json=payload)
    assert replay.json() == result.model_dump(mode='json')
    conflict = await client.post('/breakthrough/attempt', json={**payload, 'item_key': None, 'quantity': 0})
    assert conflict.json()['detail'] == 'request_conflict'
    state = (await client.get('/game/state')).json()
    assert state['player']['qi_gathering_pills'] == 2
    assert len([log for log in state['recent_logs'] if log['scope'] == 'breakthrough']) == 1
    async with sessions() as session:
        receipt = await session.scalar(select(GameLog).where(GameLog.scope == 'breakthrough'))
        assert receipt.log_metadata['player_id'] == state['player']['id']
        assert receipt.log_metadata['source']['stage'] == 1
        assert receipt.log_metadata['target']['stage'] == 2
        assert receipt.log_metadata['result']['created_at']
    rng.roll.assert_called_once()


async def test_competing_requests_last_pill(game):
    client, sessions = game
    await prepare(client, sessions, 1)
    payload = await pill_request(client)
    responses = await asyncio.gather(*[
        client.post('/breakthrough/attempt', json={**payload, 'request_id': str(uuid4())}) for _ in range(2)
    ])
    assert sorted(r.status_code for r in responses) == [200, 409]
    assert (await client.get('/game/state')).json()['player']['qi_gathering_pills'] == 0


async def test_duplicate_concurrent_requests(game):
    client, sessions = game
    await prepare(client, sessions)
    payload = await pill_request(client)
    responses = await asyncio.gather(*[client.post('/breakthrough/attempt', json=payload) for _ in range(2)])
    assert all(r.status_code == 200 for r in responses)
    assert responses[0].json() == responses[1].json()
    assert (await client.get('/game/state')).json()['player']['qi_gathering_pills'] == 2


async def test_invalid_selection_and_stale_inventory(game):
    client, sessions = game
    player_id = await prepare(client, sessions)
    payload = await pill_request(client)
    for item, quantity in [(MANUAL_KEY, 1), (PILL_KEY, 2), (None, 1), (PILL_KEY, 0), (PILL_KEY, True)]:
        response = await client.post('/breakthrough/attempt', json={**payload, 'item_key': item, 'quantity': quantity})
        assert response.status_code == 422
    changed_selection = await client.post('/breakthrough/attempt', json={**payload, 'item_key': None, 'quantity': 0})
    assert changed_selection.json()['detail'] == 'stale_preview'
    async with sessions() as session:
        pill = await session.get(OwnedItem, (player_id, PILL_KEY))
        pill.quantity = 0
        await session.commit()
    assert (await client.post('/breakthrough/attempt', json=payload)).json()['detail'] == 'stale_preview'
    empty_payload = await pill_request(client)
    assert (await client.post('/breakthrough/attempt', json=empty_payload)).json()['detail'] == 'insufficient_items'
    assert (await client.get('/game/state')).json()['player']['qi_gathering_pills'] == 0


async def test_failed_commit_rolls_back_pill_and_result(game, monkeypatch):
    client, sessions = game
    await prepare(client, sessions)
    payload = await pill_request(client)
    async with sessions() as session:
        async def fail_commit():
            await session.flush()
            raise RuntimeError('simulated storage failure')
        monkeypatch.setattr(session, 'commit', fail_commit)
        with pytest.raises(RuntimeError, match='storage failure'):
            await GameStateService(session).attempt(BreakthroughRequest(**payload))
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        assert player.stage == 1
        assert (await session.get(OwnedItem, (player.id, PILL_KEY))).quantity == 3
        assert (await session.scalar(select(func.count()).select_from(GameLog).where(GameLog.scope == 'breakthrough'))) == 0
    # The same request is valid after rollback, even without requesting another preview.
    assert (await client.post('/breakthrough/attempt', json=payload)).status_code == 200


async def test_legacy_receipt_remains_replayable(game):
    client, sessions = game
    await prepare(client, sessions)
    request_id = str(uuid4())
    old_result = dict(success=False, message='Thất bại', cultivation_lost=12,
                      realm=dict(key='qi_refining', name='Luyện Khí', stage=1, max_stage=9))
    async with sessions() as session:
        session.add(GameLog(scope='breakthrough', message='Thất bại', log_metadata={'request_id': request_id, 'result': old_result}))
        await session.commit()
    response = await client.post('/breakthrough/attempt', json={'request_id': request_id, 'revision': '2026-09-16T00:00:00Z'})
    assert response.status_code == 200
    assert response.json()['items_consumed'] == 0
    assert response.json()['rules_version'] == 1
    assert response.json()['rules_fingerprint'] == 'legacy'
    assert (await client.get('/game/state')).json()['player']['qi_gathering_pills'] == 3


@pytest.mark.parametrize('blocked', ['insufficient_cultivation', 'max_realm'])
async def test_supported_rejection_never_rolls_or_consumes(game, blocked):
    client, sessions = game
    player_id = await prepare(client, sessions)
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        if blocked == 'insufficient_cultivation':
            player.cultivation_exp = 0
        else:
            realm = await session.scalar(select(Realm).where(Realm.key == REALM_DEFINITIONS[-1]['key']))
            player.realm = realm
            player.stage = realm.max_stage
        await session.commit()
    payload = await pill_request(client)
    rng = Mock()
    async with sessions() as session:
        with pytest.raises(GameError) as error:
            await GameStateService(session, rng).attempt(BreakthroughRequest(**payload))
        assert error.value.code == blocked
    rng.roll.assert_not_called()
    async with sessions() as session:
        assert (await session.get(OwnedItem, (player_id, PILL_KEY))).quantity == 3
        assert await session.scalar(select(func.count()).select_from(GameLog).where(GameLog.scope == 'breakthrough')) == 0


async def test_major_supported_preview_and_commit(game):
    client, sessions = game
    await prepare(client, sessions)
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.stage = 9
        player.cultivation_exp = 10000
        await session.commit()
    for _ in range(2):
        payload = await pill_request(client)
    preview = (await client.get('/breakthrough/preview', params={'item_key': PILL_KEY, 'quantity': 1})).json()
    assert preview['final_chance'] == pytest.approx(.559)
    assert preview['target']['key'] == 'foundation_establishment'
    assert (await client.get('/game/state')).json()['player']['qi_gathering_pills'] == 3
    payload['revision'] = preview['revision']
    rng = Mock()
    rng.roll.return_value = .1
    async with sessions() as session:
        result = await GameStateService(session, rng).attempt(BreakthroughRequest(**payload))
    assert result.realm.key == 'foundation_establishment'
    assert result.realm.stage == 1
    assert result.items_consumed == 1
    rng.roll.assert_called_once()
