"""Unified Premium plan cards — one renderer for AI + Football."""
from __future__ import annotations

import streamlit as st

from services.billing_plans import (
    AI_CHECKOUT_KEYS,
    FOOTBALL_CHECKOUT_KEYS,
    football_metrics_text,
    is_plan_active,
    plan_catalog,
    plan_category,
    plan_checkout_ready,
)
from services.stripe_verify import get_stripe_verify_cache
from ui.stripe_checkout import begin_stripe_checkout


ICON_AI = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.5 8.5L21 9L16 13.4L17.6 20L12 16.5L6.4 20L8 13.4L3 9L9.5 8.5L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>"""
ICON_BALL = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/><path d="M12 7L15.5 10L14.2 14.5H9.8L8.5 10L12 7Z" stroke="currentColor" stroke-width="2"/></svg>"""
ICON_B2B = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M4 21V5C4 3.9 4.9 3 6 3H18C19.1 3 20 3.9 20 5V21" stroke="currentColor" stroke-width="2"/><path d="M8 8H10M14 8H16M8 12H10M14 12H16M8 16H10M14 16H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>"""


def _bubble(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
<div class="plan-bubble">
    <div class="plan-bubble-label">{label}</div>
    <div class="plan-bubble-value">{value}</div>
    <div class="plan-bubble-sub">{sub}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _section_header(icon: str, title: str, sub: str) -> None:
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


def _on_subscribe(plan_key: str) -> None:
    username = st.session_state.get("user")
    begin_stripe_checkout(plan_key, username=username or "")


def render_plan_card(plan_key: str) -> None:
    """Plan-Karte — ein Klick startet Stripe Checkout."""
    plan = plan_catalog(plan_key)
    if not plan:
        return

    user_plan = str(st.session_state.get("plan", "free"))
    football_plan = str(st.session_state.get("football_plan", "none"))
    active = is_plan_active(
        plan_key, user_plan=user_plan, football_plan=football_plan
    )
    stripe_cache = get_stripe_verify_cache()
    ready, _ = plan_checkout_ready(plan_key, stripe_cache=stripe_cache)

    highlights = plan.get("highlights", [])[:3]
    label = plan.get("label", plan_key)
    is_football = plan_category(plan_key) == "football"
    btn_label = f"{label} abonnieren"

    with st.container(border=True):
        st.caption(plan.get("badge", "Football" if is_football else "Plan"))

        if is_football:
            _bubble("Plan", label, "Football Premium")
            st.write(plan.get("description", ""))
            st.markdown(f"### {plan.get('price', '')}")
            m_label, m_val, m_sub = football_metrics_text(plan_key, plan)
            _bubble(m_label, m_val, m_sub)
        else:
            token_text = f"{int(plan.get('tokens', 0)):,}".replace(",", ".")
            _bubble("Plan", label, f"{token_text} Tokens")
            st.write(plan.get("description", ""))
            st.markdown(f"### {plan.get('price', '')}")
            _bubble("Tokens", token_text, "inklusive")

        st.markdown(
            "<div class='compact-list'>"
            + "<br>".join(f"✓ {x}" for x in highlights)
            + "</div>",
            unsafe_allow_html=True,
        )

        if plan_key == "football_elite":
            st.caption("* Bald: Zugriff auf alle Sport-APIs (NBA, NFL, F1, …)")

        if active:
            st.button("Aktiv", key=f"subscribe_{plan_key}", width="stretch", disabled=True)
        elif not ready:
            st.button(btn_label, key=f"subscribe_{plan_key}", width="stretch", disabled=True)
            st.caption("Dieser Plan ist derzeit nicht buchbar.")
        elif st.button(btn_label, key=f"subscribe_{plan_key}", width="stretch", type="primary"):
            _on_subscribe(plan_key)


def render_ai_plans_section() -> None:
    _section_header(
        ICON_AI,
        "MaByte AI Pläne",
        "Chat, Coding, Images, Reels, Video und Automation.",
    )
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, key in zip((c1, c2, c3), AI_CHECKOUT_KEYS):
        with col:
            render_plan_card(key)


def render_football_plans_section() -> None:
    _section_header(
        ICON_BALL,
        "Football AI Premium",
        "Für Creator, Fußballseiten, Apps und automatisierte Content-Systeme.",
    )
    f1, f2, f3 = st.columns(3, gap="medium")
    for col, key in zip((f1, f2, f3), FOOTBALL_CHECKOUT_KEYS):
        with col:
            render_plan_card(key)


def render_enterprise_block() -> None:
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
    if st.button("Enterprise Anfrage starten", key="enterprise_request", width="stretch"):
        st.session_state.page = "support"
        st.rerun()
