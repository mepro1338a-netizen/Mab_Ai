"""
MaByte Sidebar — session-safe Streamlit nav with scrollable layout.
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

_SB = 'section[data-testid="stSidebar"]'
_WIDTH = "240px"
_NAV_BTN = '[class*="st-key-sb_nav_"]'
_NAV_HOST = f"{_SB} .st-key-sb_nav"

_BG = "#18181b"
_BG_DEEP = "#141416"
_PANEL = "#232326"
_LINE = "rgba(255, 255, 255, 0.08)"
_MUTED = "#a1a1aa"
_TEXT = "#e4e4e7"
_ACTIVE_BG = "linear-gradient(90deg, rgba(124, 58, 237, 0.32), rgba(99, 102, 241, 0.12))"
_ACTIVE_BORDER = "rgba(167, 139, 250, 0.45)"

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

NAV_HIGHLIGHT_ALIASES: dict[str, str] = {
    "coding": "image",
    "music": "video",
    "social_oauth": "dashboard",
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


def _resolve_active(active_page: str | None) -> str:
    raw = (active_page or st.session_state.get("page") or "home").strip()
    page = LEGACY_PAGE_ALIASES.get(raw, raw)
    if page in VALID_NAV_PAGES:
        return page
    return NAV_HIGHLIGHT_ALIASES.get(page, "home")


def _nav_key(page: str) -> str:
    return f"sb_nav_{page}"


def _btn_sel(page: str) -> str:
    key = _nav_key(page)
    return (
        f'{_SB} .st-key-{key} .stButton > button, '
        f'{_SB} .st-key-{key} [data-testid="stBaseButton-tertiary"], '
        f'{_SB} .st-key-{key} [data-testid="stBaseButton-secondary"], '
        f'{_SB} .st-key-{key} button'
    )


def _active_style(page: str) -> str:
    sel = _btn_sel(page)
    return f"""
{sel} {{
  background: {_ACTIVE_BG} !important;
  background-color: rgba(124, 58, 237, 0.24) !important;
  border: 1px solid {_ACTIVE_BORDER} !important;
  border-left: 3px solid #c4b5fd !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}}
{sel}:hover, {sel}:focus-visible {{
  background: {_ACTIVE_BG} !important;
  background-color: rgba(124, 58, 237, 0.28) !important;
  border: 1px solid {_ACTIVE_BORDER} !important;
  border-left: 3px solid #c4b5fd !important;
  color: #ffffff !important;
}}
"""


def _nav_icons_css(active: str) -> str:
    chunks: list[str] = []
    for page in _ICONS:
        if page == "logout":
            continue
        uri = _icon_uri(page, active=(page == active))
        sel = _btn_sel(page)
        chunks.append(
            f"{sel} {{ padding-left: 38px !important; position: relative !important; }}"
            f"{sel}::before {{"
            f'content:"";position:absolute;left:12px;top:50%;transform:translateY(-50%);'
            f"width:18px;height:18px;background-image:{uri};"
            f"background-size:18px 18px;background-repeat:no-repeat;"
            f"}}"
        )
    return "".join(chunks)


def _scrollbar_css() -> str:
    return f"""
{_NAV_HOST} {{
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.75) rgba(255, 255, 255, 0.05);
}}
{_NAV_HOST}::-webkit-scrollbar {{ width: 6px; }}
{_NAV_HOST}::-webkit-scrollbar-track {{
  background: rgba(255, 255, 255, 0.04);
  border-radius: 999px;
  margin: 4px 0;
}}
{_NAV_HOST}::-webkit-scrollbar-thumb {{
  background: linear-gradient(180deg, #8b5cf6, #6366f1);
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
}}
{_NAV_HOST}::-webkit-scrollbar-thumb:hover {{
  background: linear-gradient(180deg, #a78bfa, #818cf8);
}}
"""


def sidebar_master_css(active_page: str) -> str:
    active = _resolve_active(active_page)
    logout_uri = _icon_uri("logout")
    nav_btn = (
        f'{_SB} {_NAV_BTN} .stButton > button, '
        f'{_SB} {_NAV_BTN} [data-testid="stBaseButton-tertiary"], '
        f'{_SB} {_NAV_BTN} [data-testid="stBaseButton-secondary"], '
        f'{_SB} {_NAV_BTN} button'
    )
    nav_wrap = (
        f'{_SB} {_NAV_BTN} [data-testid="stVerticalBlockBorderWrapper"], '
        f'{_SB} {_NAV_BTN} [data-testid="stElementContainer"], '
        f'{_SB} {_NAV_BTN} .stButton'
    )
    nav_inner_wrap = f'{_NAV_HOST} [data-testid="stVerticalBlockBorderWrapper"]'

    return f"""
:root {{
  --sb-w: {_WIDTH};
  --sb-bg: {_BG};
  --sb-bg-deep: {_BG_DEEP};
  --sb-panel: {_PANEL};
  --sb-line: {_LINE};
  --sb-nav-max: calc(100dvh - 220px);
}}
{_nav_icons_css(active)}
{_SB} {{
  width: var(--sb-w) !important;
  min-width: var(--sb-w) !important;
  max-width: var(--sb-w) !important;
  background: var(--sb-bg-deep) !important;
  border-right: 1px solid var(--sb-line) !important;
  user-select: none;
}}
{_SB} > div {{
  padding: 14px 12px 12px !important;
  background: linear-gradient(180deg, var(--sb-bg) 0%, var(--sb-bg-deep) 100%) !important;
  height: 100dvh !important;
  max-height: 100dvh !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
  padding: 0 !important;
  background: transparent !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
}}
{_SB} [data-testid="stSidebarNav"] {{ display: none !important; }}
{_SB} [data-testid="stSidebarContent"] > div,
{_SB} [data-testid="stSidebarUserContent"] > div {{
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  height: 100% !important;
  overflow: hidden !important;
  gap: 0 !important;
}}
{_SB} .st-key-sb_brand,
{_SB} .st-key-sb_foot,
{_SB} .st-key-nav_logout {{
  flex-shrink: 0 !important;
}}
{_SB} .st-key-sb_brand [data-testid="stMarkdownContainer"],
{_SB} .st-key-sb_foot [data-testid="stMarkdownContainer"],
{_SB} .st-key-sb_brand [data-testid="stElementContainer"],
{_SB} .st-key-sb_foot [data-testid="stElementContainer"] {{
  margin: 0 !important;
  padding: 0 !important;
}}
{_NAV_HOST} {{
  flex: 1 1 auto !important;
  min-height: 200px !important;
  max-height: var(--sb-nav-max) !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  overscroll-behavior: contain !important;
  -webkit-overflow-scrolling: touch !important;
  margin: 8px 0 !important;
  padding: 8px 6px !important;
  background: var(--sb-panel) !important;
  border: 1px solid var(--sb-line) !important;
  border-radius: 12px !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
}}
{nav_inner_wrap} {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
{_NAV_HOST} [data-testid="stVerticalBlock"] {{
  gap: 4px !important;
  padding: 0 !important;
}}
{_NAV_HOST} [data-testid="stMarkdownContainer"],
{_NAV_HOST} [data-testid="stElementContainer"],
{_NAV_HOST} .stMarkdown {{
  margin: 0 !important;
  padding: 0 !important;
}}
{_scrollbar_css()}
.sb-brand {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px 14px;
  border-bottom: 1px solid var(--sb-line);
}}
.sb-brand svg {{ flex-shrink: 0; }}
.sb-brand span {{
  color: #fafafa !important;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.02em;
}}
.sb-section-wrap {{
  margin: 12px 0 4px;
  padding: 0 6px;
}}
.sb-section {{
  color: #71717a !important;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  margin: 0;
  line-height: 1.4;
}}
.sb-divider-wrap {{ margin: 10px 6px; }}
.sb-divider {{ height: 1px; background: var(--sb-line); }}
{nav_wrap} {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
{_SB} {_NAV_BTN} .stButton {{
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
}}
{nav_btn} {{
  width: 100% !important;
  height: 40px !important;
  min-height: 40px !important;
  max-height: 40px !important;
  margin: 0 !important;
  padding: 0 12px !important;
  border-radius: 10px !important;
  border: none !important;
  background: transparent !important;
  background-color: transparent !important;
  color: {_TEXT} !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  text-align: left !important;
  justify-content: flex-start !important;
  box-shadow: none !important;
}}
{nav_btn}:hover {{
  background: rgba(255, 255, 255, 0.06) !important;
  color: #fafafa !important;
}}
{nav_btn} p {{
  margin: 0 !important;
  color: inherit !important;
}}
.sb-foot {{
  padding-top: 10px;
  border-top: 1px solid var(--sb-line);
}}
.sb-user {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 11px;
  background: var(--sb-panel);
  border: 1px solid var(--sb-line);
}}
.sb-av {{
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(135deg, #7c3aed, #6366f1);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.sb-un {{
  color: #f4f4f5 !important;
  font-size: 12px;
  font-weight: 600;
  max-width: 148px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.sb-up {{ color: {_MUTED} !important; font-size: 10px; margin-top: 2px; }}
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
{_SB} .st-key-nav_logout button {{
  width: 100% !important;
  height: 38px !important;
  min-height: 38px !important;
  padding: 0 12px 0 38px !important;
  border-radius: 10px !important;
  border: 1px solid var(--sb-line) !important;
  background: var(--sb-panel) !important;
  color: {_MUTED} !important;
  font-size: 12px !important;
  text-align: left !important;
  position: relative !important;
  box-shadow: none !important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover,
{_SB} .st-key-nav_logout button:hover {{
  background: rgba(255, 255, 255, 0.06) !important;
  color: {_TEXT} !important;
}}
{_SB} .st-key-nav_logout .stButton > button::before,
{_SB} .st-key-nav_logout button::before {{
  content: "";
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  background-image: {logout_uri};
  background-size: 14px;
  background-repeat: no-repeat;
}}
{_active_style(active)}
"""


def sidebar_theme_lock_css(active_page: str) -> str:
    active = _resolve_active(active_page)
    inactive_btn = (
        f'{_SB} {_NAV_BTN} .stButton > button, '
        f'{_SB} {_NAV_BTN} [data-testid="stBaseButton-tertiary"], '
        f'{_SB} {_NAV_BTN} button'
    )
    inactive_wrap = (
        f'{_SB} {_NAV_BTN} [data-testid="stVerticalBlockBorderWrapper"], '
        f'{_SB} {_NAV_BTN} .stButton'
    )
    return f"""
{_SB}, {_SB} > div {{
  background-color: var(--sb-bg-deep, {_BG_DEEP}) !important;
}}
{_SB} > div {{
  background: linear-gradient(180deg, var(--sb-bg, {_BG}) 0%, var(--sb-bg-deep, {_BG_DEEP}) 100%) !important;
}}
{_NAV_HOST} {{
  overflow-y: auto !important;
  min-height: 200px !important;
  max-height: var(--sb-nav-max, calc(100dvh - 220px)) !important;
  background: var(--sb-panel, {_PANEL}) !important;
}}
{_scrollbar_css()}
{inactive_wrap} {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}
{inactive_btn} {{
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}}
{_active_style(active)}
"""


def _render_nav_buttons(active: str) -> None:
    seen = False
    for section_title, items in NAV_SECTIONS:
        if section_title:
            st.markdown(
                f'<div class="sb-section-wrap">'
                f'<p class="sb-section">{html.escape(section_title)}</p></div>',
                unsafe_allow_html=True,
            )
        elif seen:
            st.markdown(
                '<div class="sb-divider-wrap"><div class="sb-divider"></div></div>',
                unsafe_allow_html=True,
            )
        seen = True
        for label, page in items:
            clicked = st.button(
                label,
                key=_nav_key(page),
                use_container_width=True,
                type="tertiary",
            )
            if clicked and page != active:
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


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))
    user = str(st.session_state.get("user") or "User")
    plan = _plan_label(str(st.session_state.get("plan") or "free"))

    with st.sidebar:
        with st.container(key="sb_brand"):
            st.markdown(
                f'<div class="sb-brand">{_BRAND_SVG}<span>{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )
        with st.container(key="sb_nav"):
            _render_nav_buttons(active)
        with st.container(key="sb_foot"):
            st.markdown(
                f'<div class="sb-foot"><div class="sb-user">'
                f'<div class="sb-av">{html.escape(_user_initial(user))}</div>'
                f'<div><div class="sb-un">{html.escape(user)}</div>'
                f'<div class="sb-up">{html.escape(plan)}</div></div>'
                f"</div></div>",
                unsafe_allow_html=True,
            )
        if st.button(
            "Abmelden",
            key="nav_logout",
            use_container_width=True,
            type="tertiary",
        ):
            from services.session_auth import logout_session

            logout_session()
            st.rerun()
