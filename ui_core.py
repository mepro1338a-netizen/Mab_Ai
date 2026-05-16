import base64
import html
from pathlib import Path

import streamlit as st


ASSET_DIR = Path("assets")

WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


# =========================================================
# IMAGE HELPERS
# =========================================================

def img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""

    return base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")


def sidebar_icon(name: str) -> str:
    path = ASSET_DIR / f"{name}.png"

    if not path.exists():
        return ""

    encoded = img_base64(path)

    return f"""
<img
    src="data:image/png;base64,{encoded}"
    style="
        width:18px;
        height:18px;
        object-fit:contain;
        margin-right:12px;
        vertical-align:middle;
        border-radius:0px!important;
    "
>
"""


# =========================================================
# GLOBAL CSS
# =========================================================

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

.stApp {{
    background:
        radial-gradient(
            circle at top left,
            rgba(56,189,248,.16),
            transparent 26%
        ),

        radial-gradient(
            circle at top right,
            rgba(147,51,234,.14),
            transparent 26%
        ),

        linear-gradient(
            180deg,
            var(--mb-bg-1) 0%,
            var(--mb-bg-2) 52%,
            var(--mb-bg-0) 100%
        );
}}

.main .block-container {{
    max-width:1480px;
    padding-top:96px;
    padding-bottom:36px;
}}

.custom-topbar {{

    position:fixed;

    top:0;
    left:0;
    right:0;

    height:76px;

    z-index:999999;

    background:
        linear-gradient(
            90deg,
            rgba(5,10,20,.96),
            rgba(8,22,40,.96)
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
        linear-gradient(
            180deg,
            #06101d 0%,
            #0a1b31 100%
        )!important;

    border-right:
        1px solid rgba(255,255,255,.07);

    z-index:999!important;
}}

section[data-testid="stSidebar"] > div {{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
}}

section[data-testid="stSidebar"]
[data-testid="stVerticalBlock"] {{
    gap:.42rem!important;
}}

section[data-testid="stSidebar"] img {{
    border-radius:18px;
}}

section[data-testid="stSidebar"] .stCaption {{

    margin-top:1.1rem;

    color:var(--mb-muted)!important;

    font-size:.72rem;

    font-weight:800;

    letter-spacing:.12em;

    text-transform:uppercase;
}}

button[data-testid="collapsedControl"] {{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
}}

/* ===================================================== */
/* SIDEBAR BUTTONS */
/* ===================================================== */

.stButton > button {{

    width:100%;

    min-height:48px!important;

    border-radius:18px!important;

    border:
        1px solid rgba(56,189,248,.14)!important;

    background:
        linear-gradient(
            135deg,
            rgba(56,189,248,.92),
            rgba(14,165,233,.92)
        )!important;

    color:#ffffff!important;

    font-weight:850!important;

    font-size:14px!important;

    text-align:left!important;

    padding-left:18px!important;

    box-shadow:
        0 0 18px rgba(56,189,248,.10);

    transition:
        transform .18s ease,
        box-shadow .18s ease;
}}

.stButton > button:hover {{

    transform:translateY(-1px);

    box-shadow:
        0 0 26px rgba(56,189,248,.28);
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
            rgba(14,116,144,.34),
            rgba(30,64,175,.26)
        )!important;

    border:
        1px solid rgba(56,189,248,.22)!important;

    border-radius:16px!important;
}}

/* ===================================================== */
/* METRICS */
/* ===================================================== */

[data-testid="metric-container"] {{

    background:
        linear-gradient(
            180deg,
            rgba(11,24,44,.96),
            rgba(8,16,30,.96)
        )!important;

    border-radius:22px!important;

    border:
        1px solid var(--mb-line)!important;

    padding:20px!important;

    box-shadow:
        0 0 26px rgba(0,140,255,.07)!important;
}}

[data-testid="metric-container"] label {{

    color:#7dd3fc!important;

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
            rgba(11,24,44,.98),
            rgba(8,16,30,.98)
        );

    border:
        1px solid rgba(255,255,255,.07);

    border-radius:24px;

    padding:18px;

    margin-top:20px;

    box-shadow:
        0 0 32px rgba(0,140,255,.10);
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
            #9333ea
        );

    color:#ffffff!important;

    font-size:12px;

    font-weight:900;

    margin-bottom:12px;
}}

.sidebar-user-tokens {{

    color:var(--mb-cyan)!important;

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
/* SCROLLBAR */
/* ===================================================== */

::-webkit-scrollbar {{
    width:10px;
}}

::-webkit-scrollbar-thumb {{
    background:#1ea7ff;
    border-radius:20px;
}}

::-webkit-scrollbar-track {{
    background:#071120;
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


# =========================================================
# AUTH
# =========================================================

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

    st.session_state.user = user.get(
        "username",
        "User",
    )

    st.session_state.email = user.get(
        "email",
        "",
    )

    st.session_state.plan = user.get(
        "plan",
        "free",
    )

    st.session_state.tokens = int(
        user.get("tokens", 0) or 0
    )

    st.session_state.role = user.get(
        "role",
        "user",
    )

    st.session_state.admin_level = int(
        user.get("admin_level", 0) or 0
    )


# =========================================================
# NAVIGATION
# =========================================================

def nav(
    label: str,
    page: str,
    icon: str,
) -> None:

    icon_html = sidebar_icon(icon)

    button_label = f"{icon_html}{label}"

    if st.button(
        button_label,
        key=f"nav_{page}",
        width="stretch",
    ):
        st.session_state.page = page
        st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

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
            "redeem",
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
                "tools",
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