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

    # Confidence: model signal strength (educational, not predictive guarantee)
    confidence = min(95.0, max(22.0, 48.0 + abs(edge_pct) * 2.4 + (8.0 if is_value else 0.0)))

    # Quarter-Kelly style bankroll hint (capped, analysis only)
    bankroll_pct = 0.0
    if edge_pct > 0.5 and odds > 1.01:
        kelly = (p_user * odds - 1.0) / (odds - 1.0)
        bankroll_pct = max(0.0, min(5.0, kelly * 25.0))

    value_label = "Value erkannt" if is_value else "Kein klarer Value"
    if edge_pct > 6:
        value_label = "Starker Value (modell)"
    elif edge_pct < -4:
        value_label = "Markt wirkt teurer"

    return {
        "implied_probability_pct": round(implied_pct, 2),
        "break_even_probability_pct": round(break_even_pct, 2),
        "profit": round(profit, 2),
        "payout": round(payout, 2),
        "expected_value": round(expected_value, 2),
        "edge_pct": round(edge_pct, 2),
        "is_value_bet": is_value,
        "risk_level": risk,
        "confidence_pct": round(confidence, 1),
        "bankroll_stake_pct": round(bankroll_pct, 2),
        "value_label": value_label,
    }


def extract_1x2_odds(markets: list[dict[str, Any]]) -> dict[str, float | None]:
    """Best available 1X2 decimal odds from normalized market rows."""
    home_odd = draw_odd = away_odd = None
    for m in markets or []:
        market = str(m.get("market") or "").lower()
        sel = str(m.get("selection") or "").lower()
        if "match winner" not in market and "1x2" not in market and "winner" not in market:
            continue
        try:
            odd = float(m.get("odd") or 0)
        except (TypeError, ValueError):
            continue
        if odd < 1.01:
            continue
        if sel in ("home", "1"):
            home_odd = home_odd or odd
        elif sel in ("draw", "x"):
            draw_odd = draw_odd or odd
        elif sel in ("away", "2"):
            away_odd = away_odd or odd
    return {"home": home_odd, "draw": draw_odd, "away": away_odd}


def get_odds_for_fixture(
    service: Any,
    fixture_id: int,
    *,
    username: str,
) -> dict[str, float | None]:
    """Fetch 1X2 odds via API-Football GET /odds?fixture=ID."""
    from services.football_service import FootballAPIError

    try:
        raw = service.get_fixture_odds(int(fixture_id), username=username)
        markets = parse_fixture_odds_payload(raw)
        return extract_1x2_odds(markets)
    except FootballAPIError:
        return {"home": None, "draw": None, "away": None}


def win_pcts_from_odds(
    home_odd: float | None,
    draw_odd: float | None,
    away_odd: float | None,
) -> tuple[float | None, float | None, float | None]:
    """Normalized implied win % from decimal odds."""
    try:
        h = float(home_odd) if home_odd else None
        d = float(draw_odd) if draw_odd else None
        a = float(away_odd) if away_odd else None
    except (TypeError, ValueError):
        return None, None, None
    if not h or not d or not a or h < 1.01 or d < 1.01 or a < 1.01:
        return None, None, None
    hp, dp, ap = 1.0 / h, 1.0 / d, 1.0 / a
    total = hp + dp + ap
    if total <= 0:
        return None, None, None
    return round(hp / total * 100, 1), round(dp / total * 100, 1), round(ap / total * 100, 1)


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
