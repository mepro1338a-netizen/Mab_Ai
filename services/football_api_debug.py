"""Football API diagnostics — raw fixtures, league IDs, premium matching, endpoint probes."""
from __future__ import annotations

from collections import Counter
from typing import Any

from config import (
    FOOTBALL_BETTING_CORE_LEAGUE_IDS,
    FOOTBALL_LEAGUE_META,
    FOOTBALL_PREMIUM_LEAGUE_IDS,
    football_api_season,
)
from services.football_leagues import filter_premium_fixtures, is_premium_league_match
from services.football_match_center import _local_today_tomorrow
from services.football_service import FootballAPIError, FootballService


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
                "betting_core": lid in FOOTBALL_BETTING_CORE_LEAGUE_IDS,
                "premium_match": is_premium_league_match(
                    lid,
                    str(league.get("name") or ""),
                    str(league.get("country") or ""),
                ),
            }
        meta[lid]["count"] = counts[lid]
    rows = sorted(meta.values(), key=lambda x: (-int(x["count"]), int(x["league_id"])))
    return rows


def probe_football_api_endpoints(
    service: FootballService,
    *,
    username: str = "",
    sample_fixture_id: int | None = None,
) -> dict[str, Any]:
    """Probe key endpoints — plan limits, season/date issues."""
    today_s, _ = _local_today_tomorrow()
    season = football_api_season()
    probes: list[dict[str, Any]] = []
    discovered_fixture_id = sample_fixture_id

    def _run(
        name: str,
        endpoint: str,
        params: dict[str, Any],
        *,
        feature: str,
        live: bool = False,
    ) -> list[Any]:
        nonlocal discovered_fixture_id
        try:
            rows = service._request(
                endpoint,
                params,
                feature=feature,
                live=live,
                username=username,
            )
            count = len(rows) if isinstance(rows, list) else 0
            err = None
            ok = True
        except FootballAPIError as exc:
            rows = []
            count = 0
            err = str(exc)
            ok = False
        last = service.last_http_debug() or {}
        entry: dict[str, Any] = {
            "name": name,
            "endpoint": endpoint,
            "params": params,
            "ok": ok,
            "count": count,
            "error": err,
            "status_code": last.get("status_code"),
        }
        if ok and count and not discovered_fixture_id and endpoint == "fixtures":
            first = rows[0]
            fid = (first.get("fixture") or {}).get("id")
            if fid:
                discovered_fixture_id = int(fid)
                entry["sample_fixture_id"] = discovered_fixture_id
        probes.append(entry)
        return rows if isinstance(rows, list) else []

    _run("fixtures_by_date", "fixtures", {"date": today_s}, feature="api_fixtures")
    _run(
        "fixtures_league_next",
        "fixtures",
        {"league": 78, "season": season, "next": 3},
        feature="api_fixtures",
    )
    _run(
        "fixtures_league_prev_season",
        "fixtures",
        {"league": 78, "season": season - 1, "next": 3},
        feature="api_fixtures",
    )

    fid = discovered_fixture_id or 0
    if fid:
        _run("odds", "odds", {"fixture": int(fid)}, feature="ai_betting_intelligence", live=True)
        _run("predictions", "predictions", {"fixture": int(fid)}, feature="api_predictions")
        _run("injuries_fixture", "injuries", {"fixture": int(fid)}, feature="api_injuries")
    _run(
        "standings_bundesliga",
        "standings",
        {"league": 78, "season": season},
        feature="api_standings",
    )

    bl_next_ok = False
    bl_next_count = 0
    bl_next_error = None
    for p in probes:
        if p.get("name") == "fixtures_league_next" and p.get("ok"):
            bl_next_ok = True
            bl_next_count = int(p.get("count") or 0)
            bl_next_error = p.get("error")
            break
        if p.get("name") == "fixtures_league_next":
            bl_next_error = p.get("error")

    core_meta = [
        {
            "id": lid,
            "name": FOOTBALL_LEAGUE_META.get(lid, {}).get("name"),
            "country": FOOTBALL_LEAGUE_META.get(lid, {}).get("country"),
        }
        for lid in sorted(FOOTBALL_BETTING_CORE_LEAGUE_IDS)
    ]

    return {
        "season": season,
        "today": today_s,
        "probes": probes,
        "fixtures_ok": any(p["ok"] and p["count"] for p in probes if p["name"] == "fixtures_by_date"),
        "odds_ok": any(p["ok"] and p["count"] for p in probes if p["name"] == "odds"),
        "predictions_ok": any(p["ok"] and p["count"] for p in probes if p["name"] == "predictions"),
        "injuries_ok": any(p["ok"] and p["count"] for p in probes if p["name"] == "injuries_fixture"),
        "standings_ok": any(p["ok"] and p["count"] for p in probes if p["name"] == "standings_bundesliga"),
        "bundesliga_next_ok": bl_next_ok,
        "bundesliga_next_count": bl_next_count,
        "bundesliga_next_error": bl_next_error,
        "betting_core_league_ids": core_meta,
        "sample_fixture_id": fid or None,
    }


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
        for lid in sorted(FOOTBALL_BETTING_CORE_LEAGUE_IDS)
    ]

    premium_ids_in_raw = [lg for lg in leagues_today if lg.get("betting_core")]

    why_zero = "unknown"
    if not raw_today and not raw_live:
        why_zero = "API liefert 0 Fixtures für heute/live"
    elif not premium_ids_in_raw and not premium_upcoming:
        why_zero = (
            "Keine Core-Premium-Liga in Raw-Daten — Saisonpause; "
            "nur Low-Tier-Ligen (USL etc.) aktiv"
        )
    elif not premium_today and premium_upcoming:
        why_zero = "Heute keine Premium-Spiele; nächste Termine im 14-Tage-Scan"
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
        f"- **Nächste Premium (14T):** {report.get('next_premium_upcoming', 0)}",
        f"- **Diagnose:** {report.get('why_premium_zero', '—')}",
        "",
    ]
    leagues = report.get("leagues_today") or []
    if leagues:
        lines.append("| ID | Liga | Land | Spiele | Core |")
        lines.append("|---:|------|------|-------:|:----:|")
        for lg in leagues[:25]:
            prem = "✓" if lg.get("betting_core") else "—"
            lines.append(
                f"| {lg.get('league_id')} | {lg.get('league_name')} | "
                f"{lg.get('country')} | {lg.get('count')} | {prem} |"
            )
    else:
        lines.append("_Keine Ligen in Raw-Daten heute._")
    return "\n".join(lines)


def format_admin_endpoint_probe_markdown(probe: dict[str, Any]) -> str:
    """Admin panel: API plan / endpoint status."""
    lines = [
        "### API Plan / Endpoint Status",
        f"- **Saison (Config):** {probe.get('season', '—')}",
        f"- **Fixtures OK:** {'Ja' if probe.get('fixtures_ok') else 'Nein'}",
        f"- **Odds OK:** {'Ja' if probe.get('odds_ok') else 'Nein'}",
        f"- **Predictions OK:** {'Ja' if probe.get('predictions_ok') else 'Nein'}",
        f"- **Injuries OK:** {'Ja' if probe.get('injuries_ok') else 'Nein'}",
        f"- **Standings OK:** {'Ja' if probe.get('standings_ok') else 'Nein'}",
        f"- **Bundesliga next= OK:** {'Ja' if probe.get('bundesliga_next_ok') else 'Nein'}"
        f" ({probe.get('bundesliga_next_count', 0)} Spiele)",
        "",
        "| Endpoint | Status | Count | Fehler |",
        "|----------|:------:|------:|--------|",
    ]
    for p in probe.get("probes") or []:
        status = "OK" if p.get("ok") and (p.get("count") or 0) >= 0 else "FAIL"
        err = str(p.get("error") or "—")[:60]
        lines.append(
            f"| {p.get('name')} | {status} | {p.get('count', 0)} | {err} |"
        )
    core = probe.get("betting_core_league_ids") or []
    if core:
        lines.append("")
        lines.append("**Premium League IDs (Core):**")
        for lg in core:
            lines.append(f"- {lg.get('id')}: {lg.get('name')} ({lg.get('country')})")
    if probe.get("bundesliga_next_error") and not probe.get("bundesliga_next_ok"):
        lines.append("")
        lines.append(f"_Bundesliga next=: {probe.get('bundesliga_next_error')}_")
    return "\n".join(lines)
