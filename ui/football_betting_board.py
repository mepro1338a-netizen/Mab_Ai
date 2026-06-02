"""Football AI — kuratierter Feed (Topspiele / Alle Spiele)."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_board import (
    fetch_board_payload,
    resolve_football_board,
)
from services.football_service import FootballAPIError, get_football_service
from ui.premium_foundation import BETA_GLOBAL_CSS, render_upgrade_card
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css

_CSS = """
.fbb-root { max-width: 1100px; margin: 0 auto; }
.fbb-title { margin: 0 0 4px 0; font-size: 22px; color: #f8fafc !important; font-weight: 800; }
.fbb-sub { color: #94a3b8 !important; font-size: 13px; margin: 0 0 14px 0; }
.fbb-note {
    color: #fde047 !important; font-size: 12px; padding: 8px 12px; margin: 0 0 12px 0;
    background: rgba(234,179,8,.08); border: 1px solid rgba(234,179,8,.22); border-radius: 8px;
}
.fbb-match {
    padding: 12px 14px; margin-bottom: 8px;
    background: rgba(15,23,42,.9); border: 1px solid rgba(255,255,255,.07); border-radius: 10px;
}
.fbb-match.live { border-left: 3px solid #22c55e; }
.fbb-meta { font-size: 11px; color: #94a3b8 !important; margin-bottom: 6px; }
.fbb-team { font-size: 14px; font-weight: 700; color: #f1f5f9 !important; }
.fbb-mid { font-size: 13px; font-weight: 800; color: #e2e8f0 !important; margin: 4px 0; }
.fbb-quote, .fbb-hint { font-size: 12px; margin-top: 6px; }
.fbb-quote { color: #94a3b8 !important; }
.fbb-hint { color: #64748b !important; }
.fbb-empty {
    text-align: center; padding: 24px 16px; color: #94a3b8 !important;
    background: rgba(15,23,42,.75); border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
}
"""

_TIME = (("heute", "Heute"), ("live", "Live"), ("morgen", "Morgen"))
_MODES = (("premium", "Topspiele"), ("raw", "Alle Spiele"))


def _inject_css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1100, 100, 28) + BETA_GLOBAL_CSS + _CSS)


def _match_html(row: dict[str, Any]) -> str:
    card = row.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    league = html.escape(str(card.get("league") or ""))
    country = html.escape(str(card.get("country") or ""))
    when = html.escape(str(card.get("time") or card.get("date") or ""))
    meta = " · ".join(x for x in (league, country, when) if x)
    live = bool(card.get("live"))
    mid = html.escape(str(card.get("score") if live else (card.get("time") or "—")))
    cls = "fbb-match live" if live else "fbb-match"
    return (
        f'<div class="{cls}">'
        f'<div class="fbb-meta">{meta}</div>'
        f'<div class="fbb-team">{home}</div>'
        f'<div class="fbb-mid">{mid}</div>'
        f'<div class="fbb-team">{away}</div>'
        f'<div class="fbb-quote">Quote: —</div>'
        f'<div class="fbb-hint">Analyse nicht verfügbar</div>'
        f"</div>"
    )


def render_football_betting_board(
    *,
    username: str,
    session_plan: str,
    open_premium,
) -> None:
    _inject_css()
    st.markdown('<div class="fbb-root">', unsafe_allow_html=True)
    st.markdown('<h1 class="fbb-title">Football AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="fbb-sub">Kuratiert · Top-Ligen · max. 10 Topspiele · 50 Alle Spiele</p>',
        unsafe_allow_html=True,
    )

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        render_upgrade_card(
            "Football AI",
            "Topspiele ab Football Starter.",
            "football_starter",
            button_key="fbb_starter",
            on_upgrade=open_premium,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    service = get_football_service()
    if not service.is_configured():
        st.error("FOOTBALL_API_KEY fehlt.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if "fb_mode" not in st.session_state:
        st.session_state.fb_mode = "premium"
    if "fb_time" not in st.session_state:
        st.session_state.fb_time = "heute"
    if "fb_payload" not in st.session_state:
        st.session_state.fb_payload = None
    if st.session_state.get("fb_ver") != 5:
        st.session_state.fb_ver = 5
        st.session_state.fb_payload = None

    mode = str(st.session_state.fb_mode or "premium")
    time_f = str(st.session_state.fb_time or "heute")

    rc = st.columns([1, 8])
    with rc[0]:
        if st.button("↻", key="fbb_refresh", help="Aktualisieren"):
            st.session_state.fb_payload = None
            st.rerun()

    mc = st.columns(2)
    new_mode = mode
    for col, (key, label) in zip(mc, _MODES):
        with col:
            if st.button(
                label,
                key=f"fbb_m_{key}",
                type="primary" if mode == key else "secondary",
                width="stretch",
            ):
                new_mode = key
    tc = st.columns(3)
    new_time = time_f
    for col, (key, label) in zip(tc, _TIME):
        with col:
            if st.button(
                label,
                key=f"fbb_t_{key}",
                type="primary" if time_f == key else "secondary",
                width="stretch",
            ):
                new_time = key

    if new_mode != mode or new_time != time_f:
        st.session_state.fb_mode = new_mode
        st.session_state.fb_time = new_time
        st.session_state.fb_payload = None
        st.rerun()
    mode = str(st.session_state.fb_mode)
    time_f = str(st.session_state.fb_time)

    if st.session_state.fb_payload is None:
        with st.spinner("Spiele laden…"):
            try:
                st.session_state.fb_payload = fetch_board_payload(
                    service,
                    username=username,
                    include_live=(time_f == "live"),
                    include_raw=True,
                )
            except FootballAPIError as exc:
                st.error(str(exc))
                st.markdown("</div>", unsafe_allow_html=True)
                return

    payload = st.session_state.fb_payload or {}
    for err in payload.get("errors") or []:
        low = str(err).lower()
        if "rate limit" not in low:
            st.warning(str(err))

    result = resolve_football_board(
        payload,
        service,
        view_mode=mode,
        time_filter=time_f,
        username=username,
        session_plan=session_plan,
    )
    rows = result.get("rows") or []
    banner = str(result.get("banner") or "").strip()
    if banner:
        st.markdown(f'<p class="fbb-note">{html.escape(banner)}</p>', unsafe_allow_html=True)

    if not rows:
        st.markdown(
            f'<div class="fbb-empty"><p>{html.escape(banner or "Keine Spiele.")}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for row in rows:
        st.markdown(_match_html(row), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
