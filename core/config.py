"""Pydantic settings for the Football AI FastAPI service."""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

# Single source of truth — only place that reads FOOTBALL_DATA_* from the environment.
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "").strip()
FOOTBALL_DATA_BASE_URL = os.getenv(
    "FOOTBALL_DATA_BASE_URL",
    "https://api.football-data.org/v4",
).strip()
FOOTBALL_DATA_TIMEOUT = int(os.getenv("FOOTBALL_DATA_TIMEOUT", "20") or 20)
FOOTBALL_DATA_CACHE_TTL = int(os.getenv("FOOTBALL_DATA_CACHE_TTL", "21600") or 21600)
FOOTBALL_DATA_LIVE_CACHE_TTL = int(os.getenv("FOOTBALL_DATA_LIVE_CACHE_TTL", "120") or 120)
FOOTBALL_DATA_STANDINGS_CACHE_TTL = int(
    os.getenv("FOOTBALL_DATA_STANDINGS_CACHE_TTL", "43200") or 43200
)


def get_football_data_api_key() -> str:
    """Return the configured football-data.org API key (may be empty)."""
    return FOOTBALL_DATA_API_KEY


def require_football_data_api_key() -> str:
    """Fail fast when the FastAPI service starts without a football-data.org key."""
    if not FOOTBALL_DATA_API_KEY:
        raise RuntimeError(
            "FOOTBALL_DATA_API_KEY is required to start the Football AI API. "
            "Set it in Railway or .env."
        )
    return FOOTBALL_DATA_API_KEY


class Settings(BaseSettings):
    """Environment-backed settings for the Football AI FastAPI service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    football_ai_cache_ttl: int = Field(
        default=900,
        validation_alias="FOOTBALL_AI_CACHE_TTL",
    )
    football_default_season: int = Field(
        default=2025,
        validation_alias="FOOTBALL_DEFAULT_SEASON",
    )
    app_base_url: str = Field(
        default="http://localhost:8501",
        validation_alias="APP_BASE_URL",
    )
    api_cors_origins: str = Field(default="", validation_alias="API_CORS_ORIGINS")

    def cors_origins(self) -> list[str]:
        """Explicit API_CORS_ORIGINS, else APP_BASE_URL (+ localhost for dev)."""
        raw = self.api_cors_origins.strip()
        if raw == "*":
            return ["*"]
        if raw:
            return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
        origins: list[str] = []
        for candidate in (self.app_base_url, "http://localhost:8501"):
            origin = candidate.strip().rstrip("/")
            if origin and origin not in origins:
                origins.append(origin)
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
