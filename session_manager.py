import streamlit as st
from datetime import datetime, timedelta

SESSION_TIMEOUT_MINUTES = 60


def init_session():
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False


def update_activity():
    st.session_state.last_activity = datetime.now()


def is_session_expired():
    if "last_activity" not in st.session_state:
        return False

    return datetime.now() - st.session_state.last_activity > timedelta(
        minutes=SESSION_TIMEOUT_MINUTES
    )


def logout():
    keys = list(st.session_state.keys())

    for key in keys:
        del st.session_state[key]

    st.rerun()