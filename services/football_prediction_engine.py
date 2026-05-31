"""KI-Spielprognose — Ergebnis, Wettmarkt, Konfidenz, Begründung."""
from __future__ import annotations

from typing import Any


def _pct(pred: dict[str, Any], key: str) -> float | None:
    val = pred.get(key)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _outcome_label(home: str, away: str, winner: str) -> str:
    if winner == "home":
        return "Heimsieg"
    if winner == "away":
        return "Auswärtssieg"
    return "Unentschieden"


def _form_wins(form: str) -> int:
    return sum(1 for c in (form or "").upper().split() if c == "W")


def _standing_gf_ga(summary: dict[str, Any] | None) -> tuple[float, float]:
    if not summary:
        return 0.0, 0.0
    try:
        played = max(1, int(summary.get("played") or 1))
        gf = float(summary.get("goals_for") or 0) / played
        ga = float(summary.get("goals_against") or 0) / played
        return gf, ga
    except (TypeError, ValueError):
        return 0.0, 0.0


def _score_markets(
    *,
    hp: float | None,
    dp: float | None,
    ap: float | None,
    home: str,
    away: str,
    detail: dict[str, Any],
    card: dict[str, Any],
) -> list[tuple[str, float, str]]:
    """Markt-Kandidaten: (Bezeichnung, Score, kurze Begründung)."""
    candidates: list[tuple[str, float, str]] = []
    if hp is None and dp is None and ap is None:
        return candidates

    hp_v = float(hp or 0)
    dp_v = float(dp or 0)
    ap_v = float(ap or 0)
    margin_ha = abs(hp_v - ap_v)
    best_side = "home" if hp_v >= ap_v else "away"
    best_team = home if best_side == "home" else away
    weaker = away if best_side == "home" else home

    hs = detail.get("home_standing_summary") or {}
    aws = detail.get("away_standing_summary") or {}
    hgf, hga = _standing_gf_ga(hs)
    agf, aga = _standing_gf_ga(aws)
    avg_goals = hgf + agf
    both_score_tendency = min(hgf, agf) + min(hga, aga)

    hf = str(detail.get("home_form") or "")
    af = str(detail.get("away_form") or "")
    home_w = _form_wins(hf)
    away_w = _form_wins(af)

    xg = detail.get("xg") or {}
    hxg = xg.get("home_xg")
    axg = xg.get("away_xg")

    inj = detail.get("injuries_parsed") or {}
    susp = detail.get("suspensions_parsed") or {}
    home_abs = len(inj.get("home") or []) + len(susp.get("home") or [])
    away_abs = len(inj.get("away") or []) + len(susp.get("away") or [])

    if margin_ha >= 12 and hp_v >= 52:
        candidates.append((f"{home} DNB", hp_v + 8, f"{home} Favorit laut Prognose"))
    elif margin_ha >= 12 and ap_v >= 52:
        candidates.append((f"{away} DNB", ap_v + 8, f"{away} Favorit laut Prognose"))
    elif dp_v >= 30 and margin_ha < 10:
        candidates.append((f"{away} DNB", ap_v + 4, "Enges Duell"))

    if dp_v >= 28 and margin_ha < 8:
        candidates.append(("Unentschieden", dp_v, "Ausgeglichene Wahrscheinlichkeiten"))
    elif margin_ha < 12:
        if best_side == "home":
            candidates.append((f"Doppelte Chance 1X — {home}", hp_v + dp_v * 0.5, f"Sicherheitsoption {home}"))
        else:
            candidates.append((f"Doppelte Chance X2 — {away}", ap_v + dp_v * 0.5, f"Sicherheitsoption {away}"))

    if avg_goals >= 1.35:
        candidates.append(("Über 2,5 Tore", min(85.0, 48 + avg_goals * 22), "Beide Teams torstark"))
    elif avg_goals > 0 and avg_goals < 1.05:
        candidates.append(("Unter 2,5 Tore", min(82.0, 52 + (1.05 - avg_goals) * 20), "Defensive Saisonwerte"))

    if both_score_tendency >= 0.9 or (hgf > 1.0 and agf > 1.0):
        candidates.append(("Beide treffen", min(80.0, 45 + both_score_tendency * 25), "Beide treffen regelmäßig"))

    if best_side == "home" and hp_v >= 50:
        candidates.append((f"{home} gewinnt", hp_v, f"{home} Prognose-Favorit"))
    elif best_side == "away" and ap_v >= 50:
        candidates.append((f"{away} gewinnt", ap_v, f"{away} Prognose-Favorit"))

    if card.get("live"):
        gh = str(card.get("score") or "")
        if " : " in gh:
            try:
                a, b = gh.split(":")
                total = int(a.strip()) + int(b.strip())
                if total >= 2:
                    candidates.append(("Über 2,5 Tore", 72.0, f"Live bereits {total} Tore"))
                elif total == 0:
                    candidates.append(("Unter 2,5 Tore", 68.0, "Live noch torlos"))
            except (ValueError, TypeError):
                pass

    if hxg is not None and axg is not None:
        if float(hxg) > float(axg) + 0.35:
            candidates.append((f"{home} DNB", hp_v + 6, f"xG-Vorteil {home} ({hxg} vs {axg})"))
        elif float(axg) > float(hxg) + 0.35:
            candidates.append((f"{away} DNB", ap_v + 6, f"xG-Vorteil {away} ({axg} vs {hxg})"))

    if home_w >= 3 and away_w <= 1:
        candidates.append((f"{home} gewinnt", hp_v + 5, f"{home} starke Form ({hf.strip()})"))
    if away_w >= 3 and home_w <= 1:
        candidates.append((f"{away} gewinnt", ap_v + 5, f"{away} starke Form ({af.strip()})"))

    if away_abs >= 2 and best_side == "home":
        candidates.append((f"{home} DNB", hp_v + 7, f"{weaker} mit {away_abs} Ausfällen/Sperren"))
    if home_abs >= 2 and best_side == "away":
        candidates.append((f"{away} DNB", ap_v + 7, f"{weaker} mit {home_abs} Ausfällen/Sperren"))

    return candidates


def build_match_prediction(
    detail: dict[str, Any],
    *,
    bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Vollständiges Prognosepaket für ein Spiel."""
    card = detail.get("card") or {}
    pred = detail.get("prediction_insights") or {}
    home = card.get("home") or "Heim"
    away = card.get("away") or "Auswärts"

    hp, dp, ap = _pct(pred, "home_pct"), _pct(pred, "draw_pct"), _pct(pred, "away_pct")
    values = [("home", hp, home), ("draw", dp, home), ("away", ap, away)]
    valid = [(k, v, n) for k, v, n in values if v is not None]
    outcome = "Unentschieden"
    outcome_conf = 33.0
    if valid:
        winner_key, best, _ = max(valid, key=lambda x: float(x[1]))
        outcome = _outcome_label(home, away, winner_key)
        second = sorted([float(v) for _, v, _ in valid], reverse=True)
        margin = float(best) - (second[1] if len(second) > 1 else 0.0)
        outcome_conf = min(92.0, float(best) + margin * 0.25)

    markets = _score_markets(
        hp=hp, dp=dp, ap=ap, home=home, away=away, detail=detail, card=card
    )
    best_bet = "—"
    best_conf = 35.0
    market_reason = ""
    if markets:
        markets.sort(key=lambda x: x[1], reverse=True)
        best_bet, best_conf, market_reason = markets[0]

    inj = detail.get("injuries_parsed") or {}
    susp = detail.get("suspensions_parsed") or {}
    reasons: list[str] = []

    hf = detail.get("home_form") or pred.get("form_home") or ""
    af = detail.get("away_form") or pred.get("form_away") or ""
    if hf.strip() and hf != "—":
        reasons.append(f"{home} Form (5): {hf.strip()}")
    if af.strip() and af != "—":
        reasons.append(f"{away} Form (5): {af.strip()}")

    hs = detail.get("home_standing_summary") or {}
    aws = detail.get("away_standing_summary") or {}
    if hs.get("rank") is not None:
        reasons.append(
            f"{home} Tabellenplatz #{hs.get('rank')} · {hs.get('goals_for', '—')}:{hs.get('goals_against', '—')} Tore"
        )
    if aws.get("rank") is not None:
        reasons.append(
            f"{away} Tabellenplatz #{aws.get('rank')} · {aws.get('goals_for', '—')}:{aws.get('goals_against', '—')} Tore"
        )

    if inj.get("available"):
        reasons.append(
            f"Verletzungen: {home} {inj.get('home_impact', '—')} · {away} {inj.get('away_impact', '—')}"
        )
    if susp.get("available"):
        reasons.append(
            f"Sperren: {home} {len(susp.get('home') or [])} · {away} {len(susp.get('away') or [])}"
        )

    xg = detail.get("xg") or {}
    if xg.get("home_xg") is not None and xg.get("away_xg") is not None:
        reasons.append(f"xG: {home} {xg['home_xg']} · {away} {xg['away_xg']}")

    if market_reason:
        reasons.append(market_reason)

    if bundle:
        mom = (bundle.get("overview") or {}).get("momentum") or {}
        if mom.get("label"):
            reasons.append(f"Live: {mom.get('label')}")

    if pred.get("advice") and len(reasons) < 5:
        adv = str(pred["advice"])[:100]
        reasons.append(f"API-Prognose: {adv}")

    reasons = reasons[:5]
    while len(reasons) < 3 and pred.get("winner_comment"):
        reasons.append(str(pred["winner_comment"])[:90])
        break

    no_bet = best_conf < 48 or (hp is None and dp is None and ap is None)
    if no_bet and best_bet != "—":
        no_bet = best_conf < 42

    return {
        "outcome": outcome,
        "outcome_confidence": round(outcome_conf, 1),
        "best_bet": best_bet,
        "best_bet_confidence": round(min(95.0, best_conf), 1),
        "no_bet": no_bet,
        "reasons": reasons,
        "markets_considered": [m[0] for m in markets[:6]],
    }
