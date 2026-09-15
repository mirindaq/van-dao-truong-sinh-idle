from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return app


app = create_app()

