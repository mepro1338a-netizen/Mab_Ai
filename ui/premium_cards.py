"""Unified Premium plan cards — one renderer for AI + Football (Grand reference)."""
from __future__ import annotations

import streamlit as st

from services.billing_plans import (
    AI_CHECKOUT_KEYS,
    FOOTBALL_CHECKOUT_KEYS,
    checkout_plans_status,
    football_metrics_text,
    is_plan_active,
    plan_catalog,
    plan_category,
    plan_checkout_ready,
)
from services.stripe_verify import (
    STRIPE_VERIFY_CACHE_KEY,
    get_stripe_verify_cache,
    refresh_stripe_verify_cache,
)
from ui.stripe_checkout import start_checkout_session


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


def _render_stripe_checkout_button(plan_key: str) -> None:
    """Goldener Stripe-Button — nur wenn Session für diesen Plan erstellt wurde."""
    if st.session_state.get("checkout_plan") != plan_key:
        return
    url = st.session_state.get("checkout_url")
    if not url:
        return

    st.markdown('<div class="mb-stripe-checkout-wrap">', unsafe_allow_html=True)
    st.link_button(
        "Jetzt zur Kasse (Stripe)",
        url,
        type="primary",
        width="stretch",
        help="Sichere Zahlung über Stripe Checkout",
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _on_subscribe(plan_key: str) -> None:
    username = st.session_state.get("user")
    if not username:
        st.warning("Bitte zuerst einloggen.")
        return
    if start_checkout_session(plan_key, username=username):
        st.success("Checkout bereit — klicke auf „Jetzt zur Kasse (Stripe)“.")


def render_plan_card(plan_key: str) -> None:
    """Einheitliche Karte — Abo-Button + goldener Stripe-Link (Grand-Referenz)."""
    plan = plan_catalog(plan_key)
    if not plan:
        return

    user_plan = str(st.session_state.get("plan", "free"))
    football_plan = str(st.session_state.get("football_plan", "none"))
    active = is_plan_active(
        plan_key, user_plan=user_plan, football_plan=football_plan
    )
    stripe_cache = get_stripe_verify_cache()
    ready, missing_reason = plan_checkout_ready(plan_key, stripe_cache=stripe_cache)

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
            if missing_reason and missing_reason != "no_checkout":
                st.caption(f"Stripe: {missing_reason}")
            elif missing_reason == "STRIPE_SECRET_KEY":
                st.caption("Stripe: STRIPE_SECRET_KEY fehlt")
        elif st.button(btn_label, key=f"subscribe_{plan_key}", width="stretch"):
            _on_subscribe(plan_key)

        _render_stripe_checkout_button(plan_key)


def render_stripe_status_banner() -> None:
    cache = get_stripe_verify_cache()
    status = checkout_plans_status(stripe_cache=cache)
    if not status["stripe_secret_ok"]:
        st.warning("Stripe: `STRIPE_SECRET_KEY` fehlt — keine Checkouts möglich.")
        return

    broken = [
        k for k, v in cache.items()
        if v.get("price_id") and not v.get("ok")
    ]
    ok_plans = [k for k, v in cache.items() if v.get("ok")]

    if ok_plans:
        labels = ", ".join(ok_plans)
        st.success(f"Stripe Checkout aktiv: {labels}")

    if broken:
        details = []
        for k in broken:
            err = (cache.get(k) or {}).get("error") or ""
            details.append(f"{k}" + (f" ({err})" if err else ""))
        st.warning(
            "Diese Pläne sind bei Stripe nicht als Abo-Preis gültig: "
            + "; ".join(details)
        )


def render_stripe_diagnostics_admin() -> None:
    """Admin: exakte Stripe-Fehler pro Plan (zum Beheben in Railway/Stripe)."""
    try:
        from services.session_auth import server_is_admin
        if not server_is_admin():
            return
    except Exception:
        return

    cache = get_stripe_verify_cache()
    with st.expander("Stripe Diagnose (Admin)", expanded=bool(
        any(not v.get("ok") for v in cache.values() if v.get("price_id"))
    )):
        for plan_key, row in cache.items():
            env = row.get("env", "")
            pid = row.get("price_id", "") or "—"
            if row.get("ok"):
                mode = "live" if row.get("livemode") else "test"
                interval = row.get("recurring_interval") or "recurring"
                short = pid if len(pid) <= 28 else f"{pid[:28]}…"
                st.markdown(
                    f"✅ **{plan_key}** — `{env}` → `{short}` "
                    f"({mode}, {interval}, mode=subscription)"
                )
            else:
                err = row.get("error") or "unbekannt"
                st.markdown(f"❌ **{plan_key}** — `{env}` → `{pid}` — {err}")
        if st.button("Stripe erneut prüfen", key="stripe_verify_refresh"):
            refresh_stripe_verify_cache()
            st.rerun()


def render_ai_plans_section() -> None:
    _section_header(
        ICON_AI,
        "MaByte AI Plans",
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
