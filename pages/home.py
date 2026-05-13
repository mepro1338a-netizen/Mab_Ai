import streamlit as st

from database import (
    recent_activity,
    successful_jobs_count,
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
    max-width:1320px;
    padding-top:1.6rem;
    padding-bottom:3rem;
}

.home-action-row{
    display:flex;
    justify-content:flex-end;
    gap:12px;
    margin-bottom:12px;
}

.home-icon-button{
    width:46px;
    height:46px;
    border-radius:14px;
    border:1px solid rgba(96,165,250,.20);
    background:rgba(15,23,42,.65);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}

.home-small{
    color:#9fb3d1;
    font-size:16px;
    font-weight:650;
}

.home-title{
    color:white;
    font-size:40px;
    font-weight:950;
    letter-spacing:-.04em;
}

.home-pill{
    margin-left:10px;
    padding:7px 13px;
    border-radius:999px;
    background:linear-gradient(135deg,#6d28d9,#a855f7);
    color:white;
    font-size:15px;
    font-weight:900;
}

.home-sub{
    color:#cbd5e1;
    font-size:17px;
    margin-top:8px;
    margin-bottom:34px;
}

.glass-card{
    border-radius:22px;
    border:1px solid rgba(125,211,252,.14);
    background:linear-gradient(145deg,rgba(15,23,42,.86),rgba(10,30,64,.60));
    box-shadow:0 18px 50px rgba(0,0,0,.20);
}

.quick-card{
    min-height:128px;
    padding:24px 18px;
    text-align:center;
}

.quick-icon{
    font-size:40px;
    margin-bottom:12px;
}

.quick-title{
    color:white;
    font-size:17px;
    font-weight:900;
}

.stat-card{
    min-height:145px;
    padding:24px;
}

.stat-label{
    color:#9fb3d1;
    font-size:14px;
    font-weight:800;
    margin-bottom:18px;
}

.stat-value{
    color:white;
    font-size:30px;
    font-weight:950;
    word-break:break-word;
}

.stat-caption{
    color:#22c55e;
    font-size:14px;
    font-weight:800;
    margin-top:12px;
}

.panel{
    border-radius:24px;
    border:1px solid rgba(125,211,252,.14);
    background:linear-gradient(145deg,rgba(8,19,45,.92),rgba(10,25,55,.70));
    padding:24px;
    box-shadow:0 20px 60px rgba(0,0,0,.22);
}

.panel-title{
    color:white;
    font-size:24px;
    font-weight:950;
    margin-bottom:20px;
}

.activity-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:15px;
    border-radius:18px;
    border:1px solid rgba(125,211,252,.10);
    background:rgba(15,23,42,.46);
    margin-bottom:12px;
}

.activity-left{
    display:flex;
    gap:13px;
    align-items:center;
}

.activity-icon{
    width:40px;
    height:40px;
    border-radius:14px;
    background:rgba(59,130,246,.17);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}

.activity-title{
    color:white;
    font-size:15px;
    font-weight:900;
}

.activity-sub{
    color:#9fb3d1;
    font-size:13px;
}

.activity-time{
    color:#9fb3d1;
    font-size:12px;
}

.rec-card{
    border-radius:18px;
    padding:20px;
    margin-bottom:14px;
    border:1px solid rgba(125,211,252,.14);
    background:linear-gradient(135deg,rgba(30,64,175,.25),rgba(15,23,42,.55));
}

.rec-card.purple{
    background:linear-gradient(135deg,rgba(88,28,135,.38),rgba(15,23,42,.55));
    border-color:rgba(168,85,247,.24);
}

.rec-card.cyan{
    background:linear-gradient(135deg,rgba(8,145,178,.32),rgba(15,23,42,.55));
    border-color:rgba(34,211,238,.22);
}

.rec-title{
    color:white;
    font-size:20px;
    font-weight:950;
    margin-bottom:8px;
}

.rec-text{
    color:#cbd5e1;
    font-size:14px;
    margin-bottom:14px;
}

.elite-banner{
    border-radius:24px;
    border:1px solid rgba(168,85,247,.55);
    background:
        radial-gradient(circle at 15% 50%, rgba(168,85,247,.18), transparent 24%),
        linear-gradient(135deg,rgba(15,23,42,.96),rgba(25,20,65,.80));
    padding:26px;
    box-shadow:0 0 45px rgba(168,85,247,.18);
    margin-top:32px;
}

.elite-title{
    color:white;
    font-size:26px;
    font-weight:950;
}

.elite-badge{
    display:inline-block;
    margin-left:10px;
    padding:6px 12px;
    border-radius:999px;
    color:#86efac;
    background:rgba(34,197,94,.14);
    font-size:13px;
    font-weight:900;
}

.elite-sub{
    color:#cbd5e1;
    font-size:15px;
    margin-top:6px;
}

.elite-mini-value{
    color:white;
    font-size:15px;
    font-weight:950;
    text-align:center;
}

.elite-mini-label{
    color:#9fb3d1;
    font-size:12px;
    text-align:center;
    margin-top:4px;
}

.footer{
    text-align:center;
    color:#64748b;
    font-size:13px;
    padding-top:26px;
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
<div class="glass-card quick-card">
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
<div class="glass-card stat-card">
    <div class="stat-label">{icon} {label}</div>
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
</div>

<div class="rec-card purple">
    <div class="rec-title">Upgrade auf Elite+</div>
    <div class="rec-text">Mehr Tokens, mehr Power, mehr Möglichkeiten.</div>
</div>

<div class="rec-card cyan">
    <div class="rec-title">Project Boost</div>
    <div class="rec-text">Füge mehr Memory zu deinen Projekten hinzu für bessere AI Ergebnisse.</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Automation erstellen", key="rec_auto", use_container_width=True):
            open_page("automation_lab")

    with c2:
        if st.button("Premium öffnen", key="rec_premium", use_container_width=True):
            open_page("premium")

    with c3:
        if st.button("Projekt optimieren", key="rec_projects", use_container_width=True):
            open_page("projects")


def render_elite_banner(plan_label, tokens, activity_score):
    st.markdown('<div class="elite-banner">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([1, 2.2, 3, 1.3])

    with c1:
        st.markdown(
            "<div style='font-size:52px;text-align:center;'>💎</div>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
<div class="elite-title">MaByte {plan_label}<span class="elite-badge">Aktiv</span></div>
<div class="elite-sub">Du nutzt deinen aktuellen Plan. Weiter so! Du bist bereit für Großes.</div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.markdown(
                f"<div class='elite-mini-value'>{tokens}</div><div class='elite-mini-label'>Tokens</div>",
                unsafe_allow_html=True,
            )

        with s2:
            st.markdown(
                f"<div class='elite-mini-value'>{activity_score}/100</div><div class='elite-mini-label'>Daily Limit</div>",
                unsafe_allow_html=True,
            )

        with s3:
            st.markdown(
                "<div class='elite-mini-value'>AI Power</div><div class='elite-mini-label'>Unlimited</div>",
                unsafe_allow_html=True,
            )

        with s4:
            st.markdown(
                "<div class='elite-mini-value'>Priority</div><div class='elite-mini-label'>Support</div>",
                unsafe_allow_html=True,
            )

    with c4:
        if st.button("Mehr erfahren", key="elite_more", use_container_width=True):
            open_page("premium")

    st.markdown("</div>", unsafe_allow_html=True)


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
<div class="home-action-row">
    <div class="home-icon-button">🔔</div>
    <div class="home-icon-button">⚙️</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="home-small">Welcome back,</div>
<div class="home-title">{user}<span class="home-pill">{plan_label}</span></div>
<div class="home-sub">Dein AI Operating System für maximale Performance.</div>
        """,
        unsafe_allow_html=True,
    )

    quick_cols = st.columns(5)

    quick_items = [
        ("💬", "AI Assistant", "chat"),
        ("📁", "Projects", "projects"),
        ("⚡", "Automations", "automation_lab"),
        ("⚽", "Football AI", "football"),
        ("🎬", "Media Tools", "video"),
    ]

    for col, item in zip(quick_cols, quick_items):
        with col:
            render_quick_card(*item)

    st.write("")

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

    st.write("")

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