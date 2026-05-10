import streamlit as st


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
    st.rerun()


def render_user_card():
    st.markdown(
        f"""
        <div class="sidebar-user-card">

            <div class="sidebar-user-name">
                👤 {st.session_state.get("user", "User")}
            </div>

            <div class="sidebar-line">
                📧 {st.session_state.get("email", "")}
            </div>

            <div class="sidebar-line">
                💎 Plan: {st.session_state.get("plan", "free")}
            </div>

            <div class="sidebar-line">
                🪙 Tokens: {st.session_state.get("tokens", 0)}
            </div>

            <div class="sidebar-line">
                🛡️ Role: {st.session_state.get("role", "user")}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:

        try:
            st.image("LogoMAIN.png", use_container_width=True)
        except Exception:
            st.markdown("# MaByte")

        st.markdown(
            """
            <div class="sidebar-subtitle">
                Next Generation AI Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav("🏠 Home", "home")

        if not st.session_state.get("user"):
            nav("🔐 Login / Register", "login")
            return

        render_user_card()

        st.markdown(
            """
            <div class="sidebar-section-title">
                AI Tools
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav("💬 Memory Chat", "chat")
        nav("💻 Coding AI", "coding")
        nav("🎨 Image Generator", "image")
        nav("🎵 Music Generator", "music")
        nav("🎬 Reels Creator", "reels")
        nav("🎞️ AI Video Generator", "video")

        st.markdown(
            """
            <div class="sidebar-section-title">
                Account
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav("📊 Dashboard", "dashboard")
        nav("🎁 Redeem Code", "redeem")
        nav("🆘 Support Tickets", "support")
        nav("💎 Premium", "premium")

        if (
            st.session_state.get("role") in ["admin", "owner"]
            or int(st.session_state.get("admin_level", 0)) > 0
        ):
            st.markdown(
                """
                <div class="sidebar-section-title">
                    Admin
                </div>
                """,
                unsafe_allow_html=True,
            )

            nav("🛡️ Admin Panel", "admin")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn",
        ):
            logout()