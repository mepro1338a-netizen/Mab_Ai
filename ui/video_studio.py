"""
Video Studio — delegates to unified video engine UI.
"""
from __future__ import annotations

import streamlit as st

from database import get_user
from ui.video_engine_ui import render_video_engine_studio


def render_video_studio(*, tokens_available: int, on_generate=None) -> None:
    """Legacy signature — on_generate ignored; engine handles billing."""
    user = get_user(str(st.session_state.get("user") or "")) or {}
    render_video_engine_studio(
        mode="video",
        username=str(st.session_state.get("user") or ""),
        tokens=tokens_available,
        user=user,
    )
