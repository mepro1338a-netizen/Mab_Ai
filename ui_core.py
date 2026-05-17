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

    return base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")


def icon_path(name: str) -> Path:
    return ASSET_DIR / f"{name}.png"


def load_css() -> None:

    slogan = img_base64(SLOGAN_HEADER)

    slogan_css = ""

    if slogan:
        slogan_css = f"""
.custom-topbar {{
    background-image:
        url("data:image/png;base64,{slogan}");

    background-size:cover;
    background-position:center;
    background-repeat:no-repeat;
}}
"""

    st.markdown(
        f"""
<style>

:root {{
    --mb-bg-0:#050914;
    --mb-bg-1:#071120;
    --mb-bg-2:#0b1d35;

    --mb-card:
        rgba(10,24,45,.86);

    --mb-card-strong:
        rgba(8,18,34,.96);

    --mb-line:
        rgba(255,255,255,.075);

    --mb-gold:#ffe7a3;
    --mb-gold-soft:#f8e7b0;

    --mb-cyan:#38bdf8;
    --mb-purple:#a855f7;

    --mb-muted:#94a3b8;
}}

#MainMenu,
footer,
[data-testid="stToolbar"] {{
    display:none!important;
}}

[data-testid="stHeader"] {{
    background:transparent!important;
    z-index:998!important;
}}

/* ===================================================== */
/* GLOBAL AI OS BACKGROUND */
/* ===================================================== */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main,
.block-container,
.stApp {{

    background:

        radial-gradient(
            circle at top left,
            rgba(168,85,247,.10),
            transparent 22%
        ),

        radial-gradient(
            circle at top right,
            rgba(56,189,248,.08),
            transparent 24%
        ),

        radial-gradient(
            circle at bottom left,
            rgba(168,85,247,.06),
            transparent 30%
        ),

        linear-gradient(
            180deg,
            #050510 0%,
            #0b1020 45%,
            #05060d 100%
        ) !important;

    background-attachment:fixed!important;
}}

div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="column"] {{
    background:transparent!important;
}}

.main .block-container {{
    max-width:1480px;
    padding-top:0px;
    padding-bottom:36px;
}}

.custom-topbar {{

    position:relative;

    top:0;
    left:0;
    right:0;

    height:76px;

    z-index:999999;

    background:
        linear-gradient(
            90deg,
            rgba(14,6,24,.96),
            rgba(24,10,38,.96)
        );

    border-bottom:
        1px solid rgba(255,255,255,.06);

    backdrop-filter:blur(18px);
}}

{slogan_css}

/* ===================================================== */
/* TYPO */
/* ===================================================== */

h1,h2,h3,h4,h5,h6 {{
    color:var(--mb-gold)!important;
    font-weight:900!important;
    letter-spacing:-.035em;
}}

.stMarkdown,
.stCaption,
.stText,
label {{
    color:var(--mb-gold-soft)!important;
}}

small,
.stCaption {{
    color:var(--mb-muted)!important;
}}

/* ===================================================== */
/* SIDEBAR */
/* ===================================================== */

section[data-testid="stSidebar"] {{

    display:block!important;
    visibility:visible!important;
    opacity:1!important;

    background:

        radial-gradient(
            circle at top left,
            rgba(168,85,247,.18),
            transparent 24%
        ),

        radial-gradient(
            circle at bottom right,
            rgba(56,189,248,.08),
            transparent 30%
        ),

        linear-gradient(
            180deg,
            #14051f 0%,
            #1b082b 38%,
            #100419 100%
        )!important;

    border-right:
        1px solid rgba(255,255,255,.08);

    z-index:999!important;
}}

section[data-testid="stSidebar"] > div {{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;

    padding-left:12px!important;
    padding-right:12px!important;
}}

section[data-testid="stSidebar"]
[data-testid="stVerticalBlock"] {{
    gap:.28rem!important;
}}

section[data-testid="stSidebar"] img {{
    border-radius:16px;
}}

section[data-testid="stSidebar"] .stCaption {{

    margin-top:.9rem;
    margin-bottom:.15rem;

    color:
        rgba(255,231,163,.72)!important;

    font-size:.72rem;

    font-weight:850;

    letter-spacing:.13em;

    text-transform:uppercase;
}}

button[data-testid="collapsedControl"] {{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
}}

/* ===================================================== */
/* NAVIGATION */
/* ===================================================== */

.mb-nav-wrap {{
    margin-bottom:7px;
}}

.mb-nav-wrap [data-testid="column"] {{
    padding:0!important;
}}

.mb-nav-icon-shell {{

    width:42px;
    height:42px;

    border-radius:15px;

    display:flex;
    align-items:center;
    justify-content:center;

    background:
        linear-gradient(
            135deg,
            rgba(255,231,163,.10),
            rgba(168,85,247,.10)
        );

    border:
        1px solid rgba(255,231,163,.14);

    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025);
}}

.mb-nav-icon-shell img {{

    width:24px!important;
    height:24px!important;

    object-fit:contain!important;

    border-radius:0!important;
}}

/* ===================================================== */
/* BUTTONS */
/* ===================================================== */

.stButton > button {{

    width:100%;

    min-height:42px!important;

    border-radius:15px!important;

    border:
        1px solid rgba(255,231,163,.16)!important;

    background:
        linear-gradient(
            135deg,
            rgba(28,10,42,.96),
            rgba(12,6,22,.98)
        )!important;

    color:var(--mb-gold)!important;

    font-weight:1000!important;

    font-size:14px!important;

    letter-spacing:.01em!important;

    text-align:left!important;

    padding-left:14px!important;

    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 10px 26px rgba(0,0,0,.18);

    transition:
        transform .18s ease,
        box-shadow .18s ease,
        border-color .18s ease,
        background .18s ease,
        color .18s ease;
}}

.stButton > button:hover {{

    transform:translateY(-1px);

    color:#ffffff!important;

    border-color:
        rgba(255,231,163,.38)!important;

    background:
        linear-gradient(
            135deg,
            rgba(72,28,112,.92),
            rgba(20,8,34,.98)
        )!important;

    box-shadow:
        0 0 24px rgba(168,85,247,.22),
        0 0 12px rgba(255,231,163,.08);
}}

.stButton > button:active {{
    transform:translateY(0);
}}

.mb-active-nav .mb-nav-icon-shell {{

    background:
        linear-gradient(
            135deg,
            rgba(255,231,163,.22),
            rgba(168,85,247,.24)
        );

    border-color:
        rgba(255,231,163,.42);

    box-shadow:
        0 0 22px rgba(168,85,247,.20),
        0 0 12px rgba(255,231,163,.12);
}}

.mb-active-nav .stButton > button {{

    color:#ffffff!important;

    border-color:
        rgba(255,231,163,.42)!important;

    background:
        linear-gradient(
            135deg,
            rgba(126,34,206,.70),
            rgba(38,12,62,.98)
        )!important;

    box-shadow:
        0 0 26px rgba(168,85,247,.22),
        inset 0 0 0 1px rgba(255,255,255,.04);
}}

/* ===================================================== */
/* INPUTS */
/* ===================================================== */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {{

    background:
        rgba(15,23,42,.92)!important;

    color:
        var(--mb-gold)!important;

    border:
        1px solid rgba(96,165,250,.24)!important;

    border-radius:15px!important;

    min-height:44px!important;

    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.02)!important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color:var(--mb-muted)!important;
}}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {{

    border-color:
        var(--mb-cyan)!important;

    box-shadow:
        0 0 0 3px rgba(56,189,248,.15)!important;
}}

/* ===================================================== */
/* SELECT */
/* ===================================================== */

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{

    background:
        rgba(15,23,42,.92)!important;

    color:
        var(--mb-gold)!important;

    border:
        1px solid rgba(96,165,250,.24)!important;

    border-radius:15px!important;

    min-height:44px!important;
}}

/* ===================================================== */
/* CARDS */
/* ===================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] {{

    background:
        linear-gradient(
            180deg,
            var(--mb-card),
            var(--mb-card-strong)
        )!important;

    border:
        1px solid var(--mb-line)!important;

    border-radius:24px!important;

    box-shadow:
        0 0 36px rgba(0,140,255,.075)!important;
}}

/* ===================================================== */
/* ALERTS */
/* ===================================================== */

div[data-testid="stAlert"] {{

    background:
        linear-gradient(
            135deg,
            rgba(80,20,120,.28),
            rgba(30,64,175,.22)
        )!important;

    border:
        1px solid rgba(255,255,255,.08)!important;

    border-radius:16px!important;
}}

/* ===================================================== */
/* METRICS */
/* ===================================================== */

[data-testid="metric-container"] {{

    background:
        linear-gradient(
            180deg,
            rgba(18,10,32,.96),
            rgba(10,8,20,.96)
        )!important;

    border-radius:22px!important;

    border:
        1px solid var(--mb-line)!important;

    padding:20px!important;

    box-shadow:
        0 0 26px rgba(168,85,247,.08)!important;
}}

[data-testid="metric-container"] label {{

    color:#d8b4fe!important;

    font-size:12px!important;

    font-weight:900!important;
}}

/* ===================================================== */
/* USER CARD */
/* ===================================================== */

.sidebar-user-card {{

    background:
        linear-gradient(
            180deg,
            rgba(20,8,34,.98),
            rgba(10,6,18,.98)
        );

    border:
        1px solid rgba(255,255,255,.08);

    border-radius:24px;

    padding:18px;

    margin-top:20px;

    box-shadow:
        0 0 32px rgba(168,85,247,.10);
}}

.sidebar-user-name {{

    font-size:18px;

    font-weight:950;

    color:#ffffff!important;

    margin-bottom:8px;
}}

.sidebar-user-plan {{

    display:inline-flex;

    padding:6px 12px;

    border-radius:999px;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #a855f7
        );

    color:#ffffff!important;

    font-size:12px;

    font-weight:900;

    margin-bottom:12px;
}}

.sidebar-user-tokens {{

    color:var(--mb-gold)!important;

    font-size:28px;

    font-weight:1000;

    line-height:1;

    margin-top:10px;
}}

.sidebar-user-caption {{

    color:var(--mb-muted)!important;

    font-size:13px;

    margin-top:6px;
}}

/* ===================================================== */
/* FIXES */
/* ===================================================== */

button[title="View fullscreen"],
button[title="Fullscreen"],
[data-testid="StyledFullScreenButton"],
div[data-testid="stDecoration"] {{
    display:none!important;
}}

[data-testid="stAppViewContainer"] {{
    overflow-x:hidden!important;
}}

/* ===================================================== */
/* SCROLLBAR */
/* ===================================================== */

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

/* ===================================================== */
/* MOBILE */
/* ===================================================== */

@media (max-width:900px) {{

    .main .block-container {{
        padding-top:84px;
        padding-left:1rem;
        padding-right:1rem;
    }}

    .custom-topbar {{
        height:64px;
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


def sync_session_user(
    user: dict | None
) -> None:

    if not user:
        return

    st.session_state.logged_in = True
    st.session_state.user = user.get("username", "User")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = int(user.get("tokens", 0) or 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = int(user.get("admin_level", 0) or 0)


def nav(
    label: str,
    page: str,
    icon: str,
) -> None:

    path = icon_path(icon)

    is_active = (
        st.session_state.get("page")
        == page
    )

    active_class = (
        "mb-active-nav"
        if is_active
        else ""
    )

    st.markdown(
        f'<div class="mb-nav-wrap {active_class}">',
        unsafe_allow_html=True,
    )

    icon_col, button_col = st.columns(
        [0.15, 0.85],
        gap="small",
    )

    with icon_col:

        if path.exists():

            st.markdown(
                '<div class="mb-nav-icon-shell">',
                unsafe_allow_html=True,
            )

            st.image(
                str(path),
                width=24,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                '<div class="mb-nav-icon-shell"></div>',
                unsafe_allow_html=True,
            )

    with button_col:

        if st.button(
            label,
            key=f"nav_{page}",
            width="stretch",
        ):
            st.session_state.page = page
            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:

    with st.sidebar:

        if WORDMARK.exists():

            st.image(
                str(WORDMARK),
                width="stretch",
            )

        else:
            st.markdown("## MaByte")

        st.write("")

        nav(
            "Mission Control",
            "home",
            "missioncontrol",
        )

        nav(
            "AI Assistant",
            "chat",
            "chat",
        )

        nav(
            "Projects",
            "projects",
            "projects",
        )

        nav(
            "Automations",
            "automation_lab",
            "automations",
        )

        nav(
            "Football AI",
            "football",
            "football",
        )

        st.caption("MEDIA")

        nav(
            "Image Studio",
            "image",
            "image",
        )

        nav(
            "Video Studio",
            "video",
            "video",
        )

        nav(
            "Reels Studio",
            "reels",
            "video",
        )

        nav(
            "Music Studio",
            "music",
            "music",
        )

        nav(
            "Code Studio",
            "coding",
            "code",
        )

        st.caption("ACCOUNT")

        nav(
            "Dashboard",
            "dashboard",
            "dashboard",
        )

        nav(
            "Premium",
            "premium",
            "premium",
        )

        nav(
            "Redeem",
            "redeem",
            "reedem",
        )

        nav(
            "Support",
            "support",
            "tools",
        )

        admin_level = int(
            st.session_state.get(
                "admin_level",
                0,
            ) or 0
        )

        if admin_level >= 1:

            st.caption("SYSTEM")

            nav(
                "Admin Panel",
                "admin",
                "settings-sliders",
            )

        st.divider()

        user = html.escape(
            str(
                st.session_state.get(
                    "user",
                    "User",
                )
            )
        )

        plan = html.escape(
            str(
                st.session_state.get(
                    "plan",
                    "free",
                )
            )
        )

        tokens = int(
            st.session_state.get(
                "tokens",
                0,
            ) or 0
        )

        st.markdown(
            f"""
<div class="sidebar-user-card">

<div class="sidebar-user-name">
{user}
</div>

<div class="sidebar-user-plan">
{plan.upper()}
</div>

<div class="sidebar-user-tokens">
{tokens:,}
</div>

<div class="sidebar-user-caption">
Tokens verfügbar
</div>

</div>
""",
            unsafe_allow_html=True,
        )