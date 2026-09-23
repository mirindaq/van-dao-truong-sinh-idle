from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes.alchemy import router as alchemy_router
from app.api.routes.breakthrough import router as breakthrough_router
from app.api.routes.equipment import router as equipment_router
from app.api.routes.exploration import router as exploration_router
from app.api.routes.world import router as world_router
from app.api.routes.partners import router as partners_router
from app.api.routes.pets import router as pets_router
from app.api.routes.relationships import router as relationships_router
from app.core.game_rules import game_rules
from app.core.game_rule_registry import register_game_rules
from app.services.game_state_service import GameError

from app.api.routes.game_state import router as game_state_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    await register_game_rules()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str | int]:
        return {
            "status": "ok",
            "rules_version": game_rules.rules_version,
            "rules_fingerprint": game_rules.fingerprint,
        }

    app.include_router(game_state_router, prefix="/game", tags=["game"])
    app.include_router(breakthrough_router, prefix="/breakthrough", tags=["breakthrough"])
    app.include_router(equipment_router, prefix="/equipment", tags=["equipment"])
    app.include_router(exploration_router, prefix="/exploration", tags=["exploration"])
    app.include_router(world_router, prefix="/world", tags=["world"])
    app.include_router(relationships_router, prefix="/relationships", tags=["relationships"])
    app.include_router(pets_router, prefix="/pets", tags=["pets"])
    app.include_router(alchemy_router, prefix="/alchemy", tags=["alchemy"])
    app.include_router(partners_router, prefix="/partners", tags=["partners"])

    @app.exception_handler(GameError)
    async def game_error_handler(request, exc: GameError):
        return JSONResponse(status_code=exc.status, content={"detail": exc.code})

    return app


app = create_app()
