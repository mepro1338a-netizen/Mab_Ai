"""Mathematical odds/value calculator — no gambling API, no real money."""
from __future__ import annotations


def calculate_tip_odds(
    odds: float,
    stake: float,
    win_probability_pct: float,
) -> dict:
    """
    Decimal odds model.
    - odds: decimal quote (e.g. 2.10)
    - stake: amount wagered (analysis only)
    - win_probability_pct: user estimate 0–100
    """
    odds = float(odds)
    stake = max(0.0, float(stake))
    p_user = max(0.0, min(100.0, float(win_probability_pct))) / 100.0

    if odds < 1.01:
        raise ValueError("Quote muss mindestens 1.01 sein (Dezimalformat).")

    implied_pct = (1.0 / odds) * 100.0
    break_even_pct = implied_pct
    profit = stake * (odds - 1.0)
    payout = stake * odds
    expected_value = stake * (p_user * odds - 1.0)
    edge_pct = p_user * 100.0 - implied_pct
    is_value = edge_pct > 1.0

    if odds >= 4.0 or p_user < implied_pct * 0.85:
        risk = "Hoch"
    elif odds >= 2.2 or abs(edge_pct) < 3.0:
        risk = "Mittel"
    else:
        risk = "Niedrig"

    return {
        "implied_probability_pct": round(implied_pct, 2),
        "break_even_probability_pct": round(break_even_pct, 2),
        "profit": round(profit, 2),
        "payout": round(payout, 2),
        "expected_value": round(expected_value, 2),
        "edge_pct": round(edge_pct, 2),
        "is_value_bet": is_value,
        "risk_level": risk,
    }
