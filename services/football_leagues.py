"""Curated league catalog for Live Match Center."""
from __future__ import annotations

from typing import Any

# API-Football league IDs (v3)
LEAGUE_CATALOG: dict[str, list[dict[str, Any]]] = {
    "deutschland": [
        {"id": 78, "name": "1. Bundesliga", "country": "Germany"},
        {"id": 79, "name": "2. Bundesliga", "country": "Germany"},
        {"id": 80, "name": "3. Liga", "country": "Germany"},
        {"id": 81, "name": "DFB Pokal", "country": "Germany"},
    ],
    "europa_top": [
        {"id": 39, "name": "Premier League", "country": "England"},
        {"id": 140, "name": "La Liga", "country": "Spain"},
        {"id": 135, "name": "Serie A", "country": "Italy"},
        {"id": 61, "name": "Ligue 1", "country": "France"},
        {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
    ],
    "uefa": [
        {"id": 2, "name": "Champions League", "country": "Europe"},
        {"id": 3, "name": "Europa League", "country": "Europe"},
        {"id": 848, "name": "Conference League", "country": "Europe"},
    ],
    "international": [
        {"id": 307, "name": "Saudi Pro League", "country": "Saudi Arabia"},
        {"id": 253, "name": "MLS", "country": "USA"},
    ],
    "national": [
        {"id": 1, "name": "World Cup", "country": "World"},
        {"id": 4, "name": "Euro Championship", "country": "Europe"},
        {"id": 5, "name": "UEFA Nations League", "country": "Europe"},
        {"id": 9, "name": "Copa America", "country": "South America"},
        {"id": 32, "name": "World Cup Qual. Europe", "country": "Europe"},
    ],
}

CATEGORY_LABELS: dict[str, str] = {
    "deutschland": "Deutschland",
    "europa_top": "Europa Topligen",
    "uefa": "UEFA Wettbewerbe",
    "international": "International",
    "national": "Top Nationalteams",
    "favoriten": "Favoriten",
}

LIVE_STATUSES = frozenset({"1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"})
FINISHED_STATUSES = frozenset({"FT", "AET", "PEN", "AWD", "WO"})
SCHEDULED_STATUSES = frozenset({"NS", "TBD", "PST", "SUSP"})


def all_league_ids() -> set[int]:
    ids: set[int] = set()
    for group in LEAGUE_CATALOG.values():
        for lg in group:
            ids.add(int(lg["id"]))
    return ids


def league_name_map() -> dict[int, str]:
    out: dict[int, str] = {}
    for group in LEAGUE_CATALOG.values():
        for lg in group:
            out[int(lg["id"])] = str(lg["name"])
    return out


def leagues_for_category(category: str, favorites: list[int] | None = None) -> list[dict[str, Any]]:
    if category == "favoriten":
        fav = favorites or []
        lookup = {int(lg["id"]): lg for g in LEAGUE_CATALOG.values() for lg in g}
        return [lookup[i] for i in fav if i in lookup]
    return list(LEAGUE_CATALOG.get(category, []))
