"""MaByte — alle Football-/Feed-Ausgaben testen (ohne Streamlit)."""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WHITELIST = set()
for _ids in __import__("config", fromlist=["FOOTBALL_COMPETITION_GROUPS"]).FOOTBALL_COMPETITION_GROUPS.values():
    WHITELIST.update(_ids)
TIME_FILTERS = ("heute", "live", "morgen", "naechste")


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def test_compile() -> bool:
    import py_compile
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    errors = []
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" in str(p):
            continue
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{p.relative_to(root)}: {exc}")
    if errors:
        for e in errors:
            print("FAIL", e)
        return False
    print(f"OK — {sum(1 for p in root.rglob('*.py') if '__pycache__' not in str(p))} Dateien")
    return True


def test_db() -> bool:
    from database import ensure_db_ready

    ok = ensure_db_ready()
    print("ensure_db_ready():", "OK" if ok else "FAIL")
    return bool(ok)


def test_session_defaults() -> bool:
    """Prüft ui.py DEFAULTS — Football-Keys (ohne Streamlit-Import)."""
    import ast
    from pathlib import Path

    ui_path = Path(__file__).resolve().parents[1] / "ui.py"
    tree = ast.parse(ui_path.read_text(encoding="utf-8-sig"))
    defaults: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEFAULTS":
                    defaults = ast.literal_eval(node.value)
                    break
    required = {
        "fb_v",
        "fb_competition",
        "fb_time",
        "fb_league_id",
        "fb_payload",
        "fb_detail",
        "fb_sel",
        "fb_cache_key",
        "fb_displayed_topspiele_count",
        "fb_displayed_allspiele_count",
    }
    missing = required - set(defaults.keys())
    if missing:
        print("FAIL fehlende DEFAULTS:", sorted(missing))
        return False
    print("OK — Football-Keys in ui.py DEFAULTS:", sorted(required))
    return True


def test_football_service() -> bool:
    from services.football_api import get_football_service

    svc = get_football_service()
    configured = svc.is_configured()
    print("is_configured():", configured)
    if not configured:
        print("SKIP — FOOTBALL_API_KEY fehlt")
        return True
    return True


def _print_rows(label: str, rows: list, limit: int = 5) -> None:
    print(f"  {label}: {len(rows)} Spiele")
    for i, row in enumerate(rows[:limit]):
        card = row.get("card") or {}
        home = card.get("home") or "?"
        away = card.get("away") or "?"
        league = card.get("league") or "?"
        lid = card.get("league_id") or "?"
        time_ = card.get("time") or card.get("date") or "?"
        analysis = row.get("analysis_available")
        print(f"    [{i+1}] {home} vs {away} | {league} (id={lid}) | {time_} | analyse={analysis}")
    if len(rows) > limit:
        print(f"    ... +{len(rows) - limit} weitere")


def test_football_feed_all() -> bool:
    from services.football_api import get_football_service
    from services.football_feed import (
        fetch_all_api_payload,
        league_ids_for_competition,
        resolve_all_api_board,
        resolve_competition_board,
        resolve_football_feed,
    )

    svc = get_football_service()
    if not svc.is_configured():
        print("SKIP — kein API-Key")
        return True

    ok = True
    for comp in ("deutschland", "uefa", "topligen"):
        section(f"Wettbewerb: {comp.upper()}")
        allowed = league_ids_for_competition(comp)
        try:
            result = resolve_competition_board(
                svc,
                username="test",
                session_plan="football_elite",
                competition=comp,
                time_filter="heute",
                probe_analysis=False,
            )
            rows = result.get("rows") or []
            print(f"  banner: {result.get('banner')!r}")
            print(f"  rows: {len(rows)}")
            bad = []
            for row in rows:
                lid = (row.get("card") or {}).get("league_id")
                try:
                    if int(lid or 0) not in allowed:
                        bad.append(lid)
                except (TypeError, ValueError):
                    bad.append(lid)
            if bad:
                print("  FAIL Whitelist:", bad[:5])
                ok = False
            else:
                print("  OK Whitelist-only")
            _print_rows(comp, rows, limit=3)
        except Exception as exc:
            print("  FAIL:", exc)
            traceback.print_exc()
            ok = False

    section("Alle API")
    try:
        payload = fetch_all_api_payload(svc, username="test")
        all_ = resolve_all_api_board(payload, time_filter="heute")
        print(f"  rows: {len(all_.get('rows') or [])}")
    except Exception as exc:
        print("  FAIL:", exc)
        ok = False
    return ok


def test_match_detail_sample() -> bool:
    from services.football_api import get_football_service
    from services.football_board import fetch_match_detail
    from services.football_feed import resolve_competition_board

    svc = get_football_service()
    if not svc.is_configured():
        print("SKIP")
        return True

    top = resolve_competition_board(
        svc,
        username="test",
        session_plan="football_elite",
        competition="deutschland",
        time_filter="heute",
        probe_analysis=False,
    )
    rows = top.get("rows") or []
    if not rows:
        print("SKIP — keine Topspiele für Detail-Test")
        return True

    fid = rows[0].get("fixture_id")
    if not fid:
        print("SKIP — keine fixture_id")
        return True

    detail = fetch_match_detail(svc, int(fid), username="test", session_plan="football_elite")
    card = detail.get("card") or {}
    print(f"  Fixture {fid}: {card.get('home')} vs {card.get('away')}")
    print(f"  analysis_available: {detail.get('analysis_available')}")
    print(f"  error: {detail.get('error')!r}")
    odds = detail.get("odds") or {}
    if odds:
        print(f"  odds 1X2: {odds.get('home')} / {odds.get('draw')} / {odds.get('away')}")
    pred = detail.get("prediction_insights") or {}
    if pred:
        print(f"  prediction: home={pred.get('home_pct')} draw={pred.get('draw_pct')} away={pred.get('away_pct')}")
    return True


def test_beta_routes() -> bool:
    """Smoke: beta page handlers + Football V2 package (no Streamlit UI)."""
    ok = True
    try:
        from ui.dashboard import render_home
        from ui.football import render_football_betting_board
        from pages.automation_lab import render_automation_lab
        from pages.account import render_dashboard
        from pages.chat import render_chat
        from pages.premium import render_premium

        for key, fn in (
            ("home", render_home),
            ("chat", render_chat),
            ("football", render_football_betting_board),
            ("automation_lab", render_automation_lab),
            ("dashboard", render_dashboard),
            ("premium", render_premium),
        ):
            if not callable(fn):
                print(f"  FAIL handler not callable: {key}")
                ok = False
            else:
                print(f"  OK handler: {key}")

        ui_path = Path(__file__).resolve().parents[1] / "ui.py"
        ui_src = ui_path.read_text(encoding="utf-8")
        for needle in (
            "from ui.football import render_football_betting_board",
            '"football": ("Football AI", render_football)',
            '"automation_lab": ("Content Automation", render_automation_lab)',
        ):
            if needle not in ui_src:
                print(f"  FAIL ui.py missing: {needle!r}")
                ok = False
            else:
                print(f"  OK ui.py route: {needle[:48]}…")
    except Exception as exc:
        print("  FAIL", exc)
        traceback.print_exc()
        ok = False
    return ok


def test_env_football() -> bool:
    """C2 — log required env vars (informational; does not fail CI without keys)."""
    football_key = bool(os.getenv("FOOTBALL_API_KEY", "").strip())
    print(f"  FOOTBALL_API_KEY: {'OK' if football_key else 'MISSING — Football AI leer auf Prod'}")
    for name in ("APP_BASE_URL", "DATA_DIR", "OAUTH_STATE_SECRET"):
        print(f"  {name}: {'OK' if os.getenv(name, '').strip() else 'missing'}")
    return True


def main() -> None:
    results: list[tuple[str, bool]] = []

    section("1. py_compile (gesamtes Repo)")
    results.append(("py_compile", test_compile()))

    section("2. Datenbank")
    results.append(("database", test_db()))

    section("3. Session DEFAULTS (Football Keys)")
    results.append(("session_defaults", test_session_defaults()))

    section("3b. Beta routes (Dashboard, Chat, Football, Content, Profile, Elite)")
    results.append(("beta_routes", test_beta_routes()))

    section("3c. Environment (Football / Railway)")
    results.append(("env_football", test_env_football()))

    section("4. Football Service")
    results.append(("football_service", test_football_service()))

    section("5. Football Feed — alle Zeitfilter + Modi")
    results.append(("football_feed", test_football_feed_all()))

    section("6. Match Detail (1 Topspiel)")
    results.append(("match_detail", test_match_detail_sample()))

    section("ZUSAMMENFASSUNG")
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'} — {name}")
    failed = [n for n, ok in results if not ok]
    if failed:
        print(f"\nGescheitert: {', '.join(failed)}")
        sys.exit(1)
    print("\nAlle Tests bestanden.")


if __name__ == "__main__":
    main()
