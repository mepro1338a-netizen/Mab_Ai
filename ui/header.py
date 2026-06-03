"""Compact global header — small MaByte logo + subtle claim (64px)."""
from __future__ import annotations

import html

import streamlit as st

from config import APP_NAME, APP_TAGLINE

HEADER_HEIGHT = 64

_HEADER_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="28" height="28">'
    '<defs><linearGradient id="mbh" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    "</linearGradient></defs>"
    '<rect width="40" height="40" rx="9" fill="url(#mbh)"/>'
    '<path d="M11 28V12l6.5 8.5L24 12v16" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)


def header_css() -> str:
    return f"""
.custom-topbar {{
    height: {HEADER_HEIGHT}px !important;
    min-height: {HEADER_HEIGHT}px !important;
    max-height: {HEADER_HEIGHT}px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 1rem 0 calc(var(--sb-width, 230px) + 0.75rem) !important;
    box-sizing: border-box !important;
    background: rgba(9, 9, 11, 0.92) !important;
    background-image: none !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: none !important;
}}
.mb-header-inner {{
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    max-width: 1180px;
}}
.mb-header-logo {{
    display: flex;
    align-items: center;
    flex-shrink: 0;
    line-height: 0;
}}
.mb-header-logo svg {{
    display: block;
    width: 28px;
    height: 28px;
}}
.mb-header-text {{
    display: flex;
    flex-direction: column;
    gap: 1px;
    min-width: 0;
}}
.mb-header-brand {{
    color: #fafafa !important;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.1;
}}
.mb-header-claim {{
    color: #71717a !important;
    font-size: 10px;
    font-weight: 400;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
@media (max-width: 768px) {{
    .custom-topbar {{
        padding-left: 0.75rem !important;
    }}
    .mb-header-claim {{
        display: none;
    }}
}}
"""


def render_header_bar() -> None:
    name = html.escape(APP_NAME or "MaByte")
    claim = html.escape((APP_TAGLINE or "One system. Infinite intelligence.").strip())
    st.markdown(
        f"""
<div class="custom-topbar">
  <div class="mb-header-inner">
    <span class="mb-header-logo">{_HEADER_LOGO}</span>
    <span class="mb-header-text">
      <span class="mb-header-brand">{name}</span>
      <span class="mb-header-claim">{claim}</span>
    </span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
