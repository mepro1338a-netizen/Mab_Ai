import streamlit as st


def load_css():
    st.markdown(
        """
<style>

#MainMenu,
footer,
header,
[data-testid="stToolbar"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.20), transparent 28%),
        radial-gradient(circle at bottom right, rgba(37,99,235,.18), transparent 30%),
        linear-gradient(135deg, #020617 0%, #071427 45%, #0f172a 100%) !important;
}

.main .block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(2,6,23,.98), rgba(7,20,42,.98)) !important;
    border-right: 1px solid rgba(125,211,252,.14);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton > button {
    width: 100%;
    min-height: 50px;
    border-radius: 18px !important;
    border: 1px solid rgba(125,211,252,.30) !important;
    background: linear-gradient(135deg, #1d4ed8, #38bdf8) !important;
    color: white !important;
    font-weight: 900 !important;
    transition: .2s ease;
    box-shadow: 0 0 25px rgba(56,189,248,.20);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(56,189,248,.35);
}

.stTextInput input,
.stNumberInput input {
    background: rgba(2,6,23,.88) !important;
    border: 1px solid rgba(125,211,252,.30) !important;
    color: white !important;
    border-radius: 18px !important;
    min-height: 52px !important;
    font-weight: 700 !important;
}

.stTextInput input::placeholder {
    color: #bfdbfe !important;
    opacity: 1 !important;
}

h1, h2, h3 {
    color: white !important;
    font-weight: 950 !important;
}

p, label, span {
    color: #dbeafe !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


def sync_session_user(user):
    st.session_state.logged_in = True
    st.session_state.user = user.get("username")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = user.get("tokens", 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = user.get("admin_level", 0)


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "auth"
    st.rerun()


def render_sidebar():
    with st.sidebar:

        st.markdown("# 🚀 MaByte")

        st.caption("Next Generation AI Platform")

        st.divider()

        st.markdown(f"### 👤 {st.session_state.user}")

        st.caption(f"💎 Plan: {st.session_state.plan}")

        st.divider()

        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.rerun()

        if st.button("💬 Chat"):
            st.session_state.page = "chat"
            st.rerun()

        if st.button("💻 Coding AI"):
            st.session_state.page = "coding"
            st.rerun()

        if st.button("🎨 Bilder"):
            st.session_state.page = "image"
            st.rerun()

        if st.button("🎵 Musik"):
            st.session_state.page = "music"
            st.rerun()

        if st.button("🎬 Reels"):
            st.session_state.page = "reels"
            st.rerun()

        st.divider()

        if st.button("🚪 Logout"):
            logout()