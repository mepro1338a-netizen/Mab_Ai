"""Curated league catalog — premium-first, no low-tier noise by default."""
from __future__ import annotations

from typing import Any

from config import (
    FOOTBALL_LEAGUE_GROUPS,
    FOOTBALL_LEAGUE_META,
    FOOTBALL_LEAGUE_PRIORITY,
    FOOTBALL_LEAGUE_TIER,
    FOOTBALL_LIVE_SORT_PRIORITY,
    FOOTBALL_PREMIUM_LEAGUE_IDS,
)

LEAGUE_CATALOG: dict[str, list[dict[str, Any]]] = {
    k: list(v) for k, v in FOOTBALL_LEAGUE_GROUPS.items()
}

LIVE_STATUSES = frozenset({"1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"})
FINISHED_STATUSES = frozenset({"FT", "AET", "PEN", "AWD", "WO"})
SCHEDULED_STATUSES = frozenset({"NS", "TBD", "PST", "SUSP"})

# Tier weights for sort — higher = shown first
_TIER_SCORE = {
    0: 50_000,  # Deutschland
    1: 40_000,  # UEFA
    2: 30_000,  # Topligen
    3: 20_000,  # National
    4: 5_000,   # Secondary (3. Liga etc.)
    5: 1_000,   # International low-tier
}


def premium_league_ids() -> frozenset[int]:
    return FOOTBALL_PREMIUM_LEAGUE_IDS


# Block youth / reserve / amateur leagues even if API returns them in live=all
_BLOCKED_LEAGUE_NAME_PARTS = (
    "u19",
    "u21",
    "u23",
    "u20",
    "u18",
    "youth",
    "reserve",
    "amateur",
    "regionalliga",
    "3. liga",
    "tercera",
    "fourth",
    "fourth division",
)


def extended_league_ids() -> frozenset[int]:
    """Phase 2: no extended/low-tier leagues."""
    return frozenset()


def is_blocked_league_name(name: str) -> bool:
    low = (name or "").lower()
    return any(part in low for part in _BLOCKED_LEAGUE_NAME_PARTS)


def all_curated_league_ids() -> frozenset[int]:
    return frozenset(FOOTBALL_LEAGUE_META.keys())


def all_league_ids() -> set[int]:
    return set(FOOTBALL_LEAGUE_META.keys())


def league_name_map() -> dict[int, str]:
    return {lid: str(meta.get("name") or "") for lid, meta in FOOTBALL_LEAGUE_META.items()}


def league_tier(league_id: int | None) -> int:
    if league_id is None:
        return 99
    return int(FOOTBALL_LEAGUE_TIER.get(int(league_id), 99))


def is_premium_league(league_id: int | None) -> bool:
    if not league_id:
        return False
    return int(league_id) in FOOTBALL_PREMIUM_LEAGUE_IDS


def relevance_score(
    *,
    league_id: int | None,
    live: bool = False,
    finished: bool = False,
) -> int:
    """Higher = more important. Drives Top Matches & tip selection."""
    tier = league_tier(league_id)
    prio = int(FOOTBALL_LEAGUE_PRIORITY.get(int(league_id or 0), 99))
    score = _TIER_SCORE.get(tier, 0)
    if live:
        score += 60_000
    elif not finished:
        score += 8_000
    score -= prio * 50
    score -= tier * 10
    return score


def is_featured_league(league_id: int | None) -> bool:
    """Top-tier highlight (DE + UEFA + Top-5 leagues)."""
    if not league_id:
        return False
    return league_tier(league_id) <= 2


def filter_premium_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only curated premium leagues — default for all Football AI views."""
    pids = premium_league_ids()
    out: list[dict[str, Any]] = []
    for fx in fixtures or []:
        try:
            lid = int((fx.get("league") or {}).get("id") or 0)
        except (TypeError, ValueError):
            continue
        if lid not in pids:
            continue
        league_name = str((fx.get("league") or {}).get("name") or "")
        if is_blocked_league_name(league_name):
            continue
        out.append(fx)
    return out


def filter_extended_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Non-premium curated leagues only (3. Liga, MLS, …) — never random API dump."""
    ext = extended_league_ids()
    out: list[dict[str, Any]] = []
    for fx in fixtures or []:
        try:
            lid = int((fx.get("league") or {}).get("id") or 0)
        except (TypeError, ValueError):
            continue
        if lid in ext:
            out.append(fx)
    return out


def fixture_league_id(fixture: dict[str, Any]) -> int | None:
    try:
        lid = int((fixture.get("league") or {}).get("id") or 0)
        return lid or None
    except (TypeError, ValueError):
        return None


def sort_fixtures_priority(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort: live → DE → UEFA → Top → National → rest."""

    def _status(fx: dict[str, Any]) -> str:
        return str(((fx.get("fixture") or {}).get("status") or {}).get("short") or "NS")

    def _key(fx: dict[str, Any]) -> tuple:
        lid = fixture_league_id(fx)
        tier = league_tier(lid)
        live = _status(fx) in LIVE_STATUSES
        finished = _status(fx) in FINISHED_STATUSES
        meta = fx.get("fixture") or {}
        live_prio = int(FOOTBALL_LIVE_SORT_PRIORITY.get(int(lid or 0), 500 + tier * 10))
        return (
            0 if live else 1,
            live_prio,
            int(FOOTBALL_LEAGUE_PRIORITY.get(lid or 0, 99)),
            -relevance_score(league_id=lid, live=live, finished=finished),
            str(meta.get("date") or ""),
        )

    return sorted(fixtures or [], key=_key)


def league_ids_for_view(view: str, favorites: list[int] | None = None) -> set[int] | None:
    if view in ("alle", "international", "extended"):
        return None
    if view == "deutschland":
        return {int(lg["id"]) for lg in LEAGUE_CATALOG.get("deutschland", [])}
    if view == "england":
        return {int(lg["id"]) for lg in LEAGUE_CATALOG.get("england", [])}
    if view == "europa":
        ids: set[int] = set()
        for grp in ("uefa", "england", "europa_top"):
            ids.update(int(lg["id"]) for lg in LEAGUE_CATALOG.get(grp, []))
        return ids
    if view == "favoriten":
        fav = favorites or []
        return {int(i) for i in fav if int(i) in FOOTBALL_LEAGUE_META}
    return set(FOOTBALL_PREMIUM_LEAGUE_IDS)
