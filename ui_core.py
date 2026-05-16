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
#MainMenu,
header,
footer,
[data-testid="stToolbar"]{{
    display:none!important;
}}

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

[data-testid="stSidebar"]{{
    background:linear-gradient(180deg,#07111d 0%,#0a1b31 100%)!important;
    border-right:1px solid rgba(255,255,255,.05);
}}

[data-testid="stSidebar"] *{{
    color:#ffe7a3!important;
}}

h1,h2,h3,h4,h5,h6{{
    color:#ffe7a3!important;
    font-weight:900!important;
}}

p,span,label,div{{
    color:#f8e7b0!important;
}}

.stButton > button{{
    width:100%;
    min-height:50px!important;
    border-radius:18px!important;
    border:1px solid rgba(0,180,255,.14)!important;
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

textarea,
input,
select{{
    background:rgba(255,255,255,.05)!important;
    color:#ffe7a3!important;
    border:1px solid rgba(0,180,255,.16)!important;
    border-radius:16px!important;
}}

[data-testid="metric-container"]{{
    background:linear-gradient(180deg,rgba(11,24,44,.98),rgba(8,16,30,.98))!important;
    border-radius:24px!important;
    border:1px solid rgba(255,255,255,.05)!important;
    padding:22px!important;
}}

.stTabs [data-baseweb="tab"]{{
    background:rgba(255,255,255,.04)!important;
    border-radius:14px!important;
    color:#ffe7a3!important;
    font-weight:800!important;
    padding:12px 20px!important;
}}

[data-testid="stHeader"]{{
    background:transparent!important;
}}

::-webkit-scrollbar{{
    width:10px;
}}

::-webkit-scrollbar-thumb{{
    background:#1ea7ff;
    border-radius:20px;
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

        with st.container(border=True):
            st.subheader(user)
            st.caption(plan.upper())
            st.metric("Tokens", f"{tokens:,}")