"""OAuth callback for social platform connections (not login)."""
from __future__ import annotations

import streamlit as st

from database import get_user
from db.core import normalize_username
from services.session_auth import issue_session_token, sync_from_user_record
from services.social_oauth import (
    complete_social_connect,
    social_state_error_message,
    verify_social_state,
)


def _qp(param: str) -> str:
    val = st.query_params.get(param) or ""
    if isinstance(val, list):
        val = val[0] if val else ""
    return str(val).strip()


def _restore_session(username: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    sync_from_user_record(user)
    issue_session_token()
    return True


def resume_pending_social_connect() -> bool:
    """After login, finish YouTube/social connect if OAuth returned while logged out."""
    pending = st.session_state.pop("social_oauth_resume", None)
    if not pending:
        return False
    code = str(pending.get("code") or "").strip()
    platform = str(pending.get("platform") or "").strip()
    username = normalize_username(
        pending.get("username") or st.session_state.get("user") or ""
    )
    if not code or not platform or not username:
        return False
    ok, msg = complete_social_connect(platform, code, username=username)
    st.session_state.social_oauth_notice = ("success" if ok else "error", msg)
    st.session_state.page = "reels"
    st.rerun()
    return True


def render_social_oauth_callback() -> None:
    code = _qp("code")
    state = _qp("state")
    err = _qp("error")

    if err:
        st.error(f"Verbindung abgebrochen: {err}")
        if st.button("Zurück zu Reels"):
            st.session_state.page = "reels"
            st.query_params.clear()
            st.rerun()
        return

    state_user, platform, state_err = verify_social_state(state)
    if state_err:
        st.error(social_state_error_message(state_err))
        if st.button("Zurück zu Reels"):
            st.session_state.page = "reels"
            st.query_params.clear()
            st.rerun()
        return

    session_user = normalize_username(str(st.session_state.get("user") or ""))
    if session_user and session_user != state_user:
        st.error(
            "OAuth wurde mit einem anderen Account gestartet. "
            "Bitte mit dem gleichen MaByte-Account einloggen und erneut verbinden."
        )
        if st.button("Zur Startseite"):
            st.session_state.page = "home"
            st.query_params.clear()
            st.rerun()
        return

    if not st.session_state.get("logged_in") or not session_user:
        if not _restore_session(state_user):
            st.warning("Bitte zuerst bei MaByte einloggen, dann erneut verbinden.")
            st.session_state.page = "auth"
            st.session_state.social_oauth_resume = {
                "code": code,
                "state": state,
                "platform": platform,
                "username": state_user,
            }
            st.query_params.clear()
            st.rerun()
            return

    if not code:
        st.info("Warte auf OAuth…")
        return

    ok, msg = complete_social_connect(platform, code, username=state_user)
    st.query_params.clear()
    if ok:
        st.session_state.social_oauth_notice = ("success", msg)
    else:
        st.session_state.social_oauth_notice = ("error", msg)

    st.session_state.page = "reels"
    st.rerun()
