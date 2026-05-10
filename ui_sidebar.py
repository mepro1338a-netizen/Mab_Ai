import streamlit as st


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


# =========================================================
# LOGOUT
# =========================================================

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


# =========================================================
# USER CARD
# =========================================================

def render_user_card():
    user = st.session_state.get("user", "User")
    email = st.session_state.get("email", "")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)
    role = st.session_state.get("role", "user")

    st.markdown(
        f"""
        <div class="modern-user-card">

            <div class="modern-user-top">
                <div class="modern-user-avatar">
                    👤
                </div>

                <div>
                    <div class="modern-user-name">
                        {user}
                    </div>

                    <div class="modern-user-role">
                        {role.upper()}
                    </div>
                </div>
            </div>

            <div class="modern-user-info">
                <span>📧</span>
                <span>{email}</span>
            </div>

            <div class="modern-user-info">
                <span>💎</span>
                <span>Plan: {plan.capitalize()}</span>
            </div>

            <div class="modern-user-info">
                <span>🪙</span>
                <span>{tokens:,} Tokens</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    st.markdown(
        """
        <style>

        /* =========================================
           SIDEBAR
        ========================================= */

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top,
                rgba(59,130,246,.18),
                transparent 25%),

                linear-gradient(
                    180deg,
                    #07111f 0%,
                    #08182d 100%
                ) !important;

            border-right:
                1px solid rgba(96,165,250,.20);
        }


        /* =========================================
           BUTTONS
        ========================================= */

        .stButton > button {
            width: 100%;
            min-height: 54px;

            border-radius: 18px !important;

            background:
                linear-gradient(
                    135deg,
                    #123d75 0%,
                    #1f8fff 100%
                ) !important;

            color: #ffd95e !important;

            font-size: 18px !important;
            font-weight: 900 !important;
            letter-spacing: .3px;

            border:
                1px solid rgba(125,211,252,.35) !important;

            box-shadow:
                0 0 22px rgba(59,130,246,.22);

            transition: all .18s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);

            box-shadow:
                0 0 30px rgba(56,189,248,.38);

            border-color:
                rgba(125,211,252,.7) !important;
        }


        /* =========================================
           USER CARD
        ========================================= */

        .modern-user-card {

            margin-top: 14px;
            margin-bottom: 20px;

            padding: 20px;

            border-radius: 24px;

            background:
                linear-gradient(
                    180deg,
                    rgba(12,26,48,.95),
                    rgba(10,20,38,.98)
                );

            border:
                1px solid rgba(96,165,250,.18);

            box-shadow:
                0 0 35px rgba(37,99,235,.14);

            overflow: hidden;
        }


        .modern-user-top {
            display: flex;
            align-items: center;
            gap: 14px;

            margin-bottom: 18px;
        }

        .modern-user-avatar {

            width: 58px;
            height: 58px;

            border-radius: 18px;

            display: flex;
            align-items: center;
            justify-content: center;

            font-size: 28px;

            background:
                linear-gradient(
                    135deg,
                    #1d4ed8,
                    #38bdf8
                );

            box-shadow:
                0 0 20px rgba(56,189,248,.35);
        }

        .modern-user-name {
            color: white;

            font-size: 24px;
            font-weight: 900;

            line-height: 1;
        }

        .modern-user-role {
            margin-top: 6px;

            display: inline-block;

            padding:
                4px 10px;

            border-radius: 999px;

            background:
                rgba(56,189,248,.14);

            color: #7dd3fc;

            font-size: 11px;
            font-weight: 800;

            letter-spacing: 1px;
        }


        .modern-user-info {

            display: flex;
            align-items: center;
            gap: 10px;

            margin-top: 10px;

            padding:
                12px 14px;

            border-radius: 14px;

            background:
                rgba(255,255,255,.03);

            border:
                1px solid rgba(255,255,255,.04);

            color: #dbeafe;

            font-size: 15px;
            font-weight: 700;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:

        try:
            st.image("LogoMAIN.png", width=185)
        except Exception:
            st.title("MaByte")

        st.caption("Next Generation AI Platform")

        nav("🏠 Home", "home")

        if not st.session_state.get("user"):
            nav("🔐 Login / Register", "login")
            return

        render_user_card()

        st.markdown("### AI Tools")

        nav("💬 Memory Chat", "chat")
        nav("💻 Coding AI", "coding")
        nav("🎨 Image Generator", "image")
        nav("🎵 Music AI", "music")
        nav("🎬 Reels Creator", "reels")
        nav("🎞️ AI Video", "video")

        st.markdown("### Account")

        nav("📊 Dashboard", "dashboard")
        nav("🎁 Redeem Code", "redeem")
        nav("🆘 Support Tickets", "support")
        nav("💎 Premium", "premium")

        role = st.session_state.get("role", "user")
        level = int(st.session_state.get("admin_level", 0) or 0)

        if role in ["admin", "owner"] or level > 0:
            st.markdown("### Admin")
            nav("🛡️ Admin Panel", "admin")

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn",
        ):
            logout()