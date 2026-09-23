import asyncio
from datetime import datetime, timedelta, timezone
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
from app.models.player import Player
from app.models.spirit_pet import SpiritPetBond
from app.schemas.exploration import ExplorationRequest
from app.services.exploration_service import ExplorationService


@pytest_asyncio.fixture
async def game():
    schema = "test_spirit_pet_" + uuid4().hex
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


def upgrade(connection, revision):
    config = Config("alembic.ini")
    config.attributes["connection"] = connection
    command.upgrade(config, revision)


async def test_new_and_old_saves_start_without_a_pet(game):
    client, _ = game
    await new_game(client)
    state = (await client.get("/game/state")).json()
    cult = state["cultivation"]
    assert state["spirit_pet"] is None
    assert state["active_pet"] is None
    assert state["player"]["pet_bonus"] == 0
    assert cult["pet_factor"] == 1
    assert cult["pet_flat_per_minute"] == 0
    root_rate = cult["base_rate_per_minute"] + cult["root_bonus_per_minute"]
    assert cult["rate_per_minute"] == pytest.approx(root_rate)
    catalog = (await client.get("/pets")).json()
    assert [pet["key"] for pet in catalog["species"]] == ["thanh_xa", "hoa_ho", "van_tuoc"]
    assert catalog["spirit_pet"] is None


async def test_bond_is_idempotent_and_rejects_a_second_pet(game):
    client, _ = game
    await new_game(client)
    request_id = str(uuid4())
    body = {"request_id": request_id, "pet_key": "thanh_xa"}
    first = await client.post("/pets/bond", json=body)
    assert first.status_code == 200
    replay = await client.post("/pets/bond", json=body)
    assert replay.status_code == 200
    assert replay.json()["receipt"] == first.json()["receipt"]
    conflict = await client.post("/pets/bond", json={"request_id": request_id, "pet_key": "hoa_ho"})
    assert conflict.status_code == 409
    assert conflict.json()["detail"] == "pet_request_conflict"
    second = await client.post("/pets/bond", json={"request_id": str(uuid4()), "pet_key": "van_tuoc"})
    assert second.status_code == 409
    assert second.json()["detail"] == "pet_already_bonded"
    state = (await client.get("/game/state")).json()
    assert state["spirit_pet"] == {"key": "thanh_xa", "name": "Thanh Xà", "active": True}
    assert state["active_pet"] == "Thanh Xà"
    assert state["player"]["pet_bonus"] == 6
    assert state["player"]["combat_power"] == state["player"]["base_combat_power"] + state["player"]["equipment_bonus"] + 6
    cult = state["cultivation"]
    root_rate = cult["base_rate_per_minute"] + cult["root_bonus_per_minute"]
    assert cult["rate_per_minute"] == pytest.approx(root_rate * cult["pet_factor"] + cult["pet_flat_per_minute"])
    assert cult["pet_factor"] == pytest.approx(1.05)
    assert cult["pet_flat_per_minute"] == pytest.approx(0.2)


async def test_unknown_pet_and_two_tabs_leave_one_bond(game):
    client, sessions = game
    await new_game(client)
    rejected = await client.post("/pets/bond", json={"request_id": str(uuid4()), "pet_key": "unknown"})
    assert rejected.status_code == 409
    assert rejected.json()["detail"] == "unknown_pet"
    async with sessions() as session:
        assert await session.scalar(select(SpiritPetBond)) is None
    responses = await asyncio.gather(*[
        client.post("/pets/bond", json={"request_id": str(uuid4()), "pet_key": key})
        for key in ("thanh_xa", "hoa_ho")
    ])
    assert sorted(response.status_code for response in responses) == [200, 409]
    state = (await client.get("/game/state")).json()
    assert state["spirit_pet"]["key"] in {"thanh_xa", "hoa_ho"}


async def test_rest_and_recall_split_cultivation_and_keep_one_bonus(game):
    client, sessions = game
    await new_game(client)
    before = (await client.get("/game/state")).json()
    inventory = before["inventory"]
    equipment = before["equipment"]
    chance = before["breakthrough"]["final_chance"]
    root_rate = before["cultivation"]["base_rate_per_minute"] + before["cultivation"]["root_bonus_per_minute"]
    async with sessions() as session:
        player = await session.scalar(select(Player))
        player.last_cultivation_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        await session.commit()
    bonded = (await client.post("/pets/bond", json={"request_id": str(uuid4()), "pet_key": "thanh_xa"})).json()["state"]
    plain_gain = bonded["cultivation"]["current_exp"] - before["cultivation"]["current_exp"]
    assert plain_gain == pytest.approx(root_rate * 10, abs=0.2)
    async with sessions() as session:
        player = await session.scalar(select(Player))
        player.last_cultivation_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        await session.commit()
    rested = (await client.post("/pets/rest")).json()
    boosted = root_rate * bonded["cultivation"]["pet_factor"] + bonded["cultivation"]["pet_flat_per_minute"]
    active_gain = rested["cultivation"]["current_exp"] - bonded["cultivation"]["current_exp"]
    assert active_gain == pytest.approx(boosted * 10, abs=0.2)
    assert rested["player"]["pet_bonus"] == 0
    assert rested["spirit_pet"]["active"] is False
    assert rested["spirit_pet"]["name"] == "Thanh Xà"
    assert rested["active_pet"] is None
    again = (await client.post("/pets/rest")).json()
    assert again["cultivation"]["current_exp"] == pytest.approx(rested["cultivation"]["current_exp"])
    async with sessions() as session:
        player = await session.scalar(select(Player))
        player.last_cultivation_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        await session.commit()
    later = (await client.get("/game/state")).json()
    resting_gain = later["cultivation"]["current_exp"] - rested["cultivation"]["current_exp"]
    assert resting_gain == pytest.approx(root_rate * 10, abs=0.2)
    recalled = (await client.post("/pets/recall")).json()
    assert recalled["cultivation"]["current_exp"] >= later["cultivation"]["current_exp"] - 0.01
    assert recalled["player"]["pet_bonus"] == 6
    assert recalled["player"]["combat_power"] == recalled["player"]["base_combat_power"] + recalled["player"]["equipment_bonus"] + 6
    assert recalled["breakthrough"]["final_chance"] == chance
    assert recalled["inventory"] == inventory
    assert recalled["equipment"] == equipment
    duplicate = (await client.post("/pets/recall")).json()
    assert duplicate["cultivation"]["current_exp"] == pytest.approx(recalled["cultivation"]["current_exp"])


async def test_exploration_adds_the_active_pet_bonus_once(game):
    client, sessions = game
    await new_game(client)
    await client.post("/pets/bond", json={"request_id": str(uuid4()), "pet_key": "thanh_xa"})
    rules = game_rules.model_copy(update={"exploration_empty_chance": 0})
    async with sessions() as session:
        rng = Mock()
        rng.roll = Mock(return_value=0.9)
        rng.randint = Mock(return_value=0)
        result = await ExplorationService(session, rng, rules).run(ExplorationRequest(request_id=uuid4()))
    power = game_rules.starting_combat_power + game_rules.pet_rules["thanh_xa"].combat_bonus
    assert result.exploration.combat_snapshot["player"]["hp"] == rules.battle_player_hp_base + power


async def test_migration_does_not_grant_a_pet_to_an_existing_save():
    schema = "test_spirit_pet_migration_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "20260922_0010")
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
            assert (await connection.execute(text("SELECT count(*) FROM spirit_pet_bonds"))).scalar() == 0
            assert (await connection.execute(text("SELECT count(*) FROM players"))).scalar() == 1
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
