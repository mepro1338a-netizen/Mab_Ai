import streamlit as st


def open_page(page):
    st.session_state.page = page
    st.rerun()


def tool_button(icon, title, subtitle, page):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.caption(subtitle)

        st.button(
            "Öffnen",
            use_container_width=True,
            key=f"open_{page}",
            on_click=open_page,
            args=(page,),
        )


def quick_action(label, page):
    st.button(
        label,
        use_container_width=True,
        key=f"quick_{page}",
        on_click=open_page,
        args=(page,),
    )


def render_home():
    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)

    st.title("🚀 MaByte Control Center")
    st.caption("Next Generation AI Workspace für Chat, Coding, Media, Content und Automation.")

    st.write("")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("👤 Account", user)

    with k2:
        st.metric("💎 Plan", plan)

    with k3:
        st.metric("🪙 Tokens", tokens)

    st.divider()

    left, right = st.columns([1.45, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Willkommen zurück")
            st.write(
                "Starte direkt mit deinen wichtigsten AI-Workflows. "
                "Nutze MaByte für Projekte, Content, Code, Reels und Automation."
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                quick_action("💬 Chat starten", "chat")

            with c2:
                quick_action("💻 Code erstellen", "coding")

            with c3:
                quick_action("🎬 Reel planen", "reels")

    with right:
        with st.container(border=True):
            st.subheader("Systemstatus")
            st.write("✅ Login aktiv")
            st.write("✅ Tokens synchronisiert")
            st.write("✅ AI Tools bereit")
            st.write("✅ Sidebar aktiv")

    st.divider()

    st.subheader("AI Tools")

    c1, c2, c3 = st.columns(3)

    with c1:
        tool_button(
            "💬",
            "Memory Chat",
            "Ideen, Planung, Code und Content im Chat.",
            "chat",
        )

    with c2:
        tool_button(
            "💻",
            "Coding AI",
            "Code schreiben, debuggen und exportieren.",
            "coding",
        )

    with c3:
        tool_button(
            "🎨",
            "Image AI",
            "Prompts, Bildideen und Branding Assets.",
            "image",
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        tool_button(
            "🎵",
            "Music AI",
            "Lyrics, Hooks und Song-Konzepte.",
            "music",
        )

    with c5:
        tool_button(
            "🎬",
            "Reels Creator",
            "Hooks, Skripte, Captions und Video-Prompts.",
            "reels",
        )

    with c6:
        tool_button(
            "🎞️",
            "Video AI",
            "Szenenpläne und professionelle Video-Prompts.",
            "video",
        )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        tool_button(
            "📊",
            "Dashboard",
            "Tokens, Nutzung und Account verwalten.",
            "dashboard",
        )

    with c2:
        tool_button(
            "🎁",
            "Redeem Codes",
            "Codes einlösen und Tokens freischalten.",
            "redeem",
        )

    with c3:
        tool_button(
            "🆘",
            "Support",
            "Tickets erstellen und Hilfe bekommen.",
            "support",
        )