import streamlit as st


# =========================================================
# GLOBAL CSS
# =========================================================

def load_css():
    st.markdown(
        """
<style>

#MainMenu,
header,
footer,
[data-testid="stToolbar"]{
    display:none!important;
}

.stApp{
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(37,99,235,.16), transparent 30%),
        linear-gradient(135deg,#020617 0%,#071427 48%,#0f172a 100%)!important;
}

.main .block-container{
    max-width:1450px;
    padding-top:2rem;
    padding-bottom:4rem;
}

[data-testid="stSidebar"]{
    background:
        linear-gradient(
            180deg,
            rgba(2,6,23,.98),
            rgba(7,20,42,.98)
        )!important;

    border-right:
        1px solid rgba(125,211,252,.14);
}

[data-testid="stSidebar"] *{
    color:white!important;
}

.stButton > button{
    width:100%;
    min-height:48px;
    border-radius:16px!important;
    border:
        1px solid rgba(125,211,252,.28)!important;

    background:
        linear-gradient(
            135deg,
            #1d4ed8,
            #38bdf8
        )!important;

    color:white!important;
    font-weight:900!important;

    box-shadow:
        0 0 22px rgba(56,189,248,.18);

    transition:.2s ease;
}

.stButton > button:hover{
    transform:translateY(-2px);

    box-shadow:
        0 0 30px rgba(56,189,248,.30);
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"]{
    background:rgba(2,6,23,.88)!important;

    border:
        1px solid rgba(125,211,252,.30)!important;

    color:white!important;

    -webkit-text-fill-color:white!important;

    border-radius:16px!important;

    font-weight:700!important;
}

h1,h2,h3{
    color:white!important;
    font-weight:950!important;
}

p,label,span{
    color:#dbeafe!important;
}

[data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:24px!important;

    border:
        1px solid rgba(125,211,252,.16)!important;

    background:
        linear-gradient(
            145deg,
            rgba(5,15,35,.72),
            rgba(9,35,75,.45)
        )!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# AUTH
# =========================================================

def is_logged_in():
    return bool(
        st.session_state.get("logged_in")
        and st.session_state.get("user")
    )


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

    st.session_state.tokens = int(
        user.get("tokens", 0) or 0
    )

    st.session_state.role = user.get("role", "user")

    st.session_state.admin_level = int(
        user.get("admin_level", 0) or 0
    )


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


# =========================================================
# NAVIGATION
# =========================================================

def nav(label, page):

    if st.button(
        label,
        use_container_width=True,
        key=f"nav_{page}",
    ):
        st.session_state.page = page
        st.rerun()


def section(title):
    st.caption(title)


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        st.markdown("## 🚀 MaByte OS")

        st.caption(
            "One AI system. Infinite workflows."
        )

        st.divider()

        st.markdown(
            f"### 👤 {st.session_state.get('user', '')}"
        )

        st.caption(
            f"💎 Plan: {st.session_state.get('plan', 'free')}"
        )

        st.caption(
            f"🪙 Tokens: {st.session_state.get('tokens', 0)}"
        )

        st.divider()

        # =====================================================
        # CORE
        # =====================================================

        section("CORE")

        nav("🏠 Mission Control", "home")

        nav("🧠 AI Assistant", "chat")

        nav("📁 Projects", "projects")

        nav("⚙️ Automations", "automations")

        st.divider()

        # =====================================================
        # WORKSPACES
        # =====================================================

        section("WORKSPACES")

        nav(
            "🎨 Creative Workspace",
            "image",
        )

        nav(
            "📣 Content Engine",
            "reels",
        )

        nav(
            "💻 Developer OS",
            "coding",
        )

        nav(
            "🎬 Media Studio",
            "video",
        )

        nav(
            "🎵 Music Studio",
            "music",
        )

        nav(
            "⚽ Football Intelligence",
            "football",
        )

        nav(
            "🧪 Automation Lab",
            "automation_lab",
        )

        st.divider()

        # =====================================================
        # SYSTEM
        # =====================================================

        section("SYSTEM")

        nav("📊 Dashboard", "dashboard")

        nav("🎁 Redeem", "redeem")

        nav("🆘 Support", "support")

        nav("💎 Billing", "premium")

        role = st.session_state.get(
            "role",
            "user",
        )

        level = int(
            st.session_state.get(
                "admin_level",
                0,
            ) or 0
        )

        if role in ["admin", "owner"] or level > 0:

            nav(
                "🛡️ Owner Command",
                "admin",
            )

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn",
        ):
            logout()