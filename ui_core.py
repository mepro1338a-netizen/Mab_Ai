import base64
import html
from pathlib import Path

import streamlit as st


ASSET_DIR = Path("assets")

WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


def img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""

    return base64.b64encode(path.read_bytes()).decode("utf-8")


def icon_path(name: str) -> Path:
    return ASSET_DIR / f"{name}.png"


def load_css() -> None:
    slogan = img_base64(SLOGAN_HEADER)

    slogan_css = ""

    if slogan:
        slogan_css = f"""
.custom-topbar {{
    background-image: url("data:image/png;base64,{slogan}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
"""

    st.markdown(
        f"""
<style>
:root {{
    --mb-bg:#050816;
    --mb-bg-2:#081226;
    --mb-sidebar:#13051f;
    --mb-sidebar-2:#210833;
    --mb-card:rgba(12,18,38,.90);
    --mb-card-2:rgba(8,12,26,.98);
    --mb-line:rgba(255,255,255,.08);
    --mb-gold:#ffe7a3;
    --mb-gold-soft:#f8e7b0;
    --mb-purple:#a855f7;
    --mb-purple-soft:#c084fc;
    --mb-blue:#60a5fa;
    --mb-muted:#94a3b8;
}}

#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
button[title="View fullscreen"],
button[title="Fullscreen"],
[data-testid="StyledFullScreenButton"] {{
    display: none !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
    z-index: 998 !important;
}}

html,
body,
.stApp,
.main,
.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 24%),
        radial-gradient(circle at top right, rgba(96,165,250,.10), transparent 26%),
        radial-gradient(circle at bottom left, rgba(168,85,247,.07), transparent 34%),
        linear-gradient(180deg, #050816 0%, #081226 46%, #050711 100%) !important;
    background-attachment: fixed !important;
}}

.main .block-container {{
    max-width: 1480px !important;
    padding-top: 88px !important;
    padding-bottom: 42px !important;
}}

.custom-topbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 76px;
    z-index: 999999;
    background:
        linear-gradient(90deg, rgba(9,8,24,.96), rgba(25,8,42,.96));
    border-bottom: 1px solid rgba(255,255,255,.07);
    backdrop-filter: blur(18px);
}}

{slogan_css}

h1,h2,h3,h4,h5,h6 {{
    color: var(--mb-gold) !important;
    font-weight: 1000 !important;
    letter-spacing: -.035em;
}}

.stMarkdown,
.stCaption,
.stText,
label {{
    color: var(--mb-gold-soft) !important;
}}

small,
.stCaption {{
    color: var(--mb-muted) !important;
}}

section[data-testid="stSidebar"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.22), transparent 24%),
        radial-gradient(circle at bottom right, rgba(96,165,250,.10), transparent 32%),
        linear-gradient(180deg, #13051f 0%, #210833 46%, #0d0417 100%) !important;
    border-right: 1px solid rgba(255,255,255,.09);
    z-index: 999 !important;
}}

section[data-testid="stSidebar"] > div {{
    padding-left: 12px !important;
    padding-right: 12px !important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: .22rem !important;
}}

section[data-testid="stSidebar"] img {{
    border-radius: 18px;
}}

section[data-testid="stSidebar"] .stCaption {{
    margin-top: .9rem;
    margin-bottom: .2rem;
    color: rgba(255,231,163,.68) !important;
    font-size: .70rem !important;
    font-weight: 1000 !important;
    letter-spacing: .16em !important;
    text-transform: uppercase !important;
}}

button[data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}}

.mb-nav-wrap {{
    margin-bottom: 6px;
}}

.mb-nav-wrap [data-testid="column"] {{
    padding: 0 !important;
}}

.mb-nav-icon-shell {{
    width: 40px;
    height: 40px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(135deg, rgba(255,231,163,.10), rgba(168,85,247,.12));
    border: 1px solid rgba(255,231,163,.14);
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 8px 18px rgba(0,0,0,.14);
}}

.mb-nav-icon-shell img {{
    width: 23px !important;
    height: 23px !important;
    object-fit: contain !important;
    border-radius: 0 !important;
}}

.stButton > button {{
    width: 100% !important;
    min-height: 40px !important;
    border-radius: 15px !important;
    border: 1px solid rgba(255,231,163,.14) !important;
    background:
        linear-gradient(135deg, rgba(32,9,48,.92), rgba(12,6,22,.98)) !important;
    color: var(--mb-gold) !important;
    font-weight: 1000 !important;
    font-size: 14px !important;
    letter-spacing: .01em !important;
    text-align: left !important;
    padding-left: 14px !important;
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 10px 24px rgba(0,0,0,.16) !important;
    transition: all .18s ease !important;
}}

.stButton > button:hover {{
    transform: translateY(-1px) !important;
    color: #ffffff !important;
    border-color: rgba(255,231,163,.34) !important;
    background:
        linear-gradient(135deg, rgba(91,33,182,.72), rgba(22,8,36,.98)) !important;
    box-shadow:
        0 0 24px rgba(168,85,247,.22),
        0 0 12px rgba(255,231,163,.08) !important;
}}

.stButton > button:active {{
    transform: translateY(0) !important;
}}

.mb-active-nav .mb-nav-icon-shell {{
    background:
        linear-gradient(135deg, rgba(255,231,163,.24), rgba(168,85,247,.26));
    border-color: rgba(255,231,163,.45);
    box-shadow:
        0 0 22px rgba(168,85,247,.22),
        0 0 14px rgba(255,231,163,.12);
}}

.mb-active-nav .stButton > button {{
    color: #ffffff !important;
    border-color: rgba(255,231,163,.44) !important;
    background:
        linear-gradient(135deg, rgba(126,34,206,.78), rgba(38,12,62,.98)) !important;
    box-shadow:
        0 0 28px rgba(168,85,247,.24),
        inset 0 0 0 1px rgba(255,255,255,.05) !important;
}}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {{
    background: rgba(15,23,42,.92) !important;
    color: var(--mb-gold) !important;
    border: 1px solid rgba(96,165,250,.24) !important;
    border-radius: 15px !important;
    min-height: 44px !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.02) !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: var(--mb-muted) !important;
}}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {{
    border-color: var(--mb-blue) !important;
    box-shadow: 0 0 0 3px rgba(96,165,250,.14) !important;
}}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background: rgba(15,23,42,.92) !important;
    color: var(--mb-gold) !important;
    border: 1px solid rgba(96,165,250,.24) !important;
    border-radius: 15px !important;
    min-height: 44px !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 32%),
        linear-gradient(180deg, var(--mb-card), var(--mb-card-2)) !important;
    border: 1px solid var(--mb-line) !important;
    border-radius: 24px !important;
    box-shadow: 0 0 36px rgba(0,140,255,.075) !important;
}}

div[data-testid="stAlert"] {{
    background:
        linear-gradient(135deg, rgba(80,20,120,.28), rgba(30,64,175,.22)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 16px !important;
}}

[data-testid="metric-container"] {{
    background:
        linear-gradient(180deg, rgba(18,10,32,.96), rgba(10,8,20,.96)) !important;
    border-radius: 22px !important;
    border: 1px solid var(--mb-line) !important;
    padding: 18px !important;
    box-shadow: 0 0 26px rgba(168,85,247,.08) !important;
}}

[data-testid="metric-container"] label {{
    color: #d8b4fe !important;
    font-size: 12px !important;
    font-weight: 900 !important;
}}

.sidebar-user-card {{
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.14), transparent 34%),
        linear-gradient(180deg, rgba(22,8,38,.98), rgba(10,6,18,.98));
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 24px;
    padding: 18px;
    margin-top: 18px;
    margin-bottom: 10px;
    box-shadow: 0 0 32px rgba(168,85,247,.12);
}}

.sidebar-user-name {{
    font-size: 18px;
    font-weight: 1000;
    color: #ffffff !important;
    margin-bottom: 8px;
}}

.sidebar-user-plan {{
    display: inline-flex;
    padding: 6px 12px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #ffffff !important;
    font-size: 12px;
    font-weight: 1000;
    margin-bottom: 12px;
}}

.sidebar-user-tokens {{
    color: var(--mb-gold) !important;
    font-size: 28px;
    font-weight: 1000;
    line-height: 1;
    margin-top: 10px;
}}

.sidebar-user-caption {{
    color: var(--mb-muted) !important;
    font-size: 13px;
    margin-top: 6px;
}}

[data-testid="stAppViewContainer"] {{
    overflow-x: hidden !important;
}}

::-webkit-scrollbar {{
    width: 10px;
}}

::-webkit-scrollbar-thumb {{
    background: #a855f7;
    border-radius: 20px;
}}

::-webkit-scrollbar-track {{
    background: #12051d;
}}

@media (max-width: 900px) {{
    .main .block-container {{
        padding-top: 76px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    .custom-topbar {{
        height: 64px;
    }}
}}
</style>

<div class="custom-topbar"></div>
""",
        unsafe_allow_html=True,
    )


def require_login() -> None:
    if (
        not st.session_state.get("logged_in")
        or not st.session_state.get("user")
    ):
        st.session_state.page = "auth"
        st.stop()


def sync_session_user(user: dict | None) -> None:
    if not user:
        return

    st.session_state.logged_in = True
    st.session_state.user = user.get("username", "User")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = int(user.get("tokens", 0) or 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = int(user.get("admin_level", 0) or 0)


def nav(label: str, page: str, icon: str) -> None:
    path = icon_path(icon)

    is_active = st.session_state.get("page") == page
    active_class = "mb-active-nav" if is_active else ""

    st.markdown(
        f'<div class="mb-nav-wrap {active_class}">',
        unsafe_allow_html=True,
    )

    icon_col, button_col = st.columns([0.16, 0.84], gap="small")

    with icon_col:
        st.markdown(
            '<div class="mb-nav-icon-shell">',
            unsafe_allow_html=True,
        )

        if path.exists():
            st.image(str(path), width=23)

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with button_col:
        if st.button(label, key=f"nav_{page}", width="stretch"):
            st.session_state.page = page
            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        if WORDMARK.exists():
            st.image(str(WORDMARK), width="stretch")
        else:
            st.markdown("## MaByte")

        st.write("")

        nav("Mission Control", "home", "missioncontrol")
        nav("AI Assistant", "chat", "chat")
        nav("Projects", "projects", "projects")
        nav("Automations", "automation_lab", "automations")
        nav("Football AI", "football", "football")

        st.caption("MEDIA")

        nav("Image Studio", "image", "image")
        nav("Video Studio", "video", "video")
        nav("Reels Studio", "reels", "video")
        nav("Music Studio", "music", "music")
        nav("Code Studio", "coding", "code")

        st.caption("ACCOUNT")

        nav("Dashboard", "dashboard", "dashboard")
        nav("Premium", "premium", "premium")
        nav("Redeem", "redeem", "reedem")
        nav("Support", "support", "tools")

        admin_level = int(st.session_state.get("admin_level", 0) or 0)

        if admin_level >= 1:
            st.caption("SYSTEM")
            nav("Admin Panel", "admin", "settings-sliders")

        st.divider()

        user = html.escape(str(st.session_state.get("user", "User")))
        plan = html.escape(str(st.session_state.get("plan", "free")))
        tokens = int(st.session_state.get("tokens", 0) or 0)

        st.markdown(
            f"""
<div class="sidebar-user-card">
    <div class="sidebar-user-name">{user}</div>
    <div class="sidebar-user-plan">{plan.upper()}</div>
    <div class="sidebar-user-tokens">{tokens:,}</div>
    <div class="sidebar-user-caption">Tokens verfügbar</div>
</div>
""",
            unsafe_allow_html=True,
        )