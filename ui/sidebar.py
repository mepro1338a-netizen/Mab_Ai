"""
MaByte Sidebar — single component (230px, Lucide icons, compact nav).
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

_SB = 'section[data-testid="stSidebar"]'
_WIDTH = "230px"

NAV_ITEMS: list[tuple[str, str]] = [
    ("Dashboard", "home"),
    ("AI Chat", "chat"),
    ("Football AI", "football"),
    ("Image", "image"),
    ("Video", "video"),
    ("Music", "music"),
    ("Code", "coding"),
    ("Projects", "projects"),
    ("Automations", "automation_lab"),
    ("Profile", "dashboard"),
    ("Premium", "premium"),
]

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "video",
    "creator": "video",
    "automations": "automation_lab",
}

SIDEBAR_NAV_ITEMS = NAV_ITEMS

_LUCIDE = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_ICONS: dict[str, str] = {
    "home": f"<svg {_LUCIDE}><rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\"/></svg>",
    "chat": f"<svg {_LUCIDE}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "football": f"<svg {_LUCIDE}><path d=\"M6 9H4.5a2.5 2.5 0 0 1 0-5H6\"/><path d=\"M18 9h1.5a2.5 2.5 0 0 0 0-5H18\"/><path d=\"M4 22h16\"/><path d=\"M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.7 7 22\"/><path d=\"M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.7 17 22\"/><path d=\"M18 2H6v7a6 6 0 0 0 12 0V2Z\"/></svg>",
    "image": f"<svg {_LUCIDE}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" ry=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_LUCIDE}><path d=\"M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z\"/><path d=\"m8 2 2 3\"/><path d=\"m16 2-2 3\"/></svg>",
    "music": f"<svg {_LUCIDE}><path d=\"M9 18V5l12-2v13\"/><circle cx=\"6\" cy=\"18\" r=\"3\"/><circle cx=\"18\" cy=\"16\" r=\"3\"/></svg>",
    "coding": f"<svg {_LUCIDE}><path d=\"m18 16 4-4-4-4\"/><path d=\"m6 8-4 4 4 4\"/><path d=\"M10.5 4 8 16\"/><path d=\"m14.5 4 7 16\"/></svg>",
    "projects": f"<svg {_LUCIDE}><path d=\"M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.07 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z\"/><path d=\"M8 10v4\"/><path d=\"M12 10v2\"/><path d=\"M16 10v6\"/></svg>",
    "automation_lab": f"<svg {_LUCIDE}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "dashboard": f"<svg {_LUCIDE}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_LUCIDE}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
    "logout": f"<svg {_LUCIDE}><path d=\"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4\"/><polyline points=\"16 17 21 12 16 7\"/><line x1=\"21\" x2=\"9\" y1=\"12\" y2=\"12\"/></svg>",
}

_BRAND_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="26" height="26">'
    '<defs><linearGradient id="mbs" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    '</linearGradient></defs><rect width="40" height="40" rx="9" fill="url(#mbs)"/>'
    '<path d="M11 28V12l6.5 8.5L24 12v16" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def _icon_uri(page: str, *, active: bool = False) -> str:
    color = "%23ffffff" if active else "%23a1a1aa"
    svg = _ICONS.get(page) or _ICONS["home"]
    return f'url("data:image/svg+xml,{quote(svg.format(c=color))}")'


def _plan_label(plan: str) -> str:
    key = (plan or "free").strip().lower()
    return "Free" if key in ("none", "") else key.replace("_", " ").title()


def _user_initial(username: str) -> str:
    u = (username or "U").strip()
    return (u[0] or "U").upper()


def sidebar_master_css(active_page: str) -> str:
    active = active_page or "home"
    active_key = f"nav_{active}"
    icon_rules: list[str] = []
    for _, page in NAV_ITEMS:
        key = f"nav_{page}"
        icon_rules.append(
            f'{_SB} .st-key-{key} .stButton>button::before{{'
            f"content:'';position:absolute;left:10px;top:50%;transform:translateY(-50%);"
            f"width:16px;height:16px;background-image:{_icon_uri(page, active=page == active)};"
            f"background-size:16px 16px;background-repeat:no-repeat;background-position:center;}}"
        )
    logout_uri = _icon_uri("logout")
    return f"""
:root{{--sb-width:{_WIDTH};}}
{_SB}{{
  width:var(--sb-width)!important;min-width:var(--sb-width)!important;max-width:var(--sb-width)!important;
  background:#09090b!important;border-right:1px solid rgba(255,255,255,.06)!important;overflow:hidden!important;
}}
{_SB}>div{{padding:0 8px 10px!important;height:100vh!important;overflow:hidden!important;}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"]{{
  padding:0!important;background:#09090b!important;display:flex!important;flex-direction:column!important;
  height:100vh!important;overflow:hidden!important;
}}
@media (min-width:769px){{
  {_SB},{_SB}>div,{_SB} [data-testid="stSidebarContent"]{{overflow-y:hidden!important;scrollbar-width:none!important;}}
  {_SB}::-webkit-scrollbar{{display:none!important;}}
}}
{_SB} [data-testid="stSidebarNav"]{{display:none!important;}}
{_SB} [data-testid="stVerticalBlock"],
{_SB} [data-testid="stVerticalBlockBorderWrapper"],
{_SB} [data-testid="stElementContainer"]{{
  gap:0!important;padding:0!important;margin:0!important;border:none!important;
  box-shadow:none!important;background:transparent!important;
}}
.sb-brand{{display:flex;align-items:center;gap:8px;padding:12px 4px 10px;flex-shrink:0;line-height:1;}}
.sb-brand svg{{display:block;flex-shrink:0;width:26px!important;height:26px!important;}}
.sb-brand span{{color:#fafafa!important;font-size:14px;font-weight:600;letter-spacing:-.02em;line-height:1;}}
.sb-nav-wrap{{flex:1 1 auto;min-height:0;overflow:hidden;padding:2px 0;}}
.sb-foot{{margin-top:auto!important;padding:10px 0 4px;flex-shrink:0;border-top:1px solid rgba(255,255,255,.06);}}
.sb-user{{display:flex;align-items:center;gap:8px;padding:6px 8px;margin:0 0 6px;border-radius:8px;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);}}
.sb-av{{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#7c3aed,#6366f1);
  color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;}}
.sb-un{{color:#fafafa!important;font-size:12px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.sb-up{{color:#71717a!important;font-size:10px;line-height:1.2;}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton{{
  margin:0 0 6px 0!important;padding:0!important;width:100%!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton>button{{
  width:100%!important;height:42px!important;min-height:42px!important;max-height:42px!important;
  padding:0 12px 0 34px!important;border-radius:10px!important;
  border:1px solid transparent!important;border-left:3px solid transparent!important;
  background:transparent!important;color:#a1a1aa!important;font-size:13px!important;font-weight:500!important;
  text-align:left!important;justify-content:flex-start!important;align-items:center!important;
  position:relative!important;opacity:.75!important;box-shadow:none!important;
  transition:background .15s ease,color .15s ease,border-color .15s ease,opacity .15s ease!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton>button p{{
  color:inherit!important;font-size:13px!important;font-weight:500!important;margin:0!important;
  text-align:left!important;width:100%!important;line-height:1!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-{active_key}) .stButton>button:hover{{
  opacity:1!important;background:rgba(255,255,255,.05)!important;color:#e4e4e7!important;
}}
{_SB} .st-key-{active_key} .stButton>button{{
  opacity:1!important;background:rgba(124,58,237,.2)!important;color:#fff!important;
  border-left:3px solid #8b5cf6!important;
}}
{_SB} .st-key-{active_key} .stButton>button::before{{background-image:{_icon_uri(active, active=True)}!important;}}
{_SB} .st-key-{active_key} .stButton>button p{{color:#fff!important;}}
{"".join(icon_rules)}
{_SB} .st-key-nav_logout .stButton{{margin:0!important;padding:0!important;}}
{_SB} .st-key-nav_logout .stButton>button{{
  width:100%!important;height:42px!important;min-height:42px!important;max-height:42px!important;
  padding:0 12px 0 34px!important;border-radius:10px!important;
  border:1px solid rgba(255,255,255,.07)!important;background:rgba(255,255,255,.02)!important;
  color:#a1a1aa!important;font-size:13px!important;font-weight:500!important;
  text-align:left!important;justify-content:flex-start!important;align-items:center!important;
  position:relative!important;opacity:.75!important;box-shadow:none!important;
}}
{_SB} .st-key-nav_logout .stButton>button::before{{
  content:'';position:absolute;left:10px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;background-image:{logout_uri};background-size:16px 16px;background-repeat:no-repeat;
}}
{_SB} .st-key-nav_logout .stButton>button p{{
  text-align:left!important;margin:0!important;font-size:13px!important;
}}
{_SB} .st-key-nav_logout .stButton>button:hover{{
  opacity:1!important;background:rgba(255,255,255,.05)!important;color:#fafafa!important;
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

    brand = (
        f'<div class="sb-brand">{_BRAND_SVG}'
        f'<span>{html.escape(APP_NAME)}</span></div>'
    )
    foot = (
        f'<div class="sb-foot">'
        f'<div class="sb-user"><div class="sb-av">{html.escape(_user_initial(user))}</div>'
        f'<div><div class="sb-un">{html.escape(user)}</div>'
        f'<div class="sb-up">{html.escape(plan)}</div></div></div></div>'
    )

    with st.sidebar:
        st.markdown(brand, unsafe_allow_html=True)
        for label, page in NAV_ITEMS:
            if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
                st.session_state.page = page
                st.rerun()
        st.markdown(foot, unsafe_allow_html=True)
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
