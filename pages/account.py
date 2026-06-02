"""Profile page (minimal): usage, limits, payments."""

from __future__ import annotations

import html

import streamlit as st

from config import PLANS, TOKEN_COSTS
from database import get_user, list_purchases
from ui.dashboard_ui import (
    inject_dashboard_css,
    render_daily_limits,
    render_header,
    render_recent_activity,
    render_stats,
)
from ui.os_helper import render_os_guide_dashboard
from ui.premium_foundation import render_empty_state
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

    st.markdown('<div class="mb-dash" aria-hidden="true"></div>', unsafe_allow_html=True)
    render_header(user=user, greeting=f"Profil · {html.escape(user)} — Nutzung, Limits und Zahlungen.")
    render_stats(
        plan_label=str(plan.get("label", plan_key)),
        tokens=tokens,
        football_label=fb_label,
        tier=str(plan.get("badge", "Starter")),
    )

    if st.button("Zurück zum Dashboard (Home)", key="dash_go_home", width="stretch"):
        _nav("home")

    with st.expander("Mab AI · OS Guide", expanded=False):
        render_os_guide_dashboard()

    with st.container(border=True):
        render_daily_limits(plan_key)

    with st.expander("Token-Kosten (Referenz)", expanded=False):
        token_rows = [
            {"Workspace": "AI Assistant", "Action": "Prompt", "Cost": TOKEN_COSTS.get("chat", 1)},
            {"Workspace": "Developer OS", "Action": "Coding", "Cost": TOKEN_COSTS.get("coding", 10)},
            {"Workspace": "Creative", "Action": "Image", "Cost": TOKEN_COSTS.get("image", 10)},
            {"Workspace": "Music", "Action": "Song", "Cost": TOKEN_COSTS.get("music", 50)},
            {"Workspace": "Video", "Action": "Base", "Cost": TOKEN_COSTS.get("video_base", 10)},
            {"Workspace": "Football", "Action": "Report", "Cost": TOKEN_COSTS.get("football_report", 80)},
            {"Workspace": "Automation", "Action": "Job", "Cost": TOKEN_COSTS.get("automation_job", 100)},
        ]
        st.dataframe(token_rows, width="stretch", hide_index=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            render_recent_activity(str(st.session_state.get("user") or ""), limit=12)

    with col_b:
        with st.container(border=True):
            st.markdown(
                '<div class="dash-kicker" style="margin-bottom:10px;">Zahlungen</div>',
                unsafe_allow_html=True,
            )
            payments = list_purchases(st.session_state.get("user"))
            if payments:
                blocks = []
                for row in payments[:10]:
                    plan_l = str(row.get("plan", row.get("product", "—")))
                    amt = str(row.get("amount", row.get("status", "")))
                    when = str(row.get("created_at", ""))[:16]
                    blocks.append(
                        f'<div class="dash-activity"><div class="t">{html.escape(plan_l)}</div>'
                        f'<div class="d">{html.escape(amt)} · {html.escape(when)}</div></div>'
                    )
                st.markdown("".join(blocks), unsafe_allow_html=True)
            else:
                render_empty_state("Keine Zahlungen", "Upgrades erscheinen nach Stripe Checkout.")

