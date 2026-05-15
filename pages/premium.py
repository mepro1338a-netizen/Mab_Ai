import streamlit as st
from config import PLANS, FOOTBALL_PLANS

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MaByte Premium",
    layout="wide"
)

# =========================================================
# PREMIUM CSS
# =========================================================

st.markdown("""
<style>

/* ======================================================
BACKGROUND
====================================================== */

.stApp{
    background:
        radial-gradient(circle at top left, rgba(88,28,135,.22), transparent 30%),
        radial-gradient(circle at top right, rgba(37,99,235,.18), transparent 25%),
        linear-gradient(180deg,#030712 0%, #07111f 100%);
}

/* ======================================================
GLOBAL
====================================================== */

html, body, [class*="css"]{
    color:white;
    font-family:Inter;
}

/* ======================================================
HERO
====================================================== */

.hero-box{
    padding:42px;
    border-radius:34px;

    background:
        linear-gradient(135deg,
            rgba(15,23,42,.98),
            rgba(17,24,39,.92)
        );

    border:1px solid rgba(148,163,184,.12);

    margin-bottom:30px;

    box-shadow:
        0 0 40px rgba(59,130,246,.08),
        0 20px 60px rgba(0,0,0,.45);
}

.hero-title{
    font-size:64px;
    font-weight:900;
    line-height:1;
    letter-spacing:-2px;

    background:linear-gradient(
        90deg,
        #ffffff,
        #93c5fd,
        #c084fc
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-sub{
    margin-top:18px;
    font-size:19px;
    color:#cbd5e1;
    line-height:1.7;
    max-width:900px;
}

.hero-badge{
    display:inline-block;
    margin-top:26px;
    padding:12px 18px;
    border-radius:999px;

    background:
        linear-gradient(
            90deg,
            rgba(37,99,235,.25),
            rgba(168,85,247,.25)
        );

    border:1px solid rgba(96,165,250,.18);

    font-size:14px;
    font-weight:800;

    color:#dbeafe;
}

/* ======================================================
SECTION
====================================================== */

.section-title{
    font-size:38px;
    font-weight:900;
    margin-top:20px;
    margin-bottom:10px;
    color:white;
}

.section-sub{
    color:#94a3b8;
    font-size:16px;
    margin-bottom:28px;
}

/* ======================================================
PLAN CARDS
====================================================== */

.plan-card{
    border-radius:30px;

    padding:30px;

    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.98),
            rgba(15,23,42,.84)
        );

    border:1px solid rgba(148,163,184,.12);

    min-height:720px;

    position:relative;

    overflow:hidden;

    box-shadow:
        0 15px 50px rgba(0,0,0,.35);
}

.plan-card.popular{
    border:1px solid rgba(168,85,247,.35);

    box-shadow:
        0 0 35px rgba(168,85,247,.16),
        0 15px 50px rgba(0,0,0,.45);
}

.plan-card::before{
    content:"";

    position:absolute;

    top:-100px;
    right:-100px;

    width:220px;
    height:220px;

    background:
        radial-gradient(
            circle,
            rgba(59,130,246,.14),
            transparent 70%
        );
}

.plan-name{
    font-size:34px;
    font-weight:900;
    color:white;
}

.plan-badge{
    display:inline-block;

    margin-top:12px;

    padding:8px 14px;

    border-radius:999px;

    background:
        linear-gradient(
            90deg,
            rgba(59,130,246,.25),
            rgba(168,85,247,.25)
        );

    border:1px solid rgba(96,165,250,.14);

    color:#dbeafe;

    font-size:12px;
    font-weight:800;
}

.plan-price{
    margin-top:26px;

    font-size:52px;
    font-weight:1000;
    line-height:1;
}

.plan-price-small{
    font-size:16px;
    color:#94a3b8;
    margin-top:10px;
}

.token-box{
    margin-top:24px;

    padding:20px;

    border-radius:22px;

    background:
        rgba(15,23,42,.55);

    border:1px solid rgba(148,163,184,.08);
}

.token-label{
    color:#94a3b8;
    font-size:13px;
    font-weight:700;
}

.token-value{
    margin-top:8px;
    font-size:34px;
    font-weight:900;
}

.plan-description{
    margin-top:22px;
    color:#cbd5e1;
    line-height:1.7;
    min-height:85px;
}

.feature-title{
    margin-top:28px;
    margin-bottom:16px;

    color:white;
    font-size:18px;
    font-weight:900;
}

.feature-item{
    padding:12px 0;

    color:#dbeafe;

    border-bottom:
        1px solid rgba(148,163,184,.06);

    font-size:15px;
}

/* ======================================================
FOOTBALL
====================================================== */

.football-hero{
    margin-top:70px;

    padding:38px;

    border-radius:34px;

    background:
        linear-gradient(
            135deg,
            rgba(22,101,52,.22),
            rgba(15,23,42,.95)
        );

    border:1px solid rgba(34,197,94,.14);

    box-shadow:
        0 0 40px rgba(34,197,94,.08);
}

.football-title{
    font-size:52px;
    font-weight:1000;
    line-height:1;
}

.football-sub{
    margin-top:16px;

    color:#d1fae5;

    line-height:1.7;

    max-width:900px;
}

/* ======================================================
B2B
====================================================== */

.b2b-box{
    margin-top:40px;

    padding:38px;

    border-radius:30px;

    background:
        linear-gradient(
            135deg,
            rgba(88,28,135,.25),
            rgba(15,23,42,.96)
        );

    border:1px solid rgba(168,85,247,.20);
}

.b2b-title{
    font-size:36px;
    font-weight:900;
}

.b2b-sub{
    margin-top:16px;

    color:#d8b4fe;

    line-height:1.7;
}

/* ======================================================
BUTTONS
====================================================== */

.stButton button{
    width:100%;

    border:none !important;

    border-radius:18px !important;

    padding:16px !important;

    background:
        linear-gradient(
            90deg,
            #2563eb,
            #7c3aed
        ) !important;

    color:white !important;

    font-size:15px !important;

    font-weight:800 !important;

    transition:.25s;
}

.stButton button:hover{
    transform:translateY(-2px);
    opacity:.92;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero-box">

<div class="hero-title">
One System.<br>
Infinite Intelligence.
</div>

<div class="hero-sub">
MaByte kombiniert AI, Content Engines, Coding,
Football Intelligence, Video Generation und Automation
in einer skalierbaren Plattform für Creator,
Founder und moderne Teams.
</div>

<div class="hero-badge">
⚡ Creator OS • AI Automation • Football Intelligence • Content Engine
</div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# NORMAL PREMIUM
# =========================================================

st.markdown("""
<div class="section-title">
💎 MaByte Premium
</div>

<div class="section-sub">
Die normalen AI-Pläne für Chat, Coding,
Media, Automation und Creator Workflows.
</div>
""", unsafe_allow_html=True)

# =========================================================
# PLAN CARD
# =========================================================

def render_plan(plan_key, popular=False):

    plan = PLANS[plan_key]

    card_class = "plan-card popular" if popular else "plan-card"

    st.markdown(f"""
<div class="{card_class}">

<div class="plan-name">
{plan["label"]}
</div>

<div class="plan-badge">
{plan["badge"]}
</div>

<div class="plan-price">
{plan["price"]}
</div>

<div class="plan-price-small">
monatlich
</div>

<div class="token-box">

<div class="token-label">
AI TOKENS
</div>

<div class="token-value">
{plan["tokens"]:,}
</div>

</div>

<div class="plan-description">
{plan["description"]}
</div>

<div class="feature-title">
Features
</div>

""", unsafe_allow_html=True)

    for feature in plan["highlights"]:
        st.markdown(
            f'<div class="feature-item">✅ {feature}</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        f"Upgrade auf {plan['label']}",
        key=f"buy_{plan_key}"
    ):
        st.success(f"{plan['label']} ausgewählt.")

# =========================================================
# PREMIUM GRID
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    render_plan("pro")

with col2:
    render_plan("grand", popular=True)

with col3:
    render_plan("elite")

# =========================================================
# FOOTBALL HERO
# =========================================================

st.markdown("""
<div class="football-hero">

<div class="football-title">
⚽ Football Intelligence
</div>

<div class="football-sub">
Erstelle viralen Fußball-Content mit AI,
automatisiere Matchday Workflows,
nutze Live Match Daten und skaliere
Football Creator Systeme mit AI Actions,
API Access und Automationen.
</div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# FOOTBALL SECTION
# =========================================================

st.markdown("""
<div class="section-title">
⚽ Football Premium
</div>

<div class="section-sub">
Getrennte Football Pläne für Creator,
Football Seiten, Agenturen und Apps.
</div>
""", unsafe_allow_html=True)

# =========================================================
# FOOTBALL CARDS
# =========================================================

football_col1, football_col2, football_col3 = st.columns(3)

# ---------------------------------------------------------

with football_col1:

    st.markdown("""
<div class="plan-card">

<div class="plan-name">
Football Starter
</div>

<div class="plan-badge">
Creator Entry
</div>

<div class="plan-price">
19,99€
</div>

<div class="plan-price-small">
pro Monat
</div>

<div class="token-box">

<div class="token-label">
FOOTBALL AI ACTIONS
</div>

<div class="token-value">
1.000
</div>

</div>

<div class="feature-title">
Features
</div>

<div class="feature-item">
⚽ Match Stats
</div>

<div class="feature-item">
⚽ Match Predictions
</div>

<div class="feature-item">
⚽ Team & Player Data
</div>

<div class="feature-item">
⚽ AI Match Analysis
</div>

<div class="feature-item">
⚽ Basic API Access
</div>

</div>
""", unsafe_allow_html=True)

    st.button(
        "Football Starter wählen",
        key="football_starter"
    )

# ---------------------------------------------------------

with football_col2:

    st.markdown("""
<div class="plan-card popular">

<div class="plan-name">
Football Pro
</div>

<div class="plan-badge">
Most Popular
</div>

<div class="plan-price">
99,99€
</div>

<div class="plan-price-small">
pro Monat
</div>

<div class="token-box">

<div class="token-label">
FOOTBALL AI ACTIONS
</div>

<div class="token-value">
8.000
</div>

</div>

<div class="feature-title">
Features
</div>

<div class="feature-item">
⚽ Reel Generator
</div>

<div class="feature-item">
⚽ AI Match Recaps
</div>

<div class="feature-item">
⚽ Viral Content Ideas
</div>

<div class="feature-item">
⚽ Advanced API Access
</div>

<div class="feature-item">
⚽ Auto Posting
</div>

<div class="feature-item">
⚽ Webhooks
</div>

</div>
""", unsafe_allow_html=True)

    st.button(
        "Football Pro wählen",
        key="football_pro"
    )

# ---------------------------------------------------------

with football_col3:

    st.markdown("""
<div class="plan-card">

<div class="plan-name">
Football Elite
</div>

<div class="plan-badge">
Infrastructure
</div>

<div class="plan-price">
249,99€
</div>

<div class="plan-price-small">
pro Monat
</div>

<div class="token-box">

<div class="token-label">
FOOTBALL AI ACTIONS
</div>

<div class="token-value">
20.000
</div>

</div>

<div class="feature-title">
Features
</div>

<div class="feature-item">
⚽ High Volume API
</div>

<div class="feature-item">
⚽ Multi Account Systems
</div>

<div class="feature-item">
⚽ Live Match Automation
</div>

<div class="feature-item">
⚽ Priority Infrastructure
</div>

<div class="feature-item">
⚽ Advanced Rate Limits
</div>

<div class="feature-item">
⚽ Business Usage
</div>

</div>
""", unsafe_allow_html=True)

    st.button(
        "Football Elite wählen",
        key="football_elite"
    )

# =========================================================
# B2B
# =========================================================

st.markdown("""
<div class="b2b-box">

<div class="b2b-title">
🏢 Football Enterprise / B2B
</div>

<div class="b2b-sub">
Für Agenturen, große Creator Systeme,
Football Apps, Datenplattformen
und Unternehmen mit Custom API Limits,
White Label Lösungen, Webhooks,
Dedicated Infrastructure und High Volume Access.
</div>

</div>
""", unsafe_allow_html=True)

if st.button(
    "Enterprise Anfrage stellen",
    key="enterprise_button"
):
    st.info("B2B Anfrage Bereich folgt als nächstes.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.caption(
    "MaByte • AI Operating System • Football Intelligence • Automation Infrastructure"
)