"""Football data-flow diagnosis — API probes, filter pipeline, dates."""
from __future__ import annotations

import os
from typing import Any

from services.football_betting_quality import filter_bettable_fixtures
from services.football_betting_board import collect_fixtures_for_filters, league_group_ids
from services.football_leagues import filter_premium_fixtures
from services.football_match_center import _local_today_tomorrow, dedupe_fixtures, parse_match_card
from services.football_service import FootballAPIError, FootballService


def football_debug_enabled() -> bool:
    return os.getenv("ADMIN_DEBUG", "").strip().lower() in ("1", "true", "yes", "on")


def _probe(
    service: FootballService,
    endpoint: str,
    params: dict[str, Any],
    *,
    username: str,
    live: bool = False,
    raw: bool = False,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "endpoint": endpoint,
        "params": dict(params),
        "status_code": None,
        "response_length": 0,
        "cached": False,
        "error": "",
        "ok": False,
    }
    probe_user = "" if raw else username
    try:
        data = service._request(
            endpoint,
            params,
            feature="api_fixtures",
            live=live,
            username=probe_user,
        )
        row["response_length"] = len(data) if isinstance(data, list) else 0
        row["ok"] = True
        last = service.last_http_debug()
        if last:
            row["status_code"] = last.get("status_code")
            row["cached"] = bool(last.get("cached"))
            row["rate_limit_remaining"] = last.get("rate_limit_remaining")
    except FootballAPIError as exc:
        row["error"] = str(exc)
        row["status_code"] = getattr(exc, "status_code", None)
        last = service.last_http_debug()
        if last:
            row["cached"] = bool(last.get("cached"))
            row["rate_limit_remaining"] = last.get("rate_limit_remaining")
    return row


def diagnose_filter_pipeline(
    raw_fixtures: list[dict[str, Any]],
    *,
    today_s: str,
    tomorrow_s: str,
) -> dict[str, Any]:
    """Count fixtures at each filter stage."""
    before = len(raw_fixtures or [])
    premium = filter_bettable_fixtures(filter_premium_fixtures(raw_fixtures or []))
    after_premium = len(premium)

    de_ids = league_group_ids("deutschland") or frozenset()
    uefa_ids = league_group_ids("uefa") or frozenset()

    de_pool = [
        fx
        for fx in premium
        if int((fx.get("league") or {}).get("id") or 0) in de_ids
    ]
    uefa_pool = [
        fx
        for fx in premium
        if int((fx.get("league") or {}).get("id") or 0) in uefa_ids
    ]

    today_live = [
        fx
        for fx in premium
        if parse_match_card(fx).get("date") == today_s
        or str(((fx.get("fixture") or {}).get("status") or {}).get("short") or "") in {
            "1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"
        }
    ]
    tomorrow_pool = [fx for fx in premium if parse_match_card(fx).get("date") == tomorrow_s]

    return {
        "before_filter": before,
        "after_premium_filter": after_premium,
        "after_deutschland_filter": len(de_pool),
        "after_uefa_filter": len(uefa_pool),
        "today_matches": len(today_live),
        "tomorrow_matches": len(tomorrow_pool),
        "live_matches_raw": sum(
            1
            for fx in raw_fixtures or []
            if str(((fx.get("fixture") or {}).get("status") or {}).get("short") or "")
            in {"1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"}
        ),
    }


def run_board_diagnosis(
    service: FootballService,
    *,
    username: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full diagnosis for Heute / Live / Morgen data path."""
    today_s, tomorrow_s = _local_today_tomorrow()
    report: dict[str, Any] = {
        "dates": {
            "timezone": "Europe/Berlin",
            "today": today_s,
            "tomorrow": tomorrow_s,
        },
        "probes": {},
        "filter_pipeline": {},
        "counts": {},
        "api_status": "UNKNOWN",
        "rate_limit_hit": False,
        "internal_rate_limit": False,
        "errors": [],
    }

    live_probe = _probe(
        service, "fixtures", {"live": "all"}, username=username, live=True, raw=True
    )
    today_probe = _probe(
        service, "fixtures", {"date": today_s}, username=username, live=False, raw=True
    )
    tomorrow_probe = _probe(
        service, "fixtures", {"date": tomorrow_s}, username=username, live=False, raw=True
    )

    report["probes"] = {
        "live": live_probe,
        "heute": today_probe,
        "morgen": tomorrow_probe,
    }

    for key, probe in report["probes"].items():
        err = str(probe.get("error") or "")
        if "Rate Limit" in err or probe.get("status_code") == 429:
            report["rate_limit_hit"] = True
        if "Rate Limit erreicht" in err and probe.get("status_code") != 429:
            report["internal_rate_limit"] = True
        if probe.get("error"):
            report["errors"].append(f"{key}: {err}")

    any_ok = any(p.get("ok") for p in report["probes"].values())
    report["api_status"] = "OK" if any_ok else "ERROR"

    raw_live = []
    raw_today = []
    raw_tomorrow = []
    if live_probe.get("ok"):
        raw_live = service._request(
            "fixtures",
            {"live": "all"},
            feature="api_fixtures",
            live=True,
            username="",
        )
    if today_probe.get("ok"):
        raw_today = service._request(
            "fixtures",
            {"date": today_s},
            feature="api_fixtures",
            live=False,
            username="",
        )
    if tomorrow_probe.get("ok"):
        raw_tomorrow = service._request(
            "fixtures",
            {"date": tomorrow_s},
            feature="api_fixtures",
            live=False,
            username="",
        )

    merged_raw = dedupe_fixtures(raw_live + raw_today + raw_tomorrow)
    report["filter_pipeline"] = diagnose_filter_pipeline(
        merged_raw, today_s=today_s, tomorrow_s=tomorrow_s
    )

    if payload:
        today_matches = collect_fixtures_for_filters(
            payload, time_filter="heute", region_filter="alle"
        )
        live_matches = collect_fixtures_for_filters(
            payload, time_filter="live", region_filter="alle"
        )
        tomorrow_matches = collect_fixtures_for_filters(
            payload, time_filter="morgen", region_filter="alle"
        )
    else:
        premium_live = filter_premium_fixtures(raw_live)
        premium_today = filter_premium_fixtures(raw_today)
        premium_tomorrow = filter_premium_fixtures(raw_tomorrow)
        today_matches = dedupe_fixtures(premium_live + premium_today)
        live_matches = premium_live
        tomorrow_matches = premium_tomorrow

    report["counts"] = {
        "today_matches": len(today_matches),
        "live_matches": len(live_matches),
        "tomorrow_matches": len(tomorrow_matches),
    }

    report["summary"] = {
        "api_works": any_ok,
        "data_present": any(
            report["counts"].get(k, 0) > 0
            for k in ("today_matches", "live_matches", "tomorrow_matches")
        )
        or report["filter_pipeline"].get("before_filter", 0) > 0,
        "filters_removed_data": (
            report["filter_pipeline"].get("before_filter", 0) > 0
            and report["filter_pipeline"].get("after_premium_filter", 0) == 0
        ),
        "rate_limit": report["rate_limit_hit"] or report["internal_rate_limit"],
        "failure_point": _failure_point(report),
    }

    return report


def _failure_point(report: dict[str, Any]) -> str:
    if report.get("internal_rate_limit"):
        return "Internes MaByte Rate-Limit (security.py, 60/min) — zu viele Requests pro Minute"
    if report.get("rate_limit_hit"):
        return "API-Football 429 oder Tageslimit — externer Rate Limit"
    probes = report.get("probes") or {}
    if not any(p.get("ok") for p in probes.values()):
        errs = report.get("errors") or []
        return errs[0] if errs else "Alle API-Probes fehlgeschlagen"
    fp = report.get("filter_pipeline") or {}
    if fp.get("before_filter", 0) > 0 and fp.get("after_premium_filter", 0) == 0:
        return "Premium-Liga-Filter entfernt alle Spiele (Liga-ID nicht in Whitelist)"
    counts = report.get("counts") or {}
    if all(counts.get(k, 0) == 0 for k in ("today_matches", "live_matches", "tomorrow_matches")):
        if fp.get("before_filter", 0) == 0:
            return "API liefert 0 Fixtures für heute/live/morgen (evtl. Spieltag leer)"
        return "Datums-/Filter-Logik in collect_fixtures_for_filters — 0 nach Filter"
    return "Kein Fehler erkannt — Daten sollten sichtbar sein"


def log_board_counts(counts: dict[str, int]) -> None:
    print(
        {
            "today_matches": counts.get("today_matches", 0),
            "live_matches": counts.get("live_matches", 0),
            "tomorrow_matches": counts.get("tomorrow_matches", 0),
        }
    )


def format_debug_widget(report: dict[str, Any]) -> str:
    counts = report.get("counts") or {}
    fp = report.get("filter_pipeline") or {}
    dates = report.get("dates") or {}
    summary = report.get("summary") or {}
    remaining = "—"
    for probe in (report.get("probes") or {}).values():
        if probe.get("rate_limit_remaining") is not None:
            remaining = str(probe.get("rate_limit_remaining"))

    lines = [
        "### Football Debug",
        f"- **Today Matches:** {counts.get('today_matches', 0)}",
        f"- **Live Matches:** {counts.get('live_matches', 0)}",
        f"- **Tomorrow Matches:** {counts.get('tomorrow_matches', 0)}",
        f"- **API Status:** {report.get('api_status', 'UNKNOWN')}",
        f"- **Rate Limit Remaining:** {remaining}",
        f"- **Datum (Europe/Berlin):** heute `{dates.get('today')}` · morgen `{dates.get('tomorrow')}`",
        "",
        "**Filter-Pipeline:**",
        f"- Vor Filter: {fp.get('before_filter', 0)}",
        f"- Nach Premium: {fp.get('after_premium_filter', 0)}",
        f"- Nach Deutschland: {fp.get('after_deutschland_filter', 0)}",
        f"- Nach UEFA: {fp.get('after_uefa_filter', 0)}",
        "",
        f"**Diagnose:** {summary.get('failure_point', '—')}",
    ]
    return "\n".join(lines)
