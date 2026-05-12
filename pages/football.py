import streamlit as st
from datetime import datetime


def render_metric(label, value):
    with st.container(border=True):
        st.metric(label, value)


def insight_card(title, text, action=None):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(text)

        if action:
            st.button(action, use_container_width=True, key=f"football_{title}")


def render_football():
    st.title("⚽ Football Intelligence")
    st.caption("Elite Workspace für Match Analysis, Tactics, Scouting und Content Creation.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric("Match Engine", "Online")

    with c2:
        render_metric("Reports", "0")

    with c3:
        render_metric("Clips Ready", "0")

    with c4:
        render_metric("AI Agents", "Idle")

    st.divider()

    left, right = st.columns([1.55, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🎯 Match Analysis Console")

            match = st.text_input(
                "Match",
                placeholder="z.B. Arsenal vs Manchester City",
            )

            focus = st.selectbox(
                "Analyse Fokus",
                [
                    "Tactical Breakdown",
                    "Player Performance",
                    "Scouting Report",
                    "Content Package",
                    "Match Preview",
                    "Post Match Report",
                ],
            )

            depth = st.selectbox(
                "Analyse Tiefe",
                [
                    "Quick Insight",
                    "Professional Report",
                    "Elite Tactical Analysis",
                ],
            )

            if st.button("⚽ Analyse starten", use_container_width=True):
                if not match:
                    st.warning("Bitte Match eingeben.")
                else:
                    st.success(f"Analyse vorbereitet: {match}")
                    st.info("Live-Daten/API werden später verbunden. Aktuell wird der Workspace vorbereitet.")

    with right:
        with st.container(border=True):
            st.subheader("🧠 AI Recommendations")

            st.info("Generate tactical breakdown from this match.")
            st.info("Turn analysis into TikTok/Reels package.")
            st.info("Create scouting report for key players.")
            st.info("Build YouTube breakdown script.")

    st.divider()

    st.subheader("⚡ Cross-Workflow Intelligence")

    a, b, c = st.columns(3)

    with a:
        insight_card(
            "🎬 Content Engine",
            "Convert match analysis into short-form content, captions and hooks.",
            "Create Content Package",
        )

    with b:
        insight_card(
            "🧾 Scouting Layer",
            "Generate player profiles, strengths, weaknesses and transfer fit.",
            "Generate Scouting Report",
        )

    with c:
        insight_card(
            "📊 Tactical Layer",
            "Create formations, pressing patterns, chance creation and risk zones.",
            "Create Tactical Report",
        )

    st.divider()

    st.subheader("🛰️ Football Agents")

    x, y = st.columns(2)

    with x:
        with st.container(border=True):
            st.markdown("### 🤖 Football Content Agent")
            st.caption("Analysiert Spiele und erstellt daraus Social Content.")
            st.success("Status: Ready")

            st.write("Output:")
            st.write("• TikTok Hook")
            st.write("• YouTube Short Script")
            st.write("• Instagram Carousel")
            st.write("• Twitter/X Thread")

    with y:
        with st.container(border=True):
            st.markdown("### 📡 Match Intelligence Agent")
            st.caption("Erkennt wichtige Match-Momente und taktische Muster.")
            st.success("Status: Ready")

            st.write("Signals:")
            st.write("• Pressing Triggers")
            st.write("• Chance Creation")
            st.write("• Key Players")
            st.write("• Tactical Shifts")

    st.divider()

    with st.container(border=True):
        st.subheader("📡 System Status")
        st.write(f"Workspace Time: {datetime.utcnow().strftime('%H:%M UTC')}")
        st.write("Football Data Layer: Prepared")
        st.write("Content Engine Link: Ready")
        st.write("Automation Pipeline: Ready")