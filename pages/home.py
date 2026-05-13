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

#MainMenu,
header,
footer{
    display:none;
}

.main .block-container{
    max-width:1400px;
    padding-top:1.2rem;
    padding-bottom:1rem;
}

.stApp{
    background:
        radial-gradient(circle at top,
        rgba(37,99,235,.12),
        transparent 25%),

        linear-gradient(
            135deg,
            #020617 0%,
            #071427 50%,
            #020617 100%
        );
}

/* =========================
CARDS
========================= */

.premium-card{

    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.96),
            rgba(15,30,60,.78)
        );

    border:
        1px solid rgba(96,165,250,.10);

    border-radius:28px;

    padding:24px;

    box-shadow:
        0 12px 40px rgba(0,0,0,.28);

    height:100%;
}

/* =========================
HERO
========================= */

.hero-title{
    color:white;
    font-size:58px;
    font-weight:900;
    line-height:1;
    letter-spacing:-2px;
}

.hero-sub{
    color:#cbd5e1;
    font-size:18px;
    margin-top:12px;
}

.plan-badge{

    display:inline-block;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #c084fc
        );

    padding:8px 16px;

    border-radius:999px;

    color:white;

    font-size:14px;
    font-weight:800;

    margin-left:14px;
}

/* =========================
TOP APPS
========================= */

.app-card{

    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.95),
            rgba(15,30,60,.65)
        );

    border:
        1px solid rgba(96,165,250,.10);

    border-radius:24px;

    padding:22px;

    text-align:center;

    transition:.2s;
}

.app-icon{
    font-size:38px;
    margin-bottom:14px;
}

.app-title{
    color:white;
    font-size:20px;
    font-weight:800;
}

.app-sub{
    color:#94a3b8;
    font-size:13px;
    margin-top:4px;
}

.stButton > button{

    width:100%;

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

    box-shadow:
        0 8px 25px rgba(56,189,248,.18);
}

/* =========================
METRICS
========================= */

.metric-card{

    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.92),
            rgba(15,30,60,.72)
        );

    border:
        1px solid rgba(96,165,250,.10);

    border-radius:24px;

    padding:22px;
}

.metric-label{
    color:#94a3b8;
    font-size:14px;
    font-weight:700;
}

.metric-value{
    color:white;
    font-size:44px;
    font-weight:900;
    margin-top:8px;
}

.metric-sub{
    color:#22c55e;
    font-size:14px;
    margin-top:4px;
}

/* =========================
SECTION
========================= */

.section-title{
    color:white;
    font-size:28px;
    font-weight:900;
    margin-bottom:18px;
}

/* =========================
ACTIVITY
========================= */

.activity-item{

    background:
        rgba(15,23,42,.55);

    border:
        1px solid rgba(96,165,250,.08);

    border-radius:18px;

    padding:16px;

    margin-bottom:14px;
}

.activity-title{
    color:white;
    font-size:15px;
    font-weight:800;
}

.activity-sub{
    color:#94a3b8;
    font-size:13px;
    margin-top:4px;
}

/* =========================
RECOMMENDATION
========================= */

.recommend-card{

    background:
        linear-gradient(
            135deg,
            rgba(37,99,235,.20),
            rgba(15,23,42,.92)
        );

    border:
        1px solid rgba(59,130,246,.18);

    border-radius:22px;

    padding:20px;

    margin-bottom:18px;
}

.recommend-title{
    color:white;
    font-size:20px;
    font-weight:900;
}

.recommend-sub{
    color:#cbd5e1;
    font-size:14px;
    margin-top:8px;
}

/* =========================
BOTTOM ELITE
========================= */

.elite-banner{

    background:
        linear-gradient(
            135deg,
            rgba(91,33,182,.40),
            rgba(15,23,42,.95)
        );

    border:
        1px solid rgba(168,85,247,.25);

    border-radius:30px;

    padding:28px;

    margin-top:24px;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# APP CARD
# =========================================================

def app_card(icon, title, sub, page):

    st.markdown(
        f"""
<div class="app-card">

<div class="app-icon">
{icon}
</div>

<div class="app-title">
{title}
</div>

<div class="app-sub">
{sub}
</div>

</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Open",
        key=page,
        use_container_width=True,
    ):
        open_page(page)


# =========================================================
# ACTIVITY
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
{created}
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

    activity_score = workspace_activity_score(user)

    # =====================================================
    # HERO
    # =====================================================

    st.markdown(
        f"""
<div class="hero-title">

Welcome back,
<br>
{user}

<span class="plan-badge">
{plan_data.get("label","Free")}
</span>

</div>

<div class="hero-sub">
Dein AI Operating System für maximale Performance.
</div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # =====================================================
    # APPS
    # =====================================================

    a1, a2, a3, a4, a5 = st.columns(5)

    with a1:
        app_card(
            "💬",
            "AI Assistant",
            "Strategy & AI",
            "chat",
        )

    with a2:
        app_card(
            "📁",
            "Projects",
            "Workspace Memory",
            "projects",
        )

    with a3:
        app_card(
            "⚡",
            "Automations",
            "AI Workflows",
            "automation_lab",
        )

    with a4:
        app_card(
            "⚽",
            "Football AI",
            "Matchday Engine",
            "football",
        )

    with a5:
        app_card(
            "🎬",
            "Media Tools",
            "Creator Suite",
            "video",
        )

    st.write("")

    # =====================================================
    # METRICS
    # =====================================================

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.markdown(
            f"""
<div class="metric-card">

<div class="metric-label">
🪙 Tokens
</div>

<div class="metric-value">
{tokens:,}
</div>

<div class="metric-sub">
Verfügbar
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    with m2:

        st.markdown(
            f"""
<div class="metric-card">

<div class="metric-label">
⚡ Jobs
</div>

<div class="metric-value">
{jobs}
</div>

<div class="metric-sub">
Gesamt
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    with m3:

        st.markdown(
            f"""
<div class="metric-card">

<div class="metric-label">
🧠 Activity
</div>

<div class="metric-value">
{activity_score}/100
</div>

<div class="metric-sub">
Tageslimit
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    with m4:

        st.markdown(
            f"""
<div class="metric-card">

<div class="metric-label">
💎 Plan
</div>

<div class="metric-value">
{plan_data.get("label","Free")}
</div>

<div class="metric-sub">
Max Access
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # =====================================================
    # MAIN GRID
    # =====================================================

    left, right = st.columns(
        [1.45, 1],
        gap="large",
    )

    # =====================================================
    # LEFT
    # =====================================================

    with left:

        st.markdown(
            """
<div class="premium-card">

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

    # =====================================================
    # RIGHT
    # =====================================================

    with right:

        st.markdown(
            """
<div class="recommend-card">

<div class="recommend-title">
Optimize Your Workflow
</div>

<div class="recommend-sub">
Erstelle intelligente AI Automationen und spare Zeit.
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Automation erstellen",
            key="auto_btn",
            use_container_width=True,
        ):
            open_page("automation_lab")

        st.write("")

        st.markdown(
            """
<div class="recommend-card">

<div class="recommend-title">
Upgrade auf Elite+
</div>

<div class="recommend-sub">
Mehr Tokens, mehr Power, mehr Möglichkeiten.
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Premium öffnen",
            key="premium_btn",
            use_container_width=True,
        ):
            open_page("premium")

        st.write("")

        st.markdown(
            """
<div class="recommend-card">

<div class="recommend-title">
Project Boost
</div>

<div class="recommend-sub">
Füge mehr Memory zu deinen Projekten hinzu.
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    # =====================================================
    # ELITE
    # =====================================================

    st.markdown(
        f"""
<div class="elite-banner">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
gap:30px;
flex-wrap:wrap;
">

<div>

<div style="
font-size:38px;
font-weight:900;
color:white;
">
💎 MaByte Elite
</div>

<div style="
color:#cbd5e1;
font-size:15px;
margin-top:10px;
">
Du nutzt den leistungsstärksten Plan.
Weiter so! Du bist bereit für Großes.
</div>

</div>

<div style="
display:flex;
gap:40px;
flex-wrap:wrap;
">

<div>
<div style="color:white;font-size:22px;font-weight:900;">
{tokens:,}
</div>
<div style="color:#94a3b8;font-size:12px;">
Tokens
</div>
</div>

<div>
<div style="color:white;font-size:22px;font-weight:900;">
{activity_score}/100
</div>
<div style="color:#94a3b8;font-size:12px;">
Daily Limit
</div>
</div>

<div>
<div style="color:white;font-size:22px;font-weight:900;">
Unlimited
</div>
<div style="color:#94a3b8;font-size:12px;">
AI Power
</div>
</div>

<div>
<div style="color:white;font-size:22px;font-weight:900;">
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