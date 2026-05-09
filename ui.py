import streamlit as st
from PIL import Image

from database import init_db
from ui_styles import load_css
from ui_sidebar import render_sidebar

from pages.home import render_home
from pages.auth import render_auth
from pages.chat import render_chat
from pages.media import render_media

from pages.account import (
    render_dashboard,
    render_support,
    render_premium,
    render_redeem,
)

from pages.admin import render_admin


# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="Mabyte",
    page_icon="Logo24mp.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# INIT
# =========================================================

init_db()
load_css()


# =========================================================
# SESSION DEFAULTS
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

page = st.session_state.get("page", "home")


if page == "home":
    render_home()

elif page == "login":
    render_auth()

elif page == "chat":
    render_chat()

elif page in ["image", "video", "music", "reels", "coding", "media"]:
    render_media()

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
    render_home()