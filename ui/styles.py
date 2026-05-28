"""Central MaByte UI CSS helpers and theme tokens."""
from __future__ import annotations

import streamlit as st

# Scope page-specific button CSS here so the sidebar stays identical on every route.
MAIN_CONTENT_SCOPE = "section.main"

from ui.b2b_theme import AUTH_EXTRA_VARS, MB_THEME_VARS  # noqa: F401 — re-export


def inject_css(css: str) -> None:
    st.markdown(f"<style>{css.strip()}</style>", unsafe_allow_html=True)


def page_layout_css(
    max_width: int,
    padding_top: int,
    padding_bottom: int = 42,
    selector: str = ".main .block-container",
) -> str:
    return f"""
{selector} {{
    max-width: {max_width}px !important;
    padding-top: {padding_top}px !important;
    padding-bottom: {padding_bottom}px !important;
}}
"""


def gradient_title_css(class_name: str = "mb-title") -> str:
    return f"""
.{class_name} {{
    text-align: center;
    font-size: 56px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -3px;
    margin-top: 10px;
    background: linear-gradient(135deg, #fafafa, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
"""
