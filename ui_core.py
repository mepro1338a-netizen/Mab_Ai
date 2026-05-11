import streamlit as st


def load_css():
    st.markdown(
        """
<style>

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 15% 10%, rgba(56,189,248,.18), transparent 28%),
        radial-gradient(circle at 85% 25%, rgba(37,99,235,.16), transparent 30%),
        radial-gradient(circle at 70% 90%, rgba(14,165,233,.12), transparent 30%),
        linear-gradient(135deg, #020617 0%, #061224 48%, #081a33 100%) !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1420px;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.18), transparent 24%),
        linear-gradient(180deg, rgba(2,6,23,.98), rgba(7,18,36,.98)) !important;
    border-right: 1px solid rgba(96,165,250,.18);
}

[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start;
    text-align: left;
    min-height: 48px;
    border-radius: 16px !important;
    background: linear-gradient(135deg, rgba(15,61,115,.88), rgba(20,132,214,.88)) !important;
    color: #ffe27a !important;
    border: 1px solid rgba(125,211,252,.22) !important;
    font-weight: 900 !important;
    box-shadow: 0 0 18px rgba(56,189,248,.12);
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateX(4px);
    border-color: rgba(125,211,252,.58) !important;
    box-shadow: 0 0 28px rgba(56,189,248,.26);
}

.stButton > button {
    width: 100%;
    border-radius: 18px !important;
    min-height: 50px;
    background: linear-gradient(135deg, #0f3d73, #1d9bf0) !important;
    border: 1px solid rgba(125,211,252,.30) !important;
    color: #ffe27a !important;
    font-size: 16px !important;
    font-weight: 900 !important;
    letter-spacing: .2px;
    box-shadow: 0 0 24px rgba(56,189,248,.16);
    transition: all .18s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 34px rgba(56,189,248,.30);
    border-color: rgba(125,211,252,.65) !important;
}

[data-testid="metric-container"] {
    background:
        linear-gradient(135deg, rgba(15,23,42,.92), rgba(15,42,82,.72));
    border: 1px solid rgba(96,165,250,.20);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 0 30px rgba(56,189,248,.08);
}

[data-testid="metric-container"] label {
    color: #bfdbfe !important;
    font-weight: 800 !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 900 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 24px !important;
    border: 1px solid rgba(96,165,250,.18) !important;
    background:
        linear-gradient(135deg, rgba(15,23,42,.72), rgba(15,42,82,.45)) !important;
    box-shadow: 0 0 28px rgba(56,189,248,.07);
}

.stTextInput input,
.stTextArea textarea,
textarea,
input {
    background: rgba(7,18,36,.94) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid rgba(96,165,250,.35) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 20px rgba(56,189,248,.10);
    font-weight: 700 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
textarea::placeholder,
input::placeholder {
    color: #bfdbfe !important;
    -webkit-text-fill-color: #bfdbfe !important;
    opacity: 1 !important;
}

.stSelectbox div[data-baseweb="select"] {
    background: rgba(7,18,36,.94) !important;
    border: 1px solid rgba(96,165,250,.35) !important;
    border-radius: 18px !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}

.stSelectbox * {
    color: #ffffff !important;
}

[data-testid="stFileUploader"] {
    background:
        linear-gradient(135deg, rgba(15,23,42,.75), rgba(15,42,82,.45));
    border: 1px dashed rgba(125,211,252,.35);
    border-radius: 22px;
    padding: 14px;
}

[data-testid="stFileUploader"] * {
    color: #dbeafe !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(96,165,250,.14);
    border-radius: 15px;
    margin-right: 8px;
    padding: 10px 18px;
    color: white !important;
    font-weight: 900;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1d4ed8, #38bdf8) !important;
    color: #ffe27a !important;
    box-shadow: 0 0 22px rgba(56,189,248,.24);
}

[data-testid="stChatMessage"] {
    background:
        linear-gradient(135deg, rgba(15,23,42,.78), rgba(15,42,82,.42));
    border: 1px solid rgba(96,165,250,.14);
    border-radius: 22px;
    padding: 12px;
    margin-bottom: 14px;
}

[data-testid="stChatMessage"] * {
    color: #ffffff !important;
}

.stAlert {
    border-radius: 18px !important;
    border: 1px solid rgba(96,165,250,.20) !important;
}

.stDataFrame {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid rgba(96,165,250,.16);
}

h1 {
    color: #ffffff !important;
    font-weight: 950 !important;
    letter-spacing: -.8px;
    font-size: 3rem !important;
}

h2, h3 {
    color: #ffffff !important;
    font-weight: 900 !important;
    letter-spacing: -.4px;
}

p, span, label, .stMarkdown {
    color: #dbeafe !important;
}

hr {
    border-color: rgba(96,165,250,.14) !important;
}

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #1d4ed8, #38bdf8);
    border-radius: 999px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


def is_logged_in():
    return bool(st.session_state.get("user"))


def require_login():
    if not is_logged_in():
        st.warning("Bitte zuerst einloggen.")
        st.session_state.page = "login"
        st.stop()


def sync_session_user(user):
    if not user:
        return

    st.session_state.user = user.get("username")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = int(user.get("tokens", 0) or 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.admin_level = int(user.get("admin_level", 0) or 0)
    st.session_state.logged_in = True


def nav(label, page):
    if st.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.page = page
        st.rerun()


def logout():
    st.session_state.page = "home"
    st.session_state.user = None
    st.session_state.email = ""
    st.session_state.plan = "free"
    st.session_state.tokens = 0
    st.session_state.role = "user"
    st.session_state.admin_level = 0
    st.session_state.logged_in = False
    st.rerun()


def render_user_card():
    user = st.session_state.get("user", "User")
    email = st.session_state.get("email", "")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)
    role = st.session_state.get("role", "user")

    with st.container(border=True):
        st.markdown(f"### 👤 {user}")
        st.caption(email)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Plan", plan)
        with c2:
            st.metric("Tokens", tokens)
        st.caption(f"Role: {role}")


def render_sidebar():
    with st.sidebar:
        try:
            st.image("LogoMAIN.png", width=180)
        except Exception:
            st.markdown("## MaByte")

        st.caption("Next Generation AI Platform")

        nav("🏠 Home", "home")

        if not st.session_state.get("user"):
            nav("🔐 Login / Register", "login")
            return

        render_user_card()

        st.caption("AI Tools")
        nav("💬 Memory Chat", "chat")
        nav("💻 Coding AI", "coding")
        nav("🎨 Image Generator", "image")
        nav("🎵 Music AI", "music")
        nav("🎬 Reels Creator", "reels")
        nav("🎞️ AI Video", "video")

        st.caption("Account")
        nav("📊 Dashboard", "dashboard")
        nav("🎁 Redeem Code", "redeem")
        nav("🆘 Support Tickets", "support")
        nav("💎 Premium", "premium")

        role = st.session_state.get("role", "user")
        level = int(st.session_state.get("admin_level", 0) or 0)

        if role in ["admin", "owner"] or level > 0:
            st.caption("Admin")
            nav("🛡️ Admin Panel", "admin")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()