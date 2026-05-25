import base64
import html
from pathlib import Path

import streamlit as st

from ui.styles import MB_THEME_VARS, inject_css
from ui.premium_foundation import inject_beta_global_css
from ui.design_system import inject_design_system


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
    "reels": "reels",
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

    return f"data:image/png;base64,{img_base64(path)}"


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

    inject_beta_global_css()
    inject_design_system(1480, 88)
    inject_css(f"""
{MB_THEME_VARS}

#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
button[title="View fullscreen"],
button[title="Fullscreen"],
[data-testid="StyledFullScreenButton"] {{
    display:none!important;
}}

[data-testid="stHeader"] {{
    background:transparent!important;
}}

html,
body,
.stApp,
.main,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 24%),
        radial-gradient(circle at top right, rgba(96,165,250,.10), transparent 26%),
        linear-gradient(180deg,#050816 0%,#081226 48%,#050711 100%)!important;
    background-attachment:fixed!important;
}}

.main .block-container {{
    max-width:1480px!important;
    padding-top:88px!important;
    padding-bottom:42px!important;
}}

.custom-topbar {{
    position:fixed;
    top:0;
    left:0;
    right:0;
    height:76px;
    z-index:999999;
    background:linear-gradient(90deg,rgba(9,8,24,.96),rgba(25,8,42,.96));
    border-bottom:1px solid rgba(255,255,255,.07);
    backdrop-filter:blur(18px);
}}

{slogan_css}

h1,h2,h3,h4,h5,h6 {{
    color:var(--mb-gold)!important;
    font-weight:1000!important;
}}

label,
.stMarkdown,
.stText,
.stCaption {{
    color:var(--mb-soft)!important;
}}

section[data-testid="stSidebar"] {{
    background:
        radial-gradient(ellipse 120% 80% at 0% 0%, rgba(124,58,237,.22), transparent 50%),
        radial-gradient(ellipse 80% 60% at 100% 100%, rgba(37,99,235,.12), transparent 45%),
        linear-gradient(185deg, #0c0614 0%, #1a0a28 42%, #08040f 100%)!important;
    border-right:1px solid rgba(255,231,163,.08)!important;
    box-shadow:4px 0 32px rgba(0,0,0,.25)!important;
}}

section[data-testid="stSidebar"] > div {{
    padding:12px 12px 20px 12px!important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap:8px!important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{
    background:rgba(6,4,14,.55)!important;
    border:1px solid rgba(168,85,247,.12)!important;
    border-radius:18px!important;
    padding:8px 6px 10px 6px!important;
    margin-bottom:6px!important;
    box-shadow:none!important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div {{
    padding:4px 2px!important;
}}

.sidebar-logo-wrap {{
    padding:4px 0 18px 0;
}}

.sidebar-logo-wrap img {{
    width:100%;
    border-radius:22px;
    box-shadow:0 18px 45px rgba(0,0,0,.22);
}}

.mb-section-label {{
    margin:16px 0 6px 4px;
    color:rgba(192,132,252,.85)!important;
    font-size:10px;
    font-weight:1000;
    letter-spacing:.22em;
    text-transform:uppercase;
}}
.mb-section-label:first-of-type {{
    margin-top:6px;
}}

.mb-nav-row {{
    display:flex;
    align-items:center;
    gap:8px;
    width:100%;
    margin-bottom:6px;
}}

.mb-nav-icon {{
    width:42px;
    height:42px;
    min-width:42px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.16), transparent 34%),
        linear-gradient(135deg, rgba(49,18,62,.95), rgba(20,9,32,.98));
    border:1px solid rgba(255,231,163,.15);
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 10px 24px rgba(0,0,0,.18);
}}

.mb-nav-icon img {{
    width:25px;
    height:25px;
    object-fit:contain;
    display:block;
}}

.mb-nav-button {{
    flex:1;
}}

.mb-nav-button .stButton > button {{
    width:100%!important;
    min-height:48px!important;
    border-radius:17px!important;
    border:1px solid rgba(255,231,163,.14)!important;
    background:
        linear-gradient(135deg, rgba(32,9,48,.90), rgba(12,6,22,.98))!important;
    color:var(--mb-gold)!important;
    font-weight:1000!important;
    font-size:15px!important;
    text-align:left!important;
    padding-left:18px!important;
    padding-right:12px!important;
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 10px 24px rgba(0,0,0,.16)!important;
    transition:all .18s ease!important;
}}

.mb-nav-button .stButton > button:hover {{
    transform:translateY(-1px)!important;
    color:#ffffff!important;
    border-color:rgba(255,231,163,.34)!important;
    background:
        linear-gradient(135deg, rgba(91,33,182,.72), rgba(22,8,36,.98))!important;
    box-shadow:0 0 24px rgba(168,85,247,.24)!important;
}}

.mb-nav-active .mb-nav-icon {{
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.30), transparent 34%),
        linear-gradient(135deg, rgba(126,34,206,.86), rgba(38,12,62,.98));
    border-color:rgba(255,231,163,.48);
    box-shadow:
        0 0 26px rgba(168,85,247,.28),
        0 0 14px rgba(255,231,163,.14);
}}

.mb-nav-active .mb-nav-button .stButton > button {{
    color:#ffffff!important;
    border-color:rgba(255,231,163,.48)!important;
    background:
        linear-gradient(135deg, rgba(126,34,206,.80), rgba(38,12,62,.98))!important;
    box-shadow:
        0 0 30px rgba(168,85,247,.26),
        inset 0 0 0 1px rgba(255,255,255,.05)!important;
}}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {{
    background:rgba(15,23,42,.92)!important;
    color:var(--mb-gold)!important;
    border:1px solid rgba(96,165,250,.24)!important;
    border-radius:15px!important;
    min-height:44px!important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color:var(--mb-muted)!important;
}}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background:rgba(15,23,42,.92)!important;
    color:var(--mb-gold)!important;
    border:1px solid rgba(96,165,250,.24)!important;
    border-radius:15px!important;
    min-height:44px!important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 32%),
        linear-gradient(180deg,rgba(12,18,38,.90),rgba(8,12,26,.98))!important;
    border:1px solid var(--mb-line)!important;
    border-radius:24px!important;
    box-shadow:0 0 36px rgba(0,140,255,.075)!important;
}}

div[data-testid="stAlert"] {{
    background:linear-gradient(135deg,rgba(80,20,120,.28),rgba(30,64,175,.22))!important;
    border:1px solid rgba(255,255,255,.08)!important;
    border-radius:16px!important;
}}

[data-testid="metric-container"] {{
    background:linear-gradient(180deg,rgba(18,10,32,.96),rgba(10,8,20,.96))!important;
    border-radius:22px!important;
    border:1px solid var(--mb-line)!important;
    padding:18px!important;
}}

.sidebar-user-card {{
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.2), transparent 40%),
        linear-gradient(165deg, rgba(22,10,38,.98), rgba(8,5,14,.99));
    border:1px solid rgba(255,231,163,.1);
    border-radius:22px;
    padding:16px 18px;
    margin-top:14px;
    margin-bottom:8px;
    box-shadow:0 12px 40px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.04);
}}
.sidebar-logout-wrap .stButton > button {{
    min-height:40px!important;
    border-radius:12px!important;
    background:rgba(15,23,42,.7)!important;
    border:1px solid rgba(148,163,184,.2)!important;
    color:#94a3b8!important;
    font-size:13px!important;
}}
.sidebar-logout-wrap .stButton > button:hover {{
    color:#f8fafc!important;
    border-color:rgba(255,231,163,.25)!important;
}}

.sidebar-user-row {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
}}

.sidebar-user-name {{
    font-size:18px;
    font-weight:1000;
    color:#ffffff!important;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}}

.sidebar-user-plan {{
    display:inline-flex;
    padding:6px 11px;
    border-radius:999px;
    background:linear-gradient(135deg,#7c3aed,#a855f7);
    color:#ffffff!important;
    font-size:11px;
    font-weight:1000;
    white-space:nowrap;
}}

.sidebar-user-tokens {{
    color:var(--mb-gold)!important;
    font-size:30px;
    font-weight:1000;
    line-height:1;
    margin-top:14px;
}}

.sidebar-user-caption {{
    color:var(--mb-muted)!important;
    font-size:13px;
    margin-top:6px;
}}

::-webkit-scrollbar {{
    width:10px;
}}

::-webkit-scrollbar-thumb {{
    background:#a855f7;
    border-radius:20px;
}}

::-webkit-scrollbar-track {{
    background:#12051d;
}}

@media(max-width:900px) {{
    .main .block-container {{
        padding-top:76px!important;
        padding-left:1rem!important;
        padding-right:1rem!important;
    }}

    .custom-topbar {{
        height:64px;
    }}
}}

/* Sidebar lock — page CSS must not override MaByte nav theme */
section[data-testid="stSidebar"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.24), transparent 25%),
        radial-gradient(circle at bottom right, rgba(96,165,250,.10), transparent 34%),
        linear-gradient(180deg,#16041f 0%,#230836 46%,#0d0315 100%)!important;
    border-right:1px solid rgba(255,255,255,.09)!important;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background:
        linear-gradient(135deg, rgba(32,9,48,.90), rgba(12,6,22,.98))!important;
    color:#ffe7a3!important;
    border:1px solid rgba(255,231,163,.14)!important;
    border-radius:17px!important;
    box-shadow:0 10px 24px rgba(0,0,0,.16)!important;
}}
section[data-testid="stSidebar"] .mb-nav-active .stButton > button {{
    color:#ffffff!important;
    border-color:rgba(255,231,163,.48)!important;
    background:
        linear-gradient(135deg, rgba(126,34,206,.80), rgba(38,12,62,.98))!important;
}}
""")

    st.markdown('<div class="custom-topbar"></div>', unsafe_allow_html=True)


def require_login() -> None:
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.session_state.page = "auth"
        st.stop()


def sync_session_user(user: dict | None) -> None:
    from services.session_auth import sync_from_user_record
    sync_from_user_record(user)


def is_admin_user() -> bool:
    from services.session_auth import server_is_admin
    return server_is_admin()


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
        f'<div class="mb-nav-row {active_class}">',
        unsafe_allow_html=True,
    )

    icon_col, button_col = st.columns([0.19, 0.81], gap="small")

    with icon_col:
        if src:
            st.markdown(
                f"""
<div class="mb-nav-icon">
    <img src="{src}" alt="">
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="mb-nav-icon"></div>',
                unsafe_allow_html=True,
            )

    with button_col:
        st.markdown('<div class="mb-nav-button">', unsafe_allow_html=True)

        if st.button(label, key=f"nav_{page}", width="stretch"):
            st.session_state.page = page
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _nav_section(title: str, items: list[tuple[str, str]]) -> None:
    with st.container(border=True):
        section_label(title)
        for label, page in items:
            nav(label, page)


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

        _nav_section("Workspace", [
            ("Mission Control", "home"),
            ("Dashboard", "dashboard"),
            ("AI Assistant", "chat"),
            ("Projects", "projects"),
            ("Football AI", "football"),
            ("Automations", "automation_lab"),
        ])
        _nav_section("Studios", [
            ("Image", "image"),
            ("Video", "video"),
            ("Reels", "reels"),
            ("Music", "music"),
            ("Code", "coding"),
        ])
        _nav_section("Account", [
            ("Premium", "premium"),
            ("Redeem", "redeem"),
            ("Support", "support"),
        ])
        if is_admin_user():
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