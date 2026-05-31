"""Betting board — fixture rows with odds, win %, AI pick (reuse existing API layer)."""
from __future__ import annotations

from typing import Any

from config import FOOTBALL_LEAGUE_GROUPS, football_plan_rank
from services.football_leagues import (
    LIVE_STATUSES,
    filter_blocked_fixtures,
    filter_premium_fixtures,
)
from services.football_match_center import (
    _local_today_tomorrow,
    dedupe_fixtures,
    fetch_premium_dashboard,
    parse_match_card,
    sort_fixtures_by_priority,
)
from services.football_odds import parse_fixture_odds_payload, parse_prediction_insights
from services.football_prediction_engine import build_match_prediction
from services.football_service import FootballAPIError, FootballService

_REGION_IDS: dict[str, frozenset[int]] = {
    "deutschland": frozenset(int(x["id"]) for x in FOOTBALL_LEAGUE_GROUPS.get("deutschland", [])),
    "uefa": frozenset(int(x["id"]) for x in FOOTBALL_LEAGUE_GROUPS.get("uefa", [])),
    "topligen": frozenset(
        int(x["id"])
        for grp in ("europa_top",)
        for x in FOOTBALL_LEAGUE_GROUPS.get(grp, [])
    )
    | frozenset({39}),
}


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
                filter_premium_fixtures(dedupe_fixtures(tomorrow_rows))
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
    premium_only: bool = True,
) -> list[dict[str, Any]]:
    today_s = str(payload.get("today") or payload.get("today_local") or "")
    tomorrow_s = str(payload.get("tomorrow") or "")

    if not premium_only:
        if time_filter == "live":
            pool = filter_blocked_fixtures(list(payload.get("raw_live") or []))
        elif time_filter == "morgen":
            pool = filter_blocked_fixtures(list(payload.get("raw_tomorrow") or []))
        else:
            pool = filter_blocked_fixtures(
                dedupe_fixtures(
                    list(payload.get("raw_live") or [])
                    + list(payload.get("raw_today") or [])
                    + list(payload.get("raw_tomorrow") or [])
                )
            )
            if time_filter == "heute":
                pool = [
                    fx
                    for fx in pool
                    if _is_live(fx) or _fixture_date(fx) == today_s
                ]
        return sort_fixtures_by_priority(pool)

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

    region_ids = league_group_ids(region_filter)
    if region_ids is not None:
        pool = [
            fx
            for fx in pool
            if int((fx.get("league") or {}).get("id") or 0) in region_ids
        ]

    return sort_fixtures_by_priority(pool)


def extract_1x2_odds(markets: list[dict[str, Any]]) -> dict[str, float | None]:
    home_odd = draw_odd = away_odd = None
    for m in markets or []:
        market = str(m.get("market") or "").lower()
        sel = str(m.get("selection") or "").lower()
        if "match winner" not in market and "1x2" not in market and "winner" not in market:
            continue
        try:
            odd = float(m.get("odd") or 0)
        except (TypeError, ValueError):
            continue
        if odd < 1.01:
            continue
        if sel in ("home", "1"):
            home_odd = home_odd or odd
        elif sel in ("draw", "x"):
            draw_odd = draw_odd or odd
        elif sel in ("away", "2"):
            away_odd = away_odd or odd
    return {"home": home_odd, "draw": draw_odd, "away": away_odd}


def _risk_label(pred: dict[str, Any]) -> str:
    if pred.get("no_bet"):
        return "Hoch"
    conf = float(pred.get("best_bet_confidence") or 0)
    if conf >= 72:
        return "Niedrig"
    if conf >= 55:
        return "Mittel"
    return "Hoch"


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
        "ai_pick": "—",
        "confidence": None,
        "risk": "Mittel",
        "no_bet": False,
        "live_event": "",
        "momentum": "",
        "reasons": [],
    }

    pred_insights: dict[str, Any] = {}
    odds_markets: list[dict[str, Any]] = []

    if rank >= 2 and fid_int:
        try:
            pred_rows = service.get_fixture_predictions(fid_int, username=username)
            if pred_rows:
                pred_insights = parse_prediction_insights(pred_rows[0])
        except FootballAPIError:
            pass
        try:
            odds_markets = parse_fixture_odds_payload(
                service.get_fixture_odds(fid_int, username=username)
            )
        except FootballAPIError:
            pass

    o1x2 = extract_1x2_odds(odds_markets)
    row["home_odd"] = o1x2["home"]
    row["draw_odd"] = o1x2["draw"]
    row["away_odd"] = o1x2["away"]
    row["home_pct"] = pred_insights.get("home_pct")
    row["draw_pct"] = pred_insights.get("draw_pct")
    row["away_pct"] = pred_insights.get("away_pct")

    detail = {
        "card": card,
        "prediction_insights": pred_insights,
        "injuries_parsed": {"available": False},
        "suspensions_parsed": {"available": False},
    }
    try:
        prediction = build_match_prediction(detail)
        row["ai_pick"] = prediction.get("best_bet") or "—"
        row["confidence"] = prediction.get("best_bet_confidence")
        row["no_bet"] = bool(prediction.get("no_bet"))
        row["risk"] = _risk_label(prediction)
        row["reasons"] = list(prediction.get("reasons") or [])[:3]
    except Exception:
        pass

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
    max_enrich: int = 15,
) -> list[dict[str, Any]]:
    rank = football_plan_rank(session_plan or "none")
    rows: list[dict[str, Any]] = []
    for i, fx in enumerate(fixtures):
        if i < max_enrich and rank >= 2:
            rows.append(
                enrich_fixture_row(
                    service, fx, username=username, rank=rank, cache=cache
                )
            )
        else:
            card = parse_match_card(fx)
            rows.append(
                {
                    "fixture_id": card.get("fixture_id"),
                    "card": card,
                    "home_odd": None,
                    "draw_odd": None,
                    "away_odd": None,
                    "home_pct": None,
                    "draw_pct": None,
                    "away_pct": None,
                    "ai_pick": "—",
                    "confidence": None,
                    "risk": "Mittel",
                    "no_bet": False,
                    "reasons": [],
                    "live_event": "",
                    "momentum": "",
                }
            )
    return rows
