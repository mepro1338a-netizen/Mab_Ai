"""Global CSS injection — runs every Streamlit script execution."""
from __future__ import annotations

import streamlit as st

_UI_VERSION = 6


def inject_global_ui(*, force: bool = False) -> None:
    """Inject on every run — Streamlit rebuilds the page each rerun."""
    from ui.b2b_theme import MB_THEME_VARS, streamlit_force_dark_css
    from ui.button_system import master_button_css
    from ui.design_system import GLOBAL_DESIGN_CSS
    from ui.premium_foundation import BETA_GLOBAL_CSS
    from ui.prompt_ui import MABYTE_PROMPT_CSS
    from ui.sidebar import sidebar_master_css
    from ui.styles import inject_css, page_layout_css
    from ui_core import core_app_css

    _page = str(st.session_state.get("page") or "home").strip()
    if _page in ("reels", "video"):
        _page = "creator"

    inject_css(
        f"/* mb-ui-v{_UI_VERSION} */\n"
        + MB_THEME_VARS
        + streamlit_force_dark_css()
        + BETA_GLOBAL_CSS
        + page_layout_css(1480, 92, 42)
        + GLOBAL_DESIGN_CSS
        + core_app_css()
        + master_button_css()
        + sidebar_master_css(_page)
        + MABYTE_PROMPT_CSS
    )
    st.markdown('<div class="custom-topbar"></div>', unsafe_allow_html=True)
    st.session_state["_mb_ui_version"] = _UI_VERSION
