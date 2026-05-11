import streamlit as st

from database import init_db
from ui_core import load_css, render_sidebar

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


st.set_page_config(
    page_title="Mabyte",
    page_icon="Logo24mp.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
load_css()

defaults = {
    "page": "login",
    "user": None,
    "email": "",
    "plan": "free",
    "tokens": 0,
    "role": "user",
    "admin_level": 0,
    "logged_in": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


logged_in = bool(st.session_state.get("user"))

if not logged_in:
    st.session_state.page = "login"
    render_auth()
    st.stop()

render_sidebar()

page = st.session_state.get("page", "home")

if page == "home":
    render_home()
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