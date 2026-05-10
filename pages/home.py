import streamlit as st


def render_home():
    st.markdown(
        """
<style>
.hero-header {
    text-align: center;
    padding: 38px 30px;
    border-radius: 34px;
    background:
        radial-gradient(circle at center, rgba(56,189,248,.20), transparent 38%),
        linear-gradient(145deg, rgba(5,15,35,.98), rgba(9,35,75,.92));
    border: 1px solid rgba(125,211,252,.28);
    box-shadow: 0 0 55px rgba(56,189,248,.18);
    margin-bottom: 28px;
}

.hero-badge {
    display: inline-block;
    padding: 12px 22px;
    border-radius: 999px;
    color: #7dd3fc;
    border: 1px solid rgba(125,211,252,.45);
    background: rgba(14,165,233,.16);
    font-weight: 950;
    letter-spacing: .8px;
}

.hero-title {
    text-align: center;
    font-size: 64px;
    font-weight: 1000;
    color: white;
    margin: 24px 0 12px 0;
    text-shadow: 0 0 30px rgba(56,189,248,.28);
}

.hero-sub {
    text-align: center;
    color: #dbeafe;
    font-size: 23px;
    font-weight: 750;
    max-width: 980px;
    margin: 0 auto 34px auto;
    line-height: 1.55;
}

.feature-card {
    min-height: 210px;
    padding: 28px;
    border-radius: 28px;
    background: linear-gradient(145deg, rgba(7,18,42,.98), rgba(12,38,78,.90));
    border: 1px solid rgba(96,165,250,.25);
    box-shadow: 0 0 34px rgba(37,99,235,.13);
    transition: .25s ease;
}

.feature-card:hover {
    transform: translateY(-6px);
    border-color: rgba(125,211,252,.75);
    box-shadow: 0 0 45px rgba(56,189,248,.30);
}

.feature-title {
    color: white;
    font-size: 28px;
    font-weight: 950;
    margin-bottom: 14px;
}

.feature-text {
    color: #dbeafe;
    font-size: 17px;
    line-height: 1.55;
    font-weight: 700;
}
</style>

<div class="hero-header">
    <div class="hero-badge">NEXT GENERATION AI PLATFORM</div>
</div>

<div class="hero-title">Mabyte ist die Revolution.</div>

<div class="hero-sub">
    Ein moderner AI Hub für Chat, Coding, Bilder, Videos, Musik,
    Social Media Content, Reels und Automation — alles in einer Plattform.
</div>
        """,
        unsafe_allow_html=True,
    )

    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">💬 Moderner Chatbot</div>
                <div class="feature-text">
                    Chatte mit MaByte, speichere deinen Verlauf und arbeite smarter.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">💻 Coding AI</div>
                <div class="feature-text">
                    Code schreiben, Fehler erklären, Projekte schneller bauen.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🎨 Bilder & Design</div>
                <div class="feature-text">
                    Erstelle starke Bildideen, Prompts, Thumbnails und Branding Assets.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🎬 Videos & Reels</div>
                <div class="feature-text">
                    Generiere Hooks, Skripte, Captions, Szenen und Video-Prompts.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🎵 Musik Generator</div>
                <div class="feature-text">
                    Songideen, Lyrics, Hooks, Styles und kreative Musik-Konzepte.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🚀 Social Media Automation</div>
                <div class="feature-text">
                    Content planen, Reels vorbereiten und später automatisiert posten.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )