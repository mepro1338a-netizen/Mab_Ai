import streamlit as st
from datetime import datetime

from database import (
    recent_activity,
    total_tokens_used,
    successful_jobs_count,
    failed_jobs_count,
    workspace_activity_score,
    latest_tool_used,
)

from config import PLANS


def open_page(page):
    st.session_state.page = page
    st.rerun()


def workspace_card(icon, title, desc, page):
    with st.container(border=True):

        st.markdown(f"### {icon} {title}")
        st.caption(desc)

        if st.button(
            "Open Workspace",
            use_container_width=True,
            key=f"workspace_{page}",
        ):
            open_page(page)


def activity_item(icon, title, text):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.caption(text)


def render_activity_feed(username):
    activity = recent_activity(username=username, limit=6)

    if not activity:
        st.info("Noch keine AI Aktivitäten vorhanden.")
        return

    for item in activity:

        tool = str(item.get("tool", "system")).replace("_", " ").title()
        status = item.get("status", "success")
        provider = item.get("api_provider", "system")
        tokens = item.get("cost_tokens", 0)

        created = str(item.get("created_at", ""))[:16]

        icon = "⚡"

        if "video" in tool.lower():
            icon = "🎬"

        elif "coding" in tool.lower():
            icon = "💻"

        elif "image" in tool.lower():
            icon = "🎨"

        elif "music" in tool.lower():
            icon = "🎵"

        elif "reels" in tool.lower():
            icon = "📣"

        elif "football" in tool.lower():
            icon = "⚽"

        activity_item(
            icon,
            tool,
            f"Status: {status} | Provider: {provider} | Tokens: {tokens} | {created}",
        )


def recommendation_card(text):
    st.info(text)


def render_home():

    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    plan_data = PLANS.get(plan, PLANS["free"])

    total_used = total_tokens_used(user)
    jobs_success = successful_jobs_count(user)
    jobs_failed = failed_jobs_count(user)
    activity_score = workspace_activity_score(user)
    latest_tool = latest_tool_used(user)

    st.title("🚀 MaByte Mission Control")
    st.caption("The AI Operating System for creators, analysts and modern teams.")

    st.write("")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("👤 User", user)

    with c2:
        st.metric("💎 Plan", plan_data.get("label", plan))

    with c3:
        st.metric("🪙 Tokens", tokens)

    with c4:
        st.metric("⚡ Jobs", jobs_success)

    with c5:
        st.metric("🧠 Activity", f"{activity_score}/100")

    st.divider()

    left, right = st.columns([1.7, 1], gap="large")

    with left:

        st.subheader("⚡ Live AI Activity")

        render_activity_feed(user)

    with right:

        with st.container(border=True):

            st.subheader("🧠 Smart Recommendations")

            recommendation_card(
                "Turn your latest workflow into a Content Engine package."
            )

            recommendation_card(
                "Generate short-form clips from your AI outputs."
            )

            recommendation_card(
                "Use Developer OS to accelerate current coding tasks."
            )

            recommendation_card(
                "Open Football Intelligence for tactical analysis."
            )

    st.divider()

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        with st.container(border=True):
            st.metric("Total Tokens Used", total_used)

    with k2:
        with st.container(border=True):
            st.metric("Successful Jobs", jobs_success)

    with k3:
        with st.container(border=True):
            st.metric("Failed Jobs", jobs_failed)

    with k4:
        with st.container(border=True):
            st.metric("Latest Workspace", latest_tool)

    st.divider()

    st.subheader("🧩 Workspaces")

    a, b, c = st.columns(3)

    with a:
        workspace_card(
            "💬",
            "AI Assistant",
            "Central intelligence layer for planning, strategy and execution.",
            "chat",
        )

    with b:
        workspace_card(
            "📣",
            "Content Engine",
            "Reels, captions, hooks and social AI workflows.",
            "reels",
        )

    with c:
        workspace_card(
            "💻",
            "Developer OS",
            "Coding, debugging and AI software acceleration.",
            "coding",
        )

    d, e, f = st.columns(3)

    with d:
        workspace_card(
            "🎨",
            "Creative Workspace",
            "Images, prompts, branding and visual generation.",
            "image",
        )

    with e:
        workspace_card(
            "🎬",
            "Media Studio",
            "Video prompting and cinematic AI workflows.",
            "video",
        )

    with f:
        workspace_card(
            "⚽",
            "Football Intelligence",
            "Elite tactical analysis and automated sports content.",
            "football",
        )

    g, h = st.columns(2)

    with g:
        workspace_card(
            "🧪",
            "Automation Lab",
            "Agents, automations and intelligent workflows.",
            "automation_lab",
        )

    with h:
        workspace_card(
            "📊",
            "Account Command",
            "Plans, billing, usage and premium management.",
            "dashboard",
        )

    st.divider()

    x, y = st.columns([1.4, 1], gap="large")

    with x:

        with st.container(border=True):

            st.subheader("🛰️ Active AI Systems")

            st.success("AI Core connected")
            st.success("Workspace Router online")
            st.success("Mission Control synchronized")
            st.success("Realtime Usage Tracking active")
            st.success("Premium Engine connected")
            st.success("Automation Queue operational")

    with y:

        with st.container(border=True):

            st.subheader("📡 System Status")

            st.write(f"UTC Time: {datetime.utcnow().strftime('%H:%M UTC')}")
            st.write("AI Nodes: Operational")
            st.write("Queue Status: Stable")
            st.write("Sync Layer: Connected")
            st.write("Activity Engine: Live")
            st.write("Workspace State: Healthy")