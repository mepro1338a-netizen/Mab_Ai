"""MaByte Home — minimal pro dashboard."""
from __future__ import annotations

import streamlit as st

from config import PLANS
from database import successful_jobs_count, workspace_activity_score
from ui.dashboard_ui import (
    format_num,
    inject_dashboard_css,
    nav,
    render_daily_limits,
    render_header,
    render_quick_actions,
    render_recent_activity,
    render_stats,
    render_workspace_matrix,
)


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    inject_dashboard_css()

    user = str(st.session_state.get("user") or "User")
    plan_key = str(st.session_state.get("plan") or "free")
    plan = PLANS.get(plan_key, PLANS["free"])
    plan_label = str(plan.get("label", plan_key))
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = (
        fb_plan.replace("football_", "").title()
        if fb_plan not in ("none", "", "free")
        else "—"
    )
    tier = str(plan.get("badge", "Starter"))

    st.markdown('<div class="mb-dash" aria-hidden="true"></div>', unsafe_allow_html=True)

    render_header(user=user)
    render_stats(
        plan_label=plan_label,
        tokens=tokens,
        football_label=fb_label,
        tier=tier,
    )
    render_quick_actions()

    col_ws, col_lim = st.columns([1.4, 1], gap="medium")
    with col_ws:
        with st.container(border=True):
            render_workspace_matrix(plan)
    with col_lim:
        with st.container(border=True):
            render_daily_limits(plan_key)

    with st.container(border=True):
        render_recent_activity(user)

    jobs = successful_jobs_count(user)
    score = workspace_activity_score(user)
    st.markdown(
        f'<p class="mb-dash-foot">Erfolgreiche Jobs: {format_num(jobs)} · Workspace-Score: {score}/100</p>',
        unsafe_allow_html=True,
    )

    inject_dashboard_css()
