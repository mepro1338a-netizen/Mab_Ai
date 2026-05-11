import streamlit as st


def open_page(page):
    st.session_state.page = page
    st.rerun()


def tool_card(title, text, emoji, page):
    with st.container(border=True):
        st.markdown(f"## {emoji} {title}")
        st.write(text)

        if st.button(
            f"Öffnen",
            use_container_width=True,
            key=f"open_{page}",
        ):
            open_page(page)


def render_home():
    user = st.session_state.get("user", "User")
    tokens = st.session_state.get("tokens", 0)
    plan = st.session_state.get("plan", "free")

    st.title("🚀 Willkommen bei MaByte")
    st.caption("Dein AI Workspace für Chat, Coding, Media, Musik, Reels und Automation.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("👤 Account", user)

    with c2:
        st.metric("🪙 Tokens", tokens)

    with c3:
        st.metric("💎 Plan", plan)

    st.divider()

    st.subheader("AI Tools")

    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        tool_card(
            "Memory Chat",
            "Chatte mit MaByte und speichere deinen Verlauf.",
            "💬",
            "chat",
        )

    with r1c2:
        tool_card(
            "Coding AI",
            "Code schreiben, debuggen, erklären und verbessern.",
            "💻",
            "coding",
        )

    with r1c3:
        tool_card(
            "Image Generator",
            "Prompts, Bildideen, Thumbnails und Branding Assets.",
            "🎨",
            "image",
        )

    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
        tool_card(
            "Music AI",
            "Songideen, Lyrics, Hooks und Musik-Konzepte.",
            "🎵",
            "music",
        )

    with r2c2:
        tool_card(
            "Reels Creator",
            "Hooks, Skripte, Captions und Video-Prompts.",
            "🎬",
            "reels",
        )

    with r2c3:
        tool_card(
            "AI Video",
            "Professionelle Video-Prompts und Szenenpläne.",
            "🎞️",
            "video",
        )

    st.divider()

    st.success("Bereit. Wähle links in der Sidebar oder öffne direkt ein Tool.")