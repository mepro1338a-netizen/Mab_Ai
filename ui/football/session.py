"""Football AI V2 session defaults."""
from __future__ import annotations

from typing import Any

import streamlit as st

FB_VERSION = 10

FB_DEFAULTS: dict[str, Any] = {
    "fb_v": FB_VERSION,
    "fb_competition": "deutschland",
    "fb_time": "heute",
    "fb_league_id": 0,
    "fb_payload": None,
    "fb_detail": None,
    "fb_sel": None,
    "fb_cache_key": "",
    "fb_displayed_topspiele_count": 0,
    "fb_displayed_allspiele_count": 0,
}


def ensure_football_session() -> None:
    if st.session_state.get("fb_v") != FB_VERSION:
        for key, value in FB_DEFAULTS.items():
            st.session_state[key] = value
        return
    for key, value in FB_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
