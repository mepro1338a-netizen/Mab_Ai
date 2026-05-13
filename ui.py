import streamlit as st

from database import init_db
from ui_core import load_css, render_sidebar
from pages.automation_lab import render_automation_lab

from pages.auth import render_auth
from pages.home import render_home
from pages.chat import render_chat
from pages.media import render_media
from pages.football import render_football
from pages.projects import render_projects

from pages.account import (
    render_dashboard,
    render_support,
    render_premium,
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
# HELPERS
# =========================================================

def go(page):
    st.session_state.page = page
    st.rerun()


def render_mobile_nav():
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            if st.button("🏠", key="mobile_home", use_container_width=True):
                go("home")

        with c2:
            if st.button("🧠", key="mobile_chat", use_container_width=True):
                go("chat")

        with c3:
            if st.button("📁", key="mobile_projects", use_container_width=True):
                go("projects")

        with c4:
            if st.button("⚽", key="mobile_football", use_container_width=True):
                go("football")

        with c5:
            if st.button("💎", key="mobile_premium", use_container_width=True):
                go("premium")


def render_automation_lab():
    st.title("🧪 Automation Lab")
    st.caption("AI Agents, Workflows und intelligente Automationen.")

    with st.container(border=True):
        st.subheader("Coming soon")
        st.write("Hier entstehen später Agent-Flows, Trigger, Automations und Cross-Workspace Pipelines.")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.success("Agent Engine vorbereitet")

        with c2:
            st.info("Workflow Router bereit")

        with c3:
            st.warning("API Connectors folgen")


def render_automations():
    st.title("⚙️ Automations")
    st.caption("Geplante Abläufe, Posting Flows und System Actions.")

    with st.container(border=True):
        st.subheader("Automation Center")
        st.write("Hier verwaltest du später deine geplanten Automationen.")
        st.info("Noch keine Automationen aktiv.")


# =========================================================
# AUTH GATE
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
# APP SHELL
# =========================================================

render_sidebar()
render_mobile_nav()


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