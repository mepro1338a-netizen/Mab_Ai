"""Profile page — usage, limits, payments."""

from __future__ import annotations

import html

import streamlit as st

from config import PLANS, TOKEN_COSTS
from database import get_user, list_purchases
from ui.components import (
    inject_dashboard_css,
    render_daily_limits,
    render_header,
    render_payments,
    render_recent_activity,
    render_stats,
)
from ui_core import require_login, sync_session_user


def _refresh_user() -> None:
    user = get_user(st.session_state.get("user"))
    if user:
        sync_session_user(user)


def _current_plan_key() -> str:
    return str(st.session_state.get("plan", "free") or "free")


def _current_plan() -> dict:
    return dict(PLANS.get(_current_plan_key(), PLANS["free"]))


def _nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def render_dashboard() -> None:
    require_login()
    _refresh_user()
    inject_dashboard_css()

    plan_key = _current_plan_key()
    plan = _current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = (
        fb_plan.replace("football_", "").title()
        if fb_plan not in ("none", "", "free")
        else "—"
    )
    user = str(st.session_state.get("user", "User"))
    username = str(st.session_state.get("user") or "")

    st.markdown('<div class="mb-dash" aria-hidden="true"></div>', unsafe_allow_html=True)
    render_header(user=user, greeting=f"Profil · {html.escape(user)} — Nutzung, Limits und Zahlungen.")
    render_stats(
        plan_label=str(plan.get("label", plan_key)),
        tokens=tokens,
        football_label=fb_label,
        tier=str(plan.get("badge", "Starter")),
    )

    if st.button("Zurück zum Dashboard", key="dash_go_home", width="stretch"):
        _nav("home")

    with st.container(border=True):
        render_daily_limits(plan_key)

    with st.expander("Token-Kosten (Referenz)", expanded=False):
        token_rows = [
            {"Workspace": "AI Chat", "Action": "Prompt", "Cost": TOKEN_COSTS.get("chat", 1)},
            {"Workspace": "Code", "Action": "Coding", "Cost": TOKEN_COSTS.get("coding", 10)},
            {"Workspace": "Image", "Action": "Bild", "Cost": TOKEN_COSTS.get("image", 10)},
            {"Workspace": "Video", "Action": "Video", "Cost": TOKEN_COSTS.get("video_base", 10)},
            {"Workspace": "Football", "Action": "Analyse", "Cost": TOKEN_COSTS.get("football_report", 80)},
            {"Workspace": "Content", "Action": "Automation", "Cost": TOKEN_COSTS.get("automation_job", 100)},
        ]
        st.dataframe(token_rows, width="stretch", hide_index=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            render_recent_activity(username, limit=12)

    with col_b:
        with st.container(border=True):
            render_payments(username, purchases=list_purchases(username))
