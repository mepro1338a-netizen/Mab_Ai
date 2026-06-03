"""
Football feed — strict Topspiele (league ID whitelist) vs Alle API-Spiele (raw).
No curated fallback into Topspiele. No fake analysis signals.
"""
from __future__ import annotations

from typing import Any

from config import FOOTBALL_TOPSPIELE_LEAGUE_IDS, football_plan_rank
from services.football_board import (
    fetch_match_detail,
    get_odds_for_fixture,
    has_complete_odds,
    parse_prediction_insights,
)
from services.football_loaders import (
    LIVE_STATUSES,
    dedupe_fixtures,
    filter_blocked_fixtures,
    parse_match_card,
    sort_fixtures_by_priority,
)
from services.football_service import FootballAPIError, FootballService

TOPSPIELE_CAP = 10
ALL_API_CAP = 50

MSG_TOP_EMPTY = "Heute keine Topspiele verfügbar."
MSG_TOP_EMPTY_LIVE = "Keine Live-Topspiele verfügbar."
MSG_TOP_EMPTY_TOMORROW = "Morgen keine Topspiele verfügbar."
MSG_ALL_API_LABEL = "Alle API-Spiele (max. 50) — inkl. untergeordnete Ligen."


def _league_id(fixture: dict[str, Any]) -> int | None:
    try:
        return int((fixture.get("league") or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def is_topspiele_fixture(fixture: dict[str, Any]) -> bool:
    lid = _league_id(fixture)
    return bool(lid and lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS)


def filter_topspiele_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [fx for fx in fixtures or [] if is_topspiele_fixture(fx)]


def _fixture_date(fixture: dict[str, Any]) -> str:
    return parse_match_card(fixture).get("date") or ""


def _is_live(fixture: dict[str, Any]) -> bool:
    st = str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "")
    return st in LIVE_STATUSES


def _topspiele_empty_message(time_filter: str) -> str:
    tf = (time_filter or "heute").lower()
    if tf == "morgen":
        return MSG_TOP_EMPTY_TOMORROW
    if tf == "live":
        return MSG_TOP_EMPTY_LIVE
    return MSG_TOP_EMPTY


def _all_api_sort_key(fixture: dict[str, Any]) -> tuple:
    lid = _league_id(fixture) or 0
    in_top = 0 if lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS else 1
    tier_penalty = 0 if in_top == 0 else 1
    return (in_top, tier_penalty, str((fixture.get("fixture") or {}).get("date") or ""))


def _pool_for_time(payload: dict[str, Any], time_filter: str, *, raw_only: bool) -> list[dict[str, Any]]:
    today_s = str(payload.get("today") or payload.get("today_local") or "")
    tf = (time_filter or "heute").lower()

    if raw_only:
        raw_live = list(payload.get("raw_live") or [])
        raw_today = list(payload.get("raw_today") or [])
        raw_tomorrow = list(payload.get("raw_tomorrow") or [])
        if tf == "live":
            pool = raw_live
        elif tf == "morgen":
            pool = raw_tomorrow
        else:
            pool = dedupe_fixtures(raw_live + raw_today)
            if tf == "heute":
                pool = [fx for fx in pool if _is_live(fx) or _fixture_date(fx) == today_s]
        return filter_blocked_fixtures(pool)

    raw_live = list(payload.get("raw_live") or [])
    raw_today = list(payload.get("raw_today") or [])
    raw_tomorrow = list(payload.get("raw_tomorrow") or [])
    upcoming = list(payload.get("next_matches") or payload.get("all_premium") or [])

    if tf == "live":
        pool = dedupe_fixtures(raw_live + list(payload.get("live_now") or []))
    elif tf == "morgen":
        pool = dedupe_fixtures(raw_tomorrow + list(payload.get("tomorrow_fixtures") or []))
    else:
        pool = dedupe_fixtures(raw_live + raw_today + upcoming)
        if tf == "heute":
            pool = [fx for fx in pool if _is_live(fx) or _fixture_date(fx) == today_s]

    return pool


def build_row(fixture: dict[str, Any], *, raw_mode: bool = False) -> dict[str, Any]:
    card = parse_match_card(fixture)
    fid = card.get("fixture_id")
    try:
        fid_int = int(fid) if fid is not None else None
    except (TypeError, ValueError):
        fid_int = None
    return {
        "fixture_id": fid_int,
        "card": card,
        "raw_mode": raw_mode,
        "schedule_only": True,
        "analysis_available": False,
        "has_odds": False,
        "has_predictions": False,
    }


def probe_analysis_available(
    service: FootballService,
    fixture_id: int,
    *,
    username: str,
    session_plan: str,
) -> tuple[bool, bool]:
    """Return (has_odds, has_predictions) — real API only."""
    rank = football_plan_rank(session_plan or "none")
    has_odds = False
    has_pred = False
    if rank < 1 or not fixture_id:
        return has_odds, has_pred

    try:
        o1x2 = get_odds_for_fixture(service, int(fixture_id), username=username)
        has_odds = has_complete_odds(
            {
                "home_odd": o1x2.get("home"),
                "draw_odd": o1x2.get("draw"),
                "away_odd": o1x2.get("away"),
            }
        )
    except FootballAPIError:
        pass

    if rank >= 2:
        try:
            rows = service.get_fixture_predictions(int(fixture_id), username=username)
            if rows:
                ins = parse_prediction_insights(rows[0])
                has_pred = ins.get("home_pct") is not None or bool(ins.get("advice"))
        except FootballAPIError:
            pass

    return has_odds, has_pred


def enrich_rows_analysis_flags(
    rows: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    max_probe: int = 10,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    probed = 0
    for row in rows:
        r = dict(row)
        fid = r.get("fixture_id")
        if fid and probed < max_probe:
            has_odds, has_pred = probe_analysis_available(
                service, int(fid), username=username, session_plan=session_plan
            )
            r["has_odds"] = has_odds
            r["has_predictions"] = has_pred
            r["analysis_available"] = has_odds or has_pred
            probed += 1
        else:
            r["has_odds"] = False
            r["has_predictions"] = False
            r["analysis_available"] = False
        out.append(r)
    return out


def resolve_topspiele_board(
    payload: dict[str, Any],
    *,
    time_filter: str,
) -> dict[str, Any]:
    pool = _pool_for_time(payload, time_filter, raw_only=False)
    fixtures = filter_topspiele_fixtures(pool)
    fixtures = sort_fixtures_by_priority(fixtures)[:TOPSPIELE_CAP]
    rows = [build_row(fx, raw_mode=False) for fx in fixtures]
    banner = _topspiele_empty_message(time_filter) if not rows else None
    return {
        "rows": rows,
        "banner": banner,
        "source": "topspiele",
        "raw_mode": False,
        "displayed_topspiele_count": len(rows),
        "displayed_allspiele_count": 0,
        "metrics": {
            "topspiele_pool": len(filter_topspiele_fixtures(pool)),
            "displayed_count": len(rows),
            "view_mode": "premium",
            "time_filter": time_filter,
        },
    }


def resolve_all_api_board(
    payload: dict[str, Any],
    *,
    time_filter: str,
) -> dict[str, Any]:
    pool = _pool_for_time(payload, time_filter, raw_only=True)
    pool = sorted(pool, key=_all_api_sort_key)
    fixtures = pool[:ALL_API_CAP]
    rows = [build_row(fx, raw_mode=True) for fx in fixtures]
    return {
        "rows": rows,
        "banner": MSG_ALL_API_LABEL if rows else "Aktuell keine API-Spiele für diesen Zeitraum.",
        "source": "raw",
        "raw_mode": True,
        "displayed_topspiele_count": 0,
        "displayed_allspiele_count": len(rows),
        "metrics": {
            "raw_pool": len(pool),
            "displayed_count": len(rows),
            "view_mode": "raw",
            "time_filter": time_filter,
        },
    }


def resolve_football_feed(
    payload: dict[str, Any],
    service: FootballService,
    *,
    view_mode: str,
    time_filter: str,
    username: str,
    session_plan: str,
    probe_analysis: bool = True,
) -> dict[str, Any]:
    vm = "raw" if str(view_mode).lower() == "raw" else "premium"
    if vm == "raw":
        result = resolve_all_api_board(payload, time_filter=time_filter)
    else:
        result = resolve_topspiele_board(payload, time_filter=time_filter)

    rows = result.get("rows") or []
    if probe_analysis and vm == "premium" and rows:
        rows = enrich_rows_analysis_flags(
            rows, service, username=username, session_plan=session_plan
        )
        result["rows"] = rows

    return result


def fetch_board_payload(
    service: FootballService,
    *,
    username: str,
    time_filter: str,
) -> dict[str, Any]:
    """Always load raw + live so Topspiele can filter by league ID reliably."""
    from services.football_loaders import fetch_premium_dashboard

    tf = (time_filter or "heute").lower()
    return fetch_premium_dashboard(
        service,
        username=username,
        include_live=True,
        include_raw=True,
    )
