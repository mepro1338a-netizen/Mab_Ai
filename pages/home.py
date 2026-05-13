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

def open_page(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# CSS
# =========================================================

def home_css():

    st.markdown(
        """
<style>

.main .block-container{
    max-width:1280px;
    padding-top:1rem;
    padding-bottom:1.5rem;
}

section[data-testid="stSidebar"]{
    background:
        linear-gradient(
            180deg,
            #081225 0%,
            #07111f 100%
        );
    border-right:1px solid rgba(96,165,250,.12);
}

.stApp{
    background:
        radial-gradient(circle at top,
        rgba(59,130,246,.10),
        transparent 30%),
        linear-gradient(
            135deg,
            #030712 0%,
            #071427 55%,
            #020617 100%
        );
}

#MainMenu,
header,
footer{
    display:none;
}

div[data-testid="stMetric"]{
    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.92),
            rgba(15,30,60,.72)
        );

    border:1px solid rgba(96,165,250,.10);

    padding:18px;
    border-radius:22px;

    box-shadow:
        0 10px 30px rgba(0,0,0,.20);
}

.dashboard-card{

    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.92),
            rgba(15,30,60,.72)
        );

    border:1px solid rgba(96,165,250,.10);

    border-radius:24px;

    padding:22px;

    box-shadow:
        0 10px 30px rgba(0,0,0,.20);
}

.quick-card{
    text-align:center;
    min-height:120px;
}

.quick-icon{
    font-size:38px;
    margin-bottom:12px;
}

.quick-title{
    color:white;
    font-size:18px;
    font-weight:800;
}

.quick-sub{
    color:#94a3b8;
    font-size:13px;
}

.activity-item{
    background:
        rgba(15,23,42,.55);

    border:
        1px solid rgba(96,165,250,.10);

    border-radius:18px;

    padding:14px;

    margin-bottom:12px;
}

.activity-title{
    color:white;
    font-size:15px;
    font-weight:800;
}

.activity-sub{
    color:#94a3b8;
    font-size:13px;
}

.elite-banner{

    background:
        linear-gradient(
            135deg,
            rgba(88,28,135,.35),
            rgba(15,23,42,.92)
        );

    border:
        1px solid rgba(168,85,247,.25);

    border-radius:28px;

    padding:26px;

    margin-top:24px;
}

.home-title{
    color:white;
    font-size:44px;
    font-weight:900;
    letter-spacing:-1px;
}

.home-sub{
    color:#cbd5e1;
    font-size:17px;
}

.plan-pill{
    display:inline-block;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #a855f7
        );

    color:white;

    padding:7px 14px;

    border-radius:999px;

    font-size:14px;
    font-weight:800;

    margin-left:10px;
}

.section-title{
    color:white;
    font-size:24px;
    font-weight:900;
    margin-bottom:16px;
}

.stButton > button{

    border:none!important;

    border-radius:16px!important;

    min-height:48px!important;

    font-weight:800!important;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #38bdf8
        )!important;

    color:white!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# QUICK CARDS
# =========================================================

def quick_card(icon, title, sub, page):

    with st.container():

        st.markdown(
            f"""
<div class="dashboard-card quick-card">

<div class="quick-icon">
{icon}
</div>

<div class="quick-title">
{title}
</div>

<div class="quick-sub">
{sub}
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open",
            key=f"open_{page}",
            use_container_width=True,
        ):
            open_page(page)


# =========================================================
# ACTIVITY FEED
# =========================================================

def render_activity(username):

    items = recent_activity(
        username=username,
        limit=5,
    )

    if not items:

        demo = [
            ("💬 AI Assistant", "Neue Anfrage verarbeitet"),
            ("🎨 Image Generation", "Bild erfolgreich generiert"),
            ("📣 Reels Maker", "TikTok Hook erstellt"),
            ("⚽ Football AI", "Matchday Package generiert"),
            ("⚡ Automation", "Workflow ausgeführt"),
        ]

        for title, sub in demo:

            st.markdown(
                f"""
<div class="activity-item">

<div class="activity-title">
{title}
</div>

<div class="activity-sub">
{sub}
</div>

</div>
                """,
                unsafe_allow_html=True,
            )

        return

    for item in items:

        tool = str(
            item.get("tool", "system")
        ).replace("_", " ").title()

        status = item.get(
            "status",
            "success",
        )

        created = str(
            item.get("created_at", "")
        )[:16]

        st.markdown(
            f"""
<div class="activity-item">

<div class="activity-title">
⚡ {tool}
</div>

<div class="activity-sub">
{status} • {created}
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

    user = st.session_state.get(
        "user",
        "User",
    )

    plan = st.session_state.get(
        "plan",
        "free",
    )

    tokens = int(
        st.session_state.get(
            "tokens",
            0,
        ) or 0
    )

    plan_data = PLANS.get(
        plan,
        PLANS["free"],
    )

    jobs = successful_jobs_count(user)

    activity_score = workspace_activity_score(
        user
    )

    # =====================================================
    # HERO
    # =====================================================

    st.markdown(
        f"""
<div class="home-title">
Welcome back,
<br>
{user}
<span class="plan-pill">
{plan_data.get("label","Free")}
</span>
</div>

<div class="home-sub">
Dein AI Operating System für maximale Performance.
</div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # QUICK ACCESS
    # =====================================================

    q1, q2, q3, q4, q5 = st.columns(5)

    with q1:
        quick_card(
            "💬",
            "AI Assistant",
            "Strategy & AI",
            "chat",
        )

    with q2:
        quick_card(
            "📁",
            "Projects",
            "Workspace Memory",
            "projects",
        )

    with q3:
        quick_card(
            "⚡",
            "Automations",
            "AI Workflows",
            "automation_lab",
        )

    with q4:
        quick_card(
            "⚽",
            "Football AI",
            "Matchday Engine",
            "football",
        )

    with q5:
        quick_card(
            "🎬",
            "Media Tools",
            "Creator Suite",
            "video",
        )

    st.write("")

    # =====================================================
    # STATS
    # =====================================================

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric(
            "🪙 Tokens",
            f"{tokens:,}".replace(",", "."),
        )

    with s2:
        st.metric(
            "⚡ Jobs",
            jobs,
        )

    with s3:
        st.metric(
            "🧠 Activity",
            f"{activity_score}/100",
        )

    with s4:
        st.metric(
            "💎 Plan",
            plan_data.get(
                "label",
                "Free",
            ),
        )

    st.write("")

    # =====================================================
    # MAIN GRID
    # =====================================================

    left, right = st.columns(
        [1.4, 1],
        gap="large",
    )

    with left:

        st.markdown(
            """
<div class="dashboard-card">
<div class="section-title">
⚡ Live AI Activity
</div>
            """,
            unsafe_allow_html=True,
        )

        render_activity(user)

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            """
<div class="dashboard-card">

<div class="section-title">
🧠 Smart Recommendations
</div>

<div class="activity-item">
<div class="activity-title">
Optimize Your Workflow
</div>
<div class="activity-sub">
Erstelle intelligente AI Automationen.
</div>
</div>

<div class="activity-item">
<div class="activity-title">
Upgrade auf Elite+
</div>
<div class="activity-sub">
Mehr Tokens und Creator Features.
</div>
</div>

<div class="activity-item">
<div class="activity-title">
Project Boost
</div>
<div class="activity-sub">
Mehr Memory für bessere AI Ergebnisse.
</div>
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    # =====================================================
    # ELITE BANNER
    # =====================================================

    st.markdown(
        f"""
<div class="elite-banner">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
gap:20px;
flex-wrap:wrap;
">

<div>

<div style="
color:white;
font-size:30px;
font-weight:900;
">
💎 MaByte Elite
</div>

<div style="
color:#cbd5e1;
font-size:15px;
margin-top:8px;
">
Du nutzt den leistungsstärksten Plan.
Weiter so! Du bist bereit für Großes.
</div>

</div>

<div style="
display:flex;
gap:30px;
flex-wrap:wrap;
">

<div>
<div style="color:white;font-weight:900;font-size:20px;">
{tokens:,}
</div>
<div style="color:#94a3b8;font-size:12px;">
Tokens
</div>
</div>

<div>
<div style="color:white;font-weight:900;font-size:20px;">
{activity_score}/100
</div>
<div style="color:#94a3b8;font-size:12px;">
Daily Limit
</div>
</div>

<div>
<div style="color:white;font-weight:900;font-size:20px;">
Unlimited
</div>
<div style="color:#94a3b8;font-size:12px;">
AI Power
</div>
</div>

<div>
<div style="color:white;font-weight:900;font-size:20px;">
Priority
</div>
<div style="color:#94a3b8;font-size:12px;">
Support
</div>
</div>

</div>

</div>

</div>
        """,
        unsafe_allow_html=True,
    )