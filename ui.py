import streamlit as st

from database import init_db
from ui_styles import load_css
from ui_sidebar import render_sidebar

from pages.home import render_home
from pages.auth import render_auth
from pages.chat import render_chat
from pages.media import (
    render_image_page,
    render_video_page,
    render_coding_page,
    render_music_page,
    render_reels_page,
)

from pages.account import (
    render_dashboard,
    render_support,
    render_premium,
    render_redeem,
)

from pages.admin import render_admin


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="MAB.AI",
    page_icon="logo24mp.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# INIT
# =========================================================

init_db()
load_css()


# =========================================================
# SESSION
# =========================================================

defaults = {
    "page": "home",
    "user": None,
    "email": "",
    "plan": "free",
    "tokens": 0,
    "role": "user",
    "admin_level": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SIDEBAR
# =========================================================

render_sidebar()


# =========================================================
# ROUTER
# =========================================================

page = st.session_state.page

if page == "home":
    render_home()

elif page == "login":
    render_auth()

elif page == "chat":
    render_chat()

elif page == "image":
    render_image_page()

elif page == "video":
    render_video_page()

elif page == "coding":
    render_coding_page()

elif page == "music":
    render_music_page()

elif page == "reels":
    render_reels_page()

elif page == "dashboard":
    render_dashboard()

elif page == "support":
    render_support()

elif page == "premium":
    render_premium()

elif page == "redeem":
    render_redeem()

elif page == "admin":
    render_admin()

else:
    st.error("Seite nicht gefunden.")