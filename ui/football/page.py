"""Football AI — main page orchestrator."""
from __future__ import annotations

import html

import streamlit as st

from config import football_api_env_hint, football_plan_rank, is_football_api_configured
from services.football_api import FootballAPIError, get_football_service
from services.football_feed import fetch_match_detail, resolve_competition_board
from ui.components import format_num
from ui.football.analysis import render_analysis
from ui.football.cards import filter_rows_by_league, match_card_html
from ui.football.constants import (
    CATEGORY_TABS,
    MSG_EMPTY_SELECTION,
    MSG_EMPTY_TODAY,
    MSG_NEXT_SECTION,
    MSG_PREMIUM_LEAGUE,
    PREMIUM_LEAGUE_HINT,
    TIME_OPTIONS,
    available_league_options,
    league_has_free_tier_data,
    league_options_for,
)
from ui.football.session import ensure_football_session
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css
from ui.football.styles import FOOTBALL_CSS


def _inject_css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1100, 20, 32) + FOOTBALL_CSS)


def _clear_feed() -> None:
    st.session_state["fb_payload"] = None
    st.session_state["fb_detail"] = None
    st.session_state["fb_sel"] = None


def _category_labels() -> list[str]:
    return [label for _, label in CATEGORY_TABS]


def _category_keys() -> list[str]:
    return [key for key, _ in CATEGORY_TABS]


def _time_labels() -> list[str]:
    return [label for _, label in TIME_OPTIONS]


def _time_keys() -> list[str]:
    return [key for key, _ in TIME_OPTIONS]


def _resolve_category(label: str) -> str:
    keys = _category_keys()
    labels = _category_labels()
    try:
        return keys[labels.index(label)]
    except ValueError:
        return "deutschland"


def _resolve_time(label: str) -> str:
    keys = _time_keys()
    labels = _time_labels()
    try:
        return keys[labels.index(label)]
    except ValueError:
        return "heute"


def _label_for_category(competition: str) -> str:
    for key, label in CATEGORY_TABS:
        if key == competition:
            return label
    return CATEGORY_TABS[0][1]


def _label_for_time(time_key: str) -> str:
    for key, label in TIME_OPTIONS:
        if key == time_key:
            return label
    return TIME_OPTIONS[0][1]


def _sync_selectbox(key: str, label: str, options: list[str], current_label: str) -> str:
    if key not in st.session_state or st.session_state[key] not in options:
        st.session_state[key] = current_label
    return str(
        st.selectbox(
            label,
            options=options,
            key=key,
        )
    )


def _render_top_bar() -> None:
    tokens = format_num(int(st.session_state.get("tokens", 0) or 0))
    title_l, meta_r = st.columns([8, 4])
    with title_l:
        st.markdown(
            """
<div class="fb2-header-main">
  <h1>Football</h1>
  <p>Live-Spiele, Quoten und KI-Analyse — nur echte API-Daten.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    with meta_r:
        pill_c, refresh_c = st.columns([5, 1])
        with pill_c:
            st.markdown(
                f"""
<div class="fb2-header-meta">
  <span class="fb2-pill" title="Token-Guthaben">
    <span class="fb2-pill-label">Guthaben</span>
    <strong>{html.escape(tokens)}</strong>
  </span>
</div>
                """,
                unsafe_allow_html=True,
            )
        with refresh_c:
            st.markdown('<div class="fb2-refresh-slot">', unsafe_allow_html=True)
            if st.button(
                "",
                key="fb_refresh",
                icon=":material/refresh:",
                type="tertiary",
                help="Spiele neu laden",
            ):
                _clear_feed()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def _render_filter_panel() -> tuple[str, str, int]:
    competition = str(st.session_state.get("fb_competition") or "deutschland")
    time_key = str(st.session_state.get("fb_time") or "heute")
    league_id = int(st.session_state.get("fb_league_id") or 0)

    st.markdown('<div class="fb2-panel">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="fb2-panel-head">
  <span class="fb2-panel-title">Spiel-Filter</span>
  <span class="fb2-panel-sub">Zeitraum, Wettbewerb und Liga für KI-Analyse</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    col_time, col_cat, col_league = st.columns(3, gap="medium")

    with col_time:
        time_choice = _sync_selectbox(
            "fb_time_sel",
            "⏱️ Zeitraum",
            _time_labels(),
            _label_for_time(time_key),
        )
    new_time = _resolve_time(time_choice)
    if new_time != time_key:
        st.session_state["fb_time"] = new_time
        time_key = new_time
        _clear_feed()

    with col_cat:
        cat_choice = _sync_selectbox(
            "fb_category_sel",
            "🏆 Wettbewerb",
            _category_labels(),
            _label_for_category(competition),
        )
    new_comp = _resolve_category(cat_choice)
    if new_comp != competition:
        st.session_state["fb_competition"] = new_comp
        competition = new_comp
        st.session_state["fb_league_id"] = 0
        league_id = 0
        _clear_feed()

    options = league_options_for(competition)
    labels = [label for _, label, _ in options]
    ids = [lid for lid, _, _ in options]
    if league_id not in ids:
        league_id = 0
        st.session_state["fb_league_id"] = 0

    with col_league:
        league_label = _sync_selectbox(
            f"fb_league_sel_{competition}",
            "🏟️ Liga & Turnier",
            labels,
            labels[ids.index(league_id)],
        )
    new_league_id = ids[labels.index(league_label)]
    if new_league_id != league_id:
        st.session_state["fb_league_id"] = new_league_id
        league_id = new_league_id
        _clear_feed()

    available = available_league_options(competition)
    if league_id and not league_has_free_tier_data(league_id):
        st.markdown(
            '<p class="fb2-panel-warn">🔒 Premium-Wettbewerb — '
            "im Free-Tier keine Live-Daten. Bitte eine Liga mit ✓ wählen.</p>",
            unsafe_allow_html=True,
        )
    elif len(available) < len(options):
        st.caption(PREMIUM_LEAGUE_HINT)

    st.markdown("</div>", unsafe_allow_html=True)
    return competition, time_key, league_id


def _render_empty_state(
    *,
    time_key: str,
    league_id: int,
    api_errors: list[str],
    note: str = "",
) -> None:
    if league_id and not league_has_free_tier_data(league_id):
        message = MSG_PREMIUM_LEAGUE
    elif time_key == "heute":
        message = MSG_EMPTY_TODAY
    else:
        message = MSG_EMPTY_SELECTION

    note_html = (
        f'<p class="fb2-empty-note">{html.escape(note)}</p>' if note else ""
    )
    st.markdown(
        f"""
<div class="fb2-empty">
  <div class="fb2-empty-icon" aria-hidden="true">⚽</div>
  <p class="fb2-empty-title">{html.escape(message)}</p>
  {note_html}
  <p class="fb2-empty-hint">Filter anpassen oder später erneut versuchen.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    if api_errors:
        st.caption(
            "Spieldaten derzeit nicht verfügbar (API-Limit oder Verbindung). "
            "Bitte später erneut versuchen."
        )


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
    _render_top_bar()

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        st.markdown(
            '<div class="fb2-gate">Football Intelligence ist mit deinem Plan noch nicht aktiv. '
            "Upgrade unter Premium.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not is_football_api_configured():
        env_hint = html.escape(football_api_env_hint())
        st.markdown(
            f'<div class="fb2-gate">Football Intelligence benötigt <strong>{env_hint}</strong> '
            "in der Server-Umgebung (Railway Variables oder lokale .env). "
            "Ohne Key werden keine Spiele geladen.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    service = get_football_service()
    sel = st.session_state.get("fb_sel")

    if sel:
        if st.button("← Zurück zur Spielübersicht", key="fb_back", type="secondary"):
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

    comp, time_f, league_id = _render_filter_panel()

    if league_id and not league_has_free_tier_data(league_id):
        _render_empty_state(time_key=time_f, league_id=league_id, api_errors=[])
        st.markdown("</div>", unsafe_allow_html=True)
        return

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
    empty_note = ""
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
                    empty_note = MSG_NEXT_SECTION
            except FootballAPIError:
                pass

    st.session_state["fb_displayed_topspiele_count"] = len(rows)
    st.session_state["fb_displayed_allspiele_count"] = 0

    if not rows:
        api_errors = [str(e).strip() for e in (result.get("errors") or []) if str(e).strip()]
        _render_empty_state(
            time_key=time_f,
            league_id=league_id,
            api_errors=api_errors,
            note=empty_note if show_empty_today else "",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if show_empty_today and empty_note:
        st.markdown(
            f'<p class="fb2-section-label">{html.escape(empty_note)}</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="fb2-match-list">', unsafe_allow_html=True)
    for row in rows:
        fid = row.get("fixture_id")
        st.markdown('<div class="fb2-card-wrap">', unsafe_allow_html=True)
        st.markdown(match_card_html(row), unsafe_allow_html=True)
        st.markdown('<div class="fb2-card-actions">', unsafe_allow_html=True)
        can = bool(row.get("analysis_available")) and bool(fid)
        if can:
            if st.button("Analyse", key=f"fb_a_{fid}", use_container_width=True):
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

    st.markdown("</div>", unsafe_allow_html=True)


render_football_page = render_football_betting_board
