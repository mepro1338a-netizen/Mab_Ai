"""Clean workspace shell — studios without marketing prompts or topbar."""
from __future__ import annotations

import html

import streamlit as st

from ui.styles import inject_css, page_layout_css

WORKSPACE_CSS = """
.stApp:has(.mb-workspace) section.main .block-container {
    max-width: 920px !important;
    padding-top: 92px !important;
    padding-bottom: 40px !important;
}
.stApp:has(.mb-workspace) section.main div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(10, 12, 24, .4) !important;
    border: 1px solid rgba(255, 255, 255, .07) !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    backdrop-filter: blur(10px);
}
.stApp:has(.mb-workspace) .stTextInput input,
.stApp:has(.mb-workspace) .stTextArea textarea,
.stApp:has(.mb-workspace) div[data-baseweb="select"] > div {
    background: rgba(8, 10, 22, .7) !important;
    color: #f1f5f9 !important;
    border-color: rgba(255, 255, 255, .1) !important;
    border-radius: 12px !important;
}
.stApp:has(.mb-workspace) label[data-testid="stWidgetLabel"] p,
.stApp:has(.mb-workspace) label p {
    color: rgba(203, 213, 225, .95) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
.mb-ws-head {
    margin-bottom: 18px;
}
.mb-ws-kicker {
    color: rgba(192, 132, 252, .85) !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
}
.mb-ws-title {
    color: #f8fafc !important;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 6px 0 4px 0;
}
.mb-ws-sub {
    color: rgba(148, 163, 184, .95) !important;
    font-size: 14px;
    line-height: 1.45;
}
"""


def inject_workspace_css() -> None:
    inject_css(page_layout_css(920, 92, 40) + WORKSPACE_CSS)


def workspace_marker() -> None:
    st.markdown('<div class="mb-workspace" aria-hidden="true"></div>', unsafe_allow_html=True)


def workspace_header(title: str, subtitle: str = "") -> None:
    sub = f'<p class="mb-ws-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="mb-ws-head">
  <div class="mb-ws-kicker">Workspace</div>
  <div class="mb-ws-title">{html.escape(title)}</div>
  {sub}
</div>
        """,
        unsafe_allow_html=True,
    )
