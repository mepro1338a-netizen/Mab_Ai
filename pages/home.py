import os
import streamlit as st


def show_logo():
    for name in ["LogoMAIN.png", "LogoMain.png", "logoMAIN.png", "Logo.png"]:
        if os.path.exists(name):
            st.image(name, width=320)
            return


def render_home():
    left, right = st.columns([1.2, 0.8])

    with left:
        show_logo()

        st.caption("NEXT GENERATION AI PLATFORM")
        st.title("MABYTE")
        st.header("Mehr als nur eine AI.")

        st.write(
            "Dein persönlicher Begleiter für Ideen, Projekte und Visionen. "
            "MABYTE denkt mit, inspiriert dich und hilft dir, Gedanken in echte Ergebnisse zu verwandeln."
        )

        st.write(
            "Egal ob du programmierst, ein Business aufbaust, Content erschaffst "
            "oder neue Möglichkeiten entdeckst: MABYTE begleitet dich auf deinem Weg."
        )

        st.subheader("Schneller. Kreativer. Grenzenloser.")
        st.write("Denn die Zukunft entsteht nicht irgendwann. Sie entsteht genau jetzt — mit dir.")
        st.header("MABYTE — BEYOND LIMITS.")

    with right:
        st.info("24/7 AI Tools")
        st.success("PRO Creator Workflow")
        st.info("Ideas to Reality")

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("💬 Smart Chat")
        st.write("Chatte mit deiner AI, speichere deinen Verlauf und arbeite schneller.")

    with c2:
        st.subheader("🎬 AI Media")
        st.write("Erstelle Bilder, Videos, Musik, Prompts und kreative Assets.")

    with c3:
        st.subheader("🚀 Creator Tools")
        st.write("Plane Reels, baue Workflows und automatisiere deinen Content.")