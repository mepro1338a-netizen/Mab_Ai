"""Football API diagnostics — raw fixtures, league IDs, premium matching."""
from __future__ import annotations

from collections import Counter
from typing import Any

from config import FOOTBALL_LEAGUE_META, FOOTBALL_PREMIUM_LEAGUE_IDS
from services.football_leagues import filter_premium_fixtures, is_premium_league_match


def _fixture_summary(fx: dict[str, Any]) -> dict[str, Any]:
    league = fx.get("league") or {}
    teams = fx.get("teams") or {}
    fixture = fx.get("fixture") or {}
    status = fixture.get("status") or {}
    return {
        "league_id": league.get("id"),
        "league_name": league.get("name"),
        "country": league.get("country"),
        "season": league.get("season"),
        "home": (teams.get("home") or {}).get("name"),
        "away": (teams.get("away") or {}).get("name"),
        "date": str(fixture.get("date") or "")[:10],
        "status": status.get("short"),
        "fixture_id": fixture.get("id"),
    }


def log_raw_fixtures_sample(
    fixtures: list[dict[str, Any]],
    *,
    label: str = "raw",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Log first N raw API fixtures for root-cause analysis."""
    sample = [_fixture_summary(fx) for fx in (fixtures or [])[:limit]]
    print({f"football_raw_{label}": {"count": len(fixtures or []), "sample": sample}})
    return sample


def league_ids_in_fixtures(
    fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Unique leagues in fixture list with match counts."""
    counts: Counter[int] = Counter()
    meta: dict[int, dict[str, Any]] = {}
    for fx in fixtures or []:
        league = fx.get("league") or {}
        try:
            lid = int(league.get("id") or 0)
        except (TypeError, ValueError):
            continue
        if not lid:
            continue
        counts[lid] += 1
        if lid not in meta:
            meta[lid] = {
                "league_id": lid,
                "league_name": league.get("name"),
                "country": league.get("country"),
                "count": 0,
                "premium_whitelist": lid in FOOTBALL_PREMIUM_LEAGUE_IDS,
                "premium_match": is_premium_league_match(
                    lid,
                    str(league.get("name") or ""),
                    str(league.get("country") or ""),
                ),
            }
        meta[lid]["count"] = counts[lid]
    rows = sorted(meta.values(), key=lambda x: (-int(x["count"]), int(x["league_id"])))
    return rows


def build_premium_diagnosis_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Compare raw API leagues vs premium whitelist."""
    raw_today = list(payload.get("raw_today") or [])
    raw_live = list(payload.get("raw_live") or [])
    raw_tomorrow = list(payload.get("raw_tomorrow") or [])
    merged_raw = raw_live + raw_today + raw_tomorrow

    leagues_today = league_ids_in_fixtures(raw_today)
    premium_today = filter_premium_fixtures(raw_today)
    premium_upcoming = list(payload.get("next_matches") or [])

    whitelist_names = [
        {
            "id": lid,
            "name": FOOTBALL_LEAGUE_META.get(lid, {}).get("name"),
            "country": FOOTBALL_LEAGUE_META.get(lid, {}).get("country"),
        }
        for lid in sorted(FOOTBALL_PREMIUM_LEAGUE_IDS)
    ]

    premium_ids_in_raw = [lg for lg in leagues_today if lg.get("premium_match")]

    why_zero = "unknown"
    if not raw_today and not raw_live:
        why_zero = "API liefert 0 Fixtures für heute/live"
    elif not premium_ids_in_raw and not premium_upcoming:
        why_zero = (
            "Keine Premium-Liga in Raw-Daten — Saisonpause; "
            "nur Low-Tier-Ligen (USL etc.) aktiv"
        )
    elif not premium_today and premium_upcoming:
        why_zero = "Heute keine Premium-Spiele; nächste Termine in 7-Tage-Scan"
    elif not premium_today:
        why_zero = "Premium-Ligen erkannt, aber Filter/Region schließt alle aus"

    return {
        "api_ok": bool(merged_raw),
        "raw_matches_total": len(merged_raw),
        "raw_today": len(raw_today),
        "raw_live": len(raw_live),
        "raw_tomorrow": len(raw_tomorrow),
        "premium_after_filter_today": len(premium_today),
        "next_premium_upcoming": len(premium_upcoming),
        "leagues_today": leagues_today,
        "premium_leagues_in_raw": premium_ids_in_raw,
        "whitelist_ids": whitelist_names,
        "why_premium_zero": why_zero,
    }


def format_admin_league_debug_markdown(report: dict[str, Any]) -> str:
    """Admin panel: leagues found today vs whitelist."""
    lines = [
        "### Gefundene League IDs heute",
        f"- **API OK:** {'Ja' if report.get('api_ok') else 'Nein'}",
        f"- **Raw heute:** {report.get('raw_today', 0)} · "
        f"**Premium nach Filter:** {report.get('premium_after_filter_today', 0)}",
        f"- **Nächste Premium (7T):** {report.get('next_premium_upcoming', 0)}",
        f"- **Diagnose:** {report.get('why_premium_zero', '—')}",
        "",
    ]
    leagues = report.get("leagues_today") or []
    if leagues:
        lines.append("| ID | Liga | Land | Spiele | Premium |")
        lines.append("|---:|------|------|-------:|:-------:|")
        for lg in leagues[:25]:
            prem = "✓" if lg.get("premium_match") else "—"
            lines.append(
                f"| {lg.get('league_id')} | {lg.get('league_name')} | "
                f"{lg.get('country')} | {lg.get('count')} | {prem} |"
            )
    else:
        lines.append("_Keine Ligen in Raw-Daten heute._")
    return "\n".join(lines)
