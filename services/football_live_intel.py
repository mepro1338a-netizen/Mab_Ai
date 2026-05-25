"""
Live Match Intelligence — momentum, attacks, AI alerts (API + heuristics).
"""
from __future__ import annotations

from typing import Any


def _stat_value(stats_block: dict, stat_type: str) -> int | float | None:
    for row in stats_block.get("statistics") or []:
        if str(row.get("type", "")).lower() == stat_type.lower():
            val = row.get("value")
            if val is None:
                return None
            if isinstance(val, str) and "%" in val:
                try:
                    return float(val.replace("%", "").strip())
                except ValueError:
                    return None
            try:
                return float(val)
            except (TypeError, ValueError):
                return None
    return None


def parse_fixture_statistics(stats_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Normalize API-Football fixture statistics."""
    home_name, away_name = "Home", "Away"
    home_stats: dict[str, Any] = {}
    away_stats: dict[str, Any] = {}

    for block in stats_rows or []:
        team = (block.get("team") or {}).get("name") or "Team"
        if not home_stats:
            home_name = team
            home_stats = block
        else:
            away_name = team
            away_stats = block

    def pack(block: dict, name: str) -> dict[str, Any]:
        return {
            "team": name,
            "possession": _stat_value(block, "Ball Possession"),
            "shots": _stat_value(block, "Total Shots"),
            "shots_on": _stat_value(block, "Shots on Goal"),
            "corners": _stat_value(block, "Corner Kicks"),
            "dangerous": _stat_value(block, "Dangerous Attacks") or _stat_value(block, "Attacks"),
        }

    h = pack(home_stats, home_name)
    a = pack(away_stats, away_name)
    momentum = _momentum_score(h, a)
    return {"home": h, "away": a, "momentum": momentum}


def _momentum_score(home: dict, away: dict) -> dict[str, Any]:
    h_on = float(home.get("shots_on") or 0)
    a_on = float(away.get("shots_on") or 0)
    h_pos = float(home.get("possession") or 50)
    h_dang = float(home.get("dangerous") or 0)
    a_dang = float(away.get("dangerous") or 0)
    diff = (h_on - a_on) * 8 + (h_pos - 50) * 0.4 + (h_dang - a_dang) * 0.05
    if diff > 12:
        leader, label = home.get("team", "Home"), "Heim dominiert"
    elif diff < -12:
        leader, label = away.get("team", "Away"), "Auswärts dominiert"
    else:
        leader, label = "—", "Ausgeglichen"
    return {
        "score": round(max(-100, min(100, diff)), 1),
        "leader": leader,
        "label": label,
        "pulse": "high" if abs(diff) > 20 else ("mid" if abs(diff) > 8 else "low"),
    }


def live_fixture_snapshot(fixture_row: dict[str, Any]) -> dict[str, Any]:
    fix = fixture_row.get("fixture") or {}
    teams = fixture_row.get("teams") or {}
    goals = fixture_row.get("goals") or {}
    status = (fix.get("status") or {}).get("short") or ""
    elapsed = (fix.get("status") or {}).get("elapsed") or 0
    home = (teams.get("home") or {}).get("name") or "Home"
    away = (teams.get("away") or {}).get("name") or "Away"
    gh = goals.get("home")
    ga = goals.get("away")
    scoreline = f"{gh} - {ga}" if gh is not None else "vs"
    is_live = status in ("1H", "2H", "HT", "ET", "P", "LIVE")
    upset = False
    if is_live and gh is not None and ga is not None:
        try:
            upset = int(gh) < int(ga) and elapsed and int(elapsed) > 60
        except (TypeError, ValueError):
            upset = False
    return {
        "fixture_id": fix.get("id"),
        "home": home,
        "away": away,
        "status": status,
        "elapsed": elapsed,
        "scoreline": scoreline,
        "is_live": is_live,
        "upset_alert": upset,
    }


def build_live_alerts(
    fixtures: list[dict[str, Any]],
    *,
    value_markets: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for fx in fixtures or []:
        snap = live_fixture_snapshot(fx)
        if snap.get("is_live"):
            alerts.append({
                "type": "live",
                "severity": "info",
                "title": f"LIVE · {snap['home']} {snap['scoreline']} {snap['away']}",
                "detail": f"{snap.get('elapsed', '?')}' · Status {snap.get('status')}",
            })
        if snap.get("upset_alert"):
            alerts.append({
                "type": "upset",
                "severity": "warn",
                "title": f"Upset Watch · {snap['away']} führt",
                "detail": f"{snap['home']} vs {snap['away']} — spät im Spiel",
            })

    for v in (value_markets or [])[:3]:
        alerts.append({
            "type": "value",
            "severity": "success",
            "title": "Value Odds Signal",
            "detail": f"{v.get('bookmaker', '')} · {v.get('selection', '')} @ {v.get('odd', '')}",
        })
    return alerts[:20]
