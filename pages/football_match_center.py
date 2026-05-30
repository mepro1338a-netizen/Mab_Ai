"""Football AI — Premium-first Intelligence Dashboard."""

from __future__ import annotations

import streamlit as st

from config import football_plan_rank
from services.football_access import (
    FootballAccessError,
    can_access_feature,
    can_run_action,
    consume_action,
)
from services.football_daily_tips import build_daily_betting_tips
from services.football_elite_live import EliteLiveIntelEngine
from services.football_match_center import fetch_match_detail, fetch_premium_dashboard
from services.football_service import FootballAPIError, get_football_service
from ui.football_betting_card import render_match_intelligence_section
from ui.football_components import inject_football_components_css
from ui.football_match_center import (
    fixture_select_options,
    inject_match_center_css,
    render_dashboard_tip_mini,
    render_empty_top_matches,
    render_match_grid,
    render_mc_header,
    render_premium_live_empty,
    render_section_title,
    render_top_matches_row,
)
from ui.premium_foundation import render_upgrade_card

_FB_MC_DATA_VERSION = 5


def _init_session() -> None:
    defaults = {
        "fb_mc_payload": None,
        "fb_mc_include_all": False,
        "fb_mc_selected_fixture": None,
        "fb_mc_tips": None,
        "fb_mc_tips_sig": "",
        "fb_mc_data_version": _FB_MC_DATA_VERSION,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if st.session_state.get("fb_mc_data_version") != _FB_MC_DATA_VERSION:
        st.session_state.fb_mc_data_version = _FB_MC_DATA_VERSION
        st.session_state.fb_mc_payload = None
        st.session_state.fb_mc_tips = None
        st.session_state.fb_mc_include_all = False
        # Legacy keys
        for legacy in ("fb_mc_view", "fb_mc_show_all_live", "fb_mc_filter_sig"):
            st.session_state.pop(legacy, None)


def render_tab_live_match_center(
    summary: dict,
    *,
    username: str,
    session_plan: str,
    open_premium,
) -> None:
    _init_session()
    inject_match_center_css()
    inject_football_components_css()

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        render_upgrade_card(
            "Football AI Intelligence",
            "Premium Match Center ab Football Starter.",
            "football_starter",
            button_key="fb_mc_starter_up",
            on_upgrade=open_premium,
        )
        return

    service = get_football_service()
    if not service.is_configured():
        st.markdown(
            '<div class="fb-empty">FOOTBALL_API_KEY fehlt — API wird angebunden.</div>',
            unsafe_allow_html=True,
        )
        return

    elite_ok, _, _ = can_access_feature(username, "ai_elite_live_intelligence", session_plan)
    pro_ok, _, _ = can_access_feature(username, "ai_live_match_intelligence", session_plan)
    include_all = bool(st.session_state.fb_mc_include_all)

    with st.columns([4, 1])[1]:
        if st.button("Aktualisieren", type="primary", key="fb_mc_refresh", width="stretch"):
            st.session_state.fb_mc_payload = None
            st.session_state.fb_mc_tips = None

    if st.session_state.fb_mc_payload is None:
        with st.spinner("Premium-Ligen laden…"):
            try:
                st.session_state.fb_mc_payload = fetch_premium_dashboard(
                    service,
                    username=username,
                    include_all_leagues=include_all,
                )
            except FootballAPIError as exc:
                st.error(str(exc))
                return

    payload = st.session_state.fb_mc_payload or {}
    today_local = payload.get("today_local") or payload.get("today") or ""
    for err in payload.get("errors") or []:
        st.warning(err)

    top_matches = list(payload.get("top_matches") or [])
    live_now = list(payload.get("live_now") or [])
    all_premium = list(payload.get("all_premium") or [])
    extended = list(payload.get("extended") or [])

    render_mc_header(
        live_count=len(live_now),
        today_count=len(all_premium),
        api_used=int(summary.get("api_used") or 0),
        api_limit=int(summary.get("api_limit") or 0),
    )
    st.caption(f"Premium-only · {today_local} · Europe/Berlin")

    selected = st.session_state.get("fb_mc_selected_fixture")
    try:
        selected = int(selected) if selected else None
    except (TypeError, ValueError):
        selected = None

    # —— Sektion 1: Top Matches Today ——
    render_section_title("Top Matches Today")
    if top_matches:
        render_top_matches_row(
            top_matches,
            key_prefix="top",
            selected_fixture=selected,
        )
    else:
        render_empty_top_matches(
            show_intl_hint=bool(payload.get("show_international_prompt")),
            raw_live=int(payload.get("raw_live_count") or 0),
        )
        if st.button(
            "Internationale Spiele anzeigen",
            key="fb_mc_intl_empty",
            width="stretch",
        ):
            st.session_state.fb_mc_include_all = True
            st.session_state.fb_mc_payload = None
            st.rerun()

    # —— Sektion 2: Live Now ——
    render_section_title("Live Now · Premium")
    if live_now:
        render_match_grid(
            live_now,
            key_prefix="live",
            selected_fixture=selected,
            max_cards=12,
        )
    else:
        raw = int(payload.get("raw_live_count") or 0)
        if raw:
            render_premium_live_empty(raw_live_count=raw)
        else:
            st.markdown(
                '<div class="fb-mc-empty-state"><strong>Keine Live-Spiele</strong>'
                "In Premium-Ligen läuft gerade nichts.</div>",
                unsafe_allow_html=True,
            )

    # —— Sektion 3: AI Betting Insights ——
    render_section_title("AI Betting Insights · Top 3")
    tip_pool = all_premium or top_matches
    tips_sig = f"{len(tip_pool)}|{session_plan}|{today_local}|v5"
    if st.session_state.get("fb_mc_tips_sig") != tips_sig:
        st.session_state.fb_mc_tips_sig = tips_sig
        st.session_state.fb_mc_tips = None

    if st.session_state.fb_mc_tips is None and tip_pool and rank >= 2:
        with st.spinner("AI-Tipps berechnen…"):
            st.session_state.fb_mc_tips = build_daily_betting_tips(
                service,
                tip_pool,
                username=username,
                session_plan=session_plan,
                limit=3,
            )

    tips = st.session_state.get("fb_mc_tips") or []
    if rank < 2:
        st.info("AI Betting Insights ab Football Pro.")
        if st.button("Upgrade", key="fb_mc_tip_up", width="stretch"):
            open_premium()
    elif tips:
        tip_cols = st.columns(min(len(tips), 3))
        for i, tip in enumerate(tips[:3]):
            with tip_cols[i]:
                render_dashboard_tip_mini(tip["intel"], fixture_id=int(tip["fixture_id"]))
    elif tip_pool:
        st.caption("Keine ausreichenden Prognose-Daten für Tipps heute.")
    else:
        st.caption("Tipps erscheinen, sobald Premium-Spiele verfügbar sind.")

    # —— Sektion 4: Alle Spiele ——
    st.divider()
    render_section_title("Alle Spiele")
    with st.expander("Premium-Übersicht & weitere Ligen", expanded=include_all):
        if all_premium:
            st.caption(f"{len(all_premium)} Premium-Partien heute")
            render_match_grid(
                all_premium,
                key_prefix="all_prem",
                selected_fixture=selected,
                max_cards=36,
            )
        else:
            st.caption("Keine Premium-Partien geladen.")

        if not include_all:
            if st.button(
                "Internationale & kleine Ligen laden",
                key="fb_mc_load_all",
                width="stretch",
            ):
                st.session_state.fb_mc_include_all = True
                st.session_state.fb_mc_payload = None
                st.rerun()
        elif extended:
            st.caption(f"{len(extended)} weitere Ligen (nicht Premium)")
            render_match_grid(
                extended,
                key_prefix="ext",
                selected_fixture=selected,
                max_cards=48,
            )
        elif include_all:
            st.caption("Keine weiteren Ligen für heute in der API.")

    # —— Match Detail / Elite Card ——
    if not selected:
        return

    st.divider()
    st.markdown("### Match Intelligence")
    detail_fixtures = all_premium + extended + live_now
    opts = fixture_select_options(dedupe_fixtures_list(detail_fixtures))
    if selected not in opts.values():
        opts = fixture_select_options(dedupe_fixtures_list(top_matches + live_now))

    cache_key = f"fb_mc_detail_{selected}"
    sig_d = f"{selected}|{session_plan}|v5"
    if st.session_state.get("fb_mc_detail_sig") != sig_d:
        st.session_state.fb_mc_detail_sig = sig_d
        st.session_state.pop(cache_key, None)

    if cache_key not in st.session_state:
        with st.spinner("Analysiere Spiel…"):
            st.session_state[cache_key] = fetch_match_detail(
                service,
                selected,
                username=username,
                session_plan=session_plan,
            )

    detail = st.session_state.get(cache_key)
    if not detail or detail.get("error"):
        st.error(detail.get("error", "Analyse nicht verfügbar.") if detail else "Keine Daten.")
        return

    render_match_intelligence_section(
        detail,
        fixture_id=selected,
        rank=rank,
        elite_ok=elite_ok,
        pro_ok=pro_ok,
        open_premium=open_premium,
    )

    if elite_ok and st.session_state.get(f"fb_bet_details_{selected}"):
        with st.expander("Live Momentum (Elite)", expanded=False):
            if st.button("Live-Daten nachladen", key=f"fb_mc_elite_load_{selected}"):
                ok_run, msg = can_run_action(username, "deep_match_analysis", session_plan)
                if not ok_run:
                    st.error(msg)
                else:
                    try:
                        consume_action(username, "deep_match_analysis", session_plan)
                        bundle = EliteLiveIntelEngine(service).fetch_bundle(
                            selected, username=username
                        )
                        st.session_state[f"fb_mc_elite_{selected}"] = bundle
                        st.rerun()
                    except (FootballAccessError, FootballAPIError) as exc:
                        st.error(str(exc))
            bundle = st.session_state.get(f"fb_mc_elite_{selected}")
            if bundle:
                from services.football_elite_betting_card import build_betting_intelligence_card
                from ui.football_betting_card import render_elite_betting_card

                intel = build_betting_intelligence_card(detail, bundle=bundle)
                render_elite_betting_card(intel, fixture_id=selected, show_details=True)


def dedupe_fixtures_list(fixtures: list) -> list:
    seen: set[int] = set()
    out: list = []
    for fx in fixtures or []:
        fid = (fx.get("fixture") or {}).get("id")
        if not fid:
            continue
        try:
            key = int(fid)
        except (TypeError, ValueError):
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(fx)
    return out
