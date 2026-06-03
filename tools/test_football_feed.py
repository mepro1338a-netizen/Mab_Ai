"""Smoke test football feed — competition groups + Alle API."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.football_api import get_football_service
from services.football_feed import (
    fetch_all_api_payload,
    league_ids_for_competition,
    resolve_all_api_board,
    resolve_competition_board,
)


def _check_whitelist(rows: list, allowed: frozenset) -> list:
    bad = []
    for row in rows:
        card = row.get("card") or {}
        lid = card.get("league_id")
        try:
            if int(lid or 0) not in allowed:
                bad.append(f"{card.get('league')} id={lid}")
        except (TypeError, ValueError):
            bad.append(str(card.get("league")))
    return bad


def main() -> None:
    svc = get_football_service()
    if not svc.is_configured():
        print("SKIP: FOOTBALL_API_KEY not set")
        return

    for comp in ("deutschland", "uefa", "topligen", "nationalteams"):
        allowed = league_ids_for_competition(comp)
        result = resolve_competition_board(
            svc,
            username="test",
            session_plan="football_elite",
            competition=comp,
            time_filter="heute",
            probe_analysis=False,
        )
        rows = result.get("rows") or []
        bad = _check_whitelist(rows, allowed)
        print(f"[{comp}] rows={len(rows)} banner={result.get('banner')!r}")
        if bad:
            print(f"  FAIL whitelist:", bad[:3])
        else:
            print("  OK whitelist")

    payload = fetch_all_api_payload(svc, username="test")
    all_ = resolve_all_api_board(payload, time_filter="heute")
    all_rows = all_.get("rows") or []
    print(f"alle_api rows={len(all_rows)} banner={all_.get('banner')!r}")


if __name__ == "__main__":
    main()
