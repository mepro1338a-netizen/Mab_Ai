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
    render_match_grid,
    render_mc_header,
    render_section_title,
    render_top_matches_row,
)
from ui.premium_foundation import render_upgrade_card

_FB_MC_DATA_VERSION = 10


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


def _has_live_content(payload: dict, *, include_all: bool) -> bool:
    return bool(list(payload.get("live_now") or []))


def _render_live_section(payload: dict, *, selected: int | None, include_all: bool) -> None:
    live_now = list(payload.get("live_now") or [])
    enriched = list(payload.get("live_now_cards") or [])
    if not live_now:
        return
    render_match_grid(
        live_now,
        key_prefix="live",
        selected_fixture=selected,
        max_cards=8,
        enriched_cards=enriched,
    )


def _has_top_content(payload: dict) -> bool:
    return bool(
        payload.get("top_matches")
        or payload.get("next_matches")
        or payload.get("all_premium")
    )


def _render_top_section(payload: dict, *, selected: int | None) -> None:
    top_matches = list(payload.get("top_matches") or [])
    next_matches = list(payload.get("next_matches") or [])
    all_premium = list(payload.get("all_premium") or [])
    if top_matches:
        render_top_matches_row(top_matches, key_prefix="top", selected_fixture=selected)
    elif next_matches:
        render_top_matches_row(next_matches, key_prefix="next", selected_fixture=selected)
    elif all_premium:
        render_match_grid(all_premium[:8], key_prefix="prem_fallback", selected_fixture=selected, max_cards=8)


def _has_tips_content(*, tips: list, rank: int) -> bool:
    return rank < 2 or bool(tips)


def _render_tips_section(*, tips: list, rank: int, open_premium) -> None:
    if rank < 2:
        st.info("AI Tipps ab Football Pro.")
        if st.button("Upgrade", key="fb_mc_tip_up", width="stretch"):
            open_premium()
        return
    tip_cols = st.columns(min(len(tips), 3))
    for i, tip in enumerate(tips[:3]):
        with tip_cols[i]:
            render_dashboard_tip_mini(tip["intel"], fixture_id=int(tip["fixture_id"]))


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
        pool = dedupe_fixtures_list(all_premium + next_matches + live_now + top_matches)
        if pool:
            opts = fixture_select_options(pool[:12])
            pick = st.selectbox("Spiel wählen", ["—"] + list(opts.keys()), key="fb_mc_analyse_pick")
            if pick != "—":
                st.session_state.fb_mc_selected_fixture = opts[pick]
                st.rerun()
        return

    cache_key = f"fb_mc_detail_{selected}"
    sig_d = f"{selected}|{session_plan}|v10"
    if st.session_state.get("fb_mc_detail_sig") != sig_d:
        st.session_state.fb_mc_detail_sig = sig_d
        st.session_state.pop(cache_key, None)

    if cache_key not in st.session_state:
        with st.spinner("Analysiere Spiel…"):
            st.session_state[cache_key] = fetch_match_detail(
                service, selected, username=username, session_plan=session_plan
            )

    detail = st.session_state.get(cache_key)
    if not detail:
        return
    if detail.get("error"):
        st.error(str(detail["error"]))
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
        st.error("FOOTBALL_API_KEY fehlt — Konfiguration in .env erforderlich.")
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

    if section:
        st.markdown(
            f'<p class="fb-mc-section" style="margin-top:0;">Fußball-Intelligence · '
            f"Live {len(live_now)} · Premium {len(all_premium) or len(next_matches)} · "
            f"API {int(summary.get('api_used') or 0):,}/{int(summary.get('api_limit') or 0):,}</p>".replace(
                ",", "."
            ),
            unsafe_allow_html=True,
        )
    else:
        render_mc_header(
            live_count=len(live_now),
            today_count=len(all_premium) or len(next_matches),
            api_used=int(summary.get("api_used") or 0),
            api_limit=int(summary.get("api_limit") or 0),
        )
    cap = f"Nur Premium-Ligen · {today_local} · Europe/Berlin"
    if not all_premium and next_matches:
        cap += f" · {len(next_matches)} kommende Top-Spiele"
    st.caption(cap)

    tip_pool = all_premium or top_matches or next_matches
    tips_sig = f"{len(tip_pool)}|{session_plan}|{today_local}|v10"
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
        if not _has_live_content(payload, include_all=include_all):
            return
        render_section_title("Live jetzt · Premium")
        _render_live_section(payload, selected=selected, include_all=include_all)

    def _top() -> None:
        if not _has_top_content(payload):
            return
        render_section_title("Top-Spiele heute")
        _render_top_section(payload, selected=selected)
        if all_premium and len(all_premium) > len(top_matches or []):
            with st.expander(f"Alle Premium heute ({len(all_premium)})", expanded=False):
                render_match_grid(all_premium, key_prefix="all_prem", selected_fixture=selected, max_cards=24)

    def _tips() -> None:
        if not _has_tips_content(tips=tips, rank=rank):
            return
        render_section_title("KI-Wett-Tipps · Top 3")
        _render_tips_section(tips=tips, rank=rank, open_premium=open_premium)

    def _analyse() -> None:
        render_section_title("Spielanalyse")
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
        tabs: list[str] = []
        if _has_live_content(payload, include_all=include_all):
            tabs.append("Live-Zentrale")
        if _has_top_content(payload):
            tabs.append("Top-Spiele")
        if _has_tips_content(tips=tips, rank=rank):
            tabs.append("KI-Tipps")
        tabs.append("Spielanalyse")
        if len(tabs) == 1:
            _analyse()
        else:
            widgets = st.tabs(tabs)
            for idx, label in enumerate(tabs):
                with widgets[idx]:
                    if label == "Live-Zentrale":
                        _live()
                    elif label == "Top-Spiele":
                        _top()
                    elif label == "KI-Tipps":
                        _tips()
                    else:
                        _analyse()
