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
from services.football_leagues import LIVE_STATUSES, filter_blocked_fixtures, filter_premium_fixtures
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
    elif time_filter == "upcoming":
        pool = list(payload.get("next_matches") or [])
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


def collect_raw_fixtures_for_filters(
    payload: dict[str, Any],
    *,
    time_filter: str,
) -> list[dict[str, Any]]:
    """All API fixtures for time window — youth/reserve names blocked only."""
    today_s = str(payload.get("today") or payload.get("today_local") or "")
    raw_live = list(payload.get("raw_live") or [])
    raw_today = list(payload.get("raw_today") or [])
    raw_tomorrow = list(payload.get("raw_tomorrow") or [])

    if time_filter == "live":
        pool = raw_live
    elif time_filter == "morgen":
        pool = raw_tomorrow
    elif time_filter == "alle":
        pool = dedupe_fixtures(raw_live + raw_today + raw_tomorrow)
    else:
        pool = dedupe_fixtures(raw_live + raw_today)
        if time_filter == "heute":
            pool = [
                fx
                for fx in pool
                if _is_live(fx) or _fixture_date(fx) == today_s
            ]

    pool = filter_blocked_fixtures(pool)
    return sort_fixtures_by_priority(pool)


def build_raw_board_rows(
    fixtures: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 48,
) -> list[dict[str, Any]]:
    """Minimal rows for raw mode — score/time, optional odds, no AI tips."""
    rank = football_plan_rank(session_plan or "none")
    rows: list[dict[str, Any]] = []
    odds_budget = 6
    for i, fx in enumerate(fixtures[:max_enrich]):
        card = parse_match_card(fx)
        fid = card.get("fixture_id")
        try:
            fid_int = int(fid) if fid is not None else None
        except (TypeError, ValueError):
            fid_int = None

        row: dict[str, Any] = {
            "fixture_id": fid_int,
            "card": card,
            "raw_mode": True,
            "home_odd": None,
            "draw_odd": None,
            "away_odd": None,
            "has_odds": False,
            "analysis_available": False,
        }

        if rank >= 2 and fid_int and i < odds_budget:
            cache_key = f"raw_{fid_int}"
            if cache_key in cache:
                row.update(cache[cache_key])
            else:
                try:
                    o = get_odds_for_fixture(service, fid_int, username=username)
                    row["home_odd"] = o.get("home")
                    row["draw_odd"] = o.get("draw")
                    row["away_odd"] = o.get("away")
                    row["has_odds"] = has_complete_odds(row)
                    row["analysis_available"] = bool(row["has_odds"])
                    cache[cache_key] = {
                        "home_odd": row["home_odd"],
                        "draw_odd": row["draw_odd"],
                        "away_odd": row["away_odd"],
                        "has_odds": row["has_odds"],
                        "analysis_available": row["analysis_available"],
                    }
                except FootballAPIError:
                    pass

        rows.append(row)
    return rows


def load_raw_football_matches(
    payload: dict[str, Any],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    mode: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 48,
) -> dict[str, Any]:
    """Raw API fixtures — no premium filter."""
    mode = (mode or "heute").lower().strip()
    fixtures = collect_raw_fixtures_for_filters(payload, time_filter=mode)
    rows = build_raw_board_rows(
        fixtures,
        service,
        username=username,
        session_plan=session_plan,
        cache=cache,
        max_enrich=max_enrich,
    )
    return {
        "fixtures": fixtures[:max_enrich],
        "rows": rows,
        "stage": "raw_all",
        "banner": None,
        "raw_mode": True,
        "pools": {"raw": len(fixtures)},
    }


def build_board_rows(
    fixtures: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 24,
    allow_no_odds: bool = False,
    form_only: bool = False,
) -> list[dict[str, Any]]:
    rank = football_plan_rank(session_plan or "none")
    if rank < 2:
        return build_basic_board_rows(fixtures[:max_enrich])

    rows: list[dict[str, Any]] = []
    for fx in fixtures[:max_enrich]:
        rows.append(
            enrich_fixture_row(
                service,
                fx,
                username=username,
                rank=rank,
                cache=cache,
                form_only=form_only,
            )
        )
    if form_only or allow_no_odds:
        return rows
    return filter_rows_with_odds(rows, allow_no_odds=False)


def build_basic_board_rows(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Starter plan — show premium fixtures without odds API."""
    rows: list[dict[str, Any]] = []
    for fx in fixtures or []:
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
                "no_bet": True,
                "value": False,
                "reasons": [],
                "live_event": "",
                "momentum": "",
                "has_odds": False,
            }
        )
    return rows


_FALLBACK_MESSAGES: dict[str, str] = {
    "today_premium_with_odds": "Heute keine Premium-Live-Spiele — zeige heutige Topspiele.",
    "tomorrow_premium_with_odds": "Keine Premium-Spiele heute — zeige morgige Topspiele.",
    "upcoming_premium_with_odds": "Nächste Premium-Spiele (7 Tage).",
    "today_premium_without_odds": (
        "Quoten aktuell nicht verfügbar — Analyse basiert auf Formdaten."
    ),
    "tomorrow_premium_without_odds": (
        "Quoten aktuell nicht verfügbar — Analyse basiert auf Formdaten."
    ),
    "upcoming_premium_without_odds": (
        "Quoten aktuell nicht verfügbar — nächste Premium-Spiele (Formanalyse)."
    ),
    "live_empty": "Keine Premium-Live-Spiele aktuell.",
}


def _fallback_chain(mode: str) -> list[tuple[str, str, bool]]:
    """Return (stage_id, pool_key, require_odds) in priority order."""
    chains: dict[str, list[tuple[str, str, bool]]] = {
        "live": [
            ("live_premium_with_odds", "live", True),
            ("live_premium_without_odds", "live", False),
        ],
        "heute": [
            ("today_premium_with_odds", "today", True),
            ("tomorrow_premium_with_odds", "tomorrow", True),
            ("upcoming_premium_with_odds", "upcoming", True),
            ("today_premium_without_odds", "today", False),
            ("tomorrow_premium_without_odds", "tomorrow", False),
            ("upcoming_premium_without_odds", "upcoming", False),
        ],
        "morgen": [
            ("tomorrow_premium_with_odds", "tomorrow", True),
            ("today_premium_with_odds", "today", True),
            ("upcoming_premium_with_odds", "upcoming", True),
            ("tomorrow_premium_without_odds", "tomorrow", False),
            ("today_premium_without_odds", "today", False),
            ("upcoming_premium_without_odds", "upcoming", False),
        ],
        "alle": [
            ("live_premium_with_odds", "live", True),
            ("today_premium_with_odds", "today", True),
            ("tomorrow_premium_with_odds", "tomorrow", True),
            ("upcoming_premium_with_odds", "upcoming", True),
            ("today_premium_without_odds", "today", False),
            ("tomorrow_premium_without_odds", "tomorrow", False),
            ("upcoming_premium_without_odds", "upcoming", False),
        ],
    }
    return chains.get((mode or "heute").lower(), chains["heute"])


def _count_with_odds(
    service: FootballService,
    fixtures: list[dict[str, Any]],
    *,
    username: str,
    sample: int = 8,
) -> int:
    """Sample-based odds availability count for admin debug."""
    if not fixtures:
        return 0
    hits = 0
    for fx in fixtures[:sample]:
        fid = (fx.get("fixture") or {}).get("id")
        if not fid:
            continue
        try:
            o = get_odds_for_fixture(service, int(fid), username=username)
            if has_complete_odds(
                {"home_odd": o.get("home"), "draw_odd": o.get("draw"), "away_odd": o.get("away")}
            ):
                hits += 1
        except FootballAPIError:
            pass
    if len(fixtures) <= sample:
        return hits
    return int(round(hits / min(sample, len(fixtures)) * len(fixtures)))


def build_fallback_debug_stats(
    payload: dict[str, Any],
    *,
    region_filter: str,
    service: FootballService | None = None,
    username: str = "",
) -> dict[str, Any]:
    """Admin debug: raw vs premium vs odds counts."""
    live_premium = collect_fixtures_for_filters(payload, time_filter="live", region_filter=region_filter)
    today_premium = collect_fixtures_for_filters(payload, time_filter="heute", region_filter=region_filter)
    tomorrow_premium = collect_fixtures_for_filters(
        payload, time_filter="morgen", region_filter=region_filter
    )
    upcoming_premium = collect_fixtures_for_filters(
        payload, time_filter="upcoming", region_filter=region_filter
    )
    stats: dict[str, Any] = {
        "live_raw": len(payload.get("raw_live") or []),
        "live_premium": len(live_premium),
        "today_raw": len(payload.get("raw_today") or []),
        "today_premium": len(today_premium),
        "tomorrow_raw": len(payload.get("raw_tomorrow") or []),
        "tomorrow_premium": len(tomorrow_premium),
        "upcoming_premium": len(upcoming_premium),
        "today_with_odds": None,
        "tomorrow_with_odds": None,
        "upcoming_with_odds": None,
    }
    if service and username is not None:
        stats["today_with_odds"] = _count_with_odds(service, today_premium, username=username)
        stats["tomorrow_with_odds"] = _count_with_odds(service, tomorrow_premium, username=username)
        stats["upcoming_with_odds"] = _count_with_odds(service, upcoming_premium, username=username)
    return stats


def load_football_matches(
    payload: dict[str, Any],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    mode: str,
    category: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 24,
    force_no_odds: bool = False,
) -> dict[str, Any]:
    """
    Premium fallback pipeline — never return empty while premium fixtures exist.
    """
    mode = (mode or "heute").lower().strip()
    category = (category or "alle").lower().strip()

    pools = {
        "live": collect_fixtures_for_filters(payload, time_filter="live", region_filter=category),
        "today": collect_fixtures_for_filters(payload, time_filter="heute", region_filter=category),
        "tomorrow": collect_fixtures_for_filters(
            payload, time_filter="morgen", region_filter=category
        ),
        "upcoming": collect_fixtures_for_filters(
            payload, time_filter="upcoming", region_filter=category
        ),
    }
    debug_stats = build_fallback_debug_stats(
        payload, region_filter=category, service=service, username=username
    )

    chain = _fallback_chain(mode)
    if force_no_odds:
        chain = [(s, p, r) for s, p, r in chain if not r]

    if mode == "live" and not pools.get("live"):
        return {
            "fixtures": [],
            "rows": [],
            "stage": "live_empty",
            "banner": _FALLBACK_MESSAGES["live_empty"],
            "pool_key": "live",
            "require_odds": True,
            "debug_stats": debug_stats,
            "pools": {k: len(v) for k, v in pools.items()},
        }

    for stage_id, pool_key, require_odds in chain:
        fixtures = pools.get(pool_key) or []
        if not fixtures:
            continue

        rows = build_board_rows(
            fixtures,
            service,
            username=username,
            session_plan=session_plan,
            cache=cache,
            max_enrich=max_enrich,
            allow_no_odds=not require_odds,
            form_only=not require_odds,
        )
        if not rows:
            continue

        primary_stage = chain[0][0] if chain else ""
        banner = None
        if stage_id != primary_stage:
            banner = _FALLBACK_MESSAGES.get(stage_id)
        if force_no_odds and not require_odds:
            banner = _FALLBACK_MESSAGES.get(stage_id) or (
                "Quoten aktuell nicht verfügbar — Analyse basiert auf Formdaten."
            )

        return {
            "fixtures": fixtures[:max_enrich],
            "rows": rows,
            "stage": stage_id,
            "banner": banner,
            "pool_key": pool_key,
            "require_odds": require_odds,
            "debug_stats": debug_stats,
            "pools": {k: len(v) for k, v in pools.items()},
        }

    return {
        "fixtures": [],
        "rows": [],
        "stage": "clean_empty_state",
        "banner": "Keine Premium-Spiele im gewählten Zeitraum.",
        "pool_key": "",
        "require_odds": True,
        "debug_stats": debug_stats,
        "pools": {k: len(v) for k, v in pools.items()},
    }


def enrich_fixture_row(
    service: FootballService,
    fixture: dict[str, Any],
    *,
    username: str,
    rank: int,
    cache: dict[int, dict[str, Any]],
    form_only: bool = False,
) -> dict[str, Any]:
    card = parse_match_card(fixture)
    fid = card.get("fixture_id")
    try:
        fid_int = int(fid) if fid is not None else None
    except (TypeError, ValueError):
        fid_int = None

    if fid_int and fid_int in cache and not form_only:
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

        if not form_only:
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
        form_only=form_only,
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
