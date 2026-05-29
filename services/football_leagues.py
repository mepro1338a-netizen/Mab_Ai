"""Curated league catalog for Live Match Center — backed by config.py IDs."""
from __future__ import annotations

from typing import Any

from config import (
    FOOTBALL_LEAGUE_GROUPS,
    FOOTBALL_LEAGUE_META,
    FOOTBALL_LEAGUE_PRIORITY,
    FOOTBALL_LEAGUE_TIER,
    FOOTBALL_PREMIUM_LEAGUE_IDS,
)

LEAGUE_CATALOG: dict[str, list[dict[str, Any]]] = {
    k: list(v) for k, v in FOOTBALL_LEAGUE_GROUPS.items()
}

CATEGORY_LABELS: dict[str, str] = {
    "premium": "Premium",
    "heute": "Heute",
    "live": "Live",
    "morgen": "Morgen",
    "deutschland": "Deutschland",
    "uefa": "UEFA",
    "europa_top": "Topligen",
    "national": "Nationalteams",
    "favoriten": "Favoriten",
    "alle": "Alle Ligen",
}

LIVE_STATUSES = frozenset({"1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"})
FINISHED_STATUSES = frozenset({"FT", "AET", "PEN", "AWD", "WO"})
SCHEDULED_STATUSES = frozenset({"NS", "TBD", "PST", "SUSP"})

# Featured cards: Deutschland + UEFA + Top-3 Topligen
FEATURED_LEAGUE_IDS = frozenset(
    lid
    for grp in ("deutschland", "uefa")
    for lid in (int(lg["id"]) for lg in LEAGUE_CATALOG.get(grp, []))
) | frozenset(
    int(lg["id"]) for lg in LEAGUE_CATALOG.get("europa_top", [])[:3]
)


def premium_league_ids() -> frozenset[int]:
    return FOOTBALL_PREMIUM_LEAGUE_IDS


def all_league_ids() -> set[int]:
    return set(FOOTBALL_LEAGUE_META.keys())


def league_name_map() -> dict[int, str]:
    return {lid: str(meta.get("name") or "") for lid, meta in FOOTBALL_LEAGUE_META.items()}


def league_ids_for_category(category: str, favorites: list[int] | None = None) -> set[int] | None:
    """Return league ID set for filter. None = no league restriction (alle live)."""
    if category in ("premium", "heute", "live", "morgen"):
        return set(FOOTBALL_PREMIUM_LEAGUE_IDS)
    if category == "alle":
        return None
    if category == "favoriten":
        fav = favorites or []
        return {int(i) for i in fav if int(i) in FOOTBALL_LEAGUE_META}
    if category in LEAGUE_CATALOG:
        return {int(lg["id"]) for lg in LEAGUE_CATALOG[category]}
    return set(FOOTBALL_PREMIUM_LEAGUE_IDS)


def leagues_for_category(category: str, favorites: list[int] | None = None) -> list[dict[str, Any]]:
    if category == "premium":
        out: list[dict[str, Any]] = []
        seen: set[int] = set()
        for grp in ("deutschland", "uefa", "europa_top", "national"):
            for lg in LEAGUE_CATALOG.get(grp, []):
                lid = int(lg["id"])
                if lid not in seen:
                    seen.add(lid)
                    out.append(lg)
        return out
    if category == "favoriten":
        fav = favorites or []
        lookup = {int(lg["id"]): lg for g in LEAGUE_CATALOG.values() for lg in g}
        return [lookup[i] for i in fav if i in lookup]
    if category in ("heute", "live", "morgen", "alle"):
        return []
    return list(LEAGUE_CATALOG.get(category, []))


def league_tier(league_id: int | None) -> int:
    if league_id is None:
        return 99
    return int(FOOTBALL_LEAGUE_TIER.get(int(league_id), 99))


def relevance_score(
    *,
    league_id: int | None,
    live: bool = False,
    finished: bool = False,
) -> int:
    """Higher = more important. Internal sort key only."""
    tier = league_tier(league_id)
    prio = int(FOOTBALL_LEAGUE_PRIORITY.get(int(league_id or 0), 99))
    score = 10_000
    if live:
        score += 50_000
    elif finished:
        score += 5_000
    score -= tier * 1_000
    score -= prio * 10
    if league_id and int(league_id) in FEATURED_LEAGUE_IDS:
        score += 500
    return score


def is_featured_league(league_id: int | None) -> bool:
    if not league_id:
        return False
    return int(league_id) in FEATURED_LEAGUE_IDS
