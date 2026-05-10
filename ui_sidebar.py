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


def render_sidebar():
    with st.sidebar:
        try:
            st.image("LogoMAIN.png", width=130)
        except Exception:
            st.markdown("### Mabyte")

        st.markdown(
            """
            <div style="
                color:#6ea8ff;
                font-size:13px;
                margin-top:4px;
                margin-bottom:24px;
                text-align:center;
                font-weight:700;
            ">
                Next Generation AI Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav("🏠 Home", "home")

        # Nicht eingeloggt
        if not st.session_state.get("user"):
            nav("🔐 Login / Register", "login")
            return

        # Eingeloggt
        st.markdown("### AI Tools")
        nav("💬 Memory Chat", "chat")
        nav("💻 Coding AI", "coding")
        nav("🎨 Image Generator", "image")
        nav("🎵 Music Generator", "music")
        nav("🎬 Reels Creator", "reels")
        nav("🎞️ AI Video Generator", "video")

        st.markdown("### Account")
        nav("📊 Dashboard", "dashboard")
        nav("🎁 Redeem Code", "redeem")
        nav("🆘 Support Tickets", "support")
        nav("💎 Premium", "premium")

        if (
            st.session_state.get("role") in ["admin", "owner"]
            or int(st.session_state.get("admin_level", 0)) > 0
        ):
            st.markdown("### Admin")
            nav("🛡️ Admin Panel", "admin")

        st.markdown("---")

        st.markdown(
            f"""
            <div class="sidebar-user">
                <b>{st.session_state.get("user", "User")}</b><br>
                Email: {st.session_state.get("email", "")}<br>
                Plan: {st.session_state.get("plan", "free")}<br>
                Tokens: {st.session_state.get("tokens", 0)}<br>
                Role: {st.session_state.get("role", "user")}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()