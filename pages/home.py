import os
import base64
import streamlit as st


def b64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_home():
    header = b64("Header.png")

    hero_image = (
        f'<img src="data:image/png;base64,{header}" class="mabyte-header">'
        if header
        else '<div class="mabyte-fallback">MABYTE</div>'
    )

    st.markdown(
        f"""
        <style>
        .mabyte-home {{
            padding: 24px 10px 10px 10px;
        }}

        .mabyte-hero {{
            position: relative;
            overflow: hidden;
            border-radius: 38px;
            padding: 48px 42px;
            min-height: 430px;
            background:
                radial-gradient(circle at 20% 10%, rgba(56,189,248,.32), transparent 32%),
                radial-gradient(circle at 80% 80%, rgba(37,99,235,.28), transparent 35%),
                linear-gradient(135deg, rgba(3,7,18,.98), rgba(8,22,48,.98));
            border: 1px solid rgba(125,211,252,.25);
            box-shadow: 0 0 70px rgba(56,189,248,.18);
        }}

        .mabyte-hero-grid {{
            display: grid;
            grid-template-columns: 1.1fr .9fr;
            gap: 42px;
            align-items: center;
        }}

        .mabyte-badge {{
            display: inline-block;
            padding: 10px 18px;
            border-radius: 999px;
            background: rgba(14,165,233,.14);
            border: 1px solid rgba(125,211,252,.28);
            color: #7dd3fc;
            font-weight: 900;
            letter-spacing: .8px;
            margin-bottom: 22px;
        }}

        .mabyte-title {{
            font-size: 72px;
            line-height: .95;
            font-weight: 1000;
            color: white;
            margin-bottom: 20px;
            text-shadow: 0 0 30px rgba(125,211,252,.28);
        }}

        .mabyte-text {{
            font-size: 22px;
            line-height: 1.55;
            color: #dbeafe;
            max-width: 760px;
            font-weight: 700;
        }}

        .mabyte-actions {{
            display: flex;
            gap: 14px;
            margin-top: 32px;
            flex-wrap: wrap;
        }}

        .mabyte-pill {{
            padding: 14px 20px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(14,165,233,.22), rgba(37,99,235,.28));
            border: 1px solid rgba(125,211,252,.32);
            color: white;
            font-weight: 900;
        }}

        .mabyte-header {{
            width: 100%;
            border-radius: 32px;
            box-shadow:
                0 0 45px rgba(56,189,248,.28),
                0 0 120px rgba(37,99,235,.16);
        }}

        .mabyte-fallback {{
            font-size: 56px;
            font-weight: 1000;
            color: white;
            text-align: center;
        }}

        .mabyte-section-title {{
            margin-top: 42px;
            margin-bottom: 20px;
            font-size: 28px;
            font-weight: 950;
            color: white;
        }}

        .mabyte-card {{
            min-height: 250px;
            padding: 32px;
            border-radius: 30px;
            background:
                linear-gradient(145deg, rgba(8,20,46,.98), rgba(13,47,91,.82));
            border: 1px solid rgba(125,211,252,.25);
            box-shadow:
                0 0 35px rgba(56,189,248,.12),
                inset 0 0 26px rgba(255,255,255,.025);
            transition: .25s ease;
        }}

        .mabyte-card:hover {{
            transform: translateY(-7px);
            border-color: rgba(125,211,252,.75);
            box-shadow: 0 0 50px rgba(56,189,248,.30);
        }}

        .mabyte-card h2 {{
            color: white;
            font-size: 34px;
            font-weight: 1000;
            margin-bottom: 18px;
        }}

        .mabyte-card p {{
            color: #dbeafe;
            font-size: 19px;
            line-height: 1.55;
            font-weight: 700;
        }}

        @media (max-width: 900px) {{
            .mabyte-hero-grid {{
                grid-template-columns: 1fr;
            }}
            .mabyte-title {{
                font-size: 52px;
            }}
        }}
        </style>

        <div class="mabyte-home">
            <div class="mabyte-hero">
                <div class="mabyte-hero-grid">
                    <div>
                        <div class="mabyte-badge">NEXT GENERATION AI PLATFORM</div>
                        <div class="mabyte-title">Mabyte</div>
                        <div class="mabyte-text">
                            Deine moderne AI Plattform für Chat, Coding, Bilder, Videos,
                            Musik und Creator Workflows. Schnell. Kreativ. Übersichtlich.
                        </div>

                        <div class="mabyte-actions">
                            <div class="mabyte-pill">⚡ Smart AI Tools</div>
                            <div class="mabyte-pill">💎 Pro Workflow</div>
                            <div class="mabyte-pill">🚀 Creator Ready</div>
                        </div>
                    </div>

                    <div>
                        {hero_image}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mabyte-section-title">Deine Tools</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="mabyte-card">
                <h2>💬 Smart Chat</h2>
                <p>Chatte mit Mabyte, speichere deinen Verlauf und arbeite schneller.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="mabyte-card">
                <h2>🎬 AI Media</h2>
                <p>Erstelle Bild-Prompts, Video-Konzepte, Musikideen und kreative Assets.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="mabyte-card">
                <h2>🚀 Creator Tools</h2>
                <p>Plane Reels, baue Hooks und erstelle Content für deine Plattformen.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )