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

def open_page(page: str):
    st.session_state.page = page
    st.rerun()


# =========================================================
# HELPERS
# =========================================================

def safe(value):
    return html.escape(str(value or ""))


def fmt(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


# =========================================================
# CSS
# =========================================================

def home_css():
    st.markdown(
        """
<style>

.main .block-container{
    max-width:1450px!important;
    padding-top:90px!important;
    padding-bottom:120px!important;
}

/* HERO */

.mb-hero{
    padding:32px;
    border-radius:30px;
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.16), transparent 30%),
        linear-gradient(135deg, rgba(12,18,40,.96), rgba(5,8,20,.98));
    border:1px solid rgba(168,85,247,.14);
    margin-bottom:26px;
    box-shadow:0 0 50px rgba(0,0,0,.25);
}

.mb-kicker{
    color:#c084fc;
    font-size:12px;
    font-weight:900;
    letter-spacing:.25em;
    text-transform:uppercase;
    margin-bottom:12px;
}

.mb-title{
    color:#ffe7a3;
    font-size:64px;
    font-weight:1000;
    line-height:1;
    letter-spacing:-3px;
}

.mb-sub{
    margin-top:16px;
    color:#aeb7d0;
    font-size:18px;
    max-width:720px;
    line-height:1.6;
}

/* APP GRID */

.mb-app{
    background:
        linear-gradient(180deg, rgba(10,15,35,.95), rgba(5,7,18,.98));
    border:1px solid rgba(168,85,247,.12);
    border-radius:24px;
    padding:22px;
    min-height:210px;
    position:relative;
    overflow:hidden;
    transition:.25s;
}

.mb-app:hover{
    transform:translateY(-4px);
    border:1px solid rgba(168,85,247,.35);
    box-shadow:0 0 30px rgba(168,85,247,.15);
}

.mb-icon{
    width:58px;
    height:58px;
    border-radius:18px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin-bottom:18px;
    background:rgba(168,85,247,.12);
    border:1px solid rgba(168,85,247,.18);
    font-size:28px;
}

.mb-app-title{
    color:white;
    font-size:28px;
    font-weight:900;
    margin-bottom:10px;
}

.mb-app-sub{
    color:#9ca3af;
    font-size:15px;
    line-height:1.6;
    min-height:48px;
}

/* BUTTONS */

.stButton > button{
    width:100%!important;
    border-radius:16px!important;
    height:48px!important;
    background:
        linear-gradient(135deg, rgba(36,8,56,.98), rgba(12,3,25,.98))!important;

    border:1px solid rgba(168,85,247,.24)!important;

    color:#ffe7a3!important;
    font-size:16px!important;
    font-weight:900!important;
    transition:.2s!important;
}

.stButton > button:hover{
    transform:translateY(-2px)!important;
    border:1px solid #a855f7!important;
    box-shadow:0 0 22px rgba(168,85,247,.25)!important;
}

/* STATS */

.mb-stat{
    padding:22px;
    border-radius:24px;
    background:
        linear-gradient(180deg, rgba(8,12,28,.95), rgba(5,8,20,.98));
    border:1px solid rgba(255,255,255,.06);
}

.mb-stat-top{
    color:#7dd3fc;
    font-size:12px;
    font-weight:900;
    letter-spacing:.18em;
    text-transform:uppercase;
}

.mb-stat-value{
    margin-top:12px;
    color:#ffe7a3;
    font-size:42px;
    font-weight:1000;
}

.mb-stat-sub{
    margin-top:10px;
    color:#94a3b8;
    font-size:14px;
}

/* ACTIVITY */

.mb-section{
    margin-top:34px;
}

.mb-section-title{
    color:#ffe7a3;
    font-size:28px;
    font-weight:1000;
    margin-bottom:18px;
}

.mb-activity{
    padding:18px;
    border-radius:20px;
    margin-bottom:14px;

    background:
        linear-gradient(135deg, rgba(10,14,30,.96), rgba(8,10,20,.98));

    border:1px solid rgba(255,255,255,.05);
}

.mb-activity-title{
    color:white;
    font-size:16px;
    font-weight:900;
}

.mb-activity-sub{
    color:#9ca3af;
    margin-top:6px;
    font-size:14px;
}

.mb-activity-time{
    color:#7dd3fc;
    font-size:12px;
    margin-top:10px;
}

/* ELITE */

.mb-elite{
    margin-top:38px;
    padding:30px;
    border-radius:30px;

    background:
        radial-gradient(circle at top right, rgba(168,85,247,.18), transparent 30%),
        linear-gradient(135deg, rgba(30,10,50,.96), rgba(8,8,20,.98));

    border:1px solid rgba(168,85,247,.18);
}

.mb-elite-title{
    color:#ffe7a3;
    font-size:38px;
    font-weight:1000;
}

.mb-elite-sub{
    margin-top:12px;
    color:#cbd5e1;
    font-size:16px;
    line-height:1.6;
}

@media(max-width:1200px){

    .mb-title{
        font-size:44px;
    }

    .mb-stat-value{
        font-size:32px;
    }
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# COMPONENTS
# =========================================================

def app_card(icon, title, sub, page):

    st.markdown(
        f"""
<div class="mb-app">

    <div class="mb-icon">{safe(icon)}</div>

    <div class="mb-app-title">
        {safe(title)}
    </div>

    <div class="mb-app-sub">
        {safe(sub)}
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Open", key=f"open_{page}", width="stretch"):
        open_page(page)


def stat_card(title, value, sub):

    st.markdown(
        f"""
<div class="mb-stat">

    <div class="mb-stat-top">
        {safe(title)}
    </div>

    <div class="mb-stat-value">
        {safe(value)}
    </div>

    <div class="mb-stat-sub">
        {safe(sub)}
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )


def activity(title, sub, time):

    st.markdown(
        f"""
<div class="mb-activity">

    <div class="mb-activity-title">
        {safe(title)}
    </div>

    <div class="mb-activity-sub">
        {safe(sub)}
    </div>

    <div class="mb-activity-time">
        {safe(time)}
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# MAIN
# =========================================================

def render_home():

    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    home_css()

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    jobs = successful_jobs_count(user)
    score = workspace_activity_score(user)

    plan_data = PLANS.get(plan, PLANS["free"])
    plan_label = plan_data.get("label", "Free")

    # =====================================================
    # HERO
    # =====================================================

    st.markdown(
        f"""
<div class="mb-hero">

    <div class="mb-kicker">
        AI OPERATING SYSTEM
    </div>

    <div class="mb-title">
        MaByte Intelligence
    </div>

    <div class="mb-sub">
        Strategy. Content. Automation. Projects.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # APPS
    # =====================================================

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        app_card("💬", "Assistant", "Strategy & AI", "chat")

    with c2:
        app_card("📁", "Projects", "Workspace Memory", "projects")

    with c3:
        app_card("⚡", "Automation", "AI Workflows", "automation_lab")

    with c4:
        app_card("⚽", "Football", "Matchday Engine", "football")

    with c5:
        app_card("🎬", "Media", "Creator Suite", "video")

    # =====================================================
    # STATS
    # =====================================================

    st.markdown('<div class="mb-section">', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        stat_card("Tokens", fmt(tokens), "Available")

    with s2:
        stat_card("Jobs", jobs, "Completed")

    with s3:
        stat_card("Activity", f"{score}/100", "Workspace")

    with s4:
        stat_card("Plan", plan_label, "Current Layer")

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # ACTIVITY
    # =====================================================

    st.markdown(
        """
<div class="mb-section">

    <div class="mb-section-title">
        Live Activity
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    items = recent_activity(username=user, limit=3)

    if not items:

        activity(
            "AI Assistant",
            "Neue Anfrage verarbeitet",
            "vor 2 Min"
        )

        activity(
            "Automation",
            "Workflow ausgeführt",
            "vor 8 Min"
        )

        activity(
            "Project Memory",
            "Workspace synchronisiert",
            "vor 14 Min"
        )

    else:

        for item in items:

            tool = str(item.get("tool", "system")).title()
            created = str(item.get("created_at", ""))[:16]

            activity(
                tool,
                "Neue Aktivität erkannt",
                created
            )

    # =====================================================
    # ELITE
    # =====================================================

    st.markdown(
        f"""
<div class="mb-elite">

    <div class="mb-elite-title">
        MaByte Elite Layer
    </div>

    <div class="mb-elite-sub">
        Dein AI Workspace läuft im Premium Modus mit
        schnellerem Workflow und smarterem Kontext.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )