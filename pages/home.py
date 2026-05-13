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


def stat_card(icon, label, value, sub=""):
    with st.container(border=True):
        st.markdown(f"### {icon}")
        st.caption(label)
        st.markdown(f"## {value}")
        if sub:
            st.caption(sub)


def quick_card(icon, title, page):
    with st.container(border=True):
        st.markdown(f"## {icon}")
        st.markdown(f"### {title}")
        if st.button("Öffnen", key=f"quick_{page}", use_container_width=True):
            open_page(page)


def activity_row(icon, title, text):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.caption(text)


def recommendation(title, text, button, page):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(text)
        if st.button(button, key=f"rec_{page}_{title}", use_container_width=True):
            open_page(page)


def render_activity(user):
    activity = recent_activity(username=user, limit=5)

    if not activity:
        activity_row("🧠", "AI Assistant", "Noch keine Aktivität vorhanden.")
        return

    for item in activity:
        tool = str(item.get("tool", "AI")).replace("_", " ").title()
        created = str(item.get("created_at", ""))[:16]
        tokens = item.get("cost_tokens", 0)
        status = item.get("status", "success")

        icon = "⚡"
        if "chat" in tool.lower():
            icon = "💬"
        elif "image" in tool.lower():
            icon = "🎨"
        elif "video" in tool.lower():
            icon = "🎬"
        elif "coding" in tool.lower():
            icon = "💻"
        elif "reels" in tool.lower():
            icon = "📣"
        elif "football" in tool.lower():
            icon = "⚽"

        activity_row(
            icon,
            tool,
            f"Status: {status} · Tokens: {tokens} · {created}",
        )


def render_home():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    plan_data = PLANS.get(plan, PLANS["free"])

    used_tokens = total_tokens_used(user)
    jobs = successful_jobs_count(user)
    failed = failed_jobs_count(user)
    score = workspace_activity_score(user)
    latest = latest_tool_used(user)

    st.markdown("# Welcome back,")
    st.markdown(f"# {user} ` {plan_data.get('label', plan)} `")
    st.caption("Dein AI Operating System für maximale Performance.")

    st.write("")

    a, b, c, d, e = st.columns(5)

    with a:
        quick_card("💬", "AI Assistant", "chat")

    with b:
        quick_card("📁", "Projects", "projects")

    with c:
        quick_card("⚡", "Automations", "automation_lab")

    with d:
        quick_card("⚽", "Football AI", "football")

    with e:
        quick_card("🎬", "Media Tools", "video")

    st.divider()

    s1, s2, s3, s4, s5 = st.columns(5)

    with s1:
        stat_card("👤", "User", user, "Active Account")

    with s2:
        stat_card("💎", "Plan", plan_data.get("label", plan), "Max Access")

    with s3:
        stat_card("🪙", "Tokens", f"{tokens:,}".replace(",", "."), "Verfügbar")

    with s4:
        stat_card("⚡", "Jobs", jobs, "Gesamt")

    with s5:
        stat_card("📈", "Activity", f"{score}/100", f"Latest: {latest}")

    st.divider()

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("⚡ Live AI Activity")
            render_activity(user)

            if st.button("Alle Aktivitäten anzeigen →", use_container_width=True):
                open_page("dashboard")

    with right:
        with st.container(border=True):
            st.subheader("🧠 Smart Recommendations")

            recommendation(
                "Optimize Your Workflow",
                "Erstelle Automationen für wiederkehrende Aufgaben und spare Zeit.",
                "Automation erstellen",
                "automation_lab",
            )

            recommendation(
                "Upgrade auf Elite+",
                "Mehr Tokens, mehr Power, mehr Möglichkeiten.",
                "Premium öffnen",
                "premium",
            )

            recommendation(
                "Project Boost",
                "Füge mehr Memory zu deinen Projekten hinzu für bessere AI Ergebnisse.",
                "Projekt optimieren",
                "projects",
            )

    st.divider()

    with st.container(border=True):
        st.subheader("💎 MaByte Elite")

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric("Tokens", f"{tokens:,}".replace(",", "."))

        with c2:
            st.metric("Used", used_tokens)

        with c3:
            st.metric("Daily Limit", "100/100")

        with c4:
            st.metric("Failed", failed)

        with c5:
            st.metric("System", "Online")

        st.success("Du nutzt den stärksten MaByte Plan. Bereit für große Workflows.")

    st.caption(f"© {datetime.utcnow().year} MaByte AI Operating System")