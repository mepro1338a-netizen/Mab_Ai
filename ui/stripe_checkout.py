"""Stripe Checkout — session on click, redirect on next Streamlit run (Railway-safe)."""
from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

from payments import create_checkout_session
from services.billing_plans import USER_FRIENDLY_CHECKOUT_ERROR, plan_checkout_ready

STRIPE_REDIRECT_KEY = "_stripe_checkout_url"


def process_pending_stripe_redirect() -> bool:
    """
    Run once at app entry (ui.py). Returns True if redirecting (caller should stop).
    """
    url = st.session_state.pop(STRIPE_REDIRECT_KEY, None)
    if not url:
        return False

    safe_url = html.escape(url, quote=True)
    st.markdown(
        f'<meta http-equiv="refresh" content="0;url={safe_url}">',
        unsafe_allow_html=True,
    )
    components.html(
        f"""<!DOCTYPE html><html><head>
        <meta http-equiv="refresh" content="0;url={safe_url}">
        </head><body>
        <script>window.top.location.replace({json.dumps(url)});</script>
        </body></html>""",
        height=0,
        width=0,
    )
    st.stop()
    return True


def checkout_and_redirect(plan_key: str, *, username: str) -> None:
    """Create session → store URL → rerun → process_pending_stripe_redirect()."""
    ready, _ = plan_checkout_ready(plan_key)
    if not ready:
        st.error(USER_FRIENDLY_CHECKOUT_ERROR)
        return

    with st.spinner("Stripe Checkout wird vorbereitet…"):
        url, err = create_checkout_session(username, plan_key)

    if err:
        st.error(err)
        return

    if not url:
        st.error(USER_FRIENDLY_CHECKOUT_ERROR)
        return

    st.session_state[STRIPE_REDIRECT_KEY] = url
    st.rerun()
