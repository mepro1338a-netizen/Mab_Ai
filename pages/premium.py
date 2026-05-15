import streamlit as st

from config import PLANS, FOOTBALL_PLANS


def premium_css():
    st.markdown(
        """
<style>
.premium-hero{
    border-radius:28px;
    padding:34px;
    margin-bottom:28px;
    background:
        radial-gradient(circle at 20% 20%, rgba(56,189,248,.20), transparent 28%),
        linear-gradient(135deg, rgba(15,23,42,.96), rgba(10,25,55,.82));
    border:1px solid rgba(125,211,252,.16);
}

.premium-title{
    color:white;
    font-size:42px;
    font-weight:950;
    letter-spacing:-1px;
}

.premium-sub{
    color:#cbd5e1;
    font-size:17px;
    margin-top:10px;
}

.section-title{
    color:white;
    font-size:30px;
    font-weight:950;
    margin-top:30px;
    margin-bottom:8px;
}

.section-sub{
    color:#94a3b8;
    font-size:15px;
    margin-bottom:22px;
}

.plan-card{
    min-height:430px;
    border-radius:26px;
    padding:26px;
    background:linear-gradient(145deg,rgba(10,20,40,.95),rgba(15,30,60,.72));
    border:1px solid rgba(96,165,250,.12);
    box-shadow:0 18px 50px rgba(0,0,0,.22);
}

.plan-card.highlight{
    border-color:rgba(168,85,247,.42);
    box-shadow:0 0 45px rgba(168,85,247,.18);
}

.plan-label{
    color:white;
    font-size:25px;
    font-weight:950;
}

.plan-badge{
    display:inline-block;
    margin-top:10px;
    padding:6px 12px;
    border-radius:999px;
    background:linear-gradient(135deg,#2563eb,#38bdf8);
    color:white;
    font-size:12px;
    font-weight:900;
}

.plan-price{
    color:white;
    font-size:38px;
    font-weight:1000;
    margin-top:18px;
}

.plan-desc{
    color:#94a3b8;
    font-size:14px;
    min-height:42px;
    margin-top:8px;
}

.plan-feature{
    color:#dbeafe;
    font-size:14px;
    font-weight:700;
    margin:9px 0;
}

.plan-metric{
    border-radius:18px;
    padding:14px;
    background:rgba(15,23,42,.62);
    border:1px solid rgba(125,211,252,.10);
    margin-top:14px;
}

.metric-label{
    color:#94a3b8;
    font-size:12px;
    font-weight:800;
}

.metric-value{
    color:white;
    font-size:22px;
    font-weight:950;
}

.b2b-card{
    border-radius:28px;
    padding:32px;
    margin-top:24px;
    background:
        radial-gradient(circle at 85% 30%, rgba(168,85,247,.20), transparent 30%),
        linear-gradient(135deg,rgba(15,23,42,.96),rgba(30,20,70,.78));
    border:1px solid rgba(168,85,247,.28);
    box-shadow:0 0 50px rgba(168,85,247,.14);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def select_plan(plan_key, category="normal"):
    st.session_state.selected_plan = plan_key
    st.session_state.selected_plan_category = category
    st.success("Plan ausgewählt. Stripe Checkout wird als nächstes verbunden.")


def normal_plan_card(plan_key, highlight=False):
    plan = PLANS[plan_key]
    css_class = "plan-card highlight" if highlight else "plan-card"

    st.markdown(
        f"""
<div class="{css_class}">
    <div class="plan-label">{plan.get("label", plan_key)}</div>
    <div class="plan-badge">{plan.get("badge", "")}</div>
    <div class="plan-price">{plan.get("price", "")}</div>
    <div class="plan-desc">{plan.get("description", "")}</div>

    <div class="plan-metric">
        <div class="metric-label">Tokens inklusive</div>
        <div class="metric-value">{int(plan.get("tokens", 0)):,}</div>
    </div>
        """,
        unsafe_allow_html=True,
    )

    for item in plan.get("highlights", []):
        st.markdown(f'<div class="plan-feature">✅ {item}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        f"Upgrade auf {plan.get('label', plan_key)}",
        key=f"buy_normal_{plan_key}",
        use_container_width=True,
    ):
        select_plan(plan_key, "normal")


def football_plan_card(plan_key, highlight=False):
    plan = FOOTBALL_PLANS[plan_key]
    css_class = "plan-card highlight" if highlight else "plan-card"

    ai_actions = plan.get("ai_actions")
    api_requests = plan.get("api_requests")

    ai_actions_text = "Custom" if ai_actions is None else f"{ai_actions:,}"
    api_requests_text = "Custom" if api_requests is None else f"{api_requests:,}"

    st.markdown(
        f"""
<div class="{css_class}">
    <div class="plan-label">{plan.get("label", plan_key)}</div>
    <div class="plan-badge">{plan.get("badge", "")}</div>
    <div class="plan-price">{plan.get("price", "")}</div>
    <div class="plan-desc">{plan.get("description", "")}</div>

    <div class="plan-metric">
        <div class="metric-label">Football AI Actions</div>
        <div class="metric-value">{ai_actions_text}</div>
    </div>

    <div class="plan-metric">
        <div class="metric-label">Football API Requests</div>
        <div class="metric-value">{api_requests_text}</div>
    </div>
        """,
        unsafe_allow_html=True,
    )

    for item in plan.get("highlights", []):
        st.markdown(f'<div class="plan-feature">⚽ {item}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if plan_key == "football_b2b":
        if st.button("B2B Anfrage starten", key="football_b2b_request", use_container_width=True):
            st.session_state.page = "support"
            st.rerun()
    else:
        if st.button(
            f"Football Plan wählen",
            key=f"buy_football_{plan_key}",
            use_container_width=True,
        ):
            select_plan(plan_key, "football")


def render_premium():
    premium_css()

    st.markdown(
        """
<div class="premium-hero">
    <div class="premium-title">💎 MaByte Premium</div>
    <div class="premium-sub">
        Wähle zwischen normalen AI-Tokens für MaByte und separaten Football AI Plänen für Creator, Seiten und B2B Systeme.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">🚀 MaByte AI Plans</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Für normale AI Nutzung: Chat, Coding, Images, Media und Automationen.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        normal_plan_card("pro")

    with c2:
        normal_plan_card("grand", highlight=True)

    with c3:
        normal_plan_card("elite")

    st.divider()

    st.markdown('<div class="section-title">⚽ Football AI Premium</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Getrennte Football-Pläne mit AI Actions, API Limits, Auto Posting und B2B Infrastruktur.</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)

    with f1:
        football_plan_card("football_starter")

    with f2:
        football_plan_card("football_pro", highlight=True)

    with f3:
        football_plan_card("football_elite")

    st.markdown(
        """
<div class="b2b-card">
    <div class="plan-label">🏢 Football B2B / Enterprise</div>
    <div class="plan-desc">
        Für Agenturen, Football Apps, Seiten-Netzwerke und Teams mit Custom API Limits, White Label, Webhooks und Dedicated Support.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🏢 B2B Anfrage stellen", key="b2b_footer", use_container_width=True):
        st.session_state.page = "support"
        st.rerun()