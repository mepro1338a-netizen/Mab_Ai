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

section.main .stButton > button{
    border:none!important;
    border-radius:15px!important;
    min-height:44px!important;
    font-size:14px!important;
    font-weight:950!important;
    background:
        linear-gradient(135deg,#ffd36a 0%,#f59e0b 100%)!important;
    color:#111827!important;
    box-shadow:0 12px 24px rgba(245,158,11,.24)!important;
}

section.main .stButton > button:disabled{
    opacity:.55!important;
    background:linear-gradient(135deg,#6b7280,#4b5563)!important;
    color:#e5e7eb!important;
    box-shadow:none!important;
}

/* Goldener Stripe Checkout Button */
.mb-stripe-checkout-wrap{
    margin-top:10px;
}
.mb-stripe-checkout-wrap a[data-testid="stLinkButtonLink"],
div[data-testid="stLinkButton"] a{
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    width:100%!important;
    min-height:48px!important;
    border:none!important;
    border-radius:15px!important;
    font-size:15px!important;
    font-weight:1000!important;
    text-decoration:none!important;
    color:#111827!important;
    background:linear-gradient(135deg,#ffd36a 0%,#f59e0b 55%,#ea580c 100%)!important;
    box-shadow:
        0 12px 28px rgba(245,158,11,.35),
        0 0 20px rgba(255,211,106,.25),
        inset 0 1px 0 rgba(255,255,255,.45)!important;
    transition:transform .15s ease, box-shadow .15s ease!important;
}
.mb-stripe-checkout-wrap a:hover,
div[data-testid="stLinkButton"] a:hover{
    transform:translateY(-2px)!important;
    color:#0f172a!important;
    box-shadow:
        0 16px 36px rgba(245,158,11,.45),
        0 0 28px rgba(255,211,106,.35)!important;
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
    b1, b2, b3 = st.columns([1, 1, 2])
    with b1:
        if st.button(
            "Monatlich",
            width="stretch",
            type="primary" if st.session_state.billing_interval == "monthly" else "secondary",
            key="bill_monthly",
        ):
            st.session_state.billing_interval = "monthly"
            st.rerun()
    with b2:
        if st.button(
            "Jährlich",
            width="stretch",
            type="primary" if st.session_state.billing_interval == "yearly" else "secondary",
            key="bill_yearly",
        ):
            st.session_state.billing_interval = "yearly"
            st.rerun()
    with b3:
        if st.session_state.billing_interval == "yearly":
            st.caption("Jährliche Stripe-Preise — Coming Soon. Checkout nutzt vorerst Monatspreise.")
        else:
            st.caption("Monatliche Abrechnung · Stripe Checkout")

    render_ai_plans_section()
    st.info("Token-System: 1€ = 100 Tokens. Tokens gelten für normale MaByte AI Actions.")
    render_football_plans_section()
    render_enterprise_block()
