import asyncio
from uuid import uuid4
from unittest.mock import Mock
import pytest
from sqlalchemy import select, func
from tests.test_game_api import game  # noqa: F401
from app.models.item import Item, OwnedItem
from app.models.game_log import GameLog
from app.repositories.player_repository import PlayerRepository
from app.services.game_state_service import GameStateService
from app.schemas.game_state import EquipRequest, BreakthroughRequest

SWORD = 'items/bamboo_sword'


async def create(client):
    return (await client.post('/game/new', json={'name': 'Thanh Vân'})).json()


async def test_claim_once_concurrent_and_reload(game):
    client, sessions = game
    state = await create(client)
    assert state['equipment'] == [] and not state['equipment_pack_claimed']
    assert len(state['inventory']) == 2
    responses = await asyncio.gather(*[client.post('/equipment/claim') for _ in range(3)])
    assert all(r.status_code == 200 for r in responses)
    async with sessions() as session:
        state = await GameStateService(session).get_state()
        assert state.equipment_pack_claimed
        assert {i.key: i.quantity for i in state.inventory if i.category == 'equipment'} == {
            SWORD: 1, 'items/cloth_robe': 1, 'items/wood_amulet': 1}
        assert await session.scalar(select(func.count()).select_from(GameLog).where(GameLog.scope == 'equipment')) == 1


async def test_equip_unequip_repeat_and_replacement(game):
    client, sessions = game
    state = await create(client)
    player_id = state['player']['id']
    await client.post('/equipment/claim')
    for slot, key, total in [('weapon', SWORD, 17), ('body', 'items/cloth_robe', 20), ('amulet', 'items/wood_amulet', 22)]:
        for _ in range(2):
            state = (await client.post('/equipment/slot', json={'slot': slot, 'item_key': key})).json()
            assert state['player']['combat_power'] == total
            assert state['player']['base_combat_power'] == 12
    async with sessions() as session:
        session.add(Item(key='items/test_sword', name='Test', category='equipment', description='Test',
                         asset_key='items/default', equipment_slot='weapon', combat_bonus=7))
        await session.flush()
        session.add(OwnedItem(player_id=player_id, item_key='items/test_sword', quantity=1))
        await session.commit()
    state = (await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': 'items/test_sword'})).json()
    assert state['player']['combat_power'] == 24
    assert len(state['equipment']) == 3
    for slot in ['weapon', 'body', 'amulet']:
        for _ in range(2):
            response = await client.post('/equipment/slot', json={'slot': slot, 'item_key': None})
            assert response.status_code == 200
    state = (await client.get('/game/state')).json()
    assert state['player']['combat_power'] == 12
    assert state['equipment'] == []
    assert all(i['quantity'] == 1 for i in state['inventory'] if i['category'] == 'equipment')


async def test_invalid_equipment_never_changes_state(game):
    client, _ = game
    await create(client)
    assert (await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': SWORD})).status_code == 409
    await client.post('/equipment/claim')
    for slot, key, code in [('body', SWORD, 409), ('weapon', 'items/qi_gathering_pill', 409),
                            ('weapon', 'manual/qing_mu_jue', 409), ('invalid', SWORD, 422),
                            ('weapon', 'missing', 409)]:
        assert (await client.post('/equipment/slot', json={'slot': slot, 'item_key': key})).status_code == code
    state = (await client.get('/game/state')).json()
    assert state['equipment'] == [] and state['player']['combat_power'] == 12


async def test_one_item_cannot_occupy_two_slots(game):
    client, _ = game
    await create(client)
    await client.post('/equipment/claim')
    assert (await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': SWORD})).status_code == 200
    assert (await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': SWORD})).status_code == 200
    assert (await client.post('/equipment/slot', json={'slot': 'body', 'item_key': SWORD})).status_code == 409


async def test_concurrent_slots_and_lost_reply_readback(game):
    client, _ = game
    await create(client)
    await client.post('/equipment/claim')
    responses = await asyncio.gather(*[client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': SWORD}) for _ in range(2)])
    assert all(r.status_code == 200 for r in responses)
    responses = await asyncio.gather(
        client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': None}),
        client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': SWORD}))
    assert all(r.status_code == 200 for r in responses)
    state = (await client.get('/game/state')).json()
    assert state['player']['combat_power'] == (17 if state['equipment'] else 12)
    assert next(i['quantity'] for i in state['inventory'] if i['key'] == SWORD) == 1


@pytest.mark.parametrize('action', ['claim', 'equip'])
async def test_commit_failure_rolls_back(game, monkeypatch, action):
    client, sessions = game
    await create(client)
    if action == 'equip':
        await client.post('/equipment/claim')
    async with sessions() as session:
        async def fail():
            await session.flush()
            raise RuntimeError('storage failure')
        monkeypatch.setattr(session, 'commit', fail)
        service = GameStateService(session)
        with pytest.raises(RuntimeError):
            if action == 'claim':
                await service.claim_equipment_pack()
            else:
                await service.equip(EquipRequest(slot='weapon', item_key=SWORD))
    state = (await client.get('/game/state')).json()
    assert state['equipment'] == [] and state['player']['combat_power'] == 12
    assert state['equipment_pack_claimed'] == (action == 'equip')
    if action == 'claim':
        assert len(state['inventory']) == 2


async def test_breakthrough_increases_base_only(game):
    client, sessions = game
    await create(client)
    await client.post('/equipment/claim')
    before = (await client.get('/game/state')).json()
    equipped = (await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': SWORD})).json()
    assert before['cultivation']['rate_per_minute'] == equipped['cultivation']['rate_per_minute']
    assert before['breakthrough']['final_chance'] == equipped['breakthrough']['final_chance']
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.cultivation_exp = 200
        await session.commit()
    preview = (await client.get('/breakthrough/preview')).json()
    rng = Mock(); rng.roll.return_value = .1
    async with sessions() as session:
        await GameStateService(session, rng).attempt(BreakthroughRequest(request_id=uuid4(), revision=preview['revision']))
    state = (await client.get('/game/state')).json()
    assert state['player']['base_combat_power'] == 16
    assert state['player']['combat_power'] == 21
    state = (await client.post('/equipment/slot', json={'slot': 'weapon', 'item_key': None})).json()
    assert state['player']['combat_power'] == 16
