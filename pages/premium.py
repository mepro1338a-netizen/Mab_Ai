import streamlit as st
from database import get_user
from ui.premium_cards import (
    render_ai_plans_section,
    render_enterprise_block,
    render_football_plans_section,
)
from ui.premium_foundation import premium_foundation_css, render_page_hero
from ui_core import sync_session_user


def premium_css():
    premium_foundation_css(1180, 80, """
h1,h2,h3,p,span,label,
div[data-testid="stMarkdownContainer"],
div[data-testid="stCaptionContainer"]{
    color:#f8e7b0!important;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:
        linear-gradient(180deg,rgba(15,107,255,.86),rgba(12,52,150,.92))!important;
    border:1px solid rgba(255,215,128,.22)!important;
    border-radius:24px!important;
    box-shadow:
        0 18px 44px rgba(0,0,0,.30),
        inset 0 1px 0 rgba(255,255,255,.10)!important;
}

div[data-testid="stVerticalBlockBorderWrapper"] *{
    color:#fff1c2!important;
}

div[data-testid="stVerticalBlockBorderWrapper"] p{
    color:#f8e7b0!important;
    font-size:13px!important;
    line-height:1.42!important;
    margin-bottom:.55rem!important;
}

div[data-testid="stCaptionContainer"]{
    color:#ffd36a!important;
    font-size:11px!important;
    font-weight:950!important;
    letter-spacing:.08em!important;
    text-transform:uppercase!important;
}

h3{
    font-size:24px!important;
    line-height:1.1!important;
    margin-bottom:.35rem!important;
    color:#fff1c2!important;
}

.plan-bubble{
    background:
        radial-gradient(circle at 85% 15%, rgba(125,211,252,.40), transparent 35%),
        linear-gradient(135deg,#00b7ff 0%,#006dff 52%,#083b9c 100%);
    border:1px solid rgba(255,255,255,.34);
    border-radius:22px;
    padding:14px 16px;
    margin:12px 0 14px 0;
    box-shadow:
        0 14px 30px rgba(0,102,255,.30),
        inset 0 1px 0 rgba(255,255,255,.32);
}

.plan-bubble-label{
    color:#dff7ff!important;
    font-size:11px;
    font-weight:950;
    text-transform:uppercase;
    letter-spacing:.08em;
}

.plan-bubble-value{
    color:#ffffff!important;
    font-size:27px;
    font-weight:1000;
    line-height:1.1;
    margin-top:4px;
    text-shadow:0 2px 12px rgba(0,0,0,.25);
}

.plan-bubble-sub{
    color:#dff7ff!important;
    font-size:12px;
    font-weight:800;
    margin-top:5px;
}

.section-head{
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:24px;
    margin-bottom:6px;
    color:#ffd36a!important;
}

.section-head svg{color:#ffd36a!important;}

.section-head-title{
    color:#fff1c2!important;
    font-size:25px;
    font-weight:1000;
    letter-spacing:-.7px;
}

.section-sub{
    color:#f8e7b0!important;
    font-size:14px;
    margin-bottom:14px;
}

.compact-list{
    color:#fff1c2!important;
    font-size:13px;
    line-height:1.65;
    margin-top:8px;
}

.b2b{
    margin-top:24px;
    border-radius:24px;
    padding:24px 28px;
    background:
        radial-gradient(circle at 88% 20%,rgba(255,211,106,.22),transparent 30%),
        linear-gradient(135deg,#020617,#172554);
    border:1px solid rgba(255,215,128,.18);
    box-shadow:0 22px 50px rgba(0,0,0,.32);
}

.b2b-icon{color:#ffd36a!important;margin-bottom:8px;}
.b2b-title{color:#fff1c2!important;font-size:26px;font-weight:1000;}
.b2b-sub{color:#f8e7b0!important;font-size:14px;line-height:1.55;margin-top:8px;}

div[data-testid="stAlert"]{
    background:
        linear-gradient(135deg,rgba(255,211,106,.96),rgba(255,243,196,.96))!important;
    color:#111827!important;
    border-radius:16px!important;
}
div[data-testid="stAlert"] *{color:#111827!important;}
""")


def render_premium():
    premium_css()

    user = get_user(st.session_state.get("user"))
    if user:
        sync_session_user(user)

    render_page_hero(
        "MaByte Premium",
        "AI-Pläne & Football Premium",
        "Wähle deinen Plan — sichere Zahlung über Stripe.",
    )

    st.session_state.setdefault("billing_interval", "monthly")
    billing_interval = str(st.session_state.get("billing_interval") or "monthly")
    b1, b2, b3 = st.columns([1, 1, 2])
    with b1:
        st.markdown('<div class="mb-btn-gold">', unsafe_allow_html=True)
        if st.button(
            "Monatlich",
            width="stretch",
            type="primary" if billing_interval == "monthly" else "secondary",
            key="bill_monthly",
        ):
            st.session_state["billing_interval"] = "monthly"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with b2:
        st.markdown('<div class="mb-btn-gold">', unsafe_allow_html=True)
        if st.button(
            "Jährlich",
            width="stretch",
            type="primary" if billing_interval == "yearly" else "secondary",
            key="bill_yearly",
        ):
            st.session_state["billing_interval"] = "yearly"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with b3:
        if billing_interval == "yearly":
            st.caption("Jährliche Stripe-Preise — Coming Soon. Checkout nutzt vorerst Monatspreise.")
        else:
            st.caption("Monatliche Abrechnung · Stripe Checkout")

    render_ai_plans_section()
    st.info("Token-System: 1€ = 100 Tokens. Tokens gelten für normale MaByte AI Actions.")
    render_football_plans_section()
    render_enterprise_block()
