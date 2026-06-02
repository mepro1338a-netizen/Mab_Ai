"""Minimal Football Betting Board — Tipico-style match list + analysis drawer."""
from __future__ import annotations

import html
import time
from typing import Any

import streamlit as st

from config import football_plan_rank
from services.football_service import usage_summary
from services.football_board import (
    calculate_tip_odds,
    fetch_board_payload,
    fetch_match_detail,
    load_football_matches,
    load_raw_football_matches,
    REGION_FILTERS,
)
from services.football_service import FootballAPIError, get_football_service
from ui.premium_foundation import BETA_GLOBAL_CSS, render_upgrade_card
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css

_BOARD_CSS = """
.fbb-root { max-width: 1180px; margin: 0 auto; }
.fbb-header {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start;
    gap: 12px; padding: 16px 18px; margin-bottom: 12px;
    background: linear-gradient(135deg, rgba(8,12,24,.98), rgba(12,18,36,.96));
    border: 1px solid rgba(255,255,255,.08); border-radius: 14px;
}
.fbb-header h1 { margin: 0; font-size: 22px; color: #f8fafc !important; font-weight: 800; }
.fbb-header .sub { color: #94a3b8 !important; font-size: 13px; margin-top: 4px; }
.fbb-api { color: #64748b !important; font-size: 11px; text-align: right; white-space: nowrap; }
.fbb-filters {
    display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px;
}
.fbb-filter-note { color: #64748b !important; font-size: 11px; margin: -6px 0 12px 0; }
.fbb-fallback-note {
    color: #fde047 !important; font-size: 12px; padding: 8px 12px; margin: 0 0 12px 0;
    background: rgba(234,179,8,.08); border: 1px solid rgba(234,179,8,.22); border-radius: 8px;
}
.fbb-match {
    display: grid;
    grid-template-columns: 1fr minmax(120px, 150px);
    gap: 10px 14px; align-items: center;
    padding: 12px 14px; margin-bottom: 8px;
    background: rgba(15, 23, 42, 0.88);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px;
}
.fbb-match.live { border-color: rgba(34,197,94,.35); box-shadow: inset 3px 0 0 #22c55e; }
.fbb-meta { font-size: 11px; color: #94a3b8 !important; margin-bottom: 6px; }
.fbb-meta strong { color: #e2e8f0 !important; }
.fbb-team { font-size: 14px; font-weight: 700; color: #f1f5f9 !important; }
.fbb-score { font-size: 13px; font-weight: 800; color: #e2e8f0 !important; margin: 4px 0; }
.fbb-quote { font-size: 12px; color: #fbbf24 !important; font-weight: 800; }
.fbb-badge {
    display: inline-block; padding: 3px 8px; border-radius: 6px;
    font-size: 10px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase;
}
.fbb-badge.risk-low { background: rgba(34,197,94,.15); color: #86efac !important; border: 1px solid rgba(34,197,94,.3); }
.fbb-badge.risk-mid { background: rgba(234,179,8,.12); color: #fde047 !important; border: 1px solid rgba(234,179,8,.28); }
.fbb-badge.risk-high { background: rgba(239,68,68,.12); color: #fca5a5 !important; border: 1px solid rgba(239,68,68,.28); }
.fbb-badge.value-yes { background: rgba(34,197,94,.18); color: #4ade80 !important; border: 1px solid rgba(34,197,94,.35); }
.fbb-badge.nobet { background: rgba(239,68,68,.15); color: #f87171 !important; border: 1px solid rgba(239,68,68,.35); }
.fbb-live-strip { font-size: 11px; color: #86efac !important; margin-top: 4px; }
.fbb-panel {
    margin: 14px 0 20px 0; padding: 16px 18px;
    background: rgba(10, 14, 28, 0.96);
    border: 1px solid rgba(168,85,247,.25); border-radius: 14px;
}
.fbb-panel h3 { margin: 0 0 12px 0; color: #e2e8f0 !important; font-size: 16px; }
.fbb-reasons { margin: 8px 0; padding-left: 18px; color: #cbd5e1 !important; font-size: 13px; }
.fbb-inj-row { font-size: 12px; color: #94a3b8 !important; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,.04); }
.fbb-form { font-size: 12px; color: #cbd5e1 !important; }
.fbb-h2h { font-size: 12px; color: #94a3b8 !important; }
.fbb-value-box {
    margin-top: 14px; padding: 12px; border-radius: 10px;
    background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,.08);
}
.fbb-empty {
    color: #94a3b8 !important; font-size: 14px; padding: 28px 20px; text-align: center;
    background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px; margin: 12px 0;
}
.fbb-empty h4 { color: #e2e8f0 !important; margin: 0 0 8px 0; font-size: 16px; }
@media (max-width: 768px) {
    .fbb-match { grid-template-columns: 1fr; }
    .fbb-header h1 { font-size: 18px; }
}
.fbb-root .stButton > button {
    min-height: 34px !important; font-size: 12px !important; font-weight: 700 !important;
    border-radius: 8px !important; padding: 0 12px !important;
}
.fbb-root [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: rgba(30,41,59,.95) !important; color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,.1) !important;
}
"""

_TIME_FILTERS: tuple[tuple[str, str], ...] = (
    ("upcoming", "Nächste Topspiele"),
    ("heute", "Heute"),
    ("live", "Live"),
    ("morgen", "Morgen"),
)


def _filter_user_errors(errors: list[str]) -> list[str]:
    """Hide rate-limit noise when API/cache still delivers data."""
    out: list[str] = []
    for err in errors or []:
        low = str(err).lower()
        if "rate limit" in low:
            continue
        out.append(str(err))
    return out


def _render_empty_state(*, raw_count: int = 0) -> None:
    st.markdown(
        """
<div class="fbb-empty">
  <h4>Keine Topspiele im gewählten Filter.</h4>
  <p>Aktuell keine Spiele im gewählten Filter. Nächste Topspiele werden geladen.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    _ = raw_count


def inject_betting_board_css() -> None:
    inject_css(
        MB_THEME_VARS
        + page_layout_css(1180, 100, 32)
        + BETA_GLOBAL_CSS
        + _BOARD_CSS
    )


def _fmt_odd(val: float | None) -> str:
    if val is None:
        return "—"
    return f"{val:.2f}"


def _fmt_pct(val: float | None) -> str:
    if val is None:
        return "—"
    return f"{int(round(val))}%"


def _risk_class(risk: str) -> str:
    r = (risk or "").lower()
    if "niedrig" in r:
        return "risk-low"
    if "hoch" in r:
        return "risk-high"
    return "risk-mid"


def _live_enrichment_map(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for card in payload.get("live_now_cards") or []:
        fid = card.get("fixture_id")
        if fid:
            try:
                out[int(fid)] = card
            except (TypeError, ValueError):
                pass
    return out


def _apply_live_enrichment(row: dict[str, Any], enriched: dict[int, dict[str, Any]]) -> None:
    fid = row.get("fixture_id")
    if not fid:
        return
    try:
        extra = enriched.get(int(fid))
    except (TypeError, ValueError):
        return
    if not extra:
        return
    card = row.get("card") or {}
    for key in ("red_cards", "live_xg", "live_possession", "live_shots", "minute", "score", "status_label"):
        if extra.get(key) is not None:
            card[key] = extra[key]
    row["card"] = card
    if extra.get("red_cards", {}).get("total"):
        row["live_event"] = f"Rote Karten: {extra['red_cards']['total']}"
    if extra.get("live_xg"):
        row["momentum"] = f"xG {extra['live_xg']}"


def _render_match_row_html(row: dict[str, Any]) -> str:
    card = row.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    league = html.escape(str(card.get("league") or ""))
    country = html.escape(str(card.get("country") or ""))
    live = bool(card.get("live"))
    fx_date = html.escape(str(card.get("date") or ""))
    time_lbl = html.escape(str(card.get("time") or ""))
    score = html.escape(str(card.get("score") or "vs"))
    meta = " · ".join([x for x in [league, country, (time_lbl or fx_date)] if x])

    live_cls = " live" if live else ""
    ho, do, ao = row.get("home_odd"), row.get("draw_odd"), row.get("away_odd")
    quote = "—"
    if ho and do and ao:
        quote = f"{_fmt_odd(ho)} · {_fmt_odd(do)} · {_fmt_odd(ao)}"
    return f"""
<div class="fbb-match{live_cls}">
  <div>
    <div class="fbb-meta">{html.escape(meta)}</div>
    <div class="fbb-team">{home}</div>
    <div class="fbb-score">{score}</div>
    <div class="fbb-team">{away}</div>
    <div class="fbb-quote" style="margin-top:8px">Quote: {html.escape(quote)}</div>
  </div>
</div>
"""


def _render_filter_bar(*, time_filter: str, region_filter: str) -> tuple[str, str]:
    st.markdown('<div class="fbb-filters">', unsafe_allow_html=True)
    cols = st.columns(len(_TIME_FILTERS))
    new_time = time_filter
    for col, (key, label) in zip(cols, _TIME_FILTERS):
        with col:
            if st.button(
                label,
                key=f"fbb_tf_{key}",
                type="primary" if time_filter == key else "secondary",
                width="stretch",
            ):
                new_time = key
    cols2 = st.columns(len(REGION_FILTERS))
    new_region = region_filter
    for col, (key, label) in zip(cols2, REGION_FILTERS):
        with col:
            if st.button(
                label,
                key=f"fbb_rf_{key}",
                type="primary" if region_filter == key else "secondary",
                width="stretch",
            ):
                new_region = key
    st.markdown("</div>", unsafe_allow_html=True)
    return new_time, new_region


def _render_injuries_compact(inj: dict[str, Any]) -> None:
    rows: list[str] = []
    for side_label, side_key in (("Heim", "home"), ("Auswärts", "away")):
        for item in (inj.get(side_key) or [])[:5]:
            if isinstance(item, dict):
                player = html.escape(str(item.get("player") or "Spieler"))
                pos = html.escape(str(item.get("position") or item.get("reason") or "—"))
                impact = html.escape(str(inj.get(f"{side_key}_impact") or "mittel"))
            else:
                player = html.escape(str(item))
                pos = "—"
                impact = "mittel"
            rows.append(
                f'<div class="fbb-inj-row">{player} · {pos} · Impact {impact}</div>'
            )
    if rows:
        st.markdown("".join(rows), unsafe_allow_html=True)
    else:
        st.caption("Keine relevanten Ausfälle bekannt")


def _render_analysis_panel(
    detail: dict[str, Any],
    *,
    row: dict[str, Any] | None,
    username: str,
    session_plan: str,
) -> None:
    card = detail.get("card") or {}

    home = html.escape(str(card.get("home") or ""))
    away = html.escape(str(card.get("away") or ""))
    title = f"{home} vs {away}"

    if not detail.get("analysis_available"):
        st.markdown(f'<div class="fbb-panel"><h3>{title}</h3>', unsafe_allow_html=True)
        st.warning("Analyse nicht verfügbar – zu wenig Daten.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    pred = detail.get("prediction") or {}
    intel = detail.get("intel") or {}
    rec = intel.get("recommendation") or {}

    main_pick = rec.get("main_pick") or pred.get("best_bet") or row.get("ai_pick") if row else pred.get("best_bet")
    conf = rec.get("confidence") or pred.get("best_bet_confidence") or (row.get("confidence") if row else None)
    risk = str(rec.get("risk") or (row.get("risk") if row else "") or "")
    no_bet = bool(pred.get("no_bet") or (row.get("no_bet") if row else False))
    reasons = list(pred.get("reasons") or (row.get("reasons") if row else []) or [])[:3]

    st.markdown(f'<div class="fbb-panel"><h3>{title}</h3>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Haupttipp:** {html.escape(str(main_pick or '—'))}")
    with c2:
        conf_txt = f"{float(conf):.0f}%" if conf is not None else "—"
        st.markdown(f"**Confidence:** {conf_txt}")
    with c3:
        badge = "No Bet" if no_bet else f"Risiko {risk}"
        st.markdown(f"**{badge}**")

    if reasons:
        items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons)
        st.markdown(f'<ul class="fbb-reasons">{items}</ul>', unsafe_allow_html=True)

    inj = detail.get("injuries_parsed") or {}
    st.markdown("**Verletzungen**")
    if inj.get("available") or inj.get("home") or inj.get("away"):
        _render_injuries_compact(inj)
    else:
        st.caption("Keine relevanten Ausfälle bekannt")

    hf = detail.get("home_form") or ""
    af = detail.get("away_form") or ""
    if (hf and str(hf).strip() != "—") or (af and str(af).strip() != "—"):
        st.markdown(
            f'<p class="fbb-form"><strong>Form (5):</strong> {html.escape(str(card.get("home")))} '
            f'{html.escape(str(hf))} · {html.escape(str(card.get("away")))} {html.escape(str(af))}</p>',
            unsafe_allow_html=True,
        )

    h2h = detail.get("h2h") or []
    if h2h:
        lines = []
        for fx in h2h[:5]:
            t = fx.get("teams") or {}
            g = fx.get("goals") or {}
            lines.append(
                f"{(t.get('home') or {}).get('name', '?')} "
                f"{g.get('home')}-{g.get('away')} "
                f"{(t.get('away') or {}).get('name', '?')}"
            )
        st.markdown("**H2H**")
        for line in lines:
            st.markdown(f'<p class="fbb-h2h">{html.escape(line)}</p>', unsafe_allow_html=True)

    st.markdown('<div class="fbb-value-box">', unsafe_allow_html=True)
    st.markdown("**Value Check**")
    default_odd = float(row.get("home_odd") or 2.0) if row and row.get("home_odd") else 2.0
    default_prob = float(conf or 50.0) if conf else 50.0
    quote = st.number_input(
        "Quote (Dezimal)",
        min_value=1.01,
        value=max(1.01, default_odd),
        step=0.01,
        key=f"fbb_vq_{detail.get('fixture_id')}",
    )
    ai_prob = st.number_input(
        "AI Wahrscheinlichkeit %",
        min_value=0.0,
        max_value=100.0,
        value=min(100.0, default_prob),
        step=0.5,
        key=f"fbb_vp_{detail.get('fixture_id')}",
    )
    try:
        vr = calculate_tip_odds(quote, 10.0, ai_prob)
        value_yes = vr.get("is_value_bet")
        val_cls = "value-yes" if value_yes else "risk-mid"
        val_lbl = "Value: Ja" if value_yes else "Value: Nein"
        st.markdown(
            f'<p style="color:#94a3b8;font-size:12px;">Implizit: {vr["implied_probability_pct"]:.1f}% · '
            f'AI: {ai_prob:.1f}% · Edge: {vr["edge_pct"]:+.1f}%</p>'
            f'<span class="fbb-badge {val_cls}">{val_lbl}</span>',
            unsafe_allow_html=True,
        )
    except ValueError as exc:
        st.caption(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_football_betting_board(
    *,
    username: str,
    session_plan: str,
    open_premium,
) -> None:
    inject_betting_board_css()
    st.markdown('<div class="fbb-root">', unsafe_allow_html=True)

    summary = usage_summary(username, session_plan)
    rank = football_plan_rank(session_plan or "none")
    api_line = (
        f"API {summary['api_used']:,}/{summary['api_limit']:,}".replace(",", ".")
        if summary.get("live_api")
        else "API —"
    )

    st.markdown(
        f"""
<div class="fbb-header">
  <div>
    <div class="sub" style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#86efac!important;">Football Intelligence</div>
    <h1>Premium Betting Analysis</h1>
    <div class="sub">Top-Spiele · Quoten · KI-Tipps · Value</div>
  </div>
  <div class="fbb-api">{html.escape(api_line)}<br>{html.escape(str(summary.get('plan_label') or ''))}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if rank < 1 or session_plan in ("none", ""):
        render_upgrade_card(
            "Football Betting Analysis",
            "Premium-Wettanalyse ab Football Starter.",
            "football_starter",
            button_key="fbb_starter",
            on_upgrade=open_premium,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    service = get_football_service()
    if not service.is_configured():
        st.error("FOOTBALL_API_KEY fehlt — Konfiguration in .env erforderlich.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if "fb_board_view" not in st.session_state:
        st.session_state.fb_board_view = "upcoming"
    if "fb_show_raw_all" not in st.session_state:
        st.session_state.fb_show_raw_all = False
    if "fb_board_region" not in st.session_state:
        st.session_state.fb_board_region = "alle"
    if "fb_board_cache" not in st.session_state:
        st.session_state.fb_board_cache = {}
    if "fb_board_payload" not in st.session_state:
        st.session_state.fb_board_payload = None
    _FB_DATA_VERSION = 2
    if st.session_state.get("fb_board_version") != _FB_DATA_VERSION:
        st.session_state.fb_board_version = _FB_DATA_VERSION
        st.session_state.fb_board_payload = None
        st.session_state.fb_board_cache = {}
    if "fb_board_force_no_odds" not in st.session_state:
        st.session_state.fb_board_force_no_odds = False

    force_no_odds = bool(st.session_state.fb_board_force_no_odds)
    time_filter = str(st.session_state.fb_board_view or "upcoming").lower()
    show_raw = bool(st.session_state.fb_show_raw_all)
    region_filter = str(st.session_state.fb_board_region or "alle").lower()

    hdr_cols = st.columns([5, 1])
    with hdr_cols[1]:
        if "fb_board_last_refresh" not in st.session_state:
            st.session_state.fb_board_last_refresh = 0.0
        cooldown_ok = (time.time() - float(st.session_state.fb_board_last_refresh or 0.0)) >= 60.0
        if st.button(
            "↻",
            key="fbb_refresh",
            help="Aktualisieren (Cooldown 60s)",
            width="stretch",
            disabled=not cooldown_ok,
        ):
            st.session_state.fb_board_last_refresh = time.time()
            st.session_state.fb_board_payload = None
            st.session_state.fb_board_cache = {}
            st.session_state.fb_board_force_no_odds = False

    new_time, new_region = _render_filter_bar(time_filter=time_filter, region_filter=region_filter)
    if new_time != time_filter or new_region != region_filter:
        st.session_state.fb_board_view = new_time
        st.session_state.fb_board_region = new_region
        st.session_state.fb_board_force_no_odds = False
        st.session_state.fb_show_raw_all = False
        st.session_state.fb_board_payload = None
        st.rerun()
    time_filter = str(st.session_state.fb_board_view or "upcoming").lower()
    show_raw = bool(st.session_state.fb_show_raw_all)
    region_filter = str(st.session_state.fb_board_region or "alle").lower()

    subtitle = "Top-Ligen · Bundesliga · UEFA · Premier League & mehr"
    st.markdown(
        f'<p class="fbb-filter-note">{html.escape(subtitle)}</p>',
        unsafe_allow_html=True,
    )

    if st.session_state.fb_board_payload is None:
        with st.spinner("Topspiele laden…"):
            try:
                st.session_state.fb_board_payload = fetch_board_payload(
                    service,
                    username=username,
                    include_live=(time_filter == "live"),
                )
            except FootballAPIError as exc:
                msg = str(exc)
                low = msg.lower()
                if "rate limit" in low or getattr(exc, "status_code", None) == 429:
                    st.info("Analyse aktuell nicht verfügbar – API-Limit erreicht.")
                    st.caption(msg)
                else:
                    st.error(msg)
                st.markdown("</div>", unsafe_allow_html=True)
                return

    payload = st.session_state.fb_board_payload or {}
    for err in _filter_user_errors(list(payload.get("errors") or [])):
        low = str(err).lower()
        if "rate limit" in low:
            st.info("Analyse aktuell nicht verfügbar – API-Limit erreicht.")
            st.caption(str(err))
        else:
            st.warning(err)

    cache: dict[int, dict[str, Any]] = st.session_state.fb_board_cache

    if show_raw:
        match_result = load_raw_football_matches(
            payload,
            service,
            username=username,
            session_plan=session_plan,
            mode=time_filter,
            cache=cache,
            max_enrich=48,
        )
    else:
        match_result = load_football_matches(
            payload,
            service,
            username=username,
            session_plan=session_plan,
            mode=time_filter,
            region_filter=region_filter,
            cache=cache,
            max_enrich=24,
        )

    rows = match_result.get("rows") or []
    if match_result.get("banner"):
        st.markdown(
            f'<p class="fbb-fallback-note">{html.escape(str(match_result["banner"]))}</p>',
            unsafe_allow_html=True,
        )

    if not rows:
        stage = str(match_result.get("stage") or "")
        if stage == "live_empty" and time_filter == "live":
            pools = match_result.get("pools") or {}
            if int(pools.get("upcoming") or 0) > 0:
                if st.button("Nächste Topspiele", key="fbb_live_to_upcoming", width="stretch"):
                    st.session_state.fb_board_view = "upcoming"
                    st.session_state.fb_show_raw_all = False
                    st.rerun()
        else:
            _render_empty_state(raw_count=0)
            if not show_raw and int((match_result.get("pools") or {}).get("upcoming") or 0) > 0:
                if st.button("Nächste Topspiele anzeigen", key="fbb_empty_to_upcoming", width="stretch"):
                    st.session_state.fb_board_view = "upcoming"
                    st.session_state.fb_show_raw_all = False
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    enriched_map = _live_enrichment_map(payload) if not show_raw else {}
    for row in rows:
        if not show_raw:
            _apply_live_enrichment(row, enriched_map)

    selected = st.session_state.get("fb_board_analyse")
    for row in rows:
        fid = row.get("fixture_id")
        row_cols = st.columns([12, 1])
        with row_cols[0]:
            st.markdown(_render_match_row_html(row), unsafe_allow_html=True)
        with row_cols[1]:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if show_raw or rank < 2:
                st.button(
                    "Analyse später verfügbar",
                    key=f"fbb_an_{fid}",
                    width="stretch",
                    disabled=True,
                )
            elif st.button("Analyse", key=f"fbb_an_{fid}", width="stretch"):
                st.session_state.fb_board_analyse = fid
                st.rerun()
        if not show_raw and rank >= 2 and selected and fid and int(selected) == int(fid):
            cache_key = f"fbb_detail_{fid}"
            if cache_key not in st.session_state:
                with st.spinner("Analyse laden…"):
                    try:
                        st.session_state[cache_key] = fetch_match_detail(
                            service,
                            int(fid),
                            username=username,
                            session_plan=session_plan,
                        )
                    except Exception as exc:
                        st.session_state[cache_key] = {"error": str(exc), "fixture_id": fid}
            detail = st.session_state.get(cache_key) or {}
            if detail.get("error"):
                msg = str(detail["error"])
                low = msg.lower()
                if "rate limit" in low or "tageslimit" in low:
                    st.info("Analyse aktuell nicht verfügbar – API-Limit erreicht.")
                    st.caption(msg)
                else:
                    st.warning(msg)
            elif not detail.get("analysis_available"):
                st.info("Analyse später verfügbar – Quoten oder Prognose fehlen noch.")
            else:
                _render_analysis_panel(
                    detail,
                    row=row,
                    username=username,
                    session_plan=session_plan,
                )
            if st.button("Schließen", key=f"fbb_close_{fid}"):
                st.session_state.pop("fb_board_analyse", None)
                st.rerun()

    if rank < 2:
        st.caption("Volle Quoten & KI-Tipps ab Football Pro.")

    st.divider()
    raw_lbl = "Premium-Ansicht" if show_raw else "Alle API-Spiele anzeigen"
    if st.button(raw_lbl, key="fbb_toggle_raw", width="stretch"):
        st.session_state.fb_show_raw_all = not show_raw
        st.session_state.fb_board_analyse = None
        st.rerun()
    if show_raw:
        st.caption("Rohdaten: alle heutigen API-Spiele (ohne Premium-Filter).")

    st.markdown("</div>", unsafe_allow_html=True)
