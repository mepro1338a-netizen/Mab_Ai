"""
MaByte sidebar — single implementation (Enterprise SaaS nav).
Expanded 220px · Collapsed 64px · flat list · no sections.
"""
from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
_SB = 'section[data-testid="stSidebar"]'

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

_ICON: dict[str, str] = {
    "home": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21V12h6v9"/></svg>',
    "chat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M21 11.5a8.38 8.38 0 0 1-1.9 5.4 8.5 8.5 0 0 1-13.6 0A8.38 8.38 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5z"/></svg>',
    "football": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><circle cx="12" cy="12" r="9"/><path d="M12 3c2 3 2 15 0 18M3 12h18"/></svg>',
    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/></svg>',
    "video": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><rect x="2" y="4" width="15" height="16" rx="2"/><path d="M17 8.5 22 6v12l-5-2.5"/></svg>',
    "music": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
    "coding": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/></svg>',
    "projects": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M3 7h7V3H3zm11 0h7V3h-7zM3 21h7v-4H3zm11 0h7v-4h-7z"/></svg>',
    "automation_lab": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83"/></svg>',
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>',
    "premium": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7-6.3-4.6L5.7 21l2.3-7-6-4.6h7.6z"/></svg>',
}


def _svg_uri(page: str, *, active: bool = False) -> str:
    color = "%23fafafa" if active else "%23a1a1aa"
    tpl = _ICON.get(page) or _ICON["home"]
    return f'url("data:image/svg+xml,{quote(tpl.format(c=color))}")'


def sidebar_master_css(active_page: str = "home", *, collapsed: bool = False) -> str:
    active = active_page or "home"
    width = "64px" if collapsed else "220px"
    pad_x = "6px" if collapsed else "10px"
    active_key = f"nav_{active}"

    icon_rules: list[str] = []
    for _, page in SIDEBAR_NAV_ITEMS:
        key = f"nav_{page}"
        is_active = page == active
        uri = _svg_uri(page, active=is_active)
        if collapsed:
            icon_rules.append(
                f'{_SB} .st-key-{key} .stButton > button::before {{'
                f'content:"";position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);'
                f'width:18px;height:18px;background-image:{uri};background-size:18px;background-repeat:no-repeat;}}'
            )
        else:
            icon_rules.append(
                f'{_SB} .st-key-{key} .stButton > button::before {{'
                f'content:"";position:absolute;left:12px;top:50%;transform:translateY(-50%);'
                f'width:16px;height:16px;background-image:{uri};background-size:16px;background-repeat:no-repeat;}}'
            )

    collapsed_label = f"""
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-sb_toggle) .stButton > button p {{
    display:none!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-sb_toggle) .stButton > button {{
    padding:0!important;justify-content:center!important;
}}
""" if collapsed else ""

    return f"""
:root {{
    --sb-width-expanded: 220px;
    --sb-width-collapsed: 64px;
    --sb-width: {width};
}}
{_SB} {{
    width:var(--sb-width)!important;min-width:var(--sb-width)!important;max-width:var(--sb-width)!important;
    background:#09090b!important;border-right:1px solid rgba(255,255,255,.06)!important;
}}
@media (min-width:769px) {{
    {_SB}, {_SB} > div, {_SB} [data-testid="stSidebarContent"],
    {_SB} [data-testid="stSidebarUserContent"] {{
        overflow:hidden!important;overflow-y:hidden!important;max-height:100vh!important;
    }}
}}
{_SB} > div {{padding:0 {pad_x} 8px {pad_x}!important;}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
    padding:0!important;margin:0!important;background:#09090b!important;
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
    height:48px;max-height:48px;display:flex;align-items:center;
    {"justify-content:center;" if collapsed else "justify-content:flex-start;"}
    box-sizing:border-box;overflow:hidden;
}}
.sb-brand img {{
    max-height:{"28px" if collapsed else "32px"};width:auto;max-width:100%;
    object-fit:contain;display:block;
}}
.sb-brand-name {{
    margin:0;color:#fafafa;font-size:15px;font-weight:700;letter-spacing:-.02em;
}}
{_SB} .st-key-sb_toggle .stButton > button {{
    min-height:28px!important;height:28px!important;width:100%!important;
    margin:0 0 4px 0!important;padding:0!important;border-radius:6px!important;
    border:1px solid rgba(255,255,255,.06)!important;background:transparent!important;
    color:#71717a!important;font-size:12px!important;
}}
{_SB} .st-key-sb_toggle .stButton > button:hover {{
    background:#18181b!important;color:#e4e4e7!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-sb_toggle) .stButton {{
    margin:4px 0!important;padding:0!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-sb_toggle) .stButton > button {{
    width:100%!important;min-height:40px!important;height:40px!important;
    margin:0!important;padding:0 12px 0 40px!important;border-radius:8px!important;
    border:1px solid transparent!important;border-left:3px solid transparent!important;
    background:transparent!important;color:#a1a1aa!important;
    font-size:13px!important;font-weight:500!important;line-height:1!important;
    text-align:left!important;position:relative!important;
    white-space:nowrap!important;overflow:hidden!important;box-shadow:none!important;
    transition:background .12s ease,color .12s ease,border-color .12s ease!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-sb_toggle) .stButton > button p {{
    color:inherit!important;font-size:13px!important;font-weight:inherit!important;
    margin:0!important;line-height:1!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout):not(.st-key-sb_toggle) .stButton > button:hover {{
    background:#18181b!important;color:#e4e4e7!important;
    border-left-color:rgba(255,255,255,.1)!important;
}}
{_SB} .st-key-{active_key} .stButton > button {{
    background:rgba(124,58,237,.22)!important;color:#fafafa!important;font-weight:700!important;
    border:1px solid rgba(139,92,246,.35)!important;
    border-left:3px solid #a78bfa!important;
}}
{_SB} .st-key-{active_key} .stButton > button::before {{
    background-image:{_svg_uri(active, active=True)}!important;
}}
{_SB} .st-key-{active_key} .stButton > button p {{
    color:#fafafa!important;font-weight:700!important;
}}
{"".join(icon_rules)}
{collapsed_label}
{_SB} .st-key-nav_logout {{
    margin-top:auto!important;padding-top:8px!important;flex-shrink:0!important;
}}
{_SB} .st-key-nav_logout .stButton {{
    margin:4px 0 0!important;padding:0!important;
}}
{_SB} .st-key-nav_logout .stButton > button {{
    min-height:40px!important;height:40px!important;width:100%!important;
    font-size:12px!important;font-weight:600!important;border-radius:8px!important;
    border:1px solid rgba(255,255,255,.08)!important;
    background:#111113!important;color:#71717a!important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover {{
    background:rgba(127,29,29,.18)!important;color:#fca5a5!important;
    border-color:rgba(248,113,113,.22)!important;
}}
"""


def _resolve_active(active_page: str | None) -> str:
    active = (active_page or st.session_state.get("page") or "home").strip()
    return LEGACY_PAGE_ALIASES.get(active, active)


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    collapsed = bool(st.session_state.get("sb_collapsed"))
    inject_css(sidebar_master_css(active, collapsed=collapsed))

    with st.sidebar:
        brand_html = ""
        if WORDMARK.exists():
            import base64
            b64 = base64.b64encode(WORDMARK.read_bytes()).decode("utf-8")
            brand_html = (
                f'<div class="sb-brand"><img src="data:image/png;base64,{b64}" '
                f'alt="{html.escape(APP_NAME)}"></div>'
            )
        else:
            letter = html.escape(APP_NAME[:1].upper())
            if collapsed:
                brand_html = f'<div class="sb-brand"><span class="sb-brand-name">{letter}</span></div>'
            else:
                brand_html = f'<div class="sb-brand"><span class="sb-brand-name">{html.escape(APP_NAME)}</span></div>'

        st.markdown(brand_html, unsafe_allow_html=True)

        toggle_lbl = "›" if collapsed else "‹"
        if st.button(toggle_lbl, key="sb_toggle", help="Sidebar ein-/ausklappen"):
            st.session_state.sb_collapsed = not collapsed
            st.rerun()

        for label, page in SIDEBAR_NAV_ITEMS:
            if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
                st.session_state.page = page
                st.rerun()

        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
