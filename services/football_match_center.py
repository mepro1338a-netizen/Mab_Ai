"""Live Match Center — fixture grouping, filtering, match detail bundles."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from config import FOOTBALL_DEFAULT_SEASON, FOOTBALL_LEAGUE_PRIORITY, FOOTBALL_LEAGUE_TIER, football_plan_rank
from services.football_leagues import (
    FINISHED_STATUSES,
    LIVE_STATUSES,
    SCHEDULED_STATUSES,
    extended_league_ids,
    is_featured_league,
    is_premium_league,
    league_name_map,
    league_tier,
    premium_league_ids,
    relevance_score,
)
from services.football_odds import parse_fixture_odds_payload, parse_prediction_insights
from services.football_service import FootballAPIError, FootballService, fixture_team_names

_FB_TZ = ZoneInfo("Europe/Berlin")


def _league_id(fixture: dict[str, Any]) -> int | None:
    try:
        return int((fixture.get("league") or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def _local_today_tomorrow() -> tuple[str, str]:
    now = datetime.now(_FB_TZ)
    today = now.date()
    return today.isoformat(), (today + timedelta(days=1)).isoformat()


def _fixture_date(fixture: dict[str, Any]) -> str:
    raw = str((fixture.get("fixture") or {}).get("date") or "")
    if not raw:
        return ""
    try:
        normalized = raw.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_FB_TZ)
        return dt.astimezone(_FB_TZ).date().isoformat()
    except ValueError:
        return raw[:10] if raw else ""


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
        "premium": is_premium_league(lid_int),
        "relevance_score": relevance_score(league_id=lid_int, live=live, finished=finished),
    }


def _status_short(fixture: dict[str, Any]) -> str:
    return str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "NS")


def _elapsed(fixture: dict[str, Any]) -> int | None:
    val = ((fixture.get("fixture") or {}).get("status") or {}).get("elapsed")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


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
        if league_ids:
            if lid is None or int(lid) not in league_ids:
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
    from services.football_leagues import sort_fixtures_priority
    return sort_fixtures_priority(fixtures)


def _sorted_league_ids(league_ids: set[int]) -> list[int]:
    return sorted(
        league_ids,
        key=lambda lid: (
            FOOTBALL_LEAGUE_TIER.get(int(lid), 99),
            FOOTBALL_LEAGUE_PRIORITY.get(int(lid), 99),
        ),
    )


def _fetch_by_leagues(
    service: FootballService,
    date_s: str,
    league_ids: set[int],
    *,
    username: str,
    max_leagues: int = 18,
) -> list[dict[str, Any]]:
    """Reliable path: fixtures per league+date (finds Bundesliga etc.)."""
    rows: list[dict[str, Any]] = []
    for lid in _sorted_league_ids(league_ids)[:max_leagues]:
        try:
            rows.extend(
                service.get_fixtures_by_date(
                    date_s,
                    league_id=int(lid),
                    username=username,
                )
            )
        except FootballAPIError:
            continue
    return dedupe_fixtures(rows)


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
        else:
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
    show_all_live: bool = False,
    view: str = "top",
) -> dict[str, Any]:
    today_s, tomorrow_s = _local_today_tomorrow()
    errors: list[str] = []
    live_rows: list[dict[str, Any]] = []

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
            "today_local": today_s,
        }

    try:
        live_rows = service.get_live_fixtures(username=username)
    except FootballAPIError as exc:
        errors.append(str(exc))

    premium_ids = set(premium_league_ids())
    if show_all_live or view == "alle":
        effective_ids = None
    elif league_filter is not None:
        effective_ids = league_filter
    else:
        effective_ids = premium_ids

    today_rows: list[dict[str, Any]] = []
    tomorrow_rows: list[dict[str, Any]] = []

    if effective_ids:
        if view in ("top", "heute", "deutschland", "europa", "live"):
            today_rows = _fetch_by_leagues(
                service, today_s, effective_ids, username=username
            )
        if view in ("top", "morgen"):
            tomorrow_rows = _fetch_by_leagues(
                service, tomorrow_s, effective_ids, username=username
            )
    else:
        try:
            today_rows = service.get_fixtures_by_date(today_s, username=username)
        except FootballAPIError as exc:
            errors.append(str(exc))
        if view in ("top", "morgen"):
            try:
                tomorrow_rows = service.get_fixtures_by_date(tomorrow_s, username=username)
            except FootballAPIError as exc:
                errors.append(str(exc))

    merged = dedupe_fixtures(live_rows + today_rows + tomorrow_rows)

    if effective_ids is not None:
        filtered = filter_fixtures(merged, league_ids=effective_ids, country=country_filter)
        live_filtered = filter_fixtures(live_rows, league_ids=effective_ids, country=country_filter)
    else:
        filtered = filter_fixtures(merged, league_ids=None, country=country_filter)
        live_filtered = live_rows

    if view == "live":
        filtered = live_filtered or [
            fx for fx in filtered if _status_short(fx) in LIVE_STATUSES
        ]
    elif view == "heute":
        filtered = [
            fx for fx in filtered
            if _fixture_date(fx) == today_s or _status_short(fx) in LIVE_STATUSES
        ]
    elif view == "morgen":
        filtered = [fx for fx in filtered if _fixture_date(fx) == tomorrow_s]

    sections = classify_fixtures(filtered, today=today_s, tomorrow=tomorrow_s)

    if view == "live" and not sections.get("live_now") and filtered:
        sections["live_now"] = sort_fixtures_by_priority(
            [fx for fx in filtered if _status_short(fx) in LIVE_STATUSES]
        )

    premium_live_count = len(filter_fixtures(live_rows, league_ids=premium_ids))
    raw_live_count = len(live_rows)
    show_prompt = (
        not show_all_live
        and view in ("top", "live")
        and premium_live_count == 0
        and raw_live_count > 0
        and effective_ids == premium_ids
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
        "today_local": today_s,
    }


def fetch_premium_dashboard(
    service: FootballService,
    *,
    username: str,
    include_all_leagues: bool = False,
) -> dict[str, Any]:
    """
    Premium-first dashboard payload — no low-tier leagues unless include_all_leagues.
    Sections: top_matches (max 5), live_now, all_premium_today, extended_fixtures.
    """
    today_s, tomorrow_s = _local_today_tomorrow()
    errors: list[str] = []
    premium_ids = set(premium_league_ids())

    if not service.is_configured():
        return {
            "configured": False,
            "today": today_s,
            "errors": ["API-Football ist nicht konfiguriert (FOOTBALL_API_KEY)."],
            "top_matches": [],
            "live_now": [],
            "all_premium": [],
            "extended": [],
            "premium_count": 0,
            "raw_live_count": 0,
            "show_international_prompt": False,
            "include_all_leagues": include_all_leagues,
        }

    live_rows: list[dict[str, Any]] = []
    try:
        live_rows = service.get_live_fixtures(username=username)
    except FootballAPIError as exc:
        errors.append(str(exc))

    today_premium = _fetch_by_leagues(
        service, today_s, premium_ids, username=username, max_leagues=24
    )
    merged = dedupe_fixtures(live_rows + today_premium)
    premium_fixtures = filter_fixtures(merged, league_ids=premium_ids)
    premium_live = filter_fixtures(live_rows, league_ids=premium_ids)

    sections = classify_fixtures(premium_fixtures, today=today_s, tomorrow=tomorrow_s)
    live_now = list(sections.get("live_now") or premium_live)
    if not live_now and premium_live:
        live_now = sort_fixtures_by_priority(premium_live)

    today_pool: list[dict[str, Any]] = []
    today_pool.extend(sections.get("live_now") or [])
    today_pool.extend(sections.get("later_today") or [])
    today_pool.extend(sections.get("finished_today") or [])
    today_pool = dedupe_fixtures(today_pool)
    today_sorted = sort_fixtures_by_priority(today_pool)

    top_matches = today_sorted[:5]
    all_premium = sort_fixtures_by_priority(premium_fixtures)

    extended: list[dict[str, Any]] = []
    if include_all_leagues:
        ext_ids = set(extended_league_ids())
        # Curated non-premium leagues only — per-league fetch (no global API dump)
        extended = _fetch_by_leagues(
            service, today_s, ext_ids, username=username, max_leagues=12
        )
        # Non-premium live spillover (e.g. MLS live while user opted in)
        for fx in live_rows:
            lid = _league_id(fx)
            if lid is None or int(lid) in premium_ids:
                continue
            if int(lid) in ext_ids:
                extended.append(fx)
        extended = sort_fixtures_by_priority(dedupe_fixtures(extended))

    raw_live_count = len(live_rows)
    non_premium_live_count = raw_live_count - len(premium_live)
    premium_count = len(all_premium)
    show_intl = not include_all_leagues and (
        (premium_count == 0 and raw_live_count > 0)
        or (len(live_now) == 0 and non_premium_live_count > 0)
    )

    return {
        "configured": True,
        "today": today_s,
        "tomorrow": tomorrow_s,
        "errors": errors,
        "top_matches": top_matches,
        "live_now": live_now,
        "all_premium": all_premium,
        "extended": extended,
        "premium_count": premium_count,
        "raw_live_count": raw_live_count,
        "show_international_prompt": show_intl,
        "show_live_intl_prompt": show_intl and len(live_now) == 0,
        "non_premium_live_count": non_premium_live_count,
        "include_all_leagues": include_all_leagues,
        "today_local": today_s,
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
