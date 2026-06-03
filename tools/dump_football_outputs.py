"""Quick football output dump for mepro1337 / elite plan."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from database import get_user
from services.football_api import get_football_service
from services.football_feed import (
    fetch_board_payload,
    resolve_all_api_board,
    resolve_football_feed,
    resolve_topspiele_board,
)
from services.football_board import fetch_match_detail

USERNAME = "mepro1337"
SESSION_PLAN = "football_elite"


def main() -> None:
    user = get_user(USERNAME)
    print(f"User: {USERNAME} exists={bool(user)} plan={user.get('football_plan') if user else '?'}")

    svc = get_football_service()
    print(f"API configured: {svc.is_configured()}")

    for tf in ("heute", "live", "morgen"):
        print(f"\n{'='*50}\nZEITFILTER: {tf.upper()}\n{'='*50}")
        payload = fetch_board_payload(svc, username=USERNAME, time_filter=tf)
        errs = payload.get("errors") or []
        if errs:
            print("Warnungen:", errs[:3])
        print(
            f"Pools: raw_today={len(payload.get('raw_today') or [])} "
            f"raw_live={len(payload.get('raw_live') or [])} "
            f"raw_tomorrow={len(payload.get('raw_tomorrow') or [])} "
            f"next={len(payload.get('next_matches') or [])}"
        )

        top = resolve_topspiele_board(payload, time_filter=tf)
        all_ = resolve_all_api_board(payload, time_filter=tf)
        print(f"TOPSPIELE: {len(top.get('rows') or [])} | banner={top.get('banner')!r}")
        for i, row in enumerate((top.get("rows") or [])[:8]):
            c = row.get("card") or {}
            print(
                f"  [{i+1}] {c.get('home')} vs {c.get('away')} | "
                f"{c.get('league')} (id={c.get('league_id')}) | "
                f"{c.get('time') or c.get('date')} | analyse={row.get('analysis_available')}"
            )

        print(f"ALLE API: {len(all_.get('rows') or [])} | banner={all_.get('banner')!r}")
        for i, row in enumerate((all_.get("rows") or [])[:5]):
            c = row.get("card") or {}
            print(
                f"  [{i+1}] {c.get('home')} vs {c.get('away')} | "
                f"{c.get('league')} (id={c.get('league_id')})"
            )

        feed = resolve_football_feed(
            payload,
            svc,
            view_mode="premium",
            time_filter=tf,
            username=USERNAME,
            session_plan=SESSION_PLAN,
            probe_analysis=True,
        )
        print(f"UI resolve(premium): rows={len(feed.get('rows') or [])}")

    rows = (resolve_topspiele_board(
        fetch_board_payload(svc, username=USERNAME, time_filter="heute"),
        time_filter="heute",
    ).get("rows") or [])
    if rows and rows[0].get("fixture_id"):
        fid = int(rows[0]["fixture_id"])
        detail = fetch_match_detail(
            svc, fid, username=USERNAME, session_plan=SESSION_PLAN
        )
        c = detail.get("card") or {}
        print(f"\n{'='*50}\nDETAIL Fixture {fid}: {c.get('home')} vs {c.get('away')}")
        print(f"analysis_available={detail.get('analysis_available')}")
        print(f"error={detail.get('error')!r}")
        odds = detail.get("odds") or {}
        if odds:
            print(f"odds: 1={odds.get('home')} X={odds.get('draw')} 2={odds.get('away')}")
        pred = detail.get("prediction_insights") or {}
        if pred:
            print(
                f"pred: H={pred.get('home_pct')}% D={pred.get('draw_pct')}% "
                f"A={pred.get('away_pct')}% advice={pred.get('advice')!r}"
            )


if __name__ == "__main__":
    main()
