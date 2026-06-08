"""MaByte Dashboard — workspace home (HTML-first, nav via ?nav=)."""
from __future__ import annotations

import html

import streamlit as st

from config import PLANS
from database import recent_activity
from ui.components import format_num
from ui.styles import inject_css

_MODULES = (
    ("chat", "AI Chat", "Fragen stellen und Ideen entwickeln.", "chat"),
    ("image", "Image", "Bilder mit AI erstellen.", "image"),
    ("video", "Video", "Shorts und Videos produzieren.", "video"),
    ("music", "Music", "Musik und Audio generieren.", "music"),
    ("coding", "Code", "Code schreiben und verbessern.", "coding"),
    ("automation_lab", "Content", "Posts planen und veröffentlichen.", "automation_lab"),
)

_MODULE_ICONS: dict[str, str] = {
    "chat": "💬",
    "image": "🖼",
    "video": "🎬",
    "music": "🎵",
    "coding": "⌨",
    "automation_lab": "✦",
}

_DASH_CSS = """
.stApp:has(.mb-dash) section.main .block-container {
    max-width: var(--mb-content-max) !important;
}
.mb-dash {
    display: flex;
    flex-direction: column;
    gap: var(--mb-gap-section, 20px);
}
.mb-dash-top {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
}
.mb-dash-greet h1 {
    margin: 0;
    font-size: clamp(24px, 2.8vw, 30px);
    font-weight: 800;
    color: #fafafa !important;
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.mb-dash-greet p {
    margin: 6px 0 0;
    font-size: 13px;
    color: #94a3b8 !important;
    line-height: 1.5;
    max-width: 480px;
}
.mb-dash-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.35);
    color: #e9d5ff !important;
    font-size: 12px;
    font-weight: 600;
}
.mb-dash-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--mb-gap-card, 12px);
}
@media (max-width: 720px) {
    .mb-dash-stats { grid-template-columns: 1fr; }
}
.mb-dash-stat {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.mb-dash-stat .k {
    font-size: var(--mb-label-size, 10px);
    font-weight: var(--mb-label-weight, 700);
    letter-spacing: var(--mb-label-spacing, 0.12em);
    text-transform: uppercase;
    color: #71717a !important;
}
.mb-dash-stat .v {
    margin-top: 5px;
    font-size: 20px;
    font-weight: 800;
    color: #fafafa !important;
    line-height: 1.2;
}
.mb-dash-stat .v.sm {
    font-size: 15px;
    font-weight: 700;
}
.mb-dash-stat .h {
    margin-top: 4px;
    font-size: 11px;
    color: #64748b !important;
}
.mb-dash-label {
    font-size: var(--mb-label-size, 10px);
    font-weight: var(--mb-label-weight, 700);
    letter-spacing: var(--mb-label-spacing, 0.12em);
    text-transform: uppercase;
    color: var(--mb-label-color, #a78bfa) !important;
    margin: 0 0 var(--mb-gap-card, 12px);
}
.mb-dash-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--mb-gap-card, 12px);
}
@media (max-width: 900px) {
    .mb-dash-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 520px) {
    .mb-dash-grid { grid-template-columns: 1fr; }
}
.mb-dash-tile {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 18px 16px;
    min-height: 118px;
    border-radius: 16px;
    text-decoration: none !important;
    background: linear-gradient(155deg, rgba(30, 30, 36, 0.95), rgba(15, 15, 18, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.25);
    transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
}
.mb-dash-tile:hover {
    border-color: rgba(139, 92, 246, 0.45);
    transform: translateY(-2px);
    box-shadow: 0 12px 36px rgba(124, 58, 237, 0.12);
}
.mb-dash-tile .ico {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    background: rgba(124, 58, 237, 0.18);
    border: 1px solid rgba(139, 92, 246, 0.25);
}
.mb-dash-tile .t {
    font-size: 15px;
    font-weight: 700;
    color: #f4f4f5 !important;
}
.mb-dash-tile .d {
    font-size: 12px;
    color: #94a3b8 !important;
    line-height: 1.45;
}
.mb-dash-row2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--mb-gap-card, 12px);
}
@media (max-width: 520px) {
    .mb-dash-row2 { grid-template-columns: 1fr; }
}
.mb-dash-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-radius: 14px;
    text-decoration: none !important;
    background: rgba(24, 24, 27, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #e4e4e7 !important;
    font-size: 14px;
    font-weight: 600;
    transition: border-color 0.12s ease, background 0.12s ease;
}
.mb-dash-link:hover {
    border-color: rgba(139, 92, 246, 0.35);
    background: rgba(124, 58, 237, 0.08);
}
.mb-dash-link span {
    color: #a1a1aa !important;
    font-size: 12px;
    font-weight: 500;
}
"""


def _inject_css() -> None:
    inject_css(_DASH_CSS)


def _activity_snippet(username: str) -> str:
    items = recent_activity(username=username, limit=1) or []
    if not items:
        return "Noch keine Aktivität"
    row = items[0]
    tool = str(row.get("tool", "system")).replace("_", " ").title()
    when = str(row.get("created_at", ""))[:16]
    return f"{tool} · {when}" if when else tool


def _tiles_html() -> str:
    parts: list[str] = []
    for page, title, desc, _ in _MODULES:
        icon = _MODULE_ICONS.get(page, "•")
        parts.append(
            f'<a class="mb-dash-tile" href="?nav={html.escape(page)}">'
            f'<span class="ico">{html.escape(icon)}</span>'
            f'<span class="t">{html.escape(title)}</span>'
            f'<span class="d">{html.escape(desc)}</span></a>'
        )
    return "".join(parts)


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

    _inject_css()

    st.markdown(
        f"""
<div class="mb-dash">
  <div class="mb-dash-top">
    <div class="mb-dash-greet">
      <h1>Hallo, {html.escape(user)}</h1>
      <p>Wähle einen Bereich — alles startet von hier.</p>
    </div>
  </div>

  <div class="mb-dash-stats">
    <div class="mb-dash-stat">
      <div class="k">Tokens</div>
      <div class="v">{html.escape(format_num(tokens))}</div>
      <div class="h">Verfügbares Guthaben</div>
    </div>
    <div class="mb-dash-stat">
      <div class="k">Plan</div>
      <div class="v">{html.escape(plan_label)}</div>
      <div class="h">MaByte Abonnement</div>
    </div>
    <div class="mb-dash-stat">
      <div class="k">Letzte Aktivität</div>
      <div class="v sm">{html.escape(activity)}</div>
      <div class="h">Zuletzt im Workspace</div>
    </div>
  </div>

  <div>
    <div class="mb-dash-label">Workspace</div>
    <div class="mb-dash-grid">{_tiles_html()}</div>
  </div>

  <div>
    <div class="mb-dash-label">Account</div>
    <div class="mb-dash-row2">
      <a class="mb-dash-link" href="?nav=dashboard">Profil <span>→</span></a>
      <a class="mb-dash-link" href="?nav=premium">Premium <span>→</span></a>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
