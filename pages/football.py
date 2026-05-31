"""Football AI — minimalist Premium Betting Analysis (single page)."""
from __future__ import annotations

import streamlit as st

from ui.football_betting_board import render_football_betting_board


def _username() -> str:
    return str(st.session_state.get("user") or "")


def _session_plan() -> str:
    return str(st.session_state.get("football_plan") or "none")


def open_premium() -> None:
    st.session_state.page = "premium"
    st.rerun()


def render_football() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    render_football_betting_board(
        username=_username(),
        session_plan=_session_plan(),
        open_premium=open_premium,
    )
