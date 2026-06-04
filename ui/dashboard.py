"""MaByte home dashboard — minimal SaaS workspace overview."""
from __future__ import annotations

import html

import streamlit as st

from config import PLANS
from database import recent_activity
from ui.components import format_num, nav
from ui.styles import inject_css, page_layout_css

_TOPBAR = 64
_ACCENT = "#8b5cf6"

_HOME_CSS = f"""
.stApp:has(.mb-home) section.main .block-container {{
    max-width: 960px !important;
    padding-top: {_TOPBAR}px !important;
    padding-bottom: 48px !important;
}}
.mb-home-hero {{
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 8px;
    background:
        radial-gradient(ellipse 70% 50% at 100% 0%, rgba(139, 92, 246, 0.18), transparent 55%),
        linear-gradient(145deg, #12121a 0%, #0d0d12 100%);
    border: 1px solid rgba(139, 92, 246, 0.22);
}}
.mb-home-kicker {{
    color: {_ACCENT} !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}}
.mb-home-hero h1 {{
    color: #fafafa !important;
    font-size: clamp(22px, 3vw, 28px);
    font-weight: 800;
    margin: 8px 0 0 0;
    line-height: 1.2;
}}
.mb-home-hero p {{
    color: #94a3b8 !important;
    font-size: 14px;
    margin: 8px 0 0 0;
    max-width: 640px;
    line-height: 1.5;
}}
.mb-home-section {{
    color: #c4b5fd !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 18px 0 10px 0;
}}
.mb-home-cards {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 8px;
}}
@media (max-width: 768px) {{
    .mb-home-cards {{ grid-template-columns: 1fr; }}
}}
.mb-home-card {{
    border-radius: 14px;
    padding: 16px 18px;
    background: rgba(24, 24, 27, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
}}
.mb-home-card .lbl {{
    color: #94a3b8 !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
.mb-home-card .val {{
    color: #fafafa !important;
    font-size: 22px;
    font-weight: 800;
    margin-top: 6px;
    line-height: 1.2;
}}
.mb-home-card .hint {{
    color: #64748b !important;
    font-size: 12px;
    margin-top: 4px;
    line-height: 1.4;
}}
"""


def _inject_css() -> None:
    inject_css(page_layout_css(960, _TOPBAR, 40) + _HOME_CSS)


def _activity_snippet(username: str) -> str:
    items = recent_activity(username=username, limit=1) or []
    if not items:
        return "Noch keine Aktivität"
    row = items[0]
    tool = str(row.get("tool", "system")).replace("_", " ").title()
    when = str(row.get("created_at", ""))[:16]
    return f"{tool} · {when}" if when else tool


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

    st.markdown('<div class="mb-home" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_css()

    st.markdown(
        f"""
<div class="mb-home-hero">
  <div class="mb-home-kicker">Workspace</div>
  <h1>Willkommen zurück, {html.escape(user)}</h1>
  <p>Dein MaByte Workspace für AI, Creator Tools und Football Intelligence.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mb-home-section">Quick Actions</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Football AI", key="home_qa_football", type="primary", use_container_width=True):
            nav("football")
    with c2:
        if st.button("AI Chat", key="home_qa_chat", use_container_width=True):
            nav("chat")
    with c3:
        if st.button("Creator", key="home_qa_creator", use_container_width=True):
            st.session_state.creator_format = "Shorts"
            nav("video")
    with c4:
        if st.button("Content", key="home_qa_content", use_container_width=True):
            nav("automation_lab")
    with c5:
        if st.button("Elite", key="home_qa_elite", use_container_width=True):
            nav("premium")

    activity = _activity_snippet(user)
    cards_html = f"""
<div class="mb-home-cards">
  <div class="mb-home-card">
    <div class="lbl">Tokens</div>
    <div class="val">{html.escape(format_num(tokens))}</div>
    <div class="hint">Verfügbares Guthaben</div>
  </div>
  <div class="mb-home-card">
    <div class="lbl">Plan</div>
    <div class="val">{html.escape(plan_label)}</div>
    <div class="hint">MaByte Abonnement</div>
  </div>
  <div class="mb-home-card">
    <div class="lbl">Letzte Aktivität</div>
    <div class="val" style="font-size:15px;font-weight:700">{html.escape(activity)}</div>
    <div class="hint">Zuletzt im Workspace</div>
  </div>
</div>
"""
    st.markdown(cards_html, unsafe_allow_html=True)
