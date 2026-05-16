import base64
from pathlib import Path
import streamlit as st


ASSET_DIR = Path("assets")

WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


# =========================================================
# IMAGES
# =========================================================

def img_base64(path):

    if not path.exists():
        return ""

    return base64.b64encode(
        path.read_bytes()
    ).decode()


# =========================================================
# GLOBAL CSS
# =========================================================

def load_css():

    slogan = img_base64(SLOGAN_HEADER)

    slogan_css = ""

    if slogan:

        slogan_css = f"""
.custom-topbar {{
    background-image:url("data:image/png;base64,{slogan}");
    background-size:cover;
    background-position:center;
    background-repeat:no-repeat;
}}
"""

    st.markdown(
        f"""
<style>

/* =========================================================
HIDE STREAMLIT
========================================================= */

#MainMenu,
header,
footer,
[data-testid="stToolbar"]{{
    display:none!important;
}}

/* =========================================================
GLOBAL BACKGROUND
========================================================= */

.stApp{{
    background:
        radial-gradient(circle at top left, rgba(0,180,255,.18), transparent 25%),
        radial-gradient(circle at top right, rgba(139,92,246,.18), transparent 25%),
        linear-gradient(
            180deg,
            #071120 0%,
            #0b1d35 45%,
            #08172b 100%
        );
}}

/* =========================================================
MAIN CONTAINER
========================================================= */

.main .block-container{{
    max-width:1500px;
    padding-top:105px;
    padding-bottom:40px;
}}

/* =========================================================
TOPBAR
========================================================= */

.custom-topbar{{
    position:fixed;
    top:0;
    left:0;
    right:0;
    height:82px;
    z-index:999999;

    background:
        linear-gradient(
            90deg,
            rgba(5,10,20,.98),
            rgba(8,22,40,.98)
        );

    border-bottom:
        1px solid rgba(255,255,255,.05);

    backdrop-filter:blur(16px);
}}

{slogan_css}

/* =========================================================
SIDEBAR
========================================================= */

[data-testid="stSidebar"]{{
    background:
        linear-gradient(
            180deg,
            #07111d 0%,
            #0a1b31 100%
        )!important;

    border-right:
        1px solid rgba(255,255,255,.05);
}}

[data-testid="stSidebar"] *{{
    color:#ffe7a3!important;
}}

/* =========================================================
SIDEBAR BUTTONS
========================================================= */

.stButton > button{{
    width:100%;
    min-height:52px!important;

    border-radius:18px!important;

    border:
        1px solid rgba(0,180,255,.14)!important;

    background:
        linear-gradient(
            135deg,
            rgba(40,180,255,.92),
            rgba(0,140,255,.92)
        )!important;

    color:white!important;

    font-weight:850!important;

    font-size:15px!important;

    box-shadow:
        0 0 18px rgba(0,180,255,.12);

    transition:.22s;
}}

.stButton > button:hover{{
    transform:
        translateY(-2px)
        scale(1.015);

    box-shadow:
        0 0 28px rgba(0,180,255,.35);

    background:
        linear-gradient(
            135deg,
            #4ad7ff,
            #149cff
        )!important;
}}

/* =========================================================
TEXT
========================================================= */

h1,h2,h3,h4,h5,h6{{
    color:#ffe7a3!important;
    font-weight:900!important;
}}

p,span,label,div{{
    color:#f8e7b0!important;
}}

/* =========================================================
CARDS
========================================================= */

.stContainer{{
    background:
        linear-gradient(
            180deg,
            rgba(10,24,45,.94),
            rgba(8,18,34,.98)
        )!important;

    border:
        1px solid rgba(255,255,255,.05)!important;

    border-radius:28px!important;

    padding:22px!important;

    box-shadow:
        0 0 40px rgba(0,140,255,.08);
}}

/* =========================================================
INPUTS
========================================================= */

textarea,
input,
select{{
    background:
        rgba(255,255,255,.04)!important;

    color:#ffe7a3!important;

    border:
        1px solid rgba(0,180,255,.12)!important;

    border-radius:18px!important;
}}

/* =========================================================
METRICS
========================================================= */

[data-testid="metric-container"]{{
    background:
        linear-gradient(
            180deg,
            rgba(11,24,44,.98),
            rgba(8,16,30,.98)
        )!important;

    border-radius:24px!important;

    border:
        1px solid rgba(255,255,255,.05)!important;

    padding:22px!important;
}}

/* =========================================================
TABS
========================================================= */

.stTabs [data-baseweb="tab"]{{
    background:
        rgba(255,255,255,.04)!important;

    border-radius:14px!important;

    color:#ffe7a3!important;

    font-weight:800!important;

    padding:12px 20px!important;
}}

/* =========================================================
SIDEBAR TITLES
========================================================= */

.sidebar-section{{
    color:#7dd3fc!important;

    font-size:12px;

    font-weight:900;

    letter-spacing:1.5px;

    margin-top:22px;

    margin-bottom:10px;
}}

/* =========================================================
USER CARD
========================================================= */

.sidebar-card{{
    background:
        linear-gradient(
            180deg,
            rgba(11,24,44,.98),
            rgba(8,16,30,.98)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:26px;

    padding:22px;

    margin-top:24px;
}}

.sidebar-user{{
    font-size:20px;
    font-weight:900;
    color:#ffffff;
}}

.sidebar-plan{{
    display:inline-block;

    margin-top:10px;

    padding:6px 14px;

    border-radius:999px;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #9333ea
        );

    font-size:12px;

    font-weight:900;

    color:white;
}}

.sidebar-tokens{{
    margin-top:18px;

    font-size:32px;

    font-weight:950;

    color:#38bdf8;
}}

/* =========================================================
SCROLLBAR
========================================================= */

::-webkit-scrollbar{{
    width:10px;
}}

::-webkit-scrollbar-thumb{{
    background:#1ea7ff;
    border-radius:20px;
}}

/* =========================================================
REMOVE BLACK AREAS
========================================================= */

[data-testid="stHeader"]{{
    background:transparent!important;
}}

</style>

<div class="custom-topbar"></div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LOGIN
# =========================================================

def require_login():

    if not st.session_state.get("logged_in"):

        st.session_state.page = "auth"

        st.stop()


# =========================================================
# SESSION SYNC
# =========================================================

def sync_session_user(user):

    if not user:
        return

    st.session_state.logged_in = True

    st.session_state.user = user.get("username", "User")

    st.session_state.email = user.get("email", "")

    st.session_state.plan = user.get("plan", "free")

    st.session_state.tokens = int(
        user.get("tokens", 0) or 0
    )

    st.session_state.role = user.get("role", "user")

    st.session_state.admin_level = int(
        user.get("admin_level", 0) or 0
    )


# =========================================================
# NAV BUTTON
# =========================================================

def nav(label, page, icon):

    if st.button(
        f"{icon}  {label}",
        key=f"nav_{page}",
        use_container_width=True
    ):

        st.session_state.page = page

        st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        if WORDMARK.exists():

            st.image(
                str(WORDMARK),
                use_container_width=True
            )

        else:

            st.markdown("## MaByte")

        st.write("")

        # MAIN

        nav("Mission Control", "home", "🏠")
        nav("AI Assistant", "chat", "💬")
        nav("Projects", "projects", "📁")
        nav("Automations", "automation_lab", "⚡")
        nav("Football AI", "football", "⚽")

        # MEDIA

        st.markdown(
            '<div class="sidebar-section">MEDIA</div>',
            unsafe_allow_html=True,
        )

        nav("Image Studio", "image", "🎨")
        nav("Video Studio", "video", "🎬")
        nav("Reels Studio", "reels", "📣")
        nav("Music Studio", "music", "🎵")
        nav("Code Studio", "coding", "💻")

        # ACCOUNT

        st.markdown(
            '<div class="sidebar-section">ACCOUNT</div>',
            unsafe_allow_html=True,
        )

        nav("Dashboard", "dashboard", "👤")
        nav("Premium", "premium", "💎")
        nav("Redeem", "redeem", "🎁")
        nav("Support", "support", "🛟")

        # ADMIN

        if (
            st.session_state.get("role")
            in ["admin", "owner"]

            or

            int(
                st.session_state.get(
                    "admin_level",
                    0
                ) or 0
            ) > 0
        ):

            st.markdown(
                '<div class="sidebar-section">SYSTEM</div>',
                unsafe_allow_html=True,
            )

            nav("Admin Panel", "admin", "🛠️")

        # USER CARD

        user = st.session_state.get(
            "user",
            "User"
        )

        plan = st.session_state.get(
            "plan",
            "free"
        )

        tokens = int(
            st.session_state.get(
                "tokens",
                0
            ) or 0
        )

        st.markdown(
            f"""
<div class="sidebar-card">

    <div class="sidebar-user">
        {user}
    </div>

    <div class="sidebar-plan">
        {plan.upper()}
    </div>

    <div class="sidebar-tokens">
        {tokens:,}
    </div>

    <div style="color:#94a3b8;font-size:13px;">
        Tokens verfügbar
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )