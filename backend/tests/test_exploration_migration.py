from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.services.exploration_service import ExplorationService
from app.schemas.exploration import ExplorationRequest
from tests.test_inventory_migration import upgrade


async def test_migration_keeps_existing_save_and_creates_run_table():
    schema = 'test_explore_' + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={'server_settings': {'search_path': schema}})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, '20260917_0005')
            assert (await connection.execute(text("SELECT to_regclass('exploration_runs')"))).scalar() is None
            await connection.run_sync(upgrade, 'head')
            assert (await connection.execute(text("SELECT to_regclass('exploration_runs')"))).scalar() == 'exploration_runs'
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            assert (await session.execute(text('SELECT count(*) FROM players'))).scalar() == 0
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


async def test_completed_run_survives_journey_migration_and_second_upgrade():
    from tests.test_inventory_migration import upgrade
    schema = "test_journey_migration_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "20260921_0009")
            await connection.execute(text("""INSERT INTO realms (key,name,rank_order,max_stage,base_required_exp,growth_factor)
                VALUES ('qi_refining','Luyện Khí',1,9,120,1.45)"""))
            await connection.execute(text("""INSERT INTO spiritual_roots (key,name,elements,quality,cultivation_modifier,breakthrough_modifier)
                VALUES ('wood_common','Mộc Linh Căn',ARRAY['wood'],'common',1.08,1.02)"""))
            await connection.execute(text("""INSERT INTO players (name,realm_id,spiritual_root_id,stage,cultivation_exp,spirit_stones,
                combat_power,manual_key,current_activity,last_cultivation_at)
                VALUES ('Thanh Vân',(SELECT id FROM realms WHERE key='qi_refining'),
                    (SELECT id FROM spiritual_roots WHERE key='wood_common'),
                    1,0,10,12,'manual/qing_mu_jue','cultivating',now())"""))
            await connection.execute(text("""INSERT INTO exploration_runs
                (player_id,request_id,location_key,state,message,victory,reward_stones,reward_pills,battle_log,combat_snapshot,rules_version,rules_fingerprint)
                VALUES ((SELECT id FROM players),'legacy-run','qingyun_mountain','victory','đã xong',true,10,1,'[]','{}',1,'legacy')"""))
            await connection.run_sync(upgrade, "head")
            await connection.run_sync(upgrade, "head")
            assert (await connection.execute(text("SELECT version_num FROM alembic_version"))).scalar() == "20260922_0010"
            row = (await connection.execute(text("SELECT state, reward_item_quantity, available_at FROM exploration_runs"))).one()
            assert row.state == "victory" and row.reward_item_quantity == 0 and row.available_at is None
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
