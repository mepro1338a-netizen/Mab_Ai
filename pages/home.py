import streamlit as st


def render_home():
    st.markdown(
        """
        <div class="hero-box">
            <h1 class="hero-title">Mabyte</h1>
            <p class="hero-sub">Die neue Generation von AI Plattformen.</p>
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