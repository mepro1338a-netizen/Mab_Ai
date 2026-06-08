"""
MaByte Sidebar v2 — compact, session-safe, full-height layout.
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
SIDEBAR_WIDTH = "220px"
_NAV = '[class*="st-key-sb_nav_"]'
_SHELL = f"{_SB} .st-key-sb_shell"
_COL = f'{_SHELL} > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"]'

_BG = "#09090b"
_APP_BG = MB_APP_BACKGROUND
_LINE = "rgba(255, 255, 255, 0.06)"
_MUTED = "#71717a"
_TEXT = "#d4d4d8"
_ACTIVE = "rgba(124, 58, 237, 0.22)"
_BTN_H = 32

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
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="20" height="20">'
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
    c = "%23ffffff" if on else "%238a8a8e"
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
  background: {_ACTIVE} !important;
  color: #fff !important;
  font-weight: 600 !important;
}}
{s}:hover {{ background: rgba(124,58,237,0.28) !important; color: #fff !important; }}
"""


def _icons_css(active: str) -> str:
    out: list[str] = []
    for p in _SVG:
        if p == "logout":
            continue
        s = _btn(p)
        uri = _icon_uri(p, on=(p == active))
        out.append(
            f"{s}{{padding-left:34px!important;position:relative!important}}"
            f"{s}::before{{content:'';position:absolute;left:10px;top:50%;"
            f"transform:translateY(-50%);width:13px;height:13px;"
            f"background-image:{uri};background-size:13px;background-repeat:no-repeat}}"
        )
    return "".join(out)


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
    return f"""
:root {{ --sb-w:{SIDEBAR_WIDTH}; --sb-width:{SIDEBAR_WIDTH}; --sb-bg:{_BG}; }}
{_SB}, {_SB}>div, {_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"], {_COL} {{
  background:{_APP_BG}!important; background-color:{_BG}!important;
}}
{_SB} {{
  width:var(--sb-w)!important; min-width:var(--sb-w)!important;
  max-width:var(--sb-w)!important;
  border-right:1px solid rgba(255,255,255,0.04)!important;
  box-shadow:none!important;
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
  min-height:0!important; padding:16px 16px 14px!important; gap:0!important;
  overflow-y:auto!important; overflow-x:hidden!important;
  scrollbar-width:thin; scrollbar-color:rgba(139,92,246,.5) transparent;
}}
{_COL}::-webkit-scrollbar {{ width:3px; }}
{_COL}::-webkit-scrollbar-thumb {{ background:#8b5cf6; border-radius:99px; }}
{_SHELL} [data-testid="stVerticalBlock"],
{_SHELL} [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
  gap:0!important; row-gap:0!important;
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
  display:flex; align-items:center; gap:8px; padding:0 4px 16px;
  margin-bottom:4px; border-bottom:none; flex-shrink:0;
}}
.sb-brand span {{ color:#fafafa!important; font-size:12px; font-weight:700; letter-spacing:-0.02em; }}
.sb-sec {{
  color:var(--mb-label-color,#a78bfa)!important;
  font-size:var(--mb-label-size,10px); font-weight:var(--mb-label-weight,700);
  letter-spacing:var(--mb-label-spacing,.12em);
  text-transform:uppercase; padding:14px 6px 6px; margin:0!important; line-height:1;
}}
.sb-sec:first-of-type {{ padding-top:4px; }}
{wrap} {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{_SB} {_NAV} [data-testid='stElementContainer'] {{ margin-bottom:3px!important; }}
{_SB} {_NAV} .stButton {{ margin:0!important; padding:0!important; width:100%!important; }}
{btn} {{
  width:100%!important; height:{_BTN_H}px!important; min-height:{_BTN_H}px!important;
  max-height:{_BTN_H}px!important; margin:0!important; padding:0 10px!important;
  border-radius:8px!important; border:none!important; background:transparent!important;
  color:{_TEXT}!important; font-size:12px!important; font-weight:500!important;
  text-align:left!important; justify-content:flex-start!important; box-shadow:none!important;
  line-height:1!important;
}}
{btn}:hover {{ background:rgba(255,255,255,.05)!important; color:#fafafa!important; }}
{btn} p, {btn} span, {btn} div {{
  margin:0!important; padding:0!important; color:inherit!important;
  font-size:12px!important; line-height:1!important; white-space:nowrap!important; overflow:visible!important;
}}
.sb-user {{
  display:flex; align-items:center; gap:10px; padding:10px 10px; margin:4px 0 8px;
  border-radius:10px; background:rgba(255,255,255,.03); border:1px solid {_LINE};
}}
.sb-av {{
  width:28px; height:28px; border-radius:8px; flex-shrink:0;
  background:linear-gradient(135deg,#7c3aed,#6366f1); color:#fff;
  font-size:11px; font-weight:700; display:flex; align-items:center; justify-content:center;
}}
.sb-un {{ color:#f4f4f5!important; font-size:11px; font-weight:600;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:140px; }}
.sb-up {{ color:{_MUTED}!important; font-size:9px; line-height:1.2; margin-top:2px; }}
{_SB} .st-key-nav_logout [data-testid="stVerticalBlockBorderWrapper"],
{_SB} .st-key-nav_logout .stButton {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{_SB} .st-key-nav_logout .stButton>button, {_SB} .st-key-nav_logout button {{
  width:100%!important; height:30px!important; min-height:30px!important;
  padding:0 10px 0 32px!important; border-radius:8px!important;
  border:1px solid {_LINE}!important; background:rgba(255,255,255,.02)!important;
  color:{_MUTED}!important; font-size:11px!important; text-align:left!important;
  position:relative!important; box-shadow:none!important; line-height:1!important;
}}
{_SB} .st-key-nav_logout .stButton>button:hover {{ color:{_TEXT}!important; background:rgba(255,255,255,.05)!important; }}
{_SB} .st-key-nav_logout .stButton>button::before {{
  content:''; position:absolute; left:11px; top:50%; transform:translateY(-50%);
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
    return f"""
{_SB}, {_SB}>div {{ background:{_APP_BG}!important; background-color:{_BG}!important; }}
{btn} {{ background:transparent!important; box-shadow:none!important; }}
{_active_css(active)}
"""


def _render_nav(active: str) -> None:
    for title, items in NAV_SECTIONS:
        st.markdown(f'<p class="sb-sec">{html.escape(title)}</p>', unsafe_allow_html=True)
        for label, page in items:
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
    initial = (user.strip()[:1] or "U").upper()

    with st.sidebar:
        with st.container(key="sb_shell"):
            st.markdown(
                f'<div class="sb-brand">{_LOGO}<span>{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )
            _render_nav(active)
            with st.container(key="sb_bottom"):
                st.markdown(
                    f'<div class="sb-user"><div class="sb-av">{html.escape(initial)}</div>'
                    f'<div><div class="sb-un">{html.escape(user)}</div>'
                    f'<div class="sb-up">{html.escape(plan)}</div></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Abmelden", key="nav_logout", use_container_width=True, type="tertiary"):
                    from services.session_auth import logout_session
                    logout_session()
                    st.rerun()
