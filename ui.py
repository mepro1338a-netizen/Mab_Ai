import streamlit as st

from ui_core import load_global_styles

st.set_page_config(
    page_title="MaByte",
    page_icon="🚀",
    layout="wide",
)

load_global_styles()

# Nicht eingeloggt → direkt Login
if not st.session_state.get("logged_in"):
    st.switch_page("pages/auth.py")

# Eingeloggt → normale App
st.sidebar.title("🚀 MaByte")

st.sidebar.success(
    f"Angemeldet als: {st.session_state.get('user')}"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Chat",
    ]
)

if page == "Home":
    st.switch_page("pages/home.py")

if page == "Chat":
    st.switch_page("pages/chat.py")