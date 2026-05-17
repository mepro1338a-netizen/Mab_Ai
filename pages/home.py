from pathlib import Path

import streamlit as st

from database import (
    recent_activity,
    successful_jobs_count,
    workspace_activity_score,
)

from config import PLANS


ASSET_DIR = Path("assets")


def open_page(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def format_number(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


def asset_path(name: str) -> Path:
    return ASSET_DIR / f"{name}.png"


def home_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1320px !important;
    padding-top: 92px !important;
    padding-bottom: 80px !important;
}

.mb-home-hero {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.22), transparent 32%),
        radial-gradient(circle at bottom left, rgba(56,189,248,.10), transparent 34%),
        linear-gradient(135deg, rgba(18,10,38,.94), rgba(6,7,18,.98));
    border: 1px solid rgba(168,85,247,.28);
    border-radius: 30px;
    padding: 34px;
    margin-bottom: 24px;
    box-shadow: 0 24px 60px rgba(0,0,0,.28);
}

.mb-kicker {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.mb-title {
    color: #ffe7a3 !important;
    font-size: 56px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -2.4px;
}

.mb-subtitle {
    margin-top: 14px;
    max-width: 720px;
    color: #c7d2fe !important;
    font-size: 16px;
    line-height: 1.5;
}

.mb-badge {
    display: inline-flex;
    padding: 8px 15px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 1000;
    box-shadow: 0 0 24px rgba(168,85,247,.30);
    margin-left: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.90), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 42px rgba(0,0,0,.22) !important;
}

[data-testid="metric-container"] {
    background:
        linear-gradient(145deg, rgba(12,13,32,.90), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 22px !important;
    padding: 20px !important;
    box-shadow: 0 14px 34px rgba(0,0,0,.20) !important;
}

[data-testid="metric-container"] label {
    color: #c084fc !important;
    font-size: 11px !important;
    font-weight: 1000 !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

.stButton > button {
    width: 100% !important;
    height: 44px !important;
    border-radius: 15px !important;
    background: linear-gradient(135deg, rgba(36,8,56,.98), rgba(12,3,25,.98)) !important;
    border: 1px solid rgba(168,85,247,.30) !important;
    color: #ffe7a3 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
    box-shadow: 0 10px 24px rgba(0,0,0,.20) !important;
}

.stButton > button:hover {
    border-color: rgba(255,231,163,.36) !important;
    box-shadow: 0 0 24px rgba(168,85,247,.28) !important;
    transform: translateY(-1px);
}

.mb-card-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 1000;
    margin-top: 8px;
    margin-bottom: 4px;
}

.mb-card-sub {
    color: #aab3c5 !important;
    font-size: 13px;
    line-height: 1.4;
}

.mb-section-title {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    margin-bottom: 12px;
}

.mb-small-muted {
    color: #94a3b8 !important;
    font-size: 13px;
}

.mb-activity-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 1000;
}

.mb-activity-sub {
    color: #aab3c5 !important;
    font-size: 13px;
}

.mb-side-title {
    color: #ffe7a3 !important;
    font-size: 19px;
    font-weight: 1000;
}

.mb-side-sub {
    color: #c7d2fe !important;
    font-size: 14px;
    line-height: 1.45;
}

.mb-elite-title {
    color: #ffe7a3 !important;
    font-size: 30px;
    font-weight: 1000;
}

.mb-elite-sub {
    color: #c7d2fe !important;
    font-size: 15px;
    line-height: 1.5;
}

@media(max-width: 1100px) {
    .mb-title {
        font-size: 42px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_icon(name: str, width: int = 42) -> None:
    path = asset_path(name)

    if path.exists():
        st.image(str(path), width=width)
    else:
        st.write("")


def app_card(icon: str, title: str, sub: str, page: str) -> None:
    with st.container(border=True):
        render_icon(icon, 42)
        st.markdown(f'<div class="mb-card-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mb-card-sub">{sub}</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Open", key=f"open_{page}", width="stretch"):
            open_page(page)


def side_card(title: str, sub: str) -> None:
    with st.container(border=True):
        st.markdown(f'<div class="mb-side-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mb-side-sub">{sub}</div>', unsafe_allow_html=True)


def render_activity(user: str) -> None:
    items = recent_activity(username=user, limit=4)

    if not items:
        items = [
            {"tool": "AI Assistant", "created_at": "vor 2 Min"},
            {"tool": "Automation", "created_at": "vor 8 Min"},
            {"tool": "Projects", "created_at": "vor 14 Min"},
        ]

    for item in items:
        tool = str(item.get("tool", "system")).replace("_", " ").title()
        created = str(item.get("created_at", ""))[:16]

        with st.container(border=True):
            st.markdown(
                f'<div class="mb-activity-title">{tool}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="mb-activity-sub">Neue Aktivität erkannt · {created}</div>',
                unsafe_allow_html=True,
            )


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    home_css()

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    plan_data = PLANS.get(plan, PLANS["free"])
    plan_label = plan_data.get("label", "Free")

    jobs = successful_jobs_count(user)
    score = workspace_activity_score(user)

    st.markdown(
        f"""
<div class="mb-home-hero">
    <div class="mb-kicker">Mission Control</div>
    <div class="mb-title">
        Welcome back, {user}
        <span class="mb-badge">{plan_label}</span>
    </div>
    <div class="mb-subtitle">
        Dein AI Operating System für Strategie, Content, Projekte und Automationen.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5, gap="medium")

    with c1:
        app_card("chat", "Assistant", "Chat, Strategie, Coding", "chat")

    with c2:
        app_card("projects", "Projects", "Workspace Memory", "projects")

    with c3:
        app_card("automations", "Automation", "AI Workflows", "automation_lab")

    with c4:
        app_card("football", "Football", "Matchday Engine", "football")

    with c5:
        app_card("video", "Media", "Creator Tools", "video")

    st.write("")

    s1, s2, s3, s4 = st.columns(4, gap="medium")

    with s1:
        st.metric("Tokens", format_number(tokens), "Verfügbar")

    with s2:
        st.metric("Jobs", jobs, "Erfolgreich")

    with s3:
        st.metric("Activity", f"{score}/100", "Workspace Score")

    with s4:
        st.metric("Plan", plan_label, "Aktueller Zugriff")

    st.write("")

    left, right = st.columns([1.45, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                '<div class="mb-section-title">Live Activity</div>',
                unsafe_allow_html=True,
            )
            render_activity(user)

    with right:
        side_card(
            "Optimize Workflow",
            "Baue wiederholbare Abläufe für Content, Projekte und Automationen.",
        )

        side_card(
            "Project Boost",
            "Nutze Projektkontext für bessere Antworten und mehr Memory.",
        )

        side_card(
            "Creator Layer",
            "Erstelle schneller Reels, Assets, Ideen und Kampagnen.",
        )

    st.write("")

    with st.container(border=True):
        st.markdown(
            '<div class="mb-elite-title">MaByte Elite Layer</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="mb-elite-sub">{format_number(tokens)} Tokens verfügbar. Dein Workspace ist bereit für größere AI Workflows.</div>',
            unsafe_allow_html=True,
        )