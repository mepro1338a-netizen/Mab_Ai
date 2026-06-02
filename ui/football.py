"""Football AI — Topspiele / Alle Spiele + Match-Analyse."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_logic import (
    fetch_board_payload,
    fetch_match_detail,
    resolve_football_board,
)
from services.football_api import FootballAPIError, get_football_service
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
    padding: 12px 14px; margin-bottom: 4px;
    background: rgba(15,23,42,.9); border: 1px solid rgba(255,255,255,.07); border-radius: 10px;
}
.fbb-match.live { border-left: 3px solid #22c55e; }
.fbb-meta { font-size: 11px; color: #94a3b8 !important; margin-bottom: 6px; }
.fbb-team { font-size: 14px; font-weight: 700; color: #f1f5f9 !important; }
.fbb-mid { font-size: 13px; font-weight: 800; color: #e2e8f0 !important; margin: 4px 0; }
.fbb-row-foot { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; margin-top: 8px; }
.fbb-quote { color: #94a3b8 !important; }
.fbb-hint { color: #64748b !important; }
.fbb-empty {
    text-align: center; padding: 24px 16px; color: #94a3b8 !important;
    background: rgba(15,23,42,.75); border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
}
.fbb-analysis {
    margin-top: 16px; padding: 18px 20px;
    background: rgba(15,23,42,.92); border: 1px solid rgba(139,92,246,.25); border-radius: 12px;
}
.fbb-analysis h3 { color: #f8fafc !important; font-size: 16px; margin: 0 0 12px 0; }
.fbb-analysis-grid {
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px;
}
@media (max-width: 768px) { .fbb-analysis-grid { grid-template-columns: 1fr; } }
.fbb-stat {
    padding: 10px 12px; border-radius: 10px;
    background: rgba(0,0,0,.25); border: 1px solid rgba(255,255,255,.06);
}
.fbb-stat .lbl { color: #94a3b8 !important; font-size: 10px; font-weight: 700; text-transform: uppercase; }
.fbb-stat .val { color: #f1f5f9 !important; font-size: 15px; font-weight: 700; margin-top: 4px; }
.fbb-analysis-empty { color: #94a3b8 !important; font-size: 14px; line-height: 1.5; }
"""

_TIME = (("heute", "Heute"), ("live", "Live"), ("morgen", "Morgen"))
_MODES = (("premium", "Topspiele"), ("raw", "Alle Spiele"))


def _inject_css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1100, 88, 28) + BETA_GLOBAL_CSS + _CSS)


def _format_quote(row: dict[str, Any]) -> str:
    for key in ("home_odd", "draw_odd", "away_odd"):
        val = row.get(key)
        if val is not None:
            try:
                if float(val) >= 1.01:
                    h = row.get("home_odd")
                    d = row.get("draw_odd")
                    a = row.get("away_odd")
                    parts = []
                    if h:
                        parts.append(f"1 {float(h):.2f}")
                    if d:
                        parts.append(f"X {float(d):.2f}")
                    if a:
                        parts.append(f"2 {float(a):.2f}")
                    if parts:
                        return " · ".join(parts)
            except (TypeError, ValueError):
                pass
    odds = row.get("odds") or {}
    if isinstance(odds, dict):
        parts = []
        for label, k in (("1", "home"), ("X", "draw"), ("2", "away")):
            v = odds.get(k)
            if v is not None:
                try:
                    if float(v) >= 1.01:
                        parts.append(f"{label} {float(v):.2f}")
                except (TypeError, ValueError):
                    pass
        if parts:
            return " · ".join(parts)
    return "—"


def _match_html(row: dict[str, Any], *, quote: str) -> str:
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
        f'<div class="fbb-row-foot">'
        f'<span class="fbb-quote">Quote: {html.escape(quote)}</span>'
        f"</div></div>"
    )


def _render_analysis_panel(detail: dict[str, Any]) -> None:
    card = detail.get("card") or {}
    home = html.escape(str(card.get("home") or detail.get("summary", {}).get("home") or "Heim"))
    away = html.escape(str(card.get("away") or detail.get("summary", {}).get("away") or "Auswärts"))

    if detail.get("error"):
        st.markdown(
            f'<div class="fbb-analysis"><p class="fbb-analysis-empty">'
            f'{html.escape(str(detail["error"]))}</p></div>',
            unsafe_allow_html=True,
        )
        return

    if not detail.get("analysis_available"):
        st.markdown(
            '<div class="fbb-analysis"><p class="fbb-analysis-empty">'
            "Analyse für dieses Spiel aktuell nicht verfügbar."
            "</p></div>",
            unsafe_allow_html=True,
        )
        return

    pred = detail.get("prediction_insights") or {}
    odds = detail.get("odds") or {}
    form = detail.get("form") or {}
    home_inj = detail.get("home_injuries") or []
    away_inj = detail.get("away_injuries") or []

    hp, dp, ap = pred.get("home_pct"), pred.get("draw_pct"), pred.get("away_pct")
    if hp is not None:
        win_txt = f"Heim {hp:.0f}% · X {dp or 0:.0f}% · Auswärts {ap or 0:.0f}%"
    else:
        win_txt = "—"

    h_odd, d_odd, a_odd = odds.get("home"), odds.get("draw"), odds.get("away")
    if h_odd and d_odd and a_odd:
        quote_txt = f"1 {float(h_odd):.2f} · X {float(d_odd):.2f} · 2 {float(a_odd):.2f}"
    else:
        quote_txt = "—"

    value_txt = "—"
    advice = str(pred.get("advice") or "").strip()
    if advice:
        value_txt = advice[:120]
    elif pred.get("winner_comment"):
        value_txt = str(pred["winner_comment"])[:120]

    fh = form.get("home") or pred.get("form_home") or "—"
    fa = form.get("away") or pred.get("form_away") or "—"
    form_txt = f"{fh} · {fa}"

    inj_parts = []
    if home_inj:
        inj_parts.append(f"Heim: {len(home_inj)}")
    if away_inj:
        inj_parts.append(f"Auswärts: {len(away_inj)}")
    inj_txt = " · ".join(inj_parts) if inj_parts else "—"

    rec_txt = advice if advice else "—"

    st.markdown(
        f"""
<div class="fbb-analysis">
  <h3>Analyse · {home} vs {away}</h3>
  <div class="fbb-analysis-grid">
    <div class="fbb-stat"><div class="lbl">Siegchance</div><div class="val">{html.escape(win_txt)}</div></div>
    <div class="fbb-stat"><div class="lbl">Quote</div><div class="val">{html.escape(quote_txt)}</div></div>
    <div class="fbb-stat"><div class="lbl">Value / Tendenz</div><div class="val">{html.escape(value_txt)}</div></div>
    <div class="fbb-stat"><div class="lbl">Form</div><div class="val">{html.escape(form_txt)}</div></div>
    <div class="fbb-stat"><div class="lbl">Verletzungen</div><div class="val">{html.escape(inj_txt)}</div></div>
    <div class="fbb-stat"><div class="lbl">Empfehlung</div><div class="val">{html.escape(rec_txt)}</div></div>
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
    _inject_css()
    st.markdown('<div class="fbb-root">', unsafe_allow_html=True)
    st.markdown('<h1 class="fbb-title">Football AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="fbb-sub">Topspiele = Premium-Ligen · Alle Spiele = kuratierte API-Liste (max. 50)</p>',
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
    if "fb_selected_fixture" not in st.session_state:
        st.session_state.fb_selected_fixture = None
    if st.session_state.get("fb_ver") != 7:
        st.session_state.fb_ver = 7
        st.session_state.fb_payload = None
        st.session_state.fb_detail = None

    mode = str(st.session_state.fb_mode or "premium")
    time_f = str(st.session_state.fb_time or "heute")

    rc = st.columns([1, 8])
    with rc[0]:
        if st.button("↻", key="fbb_refresh", help="Aktualisieren"):
            st.session_state.fb_payload = None
            st.session_state.fb_detail = None
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
        st.session_state.fb_detail = None
        st.session_state.fb_selected_fixture = None
        st.rerun()
    mode = str(st.session_state.fb_mode)
    time_f = str(st.session_state.fb_time)

    need_raw = mode == "raw"
    if st.session_state.fb_payload is None or (
        need_raw and not (st.session_state.fb_payload or {}).get("raw_today")
    ):
        with st.spinner("Spiele laden…"):
            try:
                st.session_state.fb_payload = fetch_board_payload(
                    service,
                    username=username,
                    include_live=(time_f == "live") or need_raw,
                    include_raw=need_raw,
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
    is_empty_topspiele = mode == "premium" and not rows

    if banner and not is_empty_topspiele:
        st.markdown(f'<p class="fbb-note">{html.escape(banner)}</p>', unsafe_allow_html=True)

    if not rows:
        st.markdown(
            f'<div class="fbb-empty"><p>{html.escape(banner or "Keine Spiele.")}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    selected = st.session_state.get("fb_selected_fixture")
    for row in rows:
        fid = row.get("fixture_id")
        quote = _format_quote(row)
        col_main, col_btn = st.columns([6, 1])
        with col_main:
            st.markdown(_match_html(row, quote=quote), unsafe_allow_html=True)
        with col_btn:
            can_analyse = bool(fid) and rank >= 1
            if st.button(
                "Analyse",
                key=f"fbb_analyse_{fid or id(row)}",
                disabled=not can_analyse,
                use_container_width=True,
            ):
                st.session_state.fb_selected_fixture = int(fid)
                st.session_state.fb_detail = None
                st.rerun()

    if selected:
        cache_key = f"{selected}|{session_plan}"
        detail = st.session_state.get("fb_detail")
        if not isinstance(detail, dict) or detail.get("_cache_key") != cache_key:
            with st.spinner("Analyse laden…"):
                detail = fetch_match_detail(
                    service,
                    int(selected),
                    username=username,
                    session_plan=session_plan,
                )
                detail["_cache_key"] = cache_key
                st.session_state.fb_detail = detail
        _render_analysis_panel(detail or {})

    st.markdown("</div>", unsafe_allow_html=True)
