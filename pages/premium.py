import streamlit as st
from config import PLANS, FOOTBALL_PLANS


def premium_css():
    st.markdown(
        """
<style>

/* ===== HARD RESET PREMIUM PAGE ===== */

.stApp{
    background:
        linear-gradient(180deg,#eaf6ff 0%,#f8fafc 45%,#ffffff 100%) !important;
}

.main .block-container{
    max-width:1280px !important;
    padding-top:6.5rem !important;
    padding-bottom:4rem !important;
}

/* falls globales Dark CSS reinfunkt */
[data-testid="stAppViewContainer"]{
    background:
        linear-gradient(180deg,#eaf6ff 0%,#f8fafc 45%,#ffffff 100%) !important;
}

[data-testid="stHeader"]{
    background:transparent !important;
}

/* ===== HERO ===== */

.premium-hero{
    background:
        radial-gradient(circle at 85% 10%,rgba(56,189,248,.26),transparent 30%),
        linear-gradient(135deg,#0f6bff 0%,#00c2ff 100%) !important;

    border-radius:34px;
    padding:34px 38px;
    margin-bottom:32px;

    color:white;

    box-shadow:
        0 24px 55px rgba(37,99,235,.28);

    border:1px solid rgba(255,255,255,.24);
}

.hero-kicker{
    font-size:13px;
    font-weight:950;
    letter-spacing:.12em;
    text-transform:uppercase;
    opacity:.9;
}

.hero-title{
    font-size:48px;
    font-weight:1000;
    letter-spacing:-1.5px;
    line-height:1.05;
    margin-top:10px;
}

.hero-sub{
    max-width:850px;
    margin-top:14px;
    font-size:17px;
    line-height:1.65;
    color:rgba(255,255,255,.88);
}

/* ===== SECTION ===== */

.section-title{
    color:#0f172a !important;
    font-size:32px;
    font-weight:1000;
    letter-spacing:-.8px;
    margin-top:34px;
    margin-bottom:4px;
}

.section-sub{
    color:#475569 !important;
    font-size:15px;
    margin-bottom:20px;
}

/* ===== STREAMLIT CARD WRAPPER ===== */

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:
        linear-gradient(180deg,#0b8dff 0%,#075bcc 100%) !important;

    border:1px solid rgba(255,255,255,.35) !important;
    border-radius:30px !important;

    box-shadow:
        0 22px 50px rgba(37,99,235,.24) !important;

    overflow:hidden !important;
}

/* text in container */
div[data-testid="stVerticalBlockBorderWrapper"] *{
    color:white !important;
}

/* captions */
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"]{
    color:rgba(255,255,255,.78) !important;
}

/* metric cards */
div[data-testid="stMetric"]{
    background:rgba(255,255,255,.16) !important;
    border:1px solid rgba(255,255,255,.22) !important;
    border-radius:20px !important;
    padding:16px !important;
    backdrop-filter:blur(12px);
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricLabel"]{
    color:rgba(255,255,255,.78) !important;
    font-size:12px !important;
    font-weight:900 !important;
}

div[data-testid="stMetricValue"]{
    color:white !important;
    font-size:30px !important;
    font-weight:1000 !important;
}

/* headings */
h1,h2,h3{
    color:inherit !important;
}

/* dividers */
hr{
    border-color:rgba(255,255,255,.18) !important;
}

/* buttons */
.stButton > button{
    border-radius:17px !important;
    min-height:48px !important;
    font-weight:950 !important;
    border:none !important;

    background:
        linear-gradient(135deg,#0f172a,#1e293b) !important;

    color:white !important;

    box-shadow:
        0 12px 25px rgba(15,23,42,.22) !important;
}

.stButton > button:hover{
    transform:translateY(-1px);
    opacity:.94;
}

/* info box */
div[data-testid="stAlert"]{
    background:#dbeafe !important;
    color:#0f172a !important;
    border:1px solid rgba(37,99,235,.18) !important;
    border-radius:20px !important;
}

/* B2B */
.b2b-box{
    background:
        radial-gradient(circle at 90% 15%,rgba(56,189,248,.22),transparent 35%),
        linear-gradient(135deg,#0f172a,#1d4ed8) !important;

    color:white;
    border-radius:32px;
    padding:34px;
    margin-top:30px;

    box-shadow:0 24px 55px rgba(15,23,42,.24);
}

.b2b-title{
    font-size:34px;
    font-weight:1000;
    letter-spacing:-.7px;
}

.b2b-sub{
    color:rgba(255,255,255,.82);
    line-height:1.65;
    max-width:880px;
    margin-top:10px;
}

/* sidebar bleibt wie sie ist */
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
    st.success("Plan ausgewählt. Stripe Checkout verbinden wir als nächstes.")


def normal_card(plan_key):
    plan = PLANS[plan_key]

    with st.container(border=True):
        st.caption(plan.get("badge", "Plan"))
        st.subheader(plan.get("label", plan_key))

        st.write(plan.get("description", ""))

        st.markdown(f"## {plan.get('price', '')}")

        st.metric(
            label="Tokens",
            value=f"{int(plan.get('tokens', 0)):,}".replace(",", "."),
        )

        st.divider()

        for item in plan.get("highlights", []):
            st.write(f"✅ {item}")

        st.divider()

        if st.button(
            f"{plan.get('label', plan_key)} auswählen",
            key=f"normal_{plan_key}",
            use_container_width=True,
        ):
            choose_plan(plan_key, "normal")


def football_card(plan_key):
    plan = FOOTBALL_PLANS[plan_key]

    actions = plan.get("ai_actions")
    requests = plan.get("api_requests")

    actions_text = "Custom" if actions is None else f"{actions:,}".replace(",", ".")
    requests_text = "Custom" if requests is None else f"{requests:,}".replace(",", ".")

    with st.container(border=True):
        st.caption(plan.get("badge", "Football"))
        st.subheader(plan.get("label", plan_key))

        st.write(plan.get("description", ""))

        st.markdown(f"## {plan.get('price', '')}")

        m1, m2 = st.columns(2)

        with m1:
            st.metric(
                label="AI Actions",
                value=actions_text,
            )

        with m2:
            st.metric(
                label="API Requests",
                value=requests_text,
            )

        st.divider()

        for item in plan.get("highlights", []):
            st.write(f"⚽ {item}")

        st.divider()

        if st.button(
            f"{plan.get('label', plan_key)} wählen",
            key=f"football_{plan_key}",
            use_container_width=True,
        ):
            choose_plan(plan_key, "football")


def render_premium():
    premium_css()

    st.markdown(
        """
<div class="premium-hero">
    <div class="hero-kicker">MaByte Premium</div>
    <div class="hero-title">Wähle deinen AI Plan.</div>
    <div class="hero-sub">
        Normale MaByte-Pläne laufen über Tokens. Football Premium ist getrennt und nutzt
        AI Actions, API Limits und B2B Infrastruktur.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="section-title">🚀 MaByte AI Plans</div>
<div class="section-sub">Für Chat, Coding, Images, Reels, Video und Automation.</div>
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

    st.info("Token-System: 1€ = 100 Tokens. Normale Tokens bleiben für MaByte AI Actions.")

    st.markdown(
        """
<div class="section-title">⚽ Football AI Premium</div>
<div class="section-sub">Getrennte Football-Pläne für Creator, Seiten, Apps und automatisierte Content Systeme.</div>
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
    <div class="b2b-title">🏢 Football B2B / Enterprise</div>
    <div class="b2b-sub">
        Für Agenturen, Football Apps, Seiten-Netzwerke und Teams mit Custom API Limits,
        White Label, Webhooks, Team Access und Dedicated Support.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Enterprise Anfrage starten", key="enterprise_request", use_container_width=True):
        st.session_state.page = "support"
        st.rerun()