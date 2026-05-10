import os
import base64
import streamlit as st


def img_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_home():
    logo = img_base64("LogoMAIN.png")

    if logo:
        logo_html = f"""
        <img src="data:image/png;base64,{logo}" class="home-main-logo">
        """
    else:
        logo_html = "<h1>Mabyte</h1>"

    st.markdown(
        f"""
        <style>
        .home-hero {{
            text-align:center;
            padding: 45px 20px 38px 20px;
        }}

        .home-main-logo {{
            width: 520px;
            max-width: 88%;
            filter: drop-shadow(0 0 28px rgba(59,130,246,.55));
            margin-bottom: 18px;
        }}

        .home-sub {{
            color:#cfe6ff;
            font-size:26px;
            font-weight:800;
            text-shadow:0 0 18px rgba(96,165,250,.35);
            margin-bottom:55px;
        }}

        .home-card {{
            min-height: 265px;
            padding: 38px;
            border-radius: 32px;
            background:
                linear-gradient(145deg, rgba(9,18,42,.96), rgba(13,30,65,.92));
            border:1px solid rgba(96,165,250,.22);
            box-shadow:
                0 0 35px rgba(59,130,246,.12),
                inset 0 0 30px rgba(255,255,255,.025);
            transition:.25s ease;
        }}

        .home-card:hover {{
            transform: translateY(-6px);
            border-color:rgba(125,211,252,.7);
            box-shadow:0 0 45px rgba(56,189,248,.28);
        }}

        .home-card h2 {{
            font-size:38px;
            font-weight:950;
            color:white;
            margin-bottom:22px;
        }}

        .home-card p {{
            font-size:20px;
            line-height:1.55;
            color:#dbeafe;
            font-weight:700;
        }}
        </style>

        <div class="home-hero">
            {logo_html}
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
            <div class="home-card">
                <h2>💬 Smart Chat</h2>
                <p>Chatte mit deiner AI und speichere deinen Verlauf.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="home-card">
                <h2>🎬 AI Media</h2>
                <p>Bilder, Videos, Musik und kreative Assets erstellen.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="home-card">
                <h2>🚀 Creator Tools</h2>
                <p>Reels Creator, Scheduler und Automation Tools.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )