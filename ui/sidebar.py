"""
MaByte sidebar — single SaaS nav (240px, sections, icons, user footer).
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

_SB = 'section[data-testid="stSidebar"]'
_SB_W = "240px"

SIDEBAR_SECTIONS: list[tuple[str | None, list[tuple[str, str]]]] = [
    (None, [("Dashboard", "home")]),
    ("WORKSPACE", [("AI Chat", "chat"), ("Projects", "projects"), ("Automations", "automation_lab")]),
    ("CREATOR", [("Image", "image"), ("Video", "video"), ("Music", "music"), ("Code", "coding")]),
    ("INTELLIGENCE", [("Football AI", "football")]),
    ("ACCOUNT", [("Profile", "dashboard"), ("Premium", "premium")]),
]

SIDEBAR_NAV_ITEMS: list[tuple[str, str]] = [
    item for _, items in SIDEBAR_SECTIONS for item in items
]

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "video",
    "creator": "video",
    "automations": "automation_lab",
}

# Lucide icons (stroke 2, 24×24) — https://lucide.dev
_LUCIDE = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_ICON: dict[str, str] = {
    "home": f"<svg {_LUCIDE}><rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\"/></svg>",
    "chat": f"<svg {_LUCIDE}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "projects": f"<svg {_LUCIDE}><path d=\"M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.07 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z\"/><path d=\"M8 10v4\"/><path d=\"M12 10v2\"/><path d=\"M16 10v6\"/></svg>",
    "automation_lab": f"<svg {_LUCIDE}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "image": f"<svg {_LUCIDE}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" ry=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_LUCIDE}><path d=\"M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z\"/><path d=\"m8 2 2 3\"/><path d=\"m16 2-2 3\"/></svg>",
    "music": f"<svg {_LUCIDE}><path d=\"M9 18V5l12-2v13\"/><circle cx=\"6\" cy=\"18\" r=\"3\"/><circle cx=\"18\" cy=\"16\" r=\"3\"/></svg>",
    "coding": f"<svg {_LUCIDE}><path d=\"m18 16 4-4-4-4\"/><path d=\"m6 8-4 4 4 4\"/><path d=\"M10.5 4 8 16\"/><path d=\"m14.5 4 7 16\"/></svg>",
    "football": f"<svg {_LUCIDE}><path d=\"M6 9H4.5a2.5 2.5 0 0 1 0-5H6\"/><path d=\"M18 9h1.5a2.5 2.5 0 0 0 0-5H18\"/><path d=\"M4 22h16\"/><path d=\"M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.7 7 22\"/><path d=\"M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.7 17 22\"/><path d=\"M18 2H6v7a6 6 0 0 0 12 0V2Z\"/></svg>",
    "dashboard": f"<svg {_LUCIDE}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_LUCIDE}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
    "logout": f"<svg {_LUCIDE}><path d=\"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4\"/><polyline points=\"16 17 21 12 16 7\"/><line x1=\"21\" x2=\"9\" y1=\"12\" y2=\"12\"/></svg>",
}

_BRAND_MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="36" height="36">'
    '<defs><linearGradient id="mbg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    "</linearGradient></defs>"
    '<rect width="40" height="40" rx="10" fill="url(#mbg)"/>'
    '<path d="M11 28V12l6.5 8.5L24 12v16" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)


def _icon_uri(page: str, *, active: bool = False) -> str:
    color = "%23ffffff" if active else "%23a1a1aa"
    tpl = _ICON.get(page) or _ICON["home"]
    return f'url("data:image/svg+xml,{quote(tpl.format(c=color))}")'


def _plan_label(plan: str) -> str:
    key = (plan or "free").strip().lower()
    if key in ("none", ""):
        return "Free"
    return key.replace("_", " ").title()


def _user_initial(username: str) -> str:
    u = (username or "U").strip()
    return (u[0] or "U").upper()


def sidebar_master_css(active_page: str = "home") -> str:
    active = active_page or "home"
    active_key = f"nav_{active}"
    icon_rules: list[str] = []

    for _, page in SIDEBAR_NAV_ITEMS:
        key = f"nav_{page}"
        is_active = page == active
        uri = _icon_uri(page, active=is_active)
        icon_rules.append(
            f'{_SB} .st-key-{key} .stButton > button::before {{'
            f'content:"";position:absolute;left:14px;top:50%;transform:translateY(-50%);'
            f'width:20px;height:20px;background-image:{uri};background-size:20px 20px;'
            f'background-repeat:no-repeat;background-position:center;}}'
        )

    logout_uri = _icon_uri("logout")
    return f"""
:root {{ --sb-width: {_SB_W}; }}
{_SB} {{
    width:var(--sb-width)!important;min-width:var(--sb-width)!important;max-width:var(--sb-width)!important;
    height:100vh!important;position:sticky!important;top:0!important;
    background:#09090b!important;border-right:1px solid rgba(255,255,255,.06)!important;
    overflow:hidden!important;
}}
{_SB} > div {{
    padding:0 10px 12px 10px!important;overflow:hidden!important;height:100vh!important;
}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
    padding:0!important;margin:0!important;background:#09090b!important;
    display:flex!important;flex-direction:column!important;
    min-height:100vh!important;height:100vh!important;overflow:hidden!important;
}}
@media (min-width:769px) {{
    {_SB}, {_SB} > div, {_SB} [data-testid="stSidebarContent"],
    {_SB} [data-testid="stSidebarUserContent"] {{
        overflow-y:hidden!important;scrollbar-width:none!important;
    }}
    {_SB} ::-webkit-scrollbar {{ display:none!important;width:0!important;height:0!important; }}
}}
@media (max-width:768px) {{
    {_SB} [data-testid="stSidebarContent"],
    {_SB} [data-testid="stSidebarUserContent"] {{
        overflow-y:auto!important;
    }}
}}
{_SB} [data-testid="stSidebarNav"] {{ display:none!important; }}
{_SB} [data-testid="stVerticalBlock"],
{_SB} [data-testid="stVerticalBlock"] > div,
{_SB} [data-testid="stVerticalBlockBorderWrapper"],
{_SB} [data-testid="stElementContainer"] {{
    gap:0!important;padding:0!important;margin:0!important;
    border:none!important;box-shadow:none!important;background:transparent!important;
}}
.sb-brand {{
    display:flex;align-items:center;gap:10px;padding:16px 10px 12px;box-sizing:border-box;
}}
.sb-brand-mark {{ display:flex;align-items:center;justify-content:center;flex-shrink:0; }}
.sb-brand-mark svg {{ width:36px;height:36px;display:block; }}
.sb-brand-text {{
    margin:0;color:#fafafa!important;font-size:16px;font-weight:600;
    letter-spacing:-.02em;line-height:1;
}}
.sb-section {{
    color:#52525b!important;font-size:10px;font-weight:700;letter-spacing:.12em;
    text-transform:uppercase;padding:14px 12px 4px;margin:0;
}}
.sb-rule {{
    height:1px;margin:0 0 6px;background:rgba(255,255,255,.07);
}}
.sb-footer {{ margin-top:auto!important;padding-top:6px;flex-shrink:0!important; }}
.sb-user {{
    display:flex;align-items:center;gap:10px;padding:10px 12px;margin-bottom:6px;
    border-radius:12px;background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.06);box-sizing:border-box;
}}
.sb-avatar {{
    width:36px;height:36px;min-width:36px;border-radius:10px;
    background:linear-gradient(135deg,#7c3aed,#6366f1);
    color:#fff;font-size:14px;font-weight:700;
    display:flex;align-items:center;justify-content:center;
}}
.sb-user-meta {{ min-width:0;flex:1; }}
.sb-user-name {{
    color:#fafafa!important;font-size:14px;font-weight:600;line-height:1.2;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}}
.sb-user-plan {{
    color:#71717a!important;font-size:12px;font-weight:500;line-height:1.2;margin-top:2px;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton {{
    margin:2px 0!important;padding:0!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button {{
    width:100%!important;min-height:44px!important;height:44px!important;
    margin:0!important;padding:0 12px 0 46px!important;border-radius:10px!important;
    border:1px solid transparent!important;border-left:3px solid transparent!important;
    background:transparent!important;color:#a1a1aa!important;
    font-size:14px!important;font-weight:500!important;line-height:1!important;
    text-align:left!important;position:relative!important;
    white-space:nowrap!important;overflow:visible!important;box-shadow:none!important;
    opacity:.75!important;
    transition:background 180ms ease,color 180ms ease,border-color 180ms ease,
        transform 180ms ease,opacity 180ms ease!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button p {{
    color:inherit!important;font-size:14px!important;font-weight:500!important;
    margin:0!important;line-height:1!important;white-space:nowrap!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-{active_key}) .stButton > button:hover {{
    opacity:1!important;
    background:rgba(255,255,255,.06)!important;
    color:#e4e4e7!important;
    transform:translateX(2px)!important;
}}
{_SB} .st-key-{active_key} .stButton > button {{
    opacity:1!important;
    background:rgba(124,58,237,.2)!important;
    color:#ffffff!important;
    border-left:3px solid #8B5CF6!important;
    transform:none!important;
}}
{_SB} .st-key-{active_key} .stButton > button::before {{
    background-image:{_icon_uri(active, active=True)}!important;
}}
{_SB} .st-key-{active_key} .stButton > button p {{
    color:#ffffff!important;font-weight:500!important;
}}
{_SB} .st-key-{active_key} .stButton > button:hover {{
    background:rgba(124,58,237,.26)!important;
    color:#ffffff!important;
    transform:none!important;
}}
{"".join(icon_rules)}
{_SB} .st-key-nav_logout .stButton {{
    margin:0!important;padding:0!important;
}}
{_SB} .st-key-nav_logout .stButton > button {{
    min-height:44px!important;height:44px!important;width:100%!important;
    padding:0 12px 0 46px!important;border-radius:10px!important;
    border:1px solid rgba(255,255,255,.08)!important;
    background:rgba(255,255,255,.03)!important;color:#a1a1aa!important;
    font-size:14px!important;font-weight:500!important;position:relative!important;
    opacity:.75!important;
    transition:background 180ms ease,color 180ms ease,transform 180ms ease,opacity 180ms ease!important;
}}
{_SB} .st-key-nav_logout .stButton > button::before {{
    content:"";position:absolute;left:14px;top:50%;transform:translateY(-50%);
    width:20px;height:20px;background-image:{logout_uri};background-size:20px 20px;
    background-repeat:no-repeat;background-position:center;
}}
{_SB} .st-key-nav_logout .stButton > button p {{
    color:inherit!important;font-size:14px!important;font-weight:500!important;margin:0!important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover {{
    opacity:1!important;
    background:rgba(255,255,255,.06)!important;
    color:#fafafa!important;
    transform:translateX(2px)!important;
}}
"""


def _resolve_active(active_page: str | None) -> str:
    active = (active_page or st.session_state.get("page") or "home").strip()
    return LEGACY_PAGE_ALIASES.get(active, active)


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))

    user = str(st.session_state.get("user", "User"))
    plan = _plan_label(str(st.session_state.get("plan", "free")))

    brand = (
        f'<div class="sb-brand">'
        f'<div class="sb-brand-mark">{_BRAND_MARK}</div>'
        f'<span class="sb-brand-text">{html.escape(APP_NAME)}</span>'
        f"</div>"
        f'<div class="sb-rule"></div>'
    )

    footer = (
        f'<div class="sb-footer">'
        f'<div class="sb-rule"></div>'
        f'<div class="sb-user">'
        f'<div class="sb-avatar">{html.escape(_user_initial(user))}</div>'
        f'<div class="sb-user-meta">'
        f'<div class="sb-user-name">{html.escape(user)}</div>'
        f'<div class="sb-user-plan">{html.escape(plan)}</div>'
        f"</div></div></div>"
    )

    with st.sidebar:
        st.markdown(brand, unsafe_allow_html=True)
        for section_title, items in SIDEBAR_SECTIONS:
            if section_title:
                st.markdown(
                    f'<p class="sb-section">{html.escape(section_title)}</p>',
                    unsafe_allow_html=True,
                )
            for label, page in items:
                if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
                    st.session_state.page = page
                    st.rerun()
        st.markdown(footer, unsafe_allow_html=True)
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
