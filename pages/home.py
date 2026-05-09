import streamlit as st


def render_home():

    st.markdown(
        """
        <div style='text-align:center; padding-top:40px; padding-bottom:10px;'>
            <h1 style='font-size:64px; margin-bottom:0;'>Mabyte</h1>
            <p style='font-size:22px; color:#9db4ff; margin-top:0;'>
                Die neue Generation von AI Plattformen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h2>💬 Smart Chat</h2>
                <p>Chatte mit deiner AI und speichere deinen Verlauf.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h2>🎬 AI Media</h2>
                <p>Bilder, Videos, Musik und kreative Assets erstellen.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h2>🚀 Creator Tools</h2>
                <p>Reels Creator, Scheduler und Automation Tools.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )