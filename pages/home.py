import os
import streamlit as st


def safe_logo():
    if os.path.exists("LogoMAIN.png"):
        st.image("LogoMAIN.png", width=260)
    elif os.path.exists("LogoMain.png"):
        st.image("LogoMain.png", width=260)
    elif os.path.exists("logoMAIN.png"):
        st.image("logoMAIN.png", width=260)
    else:
        st.markdown("# Mabyte")


def render_home():
    col_left, col_mid, col_right = st.columns([1, 2, 1])

    with col_mid:
        safe_logo()

    st.markdown("# Willkommen bei MABYTE")
    st.markdown("## MABYTE ist mehr als nur eine AI.")

    st.markdown(
        """
MABYTE ist dein persönlicher Begleiter für Ideen, Projekte und Visionen.

Eine Unterstützung, die mitdenkt, dich inspiriert und dir hilft, deine Gedanken zu realisieren.

Egal ob du programmierst, ein Business aufbaust, Content erschaffst oder einfach neue Möglichkeiten entdecken willst:  
**MABYTE begleitet dich auf deinem Weg.**

### Schneller. Kreativer. Grenzenloser.

Denn die Zukunft entsteht nicht irgendwann.  
Sie entsteht genau jetzt — mit dir.

## MABYTE — BEYOND LIMITS.
"""
    )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("## 💬 Smart Chat")
        st.write("Chatte mit deiner AI und speichere deinen Verlauf.")

    with c2:
        st.markdown("## 🎬 AI Media")
        st.write("Bilder, Videos, Musik und kreative Assets erstellen.")

    with c3:
        st.markdown("## 🚀 Creator Tools")
        st.write("Reels Creator, Scheduler und Automation Tools.")