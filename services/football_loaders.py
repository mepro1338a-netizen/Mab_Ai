"""Fixture loading, filtering, and dashboard assembly for football UI."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable
from zoneinfo import ZoneInfo

from config import (
    FOOTBALL_BETTING_CORE_LEAGUE_IDS,
    FOOTBALL_LEAGUE_META,
    FOOTBALL_LEAGUE_PRIORITY,
    FOOTBALL_LEAGUE_TIER,
    FOOTBALL_LIVE_SORT_PRIORITY,
    FOOTBALL_PREMIUM_LEAGUE_IDS,
    FOOTBALL_UPCOMING_HORIZON_DAYS,
)
from services.football_service import FootballAPIError, FootballService

_FB_TZ = ZoneInfo("Europe/Berlin")
LIVE_STATUSES = frozenset({"1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"})
FINISHED_STATUSES = frozenset({"FT", "AET", "PEN", "AWD", "WO"})
_TIER_SCORE = {0: 50_000, 1: 40_000, 2: 30_000, 3: 20_000, 4: 5_000, 5: 1_000}
_BLOCKED = (
    "u17", "u-17", " u17", "u19", "u21", "u23", "u20", "u18", "youth", "women",
    "woman", "feminin", "frauen", "reserve", " ii", "amateur", " usl", "usl ",
    "canadian premier", "canada premier", "sudan", "queensland", "tasmania",
    "regionalliga", "3. liga", "4. liga", "landesliga", "tercera", "fourth",
    "fourth division", "development league", "premier league 2", "feminine",
    " frauen", "npl", " 2 team", "reserve league", "primera b", "segunda b",
    "third league", "isthmian", "national league north",
)

FEED_CAP_DEFAULT = 10
FEED_CAP_RAW = 50
FEED_MIN_SCORE_DEFAULT = 30
FEED_MIN_SCORE_RAW = 1

_MAJOR_COUNTRIES = frozenset({
    "germany", "deutschland", "england", "spain", "italy", "france", "portugal",
    "netherlands", "holland", "belgium", "austria", "switzerland", "scotland", "wales",
    "ireland", "poland", "czech-republic", "czechia", "croatia", "serbia", "denmark",
    "sweden", "norway", "finland", "turkey", "greece", "ukraine", "russia",
    "usa", "united-states", "mexico", "brazil", "argentina", "colombia", "chile",
    "uruguay", "japan", "south-korea", "korea-republic", "australia", "canada",
    "europe", "world", "international",
})

_EXOTIC_COUNTRIES = frozenset({
    "algeria", "iran", "iraq", "mali", "gabon", "aruba", "libya", "syria", "yemen",
    "oman", "kuwait", "bahrain", "jordan", "lebanon", "palestine", "bangladesh",
    "myanmar", "cambodia", "laos", "mongolia", "uzbekistan", "turkmenistan",
    "bolivia", "paraguay", "nicaragua", "honduras", "el-salvador", "jamaica",
    "haiti", "kenya", "uganda", "tanzania", "zambia", "zimbabwe", "mozambique",
    "angola", "ghana", "nigeria", "senegal", "tunisia", "morocco", "egypt",
    "venezuela", "ecuador", "peru", "panama", "costa-rica", "guatemala",
})

_TOP_LEAGUE_HINTS = (
    "premier league", "la liga", "serie a", "ligue 1", "bundesliga", "eredivisie",
    "primeira", "super lig", "championship", "2. bundesliga", "world cup", "euro",
    "nations league", "champions", "europa", "conference", "dfb", "fa cup",
    "copa del rey", "mls", "liga mx", "brasileir", "serie a",
)

_YOUTH_MARKERS = ("u17", "u-17", "u19", "u21", "u23", "u20", "u18", "youth", "junior")
_WOMEN_MARKERS = ("women", "woman", "feminin", "frauen", "feminine", " damen")
_LOW_TIER_MARKERS = (
    "regionalliga", "3. liga", "4. liga", "landesliga", "tercera", "fourth",
    "reserve", " ii", " usl", "usl ", "development", "premier league 2", "npl",
    "isthmian", "national league north", "primera b", "segunda b", "third league",
    "serie c", "serie d", "2. liga", "asean", "ykkönen", "ykkonen",
    "ii liga", "ettan", "persha liga", "tournoi", "revello", "concacaf",
)


def _league_id(fixture: dict[str, Any]) -> int | None:
    try:
        return int((fixture.get("league") or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def is_blocked_league_name(name: str) -> bool:
    low = (name or "").lower()
    return any(part in low for part in _BLOCKED)


def league_tier(league_id: int | None) -> int:
    return 99 if league_id is None else int(FOOTBALL_LEAGUE_TIER.get(int(league_id), 99))


def is_premium_league(league_id: int | None) -> bool:
    return bool(league_id) and int(league_id) in FOOTBALL_PREMIUM_LEAGUE_IDS


def _names_match_premium(api_name: str, meta_name: str) -> bool:
    api, meta = (api_name or "").lower().strip(), (meta_name or "").lower().strip()
    if not api or not meta or (api != meta and meta not in api and api not in meta):
        return False
    if meta == "premier league" and "championship" in api:
        return False
    if meta == "1. bundesliga" and api.startswith("2."):
        return False
    if meta == "2. bundesliga" and "1." in api and "2." not in api:
        return False
    return True


def _country_matches_premium(api_country: str, meta_country: str) -> bool:
    api, meta = (api_country or "").lower().strip(), (meta_country or "").lower().strip()
    if not meta or not api or api == meta:
        return True
    groups = ({"germany", "deutschland"}, {"england", "uk"}, {"netherlands", "holland"})
    return any(meta in g and api in g for g in groups)


def is_premium_league_match(league_id: int | None, league_name: str = "", country: str = "") -> bool:
    low = (league_name or "").lower().strip()
    if is_blocked_league_name(league_name):
        return False
    if any(x in low for x in ("concacaf", "afc ", " caf ", "copa libertadores", "copa sudamericana")):
        return False
    if league_id and int(league_id) in FOOTBALL_PREMIUM_LEAGUE_IDS:
        return True
    if not low:
        return False
    api_country = (country or "").lower().strip()
    for lid, meta in FOOTBALL_LEAGUE_META.items():
        if int(lid) not in FOOTBALL_PREMIUM_LEAGUE_IDS:
            continue
        meta_name, meta_country = str(meta.get("name") or ""), str(meta.get("country") or "")
        if not _names_match_premium(low, meta_name) or not _country_matches_premium(api_country, meta_country):
            continue
        if "champions league" in low and "uefa" not in low:
            if meta_country.lower() != "europe" or api_country not in ("europe", ""):
                continue
        return True
    return False


def filter_blocked_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        fx for fx in fixtures or []
        if not is_blocked_league_name(str((fx.get("league") or {}).get("name") or ""))
    ]


def filter_premium_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fx in fixtures or []:
        league = fx.get("league") or {}
        try:
            lid = int(league.get("id") or 0) or None
        except (TypeError, ValueError):
            lid = None
        if is_premium_league_match(lid, str(league.get("name") or ""), str(league.get("country") or "")):
            out.append(fx)
    return out


def relevance_score(*, league_id: int | None, live: bool = False, finished: bool = False) -> int:
    tier = league_tier(league_id)
    prio = int(FOOTBALL_LEAGUE_PRIORITY.get(int(league_id or 0), 99))
    score = _TIER_SCORE.get(tier, 0) + (60_000 if live else 0 if finished else 8_000)
    return score - prio * 50 - tier * 10


def is_featured_league(league_id: int | None) -> bool:
    return bool(league_id) and league_tier(league_id) <= 2


def is_betting_core_fixture(fixture: dict[str, Any]) -> bool:
    league = fixture.get("league") or {}
    name, country = str(league.get("name") or "").lower(), str(league.get("country") or "").lower()
    if is_blocked_league_name(name) or any(p in f"{name} {country}" for p in _BLOCKED):
        return False
    if "serie a" in name and country in ("brazil", "brasil"):
        return False
    return _league_id(fixture) in FOOTBALL_BETTING_CORE_LEAGUE_IDS


def filter_betting_core_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [fx for fx in fixtures or [] if is_betting_core_fixture(fx)]


def _fixture_league_context(fixture: dict[str, Any]) -> tuple[str, str, int | None]:
    league = fixture.get("league") or {}
    name = str(league.get("name") or "").lower()
    country = str(league.get("country") or "").lower().replace(" ", "-")
    return name, country, _league_id(fixture)


def fixture_feed_relevance_score(fixture: dict[str, Any]) -> int:
    """Beta feed score — higher = more relevant for default view."""
    name, country, lid = _fixture_league_context(fixture)
    country_spaced = country.replace("-", " ")
    blob = f"{name} {country}"

    if is_blocked_league_name(name):
        return -200

    score = 0

    if is_betting_core_fixture(fixture) or (lid and int(lid) in FOOTBALL_PREMIUM_LEAGUE_IDS):
        score += 100
    elif is_premium_league_match(lid, name, country_spaced):
        score += 100

    if any(m in name for m in ("world cup", "euro championship", "euro ", "nations league")):
        score += 80
    elif "friendl" in name:
        if country in _MAJOR_COUNTRIES and country not in ("world", "international"):
            score += 80
        else:
            score -= 50
    elif country in _MAJOR_COUNTRIES and any(h in name for h in _TOP_LEAGUE_HINTS):
        score += 60
    elif country in _MAJOR_COUNTRIES:
        score += 40

    if any(m in blob for m in _YOUTH_MARKERS):
        score -= 100
    if any(m in blob for m in _WOMEN_MARKERS):
        score -= 80
    if any(m in blob for m in _LOW_TIER_MARKERS):
        score -= 80
    if country in _EXOTIC_COUNTRIES:
        score -= 70
    if "friendl" in name and country not in _MAJOR_COUNTRIES:
        score -= 60

    st = _status_short(fixture)
    if st in LIVE_STATUSES:
        score += 15

    return score


def curate_feed_fixtures(
    fixtures: list[dict[str, Any]],
    *,
    min_score: int = FEED_MIN_SCORE_DEFAULT,
    max_count: int = FEED_CAP_DEFAULT,
) -> list[dict[str, Any]]:
    """Sort by relevance and cap — curated feed, not API dump."""
    pool = dedupe_fixtures(fixtures or [])
    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for fx in pool:
        pts = fixture_feed_relevance_score(fx)
        if pts > min_score:
            kickoff = str((fx.get("fixture") or {}).get("date") or "")
            ranked.append((pts, kickoff, fx))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return [fx for _, _, fx in ranked[: max(1, int(max_count))]]


def _local_today_tomorrow() -> tuple[str, str]:
    today = datetime.now(_FB_TZ).date()
    return today.isoformat(), (today + timedelta(days=1)).isoformat()


def _fixture_date(fixture: dict[str, Any]) -> str:
    raw = str((fixture.get("fixture") or {}).get("date") or "")
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_FB_TZ)
        return dt.astimezone(_FB_TZ).date().isoformat()
    except ValueError:
        return raw[:10]


def _status_short(fixture: dict[str, Any]) -> str:
    return str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "NS")


def _elapsed(fixture: dict[str, Any]) -> int | None:
    val = ((fixture.get("fixture") or {}).get("status") or {}).get("elapsed")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


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
        if key not in seen:
            seen.add(key)
            out.append(fx)
    return out


def sort_fixtures_priority(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def _key(fx: dict[str, Any]) -> tuple:
        lid = _league_id(fx)
        tier = league_tier(lid)
        st = _status_short(fx)
        live, finished = st in LIVE_STATUSES, st in FINISHED_STATUSES
        live_prio = int(FOOTBALL_LIVE_SORT_PRIORITY.get(int(lid or 0), 500 + tier * 10))
        return (
            0 if live else 1, live_prio,
            int(FOOTBALL_LEAGUE_PRIORITY.get(lid or 0, 99)),
            -relevance_score(league_id=lid, live=live, finished=finished),
            str((fx.get("fixture") or {}).get("date") or ""),
        )
    return sorted(fixtures or [], key=_key)


def sort_fixtures_by_priority(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sort_fixtures_priority(fixtures)


def parse_match_card(fixture: dict[str, Any]) -> dict[str, Any]:
    meta, teams = fixture.get("fixture") or {}, fixture.get("teams") or {}
    goals, league = fixture.get("goals") or {}, fixture.get("league") or {}
    home, away = teams.get("home") or {}, teams.get("away") or {}
    status = _status_short(fixture)
    gh, ga = goals.get("home"), goals.get("away")
    live, finished = status in LIVE_STATUSES, status in FINISHED_STATUSES
    if gh is not None and ga is not None:
        score = f"{gh}:{ga}"
    elif live or finished:
        score = "–:–"
    else:
        score = ""
    minute = _elapsed(fixture)
    status_label = f"{status} {minute}'" if status in LIVE_STATUSES and minute is not None else status
    date_raw = str(meta.get("date") or "")
    try:
        lid_int = int(league.get("id")) if league.get("id") is not None else None
    except (TypeError, ValueError):
        lid_int = None
    try:
        home_id = int(home.get("id")) if home.get("id") is not None else None
    except (TypeError, ValueError):
        home_id = None
    try:
        away_id = int(away.get("id")) if away.get("id") is not None else None
    except (TypeError, ValueError):
        away_id = None
    try:
        season = int(league.get("season")) if league.get("season") is not None else None
    except (TypeError, ValueError):
        season = None
    return {
        "fixture_id": meta.get("id"), "home": home.get("name") or "Home", "away": away.get("name") or "Away",
        "home_id": home_id, "away_id": away_id, "season": season,
        "home_logo": home.get("logo") or "", "away_logo": away.get("logo") or "", "score": score,
        "status": status, "status_label": status_label, "minute": minute,
        "league": league.get("name") or "", "league_id": league.get("id"), "league_logo": league.get("logo") or "",
        "country": league.get("country") or "", "date": _fixture_date(fixture),
        "time": date_raw[11:16] if "T" in date_raw else "",
        "venue": (meta.get("venue") or {}).get("name") or "", "city": (meta.get("venue") or {}).get("city") or "",
        "live": live, "finished": finished, "tier": league_tier(lid_int),
        "featured": is_featured_league(lid_int), "premium": is_premium_league(lid_int),
        "relevance_score": relevance_score(league_id=lid_int, live=live, finished=finished),
    }


def classify_fixtures(
    fixtures: list[dict[str, Any]], *, today: str, tomorrow: str,
) -> dict[str, list[dict[str, Any]]]:
    live_now, later_today, finished_today, tomorrow_list = [], [], [], []
    for fx in fixtures:
        d, st = _fixture_date(fx), _status_short(fx)
        if st in LIVE_STATUSES:
            live_now.append(fx)
        elif d == tomorrow:
            tomorrow_list.append(fx)
        elif d == today:
            (finished_today if st in FINISHED_STATUSES else later_today).append(fx)
    return {
        "live_now": sort_fixtures_by_priority(live_now),
        "later_today": sort_fixtures_by_priority(later_today),
        "finished_today": sort_fixtures_by_priority(finished_today),
        "tomorrow": sort_fixtures_by_priority(tomorrow_list),
    }


def _fetch_rows(fn: Callable[[], list[dict[str, Any]]], errors: list[str]) -> list[dict[str, Any]]:
    try:
        return fn()
    except FootballAPIError as exc:
        errors.append(str(exc))
        return []


def fetch_premium_dashboard(
    service: FootballService,
    *,
    username: str,
    include_live: bool = False,
    include_raw: bool = False,
) -> dict[str, Any]:
    today_s, tomorrow_s = _local_today_tomorrow()
    errors: list[str] = []
    empty = {
        "configured": False, "today": today_s,
        "errors": ["API-Football ist nicht konfiguriert (FOOTBALL_API_KEY)."],
        "top_matches": [], "live_now": [], "all_premium": [], "next_matches": [], "extended": [],
        "premium_count": 0,
        "raw_live_count": 0,
        "raw_today_count": 0,
        "raw_tomorrow_count": 0,
        "show_international_prompt": False,
        "include_live": include_live,
        "include_raw": include_raw,
    }
    if not service.is_configured():
        return empty

    upcoming_rows = _fetch_rows(
        lambda: service.get_premium_fixtures_upcoming(
            days=FOOTBALL_UPCOMING_HORIZON_DAYS,
            username=username,
        ),
        errors,
    )
    live_rows: list[dict[str, Any]] = []
    if include_live:
        live_rows = _fetch_rows(lambda: service.get_live_fixtures(username=username), errors)

    raw_today: list[dict[str, Any]] = []
    raw_tomorrow: list[dict[str, Any]] = []
    if include_raw:
        raw_today = _fetch_rows(
            lambda: service.get_fixtures_by_date(today_s, username=username),
            errors,
        )
        raw_tomorrow = _fetch_rows(
            lambda: service.get_fixtures_by_date(tomorrow_s, username=username),
            errors,
        )

    load_report = getattr(service, "_premium_load_report", None) or {}
    from config import FOOTBALL_TOPSPIELE_LEAGUE_IDS

    def _topspiele_only(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for fx in items or []:
            try:
                lid = int((fx.get("league") or {}).get("id") or 0)
            except (TypeError, ValueError):
                continue
            if lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS:
                out.append(fx)
        return out

    all_upcoming = _topspiele_only(dedupe_fixtures(upcoming_rows))
    if not all_upcoming and int(load_report.get("date_fallback") or 0) > 0:
        errors.append(
            "Heute keine Spiele in Bundesliga, UEFA oder Top-Ligen im gewählten Zeitraum. "
            "Nächste Topspiele erscheinen sobald die API sie liefert."
        )
    today_premium = [fx for fx in all_upcoming if _fixture_date(fx) == today_s]
    tomorrow_premium = [fx for fx in all_upcoming if _fixture_date(fx) == tomorrow_s]
    premium_live = _topspiele_only(live_rows)
    premium_fixtures = dedupe_fixtures(premium_live + all_upcoming)

    sections = classify_fixtures(premium_fixtures, today=today_s, tomorrow=tomorrow_s)
    live_now = list(sections.get("live_now") or premium_live) or sort_fixtures_by_priority(premium_live)
    today_pool = dedupe_fixtures(
        (sections.get("live_now") or []) + (sections.get("later_today") or []) + (sections.get("finished_today") or [])
    )
    top_matches = sort_fixtures_by_priority(today_pool)[:5]
    all_premium = sort_fixtures_by_priority(all_upcoming)
    live_now_cards = [parse_match_card(fx) for fx in live_now[:4]]
    show_intl = False

    return {
        "configured": True, "today": today_s, "tomorrow": tomorrow_s, "errors": errors,
        "top_matches": top_matches, "live_now": live_now, "all_premium": all_premium,
        "next_matches": all_upcoming,
        "extended": [],
        "live_now_cards": live_now_cards,
        "load_report": getattr(service, "_premium_load_report", None),
        "premium_count": len(all_premium),
        "raw_live_count": len(live_rows),
        "raw_today_count": 0,
        "raw_tomorrow_count": 0,
        "show_international_prompt": show_intl, "show_live_intl_prompt": show_intl and not live_now,
        "non_premium_live_count": max(0, len(live_rows) - len(premium_live)),
        "include_live": include_live,
        "include_raw": include_raw,
        "today_local": today_s,
        "tomorrow_fixtures": sort_fixtures_by_priority(tomorrow_premium),
        "raw_live": live_rows,
        "raw_today": raw_today,
        "raw_tomorrow": raw_tomorrow,
    }
