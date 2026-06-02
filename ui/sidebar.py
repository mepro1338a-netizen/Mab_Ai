"""MaByte sidebar — flat nav, fixed width, no sections."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from ui.sidebar_nav import LEGACY_PAGE_ALIASES, SIDEBAR_NAV_ITEMS
from ui.styles import inject_css

ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
_SB = 'section[data-testid="stSidebar"]'
_SB_W = "17.5rem"

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

PLAN_BADGE = {
    "elite": "plan-elite", "pro": "plan-pro", "starter": "plan-starter",
    "football_elite": "plan-elite", "football_pro": "plan-pro", "football_starter": "plan-starter",
}


def sidebar_master_css(active_page: str = "home") -> str:
    active = active_page or "home"
    icon_rules = []
    for _, page in SIDEBAR_NAV_ITEMS:
        key = f"nav_{page}"
        color = "%23ddd6fe" if page == active else "%23a1a1aa"
        svg = (_ICON.get(page) or _ICON["home"]).format(c=color)
        from urllib.parse import quote
        uri = f'url("data:image/svg+xml,{quote(svg)}")'
        icon_rules.append(
            f'{_SB} .st-key-{key} .stButton > button::before {{'
            f'content:"";position:absolute;left:11px;top:50%;transform:translateY(-50%);'
            f'width:17px;height:17px;background-image:{uri};background-size:17px;opacity:.95;}}'
        )
    active_key = f"nav_{active}"
    return f"""
{_SB} {{
    min-width:{_SB_W}!important;max-width:{_SB_W}!important;width:{_SB_W}!important;
    background:#09090b!important;border-right:1px solid rgba(255,255,255,.09)!important;
}}
{_SB} > div {{padding:0 10px 14px 10px!important;overflow-x:hidden!important;}}
{_SB} [data-testid="stSidebarContent"],{_SB} [data-testid="stSidebarUserContent"] {{
    padding:0!important;background:#09090b!important;
}}
{_SB} [data-testid="stVerticalBlock"] {{gap:3px!important;padding:0!important;}}
.mb-brand {{padding:16px 6px 12px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:6px;}}
.mb-brand img {{max-height:34px;width:100%;object-fit:contain;object-position:left;}}
.mb-brand-name {{margin:0;color:#fafafa!important;font-size:16px;font-weight:800;}}
.mb-brand-tag {{margin:4px 0 0;color:#a1a1aa!important;font-size:10px;line-height:1.3;}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button {{
    width:100%!important;min-height:40px!important;height:40px!important;
    padding:0 10px 0 40px!important;margin:1px 0!important;border-radius:9px!important;
    border:1px solid transparent!important;background:transparent!important;
    color:#a1a1aa!important;font-size:12.5px!important;font-weight:500!important;
    text-align:left!important;position:relative!important;white-space:nowrap!important;
    overflow:hidden!important;text-overflow:ellipsis!important;box-shadow:none!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button p {{
    color:inherit!important;font-size:12.5px!important;margin:0!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:hover {{
    background:#18181b!important;color:#f4f4f5!important;border-color:rgba(255,255,255,.08)!important;
}}
{_SB} .st-key-{active_key} .stButton > button {{
    background:rgba(139,92,246,.14)!important;color:#f4f4f5!important;
    border-color:rgba(139,92,246,.35)!important;font-weight:600!important;
}}
{_SB} .st-key-{active_key} .stButton > button::after {{
    content:"";position:absolute;left:0;top:7px;bottom:7px;width:3px;border-radius:0 3px 3px 0;
    background:linear-gradient(180deg,#c4b5fd,#8b5cf6);
}}
{"".join(icon_rules)}
.mb-footer {{margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);}}
.mb-user {{padding:10px;border-radius:10px;background:#18181b;border:1px solid rgba(255,255,255,.08);}}
.mb-user-name {{color:#f4f4f5!important;font-size:13px;font-weight:600;}}
.mb-user-sub {{color:#a1a1aa!important;font-size:10px;margin-top:2px;}}
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
                f'<div class="mb-brand"><img src="data:image/png;base64,{b64}" alt="{html.escape(APP_NAME)}">'
                f'<p class="mb-brand-tag">{html.escape(APP_TAGLINE)}</p></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="mb-brand"><p class="mb-brand-name">{html.escape(APP_NAME)}</p>'
                f'<p class="mb-brand-tag">{html.escape(APP_TAGLINE)}</p></div>',
                unsafe_allow_html=True,
            )

        for label, page in SIDEBAR_NAV_ITEMS:
            if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
                st.session_state.page = page
                st.rerun()

        user = str(st.session_state.get("user", "User"))
        plan = str(st.session_state.get("plan", "free"))
        tokens = int(st.session_state.get("tokens", 0) or 0)
        st.markdown(
            f'<div class="mb-footer"><div class="mb-user">'
            f'<div class="mb-user-name">{html.escape(user)}</div>'
            f'<div class="mb-user-sub">{html.escape(plan.upper())} · {tokens:,} Tokens</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
