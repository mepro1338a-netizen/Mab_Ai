"""OAuth callback for social platform connections (not login)."""
from __future__ import annotations

import streamlit as st

from services.social_oauth import complete_social_connect, verify_social_state


def render_social_oauth_callback() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()

    username = str(st.session_state.get("user") or "")
    params = st.query_params
    code = params.get("code") or ""
    state = params.get("state") or ""
    err = params.get("error") or ""

    if isinstance(code, list):
        code = code[0] if code else ""
    if isinstance(state, list):
        state = state[0] if state else ""
    if isinstance(err, list):
        err = err[0] if err else ""

    if err:
        st.error(f"Verbindung abgebrochen: {err}")
        if st.button("Zurück zu Reels"):
            st.session_state.page = "reels"
            st.query_params.clear()
            st.rerun()
        return

    state_user, platform = verify_social_state(state)
    if not state_user or state_user != username.lower():
        st.error("Ungültige OAuth-Session. Bitte erneut verbinden.")
        return

    if not code:
        st.info("Warte auf OAuth…")
        return

    ok, msg = complete_social_connect(platform, code, username=username)
    st.query_params.clear()
    if ok:
        st.session_state.social_oauth_notice = ("success", msg)
    else:
        st.session_state.social_oauth_notice = ("error", msg)

    st.session_state.page = "reels"
    st.rerun()
