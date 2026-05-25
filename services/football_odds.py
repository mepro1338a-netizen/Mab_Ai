"""Mathematical odds/value calculator + Elite live odds parsing."""
from __future__ import annotations

from typing import Any


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


def parse_fixture_odds_payload(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize API-Football odds into flat market rows."""
    markets: list[dict[str, Any]] = []
    for block in rows or []:
        for bookmaker in block.get("bookmakers") or []:
            bm_name = str(bookmaker.get("name") or "Anbieter")
            for bet in bookmaker.get("bets") or []:
                market = str(bet.get("name") or "Markt")
                for val in bet.get("values") or []:
                    try:
                        odd = float(val.get("odd") or 0)
                    except (TypeError, ValueError):
                        continue
                    if odd < 1.01:
                        continue
                    markets.append({
                        "bookmaker": bm_name,
                        "market": market,
                        "selection": str(val.get("value") or ""),
                        "odd": round(odd, 2),
                        "label": f"{bm_name} · {market} · {val.get('value', '')}",
                    })
    return markets[:48]


def parse_prediction_insights(row: dict[str, Any]) -> dict[str, Any]:
    """Extract win probabilities and advice from predictions API."""
    preds = row.get("predictions") or {}
    percent = preds.get("percent") or {}
    comparison = preds.get("comparison") or {}

    def _pct(key: str) -> float | None:
        raw = percent.get(key)
        if raw is None:
            return None
        s = str(raw).replace("%", "").strip()
        try:
            return float(s)
        except ValueError:
            return None

    home = _pct("home")
    draw = _pct("draw")
    away = _pct("away")

    teams = row.get("teams") or {}
    home_name = (teams.get("home") or {}).get("name") or "Home"
    away_name = (teams.get("away") or {}).get("name") or "Away"

    return {
        "home": home_name,
        "away": away_name,
        "home_pct": home,
        "draw_pct": draw,
        "away_pct": away,
        "advice": str(preds.get("advice") or "").strip(),
        "winner_comment": str((preds.get("winner") or {}).get("comment") or "").strip(),
        "form_home": str((comparison.get("form") or {}).get("home") or ""),
        "form_away": str((comparison.get("form") or {}).get("away") or ""),
    }


def fixture_options_from_list(fixtures: list[dict[str, Any]]) -> dict[str, int]:
    """Build selectbox labels -> fixture id."""
    from services.football_service import fixture_label

    opts: dict[str, int] = {}
    for fx in fixtures or []:
        meta = fx.get("fixture") or {}
        fid = meta.get("id")
        if fid:
            opts[fixture_label(fx)] = int(fid)
    return opts
