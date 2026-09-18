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
