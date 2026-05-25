"""Modular Football UI — Elite Live Intelligence cards (dark SaaS)."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui.styles import inject_css

FOOTBALL_COMPONENTS_CSS = """
.fb-elite-live { margin-top: 8px; }
.fb-elite-card {
    border-radius: 20px;
    padding: 18px 20px;
    margin-bottom: 14px;
    background: linear-gradient(145deg, rgba(10,18,32,.97), rgba(6,12,8,.98));
    border: 1px solid rgba(134,239,172,.16);
    box-shadow: 0 0 28px rgba(34,197,94,.06);
}
.fb-elite-card.purple { border-color: rgba(168,85,247,.22); }
.fb-elite-card-h {
    color: #86efac !important;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.fb-elite-card-title {
    color: #f0fdf4 !important;
    font-size: 17px;
    font-weight: 900;
    margin: 0 0 10px 0;
}
.fb-elite-score {
    color: #fff !important;
    font-size: 32px;
    font-weight: 1000;
}
.fb-elite-meta { color: #94a3b8 !important; font-size: 12px; margin-top: 6px; }
.fb-elite-bar-row { margin: 8px 0; }
.fb-elite-bar-label {
    display: flex;
    justify-content: space-between;
    color: #cbd5e1 !important;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 4px;
}
.fb-elite-bar-track {
    height: 8px;
    border-radius: 999px;
    background: rgba(15,23,42,.8);
    overflow: hidden;
}
.fb-elite-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #166534, #22c55e);
}
.fb-elite-bar-fill.away { background: linear-gradient(90deg, #4c1d95, #a855f7); }
.fb-elite-reason {
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 8px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
}
.fb-elite-reason .team { color: #4ade80 !important; font-weight: 900; font-size: 13px; }
.fb-elite-reason .txt { color: #e2e8f0 !important; font-size: 12px; margin-top: 4px; }
.fb-elite-reason .conf { color: #64748b !important; font-size: 11px; margin-top: 4px; }
.fb-elite-empty {
    color: #64748b !important;
    font-size: 13px;
    padding: 12px;
    border-radius: 12px;
    border: 1px dashed rgba(255,255,255,.12);
    text-align: center;
}
.fb-elite-event {
    display: flex;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,.06);
    font-size: 12px;
    color: #e2e8f0 !important;
}
.fb-elite-event .min { color: #86efac !important; font-weight: 900; min-width: 36px; }
.fb-elite-disclaimer {
    color: #94a3b8 !important;
    font-size: 11px;
    line-height: 1.45;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(251,191,36,.08);
    border: 1px solid rgba(251,191,36,.2);
    margin-bottom: 14px;
}
.fb-elite-preview-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(168,85,247,.2);
    color: #e9d5ff !important;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 10px;
}
@media (max-width: 640px) { .fb-elite-score { font-size: 26px; } }
"""


def inject_football_components_css() -> None:
    inject_css(FOOTBALL_COMPONENTS_CSS)


def render_elite_disclaimer() -> None:
    st.markdown(
        '<div class="fb-elite-disclaimer">'
        "Keine Wettberatung. MaByte liefert ausschliesslich mathematische und inhaltliche "
        "Live-Analysen fuer Creator und Analysten — keine Garantien, kein Echtgeld-Rat."
        "</div>",
        unsafe_allow_html=True,
    )


def _bar(home_val: float | None, away_val: float | None, label: str) -> str:
    h = float(home_val or 0)
    a = float(away_val or 0)
    total = h + a or 1
    hp = int(h / total * 100)
    return f"""
<div class="fb-elite-bar-row">
  <div class="fb-elite-bar-label"><span>{html.escape(label)} Heim {h:g}</span><span>Auswaerts {a:g}</span></div>
  <div class="fb-elite-bar-track"><div class="fb-elite-bar-fill" style="width:{hp}%"></div></div>
</div>
"""


def render_match_overview_card(overview: dict[str, Any]) -> None:
    mom = overview.get("momentum") or {}
    pulse = "LIVE" if overview.get("is_live") else str(overview.get("status", "NS"))
    elapsed = overview.get("elapsed") or "—"
    st.markdown(
        f"""
<div class="fb-elite-card">
  <div class="fb-elite-card-h">Match Overview</div>
  <div class="fb-elite-card-title">{html.escape(overview.get('home_team',''))} vs {html.escape(overview.get('away_team',''))}</div>
  <div class="fb-elite-score">{html.escape(str(overview.get('scoreline','')))}</div>
  <div class="fb-elite-meta">{html.escape(overview.get('league',''))} · {html.escape(pulse)} · {elapsed}' · Momentum: {html.escape(str(mom.get('label','—')))}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_edge_reasons_card(reasons: list[dict[str, Any]]) -> None:
    inner = ""
    if not reasons:
        inner = '<div class="fb-elite-empty">Noch keine Edge-Signale — Live-Daten laden.</div>'
    else:
        for r in reasons[:5]:
            inner += f"""
<div class="fb-elite-reason">
  <div class="team">{html.escape(str(r.get('team','')))}</div>
  <div class="txt">{html.escape(str(r.get('reason','')))}</div>
  <div class="conf">Confidence: {html.escape(str(r.get('confidence','—')))}%</div>
</div>"""
    st.markdown(
        f'<div class="fb-elite-card"><div class="fb-elite-card-h">Why This Team Has Edge</div>{inner}</div>',
        unsafe_allow_html=True,
    )


def render_injuries_card(injuries: dict[str, list], home: str, away: str) -> None:
    parts = []
    for side, title in (("home", home), ("away", away)):
        rows = injuries.get(side) or []
        if rows:
            parts.append(f"<p><strong>{html.escape(title)}</strong></p><ul>")
            for row in rows[:8]:
                parts.append(
                    f"<li>{html.escape(row.get('player',''))} — {html.escape(row.get('reason',''))}</li>"
                )
            parts.append("</ul>")
    inner = "".join(parts) if parts else (
        '<div class="fb-elite-empty">Keine Verletzungsdaten verfuegbar — API liefert fuer dieses Spiel nichts.</div>'
    )
    st.markdown(
        f'<div class="fb-elite-card"><div class="fb-elite-card-h">Injuries & Missing Players</div>{inner}</motionless>'.replace("motionless", "div"),
        unsafe_allow_html=True,
    )


def render_tactical_card(tactical: dict[str, Any], events: list[dict[str, Any]]) -> None:
    bars = (
        _bar(tactical.get("possession_home"), tactical.get("possession_away"), "Ballbesitz")
        + _bar(tactical.get("shots_on_home"), tactical.get("shots_on_away"), "Schuesse aufs Tor")
        + _bar(tactical.get("corners_home"), tactical.get("corners_away"), "Ecken")
        + _bar(tactical.get("dangerous_home"), tactical.get("dangerous_away"), "Gefaehrliche Angriffe")
    )
    ev_html = ""
    for e in (events or [])[-8:][::-1]:
        minute = e.get("minute", "?")
        ev_html += (
            f'<div class="fb-elite-event"><span class="min">{minute}\'</span>'
            f"<span>{html.escape(e.get('type',''))} · {html.escape(e.get('player',''))} "
            f"({html.escape(e.get('team',''))})</span></div>"
        )
    if not ev_html:
        ev_html = '<div class="fb-elite-empty">Keine Live-Events im Feed.</div>'
    meta = (
        f"Tore: {tactical.get('goals', 0)} · Karten: {tactical.get('cards', 0)} · "
        f"Wechsel: {tactical.get('substitutions', 0)} · Phase: {html.escape(str(tactical.get('danger_phase','')))}"
    )
    st.markdown(
        f"""
<div class="fb-elite-card">
  <div class="fb-elite-card-h">Live Tactical Read</div>
  <div class="fb-elite-meta">{meta}</div>
  {bars}
  <div style="margin-top:12px">{ev_html}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_key_players_card(players: list[dict[str, Any]]) -> None:
    if not players:
        body = '<div class="fb-elite-empty">Key Players nach Lineups/Events — Daten fehlen noch.</div>'
    else:
        body = "<ul>"
        for p in players[:5]:
            body += (
                f"<li><strong>{html.escape(p.get('name',''))}</strong> — "
                f"{html.escape(p.get('impact',''))} · Reel: {html.escape(p.get('reel_potential',''))}</li>"
            )
        body += "</ul>"
    st.markdown(
        f'<div class="fb-elite-card purple"><div class="fb-elite-card-h">Key Player Impact</div>{body}</div>',
        unsafe_allow_html=True,
    )


def render_odds_intel_card(odds: dict[str, Any]) -> None:
    st.markdown(
        f"""
<div class="fb-elite-card warn">
  <div class="fb-elite-card-h">Odds / Value Intelligence</div>
  <div class="fb-elite-meta">Nur Analyse — keine Wettempfehlung</div>
  <div class="fb-elite-reason">
    <div class="team">Implizit: {odds.get('implied_probability_pct', 0):.1f}% · EV: {odds.get('expected_value', 0):+.2f}</div>
    <div class="txt">Edge {odds.get('edge_pct', 0):+.2f}% · {html.escape(str(odds.get('value_label','')))}</div>
    <div class="conf">Risk: {html.escape(str(odds.get('risk_level','')))} · Confidence {odds.get('confidence_pct', 0):.0f}%</div>
  </div>
</div>
        """.replace("motionless", "div"),
        unsafe_allow_html=True,
    )


def render_creator_card(creator: dict[str, str]) -> None:
    fields = [
        ("TikTok Hook", creator.get("tiktok_hook", "")),
        ("Instagram Caption", creator.get("instagram_caption", "")),
        ("YouTube Shorts Title", creator.get("youtube_title", "")),
        ("Voiceover", creator.get("voiceover", "")),
        ("Hashtags", creator.get("hashtags", "")),
        ("Thumbnail", creator.get("thumbnail", "")),
    ]
    body = ""
    for label, val in fields:
        if val:
            body += f"<p><strong>{html.escape(label)}</strong><br>{html.escape(val)}</p>"
    st.markdown(
        f'<div class="fb-elite-card purple"><div class="fb-elite-card-h">Creator Output</div>{body or "<p>—</p>"}</div>',
        unsafe_allow_html=True,
    )


def render_final_read_card(final_read: dict[str, str]) -> None:
    st.markdown(
        f"""
<div class="fb-elite-card">
  <div class="fb-elite-card-h">AI Final Read</div>
  <p><strong>Zusammenfassung</strong><br>{html.escape(final_read.get('summary',''))}</p>
  <p><strong>Als naechstes wahrscheinlich</strong><br>{html.escape(final_read.get('next_likely',''))}</p>
  <p><strong>Best Creator Angle</strong><br>{html.escape(final_read.get('creator_angle',''))}</p>
  <p><strong>Risk Warning</strong><br>{html.escape(final_read.get('risk_warning',''))}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_elite_live_dashboard(bundle: dict[str, Any], *, is_preview: bool = False) -> None:
    st.markdown('<div class="fb-elite-live">', unsafe_allow_html=True)
    render_elite_disclaimer()
    if is_preview:
        st.markdown('<span class="fb-elite-preview-badge">Pro Preview — Elite fuer Vollanalyse</span>', unsafe_allow_html=True)

    overview = bundle.get("overview") or {}
    render_match_overview_card(overview)
    render_edge_reasons_card(bundle.get("edge_reasons") or [])

    if not is_preview:
        home = overview.get("home_team", "Home")
        away = overview.get("away_team", "Away")
        render_injuries_card(bundle.get("injuries") or {}, home, away)
        render_key_players_card(bundle.get("key_players") or [])
        render_odds_intel_card(bundle.get("odds_intel") or {})
        render_creator_card(bundle.get("creator") or {})

    render_tactical_card(bundle.get("tactical") or {}, bundle.get("events") or [])
    render_final_read_card(bundle.get("final_read") or {})

    missing = bundle.get("missing_sections") or []
    if missing:
        st.caption(f"Teilweise Daten: {', '.join(missing)} — Analyse trotzdem moeglich.")

    st.markdown("</div>", unsafe_allow_html=True)
