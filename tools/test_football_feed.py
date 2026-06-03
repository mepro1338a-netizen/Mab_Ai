"""Smoke test football feed counts (no Streamlit)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.football_api import get_football_service
from services.football_feed import (
    filter_topspiele_fixtures,
    fetch_board_payload,
    resolve_all_api_board,
    resolve_topspiele_board,
)


def main() -> None:
    svc = get_football_service()
    if not svc.is_configured():
        print("SKIP: FOOTBALL_API_KEY not set")
        return

    payload = fetch_board_payload(svc, username="test", time_filter="heute")
    top = resolve_topspiele_board(payload, time_filter="heute")
    all_ = resolve_all_api_board(payload, time_filter="heute")

    top_rows = top.get("rows") or []
    all_rows = all_.get("rows") or []

    bad_top = []
    for row in top_rows:
        card = row.get("card") or {}
        lid = card.get("league_id")
        league = card.get("league") or ""
        country = card.get("country") or ""
        try:
            if int(lid or 0) not in {78, 79, 81, 2, 3, 848, 39, 140, 135, 61}:
                bad_top.append(f"{league} ({country}) id={lid}")
        except (TypeError, ValueError):
            bad_top.append(f"{league} ({country})")

    print(f"displayed_topspiele_count={len(top_rows)}")
    print(f"displayed_allspiele_count={len(all_rows)}")
    print(f"topspiele_banner={top.get('banner')!r}")
    print(f"all_banner={all_.get('banner')!r}")
    if bad_top:
        print("FAIL topspiele non-whitelist:", bad_top[:5])
    else:
        print("OK topspiele whitelist only")
    raw_pool = payload.get("raw_today") or []
    print(f"raw_today_total={len(raw_pool)}")
    print(f"raw_topspiele_in_pool={len(filter_topspiele_fixtures(raw_pool))}")


if __name__ == "__main__":
    main()
