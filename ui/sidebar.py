"""
MaByte sidebar — single nav component (250px, icon + label rows).
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

_SB = 'section[data-testid="stSidebar"]'
_SB_W = "250px"

SIDEBAR_NAV_ITEMS: list[tuple[str, str]] = [
    ("Dashboard", "home"),
    ("Chat", "chat"),
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

# Lucide-style stroke icons (22px rendered)
_ICON: dict[str, str] = {
    "home": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "chat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>',
    "football": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="1" fill="{c}"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>',
    "video": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482A.5.5 0 0 0 22 16.07V7.93a.5.5 0 0 0-.777-.416L16 11"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>',
    "music": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
    "coding": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "projects": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>',
    "automation_lab": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>',
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "premium": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6 9 2 3 8l9 14 9-14-6-6-3 4Z"/><path d="M3 8h18"/></svg>',
    "logout": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>',
}

_BRAND_MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">'
    '<defs><linearGradient id="mbg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    '</linearGradient></defs>'
    '<rect width="32" height="32" rx="8" fill="url(#mbg)"/>'
    '<path d="M9 22V10l5 7 5-7v12" fill="none" stroke="#fafafa" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)


def _icon_uri(page: str, *, active: bool = False) -> str:
    color = "%23fafafa" if active else "%23a1a1aa"
    tpl = _ICON.get(page) or _ICON["home"]
    return f'url("data:image/svg+xml,{quote(tpl.format(c=color))}")'


def sidebar_master_css(active_page: str = "home") -> str:
    active = active_page or "home"
    active_key = f"nav_{active}"
    icon_rules: list[str] = []

    for _, page in SIDEBAR_NAV_ITEMS:
        key = f"nav_{page}"
        uri = _icon_uri(page, active=(page == active))
        icon_rules.append(
            f'{_SB} .st-key-{key} .stButton > button::before {{'
            f'content:"";position:absolute;left:14px;top:50%;transform:translateY(-50%);'
            f'width:22px;height:22px;background-image:{uri};background-size:22px 22px;'
            f'background-repeat:no-repeat;background-position:center;flex-shrink:0;}}'
        )

    logout_uri = _icon_uri("logout")
    return f"""
:root {{ --sb-width: {_SB_W}; }}
{_SB} {{
    width:var(--sb-width)!important;min-width:var(--sb-width)!important;max-width:var(--sb-width)!important;
    background:#08080a!important;border-right:1px solid rgba(255,255,255,.06)!important;
}}
@media (min-width:769px) {{
    {_SB}, {_SB} > div, {_SB} [data-testid="stSidebarContent"],
    {_SB} [data-testid="stSidebarUserContent"] {{
        overflow:hidden!important;overflow-y:hidden!important;max-height:100vh!important;
    }}
}}
{_SB} > div {{padding:0 12px 10px 12px!important;}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
    padding:0!important;margin:0!important;background:#08080a!important;
    display:flex!important;flex-direction:column!important;min-height:100vh!important;
}}
{_SB} [data-testid="stSidebarNav"] {{display:none!important;}}
{_SB} [data-testid="stVerticalBlock"],
{_SB} [data-testid="stVerticalBlock"] > div,
{_SB} [data-testid="stVerticalBlockBorderWrapper"],
{_SB} [data-testid="stElementContainer"] {{
    gap:0!important;padding:0!important;margin:0!important;
    border:none!important;box-shadow:none!important;background:transparent!important;
}}
.sb-brand {{
    display:flex;align-items:center;gap:10px;height:56px;max-height:56px;
    padding:8px 4px 12px;box-sizing:border-box;
}}
.sb-brand-mark {{width:32px;height:32px;flex-shrink:0;display:flex;align-items:center;justify-content:center;}}
.sb-brand-mark svg {{display:block;width:32px;height:32px;}}
.sb-brand-text {{
    margin:0;color:#fafafa!important;font-size:17px;font-weight:700;
    letter-spacing:-.03em;line-height:1;white-space:nowrap;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton {{
    margin:6px 0!important;padding:0!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button {{
    width:100%!important;min-height:48px!important;height:48px!important;
    margin:0!important;padding:0 14px 0 50px!important;border-radius:10px!important;
    border:1px solid transparent!important;border-left:4px solid transparent!important;
    background:transparent!important;color:#a1a1aa!important;
    font-size:15px!important;font-weight:600!important;line-height:1!important;
    text-align:left!important;position:relative!important;
    white-space:nowrap!important;overflow:visible!important;box-shadow:none!important;
    transition:background .15s ease,color .15s ease,box-shadow .15s ease,border-color .15s ease!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button p {{
    color:inherit!important;font-size:15px!important;font-weight:600!important;
    margin:0!important;line-height:1!important;white-space:nowrap!important;
    overflow:visible!important;text-overflow:clip!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:hover {{
    background:rgba(24,24,27,.95)!important;color:#e4e4e7!important;
    border-left-color:rgba(255,255,255,.08)!important;
}}
{_SB} .st-key-{active_key} .stButton > button {{
    background:linear-gradient(90deg,rgba(76,29,149,.55) 0%,rgba(30,27,75,.35) 100%)!important;
    color:#fafafa!important;font-weight:600!important;
    border:1px solid rgba(139,92,246,.35)!important;
    border-left:4px solid #a78bfa!important;
    box-shadow:0 0 24px rgba(139,92,246,.22),inset 0 1px 0 rgba(255,255,255,.06)!important;
}}
{_SB} .st-key-{active_key} .stButton > button::before {{
    background-image:{_icon_uri(active, active=True)}!important;
}}
{_SB} .st-key-{active_key} .stButton > button p {{
    color:#fafafa!important;font-weight:600!important;
}}
{"".join(icon_rules)}
{_SB} .st-key-nav_logout {{
    margin-top:auto!important;padding-top:10px!important;flex-shrink:0!important;
}}
{_SB} .st-key-nav_logout .stButton {{
    margin:6px 0 0!important;padding:0!important;
}}
{_SB} .st-key-nav_logout .stButton > button {{
    min-height:48px!important;height:48px!important;width:100%!important;
    padding:0 14px 0 50px!important;border-radius:10px!important;
    border:1px solid rgba(255,255,255,.08)!important;
    background:#111113!important;color:#a1a1aa!important;
    font-size:15px!important;font-weight:600!important;position:relative!important;
    white-space:nowrap!important;
}}
{_SB} .st-key-nav_logout .stButton > button::before {{
    content:"";position:absolute;left:14px;top:50%;transform:translateY(-50%);
    width:22px;height:22px;background-image:{logout_uri};background-size:22px 22px;
    background-repeat:no-repeat;background-position:center;
}}
{_SB} .st-key-nav_logout .stButton > button p {{
    color:inherit!important;font-size:15px!important;font-weight:600!important;margin:0!important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover {{
    background:rgba(127,29,29,.16)!important;color:#fca5a5!important;
    border-color:rgba(248,113,113,.22)!important;
}}
"""


def _resolve_active(active_page: str | None) -> str:
    active = (active_page or st.session_state.get("page") or "home").strip()
    return LEGACY_PAGE_ALIASES.get(active, active)


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))

    brand = (
        f'<div class="sb-brand">'
        f'<div class="sb-brand-mark">{_BRAND_MARK}</div>'
        f'<span class="sb-brand-text">{html.escape(APP_NAME)}</span>'
        f"</div>"
    )

    with st.sidebar:
        st.markdown(brand, unsafe_allow_html=True)
        for label, page in SIDEBAR_NAV_ITEMS:
            if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
                st.session_state.page = page
                st.rerun()
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
