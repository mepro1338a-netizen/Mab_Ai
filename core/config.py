"""Pydantic settings for the Football AI FastAPI service."""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

# Single source of truth — only place that reads FOOTBALL_* provider env vars.
FOOTBALL_API_PROVIDER = os.getenv("FOOTBALL_API_PROVIDER", "football-data.org").strip().lower()
FOOTBALL_API_INCLUDE = os.getenv(
    "FOOTBALL_API_INCLUDE",
    "participants;scores;periods;events;league.country;round",
).strip()

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

SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY", "").strip()
SPORTMONKS_BASE_URL = os.getenv(
    "SPORTMONKS_BASE_URL",
    "https://api.sportmonks.com/v3/football",
).strip()


def get_football_api_provider() -> str:
    """Return active football data provider: football-data.org or sportmonks."""
    provider = FOOTBALL_API_PROVIDER or "football-data.org"
    if provider in ("sportmonks", "sm"):
        return "sportmonks"
    return "football-data.org"


def get_football_data_api_key() -> str:
    """Return the configured football-data.org API key (may be empty)."""
    return FOOTBALL_DATA_API_KEY


def get_sportmonks_api_key() -> str:
    """Return the configured SportMonks API key (may be empty)."""
    return SPORTMONKS_API_KEY


def is_football_api_configured() -> bool:
    """True when the configured provider has a valid API key."""
    if get_football_api_provider() == "sportmonks":
        return bool(SPORTMONKS_API_KEY)
    return bool(FOOTBALL_DATA_API_KEY)


def require_football_data_api_key() -> str:
    """Fail fast when the FastAPI service starts without a football API key."""
    provider = get_football_api_provider()
    if provider == "sportmonks":
        if not SPORTMONKS_API_KEY:
            raise RuntimeError(
                "SPORTMONKS_API_KEY is required when FOOTBALL_API_PROVIDER=sportmonks. "
                "Set it in Railway or .env (never commit the token)."
            )
        return SPORTMONKS_API_KEY
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
