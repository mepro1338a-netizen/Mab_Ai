"""Betting-quality filters, odds merge, confidence & tip baseline."""
from __future__ import annotations

from typing import Any

from config import FOOTBALL_PREMIUM_LEAGUE_IDS
from services.football_leagues import is_blocked_league_name, is_premium_league_match
from services.football_odds import (
    extract_1x2_odds,
    get_odds_for_fixture,
    parse_fixture_odds_payload,
    parse_prediction_insights,
    win_pcts_from_odds,
)
from services.football_service import FootballAPIError, FootballService

BETTING_PREMIUM_IDS: frozenset[int] = FOOTBALL_PREMIUM_LEAGUE_IDS

_EXTRA_BLOCKED = (
    "u17",
    "u-17",
    " u17",
    "women",
    "woman",
    "feminin",
    "feminine",
    " frauen",
    " usl",
    "canadian premier",
    "canada premier",
    "sudan",
    "queensland",
    "tasmania",
    "npl",
    "development league",
    " ii",
    " 2 team",
    "reserve league",
    "premier league 2",
)


def is_excluded_betting_league(league: dict[str, Any] | None) -> bool:
    if not league:
        return True
    name = str(league.get("name") or "").lower()
    country = str(league.get("country") or "").lower()
    if is_blocked_league_name(name):
        return True
    hay = f"{name} {country}"
    if any(part in hay for part in _EXTRA_BLOCKED):
        return True
    if "serie a" in name and country in ("brazil", "brasil"):
        return True
    return False


def is_bettable_premium_fixture(fixture: dict[str, Any]) -> bool:
    """Premium by ID or name+country; exclude youth/low-tier by name."""
    league = fixture.get("league") or {}
    if is_excluded_betting_league(league):
        return False
    try:
        lid = int(league.get("id") or 0) or None
    except (TypeError, ValueError):
        lid = None
    return is_premium_league_match(
        lid,
        str(league.get("name") or ""),
        str(league.get("country") or ""),
    )


def filter_bettable_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [fx for fx in fixtures or [] if is_bettable_premium_fixture(fx)]


def has_complete_odds(row: dict[str, Any]) -> bool:
    return all(
        row.get(k) is not None and float(row.get(k) or 0) >= 1.01
        for k in ("home_odd", "draw_odd", "away_odd")
    )


def build_betting_signal(
    *,
    home: str,
    away: str,
    home_odd: float | None,
    draw_odd: float | None,
    away_odd: float | None,
    pred_insights: dict[str, Any] | None,
    is_live: bool = False,
    h2h_support: bool = False,
    injury_advantage: bool = False,
    form_only: bool = False,
) -> dict[str, Any]:
    """AI pick + confidence from odds, API prediction, or baseline."""
    pred = pred_insights or {}
    reasons: list[str] = []
    confidence = 50.0
    no_bet = True
    ai_pick = "No Bet"
    risk = "Hoch"
    value = False

    odds_ok = has_complete_odds(
        {"home_odd": home_odd, "draw_odd": draw_odd, "away_odd": away_odd}
    )
    has_form = bool(pred.get("form_home") or pred.get("form_away"))
    has_pred = pred.get("home_pct") is not None

    if not odds_ok:
        confidence -= 15
        if form_only and (has_pred or has_form or pred.get("advice")):
            if pred.get("advice"):
                confidence += 10
                reasons.append(str(pred["advice"])[:90])
            if has_form:
                confidence += 10
                fh, fa = pred.get("form_home"), pred.get("form_away")
                reasons.append(f"Form: {home} {fh or '—'} · {away} {fa or '—'}")
            if has_pred:
                api_best = max(
                    [
                        ("home", pred.get("home_pct"), home),
                        ("draw", pred.get("draw_pct"), "X"),
                        ("away", pred.get("away_pct"), away),
                    ],
                    key=lambda x: float(x[1] or 0),
                )
                ai_pick = (
                    f"{api_best[2]} Sieg" if api_best[0] != "draw" else "Unentschieden"
                )
                home_pct = pred.get("home_pct")
                draw_pct = pred.get("draw_pct")
                away_pct = pred.get("away_pct")
                reasons.append("Analyse basiert auf Formdaten")
            else:
                ai_pick = f"{home} Sieg"
                reasons.append("Formdaten ohne Quoten")
            confidence = max(40.0, min(75.0, confidence))
            if confidence < 60:
                no_bet = True
                ai_pick = "No Bet"
                risk = "Hoch"
            else:
                no_bet = False
                risk = "Mittel"
            return {
                "ai_pick": ai_pick,
                "confidence": round(confidence, 1),
                "no_bet": no_bet,
                "risk": risk,
                "value": False,
                "reasons": reasons[:3],
                "home_pct": pred.get("home_pct"),
                "draw_pct": pred.get("draw_pct"),
                "away_pct": pred.get("away_pct"),
            }
        if is_live:
            return {
                "ai_pick": "No Bet",
                "confidence": max(35.0, confidence),
                "no_bet": True,
                "risk": "Hoch",
                "value": False,
                "reasons": ["Keine Quoten — Live nur Score-Modus."],
                "home_pct": None,
                "draw_pct": None,
                "away_pct": None,
            }
        return {
            "ai_pick": "No Bet",
            "confidence": max(35.0, confidence),
            "no_bet": True,
            "risk": "Hoch",
            "value": False,
            "reasons": ["Keine vollständigen 1X2-Quoten."],
            "home_pct": None,
            "draw_pct": None,
            "away_pct": None,
        }

    home_pct, draw_pct, away_pct = win_pcts_from_odds(home_odd, draw_odd, away_odd)

    sides = [
        ("home", float(home_odd), home_pct, home),
        ("draw", float(draw_odd), draw_pct, "Unentschieden"),
        ("away", float(away_odd), away_pct, away),
    ]
    fav_key, fav_odd, fav_pct, fav_name = min(sides, key=lambda x: x[1])

    if not has_form and not has_pred:
        confidence -= 10

    if pred.get("advice"):
        confidence += 10
        reasons.append(str(pred["advice"])[:90])
    if has_form:
        confidence += 10
        fh, fa = pred.get("form_home"), pred.get("form_away")
        reasons.append(f"Form: {home} {fh or '—'} · {away} {fa or '—'}")
    if h2h_support:
        confidence += 10
        reasons.append("H2H stützt den Favoriten")
    if injury_advantage:
        confidence += 10
        reasons.append("Verletzungslage gibt Vorteil")

    margin = max((s[2] or 0) for s in sides) - sorted((s[2] or 0 for s in sides))[-2]
    if fav_odd < 1.70 and (fav_pct or 0) >= 50:
        confidence += 10
        ai_pick = f"{fav_name} Sieg" if fav_key != "draw" else "Unentschieden"
        reasons.append(f"Klarer Favorit {fav_odd:.2f} ({fav_pct:.0f}%)")
    elif fav_odd < 1.85 and (fav_pct or 0) >= 48:
        ai_pick = f"{fav_name} Sieg" if fav_key != "draw" else "Unentschieden"
        reasons.append(f"Markt-Favorit {fav_odd:.2f} ({fav_pct:.0f}%)")
    elif has_pred:
        api_best = max(
            [
                ("home", pred.get("home_pct"), home),
                ("draw", pred.get("draw_pct"), "X"),
                ("away", pred.get("away_pct"), away),
            ],
            key=lambda x: float(x[1] or 0),
        )
        ai_pick = f"{api_best[2]} Sieg" if api_best[0] != "draw" else "Unentschieden"
        reasons.append("API-Prognose")
    else:
        ai_pick = f"{fav_name} Sieg" if fav_key != "draw" else "Unentschieden"
        reasons.append(f"Niedrigste Quote {fav_odd:.2f}")

    if margin >= 12:
        confidence += 5

    confidence = max(35.0, min(92.0, confidence))

    if confidence < 60:
        no_bet = True
        ai_pick = "No Bet"
        risk = "Hoch"
    elif confidence < 70:
        no_bet = False
        risk = "Mittel"
    else:
        no_bet = False
        risk = "Value"
        value = True

    if no_bet:
        risk = "Hoch"

    return {
        "ai_pick": ai_pick,
        "confidence": round(confidence, 1),
        "no_bet": no_bet,
        "risk": risk,
        "value": value,
        "reasons": reasons[:3],
        "home_pct": home_pct,
        "draw_pct": draw_pct,
        "away_pct": away_pct,
    }


def filter_rows_with_odds(
    rows: list[dict[str, Any]],
    *,
    allow_no_odds: bool = False,
) -> list[dict[str, Any]]:
    if allow_no_odds:
        return list(rows or [])
    return [r for r in rows or [] if has_complete_odds(r)]


def log_fixture_data_sample(
    service: FootballService,
    fixtures: list[dict[str, Any]],
    *,
    username: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Debug: log odds/prediction availability for sample fixtures."""
    samples: list[dict[str, Any]] = []
    for fx in (fixtures or [])[:limit]:
        league = fx.get("league") or {}
        teams = fx.get("teams") or {}
        fid = (fx.get("fixture") or {}).get("id")
        odds_ok = pred_ok = False
        if fid:
            o = get_odds_for_fixture(service, int(fid), username=username)
            odds_ok = has_complete_odds(
                {"home_odd": o.get("home"), "draw_odd": o.get("draw"), "away_odd": o.get("away")}
            )
            try:
                rows = service.get_fixture_predictions(int(fid), username=username)
                pred_ok = bool(rows)
            except FootballAPIError:
                pass
        sample = {
            "fixture_id": fid,
            "league_id": league.get("id"),
            "league_name": league.get("name"),
            "country": league.get("country"),
            "home": (teams.get("home") or {}).get("name"),
            "away": (teams.get("away") or {}).get("name"),
            "odds": odds_ok,
            "prediction": pred_ok,
        }
        samples.append(sample)
        print(sample)
    return samples
