import streamlit as st

from config import PLANS, FOOTBALL_PLANS


# =========================================================
# CSS
# =========================================================

def premium_css():
    st.markdown(
        """
<style>

.main .block-container{
    max-width:1280px;
    padding-top:7rem;
    padding-bottom:3rem;
}

.premium-page{
    background:#f8fafc;
    border-radius:34px;
    padding:34px;
    border:1px solid rgba(15,23,42,.08);
    box-shadow:0 18px 55px rgba(0,0,0,.16);
}

.premium-hero{
    background:
        radial-gradient(circle at 15% 20%, rgba(59,130,246,.18), transparent 28%),
        linear-gradient(135deg,#ffffff,#eef6ff);
    border:1px solid rgba(37,99,235,.10);
    border-radius:30px;
    padding:34px;
    margin-bottom:28px;
}

.hero-kicker{
    color:#2563eb;
    font-size:14px;
    font-weight:900;
    letter-spacing:.08em;
    text-transform:uppercase;
}

.hero-title{
    color:#0f172a;
    font-size:46px;
    font-weight:950;
    letter-spacing:-1.4px;
    line-height:1.05;
    margin-top:10px;
}

.hero-sub{
    color:#475569;
    font-size:17px;
    line-height:1.65;
    max-width:850px;
    margin-top:14px;
}

.section-head{
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:20px;
    margin-top:26px;
    margin-bottom:18px;
}

.section-title{
    color:#0f172a;
    font-size:30px;
    font-weight:950;
    letter-spacing:-.8px;
}

.section-sub{
    color:#64748b;
    font-size:15px;
    margin-top:5px;
}

.plan-card{
    background:#ffffff;
    border:1px solid rgba(15,23,42,.08);
    border-radius:28px;
    padding:26px;
    min-height:520px;
    box-shadow:0 14px 35px rgba(15,23,42,.08);
    position:relative;
}

.plan-card.popular{
    border:2px solid #2563eb;
    box-shadow:0 18px 45px rgba(37,99,235,.18);
}

.plan-card.elite{
    border:2px solid #7c3aed;
    box-shadow:0 18px 45px rgba(124,58,237,.16);
}

.plan-badge{
    display:inline-block;
    padding:7px 12px;
    border-radius:999px;
    background:#eff6ff;
    color:#2563eb;
    font-size:12px;
    font-weight:900;
    margin-bottom:15px;
}

.plan-badge.purple{
    background:#f3e8ff;
    color:#7c3aed;
}

.plan-name{
    color:#0f172a;
    font-size:27px;
    font-weight:950;
    letter-spacing:-.5px;
}

.plan-desc{
    color:#64748b;
    font-size:14px;
    line-height:1.55;
    min-height:66px;
    margin-top:10px;
}

.plan-price{
    color:#0f172a;
    font-size:39px;
    font-weight:950;
    letter-spacing:-1px;
    margin-top:18px;
}

.plan-price span{
    color:#64748b;
    font-size:15px;
    font-weight:800;
}

.metric-row{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin-top:18px;
}

.metric-box{
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

.note-box{
    background:#ecfeff;
    border:1px solid rgba(6,182,212,.18);
    color:#0f172a;
    border-radius:22px;
    padding:20px;
    margin:20px 0 8px 0;
}

.b2b-box{
    background:
        linear-gradient(135deg,#111827,#1e1b4b);
    border-radius:30px;
    padding:32px;
    margin-top:20px;
    color:white;
    box-shadow:0 18px 50px rgba(15,23,42,.22);
}

.b2b-title{
    font-size:31px;
    font-weight:950;
}

.b2b-sub{
    color:#cbd5e1;
    margin-top:10px;
    line-height:1.65;
    max-width:850px;
}

.stButton > button{
    border-radius:16px!important;
    min-height:46px!important;
    font-weight:900!important;
    border:0!important;
    background:linear-gradient(135deg,#2563eb,#06b6d4)!important;
    color:white!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HELPERS
# =========================================================

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

    badge_class = "plan-badge purple" if elite else "plan-badge"

    st.markdown(
        f"""
<div class="{card_class}">
    <div class="{badge_class}">{plan.get("badge", "")}</div>
    <div class="plan-name">{plan.get("label", plan_key)}</div>
    <div class="plan-desc">{plan.get("description", "")}</div>
    <div class="plan-price">{plan.get("price", "")}</div>

    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-label">Tokens</div>
            <div class="metric-value">{int(plan.get("tokens", 0)):,}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Plan</div>
            <div class="metric-value">{plan.get("label", plan_key)}</div>
        </div>
    </div>

    <div class="features">
        """,
        unsafe_allow_html=True,
    )

    for item in plan.get("highlights", []):
        st.markdown(f'<div class="feature">✅ {item}</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    if st.button(f"{plan.get('label', plan_key)} auswählen", key=f"normal_{plan_key}", use_container_width=True):
        select_plan(plan_key, "normal")


def football_plan_card(plan_key, popular=False, elite=False):
    plan = FOOTBALL_PLANS[plan_key]
    card_class = "plan-card"

    if popular:
        card_class += " popular"

    if elite:
        card_class += " elite"

    badge_class = "plan-badge purple" if elite else "plan-badge"

    actions = plan.get("ai_actions")
    requests = plan.get("api_requests")

    actions_text = "Custom" if actions is None else f"{actions:,}"
    requests_text = "Custom" if requests is None else f"{requests:,}"

    st.markdown(
        f"""
<div class="{card_class}">
    <div class="{badge_class}">{plan.get("badge", "")}</div>
    <div class="plan-name">{plan.get("label", plan_key)}</div>
    <div class="plan-desc">{plan.get("description", "")}</div>
    <div class="plan-price">{plan.get("price", "")}</div>

    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-label">AI Actions</div>
            <div class="metric-value">{actions_text}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">API Requests</div>
            <div class="metric-value">{requests_text}</div>
        </div>
    </div>

    <div class="features">
        """,
        unsafe_allow_html=True,
    )

    for item in plan.get("highlights", []):
        st.markdown(f'<div class="feature">⚽ {item}</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    if plan_key == "football_b2b":
        if st.button("B2B Anfrage stellen", key="football_b2b", use_container_width=True):
            st.session_state.page = "support"
            st.rerun()
    else:
        if st.button(f"{plan.get('label', plan_key)} wählen", key=f"football_{plan_key}", use_container_width=True):
            select_plan(plan_key, "football")


# =========================================================
# MAIN
# =========================================================

def render_premium():
    premium_css()

    st.markdown('<div class="premium-page">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="premium-hero">
    <div class="hero-kicker">MaByte Premium</div>
    <div class="hero-title">Wähle deinen AI Plan.</div>
    <div class="hero-sub">
        Normale MaByte-Pläne bleiben für Chat, Coding, Creator Tools und Automation.
        Football Premium ist getrennt und läuft über AI Actions, API Limits und B2B Infrastruktur.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="section-head">
    <div>
        <div class="section-title">💎 MaByte AI Plans</div>
        <div class="section-sub">Für normale AI Nutzung, Content, Coding und Media Workflows.</div>
    </div>
</div>
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
<div class="note-box">
    <b>Token-Wert:</b> 1€ = 100 Tokens. Normale Tokens sind für MaByte AI, Content, Coding und Media gedacht.
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="section-head">
    <div>
        <div class="section-title">⚽ Football AI Premium</div>
        <div class="section-sub">Für Football Creator, Seiten, Apps und automatisierte Content Systeme.</div>
    </div>
</div>
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

    st.markdown("</div>", unsafe_allow_html=True)