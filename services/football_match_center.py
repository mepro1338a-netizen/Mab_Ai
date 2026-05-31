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
    filter_premium_fixtures,
    is_featured_league,
    is_premium_league,
    league_name_map,
    league_tier,
    premium_league_ids,
    relevance_score,
)
from services.football_live_intel import parse_fixture_statistics, parse_xg_from_statistics
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


def _fetch_upcoming_premium(
    service: FootballService,
    league_ids: set[int],
    *,
    username: str,
    horizon_days: int = 7,
    max_leagues: int = 12,
    per_league: int = 3,
    max_results: int = 8,
) -> list[dict[str, Any]]:
    """Next premium fixtures within N days — league next=N first, then date scan fallback."""
    today_s, _ = _local_today_tomorrow()
    try:
        today_dt = datetime.fromisoformat(today_s).date()
    except ValueError:
        return []
    horizon = today_dt + timedelta(days=max(1, horizon_days))

    def _in_window(fx: dict[str, Any]) -> bool:
        d_raw = _fixture_date(fx)
        if not d_raw:
            return False
        try:
            fx_date = datetime.fromisoformat(d_raw).date()
        except ValueError:
            return False
        if fx_date <= today_dt or fx_date > horizon:
            return False
        return _status_short(fx) not in FINISHED_STATUSES

    rows: list[dict[str, Any]] = []
    for lid in _sorted_league_ids(league_ids)[:max_leagues]:
        try:
            rows.extend(
                service.get_league_upcoming_fixtures(
                    int(lid),
                    next_count=per_league,
                    username=username,
                )
            )
        except FootballAPIError:
            continue

    upcoming = [fx for fx in dedupe_fixtures(rows) if _in_window(fx)]
    if not upcoming:
        for offset in range(1, horizon_days + 1):
            day_s = (today_dt + timedelta(days=offset)).isoformat()
            try:
                day_rows = service.get_fixtures_by_date(day_s, username=username)
            except FootballAPIError:
                continue
            upcoming.extend(filter_fixtures(day_rows, league_ids=league_ids))
        upcoming = [fx for fx in dedupe_fixtures(upcoming) if _in_window(fx)]

    return sort_fixtures_by_priority(upcoming)[:max_results]


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
            "next_matches": [],
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
    premium_fixtures = filter_premium_fixtures(merged)
    premium_live = filter_premium_fixtures(live_rows)

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

    next_matches: list[dict[str, Any]] = []
    if not today_sorted:
        next_matches = _fetch_upcoming_premium(
            service, premium_ids, username=username, horizon_days=7
        )

    extended: list[dict[str, Any]] = []

    live_now_cards = _enrich_live_cards(service, live_now, username=username, max_cards=6)

    raw_live_count = len(live_rows)
    non_premium_live_count = max(0, raw_live_count - len(premium_live))
    premium_count = len(all_premium)
    show_intl = False

    return {
        "configured": True,
        "today": today_s,
        "tomorrow": tomorrow_s,
        "errors": errors,
        "top_matches": top_matches,
        "live_now": live_now,
        "all_premium": all_premium,
        "next_matches": next_matches,
        "extended": extended,
        "live_now_cards": live_now_cards,
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


def _standing_summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    all_ = row.get("all") or {}
    goals = all_.get("goals") or {}
    try:
        return {
            "rank": row.get("rank"),
            "points": row.get("points"),
            "played": all_.get("played"),
            "goals_for": goals.get("for"),
            "goals_against": goals.get("against"),
            "goal_diff": row.get("goalsDiff"),
        }
    except (TypeError, ValueError):
        return None


def _parse_suspensions(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for r in rows or []:
        typ = str(r.get("type") or "").lower()
        if "suspend" not in typ and typ not in ("red card", "yellow red"):
            continue
        pl = r.get("player") or {}
        name = pl.get("name") if isinstance(pl, dict) else str(pl or "Spieler")
        reason = str(r.get("reason") or r.get("type") or "Sperre")
        out.append({"player": str(name), "reason": reason})
    return out[:8]


def _red_cards_from_events(
    events: list[dict[str, Any]],
    *,
    home_id: int | None = None,
    away_id: int | None = None,
) -> dict[str, int]:
    home_rc, away_rc = 0, 0
    for block in events or []:
        ev_list = block.get("events") or ([block] if block.get("type") else [])
        for ev in ev_list:
            if str(ev.get("type") or "").lower() != "card":
                continue
            if "red" not in str(ev.get("detail") or "").lower():
                continue
            tid = (ev.get("team") or {}).get("id")
            try:
                tid_int = int(tid) if tid is not None else None
            except (TypeError, ValueError):
                tid_int = None
            if tid_int is not None and home_id is not None and tid_int == int(home_id):
                home_rc += 1
            elif tid_int is not None and away_id is not None and tid_int == int(away_id):
                away_rc += 1
            else:
                home_rc += 1
    return {"home": home_rc, "away": away_rc, "total": home_rc + away_rc}


def _enrich_live_cards(
    service: FootballService,
    fixtures: list[dict[str, Any]],
    *,
    username: str,
    max_cards: int = 6,
) -> list[dict[str, Any]]:
    """Attach live stats, xG, red cards to premium live cards (API budget capped)."""
    cards: list[dict[str, Any]] = []
    for fx in (fixtures or [])[:max_cards]:
        card = parse_match_card(fx)
        if not card.get("live"):
            cards.append(card)
            continue
        fid = card.get("fixture_id")
        if not fid:
            cards.append(card)
            continue
        teams = fx.get("teams") or {}
        home_id = (teams.get("home") or {}).get("id")
        away_id = (teams.get("away") or {}).get("id")
        try:
            stats_rows = service.get_fixture_statistics(int(fid), username=username)
            stats = parse_fixture_statistics(stats_rows)
            xg = parse_xg_from_statistics(stats_rows)
            h = stats.get("home") or {}
            a = stats.get("away") or {}
            card["live_possession"] = f"{h.get('possession') or '—'}% / {a.get('possession') or '—'}%"
            card["live_shots"] = f"{h.get('shots_on') or h.get('shots') or '—'} / {a.get('shots_on') or a.get('shots') or '—'}"
            if xg:
                card["live_xg"] = f"{xg.get('home_xg', '—')} / {xg.get('away_xg', '—')}"
            events = service.get_fixture_events(int(fid), username=username)
            card["red_cards"] = _red_cards_from_events(
                events, home_id=home_id, away_id=away_id
            )
        except FootballAPIError:
            pass
        cards.append(card)
    return cards


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
            detail["home_standing_summary"] = _standing_summary(detail.get("home_standing"))
        if away_id:
            detail["away_standing"] = _team_standing_row(
                detail.get("standings") or [], int(away_id)
            )
            detail["away_standing_summary"] = _standing_summary(detail.get("away_standing"))

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

        for side, tid in (("home_sidelined", home_id), ("away_sidelined", away_id)):
            if tid:
                try:
                    detail[side] = service.get_team_sidelined(
                        int(tid), season=season, username=username
                    )
                except FootballAPIError:
                    detail["missing"].append(side)

        from services.football_elite_betting_card import _parse_injuries_detail

        detail["injuries_parsed"] = _parse_injuries_detail(detail)
        home_susp = _parse_suspensions(detail.get("home_sidelined") or [])
        away_susp = _parse_suspensions(detail.get("away_sidelined") or [])
        detail["suspensions_parsed"] = {
            "home": home_susp,
            "away": away_susp,
            "available": bool(home_susp or away_susp),
        }

        pred_rows = detail.get("predictions") or []
        if pred_rows:
            detail["prediction_insights"] = parse_prediction_insights(pred_rows[0])

        try:
            odds_rows = service.get_fixture_odds(fixture_id, username=username)
            detail["odds"] = parse_fixture_odds_payload(odds_rows)
        except FootballAPIError:
            detail["missing"].append("odds")

        try:
            stats_rows = service.get_fixture_statistics(fixture_id, username=username)
            detail["fixture_statistics"] = stats_rows
            detail["match_stats"] = parse_fixture_statistics(stats_rows)
            xg = parse_xg_from_statistics(stats_rows)
            if xg:
                detail["xg"] = xg
            else:
                detail["missing"].append("xg")
        except FootballAPIError:
            detail["missing"].append("fixture_statistics")

        hf, af = detail.get("home_form"), detail.get("away_form")
        if (hf and str(hf).strip() != "—") or (af and str(af).strip() != "—"):
            detail["form"] = {"home": hf or "", "away": af or ""}

        try:
            from services.football_elite_betting_card import build_betting_intelligence_card
            from services.football_prediction_engine import build_match_prediction

            detail["prediction"] = build_match_prediction(detail)
            detail["intel"] = build_betting_intelligence_card(detail)
        except Exception:
            pass

    return detail
