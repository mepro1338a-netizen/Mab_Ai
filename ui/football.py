"""Football AI — competition browser (curated) / Alle API-Spiele."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_api import FootballAPIError, get_football_service
from services.football_feed import (
    fetch_all_api_payload,
    fetch_match_detail,
    resolve_football_feed,
)
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css

_FB_SESSION_DEFAULTS: dict[str, Any] = {
    "fb_v": 9,
    "fb_mode": "curated",
    "fb_competition": "deutschland",
    "fb_time": "heute",
    "fb_payload": None,
    "fb_detail": None,
    "fb_sel": None,
    "fb_displayed_topspiele_count": 0,
    "fb_displayed_allspiele_count": 0,
}

_COMPETITIONS = (
    ("deutschland", "Deutschland"),
    ("uefa", "UEFA"),
    ("topligen", "Topligen"),
    ("nationalteams", "Nationalteams"),
)
_TIME = (
    ("heute", "Heute"),
    ("live", "Live"),
    ("morgen", "Morgen"),
    ("naechste", "Nächste"),
)
_MODES = (("curated", "Wettbewerbe"), ("alle", "Alle Spiele"))


def _ensure_football_session() -> None:
    if st.session_state.get("fb_v") != _FB_SESSION_DEFAULTS["fb_v"]:
        st.session_state["fb_v"] = _FB_SESSION_DEFAULTS["fb_v"]
        st.session_state["fb_payload"] = None
        st.session_state["fb_detail"] = None
        st.session_state["fb_sel"] = None
    for key, value in _FB_SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


_CSS = """
.fb-page { max-width: 1080px; margin: 0 auto; padding-bottom: 32px; }
.fb-h1 { margin: 0; font-size: 22px; color: #f8fafc; font-weight: 800; }
.fb-sub { color: #94a3b8; font-size: 13px; margin: 4px 0 20px; }
.fb-label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: .06em; margin: 12px 0 8px; }
.fb-banner {
  font-size: 12px; color: #a78bfa; padding: 8px 12px; margin-bottom: 12px;
  background: rgba(139,92,246,.08); border: 1px solid rgba(139,92,246,.2); border-radius: 8px;
}
.fb-banner.raw { color: #94a3b8; background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.08); }
.fb-card {
  padding: 12px 14px; margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,.07); border-radius: 10px; background: rgba(15,23,42,.88);
}
.fb-card.live { border-left: 3px solid #22c55e; }
.fb-meta { font-size: 11px; color: #94a3b8; margin-bottom: 6px; }
.fb-team { font-size: 14px; font-weight: 700; color: #f1f5f9; }
.fb-mid { font-size: 13px; font-weight: 800; color: #e2e8f0; margin: 4px 0; text-align: center; }
.fb-foot { font-size: 12px; color: #64748b; margin-top: 8px; display: flex; justify-content: space-between; gap: 8px; }
.fb-quote { color: #94a3b8; }
.fb-analysis {
  margin-top: 14px; padding: 16px 18px;
  border: 1px solid rgba(139,92,246,.25); border-radius: 12px; background: rgba(15,23,42,.92);
}
.fb-analysis h3 { color: #f8fafc; font-size: 15px; margin: 0 0 10px; }
.fb-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
@media (max-width: 768px) { .fb-grid { grid-template-columns: 1fr; } }
.fb-stat { padding: 8px 10px; border-radius: 8px; background: rgba(0,0,0,.2); border: 1px solid rgba(255,255,255,.06); }
.fb-stat .l { font-size: 10px; color: #94a3b8; text-transform: uppercase; }
.fb-stat .v { font-size: 14px; color: #f1f5f9; font-weight: 600; margin-top: 4px; }
.fb-gate { padding: 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,.08); color: #94a3b8; }
"""


def _css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1080, 64, 28) + _CSS)


def _card_html(row: dict[str, Any]) -> str:
    card = row.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    dt = " · ".join(
        x
        for x in (
            str(card.get("league") or ""),
            str(card.get("country") or ""),
            str(card.get("date") or ""),
            str(card.get("time") or ""),
        )
        if x
    )
    dt = html.escape(dt)
    live = bool(card.get("live"))
    mid = html.escape(str(card.get("score") if live else (card.get("time") or "–")))
    quote = html.escape(str(row.get("quote_label") or "nicht verfügbar"))
    cls = "fb-card live" if live else "fb-card"
    return (
        f'<div class="{cls}"><div class="fb-meta">{dt}</div>'
        f'<div class="fb-team">{home}</div><div class="fb-mid">{mid}</div>'
        f'<div class="fb-team">{away}</div>'
        f'<div class="fb-foot"><span class="fb-quote">Quote: {quote}</span></div></div>'
    )


def _render_analysis(detail: dict[str, Any]) -> None:
    card = detail.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    if not detail.get("analysis_available"):
        return
    pred = detail.get("prediction_insights") or {}
    odds = detail.get("odds") or {}
    hp, dp, ap = pred.get("home_pct"), pred.get("draw_pct"), pred.get("away_pct")
    win = (
        f"Heim {hp:.0f}% · X {(dp or 0):.0f}% · Auswärts {(ap or 0):.0f}%"
        if hp is not None
        else "—"
    )
    h, d, a = odds.get("home"), odds.get("draw"), odds.get("away")
    quote = (
        f"1 {float(h):.2f} · X {float(d):.2f} · 2 {float(a):.2f}"
        if h and d and a
        else "nicht verfügbar"
    )
    advice = str(pred.get("advice") or "").strip() or "—"
    st.markdown(
        f"""
<div class="fb-analysis">
  <h3>{home} vs {away}</h3>
  <div class="fb-grid">
    <div class="fb-stat"><div class="l">Siegchance</div><div class="v">{html.escape(win)}</div></div>
    <div class="fb-stat"><div class="l">Quote</div><div class="v">{html.escape(quote)}</div></div>
    <div class="fb-stat"><div class="l">Hinweis</div><div class="v">{html.escape(advice[:80])}</div></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_football_betting_board(
    *,
    username: str,
    session_plan: str,
    open_premium,
) -> None:
    _ = open_premium
    _css()
    st.markdown('<div class="fb-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="fb-h1">Football AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="fb-sub">Kuratiert · Top-Ligen · Live · Nächste Spiele</p>',
        unsafe_allow_html=True,
    )

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        st.markdown(
            '<div class="fb-gate">Football AI erfordert einen aktiven Football-Plan.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    service = get_football_service()
    if not service.is_configured():
        st.error("FOOTBALL_API_KEY fehlt.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    _ensure_football_session()

    mode = str(st.session_state.get("fb_mode") or "curated")
    comp = str(st.session_state.get("fb_competition") or "deutschland")
    time_f = str(st.session_state.get("fb_time") or "heute")

    ref_col, _ = st.columns([1, 11])
    with ref_col:
        if st.button("↻", key="fb_ref"):
            st.session_state["fb_payload"] = None
            st.session_state["fb_detail"] = None
            st.rerun()

    st.markdown('<div class="fb-label">Wettbewerb</div>', unsafe_allow_html=True)
    mc = st.columns(4)
    nc, nm, nt = comp, mode, time_f
    for col, (k, lbl) in zip(mc, _COMPETITIONS):
        with col:
            if st.button(
                lbl,
                key=f"fb_c_{k}",
                type="primary" if comp == k else "secondary",
                use_container_width=True,
            ):
                nc = k

    st.markdown('<div class="fb-label">Zeitraum</div>', unsafe_allow_html=True)
    tc = st.columns(4)
    for col, (k, lbl) in zip(tc, _TIME):
        with col:
            if st.button(
                lbl,
                key=f"fb_t_{k}",
                type="primary" if time_f == k else "secondary",
                use_container_width=True,
            ):
                nt = k

    st.markdown('<div class="fb-label">Ansicht</div>', unsafe_allow_html=True)
    vc = st.columns(2)
    for col, (k, lbl) in zip(vc, _MODES):
        with col:
            if st.button(
                lbl,
                key=f"fb_m_{k}",
                type="primary" if mode == k else "secondary",
                use_container_width=True,
            ):
                nm = k

    if nc != comp or nm != mode or nt != time_f:
        st.session_state["fb_competition"] = nc
        st.session_state["fb_mode"] = nm
        st.session_state["fb_time"] = nt
        st.session_state["fb_payload"] = None
        st.session_state["fb_detail"] = None
        st.session_state["fb_sel"] = None
        st.rerun()

    comp = str(st.session_state.get("fb_competition") or "deutschland")
    mode = str(st.session_state.get("fb_mode") or "curated")
    time_f = str(st.session_state.get("fb_time") or "heute")
    is_raw = mode == "alle"

    cache_key = f"{mode}|{comp}|{time_f}"
    if st.session_state.get("fb_cache_key") != cache_key:
        st.session_state["fb_payload"] = None
        st.session_state["fb_cache_key"] = cache_key

    if st.session_state.get("fb_payload") is None and is_raw:
        with st.spinner("Lade API-Spiele…"):
            try:
                st.session_state["fb_payload"] = fetch_all_api_payload(
                    service, username=username
                )
            except FootballAPIError as exc:
                st.error(str(exc))
                st.markdown("</div>", unsafe_allow_html=True)
                return

    payload = st.session_state.get("fb_payload")

    with st.spinner("Lade Spiele…"):
        try:
            result = resolve_football_feed(
                payload,
                service,
                view_mode=mode,
                time_filter=time_f,
                username=username,
                session_plan=session_plan,
                competition=comp,
                probe_analysis=not is_raw,
            )
        except FootballAPIError as exc:
            st.error(str(exc))
            st.markdown("</div>", unsafe_allow_html=True)
            return

    rows = result.get("rows") or []
    banner = str(result.get("banner") or "").strip()

    st.session_state["fb_displayed_topspiele_count"] = len(rows) if not is_raw else 0
    st.session_state["fb_displayed_allspiele_count"] = len(rows) if is_raw else 0

    if banner:
        cls = " raw" if is_raw else ""
        st.markdown(
            f'<p class="fb-banner{cls}">{html.escape(banner)}</p>',
            unsafe_allow_html=True,
        )

    if not rows:
        st.markdown(
            f'<p class="fb-sub">{html.escape(banner or "Keine Spiele in dieser Auswahl.")}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    sel = st.session_state.get("fb_sel")
    for row in rows:
        fid = row.get("fixture_id")
        st.markdown(_card_html(row), unsafe_allow_html=True)
        can = bool(row.get("analysis_available")) and bool(fid)
        if can:
            if st.button("Analyse", key=f"fb_a_{fid}", use_container_width=True):
                st.session_state["fb_sel"] = int(fid)
                st.session_state["fb_detail"] = None
                st.rerun()
        else:
            st.caption("Analyse nicht verfügbar")

    if sel:
        ck = f"{sel}|{session_plan}"
        detail = st.session_state.get("fb_detail")
        if not isinstance(detail, dict) or detail.get("_ck") != ck:
            with st.spinner("Analyse laden…"):
                detail = fetch_match_detail(
                    service, int(sel), username=username, session_plan=session_plan
                )
                detail["_ck"] = ck
                st.session_state["fb_detail"] = detail
        _render_analysis(detail or {})

    st.markdown("</div>", unsafe_allow_html=True)


render_football_page = render_football_betting_board
