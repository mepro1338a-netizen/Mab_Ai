"""Football AI — minimal beta board (Topspiele / Alle Spiele)."""
from __future__ import annotations

import html
import time
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_board import (
    fetch_board_payload,
    fetch_match_detail,
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
.fbb-quote { font-size: 12px; color: #fbbf24 !important; margin-top: 6px; }
.fbb-empty {
    text-align: center; padding: 24px 16px; color: #94a3b8 !important;
    background: rgba(15,23,42,.75); border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
}
.fbb-panel {
    margin: 8px 0 16px 0; padding: 14px 16px;
    background: rgba(10,14,28,.96); border: 1px solid rgba(139,92,246,.25); border-radius: 12px;
}
.fbb-panel h4 { margin: 0 0 8px 0; color: #e2e8f0 !important; font-size: 15px; }
.fbb-panel p { margin: 4px 0; color: #cbd5e1 !important; font-size: 13px; }
"""

_TIME = (("heute", "Heute"), ("live", "Live"), ("morgen", "Morgen"))
_MODES = (("premium", "Topspiele"), ("raw", "Alle Spiele"))


def _inject_css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1100, 100, 28) + BETA_GLOBAL_CSS + _CSS)


def _fmt_odd(val: float | None) -> str:
    return "—" if val is None else f"{val:.2f}"


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
    ho, do, ao = row.get("home_odd"), row.get("draw_odd"), row.get("away_odd")
    quote = "—"
    if ho and do and ao:
        quote = f"{_fmt_odd(ho)} / {_fmt_odd(do)} / {_fmt_odd(ao)}"
    cls = " fbb-match live" if live else " fbb-match"
    return (
        f'<div class="{cls.strip()}">'
        f'<div class="fbb-meta">{meta}</div>'
        f'<div class="fbb-team">{home}</div>'
        f'<div class="fbb-mid">{mid}</div>'
        f'<div class="fbb-team">{away}</div>'
        f'<div class="fbb-quote">Quote: {html.escape(quote)}</div>'
        f"</div>"
    )


def _render_analysis(detail: dict[str, Any]) -> None:
    card = detail.get("card") or {}
    title = html.escape(f"{card.get('home')} vs {card.get('away')}")
    pred = detail.get("prediction") or {}
    pick = pred.get("best_bet") or "—"
    st.markdown(f'<div class="fbb-panel"><h4>{title}</h4>', unsafe_allow_html=True)
    st.markdown(f'<p><strong>Tipp:</strong> {html.escape(str(pick))}</p>', unsafe_allow_html=True)
    reasons = pred.get("reasons") or []
    if reasons:
        items = "".join(f"<li>{html.escape(str(r))}</li>" for r in reasons[:3])
        st.markdown(f"<ul>{items}</ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


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
        '<p class="fbb-sub">Bundesliga · UEFA · Top-Ligen · WM</p>',
        unsafe_allow_html=True,
    )

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        render_upgrade_card(
            "Football AI",
            "Topspiele & Analyse ab Football Starter.",
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
    if st.session_state.get("fb_ver") != 4:
        st.session_state.fb_ver = 4
        st.session_state.fb_payload = None

    mode = str(st.session_state.fb_mode or "premium")
    time_f = str(st.session_state.fb_time or "heute")

    top = st.columns([1, 1, 6])
    with top[0]:
        if st.button("↻", key="fbb_refresh", help="Aktualisieren"):
            st.session_state.fb_payload = None
            st.rerun()

    mc = st.columns(2)
    new_mode = mode
    for col, (key, label) in zip(mc, _MODES):
        with col:
            if st.button(label, key=f"fbb_m_{key}", type="primary" if mode == key else "secondary", width="stretch"):
                new_mode = key
    tc = st.columns(3)
    new_time = time_f
    for col, (key, label) in zip(tc, _TIME):
        with col:
            if st.button(label, key=f"fbb_t_{key}", type="primary" if time_f == key else "secondary", width="stretch"):
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

    selected = st.session_state.get("fb_analyse")
    for row in rows:
        fid = row.get("fixture_id")
        c1, c2 = st.columns([11, 1])
        with c1:
            st.markdown(_match_html(row), unsafe_allow_html=True)
        with c2:
            can_analyse = bool(rank >= 2 and row.get("analysis_available"))
            if st.button(
                "Analyse" if can_analyse else "—",
                key=f"fbb_a_{fid}",
                disabled=not can_analyse,
                width="stretch",
            ):
                st.session_state.fb_analyse = fid
                st.rerun()

        if selected and fid and int(selected) == int(fid):
            cache_key = f"fb_detail_{fid}"
            if cache_key not in st.session_state:
                with st.spinner("Analyse…"):
                    try:
                        st.session_state[cache_key] = fetch_match_detail(
                            service,
                            int(fid),
                            username=username,
                            session_plan=session_plan,
                        )
                    except Exception as exc:
                        st.session_state[cache_key] = {"error": str(exc)}
            detail = st.session_state.get(cache_key) or {}
            if detail.get("error"):
                st.warning(str(detail["error"]))
            elif detail.get("analysis_available"):
                _render_analysis(detail)
            else:
                st.info("Analyse nicht verfügbar – zu wenig Daten.")
            if st.button("Schließen", key=f"fbb_x_{fid}"):
                st.session_state.pop("fb_analyse", None)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
