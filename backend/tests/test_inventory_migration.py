from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.services.game_state_service import GameStateService
from app.game.data.items import PILL_KEY, MANUAL_KEY
from app.schemas.game_state import BreakthroughRequest, BreakthroughSelection
from app.repositories.player_repository import PlayerRepository
from app.game.random_service import RandomService


def upgrade(connection, revision):
    config = Config("alembic.ini")
    config.attributes['connection'] = connection
    command.upgrade(config, revision)


@pytest.mark.parametrize('quantity', [None, 0, 3, 7])
async def test_legacy_save_migration_and_redeploy(quantity):
    schema = 'test_migration_' + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    options = {'server_settings': {'search_path': schema}}
    engine = create_async_engine(settings.database_url, connect_args=options)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(upgrade, '20260916_0003')
            if quantity is not None:
                await conn.execute(text("""INSERT INTO realms
                    (key,name,rank_order,max_stage,base_required_exp,growth_factor)
                    VALUES ('qi_refining','Luyện Khí',1,9,120,1.45)"""))
                await conn.execute(text("""INSERT INTO spiritual_roots
                    (key,name,elements,quality,cultivation_modifier,breakthrough_modifier)
                    VALUES ('wood_common','Mộc Linh Căn',ARRAY['wood'],'common',1.08,1.02)"""))
                await conn.execute(text("""INSERT INTO players
                    (name,realm_id,spiritual_root_id,stage,cultivation_exp,spirit_stones,
                    qi_gathering_pills,combat_power,manual_key,current_activity,last_cultivation_at)
                    VALUES ('Thanh Vân',(SELECT id FROM realms WHERE key='qi_refining'),
                    (SELECT id FROM spiritual_roots WHERE key='wood_common'),2,45,17,:quantity,12,
                    'manual/qing_mu_jue','cultivating',now() + interval '1 hour')"""), {'quantity': quantity})
            await conn.run_sync(upgrade, 'head')
        await engine.dispose()
        engine = create_async_engine(settings.database_url, connect_args=options)
        async with engine.begin() as conn:
            await conn.run_sync(upgrade, 'head')
            assert (await conn.execute(text('SELECT version_num FROM alembic_version'))).scalar() == '20260922_0010'
            assert (await conn.execute(text('SELECT count(*) FROM players'))).scalar() == (0 if quantity is None else 1)
            if quantity is None:
                assert (await conn.execute(text('SELECT count(*) FROM owned_items'))).scalar() == 0
        if quantity is not None:
            sessions = async_sessionmaker(engine, expire_on_commit=False)
            async with sessions() as session:
                state = await GameStateService(session).get_state()
                assert {i.key: i.quantity for i in state.inventory} == {PILL_KEY: quantity, MANUAL_KEY: 1}
                assert state.player.qi_gathering_pills == quantity
                assert state.player.spirit_stones == 17
                assert state.cultivation.current_exp == 45
                assert state.realm.stage == 2
            if quantity > 0:
                async with sessions() as session:
                    player = await PlayerRepository(session).get_first()
                    player.cultivation_exp = 2000
                    await session.commit()
                    service = GameStateService(session, RandomService(seed=1))
                    preview = await service.preview(BreakthroughSelection(item_key=PILL_KEY, quantity=1))
                    payload = BreakthroughRequest(request_id=str(uuid4()), revision=preview.revision,
                                                  item_key=PILL_KEY, quantity=1)
                    receipt = await service.attempt(payload)
                await engine.dispose()
                engine = create_async_engine(settings.database_url, connect_args=options)
                async with engine.begin() as conn:
                    await conn.run_sync(upgrade, 'head')
                sessions = async_sessionmaker(engine, expire_on_commit=False)
                async with sessions() as session:
                    service = GameStateService(session)
                    assert await service.attempt(payload) == receipt
                    state = await service.get_state()
                    assert state.player.qi_gathering_pills == quantity - 1
                    assert next(i.quantity for i in state.inventory if i.key == MANUAL_KEY) == 1
                    assert state.realm.stage == receipt.realm.stage
    finally:
        await engine.dispose()
        async with admin.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
