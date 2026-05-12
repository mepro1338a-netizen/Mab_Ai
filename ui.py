import streamlit as st

from database import init_db
from ui_core import load_css, render_sidebar

from pages.auth import render_auth
from pages.home import render_home
from pages.chat import render_chat
from pages.media import render_media
from pages.football import render_football

from pages.account import (
    render_dashboard,
    render_support,
    render_premium,
    render_redeem,
)

from pages.admin import render_admin


st.set_page_config(
    page_title="MaByte",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
load_css()


defaults = {
    "page": "auth",
    "logged_in": False,
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


if not st.session_state.get("logged_in"):
    render_auth()
    st.stop()


render_sidebar()

page = st.session_state.get("page", "home")


if page == "home":
    render_home()

elif page == "chat":
    render_chat()

elif page == "football":
    render_football()

elif page == "automation_lab":
    st.title("🧪 Automation Lab")
    st.info("Automation Lab wird vorbereitet.")

elif page == "projects":
    st.title("📁 Projects")
    st.info("Projects Workspace wird vorbereitet.")

elif page == "automations":
    st.title("⚙️ Automations")
    st.info("Automations werden vorbereitet.")

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