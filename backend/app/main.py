from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes.breakthrough import router as breakthrough_router
from app.services.game_state_service import GameError

from app.api.routes.game_state import router as game_state_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(game_state_router, prefix="/game", tags=["game"])
    app.include_router(breakthrough_router, prefix="/breakthrough", tags=["breakthrough"])

    @app.exception_handler(GameError)
    async def game_error_handler(request, exc: GameError):
        return JSONResponse(status_code=exc.status, content={"detail": exc.code})

    return app


app = create_app()
