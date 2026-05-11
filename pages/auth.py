import streamlit as st


def render_home():

    st.markdown(
        """
<style>

.home-hero {
    padding: 45px;
    border-radius: 34px;
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 30%),
        linear-gradient(145deg, rgba(5,15,35,.98), rgba(9,35,75,.92));
    border: 1px solid rgba(125,211,252,.20);
    box-shadow: 0 0 40px rgba(56,189,248,.16);
    margin-bottom: 28px;
}

.home-title {
    font-size: 64px;
    font-weight: 1000;
    color: white;
    margin-bottom: 18px;
}

.home-sub {
    font-size: 22px;
    line-height: 1.6;
    color: #dbeafe;
    font-weight: 700;
}

.home-card {
    padding: 28px;
    border-radius: 26px;
    background:
        linear-gradient(145deg, rgba(7,18,42,.96), rgba(12,38,78,.92));
    border: 1px solid rgba(125,211,252,.16);
    margin-bottom: 20px;
    transition: .2s ease;
}

.home-card:hover {
    transform: translateY(-4px);
    border-color: rgba(125,211,252,.42);
}

.home-card-title {
    color: white;
    font-size: 26px;
    font-weight: 900;
    margin-bottom: 10px;
}

.home-card-text {
    color: #dbeafe;
    font-size: 17px;
    line-height: 1.6;
    font-weight: 700;
}

</style>

<div class="home-hero">

    <div class="home-title">
        🚀 Willkommen bei MaByte
    </div>

    <div class="home-sub">
        Dein modernes AI Workspace für Chat, Coding,
        Content, Bilder, Musik, Reels und Automation.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
<div class="home-card">
    <div class="home-card-title">
        💬 AI Chat
    </div>

    <div class="home-card-text">
        Intelligenter AI Chat mit Memory und modernen Antworten.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
<div class="home-card">
    <div class="home-card-title">
        💻 Coding AI
    </div>

    <div class="home-card-text">
        Projekte bauen, Bugs fixen und schneller entwickeln.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
<div class="home-card">
    <div class="home-card-title">
        🎨 Media Studio
    </div>

    <div class="home-card-text">
        Bilder, Reels, Musik und kreative Inhalte generieren.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.success(f"Angemeldet als: {st.session_state.user}")