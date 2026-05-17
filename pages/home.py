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
    padding-bottom: 90px !important;
}

.mb-home-hero {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.18), transparent 32%),
        radial-gradient(circle at top left, rgba(59,130,246,.16), transparent 34%),
        linear-gradient(135deg, rgba(10,22,45,.96), rgba(7,12,24,.98));
    border: 1px solid rgba(96,165,250,.18);
    border-radius: 30px;
    padding: 34px;
    margin-bottom: 24px;
    box-shadow:
        0 0 40px rgba(59,130,246,.08),
        0 24px 60px rgba(0,0,0,.34);
}

.mb-kicker {
    color: #60a5fa !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.mb-title {
    color: #ffe7a3 !important;
    font-size: 54px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -2.2px;
}

.mb-subtitle {
    margin-top: 14px;
    max-width: 720px;
    color: #cbd5e1 !important;
    font-size: 16px;
    line-height: 1.5;
}

.mb-badge {
    display: inline-flex;
    padding: 8px 15px;
    border-radius: 999px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 1000;
    box-shadow: 0 0 24px rgba(59,130,246,.28);
    margin-left: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,.08), transparent 30%),
        linear-gradient(145deg, rgba(9,19,36,.96), rgba(7,11,22,.98)) !important;
    border: 1px solid rgba(96,165,250,.10) !important;
    border-radius: 24px !important;
    box-shadow:
        0 0 24px rgba(59,130,246,.05),
        0 16px 42px rgba(0,0,0,.24) !important;
}

[data-testid="metric-container"] {
    background:
        linear-gradient(145deg, rgba(9,19,36,.96), rgba(7,11,22,.98)) !important;
    border: 1px solid rgba(96,165,250,.10) !important;
    border-radius: 22px !important;
    padding: 20px !important;
    box-shadow: 0 14px 34px rgba(0,0,0,.22) !important;
}

[data-testid="metric-container"] label {
    color: #60a5fa !important;
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
    background:
        linear-gradient(135deg, rgba(29,78,216,.22), rgba(91,33,182,.22)) !important;
    border: 1px solid rgba(96,165,250,.22) !important;
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
    box-shadow: 0 10px 24px rgba(0,0,0,.18) !important;
}

.stButton > button:hover {
    border-color: rgba(255,255,255,.20) !important;
    background:
        linear-gradient(135deg, rgba(59,130,246,.30), rgba(168,85,247,.28)) !important;
    box-shadow: 0 0 24px rgba(59,130,246,.18) !important;
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
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.4;
}

.mb-section-title {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    margin-bottom: 12px;
}

.mb-activity-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 1000;
}

.mb-activity-sub {
    color: #94a3b8 !important;
    font-size: 13px;
}

.mb-side-title {
    color: #ffe7a3 !important;
    font-size: 19px;
    font-weight: 1000;
}

.mb-side-sub {
    color: #cbd5e1 !important;
    font-size: 14px;
    line-height: 1.45;
}

.mb-elite-title {
    color: #ffe7a3 !important;
    font-size: 30px;
    font-weight: 1000;
}

.mb-elite-sub {
    color: #cbd5e1 !important;
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


def app_card(icon: str, title: str, sub: str, page: str, key: str) -> None:
    with st.container(border=True):
        render_icon(icon, 42)
        st.markdown(
            f'<div class="mb-card-title">{title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="mb-card-sub">{sub}</div>',
            unsafe_allow_html=True,
        )
        st.write("")

        if st.button("Open", key=key, width="stretch"):
            open_page(page)


def side_card(title: str, sub: str) -> None:
    with st.container(border=True):
        st.markdown(
            f'<div class="mb-side-title">{title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="mb-side-sub">{sub}</div>',
            unsafe_allow_html=True,
        )


def render_activity(user: str) -> None:
    items = recent_activity(username=user, limit=4)

    if not items:
        items = [
            {"tool": "AI Assistant", "created_at": "vor 2 Min"},
            {"tool": "Automation", "created_at": "vor 8 Min"},
            {"tool": "Projects", "created_at": "vor 14 Min"},
        ]

    for index, item in enumerate(items):
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
        app_card("chat", "Assistant", "Chat, Strategie, Coding", "chat", "home_open_chat")

    with c2:
        app_card("projects", "Projects", "Workspace Memory", "projects", "home_open_projects")

    with c3:
        app_card(
            "automations",
            "Automation",
            "AI Workflows",
            "automation_lab",
            "home_open_automation",
        )

    with c4:
        app_card("football", "Football", "Matchday Engine", "football", "home_open_football")

    with c5:
        app_card("video", "Media", "Creator Tools", "video", "home_open_media")

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