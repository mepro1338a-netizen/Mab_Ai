import streamlit as st

from database import init_db
from ui_core import render_sidebar, load_css
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
# GLOBAL STYLE EXTRA
# =========================================================

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .block-container {
            padding-top: 2.5rem !important;
            padding-left: 4rem !important;
            padding-right: 4rem !important;
            max-width: 1500px !important;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 20% 20%, rgba(56,189,248,.16), transparent 28%),
                radial-gradient(circle at 85% 70%, rgba(99,102,241,.18), transparent 30%),
                linear-gradient(135deg, #030712 0%, #071326 45%, #081a36 100%) !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        input, textarea {
            color: white !important;
        }

        input::placeholder, textarea::placeholder {
            color: #93c5fd !important;
        }

        [data-testid="stChatInput"] {
            background: rgba(3,7,18,.96) !important;
            border-top: 1px solid rgba(56,189,248,.25) !important;
        }

        [data-testid="stChatInput"] textarea {
            background: linear-gradient(135deg, #07152e, #0f2a52) !important;
            color: white !important;
            border: 1px solid rgba(96,165,250,.55) !important;
            border-radius: 18px !important;
            box-shadow: 0 0 28px rgba(56,189,248,.18) !important;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top, rgba(56,189,248,.18), transparent 25%),
                linear-gradient(180deg, #061126 0%, #07182f 100%) !important;
            border-right: 1px solid rgba(96,165,250,.25) !important;
        }

        .stButton > button {
            border-radius: 18px !important;
            background: linear-gradient(135deg, #0f3c73, #1584d6) !important;
            color: white !important;
            border: 1px solid rgba(125,211,252,.45) !important;
            font-weight: 800 !important;
            min-height: 48px !important;
            box-shadow: 0 0 22px rgba(56,189,248,.18) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 34px rgba(56,189,248,.35) !important;
            border-color: #7dd3fc !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
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