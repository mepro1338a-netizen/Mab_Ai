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
    background-image: url("data:image/png;base64,{slogan}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
"""

    st.markdown(
        f"""
<style>
#MainMenu,
header,
footer,
[data-testid="stToolbar"] {{
    display: none !important;
}}

.stApp {{
    background:
        radial-gradient(circle at top, rgba(37,99,235,.12), transparent 30%),
        linear-gradient(135deg, #020617 0%, #071427 55%, #020617 100%);
}}

.main .block-container {{
    max-width: 1450px;
    padding-top: 95px;
    padding-bottom: 1rem;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #071120 0%, #050b16 100%) !important;
    border-right: 1px solid rgba(96,165,250,.12);
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

.custom-topbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 82px;
    z-index: 999999;
    background-color: #020617;
    border-bottom: 1px solid rgba(96,165,250,.10);
}}

{slogan_css}

.stButton > button {{
    width: 100%;
    min-height: 46px !important;
    border-radius: 15px !important;
    border: 1px solid rgba(96,165,250,.12) !important;
    background: rgba(15,23,42,.58) !important;
    color: #dbeafe !important;
    font-weight: 850 !important;
    box-shadow: none !important;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
    color: white !important;
    transform: translateY(-1px);
}}

.sidebar-section {{
    color: #64748b !important;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-top: 22px;
    margin-bottom: 8px;
}}

.sidebar-card {{
    background: linear-gradient(135deg, rgba(15,23,42,.95), rgba(30,41,59,.82));
    border: 1px solid rgba(96,165,250,.12);
    border-radius: 22px;
    padding: 18px;
    margin-top: 22px;
}}

.sidebar-user {{
    font-size: 18px;
    font-weight: 900;
    color: white;
}}

.sidebar-plan {{
    display: inline-block;
    margin-top: 8px;
    padding: 5px 11px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    font-size: 12px;
    font-weight: 850;
    color: white;
}}

.sidebar-tokens {{
    margin-top: 16px;
    color: #38bdf8;
    font-size: 24px;
    font-weight: 950;
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
            st.markdown("## 🚀 MaByte")

        st.write("")

        nav("Mission Control", "home", "🏠")
        nav("AI Assistant", "chat", "💬")
        nav("Projects", "projects", "📁")
        nav("Automations", "automation_lab", "⚡")
        nav("Football AI", "football", "⚽")

        st.markdown('<div class="sidebar-section">MEDIA TOOLS</div>', unsafe_allow_html=True)

        nav("Image Generation", "image", "🎨")
        nav("Video Generation", "video", "🎬")
        nav("Reels Maker", "reels", "📣")
        nav("Music Creator", "music", "🎵")
        nav("Coding Assistant", "coding", "💻")

        st.markdown('<div class="sidebar-section">ACCOUNT</div>', unsafe_allow_html=True)

        nav("Dashboard", "dashboard", "👤")
        nav("Premium", "premium", "💎")
        nav("Redeem Code", "redeem", "🎁")
        nav("Support", "support", "🛟")

        if st.session_state.get("role") in ["admin", "owner"] or int(st.session_state.get("admin_level", 0) or 0) > 0:
            st.markdown('<div class="sidebar-section">SYSTEM</div>', unsafe_allow_html=True)
            nav("Admin Panel", "admin", "🛠️")

        user = st.session_state.get("user", "User")
        plan = st.session_state.get("plan", "free")
        tokens = int(st.session_state.get("tokens", 0) or 0)

        st.markdown(
            f"""
<div class="sidebar-card">
    <div class="sidebar-user">{user}</div>
    <div class="sidebar-plan">{plan}</div>
    <div class="sidebar-tokens">{tokens:,}</div>
    <div style="color:#94a3b8;font-size:13px;">Tokens verfügbar</div>
</div>
            """,
            unsafe_allow_html=True,
        )