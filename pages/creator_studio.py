"""
MaByte Creator Studio — Shorts (Reels) & Video in einem Workspace.
"""
from __future__ import annotations

import streamlit as st

from database import get_user
from ui.reels_studio_ui import render_reels_studio_premium
from ui.video_engine_ui import render_video_engine_studio


def _username() -> str:
    return str(st.session_state.get("user") or "")


def _tokens() -> int:
    return int(st.session_state.get("tokens", 0) or 0)


def _render_format_switch() -> str:
    """Premium segmented control — no Streamlit radio dots."""
    cur = str(st.session_state.get("creator_format") or "Shorts")
    st.markdown('<div class="mb-format-bar">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "Shorts",
            key="creator_fmt_shorts",
            use_container_width=True,
            type="primary" if cur == "Shorts" else "secondary",
        ):
            st.session_state.creator_format = "Shorts"
            st.rerun()
    with c2:
        if st.button(
            "Video",
            key="creator_fmt_video",
            use_container_width=True,
            type="primary" if cur == "Video" else "secondary",
        ):
            st.session_state.creator_format = "Video"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    return str(st.session_state.get("creator_format") or "Shorts")


def render_creator_studio_page() -> None:
    """Unified Shorts + Video — SaaS OS Creator module."""
    user = get_user(_username()) or {}

    page = str(st.session_state.get("page") or "creator")
    if page == "reels" and "creator_format" not in st.session_state:
        st.session_state.creator_format = "Shorts"
    elif page == "video" and "creator_format" not in st.session_state:
        st.session_state.creator_format = "Video"

    fmt = _render_format_switch()
    if fmt == "Shorts":
        render_reels_studio_premium(
            username=_username(),
            tokens=_tokens(),
            user=user,
        )
        return

    render_video_engine_studio(
        mode="video",
        username=_username(),
        tokens=_tokens(),
        user=user,
    )
