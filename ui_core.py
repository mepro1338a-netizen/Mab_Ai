import streamlit as st


def load_css():
    st.markdown(
        """
<style>

#MainMenu,
footer,
header,


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
.stTextArea textarea,
.stNumberInput input,
textarea {
    background: rgba(2,6,23,.88) !important;
    border: 1px solid rgba(125,211,252,.30) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    border-radius: 18px !important;
    min-height: 52px !important;
    font-weight: 700 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
textarea::placeholder {
    color: #bfdbfe !important;
    -webkit-text-fill-color: #bfdbfe !important;
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


def is_logged_in():
    return bool(st.session_state.get("logged_in") and st.session_state.get("user"))


def require_login():
    if not is_logged_in():
        st.session_state.page = "auth"
        st.rerun()


def sync_session_user(user):
    if not user:
        return

    st.session_state.logged_in = True
    st.session_state.user = user.get("username")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = int(user.get("tokens", 0) or 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = int(user.get("admin_level", 0) or 0)


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.email = ""
    st.session_state.plan = "free"
    st.session_state.tokens = 0
    st.session_state.role = "user"
    st.session_state.admin_level = 0
    st.session_state.page = "auth"
    st.rerun()


def nav(label, page):
    if st.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.page = page
        st.rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown("# 🚀 MaByte")
        st.caption("Next Generation AI Platform")

        st.divider()

        st.markdown(f"### 👤 {st.session_state.get('user', '')}")
        st.caption(f"💎 Plan: {st.session_state.get('plan', 'free')}")
        st.caption(f"🪙 Tokens: {st.session_state.get('tokens', 0)}")

        st.divider()

        nav("🏠 Home", "home")
        nav("💬 Chat", "chat")
        nav("💻 Coding AI", "coding")
        nav("🎨 Bilder", "image")
        nav("🎵 Musik", "music")
        nav("🎬 Reels", "reels")
        nav("🎞️ Video", "video")

        st.divider()

        nav("📊 Dashboard", "dashboard")
        nav("🎁 Redeem", "redeem")
        nav("🆘 Support", "support")
        nav("💎 Premium", "premium")

        role = st.session_state.get("role", "user")
        level = int(st.session_state.get("admin_level", 0) or 0)

        if role in ["admin", "owner"] or level > 0:
            st.divider()
            nav("🛡️ Admin", "admin")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()