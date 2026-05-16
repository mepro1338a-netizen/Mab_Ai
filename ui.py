import streamlit as st

from database import init_db
from ui_core import load_css, render_sidebar

from pages.auth import render_auth
from pages.home import render_home
from pages.chat import render_chat
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
# SAFE MEDIA IMPORT
# =========================================================

try:
    from pages.media import render_media
    MEDIA_IMPORT_ERROR = None
except Exception as e:
    MEDIA_IMPORT_ERROR = e

    def render_media(active_tool="reels"):
        st.error("Media Workspace konnte nicht geladen werden.")
        st.code(str(MEDIA_IMPORT_ERROR))
        st.info(
            "Prüfe pages/media.py: Dort darf NICHT `from pages.media import render_media` stehen "
            "und ganz unten muss `def render_media(...)` existieren."
        )


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
# LOCAL FALLBACK PAGE
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
# SIDEBAR
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