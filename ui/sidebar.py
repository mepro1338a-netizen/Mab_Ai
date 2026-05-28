"""
MaByte sidebar — single render_sidebar(active_page) for ALL pages (via ui.py only).

Do not use st.sidebar in page modules.
"""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from ui.sidebar_nav import SIDEBAR_SECTIONS
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


def sidebar_master_css() -> str:
    """Premium SaaS sidebar — single source of truth."""
    return """
section[data-testid="stSidebar"] {
    min-width: 15.5rem !important;
    width: 15.5rem !important;
    background: #18181b !important;
    background-color: #18181b !important;
    border-right: 1px solid #3f3f46 !important;
    box-shadow: 1px 0 0 rgba(0, 0, 0, .4) !important;
}
section[data-testid="stSidebar"] > div {
    padding: 12px 10px 20px 10px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 4px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 2px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}

.sidebar-logo-wrap {
    padding: 4px 4px 14px 4px;
    margin-bottom: 4px;
    border-bottom: 1px solid rgba(255, 255, 255, .06);
}
.sidebar-logo-wrap img {
    width: 100%;
    max-height: 52px;
    object-fit: contain;
    border-radius: 12px;
}

.mb-nav-section {
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, .05);
}
.mb-nav-section:last-of-type {
    border-bottom: none;
    margin-bottom: 6px;
}

.mb-section-label {
    margin: 12px 0 6px 10px;
    color: #71717a !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mb-nav-section:first-of-type .mb-section-label {
    margin-top: 8px;
}

.mb-nav-item {
    margin: 0 0 2px 0 !important;
    padding: 0 !important;
}

/* Base nav button — inactive */
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) .stButton > button,
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button[data-testid="stBaseButton-secondary"] {
    width: 100% !important;
    min-height: 40px !important;
    padding: 0 12px 0 44px !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    background-color: transparent !important;
    color: rgba(148, 163, 184, .95) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-align: left !important;
    box-shadow: none !important;
    position: relative !important;
    transition: background .12s ease, color .12s ease, border-color .12s ease !important;
}
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button p {
    color: rgba(148, 163, 184, .95) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) .stButton > button:hover,
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button:hover {
    background: rgba(255, 255, 255, .04) !important;
    color: #e2e8f0 !important;
    border-color: rgba(255, 255, 255, .06) !important;
}
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) .stButton > button:hover p {
    color: #e2e8f0 !important;
}

/* Active nav — single clear state */
section[data-testid="stSidebar"] .mb-nav-active .stButton > button,
section[data-testid="stSidebar"] .mb-nav-active button[data-testid="stBaseButton-secondary"] {
    width: 100% !important;
    min-height: 40px !important;
    padding: 0 12px 0 44px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(168, 85, 247, .28) !important;
    background: rgba(124, 58, 237, .14) !important;
    background-color: rgba(124, 58, 237, .14) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    text-align: left !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05) !important;
    position: relative !important;
}
section[data-testid="stSidebar"] .mb-nav-active button p {
    color: #fff !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .mb-nav-active .stButton > button::before,
section[data-testid="stSidebar"] .mb-nav-active button::before {
    content: "";
    position: absolute;
    left: 0;
    top: 8px;
    bottom: 8px;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: linear-gradient(180deg, #c084fc, #7c3aed);
    box-shadow: 0 0 12px rgba(168, 85, 247, .5);
}

/* Nav icon */
section[data-testid="stSidebar"] .mb-nav-item .stButton > button::after,
section[data-testid="stSidebar"] .mb-nav-item button::after {
    content: "";
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background-color: rgba(255, 255, 255, .04);
    border: 1px solid rgba(255, 255, 255, .08);
    background-image: var(--mb-nav-icon);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 16px 16px;
    pointer-events: none;
}
section[data-testid="stSidebar"] .mb-nav-active .stButton > button::after,
section[data-testid="stSidebar"] .mb-nav-active button::after {
    border-color: rgba(168, 85, 247, .35);
    background-color: rgba(124, 58, 237, .2);
    box-shadow: 0 0 14px rgba(124, 58, 237, .2);
}

.mb-nav-item [data-testid="column"] {
    display: none !important;
}

.sidebar-user-card {
    margin-top: 12px;
    padding: 14px 14px;
    border-radius: 14px;
    background: rgba(255, 255, 255, .03);
    border: 1px solid rgba(255, 255, 255, .07);
}
.sidebar-user-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.sidebar-user-name {
    font-size: 14px;
    font-weight: 700;
    color: #f8fafc !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.sidebar-user-plan {
    padding: 4px 8px;
    border-radius: 6px;
    background: rgba(124, 58, 237, .25);
    border: 1px solid rgba(168, 85, 247, .3);
    color: #e9d5ff !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.sidebar-user-tokens {
    color: #f8fafc !important;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-top: 10px;
    line-height: 1;
}
.sidebar-user-caption {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 4px;
}

section[data-testid="stSidebar"] .sidebar-logout-wrap .stButton > button,
section[data-testid="stSidebar"] .sidebar-logout-wrap button {
    min-height: 38px !important;
    margin-top: 8px !important;
    border-radius: 10px !important;
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, .08) !important;
    color: rgba(148, 163, 184, .9) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .sidebar-logout-wrap button:hover {
    background: rgba(255, 255, 255, .04) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .sidebar-logout-wrap button p {
    color: inherit !important;
    font-size: 12px !important;
}

@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        min-width: 100% !important;
        width: 100% !important;
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
    return f"data:image/png;base64,{_img_base64(path)}"


def _is_admin_user() -> bool:
    from services.session_auth import server_is_admin
    return server_is_admin()


def _section_label(label: str) -> None:
    st.markdown(
        f'<div class="mb-section-label">{html.escape(label)}</div>',
        unsafe_allow_html=True,
    )


def _nav_item(label: str, page: str, active_page: str) -> None:
    src = _icon_src(page)
    is_active = active_page == page
    active_class = "mb-nav-active" if is_active else ""
    icon_var = f"url({src})" if src else "none"

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


def render_sidebar(active_page: str | None = None) -> None:
    """
    Central sidebar — only entry point. Call from ui.py with current page key.
    Example: render_sidebar(st.session_state.get("page", "home"))
    """
    active = (active_page or st.session_state.get("page") or "home").strip()
    if active in ("reels", "video"):
        active = "creator"

    with st.sidebar:
        if WORDMARK.exists():
            wordmark_src = _img_base64(WORDMARK)
            st.markdown(
                f"""
<div class="sidebar-logo-wrap">
    <img src="data:image/png;base64,{wordmark_src}" alt="MaByte">
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("### MaByte")

        for section_title, items in SIDEBAR_SECTIONS:
            _nav_section(section_title, items, active)
        if _is_admin_user():
            _nav_section("System", [("Admin Panel", "admin")], active)

        user = html.escape(str(st.session_state.get("user", "User")))
        plan = html.escape(str(st.session_state.get("plan", "free")))
        fb_plan = html.escape(str(st.session_state.get("football_plan", "none")))
        tokens = int(st.session_state.get("tokens", 0) or 0)
        fb_line = ""
        if fb_plan and fb_plan not in ("none", "", "free"):
            fb_line = f'<div class="sidebar-user-caption">Football · {fb_plan}</div>'

        st.markdown(
            f"""
<div class="sidebar-user-card">
    <div class="sidebar-user-row">
        <div class="sidebar-user-name">{user}</div>
        <div class="sidebar-user-plan">{plan.upper()}</div>
    </div>
    <div class="sidebar-user-tokens">{tokens:,}</div>
    <div class="sidebar-user-caption">Tokens verfügbar</div>
    {fb_line}
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-logout-wrap">', unsafe_allow_html=True)
        if st.button("Abmelden", key="nav_logout", width="stretch", type="secondary"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
