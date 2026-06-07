"""
MaByte Sidebar — flat nav buttons (session-safe) in a single HTML shell layout.
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

_SB = 'section[data-testid="stSidebar"]'
_WIDTH = "230px"
_NAV_KEY = '[class*="st-key-sb_nav_"]'
_SB_BG = "#18181b"
_SB_BG_DEEP = "#141416"
_SB_PANEL = "#27272a"
_SB_LINE = "rgba(255, 255, 255, 0.08)"

NAV_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "",
        [
            ("Dashboard", "home"),
            ("AI Chat", "chat"),
            ("Football AI", "football"),
            ("Automation", "automation_lab"),
        ],
    ),
    (
        "Create",
        [
            ("Image", "image"),
            ("Video", "video"),
        ],
    ),
    (
        "",
        [
            ("Profile", "dashboard"),
            ("Premium", "premium"),
        ],
    ),
]

NAV_ITEMS: list[tuple[str, str]] = [
    item for _title, items in NAV_SECTIONS for item in items
]

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "video",
    "creator": "video",
    "automations": "automation_lab",
    "projects": "home",
}

SIDEBAR_NAV_ITEMS = NAV_ITEMS
VALID_NAV_PAGES = frozenset(page for _label, page in NAV_ITEMS)

_LUCIDE = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_ICONS: dict[str, str] = {
    "home": f"<svg {_LUCIDE}><rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\"/></svg>",
    "chat": f"<svg {_LUCIDE}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "football": f"<svg {_LUCIDE}><circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20\"/><path d=\"M2 12h20\"/></svg>",
    "image": f"<svg {_LUCIDE}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" ry=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_LUCIDE}><path d=\"m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5\"/><rect x=\"2\" y=\"6\" width=\"14\" height=\"12\" rx=\"2\"/></svg>",
    "automation_lab": f"<svg {_LUCIDE}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "dashboard": f"<svg {_LUCIDE}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_LUCIDE}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
    "logout": f"<svg {_LUCIDE}><path d=\"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4\"/><polyline points=\"16 17 21 12 16 7\"/><line x1=\"21\" x2=\"9\" y1=\"12\" y2=\"12\"/></svg>",
}

_BRAND_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="24" height="24">'
    '<defs><linearGradient id="mbs" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    '</linearGradient></defs><rect width="40" height="40" rx="9" fill="url(#mbs)"/>'
    '<path d="M11 28V12l6.5 8.5L24 12v16" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def navigate_to(page: str) -> None:
    target = LEGACY_PAGE_ALIASES.get(page, page)
    if target not in VALID_NAV_PAGES:
        return
    if st.session_state.get("page") != target:
        st.session_state.page = target
        st.rerun()


def _icon_uri(page: str, *, active: bool = False) -> str:
    color = "%23ffffff" if active else "%23a1a1aa"
    svg = (_ICONS.get(page) or _ICONS["home"]).format(c=color)
    return f'url("data:image/svg+xml,{quote(svg)}")'


def _sidebar_scrollbar_css(scroll_selector: str) -> str:
    return f"""
{scroll_selector} {{
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.7) rgba(255, 255, 255, 0.04);
}}
{scroll_selector}::-webkit-scrollbar {{
  width: 6px;
}}
{scroll_selector}::-webkit-scrollbar-track {{
  background: rgba(255, 255, 255, 0.04);
  border-radius: 999px;
  margin: 8px 0;
}}
{scroll_selector}::-webkit-scrollbar-thumb {{
  background: linear-gradient(180deg, #8b5cf6 0%, #6366f1 100%);
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 36px;
}}
{scroll_selector}::-webkit-scrollbar-thumb:hover {{
  background: linear-gradient(180deg, #a78bfa 0%, #818cf8 100%);
}}
"""


def _nav_btn_selectors(page: str) -> str:
    base = f'{_SB} .st-key-sb_nav_{page}'
    return (
        f'{base} [data-testid="stVerticalBlockBorderWrapper"], '
        f'{base} [data-testid="stElementContainer"], '
        f'{base} .stButton, '
        f'{base} .stButton > button, '
        f'{base} [data-testid="stBaseButton-secondary"], '
        f'{base} [data-testid="stBaseButton-primary"], '
        f'{base} button'
    )


def _nav_icon_css(active: str) -> str:
    rules: list[str] = []
    for page in _ICONS:
        if page == "logout":
            continue
        sel = _nav_btn_selectors(page)
        uri = _icon_uri(page, active=(page == active))
        rules.append(
            f"{sel} {{ box-shadow: none !important; }}"
            f'{_SB} .st-key-sb_nav_{page} .stButton > button, '
            f'{_SB} .st-key-sb_nav_{page} [data-testid="stBaseButton-secondary"], '
            f'{_SB} .st-key-sb_nav_{page} button {{'
            f"padding-left: 36px !important; position: relative !important;"
            f"}}"
            f'{_SB} .st-key-sb_nav_{page} .stButton > button::before, '
            f'{_SB} .st-key-sb_nav_{page} [data-testid="stBaseButton-secondary"]::before, '
            f'{_SB} .st-key-sb_nav_{page} button::before {{'
            f'content:"";position:absolute;left:10px;top:50%;transform:translateY(-50%);'
            f"width:18px;height:18px;background-image:{uri};"
            f"background-size:18px 18px;background-repeat:no-repeat;"
            f"}}"
        )
    return "".join(rules)


def _active_nav_css(active: str) -> str:
    if active not in VALID_NAV_PAGES:
        return ""
    sel = _nav_btn_selectors(active)
    return f"""
{sel} {{
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}
{_SB} .st-key-sb_nav_{active} .stButton > button,
{_SB} .st-key-sb_nav_{active} [data-testid="stBaseButton-secondary"],
{_SB} .st-key-sb_nav_{active} button {{
  background: linear-gradient(90deg, rgba(124, 58, 237, 0.28), rgba(99, 102, 241, 0.14)) !important;
  background-color: rgba(124, 58, 237, 0.22) !important;
  border: 1px solid rgba(139, 92, 246, 0.35) !important;
  border-left: 3px solid #a78bfa !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}}
"""


def _render_nav_buttons(active: str) -> None:
    seen = False
    for section_title, items in NAV_SECTIONS:
        if section_title:
            st.markdown(
                f'<p class="sb-section">{html.escape(section_title)}</p>',
                unsafe_allow_html=True,
            )
        elif seen:
            st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        seen = True
        for label, page in items:
            if st.button(label, key=f"sb_nav_{page}", use_container_width=True, type="secondary"):
                if page != active:
                    navigate_to(page)


def _plan_label(plan: str) -> str:
    key = (plan or "free").strip().lower()
    if key in ("none", ""):
        return "Free"
    if key == "elite":
        return "Elite"
    return key.replace("_", " ").title()


def _user_initial(username: str) -> str:
    u = (username or "U").strip()
    return (u[0] or "U").upper()


def sidebar_master_css(active_page: str) -> str:
    active = LEGACY_PAGE_ALIASES.get(active_page, active_page)
    logout_uri = _icon_uri("logout")
    nav_scroll = f'{_SB} .st-key-sb_nav > [data-testid="stVerticalBlock"]'
    nav_wrap = (
        f'{_SB} {_NAV_KEY} [data-testid="stVerticalBlockBorderWrapper"], '
        f'{_SB} {_NAV_KEY} [data-testid="stElementContainer"], '
        f'{_SB} {_NAV_KEY} .stButton'
    )
    nav_btn = (
        f'{_SB} {_NAV_KEY} .stButton > button, '
        f'{_SB} {_NAV_KEY} [data-testid="stBaseButton-secondary"], '
        f'{_SB} {_NAV_KEY} [data-testid="stBaseButton-primary"], '
        f'{_SB} {_NAV_KEY} button'
    )
    return f"""
:root {{
  --sb-width: {_WIDTH};
  --sb-bg: {_SB_BG};
  --sb-bg-deep: {_SB_BG_DEEP};
  --sb-panel: {_SB_PANEL};
  --sb-line: {_SB_LINE};
}}
{_nav_icon_css(active)}
{_active_nav_css(active)}
{_SB} {{
  width: var(--sb-width) !important;
  min-width: var(--sb-width) !important;
  max-width: var(--sb-width) !important;
  background: var(--sb-bg-deep) !important;
  border-right: 1px solid var(--sb-line) !important;
  user-select: none;
}}
{_SB} > div {{
  padding: 12px 10px 10px !important;
  background: linear-gradient(180deg, var(--sb-bg) 0%, var(--sb-bg-deep) 100%) !important;
  height: 100dvh !important;
  max-height: 100dvh !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
  padding: 0 !important;
  background: transparent !important;
  display: flex !important;
  flex-direction: column !important;
  flex: 1 !important;
  min-height: 0 !important;
  overflow: hidden !important;
}}
{_SB} [data-testid="stSidebarNav"] {{ display: none !important; }}
{_SB} .st-key-sb_panel > [data-testid="stVerticalBlock"] {{
  display: flex !important;
  flex-direction: column !important;
  flex: 1 !important;
  min-height: 0 !important;
  gap: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}}
{_SB} .st-key-sb_nav {{
  background: rgba(39, 39, 42, 0.55) !important;
  border: 1px solid var(--sb-line) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  margin: 6px 0 8px !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow: hidden !important;
}}
{_SB} .st-key-sb_nav > [data-testid="stVerticalBlock"] {{
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  gap: 0 !important;
  padding: 2px 4px 2px 2px !important;
}}
{_sidebar_scrollbar_css(nav_scroll)}
.sb-brand {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 8px 14px;
  border-bottom: 1px solid var(--sb-line);
  margin-bottom: 2px;
}}
.sb-brand svg {{ width: 24px !important; height: 24px !important; flex-shrink: 0; }}
.sb-brand span {{ color: #fafafa !important; font-size: 15px; font-weight: 700; letter-spacing: -0.02em; }}
.sb-section {{
  color: #71717a !important;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  padding: 10px 10px 5px;
  margin: 0;
  line-height: 1.2;
}}
.sb-divider {{ height: 1px; margin: 8px 10px; background: var(--sb-line); }}
{nav_wrap} {{
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 0 3px !important;
}}
{_SB} {_NAV_KEY} .stButton {{ margin: 0 !important; padding: 0 !important; width: 100% !important; }}
{nav_btn} {{
  width: 100% !important;
  height: 38px !important;
  min-height: 38px !important;
  max-height: 38px !important;
  margin: 0 !important;
  padding: 0 12px !important;
  border-radius: 9px !important;
  border: 1px solid transparent !important;
  border-left: 3px solid transparent !important;
  background: transparent !important;
  background-color: transparent !important;
  background-image: none !important;
  color: #d4d4d8 !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  text-align: left !important;
  justify-content: flex-start !important;
  box-shadow: none !important;
  transform: none !important;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
}}
{nav_btn}:hover {{
  background: rgba(255, 255, 255, 0.06) !important;
  background-color: rgba(255, 255, 255, 0.06) !important;
  border-color: rgba(255, 255, 255, 0.05) !important;
  color: #fafafa !important;
  transform: none !important;
}}
{nav_btn}:focus-visible {{
  outline: 2px solid rgba(139, 92, 246, 0.55) !important;
  outline-offset: 1px !important;
}}
{nav_btn} p {{
  margin: 0 !important;
  color: inherit !important;
  font-size: inherit !important;
  font-weight: inherit !important;
}}
.sb-foot {{
  flex-shrink: 0;
  padding-top: 10px;
  border-top: 1px solid var(--sb-line);
  margin-top: auto;
}}
.sb-user {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 11px;
  background: rgba(39, 39, 42, 0.85);
  border: 1px solid var(--sb-line);
  margin-bottom: 8px;
}}
.sb-av {{
  width: 30px; height: 30px; border-radius: 9px;
  background: linear-gradient(135deg, #7c3aed, #6366f1);
  color: #fff; font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
}}
.sb-un {{ color: #f4f4f5 !important; font-size: 12px; font-weight: 600; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.sb-up {{ color: #a1a1aa !important; font-size: 10px; margin-top: 2px; font-weight: 500; }}
{_SB} .st-key-nav_logout [data-testid="stVerticalBlockBorderWrapper"],
{_SB} .st-key-nav_logout [data-testid="stElementContainer"],
{_SB} .st-key-nav_logout .stButton {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
{_SB} .st-key-nav_logout .stButton > button,
{_SB} .st-key-nav_logout [data-testid="stBaseButton-secondary"],
{_SB} .st-key-nav_logout button {{
  width: 100% !important;
  height: 36px !important;
  min-height: 36px !important;
  padding: 0 12px 0 36px !important;
  border-radius: 9px !important;
  border: 1px solid var(--sb-line) !important;
  background: rgba(39, 39, 42, 0.6) !important;
  background-color: rgba(39, 39, 42, 0.6) !important;
  color: #a1a1aa !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  text-align: left !important;
  position: relative !important;
  box-shadow: none !important;
  transition: background 0.15s ease, color 0.15s ease !important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover,
{_SB} .st-key-nav_logout button:hover {{
  background: rgba(255, 255, 255, 0.06) !important;
  background-color: rgba(255, 255, 255, 0.06) !important;
  color: #e4e4e7 !important;
}}
{_SB} .st-key-nav_logout .stButton > button::before,
{_SB} .st-key-nav_logout button::before {{
  content: '';
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  background-image: {logout_uri};
  background-size: 14px;
  background-repeat: no-repeat;
}}
"""


def sidebar_theme_lock_css(active_page: str) -> str:
    """Final override — beats Streamlit theme secondary button backgrounds."""
    active = LEGACY_PAGE_ALIASES.get(active_page, active_page)
    nav_scroll = f'{_SB} .st-key-sb_nav > [data-testid="stVerticalBlock"]'
    sb_shell = (
        f"{_SB}, {_SB} > div, {_SB} [data-testid=\"stSidebarContent\"], "
        f'{_SB} [data-testid="stSidebarUserContent"]'
    )
    return f"""
{sb_shell} {{
  background: var(--sb-bg-deep, {_SB_BG_DEEP}) !important;
  background-color: var(--sb-bg-deep, {_SB_BG_DEEP}) !important;
}}
{_SB} > div {{
  background: linear-gradient(180deg, var(--sb-bg, {_SB_BG}) 0%, var(--sb-bg-deep, {_SB_BG_DEEP}) 100%) !important;
}}
{_sidebar_scrollbar_css(nav_scroll)}
{_SB} {_NAV_KEY} [data-testid="stVerticalBlockBorderWrapper"],
{_SB} {_NAV_KEY} [data-testid="stVerticalBlockBorderWrapper"] > div,
{_SB} {_NAV_KEY} [data-testid="stElementContainer"],
{_SB} {_NAV_KEY} .stButton,
{_SB} {_NAV_KEY} .stButton > button,
{_SB} {_NAV_KEY} [data-testid="stBaseButton-secondary"],
{_SB} {_NAV_KEY} button[kind="secondary"] {{
  background: transparent !important;
  background-color: transparent !important;
  background-image: none !important;
  border: none !important;
  box-shadow: none !important;
}}
{_SB} .st-key-sb_nav_{active} .stButton > button,
{_SB} .st-key-sb_nav_{active} button {{
  background: linear-gradient(90deg, rgba(124, 58, 237, 0.28), rgba(99, 102, 241, 0.14)) !important;
  background-color: rgba(124, 58, 237, 0.22) !important;
  border: 1px solid rgba(139, 92, 246, 0.35) !important;
  border-left: 3px solid #a78bfa !important;
  color: #ffffff !important;
}}
"""


def _resolve_active(active_page: str | None) -> str:
    p = (active_page or st.session_state.get("page") or "home").strip()
    return LEGACY_PAGE_ALIASES.get(p, p)


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))
    user = str(st.session_state.get("user") or "User")
    plan = _plan_label(str(st.session_state.get("plan") or "free"))

    with st.sidebar:
        with st.container(key="sb_panel"):
            st.markdown(
                f'<div class="sb-brand">{_BRAND_SVG}<span>{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )
            with st.container(key="sb_nav"):
                _render_nav_buttons(active)
            st.markdown(
                f'<div class="sb-foot"><div class="sb-user">'
                f'<div class="sb-av">{html.escape(_user_initial(user))}</div>'
                f'<div><div class="sb-un">{html.escape(user)}</div>'
                f'<div class="sb-up">{html.escape(plan)}</div></div>'
                f"</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Abmelden", key="nav_logout", use_container_width=True, type="secondary"):
                from services.session_auth import logout_session
                logout_session()
                st.rerun()
