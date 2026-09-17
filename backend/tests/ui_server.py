"""Browser-test server with a disposable PostgreSQL schema, never imported by production."""
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import FastAPI
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.api.dependencies import get_session
from app.core.config import settings
from app.db.base import Base
from app.game.random_service import RandomService
from app.main import create_app
from app.models.game_log import GameLog
from app.models.player import Player
from app.game.data.items import PILL_KEY
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.player_repository import PlayerRepository
from app.services import game_state_service
from app.services.game_state_service import GameStateService

schema = "test_browser_" + uuid4().hex
engine = create_async_engine(settings.database_url, connect_args={"server_settings": {"search_path": schema}})
sessions = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


app = create_app()
app.router.lifespan_context = lifespan


async def test_session():
    async with sessions() as session:
        yield session


app.dependency_overrides[get_session] = test_session


@app.post("/_test/prepare/{mode}")
async def prepare(mode: str):
    async with sessions() as session:
        await session.execute(delete(GameLog))
        await session.execute(delete(Player))
        await session.commit()
        if mode != "empty":
            await GameStateService(session).new_game("Thanh Vân")
            player = await PlayerRepository(session).get_first()
            if mode in ("success", "failure", "no-pills"):
                player.cultivation_exp = 150
            if mode == "no-pills":
                pill = await InventoryRepository(session).get(player.id, PILL_KEY)
                pill.quantity = 0
            if mode == "offline":
                player.last_cultivation_at = datetime.now(timezone.utc) - timedelta(hours=8)
            await session.commit()
    seed = 2 if mode == "failure" else 1
    game_state_service.RandomService = lambda: RandomService(seed=seed)
    return {"ready": True}
