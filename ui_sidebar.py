import streamlit as st


# =========================================
# NAVIGATION BUTTON
# =========================================

def nav(label, page):
    if st.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.page = page
        st.rerun()


# =========================================
# LOGOUT
# =========================================

def logout():
    st.session_state.page = "home"
    st.session_state.user = None
    st.session_state.email = ""
    st.session_state.plan = "free"
    st.session_state.tokens = 0
    st.session_state.role = "user"
    st.session_state.admin_level = 0
    st.rerun()


# =========================================
# SIDEBAR
# =========================================

def render_sidebar():

    with st.sidebar:

        # =========================================
        # LOGO
        # =========================================

        try:
            st.image("LogoMAIN.png", width=140)
        except Exception:
            st.markdown("## Mabyte")

        st.markdown(
            """
            <div style="
                color:#6ea8ff;
                font-size:13px;
                margin-top:6px;
                margin-bottom:24px;
                text-align:center;
                font-weight:700;
            ">
                Next Generation AI Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        # =========================================
        # HOME
        # =========================================

        nav("🏠 Home", "home")

        # =========================================
        # NOT LOGGED IN
        # =========================================

        if not st.session_state.get("user"):

            nav("🔐 Login / Register", "login")

            return

        # =========================================
        # AI TOOLS
        # =========================================

        st.markdown("### AI Tools")

        nav("💬 Memory Chat", "chat")

        nav("💻 Coding AI", "coding")

        nav("🎨 Image Generator", "image")

        nav("🎵 Music Generator", "music")

        nav("🎬 Reels Creator", "reels")

        nav("🎞️ AI Video Generator", "video")

        # =========================================
        # ACCOUNT
        # =========================================

        st.markdown("### Account")

        nav("📊 Dashboard", "dashboard")

        nav("🎁 Redeem Code", "redeem")

        nav("🆘 Support Tickets", "support")

        nav("💎 Premium", "premium")

        # =========================================
        # ADMIN
        # =========================================

        if (
            st.session_state.get("role") in ["admin", "owner"]
            or int(st.session_state.get("admin_level", 0)) > 0
        ):

            st.markdown("### Admin")

            nav("🛡️ Admin Panel", "admin")

        # =========================================
        # USER CARD
        # =========================================

        st.markdown("---")

        st.markdown(
            f"""
            <div style="
                background: rgba(20,25,50,0.96);
                border: 1px solid rgba(90,140,255,0.25);
                border-radius: 16px;
                padding: 14px;
                margin-top: 12px;
                color: white;
                font-size: 14px;
                line-height: 1.7;
            ">

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#6ea8ff;
                    margin-bottom:8px;
                ">
                    👤 {st.session_state.get("user", "User")}
                </div>

                <div>📧 {st.session_state.get("email", "")}</div>

                <div>💎 Plan: {st.session_state.get("plan", "free")}</div>

                <div>🪙 Tokens: {st.session_state.get("tokens", 0)}</div>

                <div>🛡️ Role: {st.session_state.get("role", "user")}</div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # =========================================
        # LOGOUT
        # =========================================

        st.markdown("")

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn"
        ):
            logout()