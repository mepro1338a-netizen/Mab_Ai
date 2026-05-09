import streamlit as st


def render_home():
    st.markdown(
        """
        <div class="mabyte-hero">
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