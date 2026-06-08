"""
App chrome — fixed topbar, main offset, query-param navigation.
"""
from __future__ import annotations

import html

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from ui.sidebar import LEGACY_PAGE_ALIASES, SIDEBAR_WIDTH, VALID_NAV_PAGES, navigate_to

TOPBAR_HEIGHT = 64

_VALID_NAV = VALID_NAV_PAGES

_CHROME_CSS = f"""
:root {{
  --sb-width: {SIDEBAR_WIDTH};
  --mb-topbar-h: {TOPBAR_HEIGHT}px;
}}
section.main [data-testid="stElementContainer"]:has(.mb-topbar-mount),
section.main [data-testid="stMarkdownContainer"]:has(.mb-topbar-mount) {{
  position: fixed !important;
  top: 0 !important;
  left: var(--sb-width) !important;
  right: 0 !important;
  width: auto !important;
  height: var(--mb-topbar-h) !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: 999990 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  transform: none !important;
  filter: none !important;
}}
.mb-topbar-mount {{
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  box-sizing: border-box !important;
}}
.custom-topbar {{
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 var(--mb-content-pad-x, 1.5rem) !important;
  box-sizing: border-box !important;
  background: rgba(9, 9, 11, 0.94) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
  backdrop-filter: blur(14px) !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25) !important;
}}
.mb-header-inner {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  max-width: var(--mb-content-max, 1100px);
  margin: 0 auto;
}}
.mb-header-left {{
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
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
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.mb-header-right {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}}
.mb-header-page {{
  color: #e9d5ff !important;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(124, 58, 237, 0.12);
  border: 1px solid rgba(139, 92, 246, 0.22);
  white-space: nowrap;
}}
.mb-header-plan {{
  color: #e9d5ff !important;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(124, 58, 237, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.35);
  white-space: nowrap;
}}
.mb-topbar-spacer {{
  height: var(--mb-topbar-h) !important;
  width: 100% !important;
  flex-shrink: 0 !important;
  pointer-events: none !important;
}}
@media (max-width: 768px) {{
  section.main [data-testid="stElementContainer"]:has(.mb-topbar-mount),
  section.main [data-testid="stMarkdownContainer"]:has(.mb-topbar-mount) {{
    left: 0 !important;
    padding-left: 0 !important;
  }}
  .custom-topbar {{ padding: 0 0.85rem !important; }}
  .mb-header-claim {{ display: none; }}
}}
"""

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


def chrome_css() -> str:
    return _CHROME_CSS


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


def render_app_header(*, page_label: str = "", plan_badge: str = "") -> None:
    """Fixed MaByte topbar — call once per run after sidebar."""
    name = html.escape(APP_NAME or "MaByte")
    claim = html.escape((APP_TAGLINE or "One system. Infinite intelligence.").strip())
    right_bits: list[str] = []
    if page_label:
        right_bits.append(
            f'<span class="mb-header-page">{html.escape(page_label)}</span>'
        )
    elif plan_badge:
        right_bits.append(
            f'<span class="mb-header-plan">{html.escape(plan_badge)} Plan</span>'
        )
    right_html = (
        f'<div class="mb-header-right">{"".join(right_bits)}</div>' if right_bits else ""
    )
    st.markdown(
        f"""
<div class="mb-topbar-mount">
  <div class="custom-topbar" role="banner">
    <div class="mb-header-inner">
      <div class="mb-header-left">
        <span class="mb-header-logo">{_HEADER_LOGO}</span>
        <span class="mb-header-text">
          <span class="mb-header-brand">{name}</span>
          <span class="mb-header-claim">{claim}</span>
        </span>
      </div>
      {right_html}
    </div>
  </div>
</div>
<div class="mb-topbar-spacer" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )
