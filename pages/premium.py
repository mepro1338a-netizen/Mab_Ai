import streamlit as st
from config import PLANS, FOOTBALL_PLANS


def premium_css():
    st.markdown(
        """
<style>
.main .block-container{
    max-width:1320px;
    padding-top:7rem;
    padding-bottom:3rem;
}

.premium-wrap{
    background:#f8fafc;
    border-radius:34px;
    padding:34px;
}

.premium-hero{
    background:linear-gradient(135deg,#ffffff,#eef6ff);
    border:1px solid rgba(15,23,42,.08);
    border-radius:30px;
    padding:34px;
    margin-bottom:30px;
}

.hero-title{
    color:#0f172a;
    font-size:48px;
    font-weight:950;
    letter-spacing:-1.5px;
}

.hero-sub{
    color:#475569;
    font-size:17px;
    line-height:1.6;
    margin-top:12px;
}

.section-title{
    color:#0f172a;
    font-size:32px;
    font-weight:950;
    margin:34px 0 6px 0;
}

.section-sub{
    color:#64748b;
    font-size:15px;
    margin-bottom:20px;
}

.plan-card{
    background:#ffffff;
    color:#0f172a;
    border:1px solid rgba(15,23,42,.08);
    border-radius:28px;
    padding:26px;
    min-height:560px;
    box-shadow:0 14px 35px rgba(15,23,42,.10);
}

.plan-card.popular{
    border:2px solid #2563eb;
}

.plan-card.elite{
    border:2px solid #7c3aed;
}

.badge{
    display:inline-block;
    padding:7px 13px;
    border-radius:999px;
    background:#eff6ff;
    color:#2563eb;
    font-size:12px;
    font-weight:900;
    margin-bottom:16px;
}

.badge.purple{
    background:#f3e8ff;
    color:#7c3aed;
}

.plan-name{
    font-size:30px;
    font-weight:950;
    line-height:1.12;
}

.plan-desc{
    color:#64748b;
    font-size:14px;
    line-height:1.55;
    min-height:64px;
    margin-top:12px;
}

.plan-price{
    font-size:42px;
    font-weight:950;
    margin-top:20px;
    line-height:1.15;
}

.metric-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:12px;
    margin-top:20px;
}

.metric{
    background:#f8fafc;
    border:1px solid rgba(15,23,42,.07);
    border-radius:18px;
    padding:14px;
}

.metric-label{
    color:#64748b;
    font-size:12px;
    font-weight:800;
}

.metric-value{
    color:#0f172a;
    font-size:20px;
    font-weight:950;
    margin-top:4px;
}

.features{
    margin-top:20px;
}

.feature{
    color:#334155;
    font-size:14px;
    font-weight:650;
    padding:9px 0;
    border-bottom:1px solid rgba(15,23,42,.06);
}

.note{
    background:#ecfeff;
    border:1px solid rgba(6,182,212,.20);
    color:#0f172a;
    border-radius:22px;
    padding:20px;
    margin:24px 0;
}

.b2b{
    background:linear-gradient(135deg,#111827,#1e1b4b);
    color:white;
    border-radius:30px;
    padding:32px;
    margin-top:30px;
}

.b2b h2{
    font-size:32px;
    margin:0;
}

.b2b p{
    color:#cbd5e1;
    line-height:1.6;
}

.stButton > button{
    border-radius:16px!important;
    min-height:46px!important;
    font-weight:900!important;
    border:0!important;
    background:linear-gradient(135deg,#2563eb,#06b6d4)!important;
    color:white!important;
    margin-top:12px!important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def select_plan(plan_key, category):
    st.session_state.selected_plan = plan_key
    st.session_state.selected_plan_category = category
    st.success("Plan ausgewählt. Stripe Checkout verbinden wir als nächstes.")


def normal_plan_card(plan_key, popular=False, elite=False):
    plan = PLANS[plan_key]

    card_class = "plan-card"
    if popular:
        card_class += " popular"
    if elite:
        card_class += " elite"

    badge_class = "badge purple" if elite else "badge"

    features_html = "".join(
        [f'<div class="feature">✅ {item}</div>' for item in plan.get("highlights", [])]
    )

    html = f"""
<div class="{card_class}">
    <div class="{badge_class}">{plan.get("badge", "")}</div>

    <div class="plan-name">{plan.get("label", plan_key)}</div>

    <div class="plan-desc">{plan.get("description", "")}</div>

    <div class="plan-price">{plan.get("price", "")}</div>

    <div class="metric-grid">
        <div class="metric">
            <div class="metric-label">Tokens</div>
            <div class="metric-value">{int(plan.get("tokens", 0)):,}</div>
        </div>

        <div class="metric">
            <div class="metric-label">Kategorie</div>
            <div class="metric-value">AI</div>
        </div>
    </div>

    <div class="features">
        {features_html}
    </div>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)

    if st.button(
        f"{plan.get('label', plan_key)} auswählen",
        key=f"normal_{plan_key}",
        use_container_width=True,
    ):
        select_plan(plan_key, "normal")


def football_plan_card(plan_key, popular=False, elite=False):
    plan = FOOTBALL_PLANS[plan_key]

    card_class = "plan-card"
    if popular:
        card_class += " popular"
    if elite:
        card_class += " elite"

    badge_class = "badge purple" if elite else "badge"

    actions = plan.get("ai_actions")
    requests = plan.get("api_requests")

    actions_text = "Custom" if actions is None else f"{actions:,}"
    requests_text = "Custom" if requests is None else f"{requests:,}"

    features_html = "".join(
        [f'<div class="feature">⚽ {item}</div>' for item in plan.get("highlights", [])]
    )

    html = f"""
<div class="{card_class}">
    <div class="{badge_class}">{plan.get("badge", "")}</div>

    <div class="plan-name">{plan.get("label", plan_key)}</div>

    <div class="plan-desc">{plan.get("description", "")}</div>

    <div class="plan-price">{plan.get("price", "")}</div>

    <div class="metric-grid">
        <div class="metric">
            <div class="metric-label">AI Actions</div>
            <div class="metric-value">{actions_text}</div>
        </div>

        <div class="metric">
            <div class="metric-label">API Requests</div>
            <div class="metric-value">{requests_text}</div>
        </div>
    </div>

    <div class="features">
        {features_html}
    </div>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)

    if st.button(
        f"{plan.get('label', plan_key)} wählen",
        key=f"football_{plan_key}",
        use_container_width=True,
    ):
        select_plan(plan_key, "football")


def render_premium():
    premium_css()

    st.markdown('<div class="premium-wrap">', unsafe_allow_html=True)

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
        normal_plan_card("pro")

    with c2:
        normal_plan_card("grand", popular=True)

    with c3:
        normal_plan_card("elite", elite=True)

    st.markdown(
        """
<div class="note">
    <b>Token-System:</b> 1€ = 100 Tokens. Deine normalen Tokens bleiben für MaByte AI Actions.
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="section-title">⚽ Football AI Premium</div>
<div class="section-sub">Getrennte Football-Pläne für Creator, Seiten, Apps und automatisierte Content Systeme.</div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3, gap="large")

    with f1:
        football_plan_card("football_starter")

    with f2:
        football_plan_card("football_pro", popular=True)

    with f3:
        football_plan_card("football_elite", elite=True)

    st.markdown(
        """
<div class="b2b">
    <h2>🏢 Football B2B / Enterprise</h2>
    <p>
        Für Agenturen, Football Apps, Seiten-Netzwerke und Teams mit Custom API Limits,
        White Label, Webhooks, Team Access und Dedicated Support.
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Enterprise Anfrage starten", key="enterprise_request", use_container_width=True):
        st.session_state.page = "support"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)