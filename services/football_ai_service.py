"""Deterministic Football AI tips — scoring engine (no LLM)."""
from __future__ import annotations

import time
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from core.config import get_settings
from core.exceptions import AnalysisError
from core.models import MatchAnalysisResponse, MatchData, RiskLevel, TeamFormResponse, TipResponse, TipsTodayResponse
from logger import log_info, log_warning
from services.football_service import FootballAPIError, FootballService, get_football_service

_BERLIN_TZ = ZoneInfo("Europe/Berlin")
_RESULT_POINTS = {"W": 3.0, "D": 1.0, "L": 0.0}
_FORM_WEIGHTS = (1.0, 0.9, 0.8, 0.7, 0.6)


def _team_id_from_fixture(fixture: dict[str, Any], side: str) -> int | None:
    try:
        return int(((fixture.get("teams") or {}).get(side) or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def _team_name_from_fixture(fixture: dict[str, Any], side: str, fallback: str) -> str:
    name = ((fixture.get("teams") or {}).get(side) or {}).get("name")
    return str(name or fallback).strip() or fallback


def _match_result_char(fixture: dict[str, Any], team_id: int) -> str | None:
    teams = fixture.get("teams") or {}
    goals = fixture.get("goals") or {}
    try:
        gh, ga = int(goals.get("home")), int(goals.get("away"))
    except (TypeError, ValueError):
        return None
    hid = _team_id_from_fixture(fixture, "home")
    aid = _team_id_from_fixture(fixture, "away")
    if hid == team_id:
        if gh > ga:
            return "W"
        if gh < ga:
            return "L"
        return "D"
    if aid == team_id:
        if ga > gh:
            return "W"
        if ga < gh:
            return "L"
        return "D"
    return None


def _infer_league_id(fixtures: list[dict[str, Any]]) -> tuple[int | None, str | None]:
    if not fixtures:
        return None, None
    fx = fixtures[0]
    league = fx.get("league") or {}
    try:
        lid = int(league.get("id") or 0) or None
    except (TypeError, ValueError):
        lid = None
    return lid, str(league.get("name") or "") or None


def _standing_row(standings: list[dict[str, Any]], team_id: int) -> dict[str, Any] | None:
    if not standings:
        return None
    try:
        groups = (standings[0].get("league") or {}).get("standings") or []
        rows = groups[0] if groups else []
        for row in rows:
            tid = (row.get("team") or {}).get("id")
            if int(tid) == int(team_id):
                return row
    except (TypeError, ValueError, IndexError):
        return None
    return None


def _goals_balance(matches: list[dict[str, Any]], team_id: int) -> tuple[int, int]:
    scored, conceded = 0, 0
    for fx in matches[:5]:
        goals = fx.get("goals") or {}
        try:
            gh, ga = int(goals.get("home")), int(goals.get("away"))
        except (TypeError, ValueError):
            continue
        hid = _team_id_from_fixture(fx, "home")
        aid = _team_id_from_fixture(fx, "away")
        if hid == team_id:
            scored += gh
            conceded += ga
        elif aid == team_id:
            scored += ga
            conceded += gh
    return scored, conceded


def _venue_record(matches: list[dict[str, Any]], team_id: int, *, home: bool) -> str:
    wins = draws = losses = 0
    for fx in matches[:5]:
        hid = _team_id_from_fixture(fx, "home")
        aid = _team_id_from_fixture(fx, "away")
        if home and hid != team_id:
            continue
        if not home and aid != team_id:
            continue
        ch = _match_result_char(fx, team_id)
        if ch == "W":
            wins += 1
        elif ch == "D":
            draws += 1
        elif ch == "L":
            losses += 1
    return f"{wins}W-{draws}D-{losses}L"


def _form_score_from_matches(team_last_matches: list[dict[str, Any]], team_id: int) -> float:
    """Weighted form score 0–100 from last five finished matches."""
    if not team_last_matches:
        return 50.0
    total_pts = 0.0
    max_pts = 0.0
    for i, fx in enumerate(team_last_matches[:5]):
        ch = _match_result_char(fx, team_id)
        if not ch:
            continue
        w = _FORM_WEIGHTS[i] if i < len(_FORM_WEIGHTS) else 0.5
        total_pts += _RESULT_POINTS.get(ch, 0.0) * w
        max_pts += 3.0 * w
    if max_pts <= 0:
        return 50.0
    return round((total_pts / max_pts) * 100.0, 1)


def calculate_form_score(
    team_id: int,
    team_last_matches: list[dict[str, Any]] | None = None,
    *,
    football_service: FootballService | None = None,
) -> float:
    """Form score 0–100 for a team (fetches recent matches when not supplied)."""
    if team_last_matches is None:
        svc = football_service or get_football_service()
        team_last_matches = svc.get_recent_fixtures(team_id, last_count=5)
    return _form_score_from_matches(team_last_matches, team_id)


def _confidence_from_features(features: dict[str, Any]) -> int:
    """Combine form, ranking, goals, and home advantage into 0–100 confidence."""
    home_form = float(features.get("home_form") or 50.0)
    away_form = float(features.get("away_form") or 50.0)
    form_gap = abs(home_form - away_form)

    score = 42.0 + min(28.0, form_gap * 0.55)

    home_rank = features.get("home_rank")
    away_rank = features.get("away_rank")
    if home_rank is not None and away_rank is not None:
        rank_gap = abs(int(home_rank) - int(away_rank))
        score += min(18.0, rank_gap * 1.8)

    home_adv = float(features.get("home_advantage_boost") or 0.0)
    score += home_adv

    goals_edge = float(features.get("goals_edge") or 0.0)
    score += min(12.0, goals_edge)

    if form_gap < 6.0:
        score -= 12.0
    if home_rank is None and away_rank is None:
        score -= 8.0

    return int(max(0, min(100, round(score))))


def calculate_confidence_score(
    home_score: float,
    away_score: float,
    *,
    home_rank: int | None = None,
    away_rank: int | None = None,
    home_advantage_boost: float = 6.0,
    goals_edge: float | None = None,
) -> int:
    """Confidence 0–100 from home/away form scores (optional rank and goals edge)."""
    if goals_edge is None:
        goals_edge = abs(home_score - away_score) * 0.08
    return _confidence_from_features(
        {
            "home_form": home_score,
            "away_form": away_score,
            "home_rank": home_rank,
            "away_rank": away_rank,
            "home_advantage_boost": home_advantage_boost,
            "goals_edge": goals_edge,
        }
    )


def determine_risk_level(confidence: int) -> RiskLevel:
    if confidence >= 70:
        return RiskLevel.LOW
    if confidence >= 55:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH


def _build_factors(match_data: MatchData, home_form: float, away_form: float) -> list[str]:
    factors: list[str] = []
    factors.append(f"{match_data.home_name} form score {home_form:.0f}/100")
    factors.append(f"{match_data.away_name} form score {away_form:.0f}/100")

    hs, hc = _goals_balance(match_data.home_matches, match_data.home_team_id)
    as_, ac = _goals_balance(match_data.away_matches, match_data.away_team_id)
    factors.append(f"Last 5 goals: {match_data.home_name} {hs}:{hc}, {match_data.away_name} {as_}:{ac}")

    home_rec = _venue_record(match_data.home_matches, match_data.home_team_id, home=True)
    away_rec = _venue_record(match_data.away_matches, match_data.away_team_id, home=False)
    factors.append(f"Home/Away split: {match_data.home_name} at home {home_rec}, {match_data.away_name} away {away_rec}")

    if match_data.home_standing and match_data.away_standing:
        hr = match_data.home_standing.get("rank")
        ar = match_data.away_standing.get("rank")
        if hr and ar:
            factors.append(f"Table: {match_data.home_name} #{hr} vs {match_data.away_name} #{ar}")
    return factors[:6]


def generate_tip(match_data: MatchData) -> TipResponse:
    """Produce winner prediction, confidence, risk, and suggested market."""
    home_form = _form_score_from_matches(match_data.home_matches, match_data.home_team_id)
    away_form = _form_score_from_matches(match_data.away_matches, match_data.away_team_id)

    home_rank = (match_data.home_standing or {}).get("rank")
    away_rank = (match_data.away_standing or {}).get("rank")
    hs, hc = _goals_balance(match_data.home_matches, match_data.home_team_id)
    as_, ac = _goals_balance(match_data.away_matches, match_data.away_team_id)
    home_gd = hs - hc
    away_gd = as_ - ac

    features = {
        "home_form": home_form,
        "away_form": away_form,
        "home_rank": home_rank,
        "away_rank": away_rank,
        "home_advantage_boost": 6.0,
        "goals_edge": abs(home_gd - away_gd) * 0.8,
    }
    confidence = _confidence_from_features(features)
    risk = determine_risk_level(confidence)
    factors = _build_factors(match_data, home_form, away_form)

    match_label = f"{match_data.home_name} vs {match_data.away_name}"
    form_delta = home_form - away_form
    rank_delta = 0
    if home_rank is not None and away_rank is not None:
        rank_delta = int(away_rank) - int(home_rank)

    if form_delta >= 8 or (form_delta >= 4 and rank_delta >= 3):
        prediction = f"{match_data.home_name} Win"
        suggested = (
            f"{match_data.home_name} Win"
            if confidence >= 68
            else f"{match_data.home_name} or Draw"
        )
    elif form_delta <= -8 or (form_delta <= -4 and rank_delta <= -3):
        prediction = f"{match_data.away_name} Win"
        suggested = (
            f"{match_data.away_name} Win"
            if confidence >= 68
            else f"Draw or {match_data.away_name}"
        )
    elif abs(form_delta) <= 5:
        prediction = "Draw"
        suggested = "Draw or Double Chance"
        confidence = max(40, confidence - 8)
        risk = determine_risk_level(confidence)
    elif form_delta > 0:
        prediction = f"{match_data.home_name} Win"
        suggested = f"{match_data.home_name} or Draw"
    else:
        prediction = f"{match_data.away_name} Win"
        suggested = f"Draw or {match_data.away_name}"

    return TipResponse(
        match=match_label,
        prediction=prediction,
        confidence=confidence,
        risk=risk,
        factors=factors,
        suggested_tip=suggested,
        home_team_id=match_data.home_team_id,
        away_team_id=match_data.away_team_id,
        fixture_id=match_data.fixture_id,
    )


class FootballAIService:
    """Deterministic match analysis using FootballService data only."""

    def __init__(self, football_service: FootballService | None = None) -> None:
        self._service = football_service or get_football_service()
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = int(get_settings().football_ai_cache_ttl)

    def _cache_get(self, key: str) -> Any | None:
        hit = self._cache.get(key)
        if not hit:
            return None
        if time.time() - hit[0] >= self._ttl:
            self._cache.pop(key, None)
            return None
        return hit[1]

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)

    def _load_match_bundle(
        self,
        home_id: int,
        away_id: int,
        *,
        fixture: dict[str, Any] | None = None,
    ) -> MatchData:
        home_matches = self._service.get_recent_fixtures(home_id, last_count=5)
        away_matches = self._service.get_recent_fixtures(away_id, last_count=5)

        home_name, away_name = f"Team {home_id}", f"Team {away_id}"
        if fixture:
            home_name = _team_name_from_fixture(fixture, "home", home_name)
            away_name = _team_name_from_fixture(fixture, "away", away_name)
        for fx in home_matches + away_matches:
            if _team_id_from_fixture(fx, "home") == home_id:
                home_name = _team_name_from_fixture(fx, "home", home_name)
            elif _team_id_from_fixture(fx, "away") == home_id:
                home_name = _team_name_from_fixture(fx, "away", home_name)
            if _team_id_from_fixture(fx, "home") == away_id:
                away_name = _team_name_from_fixture(fx, "home", away_name)
            elif _team_id_from_fixture(fx, "away") == away_id:
                away_name = _team_name_from_fixture(fx, "away", away_name)

        league_id, league_name = _infer_league_id(fixture and [fixture] or home_matches)
        home_standing = away_standing = None
        if league_id:
            try:
                standings = self._service.get_standings(int(league_id))
                home_standing = _standing_row(standings, home_id)
                away_standing = _standing_row(standings, away_id)
            except FootballAPIError as exc:
                log_warning(f"Standings unavailable for league {league_id}: {exc}")

        fixture_id = None
        if fixture:
            try:
                fixture_id = int((fixture.get("fixture") or {}).get("id") or 0) or None
            except (TypeError, ValueError):
                fixture_id = None

        return MatchData(
            home_team_id=home_id,
            away_team_id=away_id,
            home_name=home_name,
            away_name=away_name,
            home_matches=home_matches,
            away_matches=away_matches,
            home_standing=home_standing,
            away_standing=away_standing,
            league_id=league_id,
            league_name=league_name,
            fixture_id=fixture_id,
        )

    def analyze_match(self, home_team_id: int, away_team_id: int) -> MatchAnalysisResponse:
        """Full analysis for a head-to-head matchup."""
        cache_key = f"analysis:{home_team_id}:{away_team_id}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        if home_team_id == away_team_id:
            raise AnalysisError("Home and away team must differ.")

        bundle = self._load_match_bundle(home_team_id, away_team_id)
        if not bundle.home_matches and not bundle.away_matches:
            raise AnalysisError("Insufficient match history for both teams.")

        tip = generate_tip(bundle)
        result = MatchAnalysisResponse(
            **tip.model_dump(),
            home_form_score=_form_score_from_matches(bundle.home_matches, home_team_id),
            away_form_score=_form_score_from_matches(bundle.away_matches, away_team_id),
            home_rank=(bundle.home_standing or {}).get("rank"),
            away_rank=(bundle.away_standing or {}).get("rank"),
            league=bundle.league_name,
        )
        self._cache_set(cache_key, result)
        log_info(f"AI match analysis: {result.match} -> {result.prediction} ({result.confidence}%)")
        return result

    def tips_for_today(self) -> list[TipResponse]:
        """Analyze all scheduled fixtures for today (Europe/Berlin)."""
        today = datetime.now(_BERLIN_TZ).date().isoformat()
        cache_key = f"tips:today:{today}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        fixtures = self._service.get_fixtures_by_date(today)
        tips: list[TipResponse] = []
        for fx in fixtures:
            status = str(((fx.get("fixture") or {}).get("status") or {}).get("short") or "NS")
            if status not in ("NS", "TBD", "SCHEDULED", "TIMED"):
                continue
            home_id = _team_id_from_fixture(fx, "home")
            away_id = _team_id_from_fixture(fx, "away")
            if not home_id or not away_id:
                continue
            try:
                bundle = self._load_match_bundle(home_id, away_id, fixture=fx)
                tips.append(generate_tip(bundle))
            except (FootballAPIError, AnalysisError) as exc:
                log_warning(f"Skip fixture tip: {exc}")
                continue

        self._cache_set(cache_key, tips)
        return tips

    def tips_for_today_response(self) -> TipsTodayResponse:
        """Today's tips wrapped for the HTTP API."""
        tips = self.tips_for_today()
        today = datetime.now(_BERLIN_TZ).date().isoformat()
        return TipsTodayResponse(date=today, count=len(tips), tips=tips)

    def team_form(self, team_id: int) -> TeamFormResponse:
        """Form breakdown for a single team."""
        cache_key = f"form:{team_id}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        matches = self._service.get_recent_fixtures(team_id, last_count=5)
        if not matches:
            raise AnalysisError(f"No recent matches for team {team_id}.")

        team_name = f"Team {team_id}"
        for fx in matches:
            if _team_id_from_fixture(fx, "home") == team_id:
                team_name = _team_name_from_fixture(fx, "home", team_name)
                break
            if _team_id_from_fixture(fx, "away") == team_id:
                team_name = _team_name_from_fixture(fx, "away", team_name)
                break

        form_chars = [
            c for c in (_match_result_char(fx, team_id) for fx in matches[:5]) if c
        ]
        scored, conceded = _goals_balance(matches, team_id)
        league_id, league_name = _infer_league_id(matches)
        rank = None
        if league_id:
            try:
                standings = self._service.get_standings(int(league_id))
                row = _standing_row(standings, team_id)
                rank = (row or {}).get("rank")
            except FootballAPIError:
                pass

        result = TeamFormResponse(
            team_id=team_id,
            team_name=team_name,
            form_score=_form_score_from_matches(matches, team_id),
            last_matches=form_chars,
            goals_scored=scored,
            goals_conceded=conceded,
            home_record=_venue_record(matches, team_id, home=True),
            away_record=_venue_record(matches, team_id, home=False),
            rank=int(rank) if rank is not None else None,
            league=league_name,
        )
        self._cache_set(cache_key, result)
        return result


_ai_service: FootballAIService | None = None


def get_football_ai_service() -> FootballAIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = FootballAIService()
    return _ai_service
