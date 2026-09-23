import asyncio
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
from app.db.base import Base
from app.game.data.items import HERB_KEY, PILL_KEY
from app.main import create_app
from app.models.alchemy import AlchemyReceipt
from app.models.item import OwnedItem
from app.models.player import Player


@pytest_asyncio.fixture
async def game():
    schema = "test_alchemy_" + uuid4().hex
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


async def grant_herbs(sessions, quantity):
    async with sessions() as session:
        player = await session.scalar(select(Player))
        owned = await session.get(OwnedItem, (player.id, HERB_KEY))
        if owned is None:
            session.add(OwnedItem(player_id=player.id, item_key=HERB_KEY, quantity=quantity))
        else:
            owned.quantity = quantity
        await session.commit()


def quantity(state, key):
    return next(item["quantity"] for item in state["inventory"] if item["key"] == key)


def craft_body(request_id, ingredient_quantity=3):
    return {"request_id": str(request_id), "recipe_key": "recipe/qi_pill", "ingredient_quantity": ingredient_quantity}


async def test_catalog_shows_both_recipes_before_any_craft(game):
    client, _ = game
    await new_game(client)
    catalog = (await client.get("/alchemy")).json()
    assert [recipe["key"] for recipe in catalog["recipes"]] == [
        "recipe/qi_pill",
        "recipe/qi_pill_batch",
    ]
    assert catalog["recipes"][0]["ingredient_quantity"] == 3
    assert catalog["recipes"][0]["result_quantity"] == 1
    assert catalog["recipes"][1]["ingredient_quantity"] == 6
    assert catalog["recipes"][1]["result_quantity"] == 2
    assert catalog["herb_quantity"] == 0
    state = (await client.get("/game/state")).json()
    async with game[1]() as session:
        assert await session.scalar(select(AlchemyReceipt)) is None
    assert quantity(state, PILL_KEY) == catalog["pill_quantity"]


async def test_craft_once_replays_and_rejects_a_different_quantity(game):
    client, sessions = game
    await new_game(client)
    await grant_herbs(sessions, 6)
    before = (await client.get("/game/state")).json()
    request_id = uuid4()
    first = await client.post("/alchemy/craft", json=craft_body(request_id))
    assert first.status_code == 200
    replay = await client.post("/alchemy/craft", json=craft_body(request_id))
    assert replay.status_code == 200
    assert replay.json()["receipt"] == first.json()["receipt"]
    conflict = await client.post("/alchemy/craft", json=craft_body(request_id, 4))
    assert conflict.status_code == 409
    assert conflict.json()["detail"] == "alchemy_request_conflict"
    state = (await client.get("/game/state")).json()
    assert quantity(state, HERB_KEY) == 3
    assert quantity(state, PILL_KEY) == quantity(before, PILL_KEY) + 1
    assert state["player"]["combat_power"] == before["player"]["combat_power"]
    assert state["cultivation"]["rate_per_minute"] == before["cultivation"]["rate_per_minute"]
    assert state["equipment"] == before["equipment"]
    assert state["spirit_pet"] == before["spirit_pet"]
    assert state["breakthrough"]["final_chance"] == before["breakthrough"]["final_chance"]


async def test_two_tabs_and_a_later_request_cannot_mint_a_pill(game):
    client, sessions = game
    await new_game(client)
    await grant_herbs(sessions, 3)
    before = (await client.get("/game/state")).json()
    responses = await asyncio.gather(*[
        client.post("/alchemy/craft", json=craft_body(uuid4()))
        for _ in range(2)
    ])
    assert sorted(response.status_code for response in responses) == [200, 409]
    state = (await client.get("/game/state")).json()
    assert quantity(state, HERB_KEY) == 0
    assert quantity(state, PILL_KEY) == quantity(before, PILL_KEY) + 1
    again = await client.post("/alchemy/craft", json=craft_body(uuid4()))
    assert again.status_code == 409
    assert again.json()["detail"] == "insufficient_herbs"
    after = (await client.get("/game/state")).json()
    assert quantity(after, PILL_KEY) == quantity(state, PILL_KEY)


async def test_batch_recipe_spends_six_herbs_once(game):
    client, sessions = game
    await new_game(client)
    await grant_herbs(sessions, 6)
    before = (await client.get("/game/state")).json()
    body = {"request_id": str(uuid4()), "recipe_key": "recipe/qi_pill_batch", "ingredient_quantity": 6}
    first = await client.post("/alchemy/craft", json=body)
    assert first.status_code == 200
    replay = await client.post("/alchemy/craft", json=body)
    assert replay.json()["receipt"] == first.json()["receipt"]
    state = (await client.get("/game/state")).json()
    assert quantity(state, HERB_KEY) == 0
    assert quantity(state, PILL_KEY) == quantity(before, PILL_KEY) + 2
    again = await client.post("/alchemy/craft", json={**body, "request_id": str(uuid4())})
    assert again.status_code == 409
    assert again.json()["detail"] == "insufficient_herbs"


async def test_too_few_herbs_and_a_bad_request_leave_the_bag_unchanged(game):
    client, sessions = game
    await new_game(client)
    await grant_herbs(sessions, 2)
    before = (await client.get("/game/state")).json()
    short = await client.post("/alchemy/craft", json=craft_body(uuid4()))
    assert short.status_code == 409
    assert short.json()["detail"] == "insufficient_herbs"
    unknown = await client.post("/alchemy/craft", json={**craft_body(uuid4()), "recipe_key": "recipe/unknown"})
    assert unknown.status_code == 409
    assert unknown.json()["detail"] == "alchemy_request_conflict" or unknown.json()["detail"] == "unknown_recipe"
    state = (await client.get("/game/state")).json()
    assert quantity(state, HERB_KEY) == 2
    assert quantity(state, PILL_KEY) == quantity(before, PILL_KEY)
    async with sessions() as session:
        assert await session.scalar(select(AlchemyReceipt)) is None
    await grant_herbs(sessions, 3)
    made = await client.post("/alchemy/craft", json=craft_body(uuid4()))
    assert made.status_code == 200
    assert quantity(made.json()["state"], HERB_KEY) == 0
    assert quantity(made.json()["state"], PILL_KEY) == quantity(before, PILL_KEY) + 1


def upgrade(connection, revision):
    config = Config("alembic.ini")
    config.attributes["connection"] = connection
    command.upgrade(config, revision)


async def test_migration_does_not_craft_for_an_existing_save():
    schema = "test_alchemy_migration_" + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, "20260923_0011")
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
            await connection.execute(text("""INSERT INTO items (key,name,category,description,asset_key)
                VALUES ('items/cloud_mist_herb','Vân Linh Thảo','material','thảo','items/cloud_mist_herb')"""))
            await connection.execute(text("""INSERT INTO owned_items (player_id,item_key,quantity)
                VALUES ((SELECT id FROM players),'items/cloud_mist_herb',5),
                       ((SELECT id FROM players),'items/qi_gathering_pill',2)"""))
            await connection.run_sync(upgrade, "head")
            assert (await connection.execute(text("SELECT version_num FROM alembic_version"))).scalar() == "20260923_0013"
            assert (await connection.execute(text("SELECT count(*) FROM alchemy_receipts"))).scalar() == 0
            assert (await connection.execute(text("SELECT quantity FROM owned_items WHERE item_key='items/cloud_mist_herb'"))).scalar() == 5
            assert (await connection.execute(text("SELECT quantity FROM owned_items WHERE item_key='items/qi_gathering_pill'"))).scalar() == 2
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
