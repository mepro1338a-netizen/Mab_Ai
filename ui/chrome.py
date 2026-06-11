"""
App chrome — query-param navigation (?nav=page bookmarks).
"""
from __future__ import annotations

import streamlit as st

from ui.sidebar import LEGACY_PAGE_ALIASES, VALID_NAV_PAGES, navigate_to

_VALID_NAV = VALID_NAV_PAGES


def _qp_first(value) -> str:
    if isinstance(value, list):
        return str(value[0] if value else "").strip()
    return str(value or "").strip()


def _clear_query_key(key: str) -> None:
    remaining: dict[str, str | list[str]] = {}
    for k, v in dict(st.query_params).items():
        if k != key:
            remaining[k] = v
    st.query_params.clear()
    for k, v in remaining.items():
        st.query_params[k] = v


def apply_nav_from_query() -> None:
    """Handle ?nav=page bookmarks — in-app only, no full page reload."""
    if not st.session_state.get("logged_in"):
        return
    raw = _qp_first(st.query_params.get("nav"))
    if not raw:
        return
    target = LEGACY_PAGE_ALIASES.get(raw, raw)
    if target not in _VALID_NAV:
        _clear_query_key("nav")
        return
    _clear_query_key("nav")
    navigate_to(target)
