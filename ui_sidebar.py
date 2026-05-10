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
    st.session_state.logged_in = False
    st.rerun()


def render_user_card():
    user = st.session_state.get("user", "User")
    email = st.session_state.get("email", "")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)
    role = st.session_state.get("role", "user")

    with st.container(border=True):
        st.subheader(f"👤 {user}")
        st.write(f"📧 {email}")
        st.write(f"💎 Plan: {plan}")
        st.write(f"🪙 Tokens: {tokens}")
        st.write(f"🛡️ Role: {role}")


def render_sidebar():
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

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()