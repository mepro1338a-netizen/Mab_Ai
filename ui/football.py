"""Football AI — Topspiele (strict) / Alle API-Spiele."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_api import FootballAPIError, get_football_service
from services.football_feed import (
    fetch_board_payload,
    fetch_match_detail,
    resolve_football_feed,
)
from ui.premium_foundation import BETA_GLOBAL_CSS, render_upgrade_card
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css

_CSS = """
.fb-page { max-width: 1080px; margin: 0 auto; }
.fb-h1 { margin: 0; font-size: 22px; color: #f8fafc; font-weight: 800; }
.fb-sub { color: #94a3b8; font-size: 13px; margin: 4px 0 16px; }
.fb-banner {
  font-size: 12px; color: #a78bfa; padding: 8px 12px; margin-bottom: 12px;
  background: rgba(139,92,246,.08); border: 1px solid rgba(139,92,246,.2); border-radius: 8px;
}
.fb-banner.raw { color: #94a3b8; background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.08); }
.fb-empty {
  text-align: center; padding: 28px 16px; color: #94a3b8;
  border: 1px solid rgba(255,255,255,.08); border-radius: 12px; background: rgba(15,23,42,.6);
}
.fb-card {
  padding: 12px 14px; margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,.07); border-radius: 10px; background: rgba(15,23,42,.88);
}
.fb-card.live { border-left: 3px solid #22c55e; }
.fb-meta { font-size: 11px; color: #94a3b8; margin-bottom: 6px; }
.fb-team { font-size: 14px; font-weight: 700; color: #f1f5f9; }
.fb-mid { font-size: 13px; font-weight: 800; color: #e2e8f0; margin: 4px 0; }
.fb-foot { font-size: 12px; color: #64748b; margin-top: 8px; }
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
"""

_TIME = (("heute", "Heute"), ("live", "Live"), ("morgen", "Morgen"))
_MODES = (("premium", "Topspiele"), ("raw", "Alle Spiele"))


def _css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1080, 64, 28) + BETA_GLOBAL_CSS + _CSS)


def _quote_text(row: dict[str, Any]) -> str:
    if row.get("has_odds"):
        for key in ("home_odd", "draw_odd", "away_odd"):
            if row.get(key) is not None:
                pass
    return "—"


def _card_html(row: dict[str, Any]) -> str:
    card = row.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    meta = " · ".join(
        x
        for x in (
            str(card.get("league") or ""),
            str(card.get("country") or ""),
            str(card.get("time") or card.get("date") or ""),
        )
        if x
    )
    meta = html.escape(meta)
    live = bool(card.get("live"))
    mid = html.escape(str(card.get("score") if live else (card.get("time") or "—")))
    cls = "fb-card live" if live else "fb-card"
    return (
        f'<div class="{cls}"><div class="fb-meta">{meta}</div>'
        f'<div class="fb-team">{home}</div><div class="fb-mid">{mid}</div>'
        f'<div class="fb-team">{away}</div>'
        f'<div class="fb-foot"><span class="fb-quote">Quote: —</span></div></div>'
    )


def _render_analysis(detail: dict[str, Any]) -> None:
    card = detail.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    if detail.get("error"):
        st.markdown(
            f'<div class="fb-analysis"><p class="fb-foot">{html.escape(str(detail["error"]))}</p></div>',
            unsafe_allow_html=True,
        )
        return
    if not detail.get("analysis_available"):
        st.markdown(
            '<div class="fb-analysis"><p class="fb-foot">'
            "Analyse für dieses Spiel aktuell nicht verfügbar."
            "</p></div>",
            unsafe_allow_html=True,
        )
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
        else "—"
    )
    advice = str(pred.get("advice") or "").strip() or "—"
    st.markdown(
        f"""
<div class="fb-analysis">
  <h3>{home} vs {away}</h3>
  <div class="fb-grid">
    <div class="fb-stat"><div class="l">Siegchance</div><div class="v">{html.escape(win)}</div></div>
    <div class="fb-stat"><div class="l">Quote</div><div class="v">{html.escape(quote)}</div></div>
    <div class="fb-stat"><div class="l">Empfehlung</div><div class="v">{html.escape(advice[:80])}</div></div>
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
    _css()
    st.markdown('<div class="fb-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="fb-h1">Football AI</h1>', unsafe_allow_html=True)

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        render_upgrade_card(
            "Football AI",
            "Topspiele ab Football Starter.",
            "football_starter",
            button_key="fb_up",
            on_upgrade=open_premium,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    service = get_football_service()
    if not service.is_configured():
        st.error("FOOTBALL_API_KEY fehlt.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if st.session_state.get("fb_v") != 8:
        st.session_state.fb_v = 8
        st.session_state.fb_payload = None
        st.session_state.fb_detail = None
        st.session_state.fb_sel = None

    mode = str(st.session_state.get("fb_mode") or "premium")
    time_f = str(st.session_state.get("fb_time") or "heute")

    c0, c1 = st.columns([1, 9])
    with c0:
        if st.button("↻", key="fb_ref"):
            st.session_state.fb_payload = None
            st.session_state.fb_detail = None
            st.rerun()

    mc = st.columns(2)
    nm, nt = mode, time_f
    for col, (k, lbl) in zip(mc, _MODES):
        with col:
            if st.button(lbl, key=f"fb_m_{k}", type="primary" if mode == k else "secondary", width="stretch"):
                nm = k
    tc = st.columns(3)
    for col, (k, lbl) in zip(tc, _TIME):
        with col:
            if st.button(lbl, key=f"fb_t_{k}", type="primary" if time_f == k else "secondary", width="stretch"):
                nt = k

    if nm != mode or nt != time_f:
        st.session_state.fb_mode = nm
        st.session_state.fb_time = nt
        st.session_state.fb_payload = None
        st.session_state.fb_detail = None
        st.session_state.fb_sel = None
        st.rerun()
    mode = str(st.session_state.fb_mode)
    time_f = str(st.session_state.fb_time)

    is_raw = mode == "raw"
    st.markdown(
        f'<p class="fb-sub">{"Alle API-Spiele (Rohdaten, max. 50)" if is_raw else "Topspiele — nur Premium-Ligen (ID-Whitelist)"}</p>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("fb_payload") is None:
        with st.spinner("Lade Spiele…"):
            try:
                st.session_state.fb_payload = fetch_board_payload(
                    service, username=username, time_filter=time_f
                )
            except FootballAPIError as exc:
                st.error(str(exc))
                st.markdown("</div>", unsafe_allow_html=True)
                return

    payload = st.session_state.fb_payload or {}
    for err in payload.get("errors") or []:
        if "rate limit" not in str(err).lower():
            st.warning(str(err))

    with st.spinner("Filtere Spiele…") if not is_raw else st.spinner("Lade API-Liste…"):
        result = resolve_football_feed(
            payload,
            service,
            view_mode=mode,
            time_filter=time_f,
            username=username,
            session_plan=session_plan,
            probe_analysis=not is_raw,
        )

    rows = result.get("rows") or []
    banner = str(result.get("banner") or "").strip()
    top_n = int(result.get("displayed_topspiele_count") or 0)
    all_n = int(result.get("displayed_allspiele_count") or 0)

    st.session_state.fb_displayed_topspiele_count = top_n
    st.session_state.fb_displayed_allspiele_count = all_n

    if is_raw and banner:
        st.markdown(f'<p class="fb-banner raw">{html.escape(banner)}</p>', unsafe_allow_html=True)
    elif not is_raw and not rows and banner:
        st.markdown(f'<div class="fb-empty"><p>{html.escape(banner)}</p></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return
    elif banner and rows:
        st.markdown(
            f'<p class="fb-banner{" raw" if is_raw else ""}">{html.escape(banner)}</p>',
            unsafe_allow_html=True,
        )

    if not rows:
        st.markdown(
            f'<div class="fb-empty"><p>{html.escape(banner or "Keine Spiele.")}</p></div>',
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
                st.session_state.fb_sel = int(fid)
                st.session_state.fb_detail = None
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
                st.session_state.fb_detail = detail
        _render_analysis(detail or {})

    st.markdown("</div>", unsafe_allow_html=True)


# compat alias
render_football_page = render_football_betting_board
