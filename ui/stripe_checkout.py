"""Stripe Checkout — session erstellen, dann „Jetzt zur Kasse (Stripe)“ Link-Button."""
from __future__ import annotations

import streamlit as st

from payments import create_checkout_session
from services.billing_plans import USER_FRIENDLY_CHECKOUT_ERROR, plan_checkout_ready


def start_checkout_session(plan_key: str, *, username: str) -> bool:
    """
    Erstellt Stripe Checkout Session und speichert URL in session_state.
    Returns True bei Erfolg (dann Link-Button anzeigen).
    """
    ready, _ = plan_checkout_ready(plan_key)
    if not ready:
        st.error(USER_FRIENDLY_CHECKOUT_ERROR)
        return False

    # Nur ein aktiver Checkout — anderer Plan wird zurückgesetzt
    st.session_state.pop("checkout_url", None)
    st.session_state.pop("checkout_plan", None)

    with st.spinner("Stripe Checkout wird vorbereitet…"):
        url, err = create_checkout_session(username, plan_key)

    if err:
        st.error(err)
        return False

    if not url:
        st.error(USER_FRIENDLY_CHECKOUT_ERROR)
        return False

    st.session_state.checkout_url = url
    st.session_state.checkout_plan = plan_key
    return True
