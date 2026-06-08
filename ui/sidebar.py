"""
MaByte Sidebar — compact, scrollable, session-safe navigation.
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import MB_APP_BACKGROUND, inject_css

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
_SB = 'section[data-testid="stSidebar"]'
SIDEBAR_WIDTH = "184px"
_NAV = '[class*="st-key-sb_nav_"]'
_SHELL = f"{_SB} .st-key-sb_shell"
_COL = f'{_SHELL} > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"]'
_SCROLL = f"{_SB} .st-key-sb_scroll"
_SCROLL_COL = (
    f'{_SCROLL} > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"]'
)

_BG = "#09090b"
_APP_BG = MB_APP_BACKGROUND
_LINE = "rgba(255, 255, 255, 0.07)"
_MUTED = "#71717a"
_TEXT = "#d4d4d8"
_ACTIVE_BG = "rgba(124, 58, 237, 0.18)"
_ACTIVE_GLOW = "0 0 14px rgba(124, 58, 237, 0.22)"
_BTN_H = 28

NAV_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Workspace", [("Dashboard", "home"), ("AI Chat", "chat"), ("Football", "football"), ("Automation", "automation_lab")]),
    ("Create", [("Image", "image"), ("Video", "video")]),
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
    "coding": "image",
    "music": "video",
    "social_oauth": "dashboard",
    "football": "football",
}

SIDEBAR_NAV_ITEMS = NAV_ITEMS
VALID_NAV_PAGES = frozenset(p for _, p in NAV_ITEMS)

_ICON = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_SVG: dict[str, str] = {
    "home": f"<svg {_ICON}><rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\"/></svg>",
    "chat": f"<svg {_ICON}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "football": f"<svg {_ICON}><circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20\"/><path d=\"M2 12h20\"/></svg>",
    "image": f"<svg {_ICON}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_ICON}><path d=\"m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5\"/><rect x=\"2\" y=\"6\" width=\"14\" height=\"12\" rx=\"2\"/></svg>",
    "automation_lab": f"<svg {_ICON}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "dashboard": f"<svg {_ICON}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_ICON}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
    "logout": f"<svg {_ICON}><path d=\"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4\"/><polyline points=\"16 17 21 12 16 7\"/><line x1=\"21\" x2=\"9\" y1=\"12\" y2=\"12\"/></svg>",
}

_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="18" height="18">'
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


def _resolve_active(active_page: str | None) -> str:
    raw = (active_page or st.session_state.get("page") or "home").strip()
    page = LEGACY_PAGE_ALIASES.get(raw, raw)
    if page in VALID_NAV_PAGES:
        return page
    return NAV_HIGHLIGHT_ALIASES.get(page, "home")


def _nav_key(page: str) -> str:
    return f"sb_nav_{page}"


def _icon_uri(page: str, *, on: bool = False) -> str:
    c = "%23e9d5ff" if on else "%238a8a8e"
    svg = (_SVG.get(page) or _SVG["home"]).format(c=c)
    return f'url("data:image/svg+xml,{quote(svg)}")'


def _btn(page: str) -> str:
    k = _nav_key(page)
    return (
        f"{_SB} .st-key-{k} .stButton > button, "
        f"{_SB} .st-key-{k} [data-testid='stBaseButton-tertiary'], "
        f"{_SB} .st-key-{k} button"
    )


def _active_css(page: str) -> str:
    s = _btn(page)
    return f"""
{s} {{
  background: {_ACTIVE_BG} !important;
  background-color: {_ACTIVE_BG} !important;
  color: #fafafa !important;
  font-weight: 600 !important;
  box-shadow: {_ACTIVE_GLOW}, inset 2px 0 0 #a78bfa !important;
}}
{s}:hover {{
  background: rgba(124, 58, 237, 0.26) !important;
  color: #fff !important;
}}
"""


def _icons_css(active: str) -> str:
    out: list[str] = []
    for p in _SVG:
        if p == "logout":
            continue
        s = _btn(p)
        uri = _icon_uri(p, on=(p == active))
        out.append(
            f"{s}{{padding-left:28px!important;position:relative!important}}"
            f"{s}::before{{content:'';position:absolute;left:8px;top:50%;"
            f"transform:translateY(-50%);width:12px;height:12px;"
            f"background-image:{uri};background-size:12px;background-repeat:no-repeat}}"
        )
    return "".join(out)


def _scroll_css() -> str:
    return f"""
{_SCROLL} {{
  flex: 1 1 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  margin: 0 !important;
  padding: 0 !important;
}}
{_SCROLL} > [data-testid="stVerticalBlockBorderWrapper"] {{
  height: 100% !important;
  min-height: 0 !important;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
{_SCROLL_COL} {{
  display: block !important;
  height: 100% !important;
  max-height: 100% !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding: 2px 0 4px !important;
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.55) transparent;
}}
{_SCROLL_COL}::-webkit-scrollbar {{ width: 4px; }}
{_SCROLL_COL}::-webkit-scrollbar-thumb {{
  background: linear-gradient(180deg, #8b5cf6, #6366f1);
  border-radius: 99px;
}}
{_SCROLL_COL}::-webkit-scrollbar-track {{ background: transparent; }}
"""


def _base_css() -> str:
    btn = (
        f"{_SB} {_NAV} .stButton > button, "
        f"{_SB} {_NAV} [data-testid='stBaseButton-tertiary'], "
        f"{_SB} {_NAV} button"
    )
    wrap = (
        f"{_SB} {_NAV} [data-testid='stVerticalBlockBorderWrapper'], "
        f"{_SB} {_NAV} [data-testid='stElementContainer'], "
        f"{_SB} {_NAV} .stButton"
    )
    logout_btn = (
        f"{_SB} .st-key-nav_logout .stButton > button, "
        f"{_SB} .st-key-nav_logout [data-testid='stBaseButton-tertiary'], "
        f"{_SB} .st-key-nav_logout button"
    )
    return f"""
:root {{ --sb-w:{SIDEBAR_WIDTH}; --sb-width:{SIDEBAR_WIDTH}; --sb-bg:{_BG}; }}
{_SB}, {_SB}>div, {_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"], {_COL} {{
  background:{_APP_BG}!important; background-color:{_BG}!important;
}}
{_SB} {{
  width:var(--sb-w)!important; min-width:var(--sb-w)!important;
  max-width:var(--sb-w)!important; border-right:none!important; box-shadow:none!important;
  z-index:999980!important; isolation:isolate!important;
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
  min-height:0!important; padding:8px 7px 7px!important; gap:0!important;
  overflow:hidden!important;
}}
{_scroll_css()}
{_SHELL} [data-testid="stVerticalBlock"],
{_SHELL} [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
  gap:0!important; row-gap:0!important;
}}
{_SHELL} [data-testid="stMarkdownContainer"], {_SHELL} [data-testid="stElementContainer"] {{
  margin:0!important; padding:0!important;
}}
{_SHELL} [data-testid="stMarkdownContainer"] p {{ margin:0!important; padding:0!important; }}
{_SHELL} .st-key-sb_bottom {{
  flex-shrink:0!important; padding-top:6px!important;
  border-top:1px solid {_LINE};
}}
.sb-brand {{
  display:flex; align-items:center; gap:7px; padding:2px 4px 8px;
  margin-bottom:2px; flex-shrink:0;
}}
.sb-brand span {{
  color:#fafafa!important; font-size:12px; font-weight:700; letter-spacing:-0.02em;
  text-shadow:0 0 18px rgba(167,139,250,.35);
}}
.sb-sec {{
  color:rgba(161,161,170,.85)!important; font-size:8px; font-weight:700; letter-spacing:.11em;
  text-transform:uppercase; padding:7px 6px 2px; margin:0!important; line-height:1;
}}
.sb-sec:first-of-type {{ padding-top:0; }}
{wrap} {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{_SB} {_NAV} .stButton {{ margin:0!important; padding:0!important; width:100%!important; }}
{btn} {{
  width:100%!important; height:{_BTN_H}px!important; min-height:{_BTN_H}px!important;
  max-height:{_BTN_H}px!important; margin:0!important; padding:0 8px!important;
  border-radius:7px!important; border:none!important; background:transparent!important;
  color:{_TEXT}!important; font-size:11px!important; font-weight:500!important;
  text-align:left!important; justify-content:flex-start!important; box-shadow:none!important;
  line-height:1!important; transition:background .12s ease, color .12s ease;
}}
{btn}:hover {{ background:rgba(255,255,255,.06)!important; color:#fafafa!important; }}
{btn} p, {btn} span, {btn} div {{
  margin:0!important; padding:0!important; color:inherit!important;
  font-size:11px!important; line-height:1!important; white-space:nowrap!important; overflow:visible!important;
}}
.sb-user {{
  display:flex; align-items:center; gap:8px; padding:8px 8px; margin:6px 0 5px;
  border-radius:10px;
  background:linear-gradient(135deg,rgba(124,58,237,.12),rgba(99,102,241,.06));
  border:1px solid rgba(139,92,246,.22);
  box-shadow:0 0 20px rgba(124,58,237,.12), inset 0 1px 0 rgba(255,255,255,.04);
}}
.sb-av {{
  width:24px; height:24px; border-radius:7px; flex-shrink:0;
  background:linear-gradient(135deg,#7c3aed,#6366f1); color:#fff;
  font-size:10px; font-weight:700; display:flex; align-items:center; justify-content:center;
  box-shadow:0 0 12px rgba(124,58,237,.45);
}}
.sb-un {{
  color:#fafafa!important; font-size:11px; font-weight:700;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:108px;
  text-shadow:0 0 10px rgba(233,213,255,.55), 0 0 22px rgba(124,58,237,.35);
}}
.sb-up {{
  font-size:9px; font-weight:600; line-height:1.2; margin-top:1px;
  text-shadow:0 0 8px rgba(167,139,250,.45);
}}
.sb-plan-elite {{ color:#e9d5ff!important; text-shadow:0 0 10px rgba(233,213,255,.7), 0 0 18px rgba(167,139,250,.5)!important; }}
.sb-plan-pro {{ color:#c4b5fd!important; }}
.sb-plan-free {{ color:#a1a1aa!important; }}
{_SB} .st-key-nav_logout [data-testid="stVerticalBlockBorderWrapper"],
{_SB} .st-key-nav_logout .stButton {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{logout_btn} {{
  width:100%!important; height:26px!important; min-height:26px!important;
  padding:0 8px 0 26px!important; border-radius:7px!important;
  border:1px solid {_LINE}!important;
  background:rgba(9,9,11,.6)!important; background-color:rgba(9,9,11,.6)!important;
  color:{_MUTED}!important; font-size:10px!important; text-align:left!important;
  position:relative!important; box-shadow:none!important; line-height:1!important;
}}
{logout_btn}:hover {{
  color:{_TEXT}!important;
  background:rgba(255,255,255,.05)!important;
  background-color:rgba(255,255,255,.05)!important;
  border-color:rgba(139,92,246,.25)!important;
}}
{logout_btn}::before {{
  content:''; position:absolute; left:8px; top:50%; transform:translateY(-50%);
  width:11px; height:11px; background-image:{_icon_uri("logout")};
  background-size:11px; background-repeat:no-repeat;
}}
"""


def sidebar_master_css(active_page: str) -> str:
    active = _resolve_active(active_page)
    return _base_css() + _icons_css(active) + _active_css(active)


def sidebar_theme_lock_css(active_page: str) -> str:
    active = _resolve_active(active_page)
    btn = f"{_SB} {_NAV} .stButton > button, {_SB} {_NAV} button"
    logout_btn = f"{_SB} .st-key-nav_logout .stButton > button, {_SB} .st-key-nav_logout button"
    return f"""
{_SB}, {_SB}>div {{ background:{_APP_BG}!important; background-color:{_BG}!important; }}
{btn} {{ background:transparent!important; background-color:transparent!important; box-shadow:none!important; }}
{logout_btn} {{
  background:rgba(9,9,11,.6)!important; background-color:rgba(9,9,11,.6)!important;
  color:{_MUTED}!important; border:1px solid {_LINE}!important;
}}
{_active_css(active)}
"""


def _render_nav(active: str) -> None:
    for title, items in NAV_SECTIONS:
        st.markdown(f'<p class="sb-sec">{html.escape(title)}</p>', unsafe_allow_html=True)
        for label, page in items:
            if st.button(label, key=_nav_key(page), use_container_width=True, type="tertiary"):
                navigate_to(page)


def _plan_label(plan: str) -> str:
    key = (plan or "free").strip().lower()
    if key in ("none", ""):
        return "Free"
    if key == "elite":
        return "Elite"
    return key.replace("_", " ").title()


def _plan_class(plan: str) -> str:
    key = (plan or "free").strip().lower()
    if key == "elite":
        return "sb-plan-elite"
    if key in ("premium", "pro", "business"):
        return "sb-plan-pro"
    return "sb-plan-free"


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))
    user = str(st.session_state.get("user") or "User")
    plan_raw = str(st.session_state.get("plan") or "free")
    plan = _plan_label(plan_raw)
    plan_cls = _plan_class(plan_raw)
    initial = (user.strip()[:1] or "U").upper()

    with st.sidebar:
        with st.container(key="sb_shell"):
            st.markdown(
                f'<div class="sb-brand">{_LOGO}<span>{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )
            with st.container(key="sb_scroll"):
                _render_nav(active)
            with st.container(key="sb_bottom"):
                st.markdown(
                    f'<div class="sb-user"><div class="sb-av">{html.escape(initial)}</div>'
                    f'<div><div class="sb-un">{html.escape(user)}</div>'
                    f'<div class="sb-up {plan_cls}">{html.escape(plan)}</div></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Abmelden", key="nav_logout", use_container_width=True, type="tertiary"):
                    from services.session_auth import logout_session

                    logout_session()
                    st.rerun()
