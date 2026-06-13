"""
MaByte Sidebar — standard flat navigation, session-safe.

Uses native st.button icons (Material Symbols) so rows can never
collapse or overlap; no column/HTML icon hacks.
"""
from __future__ import annotations

import html

import streamlit as st

from config import APP_NAME
from ui.components import format_num
from ui.styles import MB_APP_BACKGROUND, inject_css

_SB = 'section[data-testid="stSidebar"]'
SIDEBAR_WIDTH = "240px"
_NAV = '[class*="st-key-sb_nav_"]'
_SHELL = f"{_SB} .st-key-sb_shell"
# Shell column = the vertical block that directly contains sb_bottom.
# :has() keeps this independent of where Streamlit puts the st-key class
# (1.50 puts it on the border wrapper, older builds on an outer wrapper).
_COL = f'{_SHELL} [data-testid="stVerticalBlock"]:has(> .st-key-sb_bottom)'
_USER_CONTENT = f'{_SB} [data-testid="stSidebarUserContent"]'

_BG = "#09090b"
_APP_BG = MB_APP_BACKGROUND
_LINE = "rgba(255, 255, 255, 0.08)"
_MUTED = "#71717a"
_TEXT = "#d4d4d8"
_BTN_H = 36

NAV_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Workspace", [("Dashboard", "home"), ("AI Chat", "chat"), ("Football", "football"), ("Automation", "automation_lab")]),
    ("Create", [("Image", "image"), ("Video", "video"), ("Code", "coding")]),
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
    "social_oauth": "dashboard",
}

STAFF_NAV_PAGE = "admin"
STAFF_NAV_ITEM = ("Admin", STAFF_NAV_PAGE)

SIDEBAR_NAV_ITEMS = NAV_ITEMS
VALID_NAV_PAGES = frozenset(p for _, p in NAV_ITEMS)
ROUTE_PAGES = VALID_NAV_PAGES | frozenset({STAFF_NAV_PAGE})

_NAV_ICONS: dict[str, str] = {
    "home": ":material/grid_view:",
    "chat": ":material/chat_bubble:",
    "football": ":material/sports_soccer:",
    "automation_lab": ":material/account_tree:",
    "image": ":material/image:",
    "video": ":material/movie:",
    "coding": ":material/code:",
    "dashboard": ":material/person:",
    "premium": ":material/workspace_premium:",
    "admin": ":material/admin_panel_settings:",
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
    if target == STAFF_NAV_PAGE and not _session_is_staff():
        return
    if st.session_state.get("page") != target:
        st.session_state.page = target
        st.rerun()


def _resolve_active(active_page: str | None) -> str:
    raw = (active_page or st.session_state.get("page") or "home").strip()
    page = LEGACY_PAGE_ALIASES.get(raw, raw)
    if page in ROUTE_PAGES:
        return page
    return NAV_HIGHLIGHT_ALIASES.get(page, "home")


def _nav_key(page: str) -> str:
    return f"sb_nav_{page}"


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
  gap:10px!important; box-shadow:none!important; line-height:1!important;
}}
{btn}:hover {{ background:rgba(255,255,255,0.05)!important; color:#fafafa!important; }}
{btn} p, {btn} span, {btn} div {{
  margin:0!important; padding:0!important; color:inherit!important;
  font-size:13px!important; line-height:1!important; white-space:nowrap!important;
}}
{_SB} {_NAV} [data-testid="stIconMaterial"] {{
  font-size:17px!important; color:#a1a1aa!important; line-height:1!important;
}}
{btn}:hover [data-testid="stIconMaterial"] {{ color:#fafafa!important; }}
"""
    ]
    key = _nav_key(active)
    sel = f"{_SB} .st-key-{key} .stButton > button, {_SB} .st-key-{key} button"
    parts.append(
        f"{sel} {{ background:rgba(39,39,42,0.95)!important;"
        f" color:#fafafa!important; font-weight:600!important; }}"
        f"{_SB} .st-key-{key} [data-testid='stIconMaterial'] {{ color:#fafafa!important; }}"
    )
    return "".join(parts)


def _base_css() -> str:
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
{_SB} [data-testid="stSidebarNav"] {{ display:none!important; }}
/* --- Scroll chain: lock outer shell to viewport, let the nav column scroll --- */
{_SB}>div {{
  padding:0!important; height:100dvh!important; overflow:hidden!important;
  display:flex!important; flex-direction:column!important;
}}
{_SB} [data-testid="stSidebarContent"] {{
  flex:1 1 auto!important; min-height:0!important; overflow:hidden!important;
  display:flex!important; flex-direction:column!important; padding:0!important;
}}
{_USER_CONTENT} {{
  flex:1 1 auto!important; min-height:0!important; padding:0!important;
  display:flex!important; flex-direction:column!important;
  overflow-y:auto!important; overflow-x:hidden!important;
}}
{_USER_CONTENT}>[data-testid="stVerticalBlock"] {{
  flex:1 1 auto!important; min-height:0!important; gap:0!important;
  display:flex!important; flex-direction:column!important;
}}
{_SHELL}, {_SHELL}>div {{
  flex:1 1 auto!important; min-height:0!important; height:auto!important;
  display:flex!important; flex-direction:column!important;
  background:transparent!important; border:none!important; padding:0!important; margin:0!important;
}}
{_COL} {{
  flex:1 1 auto!important; min-height:0!important;
  display:flex!important; flex-direction:column!important;
  padding:16px 14px 0!important; gap:3px!important;
  overflow-y:auto!important; overflow-x:hidden!important;
}}
/* Thin, subtle sidebar scrollbar */
{_COL}, {_USER_CONTENT} {{
  scrollbar-width:thin; scrollbar-color:rgba(255,255,255,0.15) transparent;
}}
{_COL}::-webkit-scrollbar, {_USER_CONTENT}::-webkit-scrollbar {{ width:6px; height:6px; }}
{_COL}::-webkit-scrollbar-thumb, {_USER_CONTENT}::-webkit-scrollbar-thumb {{
  background:rgba(255,255,255,0.15); border-radius:6px;
}}
{_COL}::-webkit-scrollbar-track, {_USER_CONTENT}::-webkit-scrollbar-track {{
  background:transparent;
}}
{_SHELL} .st-key-sb_bottom [data-testid="stVerticalBlock"] {{ gap:6px!important; }}
{_SHELL} [data-testid="stMarkdownContainer"], {_SHELL} [data-testid="stElementContainer"] {{
  margin:0!important; padding:0!important;
}}
{_SHELL} [data-testid="stMarkdownContainer"] p {{ margin:0!important; padding:0!important; }}
{_SHELL} .st-key-sb_bottom {{
  position:sticky!important; bottom:0!important; z-index:2!important;
  margin-top:auto!important; flex-shrink:0!important;
  padding-top:12px!important; padding-bottom:14px!important;
  background:{_BG}!important; border-top:1px solid {_LINE};
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
{_SB} {_NAV} .stButton {{ margin:0!important; padding:0!important; width:100%!important; }}
.sb-user {{
  display:flex; align-items:center; gap:10px;
  padding:10px; margin:0 0 4px;
  background:linear-gradient(135deg, rgba(139,92,246,0.10), rgba(24,24,27,0.6));
  backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
  border:1px solid rgba(255,255,255,0.10); border-radius:12px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,0.06), inset 0 0 18px rgba(139,92,246,0.06);
  user-select:none; -webkit-user-select:none; overflow:hidden;
}}
.sb-avatar {{
  flex:0 0 auto; width:30px; height:30px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#8b5cf6,#6366f1);
  color:#fff!important; font-size:13px; font-weight:700; line-height:1;
}}
.sb-user-info {{ flex:1 1 auto; min-width:0; }}
.sb-un {{
  color:#f4f4f5!important; font-size:13px; font-weight:600; margin:0;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.sb-meta {{
  color:{_MUTED}!important; font-size:11px; margin:2px 0 0!important;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.sb-badges {{
  flex:0 0 auto; display:flex; flex-wrap:wrap; gap:4px;
  justify-content:flex-end; max-width:100px;
}}
.sb-plan {{
  flex:0 0 auto; padding:3px 8px; border-radius:999px;
  font-size:9px; font-weight:700; letter-spacing:0.08em;
  text-transform:uppercase; line-height:1.3;
}}
.sb-plan-elite {{
  background:linear-gradient(135deg, rgba(139,92,246,0.35), rgba(99,102,241,0.22));
  border:1px solid rgba(167,139,250,0.45); color:#c4b5fd!important;
  text-shadow:0 0 8px rgba(139,92,246,0.55);
  box-shadow:0 0 10px rgba(139,92,246,0.25);
}}
.sb-plan-default {{
  background:rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.12); color:#a1a1aa!important;
}}
.sb-plan-admin {{
  background:linear-gradient(135deg, rgba(34,211,238,0.30), rgba(6,182,212,0.18));
  border:1px solid rgba(103,232,249,0.45); color:#67e8f9!important;
  text-shadow:0 0 8px rgba(34,211,238,0.50);
  box-shadow:0 0 10px rgba(34,211,238,0.20);
}}
{_SB} .st-key-nav_logout .stButton>button, {_SB} .st-key-nav_logout button {{
  width:100%!important; height:32px!important; min-height:32px!important;
  padding:0 10px!important; border-radius:8px!important;
  border:1px solid {_LINE}!important; background:transparent!important;
  color:{_MUTED}!important; font-size:12px!important;
  display:flex!important; align-items:center!important; gap:8px!important;
  box-shadow:none!important;
}}
{_SB} .st-key-nav_logout [data-testid="stIconMaterial"] {{
  font-size:15px!important; color:{_MUTED}!important;
}}
{_SB} .st-key-nav_logout .stButton>button:hover {{
  color:#f87171!important; background:rgba(248,113,113,0.06)!important;
}}
{_SB} .st-key-nav_logout .stButton>button:hover [data-testid="stIconMaterial"] {{
  color:#f87171!important;
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
            clicked = st.button(
                label,
                key=_nav_key(page),
                icon=_NAV_ICONS.get(page),
                use_container_width=True,
                type="tertiary",
            )
            if clicked and page != active:
                navigate_to(page)
    if _session_is_staff():
        label, page = STAFF_NAV_ITEM
        st.markdown(f'<p class="sb-sec">Team</p>', unsafe_allow_html=True)
        clicked = st.button(
            label,
            key=_nav_key(page),
            icon=_NAV_ICONS.get(page),
            use_container_width=True,
            type="tertiary",
        )
        if clicked and page != active:
            navigate_to(page)


def _session_is_staff() -> bool:
    from services.session_auth import server_is_supporter
    return server_is_supporter()


def _session_is_admin() -> bool:
    """Admin check from session_state (role/admin_level synced on login)."""
    from security import is_admin
    return is_admin({
        "role": st.session_state.get("role", "user"),
        "admin_level": st.session_state.get("admin_level", 0),
    })


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
        with st.container(key="sb_shell", border=False):
            st.markdown(
                f'<div class="sb-brand">{_LOGO}<span class="sb-name">{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )
            _render_nav(active)
            with st.container(key="sb_bottom", border=False):
                initial = (user.strip()[:1] or "U").upper()
                plan_cls = "sb-plan-elite" if plan == "Elite" else "sb-plan-default"
                badges = f'<span class="sb-plan {plan_cls}">{html.escape(plan)}</span>'
                if _session_is_admin():
                    badges += '<span class="sb-plan sb-plan-admin">Admin</span>'
                st.markdown(
                    f'<div class="sb-user">'
                    f'<span class="sb-avatar">{html.escape(initial)}</span>'
                    f'<div class="sb-user-info">'
                    f'<p class="sb-un">{html.escape(user)}</p>'
                    f'<p class="sb-meta">{html.escape(tokens)} Tokens</p>'
                    f"</div>"
                    f'<div class="sb-badges">{badges}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Abmelden",
                    key="nav_logout",
                    icon=":material/logout:",
                    use_container_width=True,
                    type="tertiary",
                ):
                    from services.session_auth import logout_session
                    logout_session()
                    st.rerun()
