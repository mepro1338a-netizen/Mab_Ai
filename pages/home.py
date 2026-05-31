"""MaByte Home — Football Intelligence Command Center."""
from __future__ import annotations

import streamlit as st

from config import PLANS
from ui.ai_dashboard import inject_ai_dashboard_css, render_ai_dashboard


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = str(st.session_state.get("user") or "User")
    plan_key = str(st.session_state.get("plan") or "free")
    plan = PLANS.get(plan_key, PLANS["free"])
    plan_label = str(plan.get("label", plan_key))
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = (
        fb_plan.replace("football_", "").title()
        if fb_plan not in ("none", "", "free")
        else "Kein Plan"
    )
    tier = str(plan.get("badge", "Starter"))

    st.markdown('<div class="mb-fb-cc" aria-hidden="true"></div>', unsafe_allow_html=True)

    inject_ai_dashboard_css()

    render_ai_dashboard(
        user=user,
        plan_key=plan_key,
        plan=plan,
        plan_label=plan_label,
        tokens=tokens,
        fb_label=fb_label,
        tier=tier,
    )
