"""Immediate redirect to Stripe Checkout — no second-step button."""
from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

from payments import create_checkout_session
from services.billing_plans import USER_FRIENDLY_CHECKOUT_ERROR, plan_checkout_ready


def redirect_to_stripe(url: str) -> None:
    """Browser redirect to external Stripe Checkout URL."""
    safe = json.dumps(url)
    components.html(
        f"<script>window.top.location.href = {safe};</script>",
        height=0,
        width=0,
    )
    st.stop()


def checkout_and_redirect(plan_key: str, *, username: str) -> None:
    """
    Create Stripe session and redirect immediately (Grand-style for all plans).
    On error: friendly UI message; technical details are logged in payments.py.
    """
    ready, _ = plan_checkout_ready(plan_key)
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

    redirect_to_stripe(url)
