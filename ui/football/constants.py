"""Football AI — navigation labels and free-tier league metadata."""
from __future__ import annotations

from config import FOOTBALL_DATA_COMPETITION_CODES

# (competition_key, tab label)
CATEGORY_TABS: tuple[tuple[str, str], ...] = (
    ("deutschland", "Deutschland"),
    ("uefa", "Europa"),
    ("nationalteams", "International"),
    ("topligen", "Top-Ligen"),
)

# (time_key, segmented label)
TIME_OPTIONS: tuple[tuple[str, str], ...] = (
    ("heute", "Heute"),
    ("live", "Live"),
    ("morgen", "Morgen"),
    ("naechste", "Kommende"),
)

# (league_id, label) — 0 = all leagues in competition group
# Only leagues with football-data.org Free-Tier codes are marked available.
_LEAGUE_CATALOG: dict[str, list[tuple[int, str]]] = {
    "deutschland": [
        (0, "Alle Wettbewerbe"),
        (78, "Bundesliga"),
        (79, "2. Bundesliga"),
        (81, "DFB-Pokal"),
    ],
    "uefa": [
        (0, "Alle Wettbewerbe"),
        (2, "Champions League"),
        (3, "Europa League"),
        (848, "Conference League"),
    ],
    "topligen": [
        (0, "Alle Wettbewerbe"),
        (39, "Premier League"),
        (140, "La Liga"),
        (135, "Serie A"),
        (61, "Ligue 1"),
        (88, "Eredivisie"),
        (94, "Primeira Liga"),
    ],
    "nationalteams": [
        (0, "Alle Turniere"),
        (1, "WM"),
        (4, "EM"),
        (5, "Nations League"),
    ],
}

def league_has_free_tier_data(league_id: int) -> bool:
    if not league_id:
        return True
    return int(league_id) in FOOTBALL_DATA_COMPETITION_CODES


def league_options_for(competition: str) -> list[tuple[int, str, bool]]:
    """Return (league_id, label, available) for selectbox."""
    out: list[tuple[int, str, bool]] = []
    for league_id, label in _LEAGUE_CATALOG.get(competition, [(0, "Alle Wettbewerbe")]):
        available = league_has_free_tier_data(league_id)
        display = label if available else f"{label} (Premium)"
        out.append((league_id, display, available))
    return out


def available_league_options(competition: str) -> list[tuple[int, str]]:
    return [
        (lid, label)
        for lid, label, ok in league_options_for(competition)
        if ok
    ]


PREMIUM_LEAGUE_HINT = (
    "Weitere Wettbewerbe (2. Bundesliga, DFB-Pokal, Europa League, Conference League, "
    "Nations League) sind im Premium-Plan verfügbar."
)

MSG_NO_ANALYSIS = (
    "Für dieses Spiel stehen aktuell keine ausreichenden Analysedaten zur Verfügung."
)
MSG_EMPTY_TODAY = "Heute sind keine Spiele verfügbar."
MSG_EMPTY_SELECTION = "Keine Spiele für diese Auswahl."
MSG_NEXT_SECTION = "Nächste Spiele"
MSG_PREMIUM_LEAGUE = (
    "Für diesen Wettbewerb liegen im Free-Tier keine Live-Daten vor. "
    "Bitte eine verfügbare Liga wählen oder Premium nutzen."
)
