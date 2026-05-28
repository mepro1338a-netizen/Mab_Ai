"""Single global CSS injection per session — avoids duplicate Streamlit style blocks."""
from __future__ import annotations

import streamlit as st

_GLOBAL_UI_DONE = False


def inject_global_ui(*, force: bool = False) -> None:
    global _GLOBAL_UI_DONE
    if _GLOBAL_UI_DONE and not force:
        return

    from ui.button_system import master_button_css
    from ui.design_system import GLOBAL_DESIGN_CSS
    from ui.premium_foundation import BETA_GLOBAL_CSS
    from ui.prompt_ui import MABYTE_PROMPT_CSS
    from ui.sidebar import sidebar_master_css
    from ui.styles import MB_THEME_VARS, inject_css, page_layout_css
    from ui_core import core_app_css

    inject_css(
        MB_THEME_VARS
        + BETA_GLOBAL_CSS
        + page_layout_css(1480, 92, 42)
        + GLOBAL_DESIGN_CSS
        + core_app_css()
        + sidebar_master_css()
        + MABYTE_PROMPT_CSS
        + master_button_css()
    )
    st.markdown('<div class="custom-topbar"></div>', unsafe_allow_html=True)
    _GLOBAL_UI_DONE = True
