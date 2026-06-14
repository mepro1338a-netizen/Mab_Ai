"""SportMonks Football API v3 client — raw HTTP plus mapper to API-Football shape.

Maps SportMonks fixtures into the fixture/teams/goals/league dict shape expected by
services.football_loaders and services.football_feed so downstream consumers stay
untouched.
"""
from __future__ import annotations

import time
from typing import Any

import requests

from config import SPORTMONKS_LEAGUE_ID_TO_INTERNAL
from core.config import (
    FOOTBALL_API_INCLUDE,
    FOOTBALL_DATA_TIMEOUT,
    SPORTMONKS_BASE_URL,
    get_sportmonks_api_key,
)
from logger import log_error, log_warning

_SM_BASE_URL = "https://api.sportmonks.com/v3/football"
_MAX_RETRIES = 2
_MAX_PAGES = 8


class SportMonksError(Exception):
    """Raised when SportMonks returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def is_sm_configured() -> bool:
    return bool(get_sportmonks_api_key())


def _transient_status(status_code: int) -> bool:
    return status_code == 429 or status_code >= 500


def _default_include() -> str:
    return FOOTBALL_API_INCLUDE or (
        "participants;scores;periods;events;league.country;round"
    )


def _request_once(
    url: str,
    params: dict[str, Any],
) -> requests.Response:
    return requests.get(url, params=params, timeout=FOOTBALL_DATA_TIMEOUT)


def sm_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET against SportMonks Football API v3 (auth via api_token query param)."""
    api_key = get_sportmonks_api_key()
    if not api_key:
        raise SportMonksError(
            "SportMonks API-Key fehlt (SPORTMONKS_API_KEY in Railway/.env)."
        )
    base = (SPORTMONKS_BASE_URL or _SM_BASE_URL).rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    query: dict[str, Any] = {"api_token": api_key}
    include = _default_include()
    if include:
        query["include"] = include
    if params:
        query.update(params)

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = _request_once(url, query)
        except requests.Timeout as exc:
            log_warning(
                f"sportmonks timeout (attempt {attempt + 1}/{_MAX_RETRIES + 1}): {path}"
            )
            if attempt < _MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            log_error(f"sportmonks timeout: {path}")
            raise SportMonksError("Spieldaten-API Timeout. Bitte erneut versuchen.") from exc
        except requests.RequestException as exc:
            log_error(f"sportmonks network error: {path} -> {exc}")
            raise SportMonksError("Spieldaten-API Netzwerkfehler.") from exc

        status = response.status_code
        if _transient_status(status):
            log_warning(
                f"sportmonks transient HTTP {status} "
                f"(attempt {attempt + 1}/{_MAX_RETRIES + 1}): {path}"
            )
            if attempt < _MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            if status == 429:
                raise SportMonksError(
                    "Spieldaten-API Rate Limit erreicht. Bitte kurz warten.",
                    status_code=429,
                )
            raise SportMonksError(
                f"Spieldaten-API HTTP {status}",
                status_code=status,
            )

        if status in (401, 403):
            log_warning(f"sportmonks auth/plan error {status}: {path}")
            raise SportMonksError(
                "Spieldaten-API: Zugriff verweigert (Key oder Plan pruefen).",
                status_code=status,
            )
        if status >= 400:
            raise SportMonksError(
                f"Spieldaten-API HTTP {status}",
                status_code=status,
            )
        try:
            return response.json() or {}
        except ValueError as exc:
            raise SportMonksError("Ungueltige Spieldaten-API Antwort.") from exc

    raise SportMonksError("Spieldaten-API Anfrage fehlgeschlagen.")


def sm_get_all(path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Paginate SportMonks list endpoints (data array + pagination.has_more)."""
    rows: list[dict[str, Any]] = []
    page_params = dict(params or {})
    page_params.setdefault("per_page", 50)

    for _ in range(_MAX_PAGES):
        payload = sm_get(path, page_params)
        chunk = payload.get("data") or []
        if isinstance(chunk, dict):
            return [chunk]
        if isinstance(chunk, list):
            rows.extend(item for item in chunk if isinstance(item, dict))
        pagination = payload.get("pagination") or {}
        if not pagination.get("has_more"):
            break
        page_params["page"] = int(pagination.get("current_page") or 1) + 1
    return rows


# SportMonks state_id -> API-Football short status codes used by parse_match_card.
_STATE_MAP = {
    1: "NS",    # Not Started
    2: "LIVE",  # 1st Half
    3: "HT",    # Half Time
    4: "HT",    # Break
    5: "FT",    # Full Time
    6: "ET",    # Extra Time
    7: "AET",   # After Extra Time
    8: "PEN",   # Full Time after penalties
    9: "P",     # Penalty Shootout
    10: "PST",  # Postponed
    11: "INT",  # Suspended
    12: "CANC", # Cancelled
    17: "AWD",  # Awarded
    22: "LIVE", # 2nd Half
    23: "ET",   # ET in play
    24: "P",    # Penalties in play
}


def _score_by_description(scores: list[dict[str, Any]], description: str) -> dict[str, int | None]:
    home: int | None = None
    away: int | None = None
    for row in scores or []:
        if str(row.get("description") or "").upper() != description.upper():
            continue
        participant = str((row.get("score") or {}).get("participant") or "").lower()
        goals = (row.get("score") or {}).get("goals")
        try:
            val = int(goals) if goals is not None else None
        except (TypeError, ValueError):
            val = None
        if participant == "home":
            home = val
        elif participant == "away":
            away = val
    return {"home": home, "away": away}


def _participants(fixture: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    home: dict[str, Any] = {}
    away: dict[str, Any] = {}
    for team in fixture.get("participants") or []:
        if not isinstance(team, dict):
            continue
        meta = team.get("meta") or {}
        loc = str(meta.get("location") or "").lower()
        block = {
            "id": team.get("id"),
            "name": team.get("short_code") or team.get("name") or "",
            "logo": team.get("image_path") or "",
            "winner": meta.get("winner"),
        }
        if loc == "home":
            home = block
        elif loc == "away":
            away = block
    if not home and not away and len(fixture.get("participants") or []) >= 2:
        parts = fixture.get("participants") or []
        home = {
            "id": parts[0].get("id"),
            "name": parts[0].get("short_code") or parts[0].get("name") or "",
            "logo": parts[0].get("image_path") or "",
            "winner": (parts[0].get("meta") or {}).get("winner"),
        }
        away = {
            "id": parts[1].get("id"),
            "name": parts[1].get("short_code") or parts[1].get("name") or "",
            "logo": parts[1].get("image_path") or "",
            "winner": (parts[1].get("meta") or {}).get("winner"),
        }
    return home, away


def _internal_league_id(sm_league_id: int | None) -> int | None:
    if sm_league_id is None:
        return None
    return SPORTMONKS_LEAGUE_ID_TO_INTERNAL.get(int(sm_league_id), int(sm_league_id))


def _iso_date(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    if "T" in text:
        return text if text.endswith("Z") else f"{text}Z"
    return f"{text.replace(' ', 'T')}Z"


def _elapsed(fixture: dict[str, Any]) -> int | None:
    for period in fixture.get("periods") or []:
        if not isinstance(period, dict):
            continue
        if period.get("ticking"):
            try:
                return int(period.get("minutes"))
            except (TypeError, ValueError):
                return None
    return None


def map_sm_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    """Map one SportMonks fixture into the API-Football fixture shape."""
    league = fixture.get("league") or {}
    country = league.get("country") or {}
    rnd = fixture.get("round") or {}
    scores = fixture.get("scores") or []
    full_time = _score_by_description(scores, "CURRENT")
    half_time = _score_by_description(scores, "1ST_HALF")
    home, away = _participants(fixture)

    try:
        state_id = int(fixture.get("state_id") or 1)
    except (TypeError, ValueError):
        state_id = 1
    status_short = _STATE_MAP.get(state_id, "NS")

    sm_league_id = league.get("id") or fixture.get("league_id")
    league_id = _internal_league_id(
        int(sm_league_id) if sm_league_id is not None else None
    )

    starting_at = str(fixture.get("starting_at") or "")
    season_year: int | None = None
    if starting_at:
        try:
            season_year = int(starting_at[:4])
        except (TypeError, ValueError):
            season_year = None

    return {
        "fixture": {
            "id": fixture.get("id"),
            "date": _iso_date(starting_at),
            "timezone": "UTC",
            "status": {
                "short": status_short,
                "long": status_short,
                "elapsed": _elapsed(fixture),
            },
            "venue": {"name": "", "city": ""},
        },
        "teams": {"home": home, "away": away},
        "goals": full_time,
        "score": {
            "halftime": half_time,
            "fulltime": full_time,
        },
        "league": {
            "id": league_id,
            "name": league.get("name") or "",
            "country": country.get("name") or "",
            "logo": league.get("image_path") or "",
            "season": season_year,
            "round": str(rnd.get("name") or ""),
        },
    }


def map_sm_fixtures(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [map_sm_fixture(row) for row in (rows or []) if isinstance(row, dict)]


def map_sm_standings(
    rows: list[dict[str, Any]] | None,
    league_id: int,
    *,
    league_meta: dict[str, Any] | None = None,
    participants: dict[int, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map SportMonks standings rows into the API-Football standings response shape."""
    league_meta = league_meta or {}
    participants = participants or {}
    table: list[dict[str, Any]] = []

    for row in rows or []:
        if not isinstance(row, dict):
            continue
        pid = row.get("participant_id")
        team = participants.get(int(pid)) if pid is not None else {}
        team = team or {}
        details = {d.get("type_id"): d for d in (row.get("details") or []) if isinstance(d, dict)}

        def _detail(type_id: int, default: int = 0) -> int:
            val = (details.get(type_id) or {}).get("value")
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        played = _detail(129)
        wins = _detail(130)
        draws = _detail(131)
        losses = _detail(132)
        goals_for = _detail(133)
        goals_against = _detail(134)

        table.append({
            "rank": row.get("position"),
            "team": {
                "id": team.get("id") or pid,
                "name": team.get("short_code") or team.get("name") or "",
                "logo": team.get("image_path") or "",
            },
            "points": row.get("points"),
            "goalsDiff": goals_for - goals_against if played else None,
            "form": "",
            "all": {
                "played": played,
                "win": wins,
                "draw": draws,
                "lose": losses,
                "goals": {"for": goals_for, "against": goals_against},
            },
        })

    if not table:
        return []
    country = (league_meta.get("country") or {}) if isinstance(league_meta.get("country"), dict) else {}
    return [{
        "league": {
            "id": int(league_id),
            "name": league_meta.get("name") or "",
            "country": country.get("name") or "",
            "logo": league_meta.get("image_path") or "",
            "season": None,
            "standings": [table],
        },
    }]


__all__ = [
    "SportMonksError",
    "is_sm_configured",
    "map_sm_fixture",
    "map_sm_fixtures",
    "map_sm_standings",
    "sm_get",
    "sm_get_all",
]
