import base64
import os
import streamlit as st


def image_to_base64(path):
    if not os.path.exists(path):
        return None

    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()


def render_home():
    header_b64 = image_to_base64("Header.png")

    if header_b64:
        bg_style = f"""
        background:
            linear-gradient(rgba(2, 6, 23, 0.72), rgba(2, 6, 23, 0.92)),
            url("data:image/png;base64,{header_b64}");
        background-size: cover;
        background-position: center;
        """
    else:
        bg_style = """
        background:
            radial-gradient(circle at top left, rgba(0, 140, 255, 0.35), transparent 35%),
            radial-gradient(circle at bottom right, rgba(80, 120, 255, 0.25), transparent 35%),
            linear-gradient(135deg, #020617, #08152e);
        """

    st.markdown(
        f"""
        <div class="mabyte-hero" style='{bg_style}'>
            <div class="mabyte-hero-content">
                <h1>Willkommen bei MABYTE</h1>

                <p class="lead">
                    MABYTE ist mehr als nur eine AI.
                </p>

                <p>
                    Es ist dein persönlicher Begleiter für Ideen, Projekte und Visionen.
                    Als Unterstützung, die mitdenkt, dich inspiriert und dir hilft,
                    deine Gedanken zu realisieren.
                </p>

                <p>
                    Egal ob du programmierst, ein Business aufbaust,
                    Content erschaffst oder einfach neue Möglichkeiten entdecken willst:
                    MABYTE begleitet dich auf deinem Weg.
                </p>

                <h3>Schneller. Kreativer. Grenzenloser.</h3>

                <p>
                    Denn die Zukunft entsteht nicht irgendwann.<br>
                    Sie entsteht genau jetzt — mit dir.
                </p>

                <div class="mabyte-claim">
                    MABYTE — BEYOND LIMITS.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>💬 Smart Chat</h3>
                <p>Chatte mit deiner AI und speichere deinen Verlauf.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🎬 AI Media</h3>
                <p>Bilder, Videos, Musik und kreative Assets erstellen.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🚀 Creator Tools</h3>
                <p>Reels Creator, Scheduler und Automation Tools.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )