"""football-data.org v4 client — raw HTTP plus mapper to API-Football shape.

Free-tier source for fixtures and standings. The mapper translates
football-data.org matches into the API-Football fixture dict shape
(fixture/teams/goals/league) expected by services.football_loaders and
services.football_feed, so all downstream consumers stay untouched.

Premium signals (odds, predictions, injuries, h2h) have no source here and
remain on the legacy API-Football path in services.football_service.
"""
from __future__ import annotations

from typing import Any

import requests

from config import (
    FOOTBALL_DATA_API_KEY,
    FOOTBALL_DATA_BASE_URL,
    FOOTBALL_DATA_ID_TO_LEAGUE_ID,
    FOOTBALL_DATA_TIMEOUT,
)
from logger import log_error, log_warning


class FootballDataError(Exception):
    """Raised when football-data.org returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def is_fd_configured() -> bool:
    return bool(FOOTBALL_DATA_API_KEY.strip())


def fd_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET against football-data.org v4 (auth via X-Auth-Token header)."""
    if not is_fd_configured():
        raise FootballDataError(
            "football-data.org Key fehlt (FOOTBALL_DATA_API_KEY in Railway/.env)."
        )
    url = f"{FOOTBALL_DATA_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "X-Auth-Token": FOOTBALL_DATA_API_KEY.strip(),
        "Accept": "application/json",
    }
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params or {},
            timeout=FOOTBALL_DATA_TIMEOUT,
        )
    except requests.Timeout as exc:
        log_error(f"football-data timeout: {path}")
        raise FootballDataError("Spieldaten-API Timeout. Bitte erneut versuchen.") from exc
    except requests.RequestException as exc:
        log_error(f"football-data network error: {path} -> {exc}")
        raise FootballDataError("Spieldaten-API Netzwerkfehler.") from exc

    if response.status_code == 429:
        log_warning(f"football-data rate limit (10/min): {path}")
        raise FootballDataError(
            "Spieldaten-API Rate Limit erreicht. Bitte kurz warten.",
            status_code=429,
        )
    if response.status_code in (401, 403):
        log_warning(f"football-data auth/plan error {response.status_code}: {path}")
        raise FootballDataError(
            "Spieldaten-API: Zugriff verweigert (Key oder Free-Tier-Plan pruefen).",
            status_code=response.status_code,
        )
    if response.status_code >= 400:
        raise FootballDataError(
            f"Spieldaten-API HTTP {response.status_code}",
            status_code=response.status_code,
        )
    try:
        return response.json() or {}
    except ValueError as exc:
        raise FootballDataError("Ungueltige Spieldaten-API Antwort.") from exc


# football-data.org status -> API-Football short codes used by parse_match_card.
_STATUS_MAP = {
    "SCHEDULED": "NS",
    "TIMED": "NS",
    "IN_PLAY": "LIVE",
    "PAUSED": "HT",
    "EXTRA_TIME": "ET",
    "PENALTY_SHOOTOUT": "P",
    "FINISHED": "FT",
    "SUSPENDED": "INT",
    "POSTPONED": "PST",
    "CANCELLED": "CANC",
    "AWARDED": "AWD",
}


def _team_block(team: dict[str, Any] | None) -> dict[str, Any]:
    team = team or {}
    return {
        "id": team.get("id"),
        "name": team.get("shortName") or team.get("name") or "",
        "logo": team.get("crest") or "",
        "winner": None,
    }


def map_fd_match(match: dict[str, Any]) -> dict[str, Any]:
    """Map one football-data.org match into the API-Football fixture shape."""
    comp = match.get("competition") or {}
    area = match.get("area") or {}
    score = match.get("score") or {}
    full_time = score.get("fullTime") or {}
    season = match.get("season") or {}
    status_raw = str(match.get("status") or "SCHEDULED").upper()

    try:
        season_year: int | None = int(str(season.get("startDate") or "")[:4])
    except (TypeError, ValueError):
        season_year = None
    try:
        fd_comp_id = int(comp.get("id") or 0)
    except (TypeError, ValueError):
        fd_comp_id = 0
    # Keep API-Football numeric league IDs alive for all downstream filters.
    league_id = FOOTBALL_DATA_ID_TO_LEAGUE_ID.get(fd_comp_id, fd_comp_id or None)

    home = _team_block(match.get("homeTeam"))
    away = _team_block(match.get("awayTeam"))
    winner = score.get("winner")
    if winner == "HOME_TEAM":
        home["winner"], away["winner"] = True, False
    elif winner == "AWAY_TEAM":
        home["winner"], away["winner"] = False, True
    elif winner == "DRAW":
        home["winner"] = away["winner"] = False

    try:
        elapsed: int | None = int(match.get("minute"))
    except (TypeError, ValueError):
        elapsed = None

    matchday = match.get("matchday")
    round_label = f"Matchday {matchday}" if matchday else str(match.get("stage") or "")

    return {
        "fixture": {
            "id": match.get("id"),
            "date": str(match.get("utcDate") or ""),
            "timezone": "UTC",
            "status": {
                "short": _STATUS_MAP.get(status_raw, "NS"),
                "long": status_raw.replace("_", " ").title(),
                "elapsed": elapsed,
            },
            "venue": {"name": str(match.get("venue") or ""), "city": ""},
        },
        "teams": {"home": home, "away": away},
        "goals": {"home": full_time.get("home"), "away": full_time.get("away")},
        "score": {
            "halftime": score.get("halfTime") or {},
            "fulltime": full_time,
        },
        "league": {
            "id": league_id,
            "name": comp.get("name") or "",
            "country": area.get("name") or "",
            "logo": comp.get("emblem") or "",
            "season": season_year,
            "round": round_label,
        },
    }


def map_fd_matches(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows = (payload or {}).get("matches") or []
    return [map_fd_match(m) for m in rows if isinstance(m, dict)]


def map_fd_standings(payload: dict[str, Any] | None, league_id: int) -> list[dict[str, Any]]:
    """Map a standings payload into the API-Football standings response shape."""
    payload = payload or {}
    comp = payload.get("competition") or {}
    season = payload.get("season") or {}
    try:
        season_year: int | None = int(str(season.get("startDate") or "")[:4])
    except (TypeError, ValueError):
        season_year = None

    groups: list[list[dict[str, Any]]] = []
    for block in payload.get("standings") or []:
        if str(block.get("type") or "").upper() != "TOTAL":
            continue
        rows: list[dict[str, Any]] = []
        for row in block.get("table") or []:
            team = row.get("team") or {}
            rows.append({
                "rank": row.get("position"),
                "team": {
                    "id": team.get("id"),
                    "name": team.get("shortName") or team.get("name") or "",
                    "logo": team.get("crest") or "",
                },
                "points": row.get("points"),
                "goalsDiff": row.get("goalDifference"),
                "form": str(row.get("form") or ""),
                "all": {
                    "played": row.get("playedGames"),
                    "win": row.get("won"),
                    "draw": row.get("draw"),
                    "lose": row.get("lost"),
                    "goals": {
                        "for": row.get("goalsFor"),
                        "against": row.get("goalsAgainst"),
                    },
                },
            })
        if rows:
            groups.append(rows)

    if not groups:
        return []
    return [{
        "league": {
            "id": int(league_id),
            "name": comp.get("name") or "",
            "country": (payload.get("area") or {}).get("name") or "",
            "logo": comp.get("emblem") or "",
            "season": season_year,
            "standings": groups,
        },
    }]


__all__ = [
    "FootballDataError",
    "fd_get",
    "is_fd_configured",
    "map_fd_match",
    "map_fd_matches",
    "map_fd_standings",
]
