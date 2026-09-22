from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


def upgrade(connection, revision):
    config = Config("alembic.ini")
    config.attributes["connection"] = connection
    command.upgrade(config, revision)


@pytest.mark.asyncio
async def test_game_rules_migration_preserves_old_receipts_and_is_idempotent():
    schema = "test_game_rules_migration_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "20260918_0007")
            await connection.run_sync(upgrade, "head")
            await connection.run_sync(upgrade, "head")
            assert (await connection.execute(text("SELECT version_num FROM alembic_version"))).scalar() == "20260922_0010"
            assert (await connection.execute(text("SELECT count(*) FROM game_rule_versions"))).scalar() == 0
            for table, columns in {
                "exploration_runs": {"rules_version", "rules_fingerprint"},
                "world_states": {"rules_fingerprint"},
                "world_reports": {"rules_version", "rules_fingerprint"},
            }.items():
                found = set((await connection.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_schema=current_schema() AND table_name=:table"
                ), {"table": table})).scalars())
                assert columns <= found
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
