"""Elite Betting Intelligence Card — compact tip synthesis from match data."""
from __future__ import annotations

from typing import Any

from services.football_betting_intel import full_betting_analysis, implied_probability
from services.football_odds import calculate_tip_odds


def _risk_from_confidence(conf: float, odds: float = 2.0) -> str:
    if conf < 42 or odds >= 4.0:
        return "Hoch"
    if conf < 62 or odds >= 2.6:
        return "Mittel"
    return "Niedrig"


def _injury_impact_level(count: int, reasons: list[str]) -> str:
    if count == 0:
        return "niedrig"
    heavy = sum(
        1 for r in reasons
        if any(x in r.lower() for x in ("knee", "muscle", "hamstring", "acl", "rupture", "surgery"))
    )
    if count >= 4 or heavy >= 2:
        return "hoch"
    if count >= 2:
        return "mittel"
    return "niedrig"


def _parse_injuries_detail(detail: dict[str, Any]) -> dict[str, Any]:
    home_rows = detail.get("home_injuries") or []
    away_rows = detail.get("away_injuries") or []
    card = detail.get("card") or {}

    def _row(r: dict) -> dict[str, str]:
        pl = (r.get("player") or {})
        name = pl.get("name") if isinstance(pl, dict) else str(pl or "Spieler")
        pos = pl.get("position") or pl.get("type") or r.get("type") or "—"
        reason = str(r.get("reason") or r.get("type") or "Ausfall")
        return {"player": str(name), "position": str(pos), "reason": reason}

    home = [_row(r) for r in home_rows[:8]]
    away = [_row(r) for r in away_rows[:8]]
    home_reasons = [x["reason"] for x in home]
    away_reasons = [x["reason"] for x in away]

    return {
        "home": home,
        "away": away,
        "home_impact": _injury_impact_level(len(home), home_reasons),
        "away_impact": _injury_impact_level(len(away), away_reasons),
        "available": bool(home or away),
        "missing": "injuries" in (detail.get("missing") or []),
    }


def _h2h_line(detail: dict[str, Any]) -> str:
    rows = detail.get("h2h") or []
    if not rows:
        return ""
    parts = []
    for fx in rows[:3]:
        t = fx.get("teams") or {}
        g = fx.get("goals") or {}
        parts.append(
            f"{(t.get('home') or {}).get('name', '?')} {g.get('home')}-{g.get('away')} "
            f"{(t.get('away') or {}).get('name', '?')}"
        )
    return " · ".join(parts)


def _standing_line(detail: dict[str, Any], card: dict[str, Any]) -> str:
    hs = detail.get("home_standing") or {}
    aws = detail.get("away_standing") or {}
    if not hs and not aws:
        return ""
    h = f"#{hs.get('rank', '—')} ({hs.get('points', '—')} Pkt)" if hs else "—"
    a = f"#{aws.get('rank', '—')} ({aws.get('points', '—')} Pkt)" if aws else "—"
    return f"{card.get('home', 'Heim')} Tab. {h} · {card.get('away', 'Ausw.')} Tab. {a}"


def _live_momentum_line(detail: dict[str, Any], bundle: dict[str, Any] | None) -> str:
    if bundle:
        mom = (bundle.get("overview") or {}).get("momentum") or {}
        label = mom.get("label") or ""
        leader = mom.get("leader") or ""
        if label:
            return f"Live: {label}" + (f" ({leader})" if leader else "")
    events = detail.get("events") or []
    goals = 0
    for block in events:
        nested = block.get("events")
        ev_list = nested if nested else ([block] if block.get("type") or block.get("time") else [])
        for ev in ev_list:
            if str(ev.get("type") or "").lower() == "goal":
                goals += 1
    if detail.get("card", {}).get("live"):
        return f"Live-Spiel · {goals} Tore im Feed"
    return ""


def _pick_main_tip(
    card: dict[str, Any],
    pred: dict[str, Any],
    detail: dict[str, Any],
    bundle: dict[str, Any] | None,
) -> tuple[str, float, bool]:
    """Returns (main_pick, confidence, no_bet)."""
    advice = (pred.get("advice") or "").strip()
    hp = pred.get("home_pct")
    dp = pred.get("draw_pct")
    ap = pred.get("away_pct")
    home = card.get("home") or "Heim"
    away = card.get("away") or "Auswärts"

    if advice:
        low = advice.lower()
        if "no bet" in low or "avoid" in low:
            return "No Bet", 35.0, True
        if len(advice) < 120:
            return advice, 58.0, False

    values = [(hp, home), (ap, away), (dp, "Unentschieden")]
    valid = [(v, name) for v, name in values if v is not None]
    if not valid:
        if card.get("live"):
            return "Live: Momentum prüfen — kein klarer Tipp", 40.0, True
        return "No Bet — zu wenig Prognose-Daten", 32.0, True

    best_val, best_name = max(valid, key=lambda x: float(x[0]))
    second_val = sorted([float(v) for v, _ in valid], reverse=True)
    second_val = second_val[1] if len(second_val) > 1 else 0.0
    margin = float(best_val) - second_val

    if float(best_val) < 48 or margin < 8:
        return "No Bet — Markt zu offen", max(30.0, float(best_val) - 5), True

    if best_name == "Unentschieden":
        pick = "Unentschieden"
    elif best_name == home:
        pick = f"{home} gewinnt"
        if margin < 12 and dp and float(dp) > 28:
            pick = f"Doppelte Chance {home[0].upper()}1" if len(home) > 2 else f"DC 1X — {home}"
    else:
        pick = f"{away} gewinnt"
        if margin < 12 and dp and float(dp) > 28:
            pick = f"Doppelte Chance X2 — {away}"

    conf = min(88.0, float(best_val) + margin * 0.35)

    gh = (detail.get("card") or {}).get("score") or ""
    if card.get("live") and " : " in str(gh):
        try:
            parts = str(gh).split(":")
            total = int(parts[0].strip()) + int(parts[1].strip())
            if total >= 1:
                pick = "Over 1.5 Tore"
                conf = min(82.0, conf + 6)
        except (ValueError, TypeError):
            pass

    winner = (pred.get("winner_comment") or "").lower()
    if "both teams score" in winner or "btts" in winner:
        if margin < 15:
            pick = "Beide Teams treffen"
            conf = min(75.0, conf)

    injuries = _parse_injuries_detail(detail)
    if injuries["home_impact"] == "hoch" and pick.startswith(home):
        conf -= 12
    if injuries["away_impact"] == "hoch" and away in pick:
        conf -= 12

    if conf < 45:
        return "No Bet — Signal zu schwach", conf, True

    return pick, round(conf, 1), False


def _build_reasons(
    detail: dict[str, Any],
    card: dict[str, Any],
    pred: dict[str, Any],
    bundle: dict[str, Any] | None,
) -> list[str]:
    reasons: list[str] = []

    hf = detail.get("home_form") or pred.get("form_home")
    af = detail.get("away_form") or pred.get("form_away")
    if hf or af:
        reasons.append(f"Form (5): {card.get('home', 'H')} {hf or '—'} · {card.get('away', 'A')} {af or '—'}")

    h2h = _h2h_line(detail)
    if h2h:
        reasons.append(f"H2H: {h2h}")

    tab = _standing_line(detail, card)
    if tab:
        reasons.append(tab)

    inj = _parse_injuries_detail(detail)
    if inj["available"]:
        reasons.append(
            f"Verletzungen: Heim {inj['home_impact']} ({len(inj['home'])}), "
            f"Auswärts {inj['away_impact']} ({len(inj['away'])})"
        )
    elif inj["missing"]:
        reasons.append("Verletzungen: keine API-Daten")

    if detail.get("lineups"):
        reasons.append("Aufstellungen verfügbar")

    live = _live_momentum_line(detail, bundle)
    if live:
        reasons.append(live)

    if pred.get("advice") and len(reasons) < 4:
        short = pred["advice"][:90] + ("…" if len(pred["advice"]) > 90 else "")
        reasons.append(f"API: {short}")

    if not reasons:
        reasons.append("Datenbasis begrenzt — vorsichtig bewerten")

    return reasons


def build_betting_intelligence_card(
    detail: dict[str, Any],
    *,
    bundle: dict[str, Any] | None = None,
    user_odd: float | None = None,
) -> dict[str, Any]:
    """Build compact intelligence card from fetch_match_detail (+ optional elite bundle)."""
    card = detail.get("card") or {}
    pred = detail.get("prediction_insights") or {}
    missing = list(detail.get("missing") or [])

    main_pick, confidence, no_bet = _pick_main_tip(card, pred, detail, bundle)
    reasons_all = _build_reasons(detail, card, pred, bundle)
    injuries = _parse_injuries_detail(detail)

    ai_prob = float(pred.get("home_pct") or 50.0)
    if main_pick and card.get("away", "") in main_pick:
        ai_prob = float(pred.get("away_pct") or ai_prob)
    elif "Unentschieden" in main_pick:
        ai_prob = float(pred.get("draw_pct") or ai_prob)

    value_block: dict[str, Any] | None = None
    if user_odd and user_odd >= 1.01:
        core = calculate_tip_odds(float(user_odd), 10.0, ai_prob)
        value_block = {
            "user_odd": float(user_odd),
            "implied_pct": core["implied_probability_pct"],
            "ai_pct": round(ai_prob, 1),
            "edge_pct": core["edge_pct"],
            "expected_value": core["expected_value"],
            "verdict": core["value_label"],
            "is_value": core["is_value_bet"],
        }

    odds_markets = detail.get("odds") or []
    if bundle and bundle.get("odds_intel"):
        oi = bundle["odds_intel"]
        if not value_block and oi.get("implied_probability_pct"):
            value_block = {
                "user_odd": None,
                "implied_pct": oi.get("implied_probability_pct"),
                "ai_pct": ai_prob,
                "edge_pct": oi.get("edge_pct"),
                "expected_value": oi.get("expected_value"),
                "verdict": oi.get("value_label", "—"),
                "is_value": oi.get("is_value_bet"),
            }

    risk = _risk_from_confidence(confidence, float(user_odd or 2.1))
    if no_bet:
        risk = "Hoch"

    time_show = card.get("time") or ""
    if card.get("live") and card.get("minute") is not None:
        time_show = f"Live {card.get('status_label', '')}"

    return {
        "header": {
            "home": card.get("home", ""),
            "away": card.get("away", ""),
            "league": card.get("league", ""),
            "time": time_show,
            "date": card.get("date", ""),
            "score": card.get("score", "vs"),
            "live": bool(card.get("live")),
        },
        "recommendation": {
            "main_pick": main_pick,
            "confidence": round(confidence, 1),
            "risk": risk,
            "no_bet": no_bet,
        },
        "reasons_short": reasons_all[:3],
        "reasons_full": reasons_all,
        "injuries": injuries,
        "prediction": {
            "home_pct": pred.get("home_pct"),
            "draw_pct": pred.get("draw_pct"),
            "away_pct": pred.get("away_pct"),
            "advice": pred.get("advice", ""),
        },
        "value_quote": value_block,
        "lineups_available": bool(detail.get("lineups")),
        "data_gaps": missing,
        "has_predictions": bool(pred),
    }


def build_pro_preview_card(detail: dict[str, Any]) -> dict[str, Any]:
    """Pro: preview only — no main tip."""
    card = detail.get("card") or {}
    pred = detail.get("prediction_insights") or {}
    return {
        "header": {
            "home": card.get("home", ""),
            "away": card.get("away", ""),
            "league": card.get("league", ""),
            "score": card.get("score", "vs"),
            "time": card.get("time") or card.get("date", ""),
            "live": bool(card.get("live")),
        },
        "prediction": {
            "home_pct": pred.get("home_pct"),
            "draw_pct": pred.get("draw_pct"),
            "away_pct": pred.get("away_pct"),
            "advice": pred.get("advice", ""),
        },
        "reasons_short": _build_reasons(detail, card, pred, None)[:3],
        "upgrade_hint": "Volle Tippempfehlung, Value-Rechner & Verletzungsimpact ab Football Elite.",
    }
