"""MaByte Home — workspace hub with status overview and quick navigation."""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

import streamlit as st

from config import PLANS
from database import recent_activity
from ui.components import format_num, inject_dashboard_css
from ui.sidebar import navigate_to
from ui.styles import inject_css
from ui_core import img_base64

_ROOT = Path(__file__).resolve().parent.parent
_HEADER_CANDIDATES = (
    _ROOT / "assets" / "headerslogan.png",
    _ROOT / "assets" / "sloganheader.png",
    _ROOT / "sloganheader.png",
)

_QUICK_ACTIONS: list[tuple[str, str, str, str]] = [
    ("chat", "AI Chat", "Fragen & Ideen"),
    ("image", "Image", "Bilder erstellen"),
    ("video", "Video", "Shorts & Clips"),
    ("football", "Football", "Analysen & Tipps"),
    ("automation_lab", "Automation", "Content planen"),
    ("coding", "Code", "Entwickeln & fixen"),
]

NEWS_ITEMS: list[tuple[str, str]] = [
    ("02. Jun", "Dashboard überarbeitet — schnellerer Zugriff auf alle Tools."),
    ("30. Mai", "Elite Plan mit erweiterten Limits verfügbar."),
]

_HOME_CSS = """
.stApp:has(.mb-dash) section.main .block-container {
    max-width: var(--mb-content-max, 1100px) !important;
    padding: 0 var(--mb-content-pad-x, 1.5rem) 48px !important;
}
.mb-home-hero {
    margin: 0 calc(-1 * var(--mb-content-pad-x, 1.5rem)) 20px;
    height: clamp(88px, 10vw, 116px);
    overflow: hidden;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: #050816;
}
.mb-home-hero img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
}
.mb-home-head { margin: 0 0 18px; }
.mb-home-greet {
    margin: 0;
    font-size: clamp(22px, 2.8vw, 30px);
    font-weight: 800;
    color: #fafafa !important;
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.mb-home-sub {
    margin: 6px 0 0;
    font-size: 13px;
    color: #71717a !important;
    line-height: 1.5;
    max-width: 520px;
}
.mb-home-kpis {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--mb-gap-card, 12px);
    margin-bottom: 22px;
}
@media (max-width: 720px) {
    .mb-home-kpis { grid-template-columns: 1fr; }
}
.mb-home-kpi {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.mb-home-kpi .k {
    font-size: var(--mb-label-size, 10px);
    font-weight: var(--mb-label-weight, 700);
    letter-spacing: var(--mb-label-spacing, 0.12em);
    text-transform: uppercase;
    color: #71717a !important;
}
.mb-home-kpi .v {
    margin-top: 5px;
    font-size: 20px;
    font-weight: 800;
    color: #fafafa !important;
    line-height: 1.2;
}
.mb-home-kpi .v.sm {
    font-size: 13px;
    font-weight: 700;
}
.mb-home-kpi .h {
    margin-top: 4px;
    font-size: 11px;
    color: #52525b !important;
}
.mb-home-panel {
    padding: 14px;
    border-radius: 12px;
    background: rgba(18, 18, 20, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 12px;
}
.mb-home-panel:last-child { margin-bottom: 0; }
.mb-home-feed {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.mb-home-feed li {
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.mb-home-feed li:last-child {
    padding-bottom: 0;
    border-bottom: none;
}
.mb-home-feed .u-date {
    font-size: 10px;
    color: #52525b !important;
}
.mb-home-feed .u-title {
    display: block;
    margin-top: 2px;
    font-size: 12px;
    color: #a1a1aa !important;
    line-height: 1.4;
}
.mb-home-act {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 8px;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    font-size: 12px;
}
.mb-home-act:last-child { border-bottom: none; padding-bottom: 0; }
.mb-home-act .t { color: #e4e4e7 !important; font-weight: 600; }
.mb-home-act .d { color: #52525b !important; font-size: 11px; white-space: nowrap; }
.mb-home-empty {
    color: #52525b !important;
    font-size: 12px;
    line-height: 1.45;
    margin: 0;
}
.stApp:has(.mb-dash) .st-key-home_main,
.stApp:has(.mb-dash) .st-key-home_aside {
    min-width: 0;
}
.stApp:has(.mb-dash) .st-key-home_main > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"],
.stApp:has(.mb-dash) .st-key-home_aside > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
.stApp:has(.mb-dash) .st-key-home_grid [data-testid="column"] > [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] .stButton,
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] [data-testid="stVerticalBlockBorderWrapper"],
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] [data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
}
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] .stButton > button,
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] button {
    width: 100% !important;
    min-height: 84px !important;
    height: auto !important;
    padding: 12px 14px 12px 52px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    background: linear-gradient(155deg, rgba(28, 28, 32, 0.96), rgba(12, 12, 15, 0.98)) !important;
    color: #71717a !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    box-shadow: none !important;
    white-space: pre-line !important;
    line-height: 1.35 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    position: relative !important;
}
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] .stButton > button::before,
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] button::before {
    position: absolute !important;
    left: 12px !important;
    top: 14px !important;
    width: 30px !important;
    height: 30px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 8px !important;
    background: rgba(124, 58, 237, 0.14) !important;
    border: 1px solid rgba(139, 92, 246, 0.22) !important;
    font-size: 14px !important;
    line-height: 1 !important;
}
.stApp:has(.mb-dash) .st-key-dash_nav_chat button::before { content: "💬" !important; }
.stApp:has(.mb-dash) .st-key-dash_nav_image button::before { content: "🖼" !important; }
.stApp:has(.mb-dash) .st-key-dash_nav_video button::before { content: "🎬" !important; }
.stApp:has(.mb-dash) .st-key-dash_nav_football button::before { content: "⚽" !important; }
.stApp:has(.mb-dash) .st-key-dash_nav_automation_lab button::before { content: "✦" !important; }
.stApp:has(.mb-dash) .st-key-dash_nav_coding button::before { content: "⌨" !important; }
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] .stButton > button:hover,
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] button:hover {
    border-color: rgba(139, 92, 246, 0.38) !important;
    background: linear-gradient(155deg, rgba(34, 30, 46, 0.98), rgba(16, 12, 26, 0.99)) !important;
}
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] .stButton > button p,
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] button p {
    white-space: pre-line !important;
    text-align: left !important;
    font-size: 11px !important;
    line-height: 1.35 !important;
    color: #71717a !important;
}
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] .stButton > button p::first-line,
.stApp:has(.mb-dash) [class*="st-key-dash_nav_"] button p::first-line {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #f4f4f5 !important;
}
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] .stButton > button,
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] button {
    min-height: 38px !important;
    padding: 9px 12px !important;
    font-size: 12px !important;
    white-space: nowrap !important;
}
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] .stButton > button::before,
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] button::before {
    display: none !important;
}
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] .stButton > button p,
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] button p {
    white-space: nowrap !important;
    font-size: 12px !important;
    color: #d4d4d8 !important;
}
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] .stButton > button p::first-line,
.stApp:has(.mb-dash) .st-key-dash_acc [class*="st-key-dash_nav_"] button p::first-line {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #d4d4d8 !important;
}
.stApp:has(.mb-dash) .st-key-dash_acc {
    padding: 14px;
    border-radius: 12px;
    background: rgba(18, 18, 20, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.06);
}
.stApp:has(.mb-dash) .st-key-dash_acc > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    gap: 8px !important;
}
.stApp:has(.mb-dash) .st-key-dash_acc .mb-dash-section,
.stApp:has(.mb-dash) .st-key-dash_acc [data-testid="stMarkdown"]:first-child .mb-dash-section {
    margin-bottom: 10px;
}
"""


def _header_path() -> Path | None:
    for path in _HEADER_CANDIDATES:
        if path.is_file():
            return path
    return None


def _hero_html() -> str:
    path = _header_path()
    if not path:
        return ""
    b64 = img_base64(path)
    if not b64:
        return ""
    return (
        f'<div class="mb-home-hero">'
        f'<img src="data:image/png;base64,{b64}" alt="MaByte" />'
        f"</div>"
    )


def _greeting_name(user: str) -> str:
    hour = datetime.now().hour
    if hour < 12:
        salut = "Guten Morgen"
    elif hour < 18:
        salut = "Guten Tag"
    else:
        salut = "Guten Abend"
    return f"{salut}, {html.escape(user)}"


def _activity_rows(username: str, *, limit: int = 4) -> list[tuple[str, str]]:
    items = recent_activity(username=username, limit=limit) or []
    rows: list[tuple[str, str]] = []
    for row in items:
        tool = str(row.get("tool", "system")).replace("_", " ").title()
        when = str(row.get("created_at", ""))[:16].replace("T", " · ")
        rows.append((tool, when))
    return rows


def _activity_panel_html(username: str) -> str:
    rows = _activity_rows(username)
    if not rows:
        return (
            '<div class="mb-home-panel">'
            '<div class="mb-dash-section">Letzte Aktivität</div>'
            '<p class="mb-home-empty">Noch nichts los — starte mit AI Chat oder einem Creator-Tool.</p>'
            "</div>"
        )
    items = "".join(
        f'<div class="mb-home-act"><span class="t">{html.escape(t)}</span>'
        f'<span class="d">{html.escape(d)}</span></div>'
        for t, d in rows
    )
    return (
        '<div class="mb-home-panel">'
        '<div class="mb-dash-section">Letzte Aktivität</div>'
        f"{items}"
        "</div>"
    )


def _updates_panel_html() -> str:
    rows = "".join(
        f"<li><span class=\"u-date\">{html.escape(date)}</span>"
        f"<span class=\"u-title\">{html.escape(title)}</span></li>"
        for date, title in NEWS_ITEMS
    )
    return (
        '<div class="mb-home-panel">'
        '<div class="mb-dash-section">Neuigkeiten</div>'
        f'<ul class="mb-home-feed">{rows}</ul>'
        "</div>"
    )


def _kpis_html(*, tokens: str, plan_label: str, tier: str, activity: str) -> str:
    return (
        '<div class="mb-home-kpis">'
        '<div class="mb-home-kpi"><div class="k">Tokens</div>'
        f'<div class="v">{html.escape(tokens)}</div>'
        '<div class="h">Verfügbares Guthaben</div></div>'
        '<div class="mb-home-kpi"><div class="k">Plan</div>'
        f'<div class="v">{html.escape(plan_label)}</div>'
        f'<div class="h">{html.escape(tier)}</div></div>'
        '<div class="mb-home-kpi"><div class="k">Zuletzt aktiv</div>'
        f'<div class="v sm">{html.escape(activity)}</div>'
        '<div class="h">Letzter Workspace</div></div>'
        "</div>"
    )


def _dash_nav_key(page: str) -> str:
    return f"dash_nav_{page}"


def _tile_label(title: str, desc: str) -> str:
    return f"{title}\n{desc}"


def _render_workspace_grid() -> None:
    with st.container(key="home_grid"):
        for row_start in range(0, len(_QUICK_ACTIONS), 3):
            cols = st.columns(3, gap="small")
            batch = _QUICK_ACTIONS[row_start : row_start + 3]
            for col, item in zip(cols, batch):
                page, title, desc = item
                with col:
                    if st.button(
                        _tile_label(title, desc),
                        key=_dash_nav_key(page),
                        use_container_width=True,
                        type="tertiary",
                    ):
                        navigate_to(page)


def _render_account_links() -> None:
    with st.container(key="dash_acc"):
        st.markdown('<div class="mb-dash-section">Account</div>', unsafe_allow_html=True)
        if st.button("Profil & Einstellungen", key=_dash_nav_key("dashboard"), use_container_width=True, type="tertiary"):
            navigate_to("dashboard")
        if st.button("Premium upgraden", key=_dash_nav_key("premium"), use_container_width=True, type="tertiary"):
            navigate_to("premium")


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = str(st.session_state.get("user") or "User")
    plan_key = str(st.session_state.get("plan") or "free")
    plan = PLANS.get(plan_key, PLANS["free"])
    plan_label = str(plan.get("label", plan_key))
    tier = str(plan.get("badge", "Starter"))
    tokens = int(st.session_state.get("tokens", 0) or 0)

    activity_rows = _activity_rows(user, limit=1)
    activity = activity_rows[0][0] if activity_rows else "—"

    inject_dashboard_css()
    inject_css(_HOME_CSS)

    st.markdown('<div class="mb-dash" aria-hidden="true"></div>', unsafe_allow_html=True)
    if _hero_html():
        st.markdown(_hero_html(), unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="mb-home-head">
  <h1 class="mb-home-greet">{_greeting_name(user)}</h1>
  <p class="mb-home-sub">Wähle einen Workspace — alles an einem Ort.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        _kpis_html(
            tokens=format_num(tokens),
            plan_label=plan_label,
            tier=tier,
            activity=activity,
        ),
        unsafe_allow_html=True,
    )

    col_main, col_aside = st.columns([1.55, 1], gap="medium")
    with col_main:
        with st.container(key="home_main"):
            st.markdown('<div class="mb-dash-section">Workspace</div>', unsafe_allow_html=True)
            _render_workspace_grid()
    with col_aside:
        with st.container(key="home_aside"):
            st.markdown(_activity_panel_html(user), unsafe_allow_html=True)
            st.markdown(_updates_panel_html(), unsafe_allow_html=True)
            _render_account_links()
