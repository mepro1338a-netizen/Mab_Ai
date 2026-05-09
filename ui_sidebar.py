import streamlit as st

from database import get_user


def sync_user(username):
    user = get_user(username)
    if user:
        st.session_state.user = user["username"]
        st.session_state.email = user.get("email", "")
        st.session_state.plan = user["plan"]
        st.session_state.tokens = user["tokens"]
        st.session_state.role = user["role"]
        st.session_state.admin_level = user["admin_level"]


def is_logged_in():
    return bool(st.session_state.get("user"))


def is_admin():
    return (
        st.session_state.get("role") in ["supporter", "moderator", "admin", "owner"]
        or int(st.session_state.get("admin_level", 0)) > 0
    )


def plan_rank(plan):
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


def can_use(required_plan):
    return plan_rank(st.session_state.get("plan", "free")) >= plan_rank(required_plan) or is_admin()


def nav_button(label, page, required_plan="free"):
    locked = is_logged_in() and not can_use(required_plan)
    text = f"🔒 {label}" if locked else label

    if st.button(text, use_container_width=True, key=f"nav_{page}_{required_plan}"):
        if not is_logged_in() and page not in ["home", "premium", "login"]:
            st.session_state.page = "login"
        elif locked:
            st.session_state.page = "premium"
        else:
            st.session_state.page = page
        st.rerun()


def logout():
    st.session_state.user = None
    st.session_state.email = ""
    st.session_state.plan = "free"
    st.session_state.tokens = 0
    st.session_state.role = "user"
    st.session_state.admin_level = 0
    st.session_state.page = "home"
    st.rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown("## ⚡ MAB.AI")

        if is_logged_in():
            st.markdown(
                f"""
                <div class="sidebar-card">
                    <h3>👤 {st.session_state.user}</h3>
                    <p>⭐ Plan: <b>{st.session_state.plan}</b></p>
                    <p>🪙 Tokens: <b>{st.session_state.tokens}</b></p>
                    <p>🛡️ Role: <b>{st.session_state.role}</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚪 Logout", key="logout_btn"):
                logout()
        else:
            if st.button("🔐 Login / Register", key="login_register_btn"):
                st.session_state.page = "login"
                st.rerun()

        st.markdown("---")

        nav_button("🏠 Home", "home")
        nav_button("💬 Memory Chat", "chat", "free")
        nav_button("💻 Coding AI", "coding", "pro")
        nav_button("🎨 Image AI", "image", "pro")
        nav_button("🎵 Music AI", "music", "pro")
        nav_button("🎞️ Reels Creator", "reels", "pro")
        nav_button("🎬 Video AI", "video", "grand")

        st.markdown("### Account")
        nav_button("📊 Dashboard", "dashboard")
        nav_button("🎁 Redeem Code", "redeem")
        nav_button("🆘 Support", "support")
        nav_button("💳 Premium", "premium")

        if is_admin():
            st.markdown("### Admin")
            nav_button("🛡️ Admin Panel", "admin")