import streamlit as st
from datetime import datetime


def open_page(page):
    st.session_state.page = page
    st.rerun()


def workspace_card(icon, title, desc, page):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.caption(desc)

        if st.button(
            "Öffnen",
            use_container_width=True,
            key=f"workspace_{page}",
        ):
            open_page(page)


def activity_item(title, text):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(text)


def render_home():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = st.session_state.get("tokens", 0)

    st.title("🚀 MaByte Mission Control")
    st.caption("The AI Operating System for creators, analysts and modern teams.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Account", user)

    with c2:
        st.metric("Plan", plan)

    with c3:
        st.metric("Tokens", tokens)

    with c4:
        st.metric("System", "Online")

    st.divider()

    left, right = st.columns([1.65, 1], gap="large")

    with left:
        st.subheader("⚡ AI Activity Feed")

        activity_item("🎬 Content Engine", "3 reel concepts prepared for your next campaign.")
        activity_item("💻 Developer OS", "Coding workspace ready for new builds and fixes.")
        activity_item("🎨 Creative Workspace", "Image prompts and brand assets can be generated.")
        activity_item("🧠 AI Core", "Central assistant is online and ready.")

    with right:
        with st.container(border=True):
            st.subheader("🧠 Smart Recommendations")
            st.info("Turn your latest idea into a content package.")
            st.info("Generate a landing page concept.")
            st.info("Create short-form content from your workflow.")
            st.info("Open Developer OS to build faster.")

    st.divider()

    st.subheader("🧩 Workspaces")

    a, b, c = st.columns(3)

    with a:
        workspace_card(
            "💬",
            "AI Assistant",
            "Central chat layer for ideas, planning and strategy.",
            "chat",
        )

    with b:
        workspace_card(
            "📣",
            "Content Engine",
            "Reels, captions, hooks and social content workflows.",
            "reels",
        )

    with c:
        workspace_card(
            "💻",
            "Developer OS",
            "Coding, debugging and software workflow acceleration.",
            "coding",
        )

    d, e, f = st.columns(3)

    with d:
        workspace_card(
            "🎨",
            "Creative Workspace",
            "Images, prompts, branding and visual AI workflows.",
            "image",
        )

    with e:
        workspace_card(
            "🎬",
            "Media Studio",
            "Video prompts, scenes and cinematic production workflows.",
            "video",
        )

    with f:
        workspace_card(
            "🧪",
            "Automation Lab",
            "Agents, workflows and intelligent task execution.",
            "automation_lab",
        )

    st.divider()

    x, y = st.columns([1.3, 1], gap="large")

    with x:
        with st.container(border=True):
            st.subheader("🛰️ Active AI Systems")
            st.success("AI Core connected")
            st.success("Memory Engine online")
            st.success("Workspace router active")
            st.success("Automation Queue ready")

    with y:
        with st.container(border=True):
            st.subheader("📡 System Status")
            st.write(f"Time: {datetime.utcnow().strftime('%H:%M UTC')}")
            st.write("Render Queue: Stable")
            st.write("AI Nodes: Operational")
            st.write("Sync: Connected")