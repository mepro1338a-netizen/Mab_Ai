"""
MaByte sidebar — B2B SaaS navigation (single entry via ui.py).
"""
from __future__ import annotations

import html
from pathlib import Path

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
    "video": "video",
    "reels": "reels",
    "creator": "reels",
    "music": "music",
    "coding": "code",
    "dashboard": "dashboard",
    "premium": "premium",
    "redeem": "redeem",
    "support": "tools",
    "admin": "settings-sliders",
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


def sidebar_master_css() -> str:
    """Enterprise B2B sidebar — Linear/Vercel-inspiriert, ruhig & präzise."""
    return """
:root {
    --sb-width: 16.75rem;
    --sb-bg: #0b0b0f;
    --sb-surface: #131318;
    --sb-border: rgba(255,255,255,.08);
    --sb-text: #e4e4e7;
    --sb-muted: #71717a;
    --sb-accent: #8b5cf6;
    --sb-accent-soft: rgba(139,92,246,.14);
}

section[data-testid="stSidebar"] {
    min-width: var(--sb-width) !important;
    max-width: var(--sb-width) !important;
    width: var(--sb-width) !important;
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
    box-shadow: 1px 0 0 rgba(255,255,255,.03), 8px 0 40px rgba(0,0,0,.25) !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    height: 100% !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 100% !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] button[kind="header"] {
    color: var(--sb-muted) !important;
}

.sidebar-shell {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    padding: 0 0 12px 0;
}

.sidebar-brand {
    padding: 20px 16px 16px 16px;
    border-bottom: 1px solid var(--sb-border);
    margin-bottom: 4px;
}
.sidebar-brand img {
    width: 100%;
    max-height: 40px;
    object-fit: contain;
    object-position: left center;
}
.sidebar-brand-text {
    margin: 0;
    color: #fafafa !important;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.sidebar-brand-tag {
    margin: 4px 0 0 0;
    color: var(--sb-muted) !important;
    font-size: 11px;
    font-weight: 500;
    line-height: 1.35;
}

.sidebar-nav {
    flex: 1;
    padding: 8px 10px 12px 10px;
}

.mb-nav-section {
    margin-bottom: 2px;
}
.mb-nav-section + .mb-nav-section {
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid rgba(255,255,255,.04);
}

.mb-section-label {
    margin: 10px 8px 6px 10px;
    color: var(--sb-muted) !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
    line-height: 1;
}

.mb-nav-item {
    margin: 2px 0 !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] .mb-nav-item .stButton,
section[data-testid="stSidebar"] .mb-nav-item .stButton > button,
section[data-testid="stSidebar"] .mb-nav-item button {
    width: 100% !important;
    min-height: 40px !important;
    height: 40px !important;
    padding: 0 12px 0 44px !important;
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
}
section[data-testid="stSidebar"] .mb-nav-item button p,
section[data-testid="stSidebar"] .mb-nav-item button span {
    color: inherit !important;
    font-weight: inherit !important;
    font-size: 13px !important;
}

section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button:hover {
    background: var(--sb-surface) !important;
    background-color: var(--sb-surface) !important;
    border-color: var(--sb-border) !important;
    color: var(--sb-text) !important;
}

section[data-testid="stSidebar"] .mb-nav-active button {
    background: var(--sb-accent-soft) !important;
    background-color: var(--sb-accent-soft) !important;
    border-color: rgba(139,92,246,.35) !important;
    color: #f4f4f5 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .mb-nav-active button::before {
    content: "";
    position: absolute;
    left: 0;
    top: 8px;
    bottom: 8px;
    width: 3px;
    border-radius: 0 4px 4px 0;
    background: linear-gradient(180deg, #c4b5fd, var(--sb-accent));
}

section[data-testid="stSidebar"] .mb-nav-item button::after {
    content: "";
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 22px;
    height: 22px;
    border-radius: 7px;
    background-color: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.06);
    background-image: var(--mb-nav-icon);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 13px 13px;
    opacity: .9;
    pointer-events: none;
}
section[data-testid="stSidebar"] .mb-nav-active button::after {
    background-color: rgba(139,92,246,.2);
    border-color: rgba(139,92,246,.35);
    opacity: 1;
}

.sidebar-footer {
    margin-top: auto;
    padding: 12px 10px 4px 10px;
    border-top: 1px solid var(--sb-border);
    background: linear-gradient(180deg, transparent, rgba(0,0,0,.35));
}

.sidebar-user-card {
    padding: 14px 12px;
    border-radius: 12px;
    background: var(--sb-surface);
    border: 1px solid var(--sb-border);
}
.sidebar-user-top {
    display: flex;
    align-items: center;
    gap: 10px;
}
.sidebar-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4c1d95, #7c3aed);
    color: #fafafa !important;
    font-size: 14px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 1px solid rgba(255,255,255,.1);
}
.sidebar-user-meta {
    min-width: 0;
    flex: 1;
}
.sidebar-user-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--sb-text) !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
}
.sidebar-user-email {
    font-size: 10px;
    color: var(--sb-muted) !important;
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.sidebar-user-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
}
.sidebar-plan-badge {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .06em;
    text-transform: uppercase;
    border: 1px solid transparent;
}
.sidebar-plan-badge.plan-free {
    background: rgba(63,63,70,.5);
    color: #d4d4d8 !important;
    border-color: rgba(255,255,255,.08);
}
.sidebar-plan-badge.plan-starter {
    background: rgba(34,197,94,.12);
    color: #86efac !important;
    border-color: rgba(34,197,94,.25);
}
.sidebar-plan-badge.plan-pro {
    background: rgba(139,92,246,.15);
    color: #ddd6fe !important;
    border-color: rgba(139,92,246,.3);
}
.sidebar-plan-badge.plan-elite {
    background: rgba(255,231,163,.12);
    color: #fde68a !important;
    border-color: rgba(255,231,163,.28);
}
.sidebar-tokens-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid rgba(255,255,255,.06);
}
.sidebar-tokens-val {
    color: #fafafa !important;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1;
}
.sidebar-tokens-lbl {
    color: var(--sb-muted) !important;
    font-size: 10px;
    font-weight: 600;
}

section[data-testid="stSidebar"] .sidebar-logout-wrap .stButton > button,
section[data-testid="stSidebar"] .sidebar-logout-wrap button {
    min-height: 38px !important;
    height: 38px !important;
    margin-top: 10px !important;
    border-radius: 10px !important;
    background: transparent !important;
    border: 1px solid var(--sb-border) !important;
    color: var(--sb-muted) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .sidebar-logout-wrap button:hover {
    background: rgba(127,29,29,.2) !important;
    border-color: rgba(248,113,113,.35) !important;
    color: #fecaca !important;
}
section[data-testid="stSidebar"] .sidebar-logout-wrap button p {
    color: inherit !important;
}

@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        min-width: 100% !important;
        width: 100% !important;
        max-width: 100% !important;
    }
}
"""


def inject_sidebar_styles() -> None:
    inject_css(sidebar_master_css())


def _img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    import base64
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _icon_src(page: str) -> str:
    icon_name = ICON_MAP.get(page, page)
    path = ASSET_DIR / f"{icon_name}.png"
    if not path.exists():
        return ""
    return f"url(data:image/png;base64,{_img_base64(path)})"


def _is_admin_user() -> bool:
    from services.session_auth import server_is_admin
    return server_is_admin()


def _plan_badge_class(plan: str) -> str:
    key = (plan or "free").strip().lower()
    return PLAN_BADGE_CLASS.get(key, "plan-free")


def _user_initial(username: str) -> str:
    u = (username or "U").strip()
    return (u[0] or "U").upper()


def _render_brand() -> None:
    if WORDMARK.exists():
        src = _img_base64(WORDMARK)
        st.markdown(
            f"""
<div class="sidebar-brand">
    <img src="data:image/png;base64,{src}" alt="{html.escape(APP_NAME)}">
    <p class="sidebar-brand-tag">{html.escape(APP_TAGLINE)}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div class="sidebar-brand">
    <p class="sidebar-brand-text">{html.escape(APP_NAME)}</p>
    <p class="sidebar-brand-tag">{html.escape(APP_TAGLINE)}</p>
</div>
            """,
            unsafe_allow_html=True,
        )


def _section_label(label: str) -> None:
    st.markdown(
        f'<div class="mb-section-label">{html.escape(label)}</div>',
        unsafe_allow_html=True,
    )


def _nav_item(label: str, page: str, active_page: str) -> None:
    is_active = active_page == page
    active_class = "mb-nav-active" if is_active else ""
    icon_var = _icon_src(page) or "none"

    st.markdown(
        f'<div class="mb-nav-item {active_class}" style="--mb-nav-icon:{icon_var};">',
        unsafe_allow_html=True,
    )
    if st.button(label, key=f"nav_{page}", width="stretch", type="secondary"):
        st.session_state.page = page
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _nav_section(title: str, items: list[tuple[str, str]], active_page: str) -> None:
    st.markdown('<div class="mb-nav-section">', unsafe_allow_html=True)
    _section_label(title)
    for label, page in items:
        _nav_item(label, page, active_page)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_user_footer() -> None:
    user = str(st.session_state.get("user", "User"))
    plan = str(st.session_state.get("plan", "free"))
    fb_plan = str(st.session_state.get("football_plan", "none"))
    tokens = int(st.session_state.get("tokens", 0) or 0)
    plan_cls = _plan_badge_class(plan)
    plan_label = plan.replace("_", " ").upper() if plan else "FREE"

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
        <span class="sidebar-tokens-val">{f"{tokens:,}".replace(",", ".")}</span>
        <span class="sidebar-tokens-lbl">Tokens</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active_page: str | None = None) -> None:
    active = (active_page or st.session_state.get("page") or "home").strip()
    if active in LEGACY_PAGE_ALIASES:
        active = LEGACY_PAGE_ALIASES[active]
    if active in ("reels", "video"):
        active = "creator"

    with st.sidebar:
        st.markdown('<div class="sidebar-shell">', unsafe_allow_html=True)
        _render_brand()
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)

        for section_title, items in SIDEBAR_SECTIONS:
            _nav_section(section_title, items, active)

        if _is_admin_user():
            _nav_section("System", [("Admin Panel", "admin")], active)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        _render_user_footer()
        st.markdown('<div class="sidebar-logout-wrap">', unsafe_allow_html=True)
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
        st.markdown("</div></div></div>", unsafe_allow_html=True)

    inject_sidebar_styles()
