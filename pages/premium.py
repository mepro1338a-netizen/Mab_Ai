import streamlit as st
from config import PLANS, FOOTBALL_PLANS


ICON_AI = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.5 8.5L21 9L16 13.4L17.6 20L12 16.5L6.4 20L8 13.4L3 9L9.5 8.5L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>"""
ICON_BALL = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/><path d="M12 7L15.5 10L14.2 14.5H9.8L8.5 10L12 7Z" stroke="currentColor" stroke-width="2"/></svg>"""
ICON_B2B = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M4 21V5C4 3.9 4.9 3 6 3H18C19.1 3 20 3.9 20 5V21" stroke="currentColor" stroke-width="2"/><path d="M8 8H10M14 8H16M8 12H10M14 12H16M8 16H10M14 16H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>"""


def premium_css():
    st.markdown(
        """
<style>
.stApp,
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at 15% 5%, rgba(56,189,248,.22), transparent 28%),
        radial-gradient(circle at 90% 0%, rgba(124,58,237,.18), transparent 28%),
        linear-gradient(180deg,#071426 0%,#0b1d36 48%,#0d2a52 100%) !important;
}

[data-testid="stHeader"]{background:transparent!important;}

.main .block-container{
    max-width:1180px!important;
    padding-top:5rem!important;
    padding-bottom:2.5rem!important;
}

section[data-testid="stSidebar"]{
    background:#06111f!important;
}

.hero{
    border-radius:28px;
    padding:28px 32px;
    margin-bottom:24px;
    background:
        radial-gradient(circle at 85% 20%,rgba(125,211,252,.18),transparent 30%),
        linear-gradient(135deg,rgba(15,23,42,.94),rgba(29,78,216,.86));
    border:1px solid rgba(255,255,255,.13);
    box-shadow:0 24px 60px rgba(0,0,0,.30);
}

.hero-top{
    color:#7dd3fc;
    font-size:12px;
    font-weight:900;
    letter-spacing:.12em;
    text-transform:uppercase;
}

.hero-title{
    color:white;
    font-size:38px;
    line-height:1.04;
    font-weight:1000;
    letter-spacing:-1.4px;
    margin-top:7px;
}

.hero-sub{
    color:#dbeafe;
    font-size:15px;
    line-height:1.55;
    max-width:860px;
    margin-top:10px;
}

.section-head{
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:24px;
    margin-bottom:6px;
    color:#7dd3fc;
}

.section-head-title{
    color:white;
    font-size:25px;
    font-weight:1000;
    letter-spacing:-.7px;
}

.section-sub{
    color:#bfdbfe;
    font-size:14px;
    margin-bottom:14px;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:
        linear-gradient(180deg,rgba(15,107,255,.96),rgba(29,78,216,.94))!important;
    border:1px solid rgba(255,255,255,.16)!important;
    border-radius:24px!important;
    box-shadow:0 18px 44px rgba(0,0,0,.28)!important;
}

div[data-testid="stVerticalBlockBorderWrapper"] *{
    color:white!important;
}

div[data-testid="stVerticalBlockBorderWrapper"] p{
    color:#dbeafe!important;
    font-size:13px!important;
    line-height:1.4!important;
    margin-bottom:.55rem!important;
}

div[data-testid="stCaptionContainer"]{
    color:#bae6fd!important;
    font-size:11px!important;
    font-weight:900!important;
    letter-spacing:.08em!important;
    text-transform:uppercase!important;
}

h3{
    font-size:24px!important;
    line-height:1.1!important;
    margin-bottom:.35rem!important;
}

div[data-testid="stMarkdownContainer"] h3{
    color:white!important;
}

div[data-testid="stMetric"]{
    background:rgba(255,255,255,.14)!important;
    border:1px solid rgba(255,255,255,.16)!important;
    border-radius:16px!important;
    padding:12px!important;
}

div[data-testid="stMetricLabel"]{
    color:#dbeafe!important;
    font-size:11px!important;
    font-weight:900!important;
}

div[data-testid="stMetricValue"]{
    color:white!important;
    font-size:25px!important;
    font-weight:1000!important;
}

hr{
    margin:10px 0!important;
    border-color:rgba(255,255,255,.14)!important;
}

.stButton > button{
    border:none!important;
    border-radius:15px!important;
    min-height:44px!important;
    font-size:14px!important;
    font-weight:950!important;
    background:linear-gradient(135deg,#020617,#0f172a)!important;
    color:white!important;
    box-shadow:0 10px 22px rgba(0,0,0,.23)!important;
}

div[data-testid="stAlert"]{
    background:rgba(219,234,254,.95)!important;
    color:#0f172a!important;
    border-radius:16px!important;
    border:1px solid rgba(37,99,235,.2)!important;
}

.b2b{
    margin-top:24px;
    border-radius:24px;
    padding:24px 28px;
    background:
        radial-gradient(circle at 88% 20%,rgba(56,189,248,.22),transparent 30%),
        linear-gradient(135deg,#020617,#172554);
    border:1px solid rgba(255,255,255,.12);
    box-shadow:0 22px 50px rgba(0,0,0,.32);
}

.b2b-icon{color:#7dd3fc;margin-bottom:8px;}
.b2b-title{color:white;font-size:26px;font-weight:1000;letter-spacing:-.7px;}
.b2b-sub{color:#cbd5e1;font-size:14px;line-height:1.55;max-width:880px;margin-top:8px;}

.compact-list{
    color:#e0f2fe;
    font-size:13px;
    line-height:1.65;
    margin-top:8px;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def choose_plan(plan_key, category):
    st.session_state.selected_plan = plan_key
    st.session_state.selected_plan_category = category
    st.success("Plan ausgewählt.")


def section_header(icon, title, sub):
    st.markdown(
        f"""
<div class="section-head">
    {icon}
    <div class="section-head-title">{title}</div>
</div>
<div class="section-sub">{sub}</div>
        """,
        unsafe_allow_html=True,
    )


def normal_card(plan_key):
    plan = PLANS[plan_key]
    highlights = plan.get("highlights", [])[:3]

    with st.container(border=True):
        st.caption(plan.get("badge", "Plan"))
        st.subheader(plan.get("label", plan_key))
        st.write(plan.get("description", ""))

        st.markdown(f"### {plan.get('price', '')}")

        st.metric(
            "Tokens",
            f"{int(plan.get('tokens', 0)):,}".replace(",", "."),
        )

        st.markdown(
            "<div class='compact-list'>"
            + "<br>".join([f"✓ {x}" for x in highlights])
            + "</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            f"{plan.get('label')} auswählen",
            key=f"normal_{plan_key}",
            use_container_width=True,
        ):
            choose_plan(plan_key, "normal")


def football_card(plan_key):
    plan = FOOTBALL_PLANS[plan_key]
    highlights = plan.get("highlights", [])[:3]

    actions = plan.get("ai_actions")
    requests = plan.get("api_requests")

    actions_text = "Custom" if actions is None else f"{actions:,}".replace(",", ".")
    requests_text = "Custom" if requests is None else f"{requests:,}".replace(",", ".")

    with st.container(border=True):
        st.caption(plan.get("badge", "Football"))
        st.subheader(plan.get("label", plan_key))
        st.write(plan.get("description", ""))

        st.markdown(f"### {plan.get('price', '')}")

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Actions", actions_text)
        with m2:
            st.metric("API", requests_text)

        st.markdown(
            "<div class='compact-list'>"
            + "<br>".join([f"✓ {x}" for x in highlights])
            + "</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            f"{plan.get('label')} wählen",
            key=f"football_{plan_key}",
            use_container_width=True,
        ):
            choose_plan(plan_key, "football")


def render_premium():
    premium_css()

    st.markdown(
        """
<div class="hero">
    <div class="hero-top">MABYTE PREMIUM</div>
    <div class="hero-title">AI-Pläne für Creator, Automation und Football.</div>
    <div class="hero-sub">
        MaByte Tokens für allgemeine AI-Workflows. Football Premium separat mit Actions,
        API Requests und skalierbarer Infrastruktur.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    section_header(
        ICON_AI,
        "MaByte AI Plans",
        "Chat, Coding, Images, Reels, Video und Automation.",
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        normal_card("pro")
    with c2:
        normal_card("grand")
    with c3:
        normal_card("elite")

    st.info("Token-System: 1€ = 100 Tokens. Tokens gelten für normale MaByte AI Actions.")

    section_header(
        ICON_BALL,
        "Football AI Premium",
        "Für Creator, Fußballseiten, Apps und automatisierte Content-Systeme.",
    )

    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        football_card("football_starter")
    with f2:
        football_card("football_pro")
    with f3:
        football_card("football_elite")

    st.markdown(
        f"""
<div class="b2b">
    <div class="b2b-icon">{ICON_B2B}</div>
    <div class="b2b-title">Football Enterprise</div>
    <div class="b2b-sub">
        Für Agenturen, Football Apps und Netzwerke mit Custom Limits,
        White Label, Webhooks, Team-Zugängen und Priority Support.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Enterprise Anfrage starten", key="enterprise_request", use_container_width=True):
        st.session_state.page = "support"
        st.rerun()