"""Betting board — fixture rows with odds, win %, AI pick (reuse existing API layer)."""
from __future__ import annotations

from typing import Any

from config import FOOTBALL_LEAGUE_GROUPS, football_plan_rank
from services.football_betting_quality import (
    build_betting_signal,
    filter_bettable_fixtures,
    filter_rows_with_odds,
    has_complete_odds,
    log_fixture_data_sample,
)
from services.football_leagues import LIVE_STATUSES, filter_premium_fixtures
from services.football_match_center import (
    _local_today_tomorrow,
    dedupe_fixtures,
    fetch_premium_dashboard,
    parse_match_card,
    sort_fixtures_by_priority,
)
from services.football_odds import (
    get_odds_for_fixture,
    parse_prediction_insights,
)
from services.football_service import FootballAPIError, FootballService

_REGION_IDS: dict[str, frozenset[int]] = {
    "deutschland": frozenset(int(x["id"]) for x in FOOTBALL_LEAGUE_GROUPS.get("deutschland", [])),
    "uefa": frozenset({2, 3, 848, 5, 4, 32}),
    "topligen": frozenset(
        int(x["id"])
        for grp in ("europa_top",)
        for x in FOOTBALL_LEAGUE_GROUPS.get(grp, [])
    )
    | frozenset({39}),
}

# Strict UEFA: club + national team competitions only (no youth/reserve)
UEFA_COMPETITION_IDS: frozenset[int] = frozenset({2, 3, 848, 5, 4, 32})

_UEFA_NAME_KEYWORDS = (
    "uefa champions league",
    "uefa europa league",
    "uefa conference league",
    "uefa nations league",
    "euro championship",
    "world cup - qualification europe",
)


def is_uefa_competition(league: dict[str, Any] | None) -> bool:
    """Only official UEFA competitions — exclude youth, local cups, non-EU."""
    if not league:
        return False
    name = str(league.get("name") or "").lower().strip()
    country = str(league.get("country") or "").lower().strip()
    if any(x in name for x in ("u17", "u19", "u21", "youth", "women", "frauen")):
        return False
    try:
        lid = int(league.get("id") or 0)
    except (TypeError, ValueError):
        lid = 0
    if lid in UEFA_COMPETITION_IDS:
        return True
    if not name:
        return False
    if "uefa" in name:
        return any(kw in name for kw in _UEFA_NAME_KEYWORDS) or (
            "champions league" in name
            or "europa league" in name
            or "conference league" in name
            or "nations league" in name
        )
    if country == "europe" and name in (
        "champions league",
        "europa league",
        "conference league",
    ):
        return True
    if "world cup" in name and "qualification" in name and country in ("europe", "world"):
        return True
    return False


def filter_fixtures_by_region(
    fixtures: list[dict[str, Any]],
    region_filter: str,
) -> list[dict[str, Any]]:
    region = (region_filter or "alle").lower().strip()
    if region in ("alle", "all", ""):
        return list(fixtures or [])

    if region == "uefa":
        return [
            fx
            for fx in fixtures or []
            if is_uefa_competition(fx.get("league") or {})
        ]

    region_ids = league_group_ids(region)
    if region_ids is not None:
        return [
            fx
            for fx in fixtures or []
            if int((fx.get("league") or {}).get("id") or 0) in region_ids
        ]
    return list(fixtures or [])


def region_filter_label(region_filter: str) -> str:
    region = (region_filter or "alle").lower().strip()
    labels = {
        "uefa": "UEFA Wettbewerbe",
        "deutschland": "Deutsche Wettbewerbe",
        "topligen": "Topligen",
        "alle": "Premium-Spiele",
    }
    return labels.get(region, labels["alle"])


def fixture_league_debug_info(fixture: dict[str, Any]) -> dict[str, Any]:
    league = fixture.get("league") or {}
    teams = fixture.get("teams") or {}
    home = (teams.get("home") or {}).get("name") or "?"
    away = (teams.get("away") or {}).get("name") or "?"
    return {
        "match": f"{home} vs {away}",
        "league_id": league.get("id"),
        "league_name": league.get("name"),
        "country": league.get("country"),
    }


def log_displayed_fixtures(
    fixtures: list[dict[str, Any]],
    *,
    region_filter: str,
) -> None:
    region = (region_filter or "alle").lower()
    print(
        {
            "board_fixtures_debug": {
                "count": len(fixtures or []),
                "region": region,
                "league_names": [
                    str((fx.get("league") or {}).get("name") or "?")
                    for fx in (fixtures or [])
                ],
            }
        }
    )
    for fx in fixtures or []:
        print(fixture_league_debug_info(fx))


def league_group_ids(region: str) -> frozenset[int] | None:
    if region in ("alle", "", "all"):
        return None
    return _REGION_IDS.get(region)


def fetch_board_payload(
    service: FootballService,
    *,
    username: str,
    include_all_leagues: bool = False,
) -> dict[str, Any]:
    payload = fetch_premium_dashboard(
        service, username=username, include_all_leagues=include_all_leagues
    )
    if "tomorrow_fixtures" not in payload:
        _today_s, tomorrow_s = _local_today_tomorrow()
        try:
            tomorrow_rows = service.get_fixtures_by_date(tomorrow_s, username=username)
            payload["tomorrow_fixtures"] = sort_fixtures_by_priority(
                filter_bettable_fixtures(
                    filter_premium_fixtures(dedupe_fixtures(tomorrow_rows))
                )
            )
        except FootballAPIError:
            payload["tomorrow_fixtures"] = []
    return payload


def _fixture_date(fixture: dict[str, Any]) -> str:
    return parse_match_card(fixture).get("date") or ""


def _is_live(fixture: dict[str, Any]) -> bool:
    st = str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "")
    return st in LIVE_STATUSES


def collect_fixtures_for_filters(
    payload: dict[str, Any],
    *,
    time_filter: str,
    region_filter: str,
) -> list[dict[str, Any]]:
    """Premium fixtures only — strict ID whitelist + region filter."""
    today_s = str(payload.get("today") or payload.get("today_local") or "")

    if time_filter == "live":
        pool = list(payload.get("live_now") or [])
    elif time_filter == "morgen":
        pool = list(payload.get("tomorrow_fixtures") or [])
    elif time_filter == "alle":
        pool = dedupe_fixtures(
            list(payload.get("live_now") or [])
            + list(payload.get("all_premium") or [])
            + list(payload.get("tomorrow_fixtures") or [])
            + list(payload.get("next_matches") or [])
        )
    else:
        pool = dedupe_fixtures(
            list(payload.get("live_now") or [])
            + list(payload.get("all_premium") or [])
            + list(payload.get("next_matches") or [])
        )
        if time_filter == "heute":
            pool = [
                fx
                for fx in pool
                if _is_live(fx) or _fixture_date(fx) == today_s
            ]

    pool = filter_bettable_fixtures(pool)
    pool = filter_fixtures_by_region(pool, region_filter)
    return sort_fixtures_by_priority(pool)


def enrich_fixture_row(
    service: FootballService,
    fixture: dict[str, Any],
    *,
    username: str,
    rank: int,
    cache: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    card = parse_match_card(fixture)
    fid = card.get("fixture_id")
    try:
        fid_int = int(fid) if fid is not None else None
    except (TypeError, ValueError):
        fid_int = None

    if fid_int and fid_int in cache:
        return cache[fid_int]

    row: dict[str, Any] = {
        "fixture_id": fid_int,
        "card": card,
        "home_odd": None,
        "draw_odd": None,
        "away_odd": None,
        "home_pct": None,
        "draw_pct": None,
        "away_pct": None,
        "ai_pick": "No Bet",
        "confidence": None,
        "risk": "Hoch",
        "no_bet": True,
        "value": False,
        "live_event": "",
        "momentum": "",
        "reasons": [],
        "has_odds": False,
    }

    pred_insights: dict[str, Any] = {}

    if rank >= 2 and fid_int:
        try:
            pred_rows = service.get_fixture_predictions(fid_int, username=username)
            if pred_rows:
                pred_insights = parse_prediction_insights(pred_rows[0])
        except FootballAPIError:
            pass

        o1x2 = get_odds_for_fixture(service, fid_int, username=username)
        row["home_odd"] = o1x2["home"]
        row["draw_odd"] = o1x2["draw"]
        row["away_odd"] = o1x2["away"]
        row["has_odds"] = has_complete_odds(row)

    signal = build_betting_signal(
        home=str(card.get("home") or "Heim"),
        away=str(card.get("away") or "Auswärts"),
        home_odd=row["home_odd"],
        draw_odd=row["draw_odd"],
        away_odd=row["away_odd"],
        pred_insights=pred_insights,
        is_live=bool(card.get("live")),
    )
    row.update(signal)

    if card.get("live"):
        rc = card.get("red_cards") or {}
        if isinstance(rc, dict) and rc.get("total"):
            row["live_event"] = f"Rote Karten: {rc.get('total')}"
        if card.get("live_xg"):
            row["momentum"] = f"xG {card.get('live_xg')}"

    if fid_int:
        cache[fid_int] = row
    return row


def build_board_rows(
    fixtures: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 24,
    allow_no_odds: bool = False,
) -> list[dict[str, Any]]:
    rank = football_plan_rank(session_plan or "none")
    if rank < 2:
        return []

    rows: list[dict[str, Any]] = []
    for fx in fixtures[:max_enrich]:
        rows.append(
            enrich_fixture_row(
                service, fx, username=username, rank=rank, cache=cache
            )
        )
    return filter_rows_with_odds(rows, allow_no_odds=allow_no_odds)
