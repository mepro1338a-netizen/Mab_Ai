"""
MaByte Sidebar — professional navigation shell, session-safe.
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.components import format_num
from ui.styles import MB_APP_BACKGROUND, inject_css

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
_SB = 'section[data-testid="stSidebar"]'
SIDEBAR_WIDTH = "236px"
_NAV = '[class*="st-key-sb_nav_"]'
_SHELL = f"{_SB} .st-key-sb_shell"
_COL = f'{_SHELL} > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"]'

_BG = "#09090b"
_APP_BG = MB_APP_BACKGROUND
_LINE = "rgba(255, 255, 255, 0.07)"
_MUTED = "#71717a"
_TEXT = "#d4d4d8"
_ACTIVE_BG = "rgba(124, 58, 237, 0.16)"
_ACTIVE_BORDER = "#8b5cf6"
_BTN_H = 36

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
ROUTE_PAGES = VALID_NAV_PAGES | frozenset({"coding", "music"})

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


def _icon_uri(page: str, *, on: bool = False) -> str:
    c = "%23fafafa" if on else "%23a1a1aa"
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
  color: #fafafa !important;
  font-weight: 600 !important;
  border: 1px solid rgba(139, 92, 246, 0.28) !important;
  border-left: 3px solid {_ACTIVE_BORDER} !important;
}}
{s}:hover {{
  background: rgba(124, 58, 237, 0.22) !important;
  color: #fff !important;
}}
{s}::before {{
  background-color: rgba(124, 58, 237, 0.22) !important;
  left: 10px !important;
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
            f"{s}{{padding-left:40px!important;position:relative!important;"
            f"display:flex!important;align-items:center!important}}"
            f"{s}::before{{content:'';position:absolute;left:9px;top:7px;"
            f"transform:none;width:22px;height:22px;"
            f"border-radius:7px;background-color:rgba(255,255,255,0.05);"
            f"background-image:{uri};background-size:14px;background-position:center;"
            f"background-repeat:no-repeat}}"
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
  min-height:0!important; padding:18px 14px 16px!important; gap:0!important;
  overflow-y:auto!important; overflow-x:hidden!important;
  scrollbar-width:thin; scrollbar-color:rgba(139,92,246,.35) transparent;
}}
{_COL}::-webkit-scrollbar {{ width:4px; }}
{_COL}::-webkit-scrollbar-thumb {{ background:rgba(139,92,246,.45); border-radius:99px; }}
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
  padding-top:16px!important; border-top:1px solid {_LINE};
}}
.sb-brand {{
  display:flex; align-items:center; gap:10px; padding:2px 6px 18px;
  margin-bottom:6px; border-bottom:1px solid {_LINE}; flex-shrink:0;
}}
.sb-brand-meta {{ display:flex; flex-direction:column; gap:1px; min-width:0; }}
.sb-name {{ color:#fafafa!important; font-size:13px; font-weight:800; letter-spacing:-0.03em; line-height:1.2; }}
.sb-tag {{ color:#52525b!important; font-size:9px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; }}
.sb-sec {{
  display:flex; align-items:center; gap:8px;
  color:#52525b!important;
  font-size:10px; font-weight:800;
  letter-spacing:0.14em; text-transform:uppercase;
  padding:18px 8px 10px; margin:0!important; line-height:1;
}}
.sb-sec::after {{
  content:""; flex:1; height:1px; background:rgba(255,255,255,0.05);
}}
.sb-sec:first-of-type {{ padding-top:10px; }}
{wrap} {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{_SB} {_NAV} [data-testid='stElementContainer'] {{ margin-bottom:4px!important; }}
{_SB} {_NAV} .stButton {{ margin:0!important; padding:0!important; width:100%!important; }}
{btn} {{
  width:100%!important; height:{_BTN_H}px!important; min-height:{_BTN_H}px!important;
  max-height:{_BTN_H}px!important; margin:0!important; padding:0 12px 0 40px!important;
  border-radius:10px!important; border:1px solid transparent!important;
  border-left:3px solid transparent!important;
  background:transparent!important;
  color:{_TEXT}!important; font-size:12.5px!important; font-weight:500!important;
  display:flex!important; align-items:center!important; justify-content:flex-start!important;
  box-shadow:none!important; line-height:1.2!important;
  transition:background .12s,border-color .12s,color .12s!important;
}}
{btn}:hover {{
  background:rgba(255,255,255,.04)!important; color:#fafafa!important;
  border-color:rgba(255,255,255,0.06)!important;
}}
{btn} p, {btn} span, {btn} div, {btn} [data-testid="stMarkdownContainer"] {{
  margin:0!important; padding:0!important; color:inherit!important;
  font-size:12.5px!important; line-height:1.2!important; white-space:nowrap!important;
  overflow:visible!important; display:flex!important; align-items:center!important;
  height:auto!important; min-height:0!important;
}}
.sb-user {{
  display:flex; align-items:center; gap:11px; padding:12px 12px; margin:0 0 10px;
  border-radius:12px;
  background:linear-gradient(145deg, rgba(30,27,40,0.55), rgba(18,18,20,0.85));
  border:1px solid rgba(139,92,246,0.18);
}}
.sb-av {{
  width:32px; height:32px; border-radius:10px; flex-shrink:0;
  background:linear-gradient(135deg,#7c3aed,#4f46e5); color:#fff;
  font-size:12px; font-weight:800; display:flex; align-items:center; justify-content:center;
  box-shadow:0 0 0 1px rgba(255,255,255,0.08);
}}
.sb-user-meta {{ min-width:0; flex:1; }}
.sb-un {{ color:#f4f4f5!important; font-size:12px; font-weight:700;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:148px; }}
.sb-up {{ display:flex; align-items:center; gap:6px; margin-top:4px; flex-wrap:wrap; }}
.sb-plan {{
  font-size:9px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;
  padding:2px 7px; border-radius:999px;
  color:#e9d5ff!important; background:rgba(124,58,237,0.18);
  border:1px solid rgba(139,92,246,0.28);
}}
.sb-tokens {{ color:{_MUTED}!important; font-size:10px; font-weight:600; }}
{_SB} .st-key-nav_logout [data-testid="stVerticalBlockBorderWrapper"],
{_SB} .st-key-nav_logout .stButton {{ background:transparent!important; border:none!important; margin:0!important; padding:0!important; }}
{_SB} .st-key-nav_logout .stButton>button, {_SB} .st-key-nav_logout button {{
  width:100%!important; height:34px!important; min-height:34px!important;
  padding:0 12px 0 38px!important; border-radius:10px!important;
  border:1px solid {_LINE}!important; background:rgba(255,255,255,.02)!important;
  color:{_MUTED}!important; font-size:11.5px!important; font-weight:500!important;
  display:flex!important; align-items:center!important; justify-content:flex-start!important;
  position:relative!important; box-shadow:none!important; line-height:1.2!important;
}}
{_SB} .st-key-nav_logout .stButton>button p, {_SB} .st-key-nav_logout button p {{
  display:flex!important; align-items:center!important; margin:0!important; padding:0!important;
}}
{_SB} .st-key-nav_logout .stButton>button:hover {{
  color:#fca5a5!important; border-color:rgba(248,113,113,0.25)!important;
  background:rgba(248,113,113,0.06)!important;
}}
{_SB} .st-key-nav_logout .stButton>button::before {{
  content:''; position:absolute; left:12px; top:10px; transform:none;
  width:14px; height:14px; border-radius:5px;
  background-color:rgba(255,255,255,0.04);
  background-image:{_icon_uri("logout")};
  background-size:12px; background-position:center; background-repeat:no-repeat;
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
{btn} {{
  background:transparent!important; box-shadow:none!important;
  display:flex!important; align-items:center!important;
}}
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
    tokens = int(st.session_state.get("tokens", 0) or 0)
    initial = (user.strip()[:1] or "U").upper()

    tokens_txt = format_num(tokens)

    with st.sidebar:
        with st.container(key="sb_shell"):
            st.markdown(
                f'<div class="sb-brand">{_LOGO}'
                f'<div class="sb-brand-meta">'
                f'<span class="sb-name">{html.escape(APP_NAME)}</span>'
                f'<span class="sb-tag">Workspace</span></div></div>',
                unsafe_allow_html=True,
            )
            _render_nav(active)
            with st.container(key="sb_bottom"):
                st.markdown(
                    f'<div class="sb-user"><div class="sb-av">{html.escape(initial)}</div>'
                    f'<div class="sb-user-meta"><div class="sb-un">{html.escape(user)}</div>'
                    f'<div class="sb-up"><span class="sb-plan">{html.escape(plan)}</span>'
                    f'<span class="sb-tokens">{html.escape(tokens_txt)} Tokens</span></div></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Abmelden", key="nav_logout", use_container_width=True, type="tertiary"):
                    from services.session_auth import logout_session
                    logout_session()
                    st.rerun()
