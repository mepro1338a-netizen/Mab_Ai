import streamlit as st


def open_page(page):
    st.session_state.page = page
    st.rerun()


def tool_card(icon, title, text, page, button_text="Öffnen"):
    with st.container(border=True):
        st.markdown(f"## {icon} {title}")
        st.write(text)
        st.button(
            button_text,
            use_container_width=True,
            key=f"open_{page}",
            on_click=open_page,
            args=(page,),
        )


def render_home():
    user = st.session_state.get("user", "User")
    tokens = st.session_state.get("tokens", 0)
    plan = st.session_state.get("plan", "free")

    st.title("🚀 MaByte Control Center")
    st.caption("Dein professioneller AI Workspace für Chat, Coding, Media, Content und Automation.")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Account", user)

    with k2:
        st.metric("Tokens", tokens)

    with k3:
        st.metric("Plan", plan)

    st.divider()

    left, right = st.columns([1.4, 1])

    with left:
        with st.container(border=True):
            st.subheader("Willkommen zurück")
            st.write(
                "Starte deine AI-Workflows schneller: Chatte mit MaByte, erstelle Code, "
                "plane Reels, entwickle Prompts und generiere Content für deine Projekte."
            )

            c1, c2 = st.columns(2)

            with c1:
                st.button(
                    "💬 Memory Chat starten",
                    use_container_width=True,
                    on_click=open_page,
                    args=("chat",),
                )

            with c2:
                st.button(
                    "💻 Coding AI öffnen",
                    use_container_width=True,
                    on_click=open_page,
                    args=("coding",),
                )

    with right:
        with st.container(border=True):
            st.subheader("Status")
            st.write("✅ Login aktiv")
            st.write("✅ Tokens synchronisiert")
            st.write("✅ AI Tools bereit")
            st.write("✅ Dashboard verbunden")

    st.divider()

    st.subheader("AI Tools")

    c1, c2, c3 = st.columns(3)

    with c1:
        tool_card(
            "💬",
            "Memory Chat",
            "Dein persönlicher AI Chat für Ideen, Planung, Code und Content.",
            "chat",
        )

    with c2:
        tool_card(
            "💻",
            "Coding AI",
            "Code schreiben, debuggen, erklären und als Datei exportieren.",
            "coding",
        )

    with c3:
        tool_card(
            "🎨",
            "Image Generator",
            "Bildideen, Prompts, Thumbnails und Branding Assets entwickeln.",
            "image",
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        tool_card(
            "🎵",
            "Music AI",
            "Songideen, Lyrics, Hooks und Musik-Konzepte erstellen.",
            "music",
        )

    with c5:
        tool_card(
            "🎬",
            "Reels Creator",
            "Hooks, Skripte, Captions und Video-Prompts für Social Media.",
            "reels",
        )

    with c6:
        tool_card(
            "🎞️",
            "AI Video",
            "Professionelle Video-Prompts, Szenenpläne und kreative Konzepte.",
            "video",
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.subheader("Account")
            st.write("Verwalte Tokens, Premium und Redeem Codes.")
            st.button(
                "📊 Dashboard öffnen",
                use_container_width=True,
                on_click=open_page,
                args=("dashboard",),
            )

    with c2:
        with st.container(border=True):
            st.subheader("Support")
            st.write("Erstelle Tickets und verwalte deine Anfragen.")
            st.button(
                "🆘 Support öffnen",
                use_container_width=True,
                on_click=open_page,
                args=("support",),
            )