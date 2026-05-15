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
# FORCE SIDEBAR VISIBLE
# =========================================================

def force_sidebar_css():
    st.markdown(
        """
<style>

/* Streamlit Sidebar hart sichtbar halten */
section[data-testid="stSidebar"]{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;

    min-width:285px!important;
    max-width:285px!important;
    width:285px!important;

    z-index:999999!important;

    background:#06111f!important;
}

/* Sidebar Inhalt sichtbar halten */
section[data-testid="stSidebar"] > div{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
}

/* verhindert, dass Sidebar Content verschwindet */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
}

/* Main Content korrekt neben Sidebar */
[data-testid="stAppViewContainer"]{
    overflow-x:hidden!important;
}

/* Mobile: Sidebar darf einklappen, aber Button bleibt sichtbar */
button[kind="header"],
button[data-testid="collapsedControl"]{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
    z-index:999999!important;
}

/* Header nicht über Sidebar legen */
[data-testid="stHeader"]{
    z-index:9999!important;
}

/* Falls globale CSS Sidebar versteckt */
.css-1d391kg,
.css-1lcbmhc,
.css-17eq0hr{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
}

/* Sidebar Buttons wieder hellblau */
section[data-testid="stSidebar"] .stButton > button{
    background:linear-gradient(135deg,#38bdf8,#0ea5e9)!important;
    color:#ffffff!important;
    border:none!important;
    border-radius:18px!important;
    min-height:44px!important;
    font-weight:900!important;
    box-shadow:0 12px 24px rgba(14,165,233,.22)!important;
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
# AUTOMATIONS PAGE
# =========================================================

def render_automations():
    st.title("⚙️ Automations")
    st.caption("Geplante Abläufe, Posting Flows und System Actions.")

    with st.container(border=True):
        st.subheader("Automation Center")
        st.info("Noch keine Automationen aktiv.")


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
# APP LAYOUT
# =========================================================

render_sidebar()


# =========================================================
# ROUTER
# =========================================================

page = st.session_state.get("page", "home")


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