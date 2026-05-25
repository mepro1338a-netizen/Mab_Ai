"""Server-side plan / admin gates — never UI-only."""
from __future__ import annotations

import streamlit as st

from config import PLANS
from database import get_user
from security import is_admin
from services.session_auth import enforce_active_session, load_server_user, server_is_admin


PLAN_RANK = {"free": 0, "pro": 1, "grand": 2, "elite": 3}


def plan_rank(plan_key: str) -> int:
    return PLAN_RANK.get(str(plan_key or "free").lower(), 0)


def require_login_server() -> dict:
    user = enforce_active_session()
    if not user:
        st.session_state.page = "auth"
        st.stop()
    return user


def require_min_plan(min_plan: str, *, redirect_page: str = "premium") -> dict:
    user = require_login_server()
    current = str(user.get("plan") or "free")
    if plan_rank(current) < plan_rank(min_plan):
        st.warning(f"Dieses Feature benötigt mindestens {PLANS.get(min_plan, {}).get('label', min_plan)}.")
        if st.button("Zu Premium", width="stretch"):
            st.session_state.page = redirect_page
            st.rerun()
        st.stop()
    return user


def require_admin_panel() -> dict:
    require_login_server()
    user = load_server_user()
    if not is_admin(user) and not _supporter_level(user):
        st.error("Kein Zugriff auf das Admin Control Panel.")
        st.session_state.page = "home"
        st.stop()
    return user or {}


def _supporter_level(user: dict | None) -> bool:
    if not user:
        return False
    role = str(user.get("role") or "user").lower()
    level = int(user.get("admin_level") or 0)
    return role in ("supporter", "moderator", "admin", "owner") or level >= 1


def can_access_plan_feature(user: dict | None, min_plan: str) -> bool:
    if not user:
        return False
    return plan_rank(str(user.get("plan") or "free")) >= plan_rank(min_plan)
