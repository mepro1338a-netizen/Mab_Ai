import streamlit as st
from datetime import datetime

from database import (
    recent_activity,
    total_tokens_used,
    successful_jobs_count,
    failed_jobs_count,
    workspace_activity_score,
    latest_tool_used,
)

from config import PLANS


def open_page(page):
    st.session_state.page = page
    st.rerun()


def home_css():
    st.markdown(
        """
<style>

.main .block-container{
    max-width: 1320px;
    padding-top: 1.8rem;
}

.home-top-actions{
    display:flex;
    justify-content:flex-end;
    gap:12px;
    margin-bottom:20px;
}

.home-icon-btn{
    width:46px;
    height:46px;
    border-radius:14px;
    border:1px solid rgba(125,211,252,.18);
    background:linear-gradient(145deg,rgba(15,23,42,.82),rgba(8,24,55,.75));
    display:flex;
    align-items:center;
    justify-content:center;
    color:#93c5fd;
    font-size:20px;
    box-shadow:0 0 22px rgba(56,189,248,.08);
}

.welcome-small{
    color:#9fb3d1;
    font-size:18px;
    font-weight:650;
    margin-bottom:4px;
}

.welcome-title{
    color:white;
    font-size:42px;
    font-weight:1000;
    letter-spacing:-.04em;
    line-height:1.1;
}

.plan-pill{
    display:inline-block;
    margin-left:12px;
    padding:7px 13px;
    border-radius:999px;
    background:linear-gradient(135deg,rgba(124,58,237,.90),rgba(168,85,247,.75));
    color:white;
    font-size:16px;
    font-weight:950;
    vertical-align:middle;
    box-shadow:0 0 24px rgba(168,85,247,.25);
}

.home-sub{
    color:#cbd5e1;
    font-size:18px;
    font-weight:650;
    margin-top:10px;
    margin-bottom:34px;
}

.quick-grid{
    display:grid;
    grid-template-columns:repeat(5,minmax(0,1fr));
    gap:22px;
    margin-bottom:34px;
}

.quick-card{
    min-height:128px;
    border-radius:22px;
    padding:25px 18px;
    border:1px solid rgba(125,211,252,.16);
    background:
        linear-gradient(145deg,rgba(15,23,42,.86),rgba(12,33,68,.70));
    box-shadow:0 18px 50px rgba(0,0,0,.20);
    text-align:center;
}

.quick-icon{
    font-size:38px;
    margin-bottom:14px;
    filter:drop-shadow(0 0 16px rgba(56,189,248,.25));
}

.quick-title{
    color:white;
    font-size:17px;
    font-weight:900;
}

.stat-grid{
    display:grid;
    grid-template-columns:repeat(5,minmax(0,1fr));
    gap:18px;
    margin-bottom:34px;
}

.stat-card{
    min-height:145px;
    border-radius:22px;
    padding:24px;
    border:1px solid rgba(125,211,252,.13);
    background:
        linear-gradient(145deg,rgba(9,20,44,.90),rgba(10,25,55,.68));
    box-shadow:0 18px 45px rgba(0,0,0,.16);
}

.stat-label{
    color:#9fb3d1;
    font-size:14px;
    font-weight:800;
    margin-bottom:18px;
}

.stat-icon{
    font-size:22px;
    margin-right:8px;
}

.stat-value{
    color:white;
    font-size:31px;
    font-weight:1000;
    letter-spacing:-.03em;
    word-break:break-word;
}

.stat-caption{
    color:#22c55e;
    font-size:14px;
    font-weight:850;
    margin-top:14px;
}

.dashboard-grid{
    display:grid;
    grid-template-columns:1.05fr .95fr;
    gap:24px;
    margin-bottom:34px;
}

.panel{
    border-radius:24px;
    border:1px solid rgba(125,211,252,.14);
    background:
        linear-gradient(145deg,rgba(8,19,45,.90),rgba(10,25,55,.66));
    padding:24px;
    box-shadow:0 20px 60px rgba(0,0,0,.22);
}

.panel-title{
    color:white;
    font-size:24px;
    font-weight:1000;
    margin-bottom:22px;
}

.activity-row{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    padding:16px;
    border-radius:18px;
    border:1px solid rgba(125,211,252,.10);
    background:rgba(15,23,42,.42);
    margin-bottom:12px;
}

.activity-left{
    display:flex;
    gap:14px;
    align-items:center;
}

.activity-icon{
    width:40px;
    height:40px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:rgba(59,130,246,.16);
    color:white;
    font-size:20px;
}

.activity-title{
    color:white;
    font-size:15px;
    font-weight:950;
}

.activity-sub{
    color:#9fb3d1;
    font-size:13px;
    font-weight:650;
}

.activity-time{
    color:#9fb3d1;
    font-size:12px;
    white-space:nowrap;
}

.rec-card{
    border-radius:18px;
    padding:20px;
    margin-bottom:14px;
    border:1px solid rgba(125,211,252,.14);
    background:linear-gradient(135deg,rgba(30,64,175,.24),rgba(15,23,42,.55));
}

.rec-card.purple{
    background:linear-gradient(135deg,rgba(88,28,135,.35),rgba(15,23,42,.55));
    border-color:rgba(168,85,247,.22);
}

.rec-card.cyan{
    background:linear-gradient(135deg,rgba(8,145,178,.30),rgba(15,23,42,.55));
    border-color:rgba(34,211,238,.20);
}

.rec-title{
    color:white;
    font-size:20px;
    font-weight:1000;
    margin-bottom:8px;
}

.rec-text{
    color:#cbd5e1;
    font-size:14px;
    font-weight:650;
    margin-bottom:14px;
}

.rec-button{
    display:inline-block;
    padding:10px 18px;
    border-radius:12px;
    background:linear-gradient(135deg,#2563eb,#38bdf8);
    color:white;
    font-weight:900;
    font-size:14px;
}

.elite-banner{
    display:grid;
    grid-template-columns:90px 1fr 1.4fr 150px;
    align-items:center;
    gap:24px;
    border-radius:24px;
    border:1px solid rgba(168,85,247,.55);
    background:
        radial-gradient(circle at 15% 50%, rgba(168,85,247,.18), transparent 22%),
        linear-gradient(135deg,rgba(15,23,42,.95),rgba(25,20,65,.78));
    padding:26px;
    box-shadow:0 0 45px rgba(168,85,247,.18);
    margin-bottom:30px;
}

.elite-gem{
    width:80px;
    height:80px;
    border-radius:999px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:42px;
    background:rgba(59,130,246,.10);
    border:1px solid rgba(125,211,252,.16);
}

.elite-title{
    color:white;
    font-size:26px;
    font-weight:1000;
}

.elite-badge{
    display:inline-block;
    margin-left:10px;
    padding:6px 12px;
    border-radius:999px;
    color:#86efac;
    background:rgba(34,197,94,.14);
    font-size:13px;
    font-weight:950;
}

.elite-sub{
    color:#cbd5e1;
    font-size:15px;
    font-weight:650;
    margin-top:6px;
}

.elite-stats{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:12px;
    border-left:1px solid rgba(255,255,255,.12);
    border-right:1px solid rgba(255,255,255,.12);
    padding:0 24px;
}

.elite-mini{
    text-align:center;
}

.elite-mini-value{
    color:white;
    font-size:15px;
    font-weight:1000;
}

.elite-mini-label{
    color:#9fb3d1;
    font-size:12px;
    margin-top:4px;
}

.footer{
    text-align:center;
    color:#64748b;
    font-size:13px;
    padding:16px 0;
}

@media(max-width:1050px){
    .quick-grid,
    .stat-grid{
        grid-template-columns:repeat(2,minmax(0,1fr));
    }

    .dashboard-grid,
    .elite-banner{
        grid-template-columns:1fr;
    }

    .elite-stats{
        border:none;
        padding:0;
    }
}

@media(max-width:650px){
    .quick-grid,
    .stat-grid,
    .elite-stats{
        grid-template-columns:1fr;
    }

    .welcome-title{
        font-size:34px;
    }
}

</style>
        """,
        unsafe_allow_html=True,
    )


def icon_for_tool(tool):
    text = str(tool or "").lower()

    if "football" in text:
        return "⚽"

    if "image" in text:
        return "🎨"

    if "video" in text:
        return "🎬"

    if "reels" in text:
        return "📣"

    if "coding" in text:
        return "💻"

    if "music" in text:
        return "🎵"

    if "chat" in text:
        return "💬"

    if "automation" in text:
        return "⚡"

    return "⚡"


def render_quick_card(icon, title, page):
    st.markdown(
        f"""
<div class="quick-card">
    <div class="quick-icon">{icon}</div>
    <div class="quick-title">{title}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Öffnen", key=f"quick_{page}", use_container_width=True):
        open_page(page)


def render_stat_card(icon, label, value, caption, caption_color="#22c55e"):
    st.markdown(
        f"""
<div class="stat-card">
    <div class="stat-label"><span class="stat-icon">{icon}</span>{label}</div>
    <div class="stat-value">{value}</div>
    <div class="stat-caption" style="color:{caption_color};">{caption}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_activity_feed(username):
    activity = recent_activity(username=username, limit=5)

    if not activity:
        rows = [
            ("💬", "AI Assistant", "Neue Anfrage verarbeitet", "vor 2 Min"),
            ("🎨", "Image Generation", "Bild erfolgreich generiert", "vor 5 Min"),
            ("📁", "Project Update", "Projekt aktualisiert", "vor 12 Min"),
            ("🪙", "Tokens Used", "-120 Tokens verbraucht", "vor 15 Min"),
            ("⚡", "Automation Trigger", "Workflow ausgeführt", "vor 18 Min"),
        ]
    else:
        rows = []

        for item in activity:
            tool = str(item.get("tool", "system")).replace("_", " ").title()
            tokens = item.get("cost_tokens", 0)
            status = item.get("status", "success")
            created = str(item.get("created_at", ""))[:16]

            rows.append(
                (
                    icon_for_tool(tool),
                    tool,
                    f"Status: {status} · Tokens: {tokens}",
                    created,
                )
            )

    for icon, title, sub, time in rows:
        st.markdown(
            f"""
<div class="activity-row">
    <div class="activity-left">
        <div class="activity-icon">{icon}</div>
        <div>
            <div class="activity-title">{title}</div>
            <div class="activity-sub">{sub}</div>
        </div>
    </div>
    <div class="activity-time">{time}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Alle Aktivitäten anzeigen →", key="all_activity", use_container_width=True):
        open_page("dashboard")


def render_recommendations():
    st.markdown(
        """
<div class="rec-card">
    <div class="rec-title">Optimize Your Workflow</div>
    <div class="rec-text">Erstelle Automationen für wiederkehrende Aufgaben und spare Zeit.</div>
    <div class="rec-button">Automation erstellen</div>
</div>

<div class="rec-card purple">
    <div class="rec-title">Upgrade auf Elite+</div>
    <div class="rec-text">Mehr Tokens, mehr Power, mehr Möglichkeiten.</div>
    <div class="rec-button">Premium öffnen</div>
</div>

<div class="rec-card cyan">
    <div class="rec-title">Project Boost</div>
    <div class="rec-text">Füge mehr Memory zu deinen Projekten hinzu für bessere AI Ergebnisse.</div>
    <div class="rec-button">Projekt optimieren</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Automation", key="rec_auto", use_container_width=True):
            open_page("automation_lab")

    with c2:
        if st.button("Premium", key="rec_premium", use_container_width=True):
            open_page("premium")

    with c3:
        if st.button("Projects", key="rec_projects", use_container_width=True):
            open_page("projects")


def render_elite_banner(plan_label, tokens, activity_score):
    st.markdown(
        f"""
<div class="elite-banner">
    <div class="elite-gem">💎</div>

    <div>
        <div class="elite-title">MaByte {plan_label}<span class="elite-badge">Aktiv</span></div>
        <div class="elite-sub">Du nutzt deinen aktuellen Plan. Weiter so! Du bist bereit für Großes.</div>
    </div>

    <div class="elite-stats">
        <div class="elite-mini">
            <div class="elite-mini-value">{tokens}</div>
            <div class="elite-mini-label">Tokens</div>
        </div>
        <div class="elite-mini">
            <div class="elite-mini-value">{activity_score}/100</div>
            <div class="elite-mini-label">Daily Limit</div>
        </div>
        <div class="elite-mini">
            <div class="elite-mini-value">AI</div>
            <div class="elite-mini-label">Power</div>
        </div>
        <div class="elite-mini">
            <div class="elite-mini-value">Priority</div>
            <div class="elite-mini-label">Support</div>
        </div>
    </div>

    <div>
        <div class="rec-button">Mehr erfahren</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_home():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    home_css()

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    plan_data = PLANS.get(plan, PLANS["free"])
    plan_label = plan_data.get("label", plan).title()

    jobs_success = successful_jobs_count(user)
    activity_score = workspace_activity_score(user)
    latest_tool = latest_tool_used(user)

    st.markdown(
        """
<div class="home-top-actions">
    <div class="home-icon-btn">🔔</div>
    <div class="home-icon-btn">⚙️</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="welcome-small">Welcome back,</div>
<div class="welcome-title">{user}<span class="plan-pill">{plan_label}</span></div>
<div class="home-sub">Dein AI Operating System für maximale Performance.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="quick-grid">', unsafe_allow_html=True)

    quick_items = [
        ("💬", "AI Assistant", "chat"),
        ("📁", "Projects", "projects"),
        ("⚡", "Automations", "automation_lab"),
        ("⚽", "Football AI", "football"),
        ("🎬", "Media Tools", "video"),
    ]

    cols = st.columns(5)

    for i, item in enumerate(quick_items):
        with cols[i]:
            render_quick_card(*item)

    st.markdown("</div>", unsafe_allow_html=True)

    stat_cols = st.columns(5)

    with stat_cols[0]:
        render_stat_card("👤", "User", user, "Active Account")

    with stat_cols[1]:
        render_stat_card("💎", "Plan", plan_label, "Max Access", "#38bdf8")

    with stat_cols[2]:
        render_stat_card("🪙", "Tokens", f"{tokens:,}".replace(",", "."), "Verfügbar")

    with stat_cols[3]:
        render_stat_card("⚡", "Jobs", jobs_success, "Gesamt", "#38bdf8")

    with stat_cols[4]:
        render_stat_card("〽️", "Activity", f"{activity_score}/100", f"Latest: {latest_tool}", "#e879f9")

    left, right = st.columns([1.05, .95], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">⚡ Live AI Activity</div>', unsafe_allow_html=True)
        render_activity_feed(user)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🧠 Smart Recommendations</div>', unsafe_allow_html=True)
        render_recommendations()
        st.markdown("</div>", unsafe_allow_html=True)

    render_elite_banner(
        plan_label=plan_label,
        tokens=f"{tokens:,}".replace(",", "."),
        activity_score=activity_score,
    )

    st.markdown(
        """
<div class="footer">© 2026 MaByte AI Operating System. All rights reserved.</div>
        """,
        unsafe_allow_html=True,
    )