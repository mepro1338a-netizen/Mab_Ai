"""Football board data diagnosis CLI. Run: python tools/test_football_board_debug.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.football_data_debug import format_debug_widget, run_board_diagnosis
from services.football_service import get_football_service


def main() -> int:
    print("=== MaByte Football Board Debug ===\n")
    service = get_football_service()
    if not service.is_configured():
        print("FEHLER: FOOTBALL_API_KEY nicht gesetzt.")
        return 1

    report = run_board_diagnosis(service, username="debug")
    print(format_debug_widget(report))
    print("\n--- API Probes ---")
    for name, probe in (report.get("probes") or {}).items():
        print(
            f"{name}: status={probe.get('status_code')} "
            f"len={probe.get('response_length')} "
            f"cached={probe.get('cached')} "
            f"error={probe.get('error') or '—'}"
        )

    print("\n--- Summary ---")
    summary = report.get("summary") or {}
    print(f"API funktioniert: {'JA' if summary.get('api_works') else 'NEIN'}")
    print(f"Daten vorhanden: {'JA' if summary.get('data_present') else 'NEIN'}")
    print(f"Filter entfernt Daten: {'JA' if summary.get('filters_removed_data') else 'NEIN'}")
    print(f"Rate Limit: {'JA' if summary.get('rate_limit') else 'NEIN'}")
    print(f"Fehlerstelle: {summary.get('failure_point', '—')}")

    print("\n--- Raw JSON ---")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    return 0 if summary.get("api_works") else 2


if __name__ == "__main__":
    raise SystemExit(main())
