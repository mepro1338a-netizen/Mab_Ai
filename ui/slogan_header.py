"""Slogan banner header — shown on top of every logged-in page."""
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from ui.styles import inject_css

_HEADER_IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "headerslogan.png"

_SLOGAN_HEADER_CSS = """
.mb-slogan-header {
    width: 100%;
    margin: 0 0 20px 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: #09090b;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}
.mb-slogan-header img {
    display: block;
    width: 100%;
    height: clamp(92px, 13vw, 150px);
    object-fit: cover;
    object-position: center;
}
@media (max-width: 768px) {
    .mb-slogan-header {
        margin-bottom: 14px;
        border-radius: 10px;
    }
    .mb-slogan-header img {
        height: 84px;
    }
}
"""


@st.cache_data(show_spinner=False)
def _header_image_data_uri() -> str:
    try:
        data = _HEADER_IMAGE_PATH.read_bytes()
    except OSError:
        return ""
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def render_slogan_header() -> None:
    """Render the MaByte slogan banner at the top of the page content."""
    uri = _header_image_data_uri()
    if not uri:
        return
    inject_css(_SLOGAN_HEADER_CSS)
    st.markdown(
        f"""
<div class="mb-slogan-header">
<img src="{uri}" alt="One system. Infinite intelligence." />
</div>
        """,
        unsafe_allow_html=True,
    )
