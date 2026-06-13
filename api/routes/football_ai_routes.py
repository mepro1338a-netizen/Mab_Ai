"""Football AI HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from core.models import MatchAnalysisResponse, TeamFormResponse, TipsTodayResponse
from services.football_ai_service import FootballAIService, get_football_ai_service

router = APIRouter(prefix="/ai", tags=["football-ai"])


def _ai_service() -> FootballAIService:
    return get_football_ai_service()


@router.get(
    "/match-analysis/{home_id}/{away_id}",
    response_model=MatchAnalysisResponse,
    summary="Analyze a head-to-head matchup",
)
def match_analysis(
    home_id: int,
    away_id: int,
    ai: FootballAIService = Depends(_ai_service),
) -> MatchAnalysisResponse:
    return ai.analyze_match(home_id, away_id)


@router.get(
    "/tips/today",
    response_model=TipsTodayResponse,
    summary="Today's AI tips for scheduled fixtures",
)
@router.get(
    "/today-tips",
    response_model=TipsTodayResponse,
    summary="Today's AI tips (alias)",
    include_in_schema=True,
)
def tips_today(
    ai: FootballAIService = Depends(_ai_service),
) -> TipsTodayResponse:
    return ai.tips_for_today_response()


@router.get(
    "/team-form/{team_id}",
    response_model=TeamFormResponse,
    summary="Recent form and goals for one team",
)
def team_form(
    team_id: int,
    ai: FootballAIService = Depends(_ai_service),
) -> TeamFormResponse:
    return ai.team_form(team_id)
