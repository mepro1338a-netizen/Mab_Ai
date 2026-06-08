"""MaByte Home — professional dashboard with full-width hero and workspace hub."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from config import PLANS
from database import recent_activity
from ui.components import format_num
from ui.styles import inject_css
from ui_core import img_base64

_ROOT = Path(__file__).resolve().parent.parent
_HEADER_CANDIDATES = (
    _ROOT / "assets" / "headerslogan.png",
    _ROOT / "assets" / "sloganheader.png",
    _ROOT / "sloganheader.png",
)

_QUICK_ACTIONS: list[tuple[str, str, str, str]] = [
    ("chat", "AI Chat", "Fragen & Ideen", "💬"),
    ("image", "Image", "Bilder erstellen", "🖼"),
    ("video", "Video", "Shorts & Clips", "🎬"),
    ("football", "Football", "Analysen & Tipps", "⚽"),
    ("automation_lab", "Automation", "Content planen", "✦"),
    ("coding", "Code", "Entwickeln & fixen", "⌨"),
]

NEWS_ITEMS: list[tuple[str, str, str]] = [
    ("02. Jun", "Dashboard neu", "Home mit Slogan-Header und kompaktem News-Feed."),
    ("30. Mai", "Elite Plan", "Erweiterte Limits und Premium-Features live."),
    ("28. Mai", "Workspace", "Image, Video und Automation vereint."),
]

_DASH_CSS = """
.stApp:has(.mb-dash) section.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}
.mb-dash {
    display: flex;
    flex-direction: column;
}
.mb-dash-hero {
    width: 100%;
    height: clamp(96px, 12vw, 132px);
    overflow: hidden;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: #050816;
}
.mb-dash-hero img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
}
.mb-dash-body {
    max-width: var(--mb-content-max, 1100px);
    margin: 0 auto;
    padding: 22px var(--mb-content-pad-x, 1.5rem) 48px;
    width: 100%;
    box-sizing: border-box;
}
.mb-dash-top {
    margin-bottom: 18px;
}
.mb-dash-top h1 {
    margin: 0;
    font-size: clamp(22px, 2.6vw, 28px);
    font-weight: 800;
    color: #fafafa !important;
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.mb-dash-top p {
    margin: 6px 0 0;
    font-size: 13px;
    color: #71717a !important;
    line-height: 1.5;
}
.mb-dash-kpis {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--mb-gap-card, 12px);
    margin-bottom: 22px;
}
@media (max-width: 720px) {
    .mb-dash-kpis { grid-template-columns: 1fr; }
}
.mb-dash-kpi {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.mb-dash-kpi .k {
    font-size: var(--mb-label-size, 10px);
    font-weight: var(--mb-label-weight, 700);
    letter-spacing: var(--mb-label-spacing, 0.12em);
    text-transform: uppercase;
    color: #71717a !important;
}
.mb-dash-kpi .v {
    margin-top: 5px;
    font-size: 20px;
    font-weight: 800;
    color: #fafafa !important;
    line-height: 1.2;
}
.mb-dash-kpi .v.sm {
    font-size: 14px;
    font-weight: 700;
}
.mb-dash-kpi .h {
    margin-top: 4px;
    font-size: 11px;
    color: #52525b !important;
}
.mb-dash-main {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 260px;
    gap: 20px;
    align-items: start;
}
@media (max-width: 900px) {
    .mb-dash-main { grid-template-columns: 1fr; }
}
.mb-dash-label {
    font-size: var(--mb-label-size, 10px);
    font-weight: var(--mb-label-weight, 700);
    letter-spacing: var(--mb-label-spacing, 0.12em);
    text-transform: uppercase;
    color: var(--mb-label-color, #a78bfa) !important;
    margin: 0 0 var(--mb-gap-card, 12px);
}
.mb-dash-label-muted {
    color: #52525b !important;
    font-weight: 600;
}
.mb-dash-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--mb-gap-card, 12px);
}
@media (max-width: 720px) {
    .mb-dash-actions { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
    .mb-dash-actions { grid-template-columns: 1fr; }
}
.mb-dash-action {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 14px 14px;
    min-height: 96px;
    border-radius: 12px;
    text-decoration: none !important;
    background: linear-gradient(155deg, rgba(28, 28, 32, 0.96), rgba(12, 12, 15, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: border-color 0.12s ease, transform 0.12s ease, box-shadow 0.12s ease;
}
.mb-dash-action:hover {
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.1);
}
.mb-dash-action .ico {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    background: rgba(124, 58, 237, 0.16);
    border: 1px solid rgba(139, 92, 246, 0.22);
}
.mb-dash-action .t {
    font-size: 14px;
    font-weight: 700;
    color: #f4f4f5 !important;
}
.mb-dash-action .d {
    font-size: 11px;
    color: #71717a !important;
    line-height: 1.35;
}
.mb-dash-aside {
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.mb-dash-updates {
    padding: 12px 12px 10px;
    border-radius: 12px;
    background: rgba(18, 18, 20, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.mb-dash-updates ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.mb-dash-updates li {
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.mb-dash-updates li:last-child {
    padding-bottom: 0;
    border-bottom: none;
}
.mb-dash-updates .u-date {
    font-size: 10px;
    color: #52525b !important;
}
.mb-dash-updates .u-title {
    display: block;
    margin-top: 2px;
    font-size: 12px;
    font-weight: 600;
    color: #a1a1aa !important;
    line-height: 1.35;
}
.mb-dash-links {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.mb-dash-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    border-radius: 10px;
    text-decoration: none !important;
    font-size: 12px;
    font-weight: 600;
    color: #d4d4d8 !important;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: border-color 0.12s ease, background 0.12s ease;
}
.mb-dash-link:hover {
    border-color: rgba(139, 92, 246, 0.25);
    background: rgba(124, 58, 237, 0.06);
}
.mb-dash-link span {
    color: #52525b !important;
    font-size: 11px;
}
@media (max-width: 768px) {
    .mb-dash-body { padding-bottom: 32px; }
}
"""


def _header_path() -> Path | None:
    for path in _HEADER_CANDIDATES:
        if path.is_file():
            return path
    return None


def _header_html() -> str:
    path = _header_path()
    if not path:
        return ""
    b64 = img_base64(path)
    if not b64:
        return ""
    return (
        f'<div class="mb-dash-hero">'
        f'<img src="data:image/png;base64,{b64}" alt="MaByte — One system. Infinite intelligence." />'
        f"</div>"
    )


def _activity_snippet(username: str) -> str:
    items = recent_activity(username=username, limit=1) or []
    if not items:
        return "Noch keine Aktivität"
    row = items[0]
    tool = str(row.get("tool", "system")).replace("_", " ").title()
    when = str(row.get("created_at", ""))[:16]
    return f"{tool} · {when}" if when else tool


def _actions_html() -> str:
    parts: list[str] = []
    for page, title, desc, icon in _QUICK_ACTIONS:
        parts.append(
            f'<a class="mb-dash-action" href="?nav={html.escape(page)}">'
            f'<span class="ico">{html.escape(icon)}</span>'
            f'<span class="t">{html.escape(title)}</span>'
            f'<span class="d">{html.escape(desc)}</span></a>'
        )
    return "".join(parts)


def _updates_html() -> str:
    rows: list[str] = []
    for date, title, _text in NEWS_ITEMS[:2]:
        rows.append(
            f"<li>"
            f'<span class="u-date">{html.escape(date)}</span>'
            f'<span class="u-title">{html.escape(title)}</span>'
            f"</li>"
        )
    return (
        f'<div class="mb-dash-updates">'
        f'<p class="mb-dash-label mb-dash-label-muted">Updates</p>'
        f'<ul>{"".join(rows)}</ul>'
        f"</div>"
    )


def _dash_page_html(*, user: str, tokens: str, plan_label: str, activity: str) -> str:
    return (
        '<div class="mb-dash">'
        + _header_html()
        + '<div class="mb-dash-body">'
        + '<header class="mb-dash-top">'
        + f"<h1>Hallo, {html.escape(user)}</h1>"
        + "<p>Dein Workspace — Status, Tools und kurze Updates.</p>"
        + "</header>"
        + '<div class="mb-dash-kpis">'
        + '<div class="mb-dash-kpi"><div class="k">Tokens</div>'
        + f'<div class="v">{html.escape(tokens)}</div>'
        + '<div class="h">Verfügbares Guthaben</div></div>'
        + '<div class="mb-dash-kpi"><div class="k">Plan</div>'
        + f'<div class="v">{html.escape(plan_label)}</div>'
        + '<div class="h">MaByte Abonnement</div></div>'
        + '<div class="mb-dash-kpi"><div class="k">Letzte Aktivität</div>'
        + f'<div class="v sm">{html.escape(activity)}</div>'
        + '<div class="h">Zuletzt im Workspace</div></div>'
        + "</div>"
        + '<div class="mb-dash-main">'
        + "<section>"
        + '<p class="mb-dash-label">Workspace</p>'
        + f'<div class="mb-dash-actions">{_actions_html()}</div>'
        + "</section>"
        + f'<aside class="mb-dash-aside">{_updates_html()}'
        + "<div>"
        + '<p class="mb-dash-label mb-dash-label-muted">Account</p>'
        + '<div class="mb-dash-links">'
        + '<a class="mb-dash-link" href="?nav=dashboard">Profil <span>→</span></a>'
        + '<a class="mb-dash-link" href="?nav=premium">Premium <span>→</span></a>'
        + "</div></div></aside></div></div></div>"
    )


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = str(st.session_state.get("user") or "User")
    plan_key = str(st.session_state.get("plan") or "free")
    plan = PLANS.get(plan_key, PLANS["free"])
    plan_label = str(plan.get("label", plan_key))
    tokens = int(st.session_state.get("tokens", 0) or 0)
    activity = _activity_snippet(user)

    inject_css(_DASH_CSS)
    st.markdown(
        _dash_page_html(
            user=user,
            tokens=format_num(tokens),
            plan_label=plan_label,
            activity=activity,
        ),
        unsafe_allow_html=True,
    )
