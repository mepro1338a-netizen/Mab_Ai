"""Futuristic Football UI — HTML cards, discovery hub, less Streamlit look."""
from __future__ import annotations

import html
import re
from typing import Any

import streamlit as st

from ui.styles import inject_css

POPULAR_LEAGUES: list[dict[str, Any]] = [
    {"id": 39, "name": "Premier League", "country": "England"},
    {"id": 140, "name": "La Liga", "country": "Spain"},
    {"id": 78, "name": "Bundesliga", "country": "Germany"},
    {"id": 135, "name": "Serie A", "country": "Italy"},
    {"id": 61, "name": "Ligue 1", "country": "France"},
    {"id": 2, "name": "Champions League", "country": "Europe"},
    {"id": 3, "name": "Europa League", "country": "Europe"},
    {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
]

FOOTBALL_UI_CSS = """
.fb-command-hero {
    border-radius: 32px;
    padding: 32px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 92% 8%, rgba(34,197,94,.22), transparent 38%),
        radial-gradient(circle at 6% 0%, rgba(168,85,247,.28), transparent 40%),
        linear-gradient(135deg, rgba(8,14,32,.98), rgba(4,18,14,.96));
    border: 1px solid rgba(134,239,172,.16);
    box-shadow: 0 32px 80px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.06);
}
.fb-command-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 48px,
        rgba(255,255,255,.015) 48px,
        rgba(255,255,255,.015) 49px
    );
    pointer-events: none;
}
.fb-scanline {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .28em;
    text-transform: uppercase;
}
.fb-command-title {
    color: #f0fdf4 !important;
    font-size: 42px;
    font-weight: 1000;
    letter-spacing: -2px;
    line-height: 1;
    margin-top: 10px;
}
.fb-command-sub {
    color: #94a3b8 !important;
    font-size: 15px;
    line-height: 1.6;
    max-width: 720px;
    margin-top: 12px;
}
.fb-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 18px 0 22px 0;
}
@media (max-width: 1100px) {
    .fb-stat-grid { grid-template-columns: repeat(2, 1fr); }
}
.fb-stat-card {
    border-radius: 20px;
    padding: 18px 20px;
    background: linear-gradient(145deg, rgba(12,20,38,.92), rgba(6,12,10,.96));
    border: 1px solid rgba(134,239,172,.14);
    box-shadow: 0 12px 32px rgba(0,0,0,.22);
}
.fb-stat-card .lbl {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.fb-stat-card .val {
    color: #f0fdf4 !important;
    font-size: 26px;
    font-weight: 1000;
    margin-top: 8px;
    letter-spacing: -.5px;
}
.fb-stat-card .hint {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 6px;
}
.fb-panel {
    border-radius: 24px;
    padding: 22px 24px;
    margin-bottom: 18px;
    background: linear-gradient(160deg, rgba(14,18,36,.94), rgba(8,12,22,.98));
    border: 1px solid rgba(168,85,247,.14);
    box-shadow: 0 18px 48px rgba(0,0,0,.26);
}
.fb-panel-title {
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
    margin: 0 0 4px 0;
}
.fb-panel-sub {
    color: #64748b !important;
    font-size: 12px;
    margin: 0 0 16px 0;
}
.fb-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}
.fb-league-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(168,85,247,.22);
    color: #e2e8f0 !important;
    font-size: 12px;
    font-weight: 800;
}
.fb-league-chip small {
    color: #64748b !important;
    font-weight: 700;
}
.fb-fixture-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
    margin-top: 12px;
}
.fb-fixture-card {
    border-radius: 18px;
    padding: 16px 18px;
    background: linear-gradient(145deg, rgba(18,24,44,.9), rgba(10,14,28,.95));
    border: 1px solid rgba(255,255,255,.07);
    transition: border-color .2s;
}
.fb-fixture-card.live {
    border-color: rgba(34,197,94,.45);
    box-shadow: 0 0 24px rgba(34,197,94,.12);
}
.fb-fixture-league {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.fb-fixture-date {
    color: #64748b !important;
    font-size: 11px;
    float: right;
}
.fb-fixture-teams {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 14px;
}
.fb-team {
    flex: 1;
    text-align: center;
    color: #f8fafc !important;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.25;
}
.fb-score {
    flex: 0 0 auto;
    min-width: 64px;
    text-align: center;
    padding: 8px 12px;
    border-radius: 14px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(255,231,163,.12);
    color: #ffe7a3 !important;
    font-size: 20px;
    font-weight: 1000;
}
.fb-status-pill {
    display: inline-block;
    margin-top: 10px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.fb-status-pill.live { background: rgba(34,197,94,.2); color: #86efac !important; }
.fb-status-pill.ns { background: rgba(100,116,139,.2); color: #cbd5e1 !important; }
.fb-status-pill.ft { background: rgba(59,130,246,.18); color: #93c5fd !important; }
.fb-team-pick {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 16px;
    margin-bottom: 8px;
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(255,255,255,.06);
}
.fb-team-pick img {
    width: 36px;
    height: 36px;
    object-fit: contain;
}
.fb-team-pick .name {
    color: #f8fafc !important;
    font-size: 14px;
    font-weight: 900;
}
.fb-team-pick .meta {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 2px;
}
.fb-standings-wrap {
    overflow-x: auto;
    margin-top: 12px;
}
.fb-standings {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.fb-standings th {
    color: #86efac !important;
    text-align: left;
    padding: 10px 8px;
    border-bottom: 1px solid rgba(134,239,172,.2);
    font-weight: 1000;
    letter-spacing: .06em;
    text-transform: uppercase;
    font-size: 10px;
}
.fb-standings td {
    color: #e2e8f0 !important;
    padding: 10px 8px;
    border-bottom: 1px solid rgba(255,255,255,.04);
}
.fb-standings tr:hover td {
    background: rgba(168,85,247,.08);
}
.fb-empty {
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    border: 1px dashed rgba(134,239,172,.2);
    color: #94a3b8 !important;
    font-size: 14px;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: rgba(8,12,24,.6) !important;
    border-radius: 16px !important;
    padding: 6px !important;
    border: 1px solid rgba(168,85,247,.12) !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 900 !important;
    color: #94a3b8 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(22,101,52,.5), rgba(76,29,149,.4)) !important;
    color: #f0fdf4 !important;
}
.fb-page .stTextInput input, .fb-page .stNumberInput input {
    border-radius: 14px !important;
    background: rgba(8,12,24,.85) !important;
    border: 1px solid rgba(134,239,172,.18) !important;
    color: #f8fafc !important;
}
.fb-page .stButton > button {
    border-radius: 14px !important;
    background: linear-gradient(135deg, rgba(22,101,52,.85), rgba(76,29,149,.75)) !important;
    border: 1px solid rgba(134,239,172,.28) !important;
    color: #f0fdf4 !important;
    font-weight: 1000 !important;
}
.fb-page [data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(12,18,32,.9), rgba(6,14,10,.95)) !important;
    border: 1px solid rgba(134,239,172,.14) !important;
    border-radius: 18px !important;
}
.fb-ai-studio {
    border-radius: 26px;
    padding: 22px 24px;
    margin-bottom: 20px;
    background: linear-gradient(160deg, rgba(14,12,32,.94), rgba(8,14,24,.98));
    border: 1px solid rgba(168,85,247,.16);
    box-shadow: 0 20px 50px rgba(0,0,0,.28);
}
.fb-match-banner {
    border-radius: 24px;
    padding: 24px 28px;
    margin: 16px 0 20px 0;
    text-align: center;
    background:
        radial-gradient(circle at 50% 0%, rgba(168,85,247,.22), transparent 55%),
        linear-gradient(135deg, rgba(10,16,36,.96), rgba(6,20,14,.94));
    border: 1px solid rgba(255,231,163,.14);
}
.fb-match-banner .vs {
    color: #64748b !important;
    font-size: 14px;
    font-weight: 1000;
    margin: 0 12px;
}
.fb-match-banner .club {
    color: #f0fdf4 !important;
    font-size: 28px;
    font-weight: 1000;
    letter-spacing: -.5px;
}
.fb-match-banner .meta {
    margin-top: 12px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
}
.fb-module-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}
.fb-module-chip {
    border-radius: 14px;
    padding: 12px 14px;
    background: rgba(12,16,32,.7);
    border: 1px solid rgba(255,255,255,.06);
}
.fb-module-chip .ico {
    font-size: 18px;
    margin-bottom: 4px;
}
.fb-module-chip .nm {
    color: #e2e8f0 !important;
    font-size: 12px;
    font-weight: 900;
}
.fb-content-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin: 16px 0;
}
@media (max-width: 900px) {
    .fb-content-grid { grid-template-columns: 1fr; }
}
.fb-content-card {
    border-radius: 20px;
    padding: 18px 20px;
    background: linear-gradient(145deg, rgba(16,20,40,.92), rgba(10,12,26,.96));
    border: 1px solid rgba(255,255,255,.07);
    min-height: 120px;
}
.fb-content-card.focus {
    border-color: rgba(134,239,172,.35);
    box-shadow: 0 0 32px rgba(34,197,94,.1);
    grid-column: 1 / -1;
}
.fb-content-card .head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.fb-content-card .tag {
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
    padding: 4px 8px;
    border-radius: 8px;
    color: #f0fdf4 !important;
}
.fb-content-card .title {
    color: #ffe7a3 !important;
    font-size: 15px;
    font-weight: 1000;
}
.fb-content-card .body {
    color: #cbd5e1 !important;
    font-size: 13px;
    line-height: 1.65;
    max-height: 280px;
    overflow-y: auto;
}
.fb-content-card.focus .body {
    max-height: none;
    font-size: 14px;
}
.fb-viral-panel {
    display: flex;
    gap: 24px;
    align-items: center;
    flex-wrap: wrap;
    border-radius: 22px;
    padding: 22px 26px;
    margin: 18px 0;
    background: linear-gradient(135deg, rgba(22,16,48,.9), rgba(8,20,16,.92));
    border: 1px solid rgba(168,85,247,.2);
}
.fb-viral-ring-wrap {
    position: relative;
    width: 128px;
    height: 128px;
    flex-shrink: 0;
}
.fb-viral-ring {
    width: 128px;
    height: 128px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 40px rgba(34,197,94,.15);
}
.fb-viral-ring .inner {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    background: rgba(8,12,24,.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.fb-viral-ring .score {
    color: #86efac !important;
    font-size: 32px;
    font-weight: 1000;
    line-height: 1;
}
.fb-viral-ring .lbl {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: 4px;
}
.fb-viral-feedback {
    flex: 1;
    min-width: 220px;
}
.fb-viral-feedback h4 {
    color: #ffe7a3 !important;
    margin: 0 0 10px 0;
    font-size: 16px;
    font-weight: 1000;
}
.fb-viral-feedback .fb-body {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.6;
}
.fb-thumb-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 12px;
    margin-top: 14px;
}
.fb-thumb-card {
    border-radius: 18px;
    padding: 16px 18px;
    background: rgba(12,16,32,.8);
    border: 1px solid rgba(255,231,163,.12);
}
.fb-thumb-card .t {
    color: #ffe7a3 !important;
    font-size: 13px;
    font-weight: 1000;
    margin-bottom: 10px;
}
.fb-thumb-card .b {
    color: #94a3b8 !important;
    font-size: 12px;
    line-height: 1.55;
}
.fb-summary-card {
    border-radius: 22px;
    padding: 24px 28px;
    margin: 16px 0;
    background: linear-gradient(145deg, rgba(12,20,38,.95), rgba(8,16,12,.96));
    border: 1px solid rgba(134,239,172,.2);
}
.fb-summary-card .fb-body {
    color: #e2e8f0 !important;
    font-size: 15px;
    line-height: 1.7;
}
.fb-export-bar {
    border-radius: 18px;
    padding: 16px 20px;
    margin: 12px 0;
    background: rgba(15,23,42,.6);
    border: 1px dashed rgba(168,85,247,.25);
    text-align: center;
}
.fb-export-bar .t {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
"""


def inject_football_ui_css() -> None:
    inject_css(FOOTBALL_UI_CSS)


def render_command_hero(title: str, subtitle: str, plan_label: str, api_line: str) -> None:
    st.markdown(
        f"""
<div class="fb-command-hero">
    <div class="fb-scanline">Football Intelligence · Live Data Mesh</div>
    <div class="fb-command-title">{html.escape(title)}</div>
    <div class="fb-command-sub">{html.escape(subtitle)}</div>
    <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap;">
        <span class="fb-league-chip">Plan <strong>{html.escape(plan_label)}</strong></span>
        <span class="fb-league-chip">{html.escape(api_line)}</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_row(stats: list[tuple[str, str, str]]) -> None:
    cards = []
    for label, value, hint in stats:
        cards.append(
            f"""
<div class="fb-stat-card">
    <div class="lbl">{html.escape(label)}</div>
    <div class="val">{html.escape(value)}</div>
    <div class="hint">{html.escape(hint)}</div>
</div>
            """
        )
    st.markdown(
        f'<div class="fb-stat-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "") -> None:
    sub = f'<p class="fb-panel-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="fb-panel" style="padding-bottom:8px;margin-bottom:12px;">
    <div class="fb-panel-title">{html.escape(title)}</div>
    {sub}
</div>
        """,
        unsafe_allow_html=True,
    )


def parse_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    teams = fixture.get("teams") or {}
    goals = fixture.get("goals") or {}
    meta = fixture.get("fixture") or {}
    league = fixture.get("league") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    status = (meta.get("status") or {}).get("short") or "NS"
    home_goals = goals.get("home")
    away_goals = goals.get("away")
    if home_goals is not None and away_goals is not None:
        score = f"{home_goals} : {away_goals}"
    elif status in ("NS", "TBD"):
        score = "vs"
    else:
        score = status
    date_raw = str(meta.get("date") or "")
    date_show = date_raw[11:16] if "T" in date_raw else date_raw[:10]
    if date_raw and "T" in date_raw:
        date_show = f"{date_raw[:10]} · {date_raw[11:16]}"
    return {
        "fixture_id": meta.get("id"),
        "home": home.get("name") or "Home",
        "away": away.get("name") or "Away",
        "home_logo": home.get("logo") or "",
        "away_logo": away.get("logo") or "",
        "score": score,
        "status": status,
        "league": league.get("name") or "",
        "country": league.get("country") or "",
        "date": date_show,
        "live": status in ("1H", "2H", "HT", "ET", "P", "LIVE"),
    }


def _status_class(status: str) -> str:
    if status in ("1H", "2H", "HT", "ET", "P", "LIVE"):
        return "live"
    if status == "FT":
        return "ft"
    return "ns"


def render_fixture_cards(fixtures: list[dict[str, Any]], *, empty_msg: str = "Keine Spiele geladen.") -> None:
    if not fixtures:
        st.markdown(f'<div class="fb-empty">{html.escape(empty_msg)}</div>', unsafe_allow_html=True)
        return
    cards = []
    for raw in fixtures:
        f = parse_fixture(raw)
        live_cls = " live" if f["live"] else ""
        st_cls = _status_class(f["status"])
        cards.append(
            f"""
<div class="fb-fixture-card{live_cls}">
    <div class="fb-fixture-league">{html.escape(f['league'] or 'Match')}
        <span class="fb-fixture-date">{html.escape(f['date'])}</span>
    </div>
    <div class="fb-fixture-teams">
        <div class="fb-team">{html.escape(f['home'])}</div>
        <div class="fb-score">{html.escape(str(f['score']))}</div>
        <div class="fb-team">{html.escape(f['away'])}</div>
    </div>
    <span class="fb-status-pill {st_cls}">{html.escape(f['status'])}</span>
</div>
            """
        )
    st.markdown(
        f'<div class="fb-fixture-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_team_results(teams: list[dict[str, Any]]) -> None:
    if not teams:
        return
    blocks = []
    for row in teams[:12]:
        team = row.get("team") or {}
        name = team.get("name") or "Team"
        country = row.get("country") or team.get("country") or ""
        logo = team.get("logo") or ""
        tid = team.get("id") or ""
        logo_html = (
            f'<img src="{html.escape(logo)}" alt="" />' if logo else "<div style='width:36px'></div>"
        )
        blocks.append(
            f"""
<div class="fb-team-pick">
    {logo_html}
    <div>
        <div class="name">{html.escape(name)}</div>
        <div class="meta">ID {html.escape(str(tid))} · {html.escape(str(country))}</div>
    </div>
</div>
            """
        )
    st.markdown("".join(blocks), unsafe_allow_html=True)


def render_league_results(leagues: list[dict[str, Any]]) -> None:
    if not leagues:
        return
    chips = []
    for row in leagues[:12]:
        league = row.get("league") or {}
        lid = league.get("id") or ""
        name = league.get("name") or "Liga"
        country = league.get("country") or ""
        chips.append(
            f'<span class="fb-league-chip"><strong>{html.escape(name)}</strong>'
            f' <small>{html.escape(str(country))} · ID {html.escape(str(lid))}</small></span>'
        )
    st.markdown(f'<div class="fb-chip-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_popular_leagues() -> None:
    chips = []
    for lg in POPULAR_LEAGUES:
        chips.append(
            f'<span class="fb-league-chip"><strong>{html.escape(lg["name"])}</strong>'
            f' <small>{html.escape(lg["country"])} · {lg["id"]}</small></span>'
        )
    st.markdown(
        f'<div class="fb-chip-row" title="IDs fuer Standings & Liga-Spiele">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def render_standings_table(standings_payload: list[dict[str, Any]], *, limit: int = 15) -> None:
    if not standings_payload:
        st.markdown('<div class="fb-empty">Keine Tabellendaten.</div>', unsafe_allow_html=True)
        return
    try:
        groups = (standings_payload[0].get("league") or {}).get("standings") or []
        rows = groups[0] if groups else []
    except (IndexError, TypeError, KeyError):
        st.markdown('<div class="fb-empty">Tabellenformat nicht lesbar.</div>', unsafe_allow_html=True)
        return
    if not rows:
        st.markdown('<div class="fb-empty">Leere Tabelle.</div>', unsafe_allow_html=True)
        return

    trs = []
    for entry in rows[:limit]:
        team = (entry.get("team") or {}).get("name") or "—"
        pts = entry.get("points", 0)
        played = (entry.get("all") or {}).get("played", 0)
        rank = entry.get("rank", "")
        trs.append(
            f"<tr><td>{html.escape(str(rank))}</td>"
            f"<td>{html.escape(team)}</td>"
            f"<td>{html.escape(str(played))}</td>"
            f"<td><strong>{html.escape(str(pts))}</strong></td></tr>"
        )
    st.markdown(
        f"""
<div class="fb-standings-wrap">
<table class="fb-standings">
<thead><tr><th>#</th><th>Team</th><th>Sp</th><th>Pkt</th></tr></thead>
<tbody>{"".join(trs)}</tbody>
</table>
</div>
        """,
        unsafe_allow_html=True,
    )


# --- AI Content Engine ---

PACKAGE_MODULES: list[dict[str, str]] = [
    {"title": "TikTok Hook", "icon": "⚡", "tag": "TikTok", "color": "#fe2c55"},
    {"title": "TikTok Caption", "icon": "🎬", "tag": "TikTok", "color": "#fe2c55"},
    {"title": "Instagram Caption", "icon": "📸", "tag": "Instagram", "color": "#e1306c"},
    {"title": "Twitter Thread", "icon": "𝕏", "tag": "X", "color": "#38bdf8"},
    {"title": "YouTube Title", "icon": "▶", "tag": "YouTube", "color": "#ef4444"},
    {"title": "YouTube Description", "icon": "📝", "tag": "YouTube", "color": "#ef4444"},
    {"title": "Thumbnail Prompt", "icon": "🖼", "tag": "Visual", "color": "#a855f7"},
    {"title": "Hashtags", "icon": "#", "tag": "Reach", "color": "#22c55e"},
    {"title": "CTA", "icon": "🎯", "tag": "Convert", "color": "#f59e0b"},
    {"title": "Posting Strategy", "icon": "📅", "tag": "Strategy", "color": "#6366f1"},
]

_MODULE_LOOKUP = {m["title"]: m for m in PACKAGE_MODULES}


def rich_text_html(text: str, *, max_len: int | None = None) -> str:
    raw = (text or "").strip()
    if not raw:
        return '<span style="color:#64748b">Kein Inhalt generiert.</span>'
    if max_len and len(raw) > max_len:
        raw = raw[: max_len - 1].rsplit(" ", 1)[0] + "…"
    escaped = html.escape(raw)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return escaped.replace("\n\n", "<br><br>").replace("\n", "<br>")


def split_markdown_sections(text: str) -> dict[str, str]:
    """Split AI output by ## headers (thumbnails etc.)."""
    sections: dict[str, str] = {}
    current_title = "Overview"
    current_lines: list[str] = []

    for line in (text or "").splitlines():
        if line.strip().startswith("##"):
            if current_lines:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line.strip().lstrip("#").strip() or "Section"
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_title] = "\n".join(current_lines).strip()
    if not sections and text:
        sections["Overview"] = text.strip()
    return sections


def render_ai_module_preview() -> None:
    chips = []
    for mod in PACKAGE_MODULES:
        chips.append(
            f'<div class="fb-module-chip">'
            f'<div class="ico">{html.escape(mod["icon"])}</div>'
            f'<div class="nm">{html.escape(mod["title"])}</div></div>'
        )
    st.markdown(
        f"""
<div class="fb-panel-title" style="margin-bottom:12px;">Content Matrix</div>
<p class="fb-panel-sub">10+ Module pro Matchday Package</p>
<div class="fb-module-grid">{"".join(chips)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_match_banner(
    club: str,
    opponent: str,
    platform: str,
    tone: str,
    *,
    badge: str = "Matchday Package",
) -> None:
    st.markdown(
        f"""
<div class="fb-match-banner">
    <div class="fb-scanline">{html.escape(badge)}</div>
    <div style="margin-top:14px;">
        <span class="club">{html.escape(club)}</span>
        <span class="vs">VS</span>
        <span class="club">{html.escape(opponent)}</span>
    </div>
    <div class="meta">
        <span class="fb-league-chip">{html.escape(platform)}</span>
        <span class="fb-league-chip">Tone · <strong>{html.escape(tone)}</strong></span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_output(text: str, club: str, opponent: str) -> None:
    render_match_banner(club, opponent, "Summary", "Starter", badge="AI Match Summary")
    st.markdown(
        f"""
<div class="fb-summary-card">
    <div class="fb-scanline" style="margin-bottom:12px;">Kurzfassung · Starter</div>
    <div class="fb-body">{rich_text_html(text)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _content_card_html(
    title: str,
    body: str,
    *,
    focus: bool = False,
    preview_len: int | None = None,
) -> str:
    meta = _MODULE_LOOKUP.get(title, {"icon": "✦", "tag": "Content", "color": "#a855f7"})
    cls = "fb-content-card focus" if focus else "fb-content-card"
    body_html = rich_text_html(body, max_len=preview_len if not focus else None)
    return f"""
<div class="{cls}">
    <div class="head">
        <span class="tag" style="background:{html.escape(meta['color'])}33;
            border:1px solid {html.escape(meta['color'])}55">{html.escape(meta['tag'])}</span>
        <span class="title">{html.escape(meta['icon'])} {html.escape(title)}</span>
    </div>
    <div class="body">{body_html}</div>
</div>
    """


def render_content_package(
    sections: dict[str, str],
    *,
    key_prefix: str = "fb_pkg",
) -> None:
    filled = {k: v.strip() for k, v in sections.items() if (v or "").strip()}
    if not filled:
        st.markdown('<div class="fb-empty">Keine Inhalte im Package.</div>', unsafe_allow_html=True)
        return

    titles = list(filled.keys())
    default_focus = titles[0]
    focus = st.selectbox(
        "Fokus-Modul",
        titles,
        key=f"{key_prefix}_focus",
        label_visibility="collapsed",
    )

    cards = [_content_card_html(focus, filled[focus], focus=True)]
    for title in titles:
        if title == focus:
            continue
        cards.append(_content_card_html(title, filled[title], preview_len=220))

    st.markdown(f'<div class="fb-content-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="fb-scanline" style="margin:14px 0 8px 0;">Einzeldownloads</div>', unsafe_allow_html=True)
    cols = st.columns(min(3, len(titles)))
    for i, title in enumerate(titles):
        with cols[i % len(cols)]:
            content = filled[title]
            st.download_button(
                f"↓ {title}",
                data=content.encode("utf-8"),
                file_name=f"mabyte_{title.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"{key_prefix}_dl_{title}",
                width="stretch",
            )


def render_viral_intelligence(score: int, feedback: str) -> None:
    score = max(0, min(100, int(score)))
    ring_color = (
        "#22c55e" if score >= 75 else "#eab308" if score >= 50 else "#ef4444"
    )
    st.markdown(
        f"""
<div class="fb-viral-panel">
    <div class="fb-viral-ring-wrap">
        <div class="fb-viral-ring" style="background:conic-gradient(
            {ring_color} {score}%,
            rgba(255,255,255,.08) 0
        );">
            <div class="inner">
                <div class="score">{score}</div>
                <div class="lbl">Viral</div>
            </div>
        </div>
    </div>
    <div class="fb-viral-feedback">
        <h4>Viral Intelligence</h4>
        <div class="fb-body">{rich_text_html(feedback)}</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100.0)


def render_thumbnail_package(text: str) -> None:
    render_section_header("Thumbnail Intelligence", "YouTube · TikTok · Instagram Covers")
    parts = split_markdown_sections(text)
    if len(parts) <= 1 and "Overview" in parts:
        parts = split_markdown_sections(
            text.replace("## YouTube Thumbnail", "\n## YouTube\n").replace(
                "## TikTok Cover", "\n## TikTok\n"
            )
        )
    cards = []
    for title, body in parts.items():
        if not body.strip():
            continue
        cards.append(
            f"""
<div class="fb-thumb-card">
    <div class="t">{html.escape(title)}</div>
    <div class="b">{rich_text_html(body, max_len=600)}</div>
</div>
            """
        )
    if cards:
        st.markdown(f'<div class="fb-thumb-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="fb-summary-card"><div class="fb-body">{rich_text_html(text)}</div></div>',
            unsafe_allow_html=True,
        )


def render_export_bar(title: str = "Full Package Export") -> None:
    st.markdown(
        f"""
<div class="fb-export-bar">
    <div class="t">{html.escape(title)}</div>
    <div style="color:#64748b;font-size:12px;">Komplettes Paket als .txt</div>
</div>
        """,
        unsafe_allow_html=True,
    )
