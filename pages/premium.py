import streamlit as st
from config import PLANS, FOOTBALL_PLANS


ICON_AI = """
<svg width="28" height="28" viewBox="0 0 24 24" fill="none">
<path d="M12 2L14.4 8.2L21 9L16 13.3L17.5 20L12 16.4L6.5 20L8 13.3L3 9L9.6 8.2L12 2Z"
stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
</svg>
"""

ICON_FOOTBALL = """
<svg width="28" height="28" viewBox="0 0 24 24" fill="none">
<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
<path d="M12 7L15.8 10L14.4 14.5H9.6L8.2 10L12 7Z" stroke="currentColor" stroke-width="2"/>
<path d="M12 7V3M15.8 10L20 8.5M14.4 14.5L17 19M9.6 14.5L7 19M8.2 10L4 8.5" stroke="currentColor" stroke-width="2"/>
</svg>
"""

ICON_ENTERPRISE = """
<svg width="28" height="28" viewBox="0 0 24 24" fill="none">
<path d="M4 21V5C4 3.9 4.9 3 6 3H18C19.1 3 20 3.9 20 5V21" stroke="currentColor" stroke-width="2"/>
<path d="M8 7H10M14 7H16M8 11H10M14 11H16M8 15H10M14 15H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
"""


def premium_css():
    st.markdown(
        """
<style>
.stApp,
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at 20% 10%, rgba(56,189,248,.26), transparent 30%),
        radial-gradient(circle at 90% 0%, rgba(124,58,237,.20), transparent 28%),
        linear-gradient(180deg,#071426 0%,#0b1f3a 45%,#0f2f5f 100%) !important;
}

.main .block-container{
    max-width:1220px !important;
    padding-top:5.5rem !important;
    padding-bottom:3rem !important;
}

[data-testid="stHeader"]{
    background:transparent !important;
}

section[data-testid="stSidebar"]{
    background:#06111f !important;
}

.premium-hero{
    background:
        linear-gradient(135deg,rgba(15,23,42,.94),rgba(29,78,216,.88));
    border:1px solid rgba(255,255,255,.14);
    border-radius:30px;
    padding:30px 34px;
    margin-bottom:26px;
    color:white;
    box-shadow:0 24px 55px rgba(0,0,0,.30);
}

.hero-kicker{
    color:#7dd3fc;
    font-size:13px;
    font-weight:900;
    letter-spacing:.12em;
    text-transform:uppercase;
}

.hero-title{
    color:#ffffff;
    font-size:42px;
    line-height:1.05;
    font-weight:1000;
    letter-spacing:-1.2px;
    margin-top:8px;
}

.hero-sub{
    color:#dbeafe;
    font-size:16px;
    line-height:1.55;
    max-width:860px;
    margin-top:12px;
}

.section-row{
    display:flex;
    align-items:center;
    gap:12px;
    color:#ffffff;
    margin-top:30px;
    margin-bottom:4px;
}

.section-row svg{
    color:#7dd3fc;
}

.section-title{
    color:#ffffff;
    font-size:30px;
    font-weight:1000;
    letter-spacing:-.8px;
}

.section-sub{
    color:#bfdbfe;
    font-size:15px;
    margin-bottom:18px;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:
        linear-gradient(180deg,rgba(15,107,255,.96),rgba(29,78,216,.96)) !important;
    border:1px solid rgba(255,255,255,.18) !important;
    border-radius:26px !important;
    box-shadow:0 20px 48px rgba(0,0,0,.30) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] *{
    color:#ffffff !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] p{
    color:#dbeafe !important;
    font-size:14px !important;
    line-height:1.45 !important;
}

div[data-testid="stCaptionContainer"]{
    color:#bae6fd !important;
    font-size:12px !important;
    font-weight:900 !important;
    letter-spacing:.08em !important;
    text-transform:uppercase !important;
}

h1,h2,h3{
    color:#ffffff !important;
}

div[data-testid="stMetric"]{
    background:rgba(255,255,255,.14) !important;
    border:1px solid rgba(255,255,255,.18) !important;
    border-radius:18px !important;
    padding:14px !important;
}

div[data-testid="stMetricLabel"]{
    color:#dbeafe !important;
    font-weight:900 !important;
    font-size:12px !important;
}

div[data-testid="stMetricValue"]{
    color:#ffffff !important;
    font-size:30px !important;
    font-weight:1000 !important;
}

hr{
    border-color:rgba(255,255,255,.16) !important;
    margin:12px 0 !important;
}

.stButton > button{
    border:none !important;
    border-radius:16px !important;
    min-height:46px !important;
    font-weight:950 !important;
    background:linear-gradient(135deg,#020617,#0f172a) !important;
    color:white !important;
    box-shadow:0 12px 24px rgba(0,0,0,.25) !important;
}

div[data-testid="stAlert"]{
    background:rgba(219,234,254,.95) !important;
    color:#0f172a !important;
    border:1px solid rgba(37,99,235,.20) !important;
    border-radius:18px !important;
}

.b2b-box{
    background:
        radial-gradient(circle at 92% 8%,rgba(56,189,248,.24),transparent 32%),
        linear-gradient(135deg,#020617,#172554);
    color:white;
    border-radius:28px;
    padding:32px;
    margin-top:28px;
    border:1px solid rgba(255,255,255,.12);
    box-shadow:0 24px 55px rgba(0,0,0,.35);
}

.b2b-title{
    color:white;
    font-size:30px;
    font-weight:1000;
    letter-spacing:-.8px;
}

.b2b-sub{
    color:#cbd5e1;
    font-size:15px;
    line-height:1.6;
    max-width:900px;
    margin-top:10px;
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

        st.markdown(f"### {plan.get('price', '')}")

        st.metric(
            "Tokens",
            f"{int(plan.get('tokens', 0)):,}".replace(",", "."),
        )

        st.divider()

        for item in plan.get("highlights", [])[:5]:
            st.write(f"✓ {item}")

        st.divider()

        if st.button(
            f"{plan.get('label')} auswählen",
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

        st.markdown(f"### {plan.get('price', '')}")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("AI Actions", actions_text)

        with c2:
            st.metric("API Requests", requests_text)

        st.divider()

        for item in plan.get("highlights", [])[:5]:
            st.write(f"✓ {item}")

        st.divider()

        if st.button(
            f"{plan.get('label')} wählen",
            key=f"football_{plan_key}",
            use_container_width=True,
        ):
            choose_plan(plan_key, "football")


def render_section_header(icon_svg, title, subtitle):
    st.markdown(
        f"""
<div class="section-row">
    {icon_svg}
    <div class="section-title">{title}</div>
</div>
<div class="section-sub">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def render_premium():
    premium_css()

    st.markdown(
        """
<div class="premium-hero">
    <div class="hero-kicker">MABYTE PREMIUM</div>
    <div class="hero-title">Klare Pläne. Mehr Power. Volle Kontrolle.</div>
    <div class="hero-sub">
        Nutze MaByte mit flexiblen AI-Tokens für Content, Coding und Automationen.
        Football Premium läuft separat über AI Actions, API Requests und skalierbare Creator-Infrastruktur.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    render_section_header(
        ICON_AI,
        "MaByte AI Plans",
        "Für Chat, Coding, Images, Reels, Video und Automation.",
    )

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        normal_card("pro")

    with c2:
        normal_card("grand")

    with c3:
        normal_card("elite")

    st.info("Token-System: 1€ = 100 Tokens. Tokens gelten für normale MaByte AI Actions.")

    render_section_header(
        ICON_FOOTBALL,
        "Football AI Premium",
        "Für Creator, Fußballseiten, Apps und automatisierte Content-Systeme.",
    )

    f1, f2, f3 = st.columns(3, gap="large")

    with f1:
        football_card("football_starter")

    with f2:
        football_card("football_pro")

    with f3:
        football_card("football_elite")

    st.markdown(
        f"""
<div class="b2b-box">
    <div style="color:#7dd3fc;margin-bottom:10px;">{ICON_ENTERPRISE}</div>
    <div class="b2b-title">Football Enterprise / B2B</div>
    <div class="b2b-sub">
        Für Agenturen, Football Apps, Seiten-Netzwerke und Teams mit eigenen API Limits,
        White Label, Webhooks, Team-Zugängen und Priority Support.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Enterprise Anfrage starten",
        key="enterprise_request",
        use_container_width=True,
    ):
        st.session_state.page = "support"
        st.rerun()