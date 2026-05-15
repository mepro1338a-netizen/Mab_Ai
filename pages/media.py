import streamlit as st

from database import init_db
from ui_core import load_css, render_sidebar

from pages.auth import render_auth
from pages.home import render_home
from pages.chat import render_chat
from pages.media import render_media
from pages.football import render_football
from pages.projects import render_projects
from pages.automation_lab import render_automation_lab

from pages.premium import render_premium

from pages.account import (
    render_dashboard,
    render_support,
    render_redeem,
)

from pages.admin import render_admin


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MaByte",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# INIT
# =========================================================

init_db()
load_css()


# =========================================================
# SAFE SIDEBAR FIX
# =========================================================

def force_sidebar_css():

    st.markdown(
        """
<style>

/* Sidebar sichtbar halten */
section[data-testid="stSidebar"]{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
    z-index:999!important;
}

/* Sidebar Content sichtbar */
section[data-testid="stSidebar"] > div{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
}

/* Sidebar Toggle sichtbar */
button[data-testid="collapsedControl"]{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
}

/* Header */
[data-testid="stHeader"]{
    z-index:998!important;
}

/* Main */
[data-testid="stAppViewContainer"]{
    overflow-x:hidden!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


force_sidebar_css()


# =========================================================
# SESSION DEFAULTS
# =========================================================

DEFAULTS = {
    "page": "auth",
    "logged_in": False,
    "user": None,
    "email": "",
    "plan": "free",
    "tokens": 0,
    "role": "user",
    "admin_level": 0,
    "active_project_id": None,
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# AUTOMATIONS
# =========================================================

def render_automations():

    st.title("⚙️ Automations")

    st.caption(
        "Geplante Abläufe, Posting Flows und System Actions."
    )

    with st.container(border=True):

        st.subheader("Automation Center")

        st.info(
            "Noch keine Automationen aktiv."
        )


# =========================================================
# AUTH CHECK
# =========================================================

logged_in = bool(
    st.session_state.get("logged_in")
    and st.session_state.get("user")
)

if not logged_in:

    st.session_state.page = "auth"

    render_auth()

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

render_sidebar()


# =========================================================
# ROUTER
# =========================================================

page = st.session_state.get(
    "page",
    "home"
)


# =========================================================
# ROUTES
# =========================================================

if page == "auth":

    st.session_state.page = "home"

    st.rerun()


elif page == "home":

    render_home()


elif page == "chat":

    render_chat()


elif page == "projects":

    render_projects()


elif page == "football":

    render_football()


elif page == "automation_lab":

    render_automation_lab()


elif page == "automations":

    render_automations()


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

    st.session_state.page = "home"

    st.rerun()