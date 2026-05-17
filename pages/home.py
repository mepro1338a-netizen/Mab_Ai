import html

import streamlit as st

from database import (
    recent_activity,
    successful_jobs_count,
    workspace_activity_score,
)

from config import PLANS


def open_page(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def safe_text(value) -> str:
    return html.escape(str(value or ""))


def format_number(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


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
        radial-gradient(circle at top right, rgba(168,85,247,.18), transparent 32%),
        radial-gradient(circle at bottom left, rgba(56,189,248,.08), transparent 35%),
        linear-gradient(135deg, rgba(15,10,34,.88), rgba(6,7,18,.98));
    border: 1px solid rgba(168,85,247,.26);
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

.mb-title-row {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}

.mb-title {
    color: #ffe7a3 !important;
    font-size: 56px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -2.4px;
}

.mb-plan {
    padding: 8px 15px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 1000;
    box-shadow: 0 0 24px rgba(168,85,247,.30);
}

.mb-subtitle {
    margin-top: 14px;
    max-width: 720px;
    color: #c7d2fe !important;
    font-size: 16px;
    line-height: 1.5;
}

.mb-app-card {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.90), rgba(6,7,18,.98));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 24px;
    padding: 20px;
    min-height: 178px;
    box-shadow: 0 16px 42px rgba(0,0,0,.22);
}

.mb-app-icon {
    width: 46px;
    height: 46px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(168,85,247,.16);
    border: 1px solid rgba(255,231,163,.14);
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.mb-app-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 1000;
    margin-bottom: 7px;
}

.mb-app-sub {
    color: #aab3c5 !important;
    font-size: 13px;
    line-height: 1.4;
    min-height: 38px;
}

.mb-stat-card {
    background:
        linear-gradient(145deg, rgba(12,13,32,.90), rgba(6,7,18,.98));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 14px 34px rgba(0,0,0,.20);
}

.mb-stat-label {
    color: #c084fc !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mb-stat-value {
    color: #ffe7a3 !important;
    font-size: 34px;
    line-height: 1;
    font-weight: 1000;
}

.mb-stat-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    margin-top: 9px;
}

.mb-section-title {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.mb-activity-card,
.mb-side-card {
    background:
        linear-gradient(145deg, rgba(15,10,34,.84), rgba(6,7,18,.98));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 16px 42px rgba(0,0,0,.20);
}

.mb-activity-item {
    padding: 14px;
    border-radius: 17px;
    background: rgba(255,255,255,.035);
    border: 1px solid rgba(255,255,255,.06);
    margin-bottom: 10px;
}

.mb-activity-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
}

.mb-activity-title {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 1000;
}

.mb-activity-time {
    color: #c084fc !important;
    font-size: 12px;
    white-space: nowrap;
}

.mb-activity-sub {
    color: #aab3c5 !important;
    font-size: 13px;
    margin-top: 5px;
}

.mb-side-card {
    margin-bottom: 14px;
}

.mb-side-title {
    color: #ffe7a3 !important;
    font-size: 20px;
    font-weight: 1000;
    margin-bottom: 8px;
}

.mb-side-sub {
    color: #c7d2fe !important;
    font-size: 14px;
    line-height: 1.45;
}

.mb-elite {
    margin-top: 24px;
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.18), transparent 32%),
        linear-gradient(135deg, rgba(30,10,50,.92), rgba(7,7,18,.98));
    border: 1px solid rgba(168,85,247,.22);
    border-radius: 30px;
    padding: 28px;
    box-shadow: 0 22px 54px rgba(0,0,0,.24);
}

.mb-elite-title {
    color: #ffe7a3 !important;
    font-size: 30px;
    font-weight: 1000;
    margin-bottom: 9px;
}

.mb-elite-sub {
    color: #c7d2fe !important;
    font-size: 15px;
    line-height: 1.5;
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

@media(max-width: 1100px) {
    .mb-title {
        font-size: 42px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def app_card(icon: str, title: str, sub: str, page: str) -> None:
    st.markdown(
        f"""
<div class="mb-app-card">
<div class="mb-app-icon">{safe_text(icon)}</div>
<div class="mb-app-title">{safe_text(title)}</div>
<div class="mb-app-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Open", key=f"open_{page}", width="stretch"):
        open_page(page)


def stat_card(title: str, value, sub: str) -> None:
    st.markdown(
        f"""
<div class="mb-stat-card">
<div class="mb-stat-label">{safe_text(title)}</div>
<div class="mb-stat-value">{safe_text(value)}</div>
<div class="mb-stat-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def activity_item(title: str, sub: str, time: str) -> None:
    st.markdown(
        f"""
<div class="mb-activity-item">
<div class="mb-activity-top">
<div class="mb-activity-title">{safe_text(title)}</div>
<div class="mb-activity-time">{safe_text(time)}</div>
</div>
<div class="mb-activity-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def side_card(title: str, sub: str) -> None:
    st.markdown(
        f"""
<div class="mb-side-card">
<div class="mb-side-title">{safe_text(title)}</div>
<div class="mb-side-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_activity(user: str) -> None:
    items = recent_activity(username=user, limit=4)

    if not items:
        demo = [
            ("AI Assistant", "Neue Anfrage verarbeitet", "vor 2 Min"),
            ("Automation", "Workflow bereit", "vor 8 Min"),
            ("Projects", "Workspace aktualisiert", "vor 14 Min"),
        ]

        for title, sub, time in demo:
            activity_item(title, sub, time)

        return

    for item in items:
        tool = str(item.get("tool", "system")).replace("_", " ").title()
        created = str(item.get("created_at", ""))[:16]

        activity_item(
            title=tool,
            sub="Neue Aktivität erkannt",
            time=created,
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
<div class="mb-title-row">
<div class="mb-title">Welcome back, {safe_text(user)}</div>
<div class="mb-plan">{safe_text(plan_label)}</div>
</div>
<div class="mb-subtitle">
Dein AI Operating System für Strategie, Content, Projekte und Automationen.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    a1, a2, a3, a4, a5 = st.columns(5, gap="medium")

    with a1:
        app_card("AI", "Assistant", "Chat, Strategie, Coding", "chat")

    with a2:
        app_card("PR", "Projects", "Workspace Memory", "projects")

    with a3:
        app_card("AU", "Automation", "AI Workflows", "automation_lab")

    with a4:
        app_card("FB", "Football", "Matchday Engine", "football")

    with a5:
        app_card("MD", "Media", "Creator Tools", "video")

    st.write("")

    s1, s2, s3, s4 = st.columns(4, gap="medium")

    with s1:
        stat_card("Tokens", format_number(tokens), "Verfügbar")

    with s2:
        stat_card("Jobs", jobs, "Erfolgreich")

    with s3:
        stat_card("Activity", f"{score}/100", "Workspace Score")

    with s4:
        stat_card("Plan", plan_label, "Aktueller Zugriff")

    st.write("")

    left, right = st.columns([1.45, 1], gap="large")

    with left:
        st.markdown(
            """
<div class="mb-activity-card">
<div class="mb-section-title">Live Activity</div>
""",
            unsafe_allow_html=True,
        )

        render_activity(user)

        st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown(
        f"""
<div class="mb-elite">
<div class="mb-elite-title">MaByte Elite Layer</div>
<div class="mb-elite-sub">
{safe_text(format_number(tokens))} Tokens verfügbar. Dein Workspace ist bereit für größere AI Workflows.
</div>
</div>
""",
        unsafe_allow_html=True,
    )