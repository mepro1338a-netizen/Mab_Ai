"""Test FOOTBALL_API_KEY against API-Football. Run: python tools/test_football_api.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import FOOTBALL_API_BASE_URL, FOOTBALL_API_KEY
from services.football_service import FootballAPIError, get_football_service


def mask_key(key: str) -> str:
    key = (key or "").strip()
    if not key:
        return "(leer)"
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def main() -> int:
    print("=== MaByte Football API Test ===\n")
    print(f"Base URL: {FOOTBALL_API_BASE_URL}")
    print(f"Key:      {mask_key(FOOTBALL_API_KEY)}\n")

    service = get_football_service()

    if not service.is_configured():
        print("FEHLER: FOOTBALL_API_KEY ist nicht gesetzt.")
        print("\nLokal:  .env im Projektroot anlegen:")
        print("  FOOTBALL_API_KEY=dein_key_von_api-football.com")
        print("\nRailway: Variables -> FOOTBALL_API_KEY -> Redeploy")
        return 1

    try:
        print("1) Teamsuche: Arsenal ...")
        teams = service.search_teams("Arsenal", username="test")
        print(f"   OK — {len(teams)} Treffer")
        if teams:
            t = teams[0].get("team") or {}
            print(f"   Erstes Team: {t.get('name')} (id={t.get('id')})")

        team_id = (teams[0].get("team") or {}).get("id") if teams else None
        if team_id:
            print(f"\n2) Naechste Fixtures fuer Team {team_id} ...")
            fixtures = service.get_upcoming_fixtures(int(team_id), next_count=3, username="test")
            print(f"   OK — {len(fixtures)} Fixtures")
            for row in fixtures[:3]:
                from services.football_service import fixture_label
                print(f"   - {fixture_label(row)}")

        print("\n3) Live-Spiele ...")
        live = service.get_live_fixtures(username="test")
        print(f"   OK — {len(live)} Live-Spiele")

        print("\n=== ALLES OK — Key funktioniert ===")
        return 0

    except FootballAPIError as exc:
        print(f"\nFEHLER: {exc}")
        if getattr(exc, "status_code", None):
            print(f"HTTP/API Status: {exc.status_code}")
        if getattr(exc, "api_errors", None):
            print(f"API Details: {exc.api_errors}")
        print("\nTypische Ursachen:")
        print("- Falscher oder abgelaufener Key")
        print("- Free-Plan: Tageslimit erreicht (Rate Limit)")
        print("- Falscher Header: Key muss von api-sports.io / dashboard sein")
        return 2
    except Exception as exc:
        print(f"\nUNERWARTETER FEHLER: {type(exc).__name__}: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
