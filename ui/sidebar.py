"""
MaByte sidebar — B2B SaaS navigation (single entry via ui.py).
"""
from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from ui.sidebar_nav import LEGACY_PAGE_ALIASES, SIDEBAR_SECTIONS
from ui.styles import inject_css

ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"

ICON_MAP = {
    "home": "home",
    "chat": "chat",
    "projects": "projects",
    "automation_lab": "automations",
    "football": "football",
    "image": "image",
    "video": "reels",
    "music": "music",
    "coding": "code",
    "dashboard": "dashboard",
    "premium": "premium",
}

# Minimal stroke icons (always available — no PNG dependency)
_NAV_SVG: dict[str, str] = {
    "home": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21V12h6v9"/></svg>',
    "chat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M21 11.5a8.38 8.38 0 0 1-1.9 5.4 8.5 8.5 0 0 1-13.6 0A8.38 8.38 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5z"/><path d="M8 14h.01M12 14h.01M16 14h.01"/></svg>',
    "football": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><circle cx="12" cy="12" r="9"/><path d="M12 3c2 3 2 15 0 18M3 12h18M5 7.5h14M5 16.5h14"/></svg>',
    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="m21 17-5-5L8 20"/></svg>',
    "reels": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><rect x="2" y="4" width="15" height="16" rx="2"/><path d="M17 8.5 22 6v12l-5-2.5"/></svg>',
    "music": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
    "code": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/></svg>',
    "projects": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M3 7h7V3H3zm11 0h7V3h-7zM3 21h7v-4H3zm11 0h7v-4h-7z"/></svg>',
    "automations": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/><circle cx="12" cy="12" r="3"/></svg>',
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>',
    "premium": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7-6.3-4.6L5.7 21l2.3-7-6-4.6h7.6z"/></svg>',
    "redeem": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M20 12v8H4V12M2 7h20v5H2zM12 22V7M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7s1-5 4.5-5a2.5 2.5 0 0 1 0 5H12z"/></svg>',
    "tools": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
    "settings-sliders": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75"><path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M2 14h4M10 10h4M18 16h4"/></svg>',
}

PLAN_BADGE_CLASS = {
    "elite": "plan-elite",
    "pro": "plan-pro",
    "premium": "plan-pro",
    "starter": "plan-starter",
    "football_elite": "plan-elite",
    "football_pro": "plan-pro",
    "football_starter": "plan-starter",
}

_SB = 'section[data-testid="stSidebar"]'


def _all_nav_pages() -> list[str]:
    pages: list[str] = []
    for _, items in SIDEBAR_SECTIONS:
        for _, page in items:
            if page not in pages:
                pages.append(page)
    return pages


def _svg_data_uri(page: str, *, active: bool = False) -> str:
    icon_name = ICON_MAP.get(page, page)
    path = ASSET_DIR / f"{icon_name}.png"
    if path.exists():
        import base64
        b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"url(data:image/png;base64,{b64})"
    color = "%23ddd6fe" if active else "%23a1a1aa"
    tpl = _NAV_SVG.get(icon_name) or _NAV_SVG["tools"]
    svg = tpl.format(c=color)
    return f'url("data:image/svg+xml,{quote(svg)}")'


def _nav_key(page: str) -> str:
    return f"nav_{page}"


def _icon_css_rules() -> str:
    rules: list[str] = []
    for page in _all_nav_pages():
        key = _nav_key(page)
        icon = _svg_data_uri(page)
        rules.append(
            f"""
{_SB} .st-key-{key} .stButton > button::before {{
    content: "";
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 18px;
    background-image: {icon};
    background-repeat: no-repeat;
    background-position: center;
    background-size: 18px 18px;
    opacity: .92;
    pointer-events: none;
}}
"""
        )
    return "\n".join(rules)


def _active_nav_css(active_page: str) -> str:
    key = _nav_key(active_page)
    icon = _svg_data_uri(active_page, active=True)
    return f"""
{_SB} .st-key-{key} .stButton > button,
{_SB} .st-key-{key} button {{
    background: rgba(139,92,246,.16) !important;
    background-color: rgba(139,92,246,.16) !important;
    border-color: rgba(139,92,246,.38) !important;
    color: #f4f4f5 !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}}
{_SB} .st-key-{key} .stButton > button::after {{
    content: "";
    position: absolute;
    left: 0;
    top: 8px;
    bottom: 8px;
    width: 3px;
    border-radius: 0 4px 4px 0;
    background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
    pointer-events: none;
}}
{_SB} .st-key-{key} .stButton > button::before {{
    background-image: {icon} !important;
    opacity: 1 !important;
}}
{_SB} .st-key-{key} .stButton > button p {{
    color: #f4f4f5 !important;
    font-weight: 600 !important;
}}
{_SB} .st-key-{key} .stButton > button:focus,
{_SB} .st-key-{key} .stButton > button:active,
{_SB} .st-key-{key} .stButton > button:focus-visible,
{_SB} .st-key-{key} .stButton > button:hover {{
    background: rgba(139,92,246,.16) !important;
    background-color: rgba(139,92,246,.16) !important;
    border-color: rgba(139,92,246,.38) !important;
    color: #f4f4f5 !important;
}}
"""


def sidebar_master_css(active_page: str = "home") -> str:
    """Enterprise B2B sidebar — Streamlit-safe (st-key selectors, no fake HTML wrappers)."""
    active = active_page or "home"
    return f"""
:root {{
    --sb-width: 17rem;
    --sb-bg: #0b0b0f;
    --sb-surface: #16161c;
    --sb-border: rgba(255,255,255,.08);
    --sb-text: #e4e4e7;
    --sb-muted: #71717a;
    --sb-accent: #8b5cf6;
}}

{_SB} {{
    min-width: var(--sb-width) !important;
    max-width: var(--sb-width) !important;
    width: var(--sb-width) !important;
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
    box-shadow: 8px 0 32px rgba(0,0,0,.28) !important;
}}
{_SB} > div {{
    padding: 0 10px 16px 10px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"] {{
    padding: 0 !important;
    background: var(--sb-bg) !important;
}}
{_SB} [data-testid="stVerticalBlock"] {{
    gap: 2px !important;
    padding: 0 !important;
}}
{_SB} [data-testid="stVerticalBlockBorderWrapper"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}}

.mb-sidebar-brand {{
    padding: 18px 6px 14px 6px;
    margin-bottom: 6px;
    border-bottom: 1px solid var(--sb-border);
}}
.mb-sidebar-brand img {{
    width: 100%;
    max-height: 36px;
    object-fit: contain;
    object-position: left center;
    display: block;
}}
.mb-sidebar-brand-name {{
    margin: 0;
    color: #fafafa !important;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.03em;
}}
.mb-sidebar-brand-tag {{
    margin: 5px 0 0 0;
    color: var(--sb-muted) !important;
    font-size: 10px;
    font-weight: 500;
    line-height: 1.35;
}}

.mb-nav-section-gap {{
    height: 8px;
    border-top: 1px solid rgba(255,255,255,.04);
    margin: 8px 0 4px 0;
}}

.mb-section-label {{
    margin: 12px 4px 6px 6px;
    color: var(--sb-muted) !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    line-height: 1;
}}

/* All nav buttons (st-key-nav_*) */
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button,
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) button {{
    width: 100% !important;
    min-height: 40px !important;
    height: 40px !important;
    padding: 0 12px 0 42px !important;
    margin: 1px 0 !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    color: #a1a1aa !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    text-align: left !important;
    box-shadow: none !important;
    position: relative !important;
    transition: background .12s ease, border-color .12s ease, color .12s ease !important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:focus,
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:active,
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:focus-visible {{
    background: var(--sb-surface) !important;
    background-color: var(--sb-surface) !important;
    border-color: var(--sb-border) !important;
    color: var(--sb-text) !important;
    outline: none !important;
    box-shadow: none !important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button:hover {{
    background: var(--sb-surface) !important;
    background-color: var(--sb-surface) !important;
    border-color: var(--sb-border) !important;
    color: var(--sb-text) !important;
}}
{_SB} div[class*="st-key-nav_"]:not(.st-key-nav_logout) .stButton > button p {{
    color: inherit !important;
    font-weight: inherit !important;
    font-size: 13px !important;
    margin: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

{_icon_css_rules()}

{_active_nav_css(active)}

.mb-sidebar-footer {{
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid var(--sb-border);
}}

.sidebar-user-card {{
    padding: 12px;
    border-radius: 12px;
    background: var(--sb-surface);
    border: 1px solid var(--sb-border);
}}
.sidebar-user-top {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.sidebar-avatar {{
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: linear-gradient(135deg, #4c1d95, #7c3aed);
    color: #fafafa !important;
    font-size: 13px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 1px solid rgba(255,255,255,.1);
}}
.sidebar-user-meta {{ min-width: 0; flex: 1; }}
.sidebar-user-name {{
    font-size: 13px;
    font-weight: 600;
    color: var(--sb-text) !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.sidebar-user-email {{
    font-size: 10px;
    color: var(--sb-muted) !important;
    margin-top: 2px;
}}
.sidebar-user-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}}
.sidebar-plan-badge {{
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .06em;
    text-transform: uppercase;
    border: 1px solid transparent;
}}
.sidebar-plan-badge.plan-free {{
    background: rgba(63,63,70,.5);
    color: #d4d4d8 !important;
    border-color: rgba(255,255,255,.08);
}}
.sidebar-plan-badge.plan-starter {{
    background: rgba(34,197,94,.12);
    color: #86efac !important;
    border-color: rgba(34,197,94,.25);
}}
.sidebar-plan-badge.plan-pro {{
    background: rgba(139,92,246,.15);
    color: #ddd6fe !important;
    border-color: rgba(139,92,246,.3);
}}
.sidebar-plan-badge.plan-elite {{
    background: rgba(255,231,163,.12);
    color: #fde68a !important;
    border-color: rgba(255,231,163,.28);
}}
.sidebar-tokens-row {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,.06);
}}
.sidebar-tokens-val {{
    color: #fafafa !important;
    font-size: 18px;
    font-weight: 800;
}}
.sidebar-tokens-lbl {{
    color: var(--sb-muted) !important;
    font-size: 10px;
    font-weight: 600;
}}

{_SB} .st-key-nav_logout .stButton > button {{
    min-height: 36px !important;
    height: 36px !important;
    margin-top: 8px !important;
    border-radius: 10px !important;
    background: transparent !important;
    border: 1px solid var(--sb-border) !important;
    color: var(--sb-muted) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}}
{_SB} .st-key-nav_logout .stButton > button:hover {{
    background: rgba(127,29,29,.22) !important;
    border-color: rgba(248,113,113,.35) !important;
    color: #fecaca !important;
}}
{_SB} .st-key-nav_logout .stButton > button p {{
    color: inherit !important;
}}

@media (max-width: 768px) {{
    {_SB} {{
        min-width: 100% !important;
        width: 100% !important;
        max-width: 100% !important;
    }}
}}
"""


def inject_sidebar_styles(active_page: str = "home") -> None:
    inject_css(sidebar_master_css(active_page))


def _img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    import base64
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _is_admin_user() -> bool:
    from services.session_auth import server_is_admin
    return server_is_admin()


def _plan_badge_class(plan: str) -> str:
    key = (plan or "free").strip().lower()
    return PLAN_BADGE_CLASS.get(key, "plan-free")


def _user_initial(username: str) -> str:
    u = (username or "U").strip()
    return (u[0] or "U").upper()


def _resolve_active(active_page: str | None) -> str:
    active = (active_page or st.session_state.get("page") or "home").strip()
    if active in LEGACY_PAGE_ALIASES:
        active = LEGACY_PAGE_ALIASES[active]
    if active in ("reels", "video"):
        active = "creator"
    return active


def _render_brand() -> None:
    if WORDMARK.exists():
        src = _img_base64(WORDMARK)
        st.markdown(
            f"""
<div class="mb-sidebar-brand">
    <img src="data:image/png;base64,{src}" alt="{html.escape(APP_NAME)}">
    <p class="mb-sidebar-brand-tag">{html.escape(APP_TAGLINE)}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div class="mb-sidebar-brand">
    <p class="mb-sidebar-brand-name">{html.escape(APP_NAME)}</p>
    <p class="mb-sidebar-brand-tag">{html.escape(APP_TAGLINE)}</p>
</div>
            """,
            unsafe_allow_html=True,
        )


def _section_label(label: str) -> None:
    st.markdown(
        f'<p class="mb-section-label">{html.escape(label)}</p>',
        unsafe_allow_html=True,
    )


def _nav_button(label: str, page: str) -> None:
    if st.button(label, key=_nav_key(page), width="stretch", type="secondary"):
        st.session_state.page = page
        st.rerun()


def _nav_section(title: str, items: list[tuple[str, str]], *, first: bool = False) -> None:
    if not first:
        st.markdown('<div class="mb-nav-section-gap"></div>', unsafe_allow_html=True)
    _section_label(title)
    for nav_label, page in items:
        _nav_button(nav_label, page)


def _render_user_footer() -> None:
    user = str(st.session_state.get("user", "User"))
    plan = str(st.session_state.get("plan", "free"))
    fb_plan = str(st.session_state.get("football_plan", "none"))
    tokens = int(st.session_state.get("tokens", 0) or 0)
    plan_cls = _plan_badge_class(plan)
    plan_label = plan.replace("_", " ").upper() if plan else "FREE"
    token_txt = f"{tokens:,}".replace(",", ".")

    badges = [f'<span class="sidebar-plan-badge {plan_cls}">{html.escape(plan_label)}</span>']
    if fb_plan and fb_plan not in ("none", "", "free"):
        fb_cls = _plan_badge_class(fb_plan)
        fb_lbl = fb_plan.replace("football_", "").upper()
        badges.append(f'<span class="sidebar-plan-badge {fb_cls}">FB {html.escape(fb_lbl)}</span>')

    st.markdown(
        f"""
<div class="sidebar-user-card">
    <div class="sidebar-user-top">
        <div class="sidebar-avatar">{html.escape(_user_initial(user))}</div>
        <div class="sidebar-user-meta">
            <div class="sidebar-user-name">{html.escape(user)}</div>
            <div class="sidebar-user-email">Angemeldet</div>
        </div>
    </div>
    <div class="sidebar-user-badges">{"".join(badges)}</div>
    <div class="sidebar-tokens-row">
        <span class="sidebar-tokens-val">{token_txt}</span>
        <span class="sidebar-tokens-lbl">Tokens</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_sidebar_styles(active)

    with st.sidebar:
        _render_brand()

        for idx, (section_title, items) in enumerate(SIDEBAR_SECTIONS):
            _nav_section(section_title, items, first=idx == 0)

        st.markdown('<div class="mb-sidebar-footer">', unsafe_allow_html=True)
        _render_user_footer()
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
