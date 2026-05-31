"""Build match analysis sections — only blocks with real API data."""
from __future__ import annotations

from typing import Any


def _form_usable(form: dict[str, Any] | None) -> bool:
    if not form:
        return False
    for side in ("home", "away"):
        f = str(form.get(side) or "").strip()
        if f and f != "—":
            return True
    return False


def _injuries_usable(inj: dict[str, Any] | None) -> bool:
    return bool(inj and inj.get("available"))


def _prediction_usable(pred: dict[str, Any] | None) -> bool:
    if not pred:
        return False
    return any(
        pred.get(k) is not None
        for k in ("home_pct", "draw_pct", "away_pct")
    ) or bool(str(pred.get("advice") or "").strip())


def _intel_usable(intel: dict[str, Any] | None) -> bool:
    if not intel:
        return False
    rec = intel.get("recommendation") or {}
    return bool(rec.get("main_pick"))


def _h2h_usable(h2h: Any) -> bool:
    if isinstance(h2h, list):
        return len(h2h) > 0
    if not h2h or not isinstance(h2h, dict):
        return False
    return bool(h2h.get("rows") or h2h.get("summary"))


def build_match_analysis_sections(
    detail: dict[str, Any],
    intel: dict[str, Any] | None = None,
    *,
    live_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Return only sections that have displayable data.
    Keys: prediction, confidence, injuries, form, h2h, xg, best_bet, reasoning, live_stats
    """
    sections: dict[str, Any] = {}
    pred = detail.get("prediction_insights") or {}
    inj = detail.get("injuries") or {}
    form = detail.get("form") or {
        "home": detail.get("home_form") or pred.get("form_home"),
        "away": detail.get("away_form") or pred.get("form_away"),
    }
    h2h = detail.get("h2h") or []
    xg = detail.get("xg")
    bundle = live_bundle or {}

    if _prediction_usable(pred):
        sections["prediction"] = pred

    conf = None
    if intel:
        rec = intel.get("recommendation") or {}
        if rec.get("confidence") is not None:
            conf = rec.get("confidence")
    if conf is not None:
        sections["confidence"] = conf

    if _injuries_usable(inj):
        sections["injuries"] = inj
    else:
        from services.football_elite_betting_card import _parse_injuries_detail

        parsed = _parse_injuries_detail(detail)
        if parsed.get("available"):
            sections["injuries"] = parsed

    if _form_usable(form):
        sections["form"] = form

    if _h2h_usable(h2h):
        sections["h2h"] = h2h

    if xg:
        sections["xg"] = xg

    stats = detail.get("match_stats") or bundle.get("statistics")
    if stats and isinstance(stats, dict) and (stats.get("home") or stats.get("away")):
        sections["live_stats"] = stats

    if _intel_usable(intel):
        rec = intel.get("recommendation") or {}
        sections["best_bet"] = {
            "pick": rec.get("main_pick"),
            "risk": rec.get("risk"),
            "no_bet": rec.get("no_bet"),
        }
        reasons = intel.get("reasons_full") or intel.get("reasons_short") or []
        if reasons:
            sections["reasoning"] = reasons

    return sections
