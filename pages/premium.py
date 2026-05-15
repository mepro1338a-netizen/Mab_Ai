import streamlit as st
from config import PLANS, FOOTBALL_PLANS


def premium_css():
    st.markdown(
        """
<style>
.main .block-container{
    max-width:1250px;
    padding-top:7rem;
    padding-bottom:3rem;
}

.stApp{
    background:
        radial-gradient(circle at top, rgba(59,130,246,.10), transparent 28%),
        linear-gradient(180deg,#06111f 0%, #020617 100%);
}

.premium-hero{
    background:#f8fafc;
    border-radius:28px;
    padding:32px;
    margin-bottom:30px;
    border:1px solid rgba(15,23,42,.08);
    box-shadow:0 20px 60px rgba(0,0,0,.22);
}

.hero-title{
    color:#0f172a;
    font-size:42px;
    font-weight:900;
    letter-spacing:-1px;
}

.hero-sub{
    color:#475569;
    font-size:16px;
    margin-top:10px;
    line-height:1.6;
}

.section-title{
    color:#ffffff;
    font-size:30px;
    font-weight:900;
    margin-top:28px;
}

.section-sub{
    color:#94a3b8;
    font-size:15px;
    margin-bottom:16px;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:#f8fafc!important;
    border:1px solid rgba(15,23,42,.10)!important;
    border-radius:26px!important;
    box-shadow:0 16px 40px rgba(0,0,0,.22)!important;
}

div[data-testid="stMetric"]{
    background:#ffffff;
    border:1px solid rgba(15,23,42,.08);
    border-radius:18px;
    padding:14px;
}

.stButton > button{
    border-radius:16px!important;
    min-height:46px!important;
    font-weight:900!important;
    border:none!important;
    background:linear-gradient(135deg,#2563eb,#06b6d4)!important;
    color:white!important;
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
            label="Tokens inklusive",
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
    <div class="hero-title">💎 MaByte Premium</div>
    <div class="hero-sub">
        Wähle deinen Plan. Normale MaByte-Pläne laufen über Tokens.
        Football Premium ist getrennt und nutzt AI Actions, API Limits und B2B Infrastruktur.
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

    st.markdown("## 🏢 Football B2B / Enterprise")
    st.write(
        "Für Agenturen, Football Apps, Seiten-Netzwerke und Teams mit Custom API Limits, "
        "White Label, Webhooks, Team Access und Dedicated Support."
    )

    if st.button("Enterprise Anfrage starten", key="enterprise_request", use_container_width=True):
        st.session_state.page = "support"
        st.rerun()