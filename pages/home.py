import streamlit as st
from datetime import datetime


def open_page(page):
    st.session_state.page = page
    st.rerun()


def workspace_card(icon, title, desc, page):
    with st.container(border=True):

        st.markdown(f"## {icon} {title}")
        st.caption(desc)

        st.write("")

        st.button(
            f"{title} öffnen",
            use_container_width=True,
            key=f"workspace_{page}",
            on_click=open_page,
            args=(page,),
        )


def activity_item(title, text):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(text)


def render_home():

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)

    st.markdown("# 🚀 MaByte Mission Control")
    st.caption("The AI Operating System for creators, analysts and modern teams.")

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("👤 User", user)

    with c2:
        st.metric("💎 Plan", plan)

    with c3:
        st.metric("🪙 Tokens", tokens)

    with c4:
        st.metric("🟢 System", "Online")

    st.divider()

    left, right = st.columns([1.7, 1])

    with left:

        st.subheader("⚡ AI Activity Feed")

        activity_item(
            "🎬 Reel Generation completed",
            "Short-form content package rendered successfully.",
        )

        activity_item(
            "⚽ Football Intelligence updated",
            "New tactical insights generated for Arsenal vs City.",
        )

        activity_item(
            "💻 Developer OS",
            "AI fixed and optimized active coding workspace.",
        )

        activity_item(
            "🧠 Automation Agent",
            "Cross-platform posting pipeline executed.",
        )

    with right:

        with st.container(border=True):

            st.subheader("🧠 Smart Recommendations")

            st.info("Turn football analysis into viral shorts.")
            st.info("Generate content package from latest AI outputs.")
            st.info("Create automated TikTok posting workflow.")
            st.info("Build scouting report from match insights.")

    st.divider()

    st.subheader("🧩 Workspaces")

    a, b, c = st.columns(3)

    with a:
        workspace_card(
            "⚽",
            "Football Intelligence",
            "Advanced tactical AI, match analytics and automated sports content.",
            "football",
        )

    with b:
        workspace_card(
            "🎨",
            "Creative Workspace",
            "Images, prompts, design systems and visual AI workflows.",
            "image",
        )

    with c:
        workspace_card(
            "📣",
            "Content Engine",
            "Reels, social content, captions and automation pipelines.",
            "reels",
        )

    d, e, f = st.columns(3)

    with d:
        workspace_card(
            "💻",
            "Developer OS",
            "AI coding, debugging and software workflow acceleration.",
            "coding",
        )

    with e:
        workspace_card(
            "🎬",
            "Media Studio",
            "AI video systems, cinematic prompting and production workflows.",
            "video",
        )

    with f:
        workspace_card(
            "🧪",
            "Automation Lab",
            "AI agents, workflows and intelligent task execution.",
            "automations",
        )

    st.divider()

    x, y = st.columns([1.3, 1])

    with x:

        with st.container(border=True):

            st.subheader("🛰️ Active AI Systems")

            st.success("AI Core connected")
            st.success("Memory Engine online")
            st.success("Automation Queue active")
            st.success("Realtime Workspace sync enabled")
            st.success("Football Intelligence loaded")

    with y:

        with st.container(border=True):

            st.subheader("📡 System Status")

            st.write(f"Current Time: {datetime.utcnow().strftime('%H:%M UTC')}")
            st.write("Render Queue: Stable")
            st.write("AI Nodes: Operational")
            st.write("Automation Engine: Running")
            st.write("Realtime Sync: Connected")