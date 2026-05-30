"""Football AI — Premium Intelligence Dashboard (Beta)."""
from __future__ import annotations

import streamlit as st

from config import football_plan_rank
from services.football_access import can_access_feature
from services.football_daily_tips import build_daily_betting_tips
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
    render_section_title,
    render_top_matches_row,
)
from ui.premium_foundation import render_upgrade_card

_FB_MC_DATA_VERSION = 8


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
        for legacy in ("fb_mc_view", "fb_mc_show_all_live", "fb_mc_filter_sig"):
            st.session_state.pop(legacy, None)


def _selected_fixture() -> int | None:
    selected = st.session_state.get("fb_mc_selected_fixture")
    try:
        return int(selected) if selected else None
    except (TypeError, ValueError):
        return None


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


def _render_live_section(payload: dict, *, selected: int | None) -> None:
    live_now = list(payload.get("live_now") or [])
    if live_now:
        render_match_grid(live_now, key_prefix="live", selected_fixture=selected, max_cards=8)
    elif payload.get("show_live_intl_prompt") or int(payload.get("raw_live_count") or 0):
        st.markdown(
            '<div class="fb-mc-empty-state"><strong>Heute keine Topspiele live.</strong>'
            "In Premium-Ligen läuft gerade nichts.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Alle Live-Spiele anzeigen", key="fb_mc_all_live", width="stretch"):
            st.session_state.fb_mc_include_all = True
            st.session_state.fb_mc_payload = None
            st.rerun()
    else:
        st.markdown(
            '<div class="fb-mc-empty-state"><strong>Heute keine Topspiele live.</strong>'
            "In Premium-Ligen läuft gerade nichts.</div>",
            unsafe_allow_html=True,
        )


def _render_top_section(payload: dict, *, selected: int | None) -> None:
    top_matches = list(payload.get("top_matches") or [])
    next_matches = list(payload.get("next_matches") or [])
    if top_matches:
        render_top_matches_row(top_matches, key_prefix="top", selected_fixture=selected)
    elif next_matches:
        st.markdown(
            '<div class="fb-mc-empty-state" style="margin-bottom:12px;">'
            "<strong>Heute keine Topspiele verfügbar.</strong> "
            "Nächste Premium-Partien in den kommenden 7 Tagen.</div>",
            unsafe_allow_html=True,
        )
        render_top_matches_row(next_matches, key_prefix="next", selected_fixture=selected)
    else:
        render_empty_top_matches(
            show_intl_hint=bool(payload.get("show_international_prompt")),
            raw_live=int(payload.get("raw_live_count") or 0),
        )
        if st.button("Alle Live-Spiele anzeigen", key="fb_mc_all_top", width="stretch"):
            st.session_state.fb_mc_include_all = True
            st.session_state.fb_mc_payload = None
            st.rerun()


def _render_tips_section(*, tip_pool: list, tips: list, rank: int, open_premium) -> None:
    if rank < 2:
        st.info("AI Tipps ab Football Pro.")
        if st.button("Upgrade", key="fb_mc_tip_up", width="stretch"):
            open_premium()
        return
    if tips:
        tip_cols = st.columns(min(len(tips), 3))
        for i, tip in enumerate(tips[:3]):
            with tip_cols[i]:
                render_dashboard_tip_mini(tip["intel"], fixture_id=int(tip["fixture_id"]))
    elif tip_pool:
        st.caption("Keine ausreichenden Prognose-Daten — nächste Spiele werden geladen.")
    else:
        st.caption("Tipps erscheinen, sobald Premium-Spiele verfügbar sind.")


def _render_analyse_section(
    *,
    service,
    selected: int | None,
    username: str,
    session_plan: str,
    rank: int,
    elite_ok: bool,
    pro_ok: bool,
    open_premium,
    top_matches: list,
    next_matches: list,
    live_now: list,
    all_premium: list,
) -> None:
    if not selected:
        st.info("Wähle ein Spiel unter Live Center oder Top Matches — dann „Analyse“.")
        pool = dedupe_fixtures_list(all_premium + next_matches + live_now + top_matches)
        if pool:
            opts = fixture_select_options(pool[:12])
            pick = st.selectbox("Spiel wählen", ["—"] + list(opts.keys()), key="fb_mc_analyse_pick")
            if pick != "—":
                st.session_state.fb_mc_selected_fixture = opts[pick]
                st.rerun()
        return

    cache_key = f"fb_mc_detail_{selected}"
    sig_d = f"{selected}|{session_plan}|v8"
    if st.session_state.get("fb_mc_detail_sig") != sig_d:
        st.session_state.fb_mc_detail_sig = sig_d
        st.session_state.pop(cache_key, None)

    if cache_key not in st.session_state:
        with st.spinner("Analysiere Spiel…"):
            st.session_state[cache_key] = fetch_match_detail(
                service, selected, username=username, session_plan=session_plan
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
        username=username,
        session_plan=session_plan,
    )


def render_tab_live_match_center(
    summary: dict,
    *,
    username: str,
    session_plan: str,
    open_premium,
    section: str | None = None,
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
        if st.button("Aktualisieren", type="primary", key=f"fb_mc_refresh_{section or 'all'}", width="stretch"):
            st.session_state.fb_mc_payload = None
            st.session_state.fb_mc_tips = None

    if st.session_state.fb_mc_payload is None:
        with st.spinner("Premium-Ligen laden…"):
            try:
                st.session_state.fb_mc_payload = fetch_premium_dashboard(
                    service, username=username, include_all_leagues=include_all
                )
            except FootballAPIError as exc:
                st.error(str(exc))
                return

    payload = st.session_state.fb_mc_payload or {}
    today_local = payload.get("today_local") or payload.get("today") or ""
    for err in payload.get("errors") or []:
        st.warning(err)

    top_matches = list(payload.get("top_matches") or [])
    next_matches = list(payload.get("next_matches") or [])
    live_now = list(payload.get("live_now") or [])
    all_premium = list(payload.get("all_premium") or [])
    extended = list(payload.get("extended") or [])
    selected = _selected_fixture()

    render_mc_header(
        live_count=len(live_now),
        today_count=len(all_premium) or len(next_matches),
        api_used=int(summary.get("api_used") or 0),
        api_limit=int(summary.get("api_limit") or 0),
    )
    cap = f"Premium-only · {today_local} · Europe/Berlin"
    if not all_premium and next_matches:
        cap += f" · {len(next_matches)} kommende Top-Spiele"
    st.caption(cap)

    tip_pool = all_premium or top_matches or next_matches
    tips_sig = f"{len(tip_pool)}|{session_plan}|{today_local}|v8"
    if st.session_state.get("fb_mc_tips_sig") != tips_sig:
        st.session_state.fb_mc_tips_sig = tips_sig
        st.session_state.fb_mc_tips = None
    if st.session_state.fb_mc_tips is None and tip_pool and rank >= 2:
        with st.spinner("AI-Tipps berechnen…"):
            st.session_state.fb_mc_tips = build_daily_betting_tips(
                service, tip_pool, username=username, session_plan=session_plan, limit=3
            )
    tips = st.session_state.get("fb_mc_tips") or []

    def _live() -> None:
        render_section_title("Live Now · Premium")
        _render_live_section(payload, selected=selected)
        if include_all and extended:
            st.caption(f"{len(extended)} weitere Live-/Liga-Spiele")
            render_match_grid(extended, key_prefix="ext_live", selected_fixture=selected, max_cards=12)

    def _top() -> None:
        render_section_title("Top Matches Today")
        _render_top_section(payload, selected=selected)
        if all_premium and len(all_premium) > len(top_matches or []):
            with st.expander(f"Alle Premium heute ({len(all_premium)})", expanded=False):
                render_match_grid(all_premium, key_prefix="all_prem", selected_fixture=selected, max_cards=24)

    def _tips() -> None:
        render_section_title("AI Betting Insights · Top 3")
        _render_tips_section(tip_pool=tip_pool, tips=tips, rank=rank, open_premium=open_premium)

    def _analyse() -> None:
        render_section_title("Match Intelligence")
        _render_analyse_section(
            service=service,
            selected=selected,
            username=username,
            session_plan=session_plan,
            rank=rank,
            elite_ok=elite_ok,
            pro_ok=pro_ok,
            open_premium=open_premium,
            top_matches=top_matches,
            next_matches=next_matches,
            live_now=live_now,
            all_premium=all_premium,
        )

    if section == "live":
        _live()
    elif section == "top":
        _top()
    elif section == "tips":
        _tips()
    elif section == "analyse":
        _analyse()
    else:
        t1, t2, t3, t4 = st.tabs(["Live Center", "Top Matches", "AI Tipps", "Match Analyse"])
        with t1:
            _live()
        with t2:
            _top()
        with t3:
            _tips()
        with t4:
            _analyse()

    if not include_all and (
        payload.get("show_international_prompt") or payload.get("show_live_intl_prompt")
    ):
        if st.button("Internationale Spiele anzeigen", key=f"fb_mc_intl_{section or 'all'}", width="stretch"):
            st.session_state.fb_mc_include_all = True
            st.session_state.fb_mc_payload = None
            st.rerun()
