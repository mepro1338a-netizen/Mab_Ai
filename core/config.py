"""Pydantic settings for the Football AI FastAPI service."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings; mirrors root config.py football-data vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    football_data_api_key: str = Field(default="", validation_alias="FOOTBALL_DATA_API_KEY")
    football_data_base_url: str = Field(
        default="https://api.football-data.org/v4",
        validation_alias="FOOTBALL_DATA_BASE_URL",
    )
    football_data_timeout: int = Field(default=20, validation_alias="FOOTBALL_DATA_TIMEOUT")
    football_data_cache_ttl: int = Field(
        default=21_600,
        validation_alias="FOOTBALL_DATA_CACHE_TTL",
    )
    football_ai_cache_ttl: int = Field(
        default=900,
        validation_alias="FOOTBALL_AI_CACHE_TTL",
    )
    football_default_season: int = Field(
        default=2025,
        validation_alias="FOOTBALL_DEFAULT_SEASON",
    )
    api_cors_origins: str = Field(default="*", validation_alias="API_CORS_ORIGINS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
