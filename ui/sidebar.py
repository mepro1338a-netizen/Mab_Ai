"""MaByte sidebar — compact flat nav, ~230px, no sections."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from config import APP_NAME
from ui.sidebar_nav import LEGACY_PAGE_ALIASES, SIDEBAR_NAV_ITEMS
from ui.styles import inject_css

ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
_SB = 'section[data-testid="stSidebar"]'
_SB_W = "14.5rem"  # ~232px

_ICON: dict[str, str] = {
    "home": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21V12h6v9"/></svg>',
    "chat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M21 11.5a8.5 8.5 0 0 1-13.6 0A8.38 8.38 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5z"/></svg>',
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


def sidebar_master_css(active_page: str = "home") -> str:
    active = active_page or "home"
    from urllib.parse import quote

    icon_rules = []
    for _, page in SIDEBAR_NAV_ITEMS:
        key = f"nav_{page}"
        color = "%23e9d5ff" if page == active else "%2394a3b8"
        svg = (_ICON.get(page) or _ICON["home"]).format(c=color)
        uri = f'url("data:image/svg+xml,{quote(svg)}")'
        icon_rules.append(
            f'{_SB} .st-key-{key} .stButton > button::before {{'
            f'content:"";position:absolute;left:10px;top:50%;transform:translateY(-50%);'
            f'width:16px;height:16px;background-image:{uri};background-size:16px;opacity:.95;}}'
        )
    active_key = f"nav_{active}"
    active_icon = (_ICON.get(active) or _ICON["home"]).format(c="%23fafafa")
    active_icon_uri = f'url("data:image/svg+xml,{quote(active_icon)}")'

    return f"""
{_SB} {{
    min-width:{_SB_W}!important;max-width:{_SB_W}!important;width:{_SB_W}!important;
    background:#09090b!important;border-right:1px solid rgba(255,255,255,.08)!important;
}}
@media (min-width: 769px) {{
    {_SB} {{
        overflow-y:hidden!important;
    }}
    {_SB} > div,
    {_SB} [data-testid="stSidebarContent"],
    {_SB} [data-testid="stSidebarUserContent"] {{
        overflow-y:hidden!important;
        max-height:100vh!important;
    }}
}}
{_SB} > div {{
    padding:0 8px 8px 8px!important;
    overflow-x:hidden!important;
}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
    padding:0!important;margin:0!important;background:#09090b!important;
}}
{_SB} [data-testid="stSidebarNav"] {{ display:none!important; }}
{_SB} [data-testid="stVerticalBlock"] {{
    gap:0!important;padding:0!important;margin:0!important;
}}
{_SB} [data-testid="stVerticalBlock"] > div {{
    padding:0!important;margin:0!important;
}}
{_SB} [data-testid="stVerticalBlockBorderWrapper"] {{
    padding:0!important;margin:0!important;border:none!important;background:transparent!important;
}}
{_SB} [data-testid="stElementContainer"] {{
    margin:0!important;padding:0!important;
}}
.mb-brand {{
    padding:10px 4px 8px;margin:0 0 4px 0;
    border-bottom:1px solid rgba(255,255,255,.06);
}}
.mb-brand img {{
    max-height:26px;width:100%;object-fit:contain;object-position:left center;display:block;
}}
.mb-brand-name {{
    margin:0;color:#fafafa!important;font-size:15px;font-weight:800;line-height:1.2;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton {{
    margin:0!important;padding:0!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button {{
    width:100%!important;min-height:34px!important;height:34px!important;
    padding:0 8px 0 36px!important;margin:0!important;border-radius:8px!important;
    border:1px solid transparent!important;background:transparent!important;
    color:#94a3b8!important;font-size:12px!important;font-weight:500!important;
    line-height:1!important;text-align:left!important;position:relative!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
    box-shadow:none!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button p {{
    color:inherit!important;font-size:12px!important;font-weight:inherit!important;
    margin:0!important;line-height:1!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:hover {{
    background:#18181b!important;color:#f4f4f5!important;
}}
{_SB} .st-key-{active_key} .stButton > button {{
    background:linear-gradient(90deg,rgba(139,92,246,.28),rgba(139,92,246,.12))!important;
    color:#fafafa!important;font-weight:700!important;
    border-color:rgba(167,139,250,.55)!important;
    box-shadow:inset 0 0 0 1px rgba(167,139,250,.15)!important;
}}
{_SB} .st-key-{active_key} .stButton > button::before {{
    background-image:{active_icon_uri}!important;opacity:1!important;
}}
{_SB} .st-key-{active_key} .stButton > button::after {{
    content:"";position:absolute;left:0;top:5px;bottom:5px;width:3px;border-radius:0 3px 3px 0;
    background:linear-gradient(180deg,#e9d5ff,#8b5cf6);
    box-shadow:0 0 8px rgba(139,92,246,.6);
}}
{_SB} .st-key-{active_key} .stButton > button p {{
    color:#fafafa!important;font-weight:700!important;
}}
{"".join(icon_rules)}
.mb-footer {{
    margin:6px 0 0;padding:6px 0 0;border-top:1px solid rgba(255,255,255,.06);
}}
.mb-user {{
    padding:6px 8px;border-radius:8px;background:#141416;
    border:1px solid rgba(255,255,255,.06);
}}
.mb-user-name {{
    color:#f4f4f5!important;font-size:11px;font-weight:600;line-height:1.25;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}}
.mb-user-sub {{
    color:#71717a!important;font-size:9px;margin-top:1px;line-height:1.2;
}}
{_SB} .st-key-nav_logout .stButton {{
    margin:4px 0 0!important;padding:0!important;
}}
{_SB} .st-key-nav_logout .stButton > button {{
    min-height:32px!important;height:32px!important;
    font-size:11px!important;border-radius:8px!important;
    border:1px solid rgba(255,255,255,.08)!important;
    background:transparent!important;color:#71717a!important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover {{
    background:rgba(127,29,29,.2)!important;color:#fca5a5!important;
    border-color:rgba(248,113,113,.25)!important;
}}
"""


def inject_sidebar_styles(active_page: str = "home") -> None:
    inject_css(sidebar_master_css(active_page))


def _resolve_active(active_page: str | None) -> str:
    active = (active_page or st.session_state.get("page") or "home").strip()
    return LEGACY_PAGE_ALIASES.get(active, active)


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_sidebar_styles(active)

    with st.sidebar:
        if WORDMARK.exists():
            import base64
            b64 = base64.b64encode(WORDMARK.read_bytes()).decode("utf-8")
            st.markdown(
                f'<div class="mb-brand"><img src="data:image/png;base64,{b64}" '
                f'alt="{html.escape(APP_NAME)}"></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="mb-brand"><p class="mb-brand-name">{html.escape(APP_NAME)}</p></div>',
                unsafe_allow_html=True,
            )

        for label, page in SIDEBAR_NAV_ITEMS:
            if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
                st.session_state.page = page
                st.rerun()

        user = str(st.session_state.get("user", "User"))
        plan = str(st.session_state.get("plan", "free"))
        tokens = int(st.session_state.get("tokens", 0) or 0)
        token_txt = f"{tokens:,}".replace(",", ".")
        st.markdown(
            f'<div class="mb-footer"><div class="mb-user">'
            f'<div class="mb-user-name">{html.escape(user)}</div>'
            f'<div class="mb-user-sub">{html.escape(plan.upper())} · {token_txt} Tokens</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
