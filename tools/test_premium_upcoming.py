"""Premium upcoming fixtures + odds probe. Run: python tools/test_premium_upcoming.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.football_board import get_odds_for_fixture, has_complete_odds
from services.football_service import FootballAPIError, get_football_service


def main() -> int:
    service = get_football_service()
    if not service.is_configured():
        print("FEHLER: FOOTBALL_API_KEY nicht gesetzt.")
        return 1

    username = ""
    try:
        upcoming = service.get_premium_fixtures_upcoming(days=30, username=username)
    except FootballAPIError as exc:
        print(f"FEHLER: {exc}")
        return 1

    print(f"Premium Upcoming (30 Tage): {len(upcoming)}")
    print("\nErste 10 Premium-Spiele:")
    print(f"{'Liga':<28} {'Datum':<12} {'Heim':<22} {'Auswärts':<22} Odds")
    print("-" * 100)

    for fx in upcoming[:10]:
        league = fx.get("league") or {}
        teams = fx.get("teams") or {}
        meta = fx.get("fixture") or {}
        home = (teams.get("home") or {}).get("name") or "?"
        away = (teams.get("away") or {}).get("name") or "?"
        date_s = str(meta.get("date") or "")[:10]
        league_name = str(league.get("name") or "?")[:28]
        fid = meta.get("id")
        odds_lbl = "nein"
        if fid:
            try:
                o = get_odds_for_fixture(service, int(fid), username=username)
                if has_complete_odds(
                    {
                        "home_odd": o.get("home"),
                        "draw_odd": o.get("draw"),
                        "away_odd": o.get("away"),
                    }
                ):
                    odds_lbl = "ja"
            except FootballAPIError:
                odds_lbl = "fehler"
        print(f"{league_name:<28} {date_s:<12} {home[:22]:<22} {away[:22]:<22} {odds_lbl}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
