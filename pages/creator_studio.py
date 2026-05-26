"""
MaByte Creator Studio — Shorts (Reels) & Video in einem Workspace.
"""
from __future__ import annotations

import streamlit as st

from database import get_user
from ui.video_engine_ui import render_video_engine_studio


def _username() -> str:
    return str(st.session_state.get("user") or "")


def _tokens() -> int:
    return int(st.session_state.get("tokens", 0) or 0)


def render_creator_studio_page() -> None:
    """Unified Shorts + Video — SaaS OS Creator module."""
    user = get_user(_username()) or {}

    # Deep links: ?page=reels or ?page=video set mode once
    page = str(st.session_state.get("page") or "creator")
    if page == "reels" and "creator_format" not in st.session_state:
        st.session_state.creator_format = "Shorts"
    elif page == "video" and "creator_format" not in st.session_state:
        st.session_state.creator_format = "Video"

    fmt = st.radio(
        "Format",
        ["Shorts", "Video"],
        horizontal=True,
        key="creator_format",
        label_visibility="collapsed",
        help="Shorts: 3–7s für TikTok, Reels, YouTube Shorts · Video: längere Clips",
    )
    mode = "reel" if fmt == "Shorts" else "video"

    render_video_engine_studio(
        mode=mode,
        username=_username(),
        tokens=_tokens(),
        user=user,
    )
