"""Real PostgreSQL tests in an isolated schema; the user's save is never changed."""
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.api.dependencies import get_session
from app.core.config import settings
from app.db.base import Base
from app.main import create_app
from app.models.player import Player
from app.repositories.player_repository import PlayerRepository
from app.services.game_state_service import GameStateService
from app.game.random_service import RandomService
from app.schemas.game_state import BreakthroughRequest


@pytest_asyncio.fixture
async def game():
    schema = "test_ui_" + uuid4().hex
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


async def test_new_save_validation_and_refresh(game):
    client, _ = game
    assert (await client.get("/game/state")).status_code == 404
    assert (await client.post("/game/new", json={"name": "   "})).status_code == 422
    responses = await asyncio.gather(*[client.post("/game/new", json={"name": "Thanh Vân"}) for _ in range(2)])
    assert sorted(r.status_code for r in responses) == [201, 409]
    state = (await client.get("/game/state")).json()
    assert state["player"]["name"] == "Thanh Vân"
    assert state["spiritual_root"]["key"] == "wood_common"
    assert state["cultivation"]["base_rate_per_minute"] + state["cultivation"]["root_bonus_per_minute"] == state["cultivation"]["rate_per_minute"]


async def test_offline_report_survives_refresh_and_ack(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Vô Danh"})
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.last_cultivation_at = datetime.now(timezone.utc) - timedelta(hours=8)
        await session.commit()
    states = await asyncio.gather(client.get("/game/state"), client.get("/game/state"))
    first, second = [r.json() for r in states]
    report = first["offline_report"]
    assert report["elapsed_seconds"] >= 28800
    assert second["offline_report"]["id"] == report["id"]
    assert abs(first["cultivation"]["current_exp"] - second["cultivation"]["current_exp"]) < 1
    for _ in range(2):
        assert (await client.post(f'/game/offline/{report["id"]}/ack')).status_code == 204
    assert (await client.get("/game/state")).json()["offline_report"] is None


@pytest.mark.parametrize("seed,success", [(1, True), (2, False)])
async def test_attempt_result_persistence_and_replay(game, seed, success):
    client, sessions = game
    await client.post("/game/new", json={"name": "Vô Danh"})
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.cultivation_exp = 150
        await session.commit()
    preview = (await client.get("/breakthrough/preview")).json()
    request = BreakthroughRequest(request_id=uuid4(), revision=preview["revision"])
    async with sessions() as session:
        result = await GameStateService(session, RandomService(seed=seed)).attempt(request)
    assert result.success is success
    replay = await client.post("/breakthrough/attempt", json=request.model_dump(mode="json"))
    assert replay.json() == result.model_dump(mode="json")
    stale = await client.post("/breakthrough/attempt", json={**request.model_dump(mode="json"), "request_id": str(uuid4())})
    assert stale.status_code == 409
    state = (await client.get("/game/state")).json()
    assert state["realm"]["stage"] == (2 if success else 1)
    assert state["cultivation"]["current_exp"] < (31 if success else 139)


async def test_insufficient_and_major_preview(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Vô Danh"})
    preview = (await client.get("/breakthrough/preview")).json()
    response = await client.post("/breakthrough/attempt", json={"request_id": str(uuid4()), "revision": preview["revision"]})
    assert response.json()["detail"] == "insufficient_cultivation"
    async with sessions() as session:
        player = await PlayerRepository(session).get_first()
        player.stage = 9
        await session.commit()
    preview = (await client.get("/breakthrough/preview")).json()
    assert preview["target"]["key"] == "foundation_establishment"
    assert preview["base_chance"] == 0.45
