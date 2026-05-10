# ui.py

import streamlit as st

from database import init_db
from ui_styles import load_css

from pages.home import render_home
from pages.chat import render_chat
from pages.media import render_media
from pages.admin import render_admin

# ============================================
# APP CONFIG
# ============================================

st.set_page_config(
    page_title="Mabyte",
    page_icon="Logo24mp.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# INIT
# ============================================

init_db()
load_css()

# ============================================
# SESSION STATE
# ============================================

if "page" not in st.session_state:
    st.session_state.page = "home"

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:

    st.image("LogoMAIN.png", use_container_width=True)

    st.markdown(
        """
        <div class="sidebar-subtitle">
            Next Generation AI Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### AI Tools")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"

    if st.button("💬 Memory Chat", use_container_width=True):
        st.session_state.page = "chat"

    if st.button("💻 Coding AI", use_container_width=True):
        st.session_state.page = "coding"

    if st.button("🎨 Image Generator", use_container_width=True):
        st.session_state.page = "image"

    if st.button("🎵 Music Generator", use_container_width=True):
        st.session_state.page = "music"

    if st.button("🎬 Reels Creator", use_container_width=True):
        st.session_state.page = "reels"

    if st.button("🎞️ AI Video Generator", use_container_width=True):
        st.session_state.page = "video"

    st.markdown("---")
    st.markdown("### Account")

    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "admin"

# ============================================
# ROUTING
# ============================================

page = st.session_state.get("page", "home")

if page == "home":
    render_home()

elif page == "login":
    render_auth()

elif page == "chat":
    render_chat()

elif page == "coding":
    render_media("coding")

elif page == "image":
    render_media("image")

elif page == "music":
    render_media("music")

elif page == "reels":
    render_media("reels")

elif page == "video":
    render_media("video")

elif page == "dashboard":
    render_dashboard()

elif page == "redeem":
    render_redeem()

elif page == "support":
    render_support()

elif page == "premium":
    render_premium()

elif page == "admin":
    render_admin()

else:
    render_home()