import streamlit as st
from config import PLANS, FOOTBALL_PLANS


def premium_css():
    st.markdown(
        """
<style>

/* =========================================================
   PAGE
========================================================= */

.stApp{
    background:
        radial-gradient(circle at top right, rgba(56,189,248,.25), transparent 25%),
        radial-gradient(circle at left, rgba(37,99,235,.18), transparent 30%),
        linear-gradient(180deg,#071426 0%,#0b1f3a 40%,#10284d 100%) !important;
}

[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at top right, rgba(56,189,248,.25), transparent 25%),
        radial-gradient(circle at left, rgba(37,99,235,.18), transparent 30%),
        linear-gradient(180deg,#071426 0%,#0b1f3a 40%,#10284d 100%) !important;
}

.main .block-container{
    max-width:1280px !important;
    padding-top:6rem !important;
    padding-bottom:4rem !important;
}

/* =========================================================
   HERO
========================================================= */

.hero-box{
    background:
        radial-gradient(circle at top right, rgba(56,189,248,.22), transparent 25%),
        linear-gradient(135deg,#0f172a 0%,#1d4ed8 100%);

    border:1px solid rgba(255,255,255,.12);

    border-radius:34px;

    padding:42px;

    margin-bottom:42px;

    box-shadow:
        0 30px 60px rgba(0,0,0,.35);
}

.hero-kicker{
    color:#7dd3fc;
    font-size:14px;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.12em;
}

.hero-title{
    color:white;
    font-size:54px;
    font-weight:1000;
    letter-spacing:-2px;
    line-height:1.05;
    margin-top:10px;
}

.hero-sub{
    color:rgba(255,255,255,.82);
    font-size:17px;
    line-height:1.7;
    max-width:900px;
    margin-top:14px;
}

/* =========================================================
   SECTION
========================================================= */

.section-title{
    color:white;
    font-size:34px;
    font-weight:1000;
    letter-spacing:-1px;
    margin-top:24px;
    margin-bottom:4px;
}

.section-sub{
    color:#cbd5e1;
    font-size:15px;
    margin-bottom:22px;
}

/* =========================================================
   PLAN CARDS
========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"]{

    background:
        linear-gradient(180deg,#0f6bff 0%,#1d4ed8 100%) !important;

    border:1px solid rgba(255,255,255,.12) !important;

    border-radius:30px !important;

    padding:10px !important;

    box-shadow:
        0 20px 50px rgba(0,0,0,.35),
        0 0 25px rgba(37,99,235,.18) !important;
}

/* text */
div[data-testid="stVerticalBlockBorderWrapper"] *{
    color:white !important;
}

/* caption */
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"]{
    color:#bfdbfe !important;
    font-weight:700 !important;
}

/* =========================================================
   METRICS
========================================================= */

div[data-testid="stMetric"]{
    background:rgba(255,255,255,.12) !important;

    border:1px solid rgba(255,255,255,.15) !important;

    border-radius:20px !important;

    padding:16px !important;

    backdrop-filter:blur(12px);
}

div[data-testid="stMetricLabel"]{
    color:#dbeafe !important;
    font-size:12px !important;
    font-weight:900 !important;
    text-transform:uppercase;
}

div[data-testid="stMetricValue"]{
    color:white !important;
    font-size:32px !important;
    font-weight:1000 !important;
}

/* =========================================================
   BUTTONS
========================================================= */

.stButton > button{

    width:100% !important;

    border:none !important;

    border-radius:18px !important;

    min-height:52px !important;

    font-size:15px !important;

    font-weight:900 !important;

    background:
        linear-gradient(135deg,#020617,#0f172a) !important;

    color:white !important;

    box-shadow:
        0 12px 25px rgba(0,0,0,.25) !important;
}

.stButton > button:hover{
    transform:translateY(-2px);
    opacity:.96;
}

/* =========================================================
   ALERT
========================================================= */

div[data-testid="stAlert"]{
    border-radius:18px !important;

    background:
        linear-gradient(135deg,#0f172a,#1e3a8a) !important;

    color:white !important;

    border:1px solid rgba(255,255,255,.10) !important;
}

/* =========================================================
   B2B
========================================================= */

.b2b-box{

    background:
        radial-gradient(circle at top right, rgba(56,189,248,.20), transparent 25%),
        linear-gradient(135deg,#020617,#0f172a);

    border-radius:34px;

    padding:40px;

    margin-top:36px;

    border:1px solid rgba(255,255,255,.08);

    box-shadow:
        0 24px 55px rgba(0,0,0,.35);
}

.b2b-title{
    color:white;
    font-size:36px;
    font-weight:1000;
    letter-spacing:-1px;
}

.b2b-sub{
    color:#cbd5e1;
    font-size:16px;
    line-height:1.7;
    max-width:900px;
    margin-top:12px;
}

/* =========================================================
   SIDEBAR
========================================================= */

section[data-testid="stSidebar"]{
    background:#06111f !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


def choose_plan(plan_key, category):
    st.session_state.selected_plan = plan_key
    st.session_state.selected_plan_category = category
    st.success("Plan ausgewählt.")


def normal_card(plan_key):
    plan = PLANS[plan_key]

    with st.container(border=True):

        st.caption(plan.get("badge", "Plan"))

        st.subheader(plan.get("label", plan_key))

        st.write(plan.get("description", ""))

        st.markdown(f"## {plan.get('price', '')}")

        st.metric(
            "Tokens",
            f"{int(plan.get('tokens', 0)):,}".replace(",", ".")
        )

        st.divider()

        for item in plan.get("highlights", []):
            st.write(f"✅ {item}")

        st.divider()

        if st.button(
            f"{plan.get('label')} auswählen",
            key=f"normal_{plan_key}",
        ):
            choose_plan(plan_key, "normal")


def football_card(plan_key):
    plan = FOOTBALL_PLANS[plan_key]

    actions = plan.get("ai_actions")
    requests = plan.get("api_requests")

    actions_text = (
        "Custom"
        if actions is None
        else f"{actions:,}".replace(",", ".")
    )

    requests_text = (
        "Custom"
        if requests is None
        else f"{requests:,}".replace(",", ".")
    )

    with st.container(border=True):

        st.caption(plan.get("badge", "Football"))

        st.subheader(plan.get("label", plan_key))

        st.write(plan.get("description", ""))

        st.markdown(f"## {plan.get('price', '')}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "AI Actions",
                actions_text
            )

        with col2:
            st.metric(
                "API Requests",
                requests_text
            )

        st.divider()

        for item in plan.get("highlights", []):
            st.write(f"⚽ {item}")

        st.divider()

        if st.button(
            f"{plan.get('label')} wählen",
            key=f"football_{plan_key}",
        ):
            choose_plan(plan_key, "football")


def render_premium():

    premium_css()

    st.markdown(
        """
<div class="hero-box">

<div class="hero-kicker">
MABYTE PREMIUM
</div>

<div class="hero-title">
One System. Infinite Intelligence.
</div>

<div class="hero-sub">
Normale MaByte-Pläne laufen über Tokens.
Football Premium ist komplett getrennt und nutzt
AI Actions, API Requests, Automation und B2B Infrastruktur.
</div>

</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="section-title">
🚀 MaByte AI Plans
</div>

<div class="section-sub">
Für Chat, Coding, Images, Reels, Video und Automation.
</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        normal_card("pro")

    with c2:
        normal_card("grand")

    with c3:
        normal_card("elite")

    st.info(
        "Token-System: 1€ = 100 Tokens. "
        "Normale Tokens bleiben für MaByte AI Actions."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="section-title">
⚽ Football AI Premium
</div>

<div class="section-sub">
Getrennte Football-Pläne für Creator,
Seiten, Apps und automatisierte Content Systeme.
</div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3, gap="large")

    with f1:
        football_card("football_starter")

    with f2:
        football_card("football_pro")

    with f3:
        football_card("football_elite")

    st.markdown(
        """
<div class="b2b-box">

<div class="b2b-title">
🏢 Football B2B / Enterprise
</div>

<div class="b2b-sub">
Für Agenturen, Football Apps, Seiten-Netzwerke und Teams
mit Custom API Limits, White Label, Webhooks,
Dedicated Infrastructure und Priority Support.
</div>

</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Enterprise Anfrage starten",
        key="enterprise_request",
    ):
        st.session_state.page = "support"
        st.rerun()