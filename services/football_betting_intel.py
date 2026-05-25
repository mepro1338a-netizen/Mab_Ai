"""
AI Betting Intelligence — implied probability, EV, value detection, bookmaker compare.
Educational analysis only — not betting advice.
"""
from __future__ import annotations

from typing import Any

from services.football_odds import calculate_tip_odds


def implied_probability(decimal_odd: float) -> float:
    if decimal_odd < 1.01:
        return 0.0
    return round((1.0 / decimal_odd) * 100.0, 2)


def risk_score(edge_pct: float, odds: float, confidence: float) -> dict[str, Any]:
    """0–100 risk index (higher = riskier)."""
    edge = float(edge_pct)
    o = float(odds)
    conf = float(confidence)
    base = 35.0
    if o >= 4.5:
        base += 28.0
    elif o >= 2.8:
        base += 14.0
    if edge < -5:
        base += 12.0
    if abs(edge) < 2:
        base += 8.0
    base -= min(20.0, conf * 0.15)
    score = max(5.0, min(95.0, base))
    label = "Niedrig" if score < 35 else ("Mittel" if score < 60 else "Hoch")
    return {"risk_score": round(score, 1), "risk_label": label}


def compare_bookmakers(markets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Best decimal odd per market+selection across bookmakers."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for m in markets or []:
        key = f"{m.get('market', '')}|{m.get('selection', '')}"
        buckets.setdefault(key, []).append(m)

    rows: list[dict[str, Any]] = []
    for key, items in buckets.items():
        best = max(items, key=lambda x: float(x.get("odd") or 0))
        market, sel = key.split("|", 1)
        rows.append({
            "market": market,
            "selection": sel,
            "best_odd": float(best.get("odd") or 0),
            "bookmaker": best.get("bookmaker", ""),
            "implied_pct": implied_probability(float(best.get("odd") or 0)),
            "count": len(items),
        })
    rows.sort(key=lambda r: -r["best_odd"])
    return rows[:24]


def detect_value_bets(
    markets: list[dict[str, Any]],
    *,
    model_probability_pct: float | None = None,
    min_edge_pct: float = 2.0,
) -> list[dict[str, Any]]:
    """Flag selections where model/user prob beats implied market prob."""
    p_model = model_probability_pct
    hits: list[dict[str, Any]] = []
    for m in markets or []:
        odd = float(m.get("odd") or 0)
        if odd < 1.01:
            continue
        impl = implied_probability(odd)
        if p_model is None:
            sel = (m.get("selection") or "").lower()
            if "home" in sel:
                continue
            p_est = impl + 4.0
        else:
            p_est = float(p_model)
        edge = p_est - impl
        if edge >= min_edge_pct:
            analysis = calculate_tip_odds(odd, 10.0, p_est)
            hits.append({
                **m,
                "implied_pct": impl,
                "model_pct": round(p_est, 2),
                "edge_pct": round(edge, 2),
                "expected_value": analysis["expected_value"],
                "confidence_pct": analysis["confidence_pct"],
                "is_value": True,
            })
    hits.sort(key=lambda x: -float(x.get("edge_pct") or 0))
    return hits[:12]


def full_betting_analysis(
    odds: float,
    stake: float,
    win_probability_pct: float,
    *,
    markets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    core = calculate_tip_odds(odds, stake, win_probability_pct)
    risk = risk_score(core["edge_pct"], odds, core["confidence_pct"])
    comparison = compare_bookmakers(markets or []) if markets else []
    value_hits = detect_value_bets(
        markets or [],
        model_probability_pct=win_probability_pct,
    ) if markets else []

    return {
        **core,
        **risk,
        "bookmaker_comparison": comparison,
        "value_opportunities": value_hits,
        "value_bet_count": len(value_hits),
    }
