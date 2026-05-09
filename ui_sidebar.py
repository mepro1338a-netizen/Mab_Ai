import streamlit as st


def is_logged_in():
    return bool(st.session_state.get("user"))


def is_admin_user():
    return (
        st.session_state.get("role") in ["supporter", "moderator", "admin", "owner"]
        or int(st.session_state.get("admin_level", 0)) > 0
    )


def nav_button(label, page, icon=""):
    if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page}"):
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
            st.image("LogoMAIN.png", width=180)
        except Exception:
            st.markdown("## 🌌 Mabyte")

        st.markdown(
            """
            <div style="color:#6ea8ff;font-size:13px;margin-bottom:20px;">
                Next Generation AI Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_button("Home", "home", "🏠")

        if not is_logged_in():
            nav_button("Login / Register", "login", "🔐")
            nav_button("Premium", "premium", "💎")
            return

        st.markdown("### AI Tools")
        nav_button("Memory Chat", "chat", "💬")
        nav_button("Coding AI", "coding", "💻")
        nav_button("Image Generator", "image", "🎨")
        nav_button("Music Generator", "music", "🎵")
        nav_button("Reels Creator", "reels", "🎞️")
        nav_button("AI Video Generator", "video", "🎬")

        st.markdown("### Account")
        nav_button("Dashboard", "dashboard", "📊")
        nav_button("Redeem Code", "redeem", "🎁")
        nav_button("Support Tickets", "support", "🆘")
        nav_button("Premium", "premium", "💳")

        if is_admin_user():
            st.markdown("### Admin")
            nav_button("Admin Panel", "admin", "🛡️")

        st.markdown("---")

        st.markdown(
            f"""
            <div class="sidebar-user">
                <b>{st.session_state.get("user")}</b><br>
                Plan: {st.session_state.get("plan", "free")}<br>
                Tokens: {st.session_state.get("tokens", 0)}<br>
                Role: {st.session_state.get("role", "user")}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()