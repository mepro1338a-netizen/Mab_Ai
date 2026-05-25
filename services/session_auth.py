"""Session security — rotation, logout, server-side validation."""
from __future__ import annotations

import secrets
import time
from typing import Any

import streamlit as st

from database import get_user
from security import is_admin as db_is_admin

# Keys cleared on logout / session rotation (anti-fixation)
VOLATILE_SESSION_KEYS = (
    "logged_in",
    "user",
    "email",
    "plan",
    "football_plan",
    "tokens",
    "role",
    "admin_level",
    "session_token",
    "session_issued_at",
    "checkout_url",
    "checkout_plan",
    "oauth_notice",
    "payment_notice",
    "os_guide_history",
    "os_guide_last_reply",
    "fb_odds_markets",
    "fb_odds_prediction",
    "fb_odds_result",
)


def issue_session_token() -> str:
    token = secrets.token_urlsafe(32)
    st.session_state.session_token = token
    st.session_state.session_issued_at = time.time()
    return token


def clear_volatile_session() -> None:
    for key in list(st.session_state.keys()):
        if key in VOLATILE_SESSION_KEYS or key.startswith(("fb_", "adm_", "os_")):
            del st.session_state[key]


def logout_session() -> None:
    """Full logout — clears auth state (Streamlit session)."""
    try:
        from logger import log_auth
        log_auth("logout", username=str(st.session_state.get("user") or ""), success=True)
    except Exception:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "auth"
    st.session_state.logged_in = False


def rotate_session_on_login(user: dict) -> None:
    """New session identity after successful auth (mitigates fixation)."""
    clear_volatile_session()
    issue_session_token()
    sync_from_user_record(user)
    st.session_state.logged_in = True


def sync_from_user_record(user: dict | None) -> None:
    if not user:
        return
    st.session_state.logged_in = True
    st.session_state.user = user.get("username", "User")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.football_plan = str(user.get("football_plan") or "none")
    st.session_state.tokens = int(user.get("tokens", 0) or 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = int(user.get("admin_level", 0) or 0)
    # Never store password_hash in session
    for sensitive in ("password_hash", "oauth_sub", "oauth_provider"):
        if sensitive in st.session_state:
            del st.session_state[sensitive]


def load_server_user() -> dict | None:
    """Always load fresh user from DB — do not trust session alone."""
    username = str(st.session_state.get("user") or "").strip().lower()
    if not username:
        return None
    return get_user(username)


def enforce_active_session() -> dict | None:
    """
    Validate session against DB (banned, exists).
    Returns user dict or None; clears session if invalid.
    """
    if not st.session_state.get("logged_in"):
        return None
    if not st.session_state.get("session_token"):
        issue_session_token()
    user = load_server_user()
    if not user or int(user.get("is_banned") or 0) == 1:
        logout_session()
        return None
    sync_from_user_record(user)
    return user


def server_is_admin() -> bool:
    user = load_server_user()
    return db_is_admin(user)


def server_is_supporter() -> bool:
    user = load_server_user()
    if not user:
        return False
    role = str(user.get("role") or "user").lower()
    level = int(user.get("admin_level") or 0)
    return role in ("supporter", "moderator", "admin", "owner") or level >= 1


def public_user_label() -> str:
    """Safe display — username only, no email in global UI."""
    return str(st.session_state.get("user") or "User")
