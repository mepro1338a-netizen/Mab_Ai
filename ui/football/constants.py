"""Football AI V2 — navigation labels (league IDs match config whitelist)."""
from __future__ import annotations

TOP_NAV: tuple[tuple[str, str], ...] = (
    ("deutschland", "Deutschland"),
    ("uefa", "UEFA"),
    ("topligen", "Top-Ligen"),
    ("nationalteams", "Nationalteams"),
)

TIME_NAV: tuple[tuple[str, str], ...] = (
    ("heute", "Heute"),
    ("live", "Live"),
    ("morgen", "Morgen"),
    ("naechste", "Nächste"),
)

# (league_id, label) — 0 = all leagues in competition group
LEAGUE_NAV: dict[str, list[tuple[int, str]]] = {
    "deutschland": [
        (0, "Alle"),
        (78, "Bundesliga"),
        (79, "2. Bundesliga"),
        (81, "DFB Pokal"),
    ],
    "uefa": [
        (0, "Alle"),
        (2, "Champions League"),
        (3, "Europa League"),
        (848, "Conference League"),
    ],
    "topligen": [
        (0, "Alle"),
        (39, "Premier League"),
        (140, "La Liga"),
        (135, "Serie A"),
        (61, "Ligue 1"),
    ],
    "nationalteams": [
        (1, "WM"),
        (4, "EM"),
        (5, "Nations League"),
        (0, "Alle Spiele"),
    ],
}

MSG_NO_ANALYSIS = (
    "Für dieses Spiel stehen aktuell keine ausreichenden Analysedaten zur Verfügung."
)
MSG_EMPTY_TODAY = "Heute sind keine Spiele verfügbar."
MSG_NEXT_SECTION = "Nächste Spiele"
