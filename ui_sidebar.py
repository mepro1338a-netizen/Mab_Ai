import streamlit as st


def nav_button(label, page):

    if st.button(label, use_container_width=True):
        st.session_state.page = page
        st.rerun()


def render_sidebar():

    with st.sidebar:

        st.image("Logo.png", width=180)

        st.markdown("---")

        nav_button("🏠 Home", "home")

        if st.session_state.user:

            nav_button("💬 Chat", "chat")
            nav_button("🖼️ Images", "image")
            nav_button("🎥 Videos", "video")
            nav_button("🎵 Music", "music")
            nav_button("🎬 Reels", "reels")

            st.markdown("---")

            nav_button("👤 Dashboard", "dashboard")
            nav_button("🎟️ Redeem", "redeem")
            nav_button("📨 Support", "support")
            nav_button("💎 Premium", "premium")

            if st.session_state.role == "admin":
                st.markdown("---")
                nav_button("🛡️ Admin", "admin")

            st.markdown("---")

            st.markdown(
                f"""
                <div class="sidebar-user">
                    <b>{st.session_state.user}</b><br>
                    Plan: {st.session_state.plan}<br>
                    Tokens: {st.session_state.tokens}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Logout", use_container_width=True):

                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                st.rerun()

        else:

            nav_button("🔐 Login", "login")