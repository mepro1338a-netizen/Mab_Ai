"""
MaByte Sidebar — standard flat navigation, session-safe.
"""
from __future__ import annotations

import base64
import html

import streamlit as st

from config import APP_NAME
from ui.components import format_num
from ui.styles import MB_APP_BACKGROUND, inject_css

_SB = 'section[data-testid="stSidebar"]'
SIDEBAR_WIDTH = "240px"
_NAV = '[class*="st-key-sb_nav_"]'
_SHELL = f"{_SB} .st-key-sb_shell"
_COL = f'{_SHELL} > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"]'

_BG = "#09090b"
_APP_BG = MB_APP_BACKGROUND
_LINE = "rgba(255, 255, 255, 0.08)"
_MUTED = "#71717a"
_TEXT = "#d4d4d8"
_BTN_H = 34

NAV_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Workspace", [("Dashboard", "home"), ("AI Chat", "chat"), ("Football", "football"), ("Automation", "automation_lab")]),
    ("Create", [("Image", "image"), ("Video", "video"), ("Code", "coding"), ("Music", "music")]),
    ("Account", [("Profile", "dashboard"), ("Premium", "premium")]),
]

NAV_ITEMS: list[tuple[str, str]] = [item for _, items in NAV_SECTIONS for item in items]

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "video",
    "creator": "video",
    "automations": "automation_lab",
    "projects": "home",
}

NAV_HIGHLIGHT_ALIASES: dict[str, str] = {
    "coding": "coding",
    "music": "music",
    "social_oauth": "dashboard",
    "football": "football",
}

SIDEBAR_NAV_ITEMS = NAV_ITEMS
VALID_NAV_PAGES = frozenset(p for _, p in NAV_ITEMS)
ROUTE_PAGES = VALID_NAV_PAGES

_SVG_PATHS: dict[str, str] = {
    "home": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "football": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "video": '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
    "automation_lab": '<rect width="8" height="8" x="3" y="3" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect width="8" height="8" x="13" y="13" rx="2"/>',
    "dashboard": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "premium": '<path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z"/>',
    "coding": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "music": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
}

_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="22" height="22">'
    '<defs><linearGradient id="mbs" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    '</linearGradient></defs><rect width="40" height="40" rx="9" fill="url(#mbs)"/>'
    '<path d="M11 28V12l6.5 8.5L24 12v16" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def navigate_to(page: str) -> None:
    target = LEGACY_PAGE_ALIASES.get(page, page)
    if target not in ROUTE_PAGES:
        return
    if st.session_state.get("page") != target:
        st.session_state.page = target
        st.rerun()


def _resolve_active(active_page: str | None) -> str:
    raw = (active_page or st.session_state.get("page") or "home").strip()
    page = LEGACY_PAGE_ALIASES.get(raw, raw)
    if page in VALID_NAV_PAGES:
        return page
    return NAV_HIGHLIGHT_ALIASES.get(page, "home")


def _nav_key(page: str) -> str:
    return f"sb_nav_{page}"


def _svg_b64(page: str, *, active: bool = False) -> str:
    stroke = "#fafafa" if active else "#a1a1aa"
    inner = _SVG_PATHS.get(page, _SVG_PATHS["home"])
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f"{inner}</svg>"
    )
    return base64.b64encode(svg.encode("utf-8")).decode("ascii")


def _icon_html(page: str, *, active: bool = False) -> str:
    b64 = _svg_b64(page, active=active)
    return f'<img src="data:image/svg+xml;base64,{b64}" width="16" height="16" alt="" class="sb-ico" />'


def _nav_btn_css(active: str) -> str:
    btn = f"{_SB} {_NAV} .stButton > button, {_SB} {_NAV} button"
    parts = [
        f"""
{btn} {{
  width:100%!important; height:{_BTN_H}px!important; min-height:{_BTN_H}px!important;
  max-height:{_BTN_H}px!important; margin:0!important; padding:0 10px!important;
  border-radius:8px!important; border:none!important; background:transparent!important;
  color:{_TEXT}!important; font-size:13px!important; font-weight:500!important;
  display:flex!important; align-items:center!important; justify-content:flex-start!important;
  box-shadow:none!important; line-height:1!important;
}}
{btn}:hover {{ background:rgba(255,255,255,0.05)!important; color:#fafafa!important; }}
{btn} p, {btn} span, {btn} div {{
  margin:0!important; padding:0!important; color:inherit!important;
  font-size:13px!important; line-height:1!important; white-space:nowrap!important;
  display:flex!important; align-items:center!important;
}}
.stApp [class*="st-key-sb_item_"] {{
  margin-bottom:2px!important;
}}
.stApp [class*="st-key-sb_item_"] > [data-testid="stVerticalBlockBorderWrapper"] {{
  padding:0!important; border:none!important; background:transparent!important;
}}
.stApp [class*="st-key-sb_item_"] > [data-testid="stHorizontalBlock"] {{
  align-items:center!important; gap:0!important;
}}
.stApp [class*="st-key-sb_item_"] [data-testid="column"]:first-child {{
  display:flex!important; align-items:center!important; justify-content:center!important;
  min-width:28px!important; max-width:28px!important; flex:0 0 28px!important;
}}
.sb-ico-wrap {{ display:flex; align-items:center; justify-content:center; width:28px; height:{_BTN_H}px; }}
.sb-ico {{ display:block; width:16px; height:16px; flex-shrink:0; }}
"""
    ]
    for _, items in NAV_SECTIONS:
        for _, page in items:
            if page == active:
                parts.append(
                    f".stApp .st-key-sb_item_{page} {{"
                    f"background:rgba(39,39,42,0.95)!important; border-radius:8px!important; }}"
                    f".stApp .st-key-sb_item_{page} {btn} {{"
                    f"color:#fafafa!important; font-weight:600!important; }}"
                )
    return "".join(parts)


def _base_css() -> str:
    btn = f"{_SB} {_NAV} .stButton > button, {_SB} {_NAV} button"
    wrap = (
        f"{_SB} {_NAV} [data-testid='stVerticalBlockBorderWrapper'], "
        f"{_SB} {_NAV} [data-testid='stElementContainer'], {_SB} {_NAV} .stButton"
    )
    return f"""
:root {{ --sb-w:{SIDEBAR_WIDTH}; --sb-width:{SIDEBAR_WIDTH}; --sb-bg:{_BG}; }}
{_SB}, {_SB}>div, {_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"], {_COL} {{
  background:{_APP_BG}!important; background-color:{_BG}!important;
}}
{_SB} {{
  width:var(--sb-w)!important; min-width:var(--sb-w)!important; max-width:var(--sb-w)!important;
  border-right:1px solid {_LINE}!important; box-shadow:none!important;
}}
{_SB} [data-testid="stSidebarHeader"], {_SB} [data-testid="stSidebarCollapsedControl"] {{
  display:none!important; height:0!important; overflow:hidden!important;
}}
{_SB}>div {{ padding:0!important; height:100dvh!important; overflow:hidden!important; }}
{_SB} [data-testid="stSidebarNav"] {{ display:none!important; }}
{_SHELL}> [data-testid="stVerticalBlockBorderWrapper"] {{
  height:100%!important; background:transparent!important; border:none!important;
  padding:0!important; margin:0!important;
}}
{_COL} {{
  display:flex!important; flex-direction:column!important; height:100%!important;
  min-height:0!important; padding:16px 14px 14px!important; gap:0!important;
  overflow-y:auto!important; overflow-x:hidden!important;
}}
{_SHELL} [data-testid="stVerticalBlock"],
{_SHELL} [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
  gap:0!important;
}}
{_SHELL} [data-testid="stMarkdownContainer"], {_SHELL} [data-testid="stElementContainer"] {{
  margin:0!important; padding:0!important;
}}
{_SHELL} [data-testid="stMarkdownContainer"] p {{ margin:0!important; padding:0!important; }}
{_SHELL} .st-key-sb_bottom {{
  margin-top:auto!important; flex-shrink:0!important;
  padding-top:14px!important; border-top:1px solid {_LINE};
}}
.sb-brand {{
  display:flex; align-items:center; gap:10px; padding:0 4px 14px;
  margin-bottom:8px; border-bottom:1px solid {_LINE};
}}
.sb-name {{ color:#fafafa!important; font-size:15px; font-weight:700; letter-spacing:-0.02em; }}
.sb-sec {{
  color:{_MUTED}!important; font-size:11px; font-weight:600;
  letter-spacing:0.06em; text-transform:uppercase;
  padding:12px 8px 6px; margin:0!important;
}}
.sb-sec:first-of-type {{ padding-top:4px; }}
{wrap} {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{_SB} {_NAV} [data-testid='stElementContainer'] {{ margin-bottom:2px!important; }}
{_SB} {_NAV} .stButton {{ margin:0!important; padding:0!important; width:100%!important; }}
.sb-user {{ padding:0 4px 10px; }}
.sb-un {{ color:#f4f4f5!important; font-size:13px; font-weight:600; margin:0; }}
.sb-meta {{ color:{_MUTED}!important; font-size:11px; margin:3px 0 0; }}
{_SB} .st-key-nav_logout .stButton>button, {_SB} .st-key-nav_logout button {{
  width:100%!important; height:32px!important; min-height:32px!important;
  padding:0 10px!important; border-radius:8px!important;
  border:1px solid {_LINE}!important; background:transparent!important;
  color:{_MUTED}!important; font-size:12px!important;
  display:flex!important; align-items:center!important;
  box-shadow:none!important;
}}
{_SB} .st-key-nav_logout .stButton>button:hover {{
  color:#f87171!important; background:rgba(248,113,113,0.06)!important;
}}
.stApp .st-key-sb_item_ [data-testid="stVerticalBlockBorderWrapper"] {{
  background:transparent!important; border:none!important; padding:0!important; margin:0!important;
}}
"""


def sidebar_master_css(active_page: str) -> str:
    active = _resolve_active(active_page)
    return _base_css() + _nav_btn_css(active)


def sidebar_theme_lock_css(active_page: str) -> str:
    active = _resolve_active(active_page)
    return f"""
{_SB}, {_SB}>div {{ background:{_APP_BG}!important; background-color:{_BG}!important; }}
{_nav_btn_css(active)}
"""


def _render_nav(active: str) -> None:
    for title, items in NAV_SECTIONS:
        st.markdown(f'<p class="sb-sec">{html.escape(title)}</p>', unsafe_allow_html=True)
        for label, page in items:
            with st.container(key=f"sb_item_{page}"):
                icon_col, btn_col = st.columns([0.12, 0.88], gap="small")
                with icon_col:
                    st.markdown(
                        f'<div class="sb-ico-wrap">{_icon_html(page, active=(page == active))}</div>',
                        unsafe_allow_html=True,
                    )
                with btn_col:
                    if st.button(label, key=_nav_key(page), use_container_width=True, type="tertiary"):
                        if page != active:
                            navigate_to(page)


def _plan_label(plan: str) -> str:
    key = (plan or "free").strip().lower()
    if key in ("none", ""):
        return "Free"
    if key == "elite":
        return "Elite"
    return key.replace("_", " ").title()


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))
    user = str(st.session_state.get("user") or "User")
    plan = _plan_label(str(st.session_state.get("plan") or "free"))
    tokens = format_num(int(st.session_state.get("tokens", 0) or 0))

    with st.sidebar:
        with st.container(key="sb_shell"):
            st.markdown(
                f'<div class="sb-brand">{_LOGO}<span class="sb-name">{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )
            _render_nav(active)
            with st.container(key="sb_bottom"):
                st.markdown(
                    f'<div class="sb-user">'
                    f'<p class="sb-un">{html.escape(user)}</p>'
                    f'<p class="sb-meta">{html.escape(plan)} · {html.escape(tokens)} Tokens</p>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                with st.container(key="sb_logout_row"):
                    lo_ic, lo_bt = st.columns([0.12, 0.88], gap="small")
                    with lo_ic:
                        st.markdown(
                            f'<div class="sb-ico-wrap">{_icon_html("logout")}</div>',
                            unsafe_allow_html=True,
                        )
                    with lo_bt:
                        if st.button("Abmelden", key="nav_logout", use_container_width=True, type="tertiary"):
                            from services.session_auth import logout_session
                            logout_session()
                            st.rerun()
