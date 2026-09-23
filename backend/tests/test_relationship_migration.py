from datetime import datetime, timezone
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.relationship_service import RelationshipService


def upgrade(connection, revision):
    config = Config("alembic.ini")
    config.attributes["connection"] = connection
    command.upgrade(config, revision)


@pytest.mark.asyncio
async def test_existing_save_upgrades_to_relationships_and_redeploy_is_idempotent():
    schema = "test_relationship_migration_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(
        settings.database_url,
        connect_args={"server_settings": {"search_path": schema}},
    )
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "20260921_0008")
            await connection.execute(text("""INSERT INTO realms
                (key,name,rank_order,max_stage,base_required_exp,growth_factor)
                VALUES ('qi_refining','Luyện Khí',1,9,120,1.45)"""))
            await connection.execute(text("""INSERT INTO spiritual_roots
                (key,name,elements,quality,cultivation_modifier,breakthrough_modifier)
                VALUES ('wood_common','Mộc Linh Căn',ARRAY['wood'],'common',1.08,1.02)"""))
            await connection.execute(text("""INSERT INTO players
                (name,realm_id,spiritual_root_id,stage,cultivation_exp,spirit_stones,
                 combat_power,equipment_pack_claimed,manual_key,current_activity,
                 last_cultivation_at)
                VALUES ('Thanh Vân',
                    (SELECT id FROM realms WHERE key='qi_refining'),
                    (SELECT id FROM spiritual_roots WHERE key='wood_common'),
                    2,45,17,12,false,'manual/qing_mu_jue','cultivating',now())"""))
            await connection.run_sync(upgrade, "head")
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            profile = await RelationshipService(
                session, now=datetime(2026, 9, 21, tzinfo=timezone.utc)
            ).get_profile("xie_wuchen")
            assert profile.affinity == 0
        await engine.dispose()
        engine = create_async_engine(
            settings.database_url,
            connect_args={"server_settings": {"search_path": schema}},
        )
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "head")
            assert (
                await connection.execute(text("SELECT version_num FROM alembic_version"))
            ).scalar() == "20260923_0013"
            assert (
                await connection.execute(text("SELECT count(*) FROM players"))
            ).scalar() == 1
            assert (
                await connection.execute(text("SELECT count(*) FROM world_npcs"))
            ).scalar() == 3
            assert (
                await connection.execute(text("SELECT count(*) FROM npc_relationships"))
            ).scalar() == 1
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()

