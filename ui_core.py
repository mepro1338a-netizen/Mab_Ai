import base64
from pathlib import Path
import streamlit as st


ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


def img_base64(path):
    if not path.exists():
        return ""

    return base64.b64encode(path.read_bytes()).decode()


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
HIDE STREAMLIT DEFAULTS
========================================================= */

#MainMenu,
header,
footer,
[data-testid="stToolbar"]{{
    display:none!important;
}}

[data-testid="stHeader"]{{
    background:transparent!important;
}}

/* =========================================================
GLOBAL BACKGROUND
========================================================= */

.stApp{{
    background:
        radial-gradient(circle at top left, rgba(0,180,255,.18), transparent 25%),
        radial-gradient(circle at top right, rgba(139,92,246,.18), transparent 25%),
        linear-gradient(180deg,#071120 0%,#0b1d35 45%,#08172b 100%);
}}

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
    background:linear-gradient(90deg,rgba(5,10,20,.98),rgba(8,22,40,.98));
    border-bottom:1px solid rgba(255,255,255,.05);
    backdrop-filter:blur(16px);
}}

{slogan_css}

/* =========================================================
SIDEBAR
========================================================= */

[data-testid="stSidebar"]{{
    background:linear-gradient(180deg,#07111d 0%,#0a1b31 100%)!important;
    border-right:1px solid rgba(255,255,255,.05);
}}

[data-testid="stSidebar"] *{{
    color:#ffe7a3!important;
}}

[data-testid="stSidebar"] img{{
    border-radius:18px;
}}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{{
    gap:.45rem!important;
}}

/* =========================================================
TEXT
========================================================= */

h1,h2,h3,h4,h5,h6{{
    color:#ffe7a3!important;
    font-weight:900!important;
    letter-spacing:-.03em;
}}

p,span,label,div{{
    color:#f8e7b0!important;
}

small{{
    color:#94a3b8!important;
}}

/* =========================================================
BUTTONS
========================================================= */

.stButton > button{{
    width:100%;
    min-height:50px!important;
    border-radius:18px!important;
    border:1px solid rgba(0,180,255,.18)!important;
    background:linear-gradient(135deg,#38bdf8,#0ea5e9)!important;
    color:white!important;
    font-weight:850!important;
    font-size:15px!important;
    box-shadow:0 0 18px rgba(0,180,255,.12);
    transition:.22s;
}}

.stButton > button:hover{{
    transform:translateY(-2px) scale(1.01);
    box-shadow:0 0 28px rgba(0,180,255,.35);
}}

.stButton > button:active{{
    transform:translateY(0px) scale(.99);
}}

/* =========================================================
INPUTS DARK PREMIUM
========================================================= */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input{{
    background:rgba(15,23,42,.94)!important;
    color:#ffe7a3!important;
    border:1px solid rgba(96,165,250,.22)!important;
    border-radius:16px!important;
    min-height:46px!important;
    box-shadow:inset 0 0 0 1px rgba(255,255,255,.02)!important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder{{
    color:#94a3b8!important;
}}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus{{
    border-color:#38bdf8!important;
    box-shadow:0 0 0 3px rgba(56,189,248,.16)!important;
}}

/* Selectbox closed */
.stSelectbox div[data-baseweb="select"] > div{{
    background:rgba(15,23,42,.94)!important;
    color:#ffe7a3!important;
    border:1px solid rgba(96,165,250,.22)!important;
    border-radius:16px!important;
    min-height:46px!important;
}}

/* Selectbox text */
.stSelectbox div[data-baseweb="select"] span{{
    color:#ffe7a3!important;
}}

/* Selectbox dropdown menu */
div[data-baseweb="popover"] div[data-baseweb="menu"]{{
    background:#0f172a!important;
    border:1px solid rgba(96,165,250,.20)!important;
    border-radius:16px!important;
    box-shadow:0 24px 60px rgba(0,0,0,.45)!important;
}}

div[data-baseweb="popover"] li{{
    background:#0f172a!important;
    color:#ffe7a3!important;
}}

div[data-baseweb="popover"] li:hover{{
    background:#1e3a8a!important;
    color:white!important;
}}

/* Multiselect */
.stMultiSelect div[data-baseweb="select"] > div{{
    background:rgba(15,23,42,.94)!important;
    border:1px solid rgba(96,165,250,.22)!important;
    border-radius:16px!important;
}}

/* Sliders */
.stSlider [data-baseweb="slider"] div{{
    color:#38bdf8!important;
}}

/* Checkboxes / radios */
.stCheckbox label,
.stRadio label{{
    color:#ffe7a3!important;
}}

/* =========================================================
CARDS / CONTAINERS
========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"]{{
    background:linear-gradient(180deg,rgba(10,24,45,.94),rgba(8,18,34,.98))!important;
    border:1px solid rgba(255,255,255,.06)!important;
    border-radius:28px!important;
    box-shadow:0 0 40px rgba(0,140,255,.08)!important;
}}

/* Info / warning / success boxes */
div[data-testid="stAlert"]{{
    background:linear-gradient(135deg,rgba(14,116,144,.35),rgba(30,64,175,.28))!important;
    border:1px solid rgba(56,189,248,.22)!important;
    border-radius:18px!important;
}}

div[data-testid="stAlert"] *{{
    color:#ffe7a3!important;
}}

/* =========================================================
METRICS
========================================================= */

[data-testid="metric-container"]{{
    background:linear-gradient(180deg,rgba(11,24,44,.98),rgba(8,16,30,.98))!important;
    border-radius:24px!important;
    border:1px solid rgba(255,255,255,.06)!important;
    padding:22px!important;
    box-shadow:0 0 28px rgba(0,140,255,.08)!important;
}}

[data-testid="metric-container"] label{{
    color:#7dd3fc!important;
    font-size:12px!important;
    font-weight:900!important;
}}

[data-testid="metric-container"] div{{
    color:#ffe7a3!important;
    font-weight:950!important;
}}

/* =========================================================
TABS
========================================================= */

.stTabs [data-baseweb="tab-list"]{{
    gap:10px!important;
}}

.stTabs [data-baseweb="tab"]{{
    background:rgba(255,255,255,.04)!important;
    border:1px solid rgba(255,255,255,.06)!important;
    border-radius:14px!important;
    color:#ffe7a3!important;
    font-weight:850!important;
    padding:12px 20px!important;
}}

.stTabs [aria-selected="true"]{{
    background:linear-gradient(135deg,rgba(56,189,248,.28),rgba(37,99,235,.30))!important;
    color:white!important;
}}

/* =========================================================
DATAFRAME
========================================================= */

[data-testid="stDataFrame"]{{
    border-radius:22px!important;
    overflow:hidden!important;
    border:1px solid rgba(255,255,255,.06)!important;
}}

/* =========================================================
EXPANDERS
========================================================= */

.streamlit-expanderHeader{{
    background:rgba(15,23,42,.72)!important;
    border-radius:16px!important;
    color:#ffe7a3!important;
    font-weight:850!important;
}}

details{{
    border-radius:18px!important;
    border:1px solid rgba(255,255,255,.06)!important;
    background:rgba(15,23,42,.50)!important;
}}

/* =========================================================
SIDEBAR USER CARD
========================================================= */

.sidebar-user-card{{
    background:linear-gradient(180deg,rgba(11,24,44,.98),rgba(8,16,30,.98));
    border:1px solid rgba(255,255,255,.06);
    border-radius:26px;
    padding:20px;
    margin-top:24px;
    box-shadow:0 0 35px rgba(0,140,255,.10);
}}

.sidebar-user-name{{
    font-size:19px;
    font-weight:950;
    color:#ffffff!important;
    margin-bottom:8px;
}}

.sidebar-user-plan{{
    display:inline-flex;
    padding:6px 13px;
    border-radius:999px;
    background:linear-gradient(135deg,#7c3aed,#9333ea);
    color:white!important;
    font-size:12px;
    font-weight:900;
    margin-bottom:14px;
}}

.sidebar-user-tokens{{
    color:#38bdf8!important;
    font-size:30px;
    font-weight:1000;
    line-height:1;
    margin-top:12px;
}}

.sidebar-user-caption{{
    color:#94a3b8!important;
    font-size:13px;
    margin-top:6px;
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

::-webkit-scrollbar-track{{
    background:#071120;
}}

</style>

<div class="custom-topbar"></div>
        """,
        unsafe_allow_html=True,
    )


def require_login():
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.session_state.page = "auth"
        st.stop()


def sync_session_user(user):
    if not user:
        return

    st.session_state.logged_in = True
    st.session_state.user = user.get("username", "User")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = int(user.get("tokens", 0) or 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = int(user.get("admin_level", 0) or 0)


def nav(label, page, icon):
    if st.button(f"{icon}  {label}", key=f"nav_{page}", use_container_width=True):
        st.session_state.page = page
        st.rerun()


def render_sidebar():
    with st.sidebar:
        if WORDMARK.exists():
            st.image(str(WORDMARK), use_container_width=True)
        else:
            st.markdown("## MaByte")

        st.write("")

        nav("Mission Control", "home", "🏠")
        nav("AI Assistant", "chat", "💬")
        nav("Projects", "projects", "📁")
        nav("Automations", "automation_lab", "⚡")
        nav("Football AI", "football", "⚽")

        st.caption("MEDIA")
        nav("Image Studio", "image", "🎨")
        nav("Video Studio", "video", "🎬")
        nav("Reels Studio", "reels", "📣")
        nav("Music Studio", "music", "🎵")
        nav("Code Studio", "coding", "💻")

        st.caption("ACCOUNT")
        nav("Dashboard", "dashboard", "👤")
        nav("Premium", "premium", "💎")
        nav("Redeem", "redeem", "🎁")
        nav("Support", "support", "🛟")

        admin_level = int(st.session_state.get("admin_level", 0) or 0)

        if admin_level >= 1:
            st.caption("SYSTEM")
            nav("Admin Panel", "admin", "🛠️")

        st.divider()

        user = st.session_state.get("user", "User")
        plan = st.session_state.get("plan", "free")
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