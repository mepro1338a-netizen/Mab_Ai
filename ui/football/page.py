"""Football AI V2 — main page orchestrator."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_api import FootballAPIError, get_football_service
from services.football_feed import fetch_match_detail, resolve_competition_board
from ui.football.analysis import render_analysis
from ui.football.cards import filter_rows_by_league, match_card_html
from ui.football.constants import LEAGUE_NAV, MSG_EMPTY_TODAY, MSG_NEXT_SECTION, TIME_NAV, TOP_NAV
from ui.football.session import ensure_football_session
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css
from ui.football.styles import FOOTBALL_CSS


def _inject_css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1100, 20, 32) + FOOTBALL_CSS)


def _clear_feed() -> None:
    st.session_state["fb_payload"] = None
    st.session_state["fb_detail"] = None
    st.session_state["fb_sel"] = None


def _filter_section(
    title: str,
    items: list[tuple[Any, str]],
    *,
    session_key: str,
    key_prefix: str,
    value_cast: type | None = None,
) -> None:
    st.markdown(f'<p class="fb2-sec">{html.escape(title)}</p>', unsafe_allow_html=True)
    st.markdown('<div class="fb2-chip-row">', unsafe_allow_html=True)
    current = st.session_state.get(session_key)
    cols = st.columns(len(items))
    for col, (value, label) in zip(cols, items):
        with col:
            if value_cast is int:
                is_on = int(current or 0) == int(value)
            else:
                is_on = str(current) == str(value)
            if st.button(
                label,
                key=f"{key_prefix}_{value}",
                type="primary" if is_on else "tertiary",
            ):
                if not is_on:
                    st.session_state[session_key] = int(value) if value_cast is int else value
                    _clear_feed()
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _league_section_label(competition: str) -> str:
    return "Turniere" if competition == "nationalteams" else "Ligen"


def _render_filters(competition: str) -> None:
    st.markdown('<div class="fb2-filters">', unsafe_allow_html=True)
    st.markdown('<div class="fb2-filters-head">', unsafe_allow_html=True)
    _, refresh_col = st.columns([11, 1])
    with refresh_col:
        if st.button(
            "",
            key="fb2_refresh",
            icon=":material/refresh:",
            type="tertiary",
            help="Spiele neu laden",
        ):
            _clear_feed()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    _filter_section(
        "Wettbewerb",
        list(TOP_NAV),
        session_key="fb_competition",
        key_prefix="fb2_top",
    )
    _filter_section(
        "Zeitraum",
        list(TIME_NAV),
        session_key="fb_time",
        key_prefix="fb2_time",
    )
    leagues = LEAGUE_NAV.get(competition, [(0, "Alle")])
    _filter_section(
        _league_section_label(competition),
        [(lid, lbl) for lid, lbl in leagues],
        session_key="fb_league_id",
        key_prefix=f"fb2_lg_{competition}",
        value_cast=int,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_football_betting_board(
    *,
    username: str,
    session_plan: str,
    open_premium,
) -> None:
    _ = open_premium
    _inject_css()
    ensure_football_session()

    st.markdown('<div class="fb2">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="fb2-hero">
  <h1>Football Intelligence</h1>
  <p>Live-Spiele, Quoten und AI-Analyse — nur echte API-Daten.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        st.markdown(
            '<div class="fb2-gate">Football Intelligence ist mit deinem Plan noch nicht aktiv. '
            "Upgrade unter Premium.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    service = get_football_service()
    if not service.is_configured():
        st.markdown(
            '<div class="fb2-gate">Football Intelligence benötigt <strong>FOOTBALL_API_KEY</strong> '
            "in der Server-Umgebung (Railway Variables oder lokale .env). "
            "Ohne Key werden keine Spiele geladen.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    sel = st.session_state.get("fb_sel")

    if sel:
        if st.button("← Zurück zur Spielübersicht", key="fb2_back", type="secondary"):
            st.session_state["fb_sel"] = None
            st.session_state["fb_detail"] = None
            st.rerun()

        ck = f"{sel}|{session_plan}"
        detail = st.session_state.get("fb_detail")
        if not isinstance(detail, dict) or detail.get("_ck") != ck:
            with st.spinner("Analyse wird geladen…"):
                try:
                    detail = fetch_match_detail(
                        service, int(sel), username=username, session_plan=session_plan
                    )
                    detail["_ck"] = ck
                    st.session_state["fb_detail"] = detail
                except FootballAPIError as exc:
                    st.error(str(exc))
                    detail = {"analysis_available": False, "card": {}}
        if isinstance(detail, dict):
            if detail.get("error"):
                st.error(str(detail.get("error")))
            else:
                render_analysis(detail)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    comp = str(st.session_state.get("fb_competition") or "deutschland")
    _render_filters(comp)

    time_f = str(st.session_state.get("fb_time") or "heute")
    league_id = int(st.session_state.get("fb_league_id") or 0)

    cache_key = f"{comp}|{time_f}|{league_id}"
    if st.session_state.get("fb_cache_key") != cache_key:
        st.session_state["fb_payload"] = None
        st.session_state["fb_cache_key"] = cache_key

    with st.spinner("Spiele laden…"):
        try:
            result = resolve_competition_board(
                service,
                username=username,
                session_plan=session_plan,
                competition=comp,
                time_filter=time_f,
                probe_analysis=True,
            )
        except FootballAPIError as exc:
            st.error(str(exc))
            st.markdown("</div>", unsafe_allow_html=True)
            return

    all_rows = result.get("rows") or []
    rows = filter_rows_by_league(all_rows, league_id)
    banner = str(result.get("banner") or "").strip()
    show_empty_today = False

    if not rows and time_f == "heute" and not all_rows:
        show_empty_today = True
        with st.spinner("Nächste Spiele laden…"):
            try:
                next_result = resolve_competition_board(
                    service,
                    username=username,
                    session_plan=session_plan,
                    competition=comp,
                    time_filter="naechste",
                    probe_analysis=True,
                )
                all_rows = next_result.get("rows") or []
                rows = filter_rows_by_league(all_rows, league_id)
                if rows:
                    banner = MSG_NEXT_SECTION
            except FootballAPIError:
                pass

    st.session_state["fb_displayed_topspiele_count"] = len(rows)
    st.session_state["fb_displayed_allspiele_count"] = 0

    if show_empty_today and rows:
        st.markdown(
            f'<p class="fb2-empty-note">{html.escape(MSG_EMPTY_TODAY)}</p>',
            unsafe_allow_html=True,
        )

    if banner:
        st.markdown(
            f'<p class="fb2-banner">{html.escape(banner)}</p>',
            unsafe_allow_html=True,
        )

    if not rows:
        empty_text = MSG_EMPTY_TODAY if time_f == "heute" else "Keine Spiele in dieser Auswahl."
        st.markdown(
            f'<div class="fb2-empty">{html.escape(empty_text)}</div>',
            unsafe_allow_html=True,
        )
        api_errors = [str(e).strip() for e in (result.get("errors") or []) if str(e).strip()]
        if api_errors:
            st.caption(
                "Spieldaten derzeit nicht verfügbar (API-Limit oder Verbindung). "
                "Bitte später erneut versuchen."
            )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for row in rows:
        fid = row.get("fixture_id")
        st.markdown('<div class="fb2-card-wrap">', unsafe_allow_html=True)
        st.markdown(match_card_html(row), unsafe_allow_html=True)
        st.markdown('<div class="fb2-card-actions">', unsafe_allow_html=True)
        can = bool(row.get("analysis_available")) and bool(fid)
        if can:
            if st.button("Analyse", key=f"fb2_a_{fid}", use_container_width=True):
                st.session_state["fb_sel"] = int(fid)
                st.session_state["fb_detail"] = None
                st.rerun()
        else:
            st.markdown(
                '<div class="fb2-no-analysis">Analyse nicht verfügbar</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


render_football_page = render_football_betting_board
