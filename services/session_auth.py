"""Session security — rotation, logout, server-side validation."""
from __future__ import annotations

import secrets
import time
from typing import Any

import streamlit as st

from config import OWNER_USERNAME
from database import force_owner_account, get_user
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
    "_session_user_cache",
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
    keep_page = st.session_state.get("page")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "auth"
    st.session_state.logged_in = False
    _ = keep_page


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
    st.session_state["_session_user_cache"] = dict(user)
    # Never store password_hash in session
    for sensitive in ("password_hash", "oauth_sub", "oauth_provider"):
        if sensitive in st.session_state:
            del st.session_state[sensitive]


def load_server_user() -> dict | None:
    """Always load fresh user from DB — do not trust session alone."""
    username = str(st.session_state.get("user") or "").strip()
    if not username:
        return None
    return get_user(username)


def _cached_session_user() -> dict[str, Any] | None:
    cached = st.session_state.get("_session_user_cache")
    if isinstance(cached, dict) and cached.get("username"):
        return cached
    username = str(st.session_state.get("user") or "").strip()
    if not username:
        return None
    return {
        "username": username,
        "email": st.session_state.get("email", ""),
        "plan": st.session_state.get("plan", "free"),
        "football_plan": st.session_state.get("football_plan", "none"),
        "tokens": st.session_state.get("tokens", 0),
        "role": st.session_state.get("role", "user"),
        "admin_level": st.session_state.get("admin_level", 0),
        "is_banned": 0,
    }


def enforce_active_session() -> dict | None:
    """
    Validate session against DB (banned, exists).
    Keeps session on transient DB errors (Railway cold start / SQLite lock).
    """
    if not st.session_state.get("logged_in"):
        return None
    if not st.session_state.get("user"):
        logout_session()
        return None
    if not st.session_state.get("session_token"):
        issue_session_token()

    user: dict | None = None
    try:
        user = load_server_user()
    except Exception as exc:
        try:
            from logger import log_warning
            log_warning(f"Session DB check failed (session kept): {exc}", category="auth")
        except Exception:
            pass
        return _cached_session_user()

    if not user:
        cached = _cached_session_user()
        if cached and st.session_state.get("logged_in"):
            return cached
        logout_session()
        return None

    if int(user.get("is_banned") or 0) == 1:
        logout_session()
        return None

    user = _self_heal_owner(user)

    sync_from_user_record(user)
    return user


def _self_heal_owner(user: dict) -> dict:
    """Promote the protected owner account on login / every request.

    force_owner_account() only runs at cold start, so an owner who registers
    *after* boot would stay on the free plan until the next restart. Re-running
    it here (idempotent, owner-only) guarantees mepro1337 becomes owner/elite on
    the very next login or rerun — no redeploy or Railway CLI needed.
    """
    try:
        username = (user.get("username") or "").strip().lower()
        if username != OWNER_USERNAME:
            return user
        if user.get("role") == "owner" and int(user.get("admin_level") or 0) == 1337 \
                and user.get("plan") == "elite":
            return user
        force_owner_account()
        refreshed = get_user(username)
        return refreshed or user
    except Exception as exc:
        try:
            from logger import log_warning
            log_warning(f"owner self-heal skipped: {exc}", category="auth")
        except Exception:
            pass
        return user


def server_is_admin() -> bool:
    user = load_server_user() or _cached_session_user()
    return db_is_admin(user)


def server_is_supporter() -> bool:
    user = load_server_user() or _cached_session_user()
    if not user:
        return False
    role = str(user.get("role") or "user").lower()
    level = int(user.get("admin_level") or 0)
    return role in ("supporter", "moderator", "admin", "owner") or level >= 1


def public_user_label() -> str:
    """Safe display — username only, no email in global UI."""
    return str(st.session_state.get("user") or "User")
