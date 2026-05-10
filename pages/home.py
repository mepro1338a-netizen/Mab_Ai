import os
import base64
import streamlit as st


def img_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_home():
    header = img_base64("Header.png")

    hero_img = f"""
    <img src="data:image/png;base64,{header}" class="home-header-img">
    """ if header else "<h1 class='home-fallback'>Mabyte</h1>"

    st.markdown(
        f"""
        <style>
        .home-wrap {{
            text-align: center;
            padding: 20px 20px 10px 20px;
        }}

        .home-header-img {{
            width: 760px;
            max-width: 92%;
            border-radius: 34px;
            box-shadow:
                0 0 55px rgba(56,189,248,.38),
                0 0 120px rgba(37,99,235,.22);
            margin-bottom: 26px;
        }}

        .home-sub {{
            color: #dbeafe;
            font-size: 28px;
            font-weight: 850;
            margin-bottom: 42px;
            text-shadow: 0 0 24px rgba(96,165,250,.55);
        }}

        .home-grid-card {{
            min-height: 235px;
            padding: 34px;
            border-radius: 30px;
            background: linear-gradient(145deg, rgba(9,18,42,.96), rgba(13,30,65,.90));
            border: 1px solid rgba(96,165,250,.24);
            box-shadow: 0 0 40px rgba(59,130,246,.13);
            transition: .25s ease;
        }}

        .home-grid-card:hover {{
            transform: translateY(-6px);
            border-color: rgba(125,211,252,.75);
            box-shadow: 0 0 45px rgba(56,189,248,.28);
        }}

        .home-grid-card h2 {{
            font-size: 34px;
            color: white;
            font-weight: 950;
            margin-bottom: 18px;
        }}

        .home-grid-card p {{
            color: #dbeafe;
            font-size: 19px;
            line-height: 1.55;
            font-weight: 700;
        }}
        </style>

        <div class="home-wrap">
            {hero_img}
            <div class="home-sub">
                Die neue Generation von AI Plattformen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="home-grid-card">
                <h2>💬 Smart Chat</h2>
                <p>Chatte mit deiner AI und speichere deinen Verlauf.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="home-grid-card">
                <h2>🎬 AI Media</h2>
                <p>Bilder, Videos, Musik und kreative Assets erstellen.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="home-grid-card">
                <h2>🚀 Creator Tools</h2>
                <p>Reels Creator, Scheduler und Automation Tools.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )