"""Live Match Center — fixture grouping, filtering, match detail bundles."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from config import FOOTBALL_DEFAULT_SEASON, football_plan_rank
from services.football_leagues import (
    FINISHED_STATUSES,
    LIVE_STATUSES,
    SCHEDULED_STATUSES,
    is_featured_league,
    league_name_map,
    league_tier,
    premium_league_ids,
    relevance_score,
)
from services.football_odds import parse_fixture_odds_payload, parse_prediction_insights
from services.football_service import FootballAPIError, FootballService, fixture_team_names


def _league_id(fixture: dict[str, Any]) -> int | None:
    try:
        return int((fixture.get("league") or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def _fixture_date(fixture: dict[str, Any]) -> str:
    raw = str((fixture.get("fixture") or {}).get("date") or "")
    return raw[:10] if raw else ""


def _status_short(fixture: dict[str, Any]) -> str:
    return str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "NS")


def _elapsed(fixture: dict[str, Any]) -> int | None:
    val = ((fixture.get("fixture") or {}).get("status") or {}).get("elapsed")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def parse_match_card(fixture: dict[str, Any]) -> dict[str, Any]:
    meta = fixture.get("fixture") or {}
    teams = fixture.get("teams") or {}
    goals = fixture.get("goals") or {}
    league = fixture.get("league") or {}
    venue = meta.get("venue") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    status = _status_short(fixture)
    gh, ga = goals.get("home"), goals.get("away")
    if gh is not None and ga is not None:
        score = f"{gh} : {ga}"
    elif status in LIVE_STATUSES:
        score = "– : –"
    else:
        score = "vs"
    minute = _elapsed(fixture)
    if status in LIVE_STATUSES and minute is not None:
        status_label = f"{status} {minute}'"
    else:
        status_label = status
    date_raw = str(meta.get("date") or "")
    time_show = date_raw[11:16] if "T" in date_raw else ""
    lid = league.get("id")
    try:
        lid_int = int(lid) if lid is not None else None
    except (TypeError, ValueError):
        lid_int = None
    live = status in LIVE_STATUSES
    finished = status in FINISHED_STATUSES
    rel = relevance_score(league_id=lid_int, live=live, finished=finished)
    return {
        "fixture_id": meta.get("id"),
        "home": home.get("name") or "Home",
        "away": away.get("name") or "Away",
        "home_logo": home.get("logo") or "",
        "away_logo": away.get("logo") or "",
        "score": score,
        "status": status,
        "status_label": status_label,
        "minute": minute,
        "league": league.get("name") or "",
        "league_id": lid,
        "league_logo": league.get("logo") or "",
        "country": league.get("country") or "",
        "date": _fixture_date(fixture),
        "time": time_show,
        "venue": venue.get("name") or "",
        "city": venue.get("city") or "",
        "live": live,
        "finished": finished,
        "tier": league_tier(lid_int),
        "featured": is_featured_league(lid_int),
        "relevance_score": rel,
    }


def filter_fixtures(
    fixtures: list[dict[str, Any]],
    *,
    league_ids: set[int] | None = None,
    country: str = "",
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    search_l = country.strip().lower()
    for fx in fixtures or []:
        lid = _league_id(fx)
        if league_ids and lid not in league_ids:
            continue
        if search_l:
            league = fx.get("league") or {}
            teams = fx.get("teams") or {}
            home = str((teams.get("home") or {}).get("name") or "").lower()
            away = str((teams.get("away") or {}).get("name") or "").lower()
            league_name = str(league.get("name") or "").lower()
            league_country = str(league.get("country") or "").lower()
            hay = f"{home} {away} {league_name} {league_country}"
            if search_l not in hay:
                continue
        out.append(fx)
    return out


def dedupe_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[int] = set()
    out: list[dict[str, Any]] = []
    for fx in fixtures or []:
        fid = (fx.get("fixture") or {}).get("id")
        if not fid:
            continue
        try:
            key = int(fid)
        except (TypeError, ValueError):
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(fx)
    return out


def sort_fixtures_by_priority(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def _key(fx: dict[str, Any]) -> tuple:
        card = parse_match_card(fx)
        meta = fx.get("fixture") or {}
        return (
            -int(card.get("relevance_score") or 0),
            str(meta.get("date") or ""),
            str((fx.get("league") or {}).get("name") or ""),
        )

    return sorted(fixtures or [], key=_key)


def classify_fixtures(
    fixtures: list[dict[str, Any]],
    *,
    today: str,
    tomorrow: str,
) -> dict[str, list[dict[str, Any]]]:
    live_now: list[dict[str, Any]] = []
    later_today: list[dict[str, Any]] = []
    finished_today: list[dict[str, Any]] = []
    tomorrow_list: list[dict[str, Any]] = []

    for fx in fixtures:
        d = _fixture_date(fx)
        st = _status_short(fx)
        if st in LIVE_STATUSES:
            live_now.append(fx)
            continue
        if d == tomorrow:
            tomorrow_list.append(fx)
            continue
        if d != today:
            continue
        if st in FINISHED_STATUSES:
            finished_today.append(fx)
        elif st in SCHEDULED_STATUSES or st not in FINISHED_STATUSES:
            later_today.append(fx)

    return {
        "live_now": sort_fixtures_by_priority(live_now),
        "later_today": sort_fixtures_by_priority(later_today),
        "finished_today": sort_fixtures_by_priority(finished_today),
        "tomorrow": sort_fixtures_by_priority(tomorrow_list),
    }


def fetch_live_center_payload(
    service: FootballService,
    *,
    username: str,
    league_filter: set[int] | None = None,
    country_filter: str = "",
    premium_only: bool = True,
    show_all_live: bool = False,
    scope: str = "all",
) -> dict[str, Any]:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    today_s = today.isoformat()
    tomorrow_s = tomorrow.isoformat()

    errors: list[str] = []
    live_rows: list[dict[str, Any]] = []
    today_rows: list[dict[str, Any]] = []
    tomorrow_rows: list[dict[str, Any]] = []

    if not service.is_configured():
        return {
            "configured": False,
            "today": today_s,
            "tomorrow": tomorrow_s,
            "errors": ["API-Football ist nicht konfiguriert (FOOTBALL_API_KEY)."],
            "sections": classify_fixtures([], today=today_s, tomorrow=tomorrow_s),
            "total_fixtures": 0,
            "premium_live_count": 0,
            "raw_live_count": 0,
            "show_all_live_prompt": False,
        }

    try:
        live_rows = service.get_live_fixtures(username=username)
    except FootballAPIError as exc:
        errors.append(str(exc))

    # Fixtures by date only when needed (Premium default: live + today + tomorrow)
    need_today = scope in ("all", "heute", "premium", "deutschland", "uefa", "europa_top", "national", "favoriten", "alle")
    need_tomorrow = scope in ("all", "morgen", "premium", "alle")

    if need_today:
        try:
            today_rows = service.get_fixtures_by_date(today_s, username=username)
        except FootballAPIError as exc:
            errors.append(str(exc))

    if need_tomorrow:
        try:
            tomorrow_rows = service.get_fixtures_by_date(tomorrow_s, username=username)
        except FootballAPIError as exc:
            errors.append(str(exc))

    merged = dedupe_fixtures(live_rows + today_rows + tomorrow_rows)

    premium_ids = premium_league_ids()
    premium_live = filter_fixtures(live_rows, league_ids=set(premium_ids))
    raw_live_count = len(live_rows)
    premium_live_count = len(premium_live)

    if league_filter is not None:
        effective_ids = league_filter
    elif premium_only and not show_all_live:
        effective_ids = set(premium_ids)
    else:
        effective_ids = None

    if scope == "live":
        merged = live_rows
    elif scope == "heute":
        merged = dedupe_fixtures(live_rows + today_rows)
    elif scope == "morgen":
        merged = tomorrow_rows

    if effective_ids is not None:
        filtered = filter_fixtures(merged, league_ids=effective_ids, country=country_filter)
    else:
        filtered = filter_fixtures(merged, league_ids=None, country=country_filter)

    if scope == "live" and premium_only and not show_all_live and effective_ids:
        filtered = filter_fixtures(live_rows, league_ids=effective_ids, country=country_filter)

    sections = classify_fixtures(filtered, today=today_s, tomorrow=tomorrow_s)

    show_prompt = (
        premium_only
        and not show_all_live
        and premium_live_count == 0
        and raw_live_count > 0
        and scope in ("all", "live", "premium", "heute")
    )

    return {
        "configured": True,
        "today": today_s,
        "tomorrow": tomorrow_s,
        "errors": errors,
        "sections": sections,
        "total_fixtures": len(filtered),
        "league_names": league_name_map(),
        "premium_live_count": premium_live_count,
        "raw_live_count": raw_live_count,
        "show_all_live_prompt": show_prompt,
        "premium_only": premium_only,
        "show_all_live": show_all_live,
    }


def _team_standing_row(standings_payload: list[dict[str, Any]], team_id: int) -> dict[str, Any] | None:
    if not standings_payload:
        return None
    try:
        groups = (standings_payload[0].get("league") or {}).get("standings") or []
        rows = groups[0] if groups else []
        for row in rows:
            tid = (row.get("team") or {}).get("id")
            if int(tid) == int(team_id):
                return row
    except (TypeError, ValueError, IndexError):
        return None
    return None


def _form_from_fixtures(fixtures: list[dict[str, Any]], team_id: int) -> str:
    chars: list[str] = []
    for fx in fixtures[:5]:
        teams = fx.get("teams") or {}
        goals = fx.get("goals") or {}
        home = teams.get("home") or {}
        away = teams.get("away") or {}
        try:
            gh, ga = int(goals.get("home")), int(goals.get("away"))
        except (TypeError, ValueError):
            continue
        hid, aid = home.get("id"), away.get("id")
        if int(hid) == int(team_id):
            if gh > ga:
                chars.append("W")
            elif gh < ga:
                chars.append("L")
            else:
                chars.append("D")
        elif int(aid) == int(team_id):
            if ga > gh:
                chars.append("W")
            elif ga < gh:
                chars.append("L")
            else:
                chars.append("D")
    return " ".join(chars) if chars else "—"


def fetch_match_detail(
    service: FootballService,
    fixture_id: int,
    *,
    username: str,
    session_plan: str,
) -> dict[str, Any]:
    rank = football_plan_rank(session_plan or "none")
    detail: dict[str, Any] = {
        "fixture_id": fixture_id,
        "missing": [],
        "plan": session_plan,
    }

    try:
        fixture = service.get_fixture(fixture_id, username=username)
    except FootballAPIError as exc:
        detail["error"] = str(exc)
        return detail
    if not fixture:
        detail["error"] = "Spiel nicht gefunden."
        return detail

    detail["card"] = parse_match_card(fixture)
    home_name, away_name = fixture_team_names(fixture)
    teams = fixture.get("teams") or {}
    home_id = (teams.get("home") or {}).get("id")
    away_id = (teams.get("away") or {}).get("id")
    league_id = _league_id(fixture)
    season = int((fixture.get("league") or {}).get("season") or FOOTBALL_DEFAULT_SEASON)

    if rank >= 1:
        detail["summary"] = {
            "home": home_name,
            "away": away_name,
            "league": (fixture.get("league") or {}).get("name") or "",
            "venue": detail["card"].get("venue") or "",
        }
        if league_id:
            try:
                detail["standings"] = service.get_standings(
                    int(league_id), season=season, username=username
                )
            except FootballAPIError:
                detail["missing"].append("standings")
        if home_id:
            detail["home_standing"] = _team_standing_row(
                detail.get("standings") or [], int(home_id)
            )
        if away_id:
            detail["away_standing"] = _team_standing_row(
                detail.get("standings") or [], int(away_id)
            )

    if rank >= 2:
        for key, fn in (
            ("lineups", lambda: service.get_fixture_lineups(fixture_id, username=username)),
            ("events", lambda: service.get_fixture_events(fixture_id, username=username)),
            ("predictions", lambda: service.get_fixture_predictions(fixture_id, username=username)),
        ):
            try:
                detail[key] = fn()
            except FootballAPIError:
                detail["missing"].append(key)

        if home_id and away_id:
            try:
                detail["h2h"] = service.get_head_to_head(
                    int(home_id), int(away_id), last_count=5, username=username
                )
            except FootballAPIError:
                detail["missing"].append("h2h")

        if home_id and away_id:
            try:
                detail["home_form_fixtures"] = service.get_recent_fixtures(
                    int(home_id), last_count=5, username=username
                )
                detail["away_form_fixtures"] = service.get_recent_fixtures(
                    int(away_id), last_count=5, username=username
                )
                detail["home_form"] = _form_from_fixtures(
                    detail.get("home_form_fixtures") or [], int(home_id)
                )
                detail["away_form"] = _form_from_fixtures(
                    detail.get("away_form_fixtures") or [], int(away_id)
                )
            except FootballAPIError:
                detail["missing"].append("form")

        for side, tid in (("home_injuries", home_id), ("away_injuries", away_id)):
            if tid:
                try:
                    detail[side] = service.get_team_injuries(
                        int(tid), season=season, username=username
                    )
                except FootballAPIError:
                    detail["missing"].append(side)

        pred_rows = detail.get("predictions") or []
        if pred_rows:
            detail["prediction_insights"] = parse_prediction_insights(pred_rows[0])

        try:
            odds_rows = service.get_fixture_odds(fixture_id, username=username)
            detail["odds"] = parse_fixture_odds_payload(odds_rows)
        except FootballAPIError:
            detail["missing"].append("odds")

    return detail
