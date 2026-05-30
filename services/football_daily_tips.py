"""Daily AI betting tips — top 3 premium fixtures."""
from __future__ import annotations

from typing import Any

from config import football_plan_rank
from services.football_elite_betting_card import (
    build_betting_intelligence_card,
    build_pro_preview_card,
)
from services.football_match_center import fetch_match_detail, sort_fixtures_by_priority


def _tip_candidates(fixtures: list[dict[str, Any]], *, limit: int = 3) -> list[dict[str, Any]]:
    sorted_fx = sort_fixtures_by_priority(fixtures or [])
    upcoming = [
        fx for fx in sorted_fx
        if str(((fx.get("fixture") or {}).get("status") or {}).get("short") or "NS")
        not in ("FT", "AET", "PEN", "AWD", "WO")
    ]
    pool = upcoming if upcoming else sorted_fx
    return pool[:limit]


def build_daily_betting_tips(
    service,
    fixtures: list[dict[str, Any]],
    *,
    username: str,
    session_plan: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Fetch detail + intelligence card for top N premium fixtures (Pro=Preview, Elite=Full)."""
    rank = football_plan_rank(session_plan or "none")
    if rank < 2:
        return []

    tips: list[dict[str, Any]] = []
    for fx in _tip_candidates(fixtures, limit=limit):
        fid = (fx.get("fixture") or {}).get("id")
        if not fid:
            continue
        try:
            fixture_id = int(fid)
        except (TypeError, ValueError):
            continue

        detail = fetch_match_detail(
            service,
            fixture_id,
            username=username,
            session_plan=session_plan,
        )
        if detail.get("error"):
            continue

        if rank >= 3:
            intel = build_betting_intelligence_card(detail)
        else:
            intel = build_pro_preview_card(detail)

        tips.append({
            "fixture_id": fixture_id,
            "detail": detail,
            "intel": intel,
            "mode": "elite" if rank >= 3 else "pro",
        })

    return tips
