import streamlit as st


def load_css():
    st.markdown(
        """
<style>

#MainMenu,
header,
footer,
[data-testid="stToolbar"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,.22), transparent 28%),
        radial-gradient(circle at bottom right, rgba(147,51,234,.18), transparent 30%),
        linear-gradient(135deg, #020617 0%, #061225 45%, #020617 100%) !important;
}

.main .block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 4rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(2,6,23,.98), rgba(3,12,31,.98)) !important;
    border-right: 1px solid rgba(96,165,250,.18);
    box-shadow: 12px 0 40px rgba(0,0,0,.25);
}

[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
}

[data-testid="stSidebar"] * {
    color: #eaf2ff !important;
}

[data-testid="stSidebar"] .stCaption {
    color: #93a4bd !important;
}

/* BUTTONS */
.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 14px !important;
    border: 1px solid rgba(96,165,250,.22) !important;
    background:
        linear-gradient(135deg, rgba(15,23,42,.92), rgba(15,35,70,.72)) !important;
    color: #dbeafe !important;
    font-weight: 850 !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.02);
    transition: .18s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(56,189,248,.6) !important;
    background:
        linear-gradient(135deg, rgba(29,78,216,.92), rgba(56,189,248,.78)) !important;
    box-shadow: 0 0 26px rgba(56,189,248,.24);
}

/* INPUTS */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: rgba(2,6,23,.75) !important;
    border: 1px solid rgba(96,165,250,.28) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    border-radius: 14px !important;
    min-height: 48px !important;
    font-weight: 700 !important;
}

/* TITLES */
h1, h2, h3 {
    color: white !important;
    font-weight: 950 !important;
    letter-spacing: -0.03em;
}

p, label, span {
    color: #dbeafe !important;
}

/* CARDS */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 22px !important;
    border: 1px solid rgba(96,165,250,.16) !important;
    background:
        linear-gradient(145deg, rgba(8,19,45,.84), rgba(7,27,58,.58)) !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,.22),
        inset 0 1px 0 rgba(255,255,255,.04);
}

/* METRICS */
[data-testid="stMetric"] {
    background: transparent !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 950 !important;
}

[data-testid="stMetricLabel"] {
    color: #93c5fd !important;
}

/* DATAFRAMES */
[data-testid="stDataFrame"] {
    border-radius: 18px !important;
    overflow: hidden;
}

/* MOBILE NAV ICON ROW */
div[data-testid="column"] .stButton > button {
    min-height: 42px;
}

/* SIDEBAR CUSTOM HTML */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 4px 0 18px 0;
}

.sidebar-logo {
    width: 38px;
    height: 38px;
    border-radius: 14px;
    background: linear-gradient(135deg, #2563eb, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 26px rgba(59,130,246,.35);
}

.sidebar-title {
    font-size: 22px;
    font-weight: 950;
    color: white;
    line-height: 1;
}

.sidebar-sub {
    font-size: 12px;
    color: #93a4bd;
    margin-top: 4px;
}

.sidebar-user-card {
    border: 1px solid rgba(96,165,250,.18);
    background:
        linear-gradient(145deg, rgba(15,23,42,.88), rgba(30,41,90,.55));
    border-radius: 20px;
    padding: 16px;
    margin: 14px 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
}

.sidebar-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563eb, #9333ea);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 950;
    margin-right: 10px;
}

.sidebar-user-name {
    font-size: 15px;
    font-weight: 900;
    color: white;
}

.sidebar-plan {
    display: inline-block;
    margin-top: 10px;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(147,51,234,.25);
    border: 1px solid rgba(168,85,247,.28);
    color: #e9d5ff;
    font-weight: 800;
    font-size: 12px;
}

.sidebar-token-card {
    border: 1px solid rgba(56,189,248,.22);
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.22), transparent 35%),
        linear-gradient(145deg, rgba(15,23,42,.92), rgba(30,41,120,.58));
    border-radius: 20px;
    padding: 16px;
    margin-top: 14px;
}

.sidebar-token-value {
    font-size: 28px;
    font-weight: 950;
    color: white;
}

.sidebar-token-label {
    color: #bfdbfe;
    font-size: 13px;
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
    st.session_state.active_project_id = None
    st.session_state.page = "auth"
    st.rerun()


def nav(label, page):
    if st.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.page = page
        st.rerun()


def section(title):
    st.caption(title)


def render_sidebar():
    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    initials = str(user[:2]).upper() if user else "MB"

    with st.sidebar:
        st.markdown(
            f"""
<div class="sidebar-brand">
    <div class="sidebar-logo">🚀</div>
    <div>
        <div class="sidebar-title">MaByte</div>
        <div class="sidebar-sub">AI Operating System</div>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        section("CORE")
        nav("🏠 Mission Control", "home")
        nav("🧠 AI Assistant", "chat")
        nav("📁 Projects", "projects")
        nav("⚙️ Automations", "automations")

        st.divider()

        section("WORKSPACES")
        nav("🎨 Creative Workspace", "image")
        nav("📣 Content Engine", "reels")
        nav("💻 Developer OS", "coding")
        nav("🎬 Media Studio", "video")
        nav("🎵 Music Studio", "music")
        nav("⚽ Football Intelligence", "football")
        nav("🧪 Automation Lab", "automation_lab")

        st.divider()

        section("SYSTEM")
        nav("📊 Dashboard", "dashboard")
        nav("💎 Premium", "premium")
        nav("🎁 Redeem", "redeem")
        nav("🆘 Support", "support")

        role = st.session_state.get("role", "user")
        level = int(st.session_state.get("admin_level", 0) or 0)

        if role in ["admin", "owner"] or level > 0:
            nav("🛡️ Admin Panel", "admin")

        st.divider()

        st.markdown(
            f"""
<div class="sidebar-user-card">
    <div>
        <span class="sidebar-avatar">{initials}</span>
        <span class="sidebar-user-name">{user}</span>
    </div>
    <div class="sidebar-plan">{plan.title()} Plan</div>
</div>

<div class="sidebar-token-card">
    <div class="sidebar-token-value">{tokens:,}</div>
    <div class="sidebar-token-label">Tokens verfügbar</div>
</div>
            """.replace(",", "."),
            unsafe_allow_html=True,
        )

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()