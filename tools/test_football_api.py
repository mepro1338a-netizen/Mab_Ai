"""Test FOOTBALL_API_KEY. Run: python tools/test_football_api.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import FOOTBALL_API_BASE_URL, FOOTBALL_API_KEY
from services.football_service import FootballAPIError, get_football_service


def main() -> int:
    print("=== MaByte Football API Test ===\n")
    service = get_football_service()
    if not service.is_configured():
        print("FEHLER: FOOTBALL_API_KEY nicht gesetzt.")
        return 1
    print(f"Base URL: {FOOTBALL_API_BASE_URL}")
    print(f"Key:      {'***' if FOOTBALL_API_KEY else '(leer)'}\n")
    try:
        live = service.get_live_fixtures(username="")
        print(f"Live: {len(live)}")
        upcoming = service.get_premium_fixtures_upcoming(days=30, username="")
        print(f"Premium upcoming: {len(upcoming)}")
        print("OK")
        return 0
    except FootballAPIError as exc:
        print(f"FEHLER: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
