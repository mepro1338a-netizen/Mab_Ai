"""
Football Intelligence Hub — premium tabs (betting, preview, viral, automation, live intel).
"""
from __future__ import annotations

import streamlit as st

from services.football_access import (
    FootballAccessError,
    can_access_feature,
    can_run_action,
    consume_action,
)
from services.football_automation_hub import (
    WORKFLOW_CARDS,
    enqueue_workflow,
    generate_matchday_report_auto,
    load_jobs,
)
from services.football_betting_intel import full_betting_analysis
from services.football_live_intel import (
    build_live_alerts,
    live_fixture_snapshot,
    parse_fixture_statistics,
)
from services.football_match_preview import generate_match_preview
from services.football_odds import fixture_options_from_list, parse_fixture_odds_payload, parse_prediction_insights
from services.football_service import FootballAPIError, get_football_service
from services.football_viral_studio import generate_viral_reel_package
from ui.football_premium import (
    render_automation_dashboard,
    render_betting_intel_dashboard,
    render_live_intel_panel,
    render_pulse_live,
    render_viral_export_bar,
)
from ui.football_ui import render_fixture_cards, render_prediction_card, render_saas_legal, render_section_header
from ui.premium_foundation import render_upgrade_card
from ui.prompt_ui import prompt_text_input


def _fixture_pick_options() -> dict[str, int]:
    combined = []
    for key in (
        "football_upcoming_fixtures",
        "football_league_upcoming",
        "football_live_fixtures",
        "football_recent_fixtures",
    ):
        combined.extend(st.session_state.get(key) or [])
    return fixture_options_from_list(combined)


def render_tab_live_intel(summary: dict, *, username: str, session_plan: str, open_premium) -> None:
    render_section_header(
        "Live Match Intelligence",
        "Momentum, gefährliche Angriffe, Upset- & Value-Alerts in Echtzeit.",
    )
    ok, _, need = can_access_feature(username, "ai_live_match_intelligence", session_plan)
    if not ok:
        render_upgrade_card(
            "Live Intelligence",
            "Live Momentum & AI Alerts ab Football Pro.",
            need,
            button_key="fb_live_intel_up",
            on_upgrade=open_premium,
        )
        return

    service = get_football_service()
    render_pulse_live("LIVE FEED")
    if st.button("Live aktualisieren", key="fb_intel_refresh", width="stretch"):
        if not service.is_configured():
            st.error("API nicht konfiguriert.")
        else:
            try:
                st.session_state.football_live_fixtures = service.get_live_fixtures(username=username)
            except FootballAPIError as exc:
                st.error(str(exc))

    live_rows = st.session_state.get("football_live_fixtures") or []
    render_fixture_cards(live_rows, empty_msg="Keine Live-Spiele — Aktualisieren.")

    fx_opts = _fixture_pick_options()
    fixture_id = None
    if fx_opts:
        pick = st.selectbox("Spiel für Deep Intel", ["—"] + list(fx_opts.keys()), key="fb_intel_fx")
        if pick != "—":
            fixture_id = fx_opts[pick]

    momentum = {"label": "Ausgeglichen", "leader": "—", "score": 0}
    alerts = build_live_alerts(live_rows)

    if fixture_id and service.is_configured():
        if st.button("Statistik & Momentum laden", key="fb_intel_stats"):
            try:
                stats = service.get_fixture_statistics(fixture_id, username=username)
                parsed = parse_fixture_statistics(stats)
                momentum = parsed.get("momentum") or momentum
                st.session_state.fb_intel_momentum = momentum
                st.session_state.fb_intel_stats = parsed
            except FootballAPIError as exc:
                st.error(str(exc))

    momentum = st.session_state.get("fb_intel_momentum") or momentum
    if summary.get("tier", 0) >= 3:
        markets = st.session_state.get("fb_odds_markets") or []
        alerts = build_live_alerts(live_rows, value_markets=markets[:5])

    render_live_intel_panel(momentum, alerts)


def render_tab_betting_ai(summary: dict, *, username: str, session_plan: str, open_premium) -> None:
    render_section_header(
        "AI Betting Intelligence",
        "Implizite Wahrscheinlichkeit, EV, Value Detection & Bookmaker-Vergleich.",
    )
    ok, _, need = can_access_feature(username, "ai_betting_intelligence", session_plan)
    if not ok:
        render_upgrade_card(
            "Betting Intelligence",
            "Mathematische Value-Analyse ab Football Pro.",
            need,
            button_key="fb_bet_up",
            on_upgrade=open_premium,
        )
        return

    render_saas_legal(
        "Nur Bildungs- & Analysezweck — keine Wettberatung, kein Echtgeld."
    )
    service = get_football_service()
    fx_opts = _fixture_pick_options()
    fixture_id = None
    if fx_opts:
        pick = st.selectbox("Spiel", ["—"] + list(fx_opts.keys()), key="fb_bet_fx")
        if pick != "—":
            fixture_id = fx_opts[pick]

    elite = summary.get("tier", 0) >= 3
    if elite and fixture_id and st.button("Marktdaten laden", key="fb_bet_load"):
        try:
            st.session_state.fb_odds_markets = parse_fixture_odds_payload(
                service.get_fixture_odds(fixture_id, username=username)
            )
            preds = service.get_fixture_predictions(fixture_id, username=username)
            if preds:
                st.session_state.fb_odds_prediction = parse_prediction_insights(preds[0])
        except FootballAPIError as exc:
            st.error(str(exc))

    if st.session_state.get("fb_odds_prediction"):
        render_prediction_card(st.session_state.fb_odds_prediction)
        ins = st.session_state.fb_odds_prediction
        if ins.get("home_pct") is not None:
            st.session_state.fb_odds_suggest_prob = float(ins["home_pct"])

    c1, c2, c3 = st.columns(3)
    with c1:
        odds = st.number_input("Quote", min_value=1.01, value=float(st.session_state.get("fb_odds_prefill", 2.1)), step=0.01)
    with c2:
        stake = st.number_input("Einsatz", min_value=0.0, value=10.0)
    with c3:
        prob = st.number_input(
            "Gewinn-Wahrscheinlichkeit %",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.get("fb_odds_suggest_prob", 52.0)),
        )
    note = prompt_text_input(placeholder="Match-Notiz…", key="fb_bet_note")

    if st.button("AI Analyse starten", type="primary", key="fb_bet_run"):
        markets = st.session_state.get("fb_odds_markets") or []
        analysis = full_betting_analysis(odds, stake, prob, markets=markets if elite else None)
        st.session_state.fb_betting_analysis = analysis
        st.session_state.fb_odds_result = analysis

    if st.session_state.get("fb_betting_analysis"):
        render_betting_intel_dashboard(st.session_state.fb_betting_analysis)
        if note:
            st.caption(f"Notiz: {note}")


def render_tab_match_preview(summary: dict, *, username: str, session_plan: str, open_premium) -> None:
    render_section_header("AI Match Preview", "Narrative, Taktik, Form, O/U & BTTS — für Creator & Analysten.")
    ok, _, need = can_access_feature(username, "ai_match_preview", session_plan)
    if not ok:
        render_upgrade_card("Match Preview", "Ab Football Pro.", need, button_key="fb_prev_up", on_upgrade=open_premium)
        return

    c1, c2 = st.columns(2)
    with c1:
        club = st.text_input("Heim", key="fb_prev_home", placeholder="Bayern")
    with c2:
        opp = st.text_input("Auswärts", key="fb_prev_away", placeholder="Dortmund")

    ins = st.session_state.get("fb_odds_prediction") or {}
    ctx = {
        "platform": st.selectbox("Fokus", ["Multi", "TikTok", "Reels", "Analyse"], key="fb_prev_plat"),
        "form_home": ins.get("form_home", ""),
        "form_away": ins.get("form_away", ""),
        "home_pct": ins.get("home_pct"),
        "draw_pct": ins.get("draw_pct"),
        "away_pct": ins.get("away_pct"),
        "api_advice": ins.get("advice", ""),
    }

    if st.button("Preview generieren", type="primary", key="fb_prev_gen"):
        if not club or not opp:
            st.warning("Beide Teams eingeben.")
            return
        ok_run, msg = can_run_action(username, "matchday_package", session_plan)
        if not ok_run:
            st.error(msg)
            return
        try:
            consume_action(username, "matchday_package", session_plan)
        except FootballAccessError as exc:
            st.error(str(exc))
            return
        with st.spinner("AI Match Preview…"):
            text, src = generate_match_preview(club, opp, context=ctx)
        st.session_state.fb_match_preview = text
        if src == "fallback":
            st.info("Offline-Vorschau — OpenAI nicht verfügbar.")

    if st.session_state.get("fb_match_preview"):
        st.markdown(st.session_state.fb_match_preview)
        st.download_button(
            "↓ Preview",
            data=st.session_state.fb_match_preview.encode("utf-8"),
            file_name="match_preview.md",
            mime="text/markdown",
            key="fb_prev_dl",
        )


def render_tab_viral_studio(summary: dict, *, username: str, session_plan: str, open_premium) -> None:
    render_section_header("Viral Reel Generator", "Hooks, Captions, Voiceover, Thumbnail — Export zu Reels Studio.")
    ok, _, need = can_access_feature(username, "ai_viral_reel_generator", session_plan)
    if not ok:
        render_upgrade_card("Viral Generator", "Ab Football Pro.", need, button_key="fb_vir_up", on_upgrade=open_premium)
        return

    c1, c2 = st.columns(2)
    with c1:
        club = st.text_input("Club", key="fb_vir_club")
    with c2:
        opp = st.text_input("Gegner", key="fb_vir_opp")
    platform = st.selectbox("Plattform", ["TikTok", "Instagram Reels", "YouTube Shorts"], key="fb_vir_plat")
    tone = st.selectbox("Ton", ["Viral", "Hype", "Funny", "Emotional"], key="fb_vir_tone")

    if st.button("Viral Paket erstellen", type="primary", key="fb_vir_gen"):
        if not club or not opp:
            st.warning("Club & Gegner eingeben.")
            return
        ok_run, msg = can_run_action(username, "reel_script", session_plan)
        if not ok_run:
            st.error(msg)
            return
        try:
            consume_action(username, "reel_script", session_plan)
        except FootballAccessError as exc:
            st.error(str(exc))
            return
        with st.spinner("Viral Engine…"):
            pkg, src = generate_viral_reel_package(club, opp, platform=platform, tone=tone)
        st.session_state.fb_viral_package = pkg
        if src == "fallback":
            st.info("Demo-Paket — API offline.")

    if st.session_state.get("fb_viral_package"):
        st.markdown(st.session_state.fb_viral_package)
        render_viral_export_bar(club or "club", opp or "opp", st.session_state.fb_viral_package)


def render_tab_automation(summary: dict, *, username: str, session_plan: str, open_premium) -> None:
    render_section_header("Elite Automation", "Matchday Reports, Auto-Reels, Scheduled Posting.")
    ok, _, need = can_access_feature(username, "automation_triggers", session_plan)
    if not ok:
        render_upgrade_card("Automation Hub", "Ab Football Elite.", need, button_key="fb_auto_up", on_upgrade=open_premium)
        return

    jobs = load_jobs(username)
    render_automation_dashboard(WORKFLOW_CARDS, jobs)

    league = st.text_input("Liga / Matchday", value="Bundesliga", key="fb_auto_league")
    matches = st.text_area("Spiele (Liste)", key="fb_auto_matches", height=80)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Matchday Report", key="fb_auto_report"):
            with st.spinner("Report…"):
                report, _ = generate_matchday_report_auto(league, matches)
            st.session_state.fb_auto_report = report
            enqueue_workflow(username, "matchday_report", title=f"Report {league}")
    with c2:
        if st.button("Reel Queue", key="fb_auto_reel"):
            enqueue_workflow(username, "auto_reel", title=f"Reels {league}", payload={"matches": matches[:500]})
            st.success("In Queue.")
    with c3:
        if st.button("Social Schedule", key="fb_auto_social"):
            enqueue_workflow(username, "scheduled_social", title="Social Queue", schedule="daily")
            st.success("Schedule vorbereitet.")

    if st.session_state.get("fb_auto_report"):
        st.markdown(st.session_state.fb_auto_report)

    st.caption("Multi-Agent Pipeline: Preview → Viral → Publish (Architektur bereit).")
