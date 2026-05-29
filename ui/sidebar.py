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
    """Futuristic MaByte sidebar — glass, neon accents, command-deck feel."""
    return """
section[data-testid="stSidebar"] {
    min-width: 15rem !important;
    width: 15rem !important;
    background:
        radial-gradient(120% 80% at 0% 0%, rgba(168,85,247,.14) 0%, transparent 55%),
        radial-gradient(90% 60% at 100% 100%, rgba(34,197,94,.08) 0%, transparent 50%),
        linear-gradient(180deg, #0a0a12 0%, #0f1018 45%, #12121c 100%) !important;
    border-right: 1px solid rgba(168,85,247,.22) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,.45), inset -1px 0 0 rgba(255,255,255,.04) !important;
}
section[data-testid="stSidebar"]::before {
    content: "";
    position: fixed;
    left: 0;
    top: 0;
    width: 15rem;
    height: 100%;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(255,255,255,.012) 2px,
        rgba(255,255,255,.012) 4px
    );
    z-index: 0;
}
section[data-testid="stSidebar"] > div {
    padding: 16px 11px 20px 11px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    position: relative;
    z-index: 1;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}

.sidebar-logo-wrap {
    padding: 4px 8px 18px 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(168,85,247,.2);
    position: relative;
}
.sidebar-logo-wrap::after {
    content: "";
    position: absolute;
    left: 8px;
    right: 8px;
    bottom: -1px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,231,163,.45), rgba(168,85,247,.6), transparent);
}
.sidebar-logo-wrap img {
    width: 100%;
    max-height: 46px;
    object-fit: contain;
    object-position: left center;
    border-radius: 0;
    filter: drop-shadow(0 0 12px rgba(168,85,247,.35)) brightness(1.08);
}

.mb-nav-section {
    margin-bottom: 6px;
    padding-bottom: 4px;
}
.mb-nav-section:last-of-type {
    margin-bottom: 4px;
}

.mb-section-label {
    margin: 14px 0 4px 8px;
    color: #52525b !important;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .16em;
    text-transform: uppercase;
    line-height: 1.2;
}
.mb-nav-section:first-of-type .mb-section-label {
    margin-top: 4px;
}

.mb-nav-item {
    margin: 0 !important;
    padding: 0 !important;
}

/* Inactive nav — flat, no white pill */
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) .stButton > button,
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button {
    width: 100% !important;
    min-height: 38px !important;
    height: 38px !important;
    padding: 0 10px 0 38px !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    background: rgba(15,23,42,.35) !important;
    background-color: rgba(15,23,42,.35) !important;
    background-image: none !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    text-align: left !important;
    box-shadow: none !important;
    position: relative !important;
    transition: border-color .15s ease, background .15s ease, color .15s ease, box-shadow .15s ease !important;
}
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button p {
    color: #a1a1aa !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) .stButton > button:hover,
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button:hover {
    background: rgba(30,27,75,.55) !important;
    background-color: rgba(30,27,75,.55) !important;
    border-color: rgba(168,85,247,.28) !important;
    color: #f8fafc !important;
    box-shadow: 0 0 18px rgba(168,85,247,.12) !important;
}
section[data-testid="stSidebar"] .mb-nav-item:not(.mb-nav-active) button:hover p {
    color: #fafafa !important;
}

/* Active nav — subtle zinc + accent bar */
section[data-testid="stSidebar"] .mb-nav-active .stButton > button,
section[data-testid="stSidebar"] .mb-nav-active button {
    width: 100% !important;
    min-height: 36px !important;
    height: 36px !important;
    padding: 0 10px 0 36px !important;
    border-radius: 8px !important;
    border: none !important;
    background: #27272a !important;
    background-color: #27272a !important;
    background-image: none !important;
    color: #fafafa !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-align: left !important;
    box-shadow: none !important;
    position: relative !important;
}
section[data-testid="stSidebar"] .mb-nav-active button p {
    color: #fafafa !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .mb-nav-active .stButton > button::before,
section[data-testid="stSidebar"] .mb-nav-active button::before {
    content: "";
    position: absolute;
    left: 0;
    top: 5px;
    bottom: 5px;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: linear-gradient(180deg, #ffe7a3, #a855f7);
    box-shadow: 0 0 10px rgba(168,85,247,.8);
}

/* Nav icon — minimal */
section[data-testid="stSidebar"] .mb-nav-item .stButton > button::after,
section[data-testid="stSidebar"] .mb-nav-item button::after {
    content: "";
    position: absolute;
    left: 8px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    border-radius: 6px;
    background-color: transparent;
    border: none;
    background-image: var(--mb-nav-icon);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 14px 14px;
    opacity: .85;
    pointer-events: none;
}
section[data-testid="stSidebar"] .mb-nav-active button::after {
    opacity: 1;
}

.mb-nav-item [data-testid="column"] {
    display: none !important;
}

.sidebar-user-card {
    margin-top: 16px;
    padding: 14px 14px;
    border-radius: 14px;
    background: linear-gradient(145deg, rgba(20,18,40,.9), rgba(10,12,22,.95));
    border: 1px solid rgba(168,85,247,.28);
    box-shadow: 0 8px 28px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.05);
}
.sidebar-user-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.sidebar-user-name {
    font-size: 13px;
    font-weight: 600;
    color: #fafafa !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.sidebar-user-plan {
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(168,85,247,.2);
    border: 1px solid rgba(168,85,247,.35);
    color: #e9d5ff !important;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.sidebar-user-tokens {
    color: #ffe7a3 !important;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-top: 8px;
    line-height: 1;
    text-shadow: 0 0 24px rgba(255,231,163,.25);
}
.sidebar-user-caption {
    color: #71717a !important;
    font-size: 10px;
    margin-top: 2px;
}

section[data-testid="stSidebar"] .sidebar-logout-wrap .stButton > button,
section[data-testid="stSidebar"] .sidebar-logout-wrap button {
    min-height: 36px !important;
    height: 36px !important;
    margin-top: 12px !important;
    border-radius: 10px !important;
    background: rgba(15,23,42,.5) !important;
    background-color: rgba(15,23,42,.5) !important;
    border: 1px solid rgba(100,116,139,.35) !important;
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .sidebar-logout-wrap button:hover {
    background: rgba(127,29,29,.35) !important;
    border-color: rgba(248,113,113,.4) !important;
    color: #fecaca !important;
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

    inject_sidebar_styles()
