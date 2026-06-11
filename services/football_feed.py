"""
Football feed — competition browser (league-ID queries) + Alle API (raw global).
No global fixtures?date as primary source for curated view.
"""
from __future__ import annotations

from typing import Any

from config import (
    FOOTBALL_COMPETITION_GROUPS,
    FOOTBALL_FRIENDLIES_LEAGUE_ID,
    FOOTBALL_TOPSPIELE_LEAGUE_IDS,
    football_plan_rank,
)
from services.football_board import (
    _standing_summary,
    _team_standing_row,
    build_league_standings_cache,
    fetch_match_detail,
    format_form_display,
    form_from_standing_row,
    format_standing_chip,
    get_odds_for_fixture,
    has_complete_odds,
    parse_prediction_insights,
)
from services.football_loaders import (
    LIVE_STATUSES,
    _local_today_tomorrow,
    dedupe_fixtures,
    filter_blocked_fixtures,
    parse_match_card,
    sort_fixtures_by_priority,
)
from services.football_service import FootballAPIError, FootballService

MATCH_CAP = 20
ALL_API_CAP = 50
MSG_NEXT = "Nächste Spiele"
MSG_ALL_API_LABEL = "Alle Free-Tier-Spiele (max. 50) — football-data.org Wettbewerbe."
MSG_QUOTE_IN_ANALYSIS = "Quote in Analyse verfügbar"
MSG_NO_ODDS_FREE = ""

_CLUB_MARKERS = (
    " fc", " cf", " sc", " united", " city", " bayern", " borussia",
    " athletic", " atletico", " real ", " inter ", " ac ", " as ",
)


def _league_id(fixture: dict[str, Any]) -> int | None:
    try:
        return int((fixture.get("league") or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def league_ids_for_competition(competition: str) -> frozenset[int]:
    key = (competition or "deutschland").strip().lower()
    return FOOTBALL_COMPETITION_GROUPS.get(key, FOOTBALL_COMPETITION_GROUPS["deutschland"])


def is_topspiele_fixture(fixture: dict[str, Any]) -> bool:
    lid = _league_id(fixture)
    return bool(lid and lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS)


def filter_topspiele_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [fx for fx in fixtures or [] if is_topspiele_fixture(fx)]


def _is_national_team_fixture(fixture: dict[str, Any]) -> bool:
    teams = fixture.get("teams") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    if home.get("national") is True or away.get("national") is True:
        return True
    lid = _league_id(fixture)
    if lid != FOOTBALL_FRIENDLIES_LEAGUE_ID:
        return lid in {1, 4, 5}
    hname = str(home.get("name") or "").strip()
    aname = str(away.get("name") or "").strip()
    if not hname or not aname:
        return False
    hl, al = hname.lower(), aname.lower()
    if any(m in hl or m in al for m in _CLUB_MARKERS):
        return False
    return True


def _matches_competition(fixture: dict[str, Any], competition: str, league_ids: frozenset[int]) -> bool:
    lid = _league_id(fixture)
    if lid not in league_ids:
        return False
    if (competition or "").lower() == "nationalteams" and lid == FOOTBALL_FRIENDLIES_LEAGUE_ID:
        return _is_national_team_fixture(fixture)
    return True


def _fixture_date(fixture: dict[str, Any]) -> str:
    return parse_match_card(fixture).get("date") or ""


def _is_live(fixture: dict[str, Any]) -> bool:
    st = str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "")
    return st in LIVE_STATUSES


def _filter_competition_pool(
    fixtures: list[dict[str, Any]],
    *,
    competition: str,
    league_ids: frozenset[int],
) -> list[dict[str, Any]]:
    return [
        fx
        for fx in dedupe_fixtures(fixtures or [])
        if _matches_competition(fx, competition, league_ids)
    ]


def _note_error(errors: list[str] | None, exc: Exception) -> None:
    msg = str(exc).strip()
    if errors is not None and msg and msg not in errors:
        errors.append(msg)


def _fetch_league_today(
    service: FootballService,
    league_id: int,
    today: str,
    *,
    username: str,
    errors: list[str] | None = None,
) -> list[dict[str, Any]]:
    try:
        return service.get_fixtures_by_league_range(
            league_id,
            date_from=today,
            date_to=today,
            username=username,
        )
    except FootballAPIError as exc:
        _note_error(errors, exc)
        return []


def _fetch_league_tomorrow(
    service: FootballService,
    league_id: int,
    tomorrow: str,
    *,
    username: str,
    errors: list[str] | None = None,
) -> list[dict[str, Any]]:
    try:
        return service.get_fixtures_by_league_range(
            league_id,
            date_from=tomorrow,
            date_to=tomorrow,
            username=username,
        )
    except FootballAPIError as exc:
        _note_error(errors, exc)
        return []


def _fetch_league_next(
    service: FootballService,
    league_id: int,
    *,
    username: str,
    count: int = 15,
    errors: list[str] | None = None,
) -> list[dict[str, Any]]:
    try:
        return service.get_fixtures_by_league_next(
            league_id, next_count=count, username=username
        )
    except FootballAPIError as exc:
        _note_error(errors, exc)
        return []


def _fetch_league_live(
    service: FootballService,
    league_ids: frozenset[int],
    *,
    username: str,
    errors: list[str] | None = None,
) -> list[dict[str, Any]]:
    try:
        rows = service.get_live_fixtures(username=username)
    except FootballAPIError as exc:
        _note_error(errors, exc)
        return []
    return [fx for fx in rows if _league_id(fx) in league_ids]


def _collect_by_leagues(
    service: FootballService,
    league_ids: frozenset[int],
    *,
    username: str,
    fetch_fn,
) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    for lid in sorted(league_ids):
        pool.extend(fetch_fn(service, int(lid), username=username))
    return pool


def fetch_competition_fixtures(
    service: FootballService,
    *,
    username: str,
    competition: str,
    time_filter: str,
) -> dict[str, Any]:
    """
    Query fixtures per league ID for the selected competition group.
    Heute: today → live → tomorrow → next (banner: Nächste Spiele).
    """
    league_ids = league_ids_for_competition(competition)
    today, tomorrow = _local_today_tomorrow()
    tf = (time_filter or "heute").lower()
    errors: list[str] = []
    banner: str | None = None
    effective_filter = tf

    def _today_fetch(svc: FootballService, lid: int, *, username: str) -> list[dict[str, Any]]:
        return _fetch_league_today(svc, lid, today, username=username, errors=errors)

    def _tomorrow_fetch(svc: FootballService, lid: int, *, username: str) -> list[dict[str, Any]]:
        return _fetch_league_tomorrow(svc, lid, tomorrow, username=username, errors=errors)

    def _next_fetch(svc: FootballService, lid: int, *, username: str) -> list[dict[str, Any]]:
        return _fetch_league_next(svc, lid, username=username, errors=errors)

    pool: list[dict[str, Any]] = []

    if tf == "live":
        live_rows = _fetch_league_live(service, league_ids, username=username, errors=errors)
        pool = _filter_competition_pool(live_rows, competition=competition, league_ids=league_ids)
        if not pool:
            pool = _filter_competition_pool(
                _collect_by_leagues(service, league_ids, username=username, fetch_fn=_next_fetch),
                competition=competition,
                league_ids=league_ids,
            )
            if pool:
                banner = MSG_NEXT
                effective_filter = "naechste"
    elif tf == "morgen":
        pool = _filter_competition_pool(
            _collect_by_leagues(service, league_ids, username=username, fetch_fn=_tomorrow_fetch),
            competition=competition,
            league_ids=league_ids,
        )
        if not pool:
            pool = _filter_competition_pool(
                _collect_by_leagues(service, league_ids, username=username, fetch_fn=_next_fetch),
                competition=competition,
                league_ids=league_ids,
            )
            if pool:
                banner = MSG_NEXT
                effective_filter = "naechste"
    elif tf == "naechste":
        pool = _filter_competition_pool(
            _collect_by_leagues(service, league_ids, username=username, fetch_fn=_next_fetch),
            competition=competition,
            league_ids=league_ids,
        )
        if pool:
            banner = MSG_NEXT
    else:  # heute
        pool = _filter_competition_pool(
            _collect_by_leagues(service, league_ids, username=username, fetch_fn=_today_fetch),
            competition=competition,
            league_ids=league_ids,
        )
        if not pool:
            live_rows = _fetch_league_live(service, league_ids, username=username, errors=errors)
            pool = _filter_competition_pool(live_rows, competition=competition, league_ids=league_ids)
            if pool:
                effective_filter = "live"
        if not pool:
            pool = _filter_competition_pool(
                _collect_by_leagues(service, league_ids, username=username, fetch_fn=_tomorrow_fetch),
                competition=competition,
                league_ids=league_ids,
            )
            if pool:
                effective_filter = "morgen"
        if not pool:
            pool = _filter_competition_pool(
                _collect_by_leagues(service, league_ids, username=username, fetch_fn=_next_fetch),
                competition=competition,
                league_ids=league_ids,
            )
            if pool:
                banner = MSG_NEXT
                effective_filter = "naechste"

    pool = sort_fixtures_by_priority(pool)[:MATCH_CAP]

    return {
        "fixtures": pool,
        "banner": banner,
        "errors": errors,
        "competition": competition,
        "time_filter": tf,
        "effective_filter": effective_filter,
        "today": today,
        "tomorrow": tomorrow,
    }


def fetch_all_api_payload(
    service: FootballService,
    *,
    username: str,
) -> dict[str, Any]:
    """Raw global API lists — only for Alle Spiele mode."""
    today, tomorrow = _local_today_tomorrow()
    errors: list[str] = []

    def _fetch(fn) -> list[dict[str, Any]]:
        try:
            return fn()
        except FootballAPIError as exc:
            errors.append(str(exc))
            return []

    raw_live = _fetch(lambda: service.get_live_fixtures(username=username))
    raw_today = _fetch(lambda: service.get_fixtures_by_date(today, username=username))
    raw_tomorrow = _fetch(lambda: service.get_fixtures_by_date(tomorrow, username=username))

    return {
        "today": today,
        "tomorrow": tomorrow,
        "errors": errors,
        "raw_live": raw_live,
        "raw_today": raw_today,
        "raw_tomorrow": raw_tomorrow,
    }


def _all_api_sort_key(fixture: dict[str, Any]) -> tuple:
    lid = _league_id(fixture) or 0
    in_top = 0 if lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS else 1
    return (in_top, str((fixture.get("fixture") or {}).get("date") or ""))


def _pool_for_time_raw(payload: dict[str, Any], time_filter: str) -> list[dict[str, Any]]:
    today_s = str(payload.get("today") or "")
    tf = (time_filter or "heute").lower()
    raw_live = list(payload.get("raw_live") or [])
    raw_today = list(payload.get("raw_today") or [])
    raw_tomorrow = list(payload.get("raw_tomorrow") or [])

    if tf == "live":
        pool = raw_live
    elif tf == "morgen":
        pool = raw_tomorrow
    elif tf == "naechste":
        pool = sorted(
            dedupe_fixtures(raw_today + raw_tomorrow + raw_live),
            key=_all_api_sort_key,
        )
    else:
        pool = dedupe_fixtures(raw_live + raw_today)
        if tf == "heute":
            pool = [fx for fx in pool if _is_live(fx) or _fixture_date(fx) == today_s]

    return filter_blocked_fixtures(pool)


def format_quote_label(row: dict[str, Any], *, deferred: bool = False) -> str:
    _ = deferred
    if row.get("home_odd") and row.get("draw_odd") and row.get("away_odd"):
        try:
            h, d, a = float(row["home_odd"]), float(row["draw_odd"]), float(row["away_odd"])
            return f"1 {h:.2f} · X {d:.2f} · 2 {a:.2f}"
        except (TypeError, ValueError):
            pass
    return MSG_QUOTE_IN_ANALYSIS


def enrich_rows_standings(
    rows: list[dict[str, Any]],
    standings_cache: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        r = dict(row)
        card = r.get("card") or {}
        try:
            lid = int(card.get("league_id") or 0)
        except (TypeError, ValueError):
            lid = 0
        payload = standings_cache.get(lid) or []
        home_id = card.get("home_id")
        away_id = card.get("away_id")
        home_row = away_row = None
        if home_id:
            home_row = _team_standing_row(payload, int(home_id))
            r["home_standing_chip"] = format_standing_chip(_standing_summary(home_row))
            hf = form_from_standing_row(home_row)
            if hf:
                r["home_form"] = hf
        else:
            r["home_standing_chip"] = ""
        if away_id:
            away_row = _team_standing_row(payload, int(away_id))
            r["away_standing_chip"] = format_standing_chip(_standing_summary(away_row))
            af = form_from_standing_row(away_row)
            if af:
                r["away_form"] = af
        else:
            r["away_standing_chip"] = ""
        r["has_standing_context"] = bool(
            r.get("home_standing_chip") or r.get("away_standing_chip")
        )
        out.append(r)
    return out


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
        "analysis_available": False,
        "has_odds": False,
        "has_predictions": False,
        "home_odd": None,
        "draw_odd": None,
        "away_odd": None,
        "quote_label": "",
    }


def probe_analysis_available(
    service: FootballService,
    fixture_id: int,
    *,
    username: str,
    session_plan: str,
) -> tuple[bool, bool, dict[str, float | None], str, str]:
    rank = football_plan_rank(session_plan or "none")
    odds = {"home": None, "draw": None, "away": None}
    has_odds = has_pred = False
    form_home = form_away = ""
    if rank < 1 or not fixture_id:
        return has_odds, has_pred, odds, form_home, form_away

    premium_api = getattr(service, "premium_api_enabled", lambda: False)()
    if premium_api:
        try:
            o1x2 = get_odds_for_fixture(service, int(fixture_id), username=username)
            odds = {
                "home": o1x2.get("home"),
                "draw": o1x2.get("draw"),
                "away": o1x2.get("away"),
            }
            has_odds = has_complete_odds(
                {"home_odd": odds["home"], "draw_odd": odds["draw"], "away_odd": odds["away"]}
            )
        except FootballAPIError:
            pass

        if rank >= 2:
            try:
                rows = service.get_fixture_predictions(int(fixture_id), username=username)
                if rows:
                    ins = parse_prediction_insights(rows[0])
                    has_pred = ins.get("home_pct") is not None or bool(ins.get("advice"))
                    form_home = format_form_display(str(ins.get("form_home") or ""))
                    form_away = format_form_display(str(ins.get("form_away") or ""))
            except FootballAPIError:
                pass

    return has_odds, has_pred, odds, form_home, form_away


def _row_analysis_available(row: dict[str, Any]) -> bool:
    return bool(
        row.get("has_odds")
        or row.get("has_predictions")
        or row.get("has_standing_context")
        or row.get("home_form")
        or row.get("away_form")
    )


def enrich_rows_analysis_flags(
    rows: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    max_probe: int = MATCH_CAP,
) -> list[dict[str, Any]]:
    rank = football_plan_rank(session_plan or "none")
    premium_api = getattr(service, "premium_api_enabled", lambda: False)()
    out: list[dict[str, Any]] = []
    probed = 0
    for row in rows:
        r = dict(row)
        fid = r.get("fixture_id")
        probed_this = bool(fid and probed < max_probe and rank >= 1 and premium_api)
        if probed_this:
            has_odds, has_pred, odds, pf_home, pf_away = probe_analysis_available(
                service, int(fid), username=username, session_plan=session_plan
            )
            r["has_odds"] = has_odds
            r["has_predictions"] = has_pred
            r["home_odd"] = odds.get("home")
            r["draw_odd"] = odds.get("draw")
            r["away_odd"] = odds.get("away")
            if pf_home and not r.get("home_form"):
                r["home_form"] = pf_home
            if pf_away and not r.get("away_form"):
                r["away_form"] = pf_away
            r["quote_label"] = format_quote_label(r, deferred=not has_odds)
            probed += 1
        else:
            r.setdefault("has_odds", False)
            r.setdefault("has_predictions", False)
            r["quote_label"] = (
                MSG_QUOTE_IN_ANALYSIS if rank >= 1 and fid and premium_api else MSG_NO_ODDS_FREE
            )
        r["analysis_available"] = _row_analysis_available(r)
        out.append(r)
    return out


def resolve_competition_board(
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    competition: str,
    time_filter: str,
    probe_analysis: bool = True,
) -> dict[str, Any]:
    payload = fetch_competition_fixtures(
        service,
        username=username,
        competition=competition,
        time_filter=time_filter,
    )
    fixtures = payload.get("fixtures") or []
    rows = [build_row(fx, raw_mode=False) for fx in fixtures]
    if rows and football_plan_rank(session_plan or "none") >= 1:
        standings_cache = build_league_standings_cache(
            service, fixtures, username=username
        )
        rows = enrich_rows_standings(rows, standings_cache)
    if probe_analysis and rows:
        rows = enrich_rows_analysis_flags(
            rows, service, username=username, session_plan=session_plan
        )

    banner = payload.get("banner")
    if not rows and not banner:
        banner = MSG_NEXT

    return {
        "rows": rows,
        "banner": banner,
        "source": "competition",
        "raw_mode": False,
        "competition": competition,
        "time_filter": time_filter,
        "effective_filter": payload.get("effective_filter"),
        "displayed_topspiele_count": len(rows),
        "displayed_allspiele_count": 0,
        "errors": payload.get("errors") or [],
    }


def resolve_all_api_board(
    payload: dict[str, Any],
    *,
    time_filter: str,
) -> dict[str, Any]:
    pool = _pool_for_time_raw(payload, time_filter)
    pool = sorted(pool, key=_all_api_sort_key)[:ALL_API_CAP]
    rows = [build_row(fx, raw_mode=True) for fx in pool]
    return {
        "rows": rows,
        "banner": MSG_ALL_API_LABEL if rows else "Aktuell keine API-Spiele für diesen Zeitraum.",
        "source": "raw",
        "raw_mode": True,
        "displayed_topspiele_count": 0,
        "displayed_allspiele_count": len(rows),
        "errors": payload.get("errors") or [],
    }


def resolve_football_feed(
    payload: dict[str, Any] | None,
    service: FootballService,
    *,
    view_mode: str,
    time_filter: str,
    username: str,
    session_plan: str,
    competition: str = "deutschland",
    probe_analysis: bool = True,
) -> dict[str, Any]:
    vm = "raw" if str(view_mode).lower() in ("raw", "alle", "alle_spiele") else "curated"
    if vm == "raw":
        raw_payload = payload or fetch_all_api_payload(service, username=username)
        return resolve_all_api_board(raw_payload, time_filter=time_filter)
    return resolve_competition_board(
        service,
        username=username,
        session_plan=session_plan,
        competition=competition,
        time_filter=time_filter,
        probe_analysis=probe_analysis,
    )


# Backward-compatible aliases
def resolve_topspiele_board(payload, *, time_filter: str) -> dict[str, Any]:
    _ = payload, time_filter
    return {"rows": [], "banner": MSG_NEXT, "displayed_topspiele_count": 0}


def fetch_board_payload(service, *, username: str, time_filter: str) -> dict[str, Any]:
    _ = time_filter
    return fetch_all_api_payload(service, username=username)


__all__ = [
    "fetch_all_api_payload",
    "fetch_board_payload",
    "fetch_competition_fixtures",
    "fetch_match_detail",
    "filter_topspiele_fixtures",
    "format_quote_label",
    "is_topspiele_fixture",
    "league_ids_for_competition",
    "resolve_all_api_board",
    "resolve_competition_board",
    "resolve_football_feed",
    "resolve_topspiele_board",
]
