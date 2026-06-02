"""Compact global header — MaByte brand + subtle claim (max ~88px)."""
from __future__ import annotations

import html

import streamlit as st

from config import APP_NAME, APP_TAGLINE

HEADER_HEIGHT = 88


def header_css() -> str:
    claim = (APP_TAGLINE or "One system. Infinite intelligence.").strip()
    return f"""
.custom-topbar {{
    height: {HEADER_HEIGHT}px !important;
    min-height: {HEADER_HEIGHT}px !important;
    max-height: 100px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 1.25rem 0 calc(var(--sb-width, 240px) + 1rem) !important;
    box-sizing: border-box !important;
    background: linear-gradient(90deg, rgba(9,8,24,.97), rgba(25,8,42,.97)) !important;
    background-image: none !important;
    border-bottom: 1px solid rgba(255,255,255,.08) !important;
    backdrop-filter: blur(18px) !important;
    box-shadow: 0 2px 16px rgba(0,0,0,.2) !important;
}}
.mb-header-inner {{
    display: flex;
    align-items: baseline;
    gap: 12px;
    width: 100%;
    max-width: 1180px;
}}
.mb-header-brand {{
    color: #fafafa !important;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
}}
.mb-header-claim {{
    color: #71717a !important;
    font-size: 11px;
    font-weight: 500;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
@media (max-width: 768px) {{
    .custom-topbar {{
        height: 72px !important;
        min-height: 72px !important;
        padding-left: 1rem !important;
    }}
    .mb-header-claim {{ display: none; }}
}}
"""


def render_header_bar() -> None:
    name = html.escape(APP_NAME or "MaByte")
    claim = html.escape((APP_TAGLINE or "One system. Infinite intelligence.").strip())
    st.markdown(
        f"""
<div class="custom-topbar">
  <div class="mb-header-inner">
    <span class="mb-header-brand">{name}</span>
    <span class="mb-header-claim">{claim}</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
