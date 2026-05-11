import streamlit as st


def open_page(page):
    st.session_state.page = page
    st.rerun()


def tool_button(icon, title, page):
    st.button(
        f"{icon} {title}",
        use_container_width=True,
        key=page,
        on_click=open_page,
        args=(page,),
    )


def render_home():

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)

    st.title("🚀 MaByte Control Center")
    st.caption("Next Generation AI Workspace")

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("👤 User", user)

    with c2:
        st.metric("💎 Plan", plan)

    with c3:
        st.metric("🪙 Tokens", tokens)

    st.divider()

    st.subheader("AI Tools")

    a, b, c = st.columns(3)

    with a:
        tool_button("💬", "Memory Chat", "chat")

    with b:
        tool_button("💻", "Coding AI", "coding")

    with c:
        tool_button("🎨", "Image AI", "image")

    d, e, f = st.columns(3)

    with d:
        tool_button("🎵", "Music AI", "music")

    with e:
        tool_button("🎬", "Reels Creator", "reels")

    with f:
        tool_button("🎞️", "Video AI", "video")

    st.divider()

    with st.container(border=True):
        st.subheader("Willkommen zurück")
        st.write(
            "Nutze MaByte für Chat, Coding, Content Creation, "
            "Automation und moderne AI Workflows."
        )

        st.success("✅ System verbunden")
        st.success("✅ Login aktiv")
        st.success("✅ Dashboard geladen")