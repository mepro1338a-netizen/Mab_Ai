"""Home dashboard — Football intelligence payload (cached per session)."""
from __future__ import annotations

from typing import Any

from config import football_plan_rank
from services.football_daily_tips import build_daily_betting_tips
from services.football_match_center import fetch_premium_dashboard, parse_match_card
from services.football_service import get_football_service


def load_home_football_hub(
    *,
    username: str,
    session_plan: str,
) -> dict[str, Any]:
    """Aggregate premium fixtures + daily tips for the home command center."""
    service = get_football_service()
    payload = fetch_premium_dashboard(service, username=username, include_all_leagues=False)
    rank = football_plan_rank(session_plan or "none")

    tips: list[dict[str, Any]] = []
    if payload.get("configured") and rank >= 2:
        pool = list(payload.get("top_matches") or [])
        if not pool:
            pool = list(payload.get("next_matches") or [])
        if not pool:
            pool = list(payload.get("live_now") or [])
        tips = build_daily_betting_tips(
            service,
            pool,
            username=username,
            session_plan=session_plan,
            limit=3,
        )

    top_raw = _first_fixture(
        payload.get("live_now"),
        payload.get("top_matches"),
        payload.get("next_matches"),
    )
    top_card = parse_match_card(top_raw) if top_raw else None

    pick_intel = tips[0]["intel"] if tips else None
    best_intel = _best_value_intel(tips)

    injuries = _injury_headlines(tips)

    live_cards = [
        parse_match_card(fx)
        for fx in (payload.get("live_now") or [])[:6]
    ]

    return {
        "payload": payload,
        "tips": tips,
        "rank": rank,
        "top_card": top_card,
        "pick_intel": pick_intel,
        "best_intel": best_intel,
        "injuries": injuries,
        "live_cards": live_cards,
    }


def _first_fixture(*groups: Any) -> dict[str, Any] | None:
    for group in groups:
        for fx in group or []:
            if fx and (fx.get("fixture") or {}).get("id"):
                return fx
    return None


def _best_value_intel(tips: list[dict[str, Any]]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_score = -1.0
    for tip in tips:
        intel = tip.get("intel") or {}
        val = intel.get("value_quote") or {}
        conf = (intel.get("recommendation") or {}).get("confidence")
        edge = val.get("edge_pct")
        score = 0.0
        if edge is not None:
            try:
                score = float(edge)
            except (TypeError, ValueError):
                score = 0.0
        elif conf is not None:
            try:
                score = float(conf) * 0.5
            except (TypeError, ValueError):
                score = 0.0
        verdict = str(val.get("verdict") or "").lower()
        if "value" in verdict or "edge" in verdict:
            score += 12
        if score > best_score and intel:
            best_score = score
            best = intel
    if best:
        return best
    return (tips[0].get("intel") if tips else None)


def _injury_headlines(tips: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for tip in tips:
        intel = tip.get("intel") or {}
        inj = intel.get("injuries") or {}
        if not inj.get("available"):
            continue
        h = intel.get("header") or {}
        match = f"{h.get('home', '')} vs {h.get('away', '')}"
        line = (
            f"{match}: Heim {inj.get('home_impact', '—')} · "
            f"Auswärts {inj.get('away_impact', '—')}"
        )
        if line in seen:
            continue
        seen.add(line)
        home_n = len(inj.get("home") or [])
        away_n = len(inj.get("away") or [])
        detail = f"{home_n} / {away_n} Ausfälle" if (home_n or away_n) else ""
        out.append({"match": match, "line": line, "detail": detail})
        if len(out) >= 5:
            break
    return out
