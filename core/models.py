"""Pydantic response models for Football AI endpoints."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TipResponse(BaseModel):
    """Frontend-ready tip payload."""

    match: str
    prediction: str
    confidence: int = Field(ge=0, le=100)
    risk: RiskLevel
    factors: list[str] = Field(default_factory=list)
    suggested_tip: str
    home_team_id: int | None = None
    away_team_id: int | None = None
    fixture_id: int | None = None


class MatchAnalysisResponse(TipResponse):
    """Extended match analysis with raw feature snapshot."""

    home_form_score: float = Field(ge=0, le=100)
    away_form_score: float = Field(ge=0, le=100)
    home_rank: int | None = None
    away_rank: int | None = None
    league: str | None = None


class TeamFormResponse(BaseModel):
    team_id: int
    team_name: str
    form_score: float = Field(ge=0, le=100)
    last_matches: list[str] = Field(default_factory=list)
    goals_scored: int = 0
    goals_conceded: int = 0
    home_record: str = ""
    away_record: str = ""
    rank: int | None = None
    league: str | None = None


class TipsTodayResponse(BaseModel):
    date: str
    count: int
    tips: list[TipResponse] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    football_api_configured: bool = False


class MatchData(BaseModel):
    """Internal bundle passed to generate_tip."""

    home_team_id: int
    away_team_id: int
    home_name: str
    away_name: str
    home_matches: list[dict[str, Any]] = Field(default_factory=list)
    away_matches: list[dict[str, Any]] = Field(default_factory=list)
    home_standing: dict[str, Any] | None = None
    away_standing: dict[str, Any] | None = None
    league_id: int | None = None
    league_name: str | None = None
    fixture_id: int | None = None

    model_config = {"arbitrary_types_allowed": True}
