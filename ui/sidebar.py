"""
MaByte sidebar — single render_sidebar(active_page) for ALL pages (via ui.py only).

Do not use st.sidebar in page modules.
"""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from ui.button_system import inject_master_buttons
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
    """Single sidebar stylesheet — injected last so every page looks identical."""
    return """
/* MaByte Sidebar — do not duplicate in page CSS */
section[data-testid="stSidebar"] {
    min-width: 14rem !important;
    width: 14rem !important;
    background:
        radial-gradient(ellipse 120% 80% at 0% 0%, rgba(124,58,237,.22), transparent 50%),
        radial-gradient(ellipse 80% 60% at 100% 100%, rgba(37,99,235,.12), transparent 45%),
        linear-gradient(185deg, #0c0614 0%, #1a0a28 42%, #08040f 100%) !important;
    border-right: 1px solid rgba(255,231,163,.08) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,.25) !important;
}
section[data-testid="stSidebar"] > div {
    padding: 10px 10px 18px 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}
.sidebar-logo-wrap {
    padding: 4px 0 18px 0;
}
.sidebar-logo-wrap img {
    width: 100%;
    border-radius: 22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.22);
}
.mb-section-label {
    margin: 16px 0 6px 4px;
    color: rgba(192,132,252,.85) !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .22em;
    text-transform: uppercase;
}
.mb-section-label:first-of-type {
    margin-top: 6px;
}
.mb-nav-section {
    margin-bottom: 14px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(168,85,247,.08);
}
.mb-nav-section:last-of-type {
    border-bottom: none;
}
.mb-nav-item {
    margin: 0 0 8px 0 !important;
    padding: 0 !important;
}
.mb-nav-item button {
    border-radius: 16px !important;
    background: rgba(10,12,24,.32) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    box-shadow: none !important;
    transition: transform .14s ease, border-color .14s ease, box-shadow .14s ease, background .14s ease;
}
.mb-nav-item button:hover {
    transform: translateY(-1px);
    border-color: rgba(168,85,247,.18) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,.24), 0 0 24px rgba(124,58,237,.10) !important;
    background: rgba(10,12,24,.40) !important;
}
.mb-nav-active button {
    background: linear-gradient(135deg, rgba(124,58,237,.34), rgba(59,130,246,.18)) !important;
    border-color: rgba(168,85,247,.35) !important;
}
.mb-nav-item [data-testid="column"] {
    display: none !important;
}
.mb-nav-item [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
.mb-nav-item .stButton > button::before,
.mb-nav-item button::before,
.mb-nav-item [data-testid="stBaseButton-secondary"]::before,
.mb-nav-item [data-testid="stBaseButton-primary"]::before {
    content: "";
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 30px;
    height: 30px;
    border-radius: 11px;
    background:
        radial-gradient(circle at 30% 20%, rgba(255,231,163,.18), transparent 45%),
        linear-gradient(135deg, rgba(49,18,62,.95), rgba(20,9,32,.98));
    border: 1px solid rgba(255,231,163,.14);
    background-image: var(--mb-nav-icon);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 20px 20px;
    box-shadow: 0 6px 14px rgba(0,0,0,.16);
}
.mb-nav-active button::before,
.mb-nav-active [data-testid="stBaseButton-secondary"]::before,
.mb-nav-active [data-testid="stBaseButton-primary"]::before {
    border-color: rgba(255,231,163,.42);
    box-shadow: 0 0 16px rgba(168,85,247,.28);
}
.sidebar-user-card {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.2), transparent 40%),
        linear-gradient(165deg, rgba(22,10,38,.98), rgba(8,5,14,.99));
    border: 1px solid rgba(255,231,163,.1);
    border-radius: 22px;
    padding: 16px 18px;
    margin-top: 14px;
    margin-bottom: 8px;
    box-shadow: 0 12px 40px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.04);
}
.sidebar-user-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.sidebar-user-name {
    font-size: 18px;
    font-weight: 1000;
    color: #ffffff !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.sidebar-user-plan {
    display: inline-flex;
    padding: 6px 11px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #ffffff !important;
    font-size: 11px;
    font-weight: 1000;
    white-space: nowrap;
}
.sidebar-user-tokens {
    color: #ffe7a3 !important;
    font-size: 30px;
    font-weight: 1000;
    line-height: 1;
    margin-top: 14px;
}
.sidebar-user-caption {
    color: #94a3b8 !important;
    font-size: 13px;
    margin-top: 6px;
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
    inject_master_buttons()


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
            _nav_section(section_title, items, active)
        if _is_admin_user():
            _nav_section("System", [("Admin Panel", "admin")], active)

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
