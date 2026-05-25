"""Stripe Checkout — direkte Weiterleitung zu Stripe."""
from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

from payments import create_checkout_session
from services.billing_plans import USER_FRIENDLY_CHECKOUT_ERROR, plan_checkout_ready
from services.stripe_verify import get_stripe_verify_cache


def begin_stripe_checkout(plan_key: str, *, username: str) -> None:
    """
    Erstellt Checkout-Session und leitet sofort zu Stripe weiter (ein Klick).
    """
    if not username:
        st.warning("Bitte zuerst einloggen.")
        return

    ready, _ = plan_checkout_ready(plan_key, stripe_cache=get_stripe_verify_cache())
    if not ready:
        st.error(USER_FRIENDLY_CHECKOUT_ERROR)
        return

    with st.spinner("Weiterleitung zu Stripe…"):
        url, err = create_checkout_session(username, plan_key)

    if err:
        st.error(err)
        return
    if not url:
        st.error(USER_FRIENDLY_CHECKOUT_ERROR)
        return

    st.session_state.pop("checkout_url", None)
    st.session_state.pop("checkout_plan", None)

    components.html(
        f"<script>window.top.location.href = {json.dumps(url)};</script>",
        height=0,
    )
    st.link_button(
        "Falls keine Weiterleitung: Jetzt zur Kasse (Stripe)",
        url,
        type="primary",
        width="stretch",
    )


def start_checkout_session(plan_key: str, *, username: str) -> bool:
    """Legacy — nutzt begin_stripe_checkout (direkte Weiterleitung)."""
    begin_stripe_checkout(plan_key, username=username)
    return False
