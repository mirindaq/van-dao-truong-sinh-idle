import asyncio
from unittest.mock import Mock
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.dependencies import get_session
from app.core.config import settings
from app.core.game_rules import game_rules
from app.db.base import Base
from app.main import create_app
from app.models.partner import DaoPartner
from app.models.player import Player
from app.models.relationship import NpcRelationship
from app.schemas.exploration import ExplorationRequest
from app.services.exploration_service import ExplorationService


@pytest_asyncio.fixture
async def game():
    schema = "test_partner_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    app = create_app()

    async def session_override():
        async with sessions() as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client, sessions
    await engine.dispose()
    async with admin.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    await admin.dispose()


async def new_game(client):
    assert (await client.post("/game/new", json={"name": "Thanh Vân"})).status_code == 201


async def set_affinity(sessions, npc_key, affinity):
    async with sessions() as session:
        player = await session.scalar(select(Player))
        row = await session.scalar(select(NpcRelationship).where(
            NpcRelationship.player_id == player.id, NpcRelationship.npc_key == npc_key,
        ))
        if row is None:
            session.add(NpcRelationship(player_id=player.id, npc_key=npc_key, affinity=affinity))
        else:
            row.affinity = affinity
        await session.commit()


def expected_rate(state):
    cult = state["cultivation"]
    root = cult["base_rate_per_minute"] + cult["root_bonus_per_minute"]
    return root * cult["pet_factor"] * cult["partner_factor"] + cult["pet_flat_per_minute"] + cult["partner_flat_per_minute"]


async def test_low_affinity_cannot_bond_and_eight_bonds_once(game):
    client, sessions = game
    await new_game(client)
    await set_affinity(sessions, "luo_qinghan", 7)
    refused = await client.post("/partners/bond", json={"npc_key": "luo_qinghan"})
    assert refused.status_code == 409
    assert refused.json()["detail"] == "partner_not_ready"
    before = (await client.get("/game/state")).json()
    assert before["player"]["partner_bonus"] == 0
    await set_affinity(sessions, "luo_qinghan", 8)
    bonded = (await client.post("/partners/bond", json={"npc_key": "luo_qinghan"})).json()
    again = (await client.post("/partners/bond", json={"npc_key": "luo_qinghan"})).json()
    assert bonded["player"]["partner_bonus"] == 3
    assert again["player"]["partner_bonus"] == 3
    assert bonded["player"]["combat_power"] == before["player"]["combat_power"] + 3
    assert bonded["cultivation"]["rate_per_minute"] == pytest.approx(expected_rate(bonded))
    assert bonded["breakthrough"]["final_chance"] == before["breakthrough"]["final_chance"]
    assert bonded["dao_partner"] == "Lạc Thanh Hàn"


async def test_all_five_new_women_can_bond_at_eight_affinity(game):
    client, sessions = game
    await new_game(client)
    expected_names = ["Diệp Thanh Trúc", "Hồng Liên", "Bạch Nguyệt", "Lôi Tử Yên", "Vân Nhược Ly"]
    new_keys = ["ye_qingzhu", "hong_lian", "bai_yue", "lei_ziyan", "yun_ruoli"]
    for index, npc_key in enumerate(new_keys, start=1):
        await set_affinity(sessions, npc_key, 8)
        state = (await client.post("/partners/bond", json={"npc_key": npc_key})).json()
        assert state["player"]["partner_bonus"] == game_rules.dao_partner_combat * index
    roster = (await client.get("/partners")).json()["partners"]
    assert len(roster) == 8
    assert [item["name"] for item in roster if item["npc_key"] in new_keys] == expected_names
    assert all(item["active"] for item in roster if item["npc_key"] in new_keys)


async def test_second_partner_stacks_and_dismiss_removes_only_that_share(game):
    client, sessions = game
    await new_game(client)
    await set_affinity(sessions, "luo_qinghan", 8)
    await set_affinity(sessions, "xie_wuchen", 8)
    await client.post("/partners/bond", json={"npc_key": "luo_qinghan"})
    both = (await client.post("/partners/bond", json={"npc_key": "xie_wuchen"})).json()
    assert both["player"]["partner_bonus"] == 6
    assert both["cultivation"]["partner_flat_per_minute"] == pytest.approx(0.2)
    assert both["cultivation"]["rate_per_minute"] == pytest.approx(expected_rate(both))
    one = (await client.post("/partners/dismiss", json={"npc_key": "luo_qinghan"})).json()
    assert one["player"]["partner_bonus"] == 3
    assert one["dao_partner"] == "Tạ Vô Trần"
    assert one["cultivation"]["rate_per_minute"] == pytest.approx(expected_rate(one))
    responses = await asyncio.gather(*[
        client.post("/partners/bond", json={"npc_key": "luo_qinghan"}) for _ in range(2)
    ])
    assert all(response.status_code == 200 for response in responses)
    state = (await client.get("/game/state")).json()
    assert state["player"]["partner_bonus"] == 6


async def test_two_tabs_first_bond_leave_one_partner(game):
    client, sessions = game
    await new_game(client)
    await set_affinity(sessions, "wandering_cultivator", 8)
    responses = await asyncio.gather(*[
        client.post("/partners/bond", json={"npc_key": "wandering_cultivator"})
        for _ in range(2)
    ])
    assert all(response.status_code == 200 for response in responses)
    async with sessions() as session:
        rows = list(await session.scalars(select(DaoPartner)))
        assert len(rows) == 1
        assert rows[0].active is True


def upgrade(connection, revision):
    config = Config("alembic.ini")
    config.attributes["connection"] = connection
    command.upgrade(config, revision)


async def test_exploration_uses_the_partner_bonus_once(game):
    client, sessions = game
    await new_game(client)
    await set_affinity(sessions, "wandering_cultivator", 8)
    await client.post("/partners/bond", json={"npc_key": "wandering_cultivator"})
    rules = game_rules.model_copy(update={"exploration_empty_chance": 0})
    async with sessions() as session:
        rng = Mock()
        rng.roll = Mock(return_value=0.9)
        rng.randint = Mock(return_value=0)
        result = await ExplorationService(session, rng, rules).run(ExplorationRequest(request_id=uuid4()))
    power = game_rules.starting_combat_power + game_rules.dao_partner_combat
    assert result.exploration.combat_snapshot["player"]["hp"] == rules.battle_player_hp_base + power


async def test_migration_does_not_create_a_partner():
    schema = "test_partner_migration_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "20260923_0012")
            await connection.execute(text("""INSERT INTO realms
                (key,name,rank_order,max_stage,base_required_exp,growth_factor)
                VALUES ('qi_refining','Luyện Khí',1,9,120,1.45)"""))
            await connection.execute(text("""INSERT INTO spiritual_roots
                (key,name,elements,quality,cultivation_modifier,breakthrough_modifier)
                VALUES ('wood_common','Mộc Linh Căn',ARRAY['wood'],'common',1.08,1.02)"""))
            await connection.execute(text("""INSERT INTO players
                (name,realm_id,spiritual_root_id,stage,cultivation_exp,spirit_stones,
                 combat_power,equipment_pack_claimed,manual_key,current_activity,last_cultivation_at)
                VALUES ('Thanh Vân',
                    (SELECT id FROM realms WHERE key='qi_refining'),
                    (SELECT id FROM spiritual_roots WHERE key='wood_common'),
                    1,0,10,12,false,'manual/qing_mu_jue','cultivating',now())"""))
            await connection.run_sync(upgrade, "head")
            assert (await connection.execute(text("SELECT version_num FROM alembic_version"))).scalar() == "20260923_0013"
            assert (await connection.execute(text("SELECT count(*) FROM dao_partners"))).scalar() == 0
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
