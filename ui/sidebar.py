"""
MaByte sidebar — single render_sidebar() for ALL pages (via ui.py).

Import: from ui.sidebar import render_sidebar
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
    "music": "music",
    "coding": "code",
    "dashboard": "dashboard",
    "premium": "premium",
    "redeem": "redeem",
    "support": "tools",
    "admin": "settings-sliders",
}


def sidebar_master_css() -> str:
    """Overrides Streamlit default white sidebar buttons on every page."""
    return """
/* MaByte Sidebar Master — identical on all routes */
section[data-testid="stSidebar"] {
    min-width: 17.5rem !important;
    width: 17.5rem !important;
}
section[data-testid="stSidebar"] > div {
    padding: 12px 12px 20px 12px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 8px !important;
}
section[data-testid="stSidebar"] .stButton {
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    width: 100% !important;
    min-height: 50px !important;
    max-height: 50px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,231,163,.14) !important;
    background: linear-gradient(135deg, rgba(32,9,48,.92), rgba(12,6,22,.98)) !important;
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
    font-size: 14px !important;
    font-family: inherit !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.03), 0 8px 20px rgba(0,0,0,.14) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    color: #ffffff !important;
    border-color: rgba(255,231,163,.32) !important;
    background: linear-gradient(135deg, rgba(91,33,182,.75), rgba(22,8,36,.98)) !important;
    box-shadow: 0 0 22px rgba(168,85,247,.22) !important;
    transform: translateY(-1px);
}
section[data-testid="stSidebar"] .stButton > button:disabled {
    opacity: 0.45 !important;
    transform: none !important;
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


def _nav_item(label: str, page: str) -> None:
    src = _icon_src(page)
    is_active = st.session_state.get("page") == page
    active_class = "mb-nav-active" if is_active else ""
    icon_var = f"url({src})" if src else "none"

    st.markdown(
        f'<div class="mb-nav-item {active_class}" style="--mb-nav-icon:{icon_var};">',
        unsafe_allow_html=True,
    )
    if st.button(label, key=f"nav_{page}", width="stretch"):
        st.session_state.page = page
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _nav_section(title: str, items: list[tuple[str, str]]) -> None:
    st.markdown('<div class="mb-nav-section">', unsafe_allow_html=True)
    _section_label(title)
    for label, page in items:
        _nav_item(label, page)
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> None:
    """Central sidebar — called once from ui.py for every authenticated page."""
    inject_sidebar_styles()

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
            st.markdown("## MaByte")

        for section_title, items in SIDEBAR_SECTIONS:
            _nav_section(section_title, items)
        if _is_admin_user():
            _nav_section("System", [("Admin Panel", "admin")])

        user = html.escape(str(st.session_state.get("user", "User")))
        plan = html.escape(str(st.session_state.get("plan", "free")))
        fb_plan = html.escape(str(st.session_state.get("football_plan", "none")))
        tokens = int(st.session_state.get("tokens", 0) or 0)
        fb_line = ""
        if fb_plan and fb_plan != "none":
            fb_line = f'<div class="sidebar-user-caption">Football: {fb_plan}</div>'

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
        if st.button("Abmelden", key="nav_logout", width="stretch"):
            from services.session_auth import logout_session
            logout_session()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
