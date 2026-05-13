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

.stApp{
    background:
        radial-gradient(circle at top,
        rgba(37,99,235,.12),
        transparent 30%),
        linear-gradient(
            135deg,
            #020617 0%,
            #071427 55%,
            #020617 100%
        );
}

/* ===================================================== */
/* LAYOUT */
/* ===================================================== */

.main .block-container{
    max-width:1450px;
    padding-top:1.2rem;
    padding-bottom:1rem;
}

/* ===================================================== */
/* SIDEBAR */
/* ===================================================== */

section[data-testid="stSidebar"]{

    background:
        linear-gradient(
            180deg,
            #071120 0%,
            #050b16 100%
        );

    border-right:
        1px solid rgba(96,165,250,.10);
}

section[data-testid="stSidebar"] *{
    color:white!important;
}

/* ===================================================== */
/* HERO */
/* ===================================================== */

.hero-wrap{
    margin-bottom:20px;
}

.hero-top{
    color:#94a3b8;
    font-size:15px;
    margin-bottom:8px;
}

.hero-title{
    font-size:58px;
    line-height:1;
    font-weight:900;
    color:white;
    letter-spacing:-2px;
}

.hero-sub{
    color:#94a3b8;
    font-size:18px;
    margin-top:12px;
}

.plan-badge{

    display:inline-block;

    margin-left:12px;

    padding:8px 16px;

    border-radius:999px;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #a855f7
        );

    color:white;

    font-size:14px;
    font-weight:800;
}

/* ===================================================== */
/* GRID */
/* ===================================================== */

.top-grid{
    margin-top:24px;
}

.card{

    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.96),
            rgba(10,20,40,.75)
        );

    border:
        1px solid rgba(96,165,250,.10);

    border-radius:26px;

    padding:22px;

    box-shadow:
        0 10px 30px rgba(0,0,0,.25);

    backdrop-filter: blur(10px);
}

/* ===================================================== */
/* APP CARDS */
/* ===================================================== */

.app-card{
    text-align:center;
    min-height:170px;
}

.app-icon{
    font-size:42px;
    margin-bottom:14px;
}

.app-title{
    color:white;
    font-size:21px;
    font-weight:800;
}

.app-sub{
    color:#94a3b8;
    font-size:14px;
    margin-top:8px;
}

/* ===================================================== */
/* STATS */
/* ===================================================== */

.stat-title{
    color:#94a3b8;
    font-size:14px;
    margin-bottom:10px;
}

.stat-value{
    color:white;
    font-size:42px;
    font-weight:900;
    line-height:1;
}

.stat-sub{
    color:#22c55e;
    margin-top:10px;
    font-size:14px;
}

/* ===================================================== */
/* SECTION */
/* ===================================================== */

.section-title{
    color:white;
    font-size:28px;
    font-weight:900;
    margin-bottom:20px;
}

/* ===================================================== */
/* ACTIVITY */
/* ===================================================== */

.activity-item{

    background:
        rgba(15,23,42,.55);

    border:
        1px solid rgba(96,165,250,.08);

    border-radius:18px;

    padding:16px;

    margin-bottom:14px;
}

.activity-head{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.activity-title{
    color:white;
    font-size:16px;
    font-weight:800;
}

.activity-time{
    color:#94a3b8;
    font-size:12px;
}

.activity-sub{
    color:#94a3b8;
    font-size:13px;
    margin-top:6px;
}

/* ===================================================== */
/* RECOMMENDATIONS */
/* ===================================================== */

.recommend-card{

    border-radius:22px;

    padding:22px;

    margin-bottom:16px;

    border:
        1px solid rgba(96,165,250,.10);
}

.blue-card{
    background:
        linear-gradient(
            135deg,
            rgba(30,64,175,.35),
            rgba(15,23,42,.95)
        );
}

.purple-card{
    background:
        linear-gradient(
            135deg,
            rgba(126,34,206,.35),
            rgba(15,23,42,.95)
        );
}

.green-card{
    background:
        linear-gradient(
            135deg,
            rgba(6,182,212,.25),
            rgba(15,23,42,.95)
        );
}

.rec-title{
    color:white;
    font-size:23px;
    font-weight:900;
}

.rec-sub{
    color:#cbd5e1;
    font-size:14px;
    margin-top:8px;
}

/* ===================================================== */
/* ELITE BANNER */
/* ===================================================== */

.elite-banner{

    margin-top:24px;

    background:
        linear-gradient(
            135deg,
            rgba(88,28,135,.30),
            rgba(15,23,42,.96)
        );

    border:
        1px solid rgba(168,85,247,.20);

    border-radius:28px;

    padding:30px;
}

.elite-flex{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:30px;
    flex-wrap:wrap;
}

.elite-title{
    color:white;
    font-size:34px;
    font-weight:900;
}

.elite-sub{
    color:#cbd5e1;
    margin-top:10px;
    font-size:15px;
}

.elite-stats{
    display:flex;
    gap:45px;
    flex-wrap:wrap;
}

.elite-num{
    color:white;
    font-size:26px;
    font-weight:900;
}

.elite-label{
    color:#94a3b8;
    font-size:13px;
}

/* ===================================================== */
/* BUTTONS */
/* ===================================================== */

.stButton > button{

    width:100%;

    border:none!important;

    min-height:48px!important;

    border-radius:16px!important;

    font-weight:800!important;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #38bdf8
        )!important;

    color:white!important;
}

/* ===================================================== */
/* MOBILE */
/* ===================================================== */

@media(max-width:1200px){

    .hero-title{
        font-size:42px;
    }

    .stat-value{
        font-size:34px;
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
<div class="card app-card">

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
        key=f"open_{page}",
        use_container_width=True,
    ):
        open_page(page)


def stat_card(title, value, sub):

    st.markdown(
        f"""
<div class="card">

<div class="stat-title">
{title}
</div>

<div class="stat-value">
{value}
</div>

<div class="stat-sub">
{sub}
</div>

</div>
        """,
        unsafe_allow_html=True,
    )


def render_activity(username):

    items = recent_activity(
        username=username,
        limit=4,
    )

    if not items:

        demo = [
            ("💬 AI Assistant", "Neue Anfrage verarbeitet", "vor 2 Min"),
            ("🎨 Image Generation", "Bild erfolgreich generiert", "vor 5 Min"),
            ("📁 Project Update", "Workspace aktualisiert", "vor 9 Min"),
            ("⚡ Automation Trigger", "Workflow ausgeführt", "vor 15 Min"),
        ]

        for title, sub, time in demo:

            st.markdown(
                f"""
<div class="activity-item">

<div class="activity-head">

<div class="activity-title">
{title}
</div>

<div class="activity-time">
{time}
</div>

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

<div class="activity-head">

<div class="activity-title">
⚡ {tool}
</div>

<div class="activity-time">
{created}
</div>

</div>

<div class="activity-sub">
Neue Aktivität erkannt
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
<div class="hero-wrap">

<div class="hero-top">
Welcome back,
</div>

<div class="hero-title">
{user}
<span class="plan-badge">
{plan_data.get("label","Free")}
</span>
</div>

<div class="hero-sub">
Dein AI Operating System für maximale Performance.
</div>

</div>
        """,
        unsafe_allow_html=True,
    )

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
    # STATS
    # =====================================================

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        stat_card(
            "🪙 Tokens",
            f"{tokens:,}".replace(",", "."),
            "Verfügbar",
        )

    with s2:
        stat_card(
            "⚡ Jobs",
            jobs,
            "Gesamt",
        )

    with s3:
        stat_card(
            "🧠 Activity",
            f"{activity_score}/100",
            "Tageslimit",
        )

    with s4:
        stat_card(
            "💎 Plan",
            plan_data.get("label", "Free"),
            "Max Access",
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
<div class="card">

<div class="section-title">
⚡ Live AI Activity
</div>
            """,
            unsafe_allow_html=True,
        )

        render_activity(user)

        st.button(
            "Alle Aktivitäten anzeigen",
            use_container_width=True,
            key="all_activity",
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            """
<div class="recommend-card blue-card">

<div class="rec-title">
Optimize Your Workflow
</div>

<div class="rec-sub">
Erstelle Automationen für wiederkehrende Aufgaben und spare Zeit.
</div>

</div>

<div class="recommend-card purple-card">

<div class="rec-title">
Upgrade auf Elite+
</div>

<div class="rec-sub">
Mehr Tokens, mehr Power und Creator Features.
</div>

</div>

<div class="recommend-card green-card">

<div class="rec-title">
Project Boost
</div>

<div class="rec-sub">
Mehr Memory für bessere AI Ergebnisse.
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

<div class="elite-flex">

<div>

<div class="elite-title">
💎 MaByte Elite
</div>

<div class="elite-sub">
Du nutzt den leistungsstärksten Plan.
Weiter so! Du bist bereit für Großes.
</div>

</div>

<div class="elite-stats">

<div>
<div class="elite-num">
{tokens:,}
</div>
<div class="elite-label">
Tokens
</div>
</div>

<div>
<div class="elite-num">
{activity_score}/100
</div>
<div class="elite-label">
Daily Limit
</div>
</div>

<div>
<div class="elite-num">
Unlimited
</div>
<div class="elite-label">
AI Power
</div>
</div>

<div>
<div class="elite-num">
Priority
</div>
<div class="elite-label">
Support
</div>
</div>

</div>

</div>

</div>
        """,
        unsafe_allow_html=True,
    )