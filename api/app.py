"""FastAPI application factory for MaByte Football AI API."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.football_ai_routes import router as football_ai_router
from core.config import get_settings, require_football_data_api_key
from core.exceptions import register_exception_handlers
from core.models import HealthResponse
from services.football_data_client import is_fd_configured


@asynccontextmanager
async def _lifespan(_: FastAPI):
    require_football_data_api_key()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="MaByte Football AI API",
        description="Deterministic football match tips powered by football-data.org v4.",
        version="1.0.0",
        lifespan=_lifespan,
    )

    origins = settings.cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=bool(origins and origins != ["*"]),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(football_ai_router)

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            football_api_configured=is_fd_configured(),
        )

    return app


app = create_app()
