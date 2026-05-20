import base64
import html
from pathlib import Path

import streamlit as st


ASSET_DIR = Path("assets")

WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


ICON_MAP = {
    "home": "missioncontrol",
    "chat": "chat",
    "projects": "projects",
    "automation_lab": "automations",
    "football": "football",
    "image": "image",
    "video": "video",
    "reels": "video",
    "music": "music",
    "coding": "code",
    "dashboard": "dashboard",
    "premium": "premium",
    "redeem": "redeem",
    "support": "tools",
    "admin": "settings-sliders",
}


def img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""

    return base64.b64encode(path.read_bytes()).decode("utf-8")


def icon_src(page: str) -> str:
    icon_name = ICON_MAP.get(page, page)
    path = ASSET_DIR / f"{icon_name}.png"

    if not path.exists():
        return ""

    encoded = img_base64(path)
    return f"data:image/png;base64,{encoded}"


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
    --mb-sidebar:#15051f;
    --mb-sidebar-2:#230836;
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
        radial-gradient(circle at top left, rgba(168,85,247,.24), transparent 25%),
        radial-gradient(circle at bottom right, rgba(96,165,250,.10), transparent 34%),
        linear-gradient(180deg, #16041f 0%, #230836 46%, #0d0315 100%) !important;
    border-right: 1px solid rgba(255,255,255,.09);
    z-index: 999 !important;
}}

section[data-testid="stSidebar"] > div {{
    padding-left: 14px !important;
    padding-right: 14px !important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: .18rem !important;
}}

.sidebar-logo-wrap {{
    padding: 4px 0 18px 0;
}}

.sidebar-logo-wrap img {{
    width: 100%;
    border-radius: 22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.22);
}}

.mb-section-label {{
    margin-top: 14px;
    margin-bottom: 7px;
    color: rgba(255,231,163,.64) !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .18em;
    text-transform: uppercase;
}}

button[data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}}

.mb-nav-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    margin-bottom: 9px;
}}

.mb-nav-icon {{
    flex: 0 0 46px;
    width: 46px;
    height: 46px;
    border-radius: 17px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.16), transparent 32%),
        linear-gradient(135deg, rgba(49,18,62,.95), rgba(20,9,32,.98));
    border: 1px solid rgba(255,231,163,.15);
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 10px 24px rgba(0,0,0,.18);
}}

.mb-nav-icon img {{
    width: 25px;
    height: 25px;
    object-fit: contain;
    display: block;
}}

.mb-nav-button {{
    flex: 1;
}}

.mb-nav-button .stButton > button {{
    width: 100% !important;
    min-height: 46px !important;
    border-radius: 17px !important;
    border: 1px solid rgba(255,231,163,.14) !important;
    background:
        linear-gradient(135deg, rgba(32,9,48,.90), rgba(12,6,22,.98)) !important;
    color: var(--mb-gold) !important;
    font-weight: 1000 !important;
    font-size: 15px !important;
    letter-spacing: .01em !important;
    text-align: center !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 10px 24px rgba(0,0,0,.16) !important;
    transition: all .18s ease !important;
}}

.mb-nav-button .stButton > button:hover {{
    transform: translateY(-1px) !important;
    color: #ffffff !important;
    border-color: rgba(255,231,163,.34) !important;
    background:
        linear-gradient(135deg, rgba(91,33,182,.72), rgba(22,8,36,.98)) !important;
    box-shadow:
        0 0 24px rgba(168,85,247,.22),
        0 0 12px rgba(255,231,163,.08) !important;
}}

.mb-nav-active .mb-nav-icon {{
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.28), transparent 32%),
        linear-gradient(135deg, rgba(126,34,206,.82), rgba(38,12,62,.98));
    border-color: rgba(255,231,163,.45);
    box-shadow:
        0 0 24px rgba(168,85,247,.26),
        0 0 16px rgba(255,231,163,.12);
}}

.mb-nav-active .mb-nav-button .stButton > button {{
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
        radial-gradient(circle at top right, rgba(168,85,247,.18), transparent 36%),
        linear-gradient(180deg, rgba(24,8,42,.98), rgba(10,6,18,.98));
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 26px;
    padding: 18px;
    margin-top: 18px;
    margin-bottom: 10px;
    box-shadow: 0 0 34px rgba(168,85,247,.14);
}}

.sidebar-user-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}}

.sidebar-user-name {{
    font-size: 18px;
    font-weight: 1000;
    color: #ffffff !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.sidebar-user-plan {{
    display: inline-flex;
    padding: 6px 11px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #ffffff !important;
    font-size: 11px;
    font-weight: 1000;
    white-space: nowrap;
}}

.sidebar-user-tokens {{
    color: var(--mb-gold) !important;
    font-size: 30px;
    font-weight: 1000;
    line-height: 1;
    margin-top: 14px;
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


def section_label(label: str) -> None:
    st.markdown(
        f'<div class="mb-section-label">{html.escape(label)}</div>',
        unsafe_allow_html=True,
    )


def nav(label: str, page: str) -> None:
    src = icon_src(page)
    is_active = st.session_state.get("page") == page
    active_class = "mb-nav-active" if is_active else ""

    st.markdown(
        f'<div class="mb-nav-item {active_class}">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mb-nav-icon">',
        unsafe_allow_html=True,
    )

    if src:
        st.markdown(
            f'<img src="{src}" alt="">',
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mb-nav-button">',
        unsafe_allow_html=True,
    )

    if st.button(label, key=f"nav_{page}", width="stretch"):
        st.session_state.page = page
        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        if WORDMARK.exists():
            wordmark_src = img_base64(WORDMARK)

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

        nav("Mission Control", "home")
        nav("AI Assistant", "chat")
        nav("Projects", "projects")
        nav("Automations", "automation_lab")
        nav("Football AI", "football")

        section_label("Media")

        nav("Image Studio", "image")
        nav("Video Studio", "video")
        nav("Reels Studio", "reels")
        nav("Music Studio", "music")
        nav("Code Studio", "coding")

        section_label("Account")

        nav("Dashboard", "dashboard")
        nav("Premium", "premium")
        nav("Redeem", "redeem")
        nav("Support", "support")

        admin_level = int(st.session_state.get("admin_level", 0) or 0)

        if admin_level >= 1:
            section_label("System")
            nav("Admin Panel", "admin")

        user = html.escape(str(st.session_state.get("user", "User")))
        plan = html.escape(str(st.session_state.get("plan", "free")))
        tokens = int(st.session_state.get("tokens", 0) or 0)

        st.markdown(
            f"""
<div class="sidebar-user-card">
    <div class="sidebar-user-row">
        <div class="sidebar-user-name">{user}</div>
        <div class="sidebar-user-plan">{plan.upper()}</div>
    </div>
    <div class="sidebar-user-tokens">{tokens:,}</div>
    <div class="sidebar-user-caption">Tokens verfügbar</div>
</div>
""",
            unsafe_allow_html=True,
        )