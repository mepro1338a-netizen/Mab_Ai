import html

import streamlit as st

from database import (
    recent_activity,
    successful_jobs_count,
    workspace_activity_score,
)

from config import PLANS


# =========================================================
# NAVIGATION
# =========================================================

def open_page(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# =========================================================
# HELPERS
# =========================================================

def safe_text(value) -> str:
    return html.escape(str(value or ""))


def format_number(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


# =========================================================
# CSS
# =========================================================

def home_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1420px !important;
    padding-top: 96px !important;
    padding-bottom: 36px !important;
}

.mb-hero {
    margin-bottom: 22px;
}

.mb-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #7dd3fc !important;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mb-title-row {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}

.mb-title {
    color: #ffe7a3 !important;
    font-size: 54px;
    line-height: .95;
    font-weight: 950;
    letter-spacing: -2px;
}

.mb-plan-badge {
    display: inline-flex;
    align-items: center;
    padding: 8px 15px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 900;
    box-shadow: 0 0 26px rgba(168,85,247,.22);
}

.mb-subtitle {
    max-width: 760px;
    margin-top: 14px;
    color: #94a3b8 !important;
    font-size: 17px;
    line-height: 1.55;
}

.mb-card {
    height: 100%;
    background: linear-gradient(145deg, rgba(10,24,45,.92), rgba(8,16,30,.97));
    border: 1px solid rgba(255,255,255,.075);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 18px 44px rgba(0,0,0,.18);
}

.mb-app-card {
    min-height: 155px;
    text-align: left;
}

.mb-app-icon {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    margin-bottom: 16px;
    background: rgba(56,189,248,.12);
    border: 1px solid rgba(56,189,248,.18);
    font-size: 24px;
}

.mb-app-title {
    color: #ffffff !important;
    font-size: 18px;
    font-weight: 900;
    letter-spacing: -.02em;
}

.mb-app-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    margin-top: 7px;
    min-height: 36px;
}

.mb-stat-title {
    color: #7dd3fc !important;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 11px;
}

.mb-stat-value {
    color: #ffe7a3 !important;
    font-size: 34px;
    font-weight: 950;
    line-height: 1;
    letter-spacing: -.04em;
}

.mb-stat-sub {
    color: #94a3b8 !important;
    margin-top: 10px;
    font-size: 13px;
}

.mb-section-title {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 950;
    letter-spacing: -.04em;
    margin-bottom: 16px;
}

.mb-activity-item {
    background: rgba(15,23,42,.56);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 12px;
}

.mb-activity-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
}

.mb-activity-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 850;
}

.mb-activity-time {
    color: #94a3b8 !important;
    font-size: 12px;
    white-space: nowrap;
}

.mb-activity-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    margin-top: 6px;
}

.mb-rec-card {
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,.075);
    box-shadow: 0 14px 36px rgba(0,0,0,.15);
}

.mb-rec-blue {
    background: linear-gradient(135deg, rgba(30,64,175,.38), rgba(15,23,42,.95));
}

.mb-rec-purple {
    background: linear-gradient(135deg, rgba(126,34,206,.38), rgba(15,23,42,.95));
}

.mb-rec-cyan {
    background: linear-gradient(135deg, rgba(6,182,212,.25), rgba(15,23,42,.95));
}

.mb-rec-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 950;
    letter-spacing: -.03em;
}

.mb-rec-sub {
    color: #cbd5e1 !important;
    font-size: 14px;
    margin-top: 8px;
    line-height: 1.45;
}

.mb-elite {
    margin-top: 18px;
    background:
        radial-gradient(circle at top right, rgba(56,189,248,.14), transparent 32%),
        linear-gradient(135deg, rgba(88,28,135,.32), rgba(15,23,42,.96));
    border: 1px solid rgba(168,85,247,.20);
    border-radius: 28px;
    padding: 26px;
    box-shadow: 0 22px 55px rgba(0,0,0,.20);
}

.mb-elite-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 28px;
    flex-wrap: wrap;
}

.mb-elite-title {
    color: #ffe7a3 !important;
    font-size: 30px;
    font-weight: 950;
    letter-spacing: -.04em;
}

.mb-elite-sub {
    color: #cbd5e1 !important;
    margin-top: 9px;
    font-size: 14px;
    line-height: 1.5;
}

.mb-elite-stats {
    display: flex;
    gap: 34px;
    flex-wrap: wrap;
}

.mb-elite-num {
    color: #ffffff !important;
    font-size: 23px;
    font-weight: 950;
}

.mb-elite-label {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-top: 3px;
}

@media (max-width: 1200px) {
    .mb-title {
        font-size: 42px;
    }

    .mb-stat-value {
        font-size: 29px;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# COMPONENTS
# =========================================================

def app_card(icon: str, title: str, sub: str, page: str) -> None:
    st.markdown(
        f"""
<div class="mb-card mb-app-card">
    <div class="mb-app-icon">{safe_text(icon)}</div>
    <div class="mb-app-title">{safe_text(title)}</div>
    <div class="mb-app-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Open", key=f"open_{page}", use_container_width=True):
        open_page(page)


def stat_card(title: str, value, sub: str) -> None:
    st.markdown(
        f"""
<div class="mb-card">
    <div class="mb-stat-title">{safe_text(title)}</div>
    <div class="mb-stat-value">{safe_text(value)}</div>
    <div class="mb-stat-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def recommendation_card(title: str, sub: str, variant: str) -> None:
    st.markdown(
        f"""
<div class="mb-rec-card mb-rec-{safe_text(variant)}">
    <div class="mb-rec-title">{safe_text(title)}</div>
    <div class="mb-rec-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def activity_item(title: str, sub: str, time: str) -> None:
    st.markdown(
        f"""
<div class="mb-activity-item">
    <div class="mb-activity-head">
        <div class="mb-activity-title">{safe_text(title)}</div>
        <div class="mb-activity-time">{safe_text(time)}</div>
    </div>
    <div class="mb-activity-sub">{safe_text(sub)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_activity(username: str) -> None:
    items = recent_activity(username=username, limit=4)

    if not items:
        demo = [
            ("💬 AI Assistant", "Neue Anfrage verarbeitet", "vor 2 Min"),
            ("🎨 Image Generation", "Bild erfolgreich generiert", "vor 5 Min"),
            ("📁 Project Update", "Workspace aktualisiert", "vor 9 Min"),
            ("⚡ Automation Trigger", "Workflow ausgeführt", "vor 15 Min"),
        ]

        for title, sub, time in demo:
            activity_item(title, sub, time)

        return

    for item in items:
        tool = str(item.get("tool", "system")).replace("_", " ").title()
        created = str(item.get("created_at", ""))[:16]

        activity_item(
            title=f"⚡ {tool}",
            sub="Neue Aktivität erkannt",
            time=created,
        )


# =========================================================
# MAIN
# =========================================================

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
    activity_score = workspace_activity_score(user)

    st.markdown(
        f"""
<div class="mb-hero">
    <div class="mb-kicker">◆ Mission Control</div>
    <div class="mb-title-row">
        <div class="mb-title">Welcome back, {safe_text(user)}</div>
        <div class="mb-plan-badge">{safe_text(plan_label)}</div>
    </div>
    <div class="mb-subtitle">
        Dein AI Operating System für Strategie, Content, Automationen,
        Projekte und Creator Workflows.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    a1, a2, a3, a4, a5 = st.columns(5, gap="medium")

    with a1:
        app_card("💬", "AI Assistant", "Strategy, Coding & Business", "chat")

    with a2:
        app_card("📁", "Projects", "Workspace Memory", "projects")

    with a3:
        app_card("⚡", "Automations", "AI Workflows", "automation_lab")

    with a4:
        app_card("⚽", "Football AI", "Matchday Engine", "football")

    with a5:
        app_card("🎬", "Media Tools", "Creator Suite", "video")

    st.write("")

    s1, s2, s3, s4 = st.columns(4, gap="medium")

    with s1:
        stat_card("Tokens", format_number(tokens), "Verfügbar")

    with s2:
        stat_card("Jobs", jobs, "Erfolgreich")

    with s3:
        stat_card("Activity", f"{activity_score}/100", "Workspace Score")

    with s4:
        stat_card("Plan", plan_label, "Aktueller Zugriff")

    st.write("")

    left, right = st.columns([1.45, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                """
<div class="mb-section-title">⚡ Live AI Activity</div>
""",
                unsafe_allow_html=True,
            )

            render_activity(user)

            st.button(
                "Alle Aktivitäten anzeigen",
                use_container_width=True,
                key="all_activity",
            )

    with right:
        recommendation_card(
            "Optimize Your Workflow",
            "Erstelle Automationen für wiederkehrende Aufgaben und spare Zeit.",
            "blue",
        )

        recommendation_card(
            "Upgrade auf Elite+",
            "Mehr Tokens, mehr Power und Creator Features.",
            "purple",
        )

        recommendation_card(
            "Project Boost",
            "Mehr Memory für bessere AI Ergebnisse.",
            "cyan",
        )

    st.markdown(
        f"""
<div class="mb-elite">
    <div class="mb-elite-flex">
        <div>
            <div class="mb-elite-title">💎 MaByte Elite Layer</div>
            <div class="mb-elite-sub">
                Dein Workspace ist bereit für größere AI Workflows,
                smartere Projekte und mehr Output pro Session.
            </div>
        </div>

        <div class="mb-elite-stats">
            <div>
                <div class="mb-elite-num">{safe_text(format_number(tokens))}</div>
                <div class="mb-elite-label">Tokens</div>
            </div>

            <div>
                <div class="mb-elite-num">{safe_text(activity_score)}/100</div>
                <div class="mb-elite-label">Activity</div>
            </div>

            <div>
                <div class="mb-elite-num">AI OS</div>
                <div class="mb-elite-label">Mode</div>
            </div>

            <div>
                <div class="mb-elite-num">Priority</div>
                <div class="mb-elite-label">Support</div>
            </div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )