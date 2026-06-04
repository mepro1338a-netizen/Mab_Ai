"""MaByte home dashboard — SaaS workspace overview."""
from __future__ import annotations

import html

import streamlit as st

from config import PLANS
from database import recent_activity
from ui.components import format_num, nav
from ui.styles import inject_css, page_layout_css

_ACCENT = "#8b5cf6"

_HOME_CSS = """
.stApp:has(.mb-home) section.main .block-container {
    max-width: 1040px !important;
    padding-bottom: 56px !important;
}
.mb-home-hero {
    border-radius: 20px;
    padding: 28px 30px;
    margin: 0 0 28px 0;
    background:
        radial-gradient(ellipse 80% 60% at 100% 0%, rgba(139, 92, 246, 0.2), transparent 58%),
        linear-gradient(155deg, rgba(24, 24, 27, 0.95) 0%, rgba(9, 9, 11, 0.98) 100%);
    border: 1px solid rgba(139, 92, 246, 0.24);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}
.mb-home-kicker {
    color: #a78bfa !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.mb-home-hero h1 {
    color: #fafafa !important;
    font-size: clamp(24px, 3.2vw, 32px);
    font-weight: 800;
    margin: 10px 0 0 0;
    line-height: 1.15;
    letter-spacing: -0.03em;
}
.mb-home-hero p {
    color: #94a3b8 !important;
    font-size: 15px;
    margin: 10px 0 0 0;
    max-width: 560px;
    line-height: 1.55;
}
.mb-home-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 32px;
}
@media (max-width: 768px) {
    .mb-home-stats { grid-template-columns: 1fr; }
}
.mb-home-stat {
    border-radius: 16px;
    padding: 18px 20px;
    background: rgba(24, 24, 27, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
}
.mb-home-stat .lbl {
    color: #71717a !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.mb-home-stat .val {
    color: #fafafa !important;
    font-size: 24px;
    font-weight: 800;
    margin-top: 8px;
    line-height: 1.2;
}
.mb-home-stat .hint {
    color: #64748b !important;
    font-size: 12px;
    margin-top: 6px;
}
.mb-home-section {
    color: #c4b5fd !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 14px 0;
}
.mb-home-qa {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 8px;
}
@media (max-width: 900px) {
    .mb-home-qa { grid-template-columns: repeat(2, 1fr); }
}
.stApp:has(.mb-home) .mb-home-qa .stButton > button {
    height: 52px !important;
    min-height: 52px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    background: rgba(24, 24, 27, 0.9) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
.stApp:has(.mb-home) .mb-home-qa .stButton > button:hover {
    border-color: rgba(139, 92, 246, 0.45) !important;
    background: rgba(124, 58, 237, 0.12) !important;
}
.stApp:has(.mb-home) .mb-home-qa .st-key-home_qa_chat .stButton > button {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.35), rgba(99, 102, 241, 0.25)) !important;
    border-color: rgba(139, 92, 246, 0.5) !important;
    color: #fafafa !important;
}
"""


def _inject_css() -> None:
    inject_css(page_layout_css(1040, 0, 48) + _HOME_CSS)


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
  <p>AI Chat, Creator Studio und Content Automation — alles an einem Ort.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    activity = _activity_snippet(user)
    st.markdown(
        f"""
<div class="mb-home-stats">
  <div class="mb-home-stat">
    <div class="lbl">Tokens</div>
    <div class="val">{html.escape(format_num(tokens))}</div>
    <div class="hint">Verfügbares Guthaben</div>
  </div>
  <div class="mb-home-stat">
    <div class="lbl">Plan</div>
    <div class="val">{html.escape(plan_label)}</div>
    <div class="hint">MaByte Abonnement</div>
  </div>
  <div class="mb-home-stat">
    <div class="lbl">Letzte Aktivität</div>
    <div class="val" style="font-size:16px;font-weight:700">{html.escape(activity)}</div>
    <div class="hint">Zuletzt im Workspace</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mb-home-section">Schnellzugriff</div>', unsafe_allow_html=True)
    st.markdown('<div class="mb-home-qa">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("AI Chat", key="home_qa_chat", type="primary", use_container_width=True):
            nav("chat")
    with c2:
        if st.button("Video", key="home_qa_video", use_container_width=True):
            st.session_state.creator_format = "Shorts"
            nav("video")
    with c3:
        if st.button("Content", key="home_qa_content", use_container_width=True):
            nav("automation_lab")
    with c4:
        if st.button("Elite", key="home_qa_elite", use_container_width=True):
            nav("premium")
    st.markdown("</div>", unsafe_allow_html=True)
