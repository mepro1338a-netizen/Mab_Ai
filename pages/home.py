import streamlit as st


def render_home():
    st.markdown(
        """
        <style>
        .home-hero {
            padding: 45px 50px;
            border-radius: 34px;
            background:
                radial-gradient(circle at 20% 20%, rgba(56,189,248,.22), transparent 32%),
                linear-gradient(135deg, rgba(5,15,35,.98), rgba(10,35,70,.92));
            border: 1px solid rgba(125,211,252,.28);
            box-shadow: 0 0 55px rgba(56,189,248,.18);
            margin-bottom: 38px;
        }

        .home-badge {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 999px;
            background: rgba(14,165,233,.16);
            border: 1px solid rgba(125,211,252,.35);
            color: #7dd3fc;
            font-weight: 900;
            margin-bottom: 22px;
        }

        .home-title {
            font-size: 72px;
            font-weight: 1000;
            color: white;
            margin-bottom: 18px;
        }

        .home-text {
            font-size: 23px;
            line-height: 1.6;
            color: #dbeafe;
            font-weight: 700;
            max-width: 850px;
        }

        .home-pills {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 28px;
        }

        .home-pill {
            padding: 13px 20px;
            border-radius: 18px;
            background: linear-gradient(135deg, #0ea5e9, #2563eb);
            color: white;
            font-weight: 900;
        }

        .tool-card {
            min-height: 250px;
            padding: 32px;
            border-radius: 30px;
            background: linear-gradient(145deg, rgba(8,20,46,.98), rgba(13,47,91,.82));
            border: 1px solid rgba(125,211,252,.28);
            box-shadow: 0 0 35px rgba(56,189,248,.14);
        }

        .tool-title {
            font-size: 34px;
            color: white;
            font-weight: 950;
            margin-bottom: 18px;
        }

        .tool-text {
            color: #dbeafe;
            font-size: 19px;
            line-height: 1.55;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-hero">
            <div class="home-badge">NEXT GENERATION AI PLATFORM</div>
            <div class="home-title">Mabyte</div>
            <div class="home-text">
                Deine moderne AI Plattform für Chat, Coding, Bilder, Videos,
                Musik und Creator Workflows. Schnell. Kreativ. Übersichtlich.
            </div>
            <div class="home-pills">
                <div class="home-pill">⚡ Smart AI</div>
                <div class="home-pill">💎 Pro Workflow</div>
                <div class="home-pill">🚀 Creator Tools</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Deine Tools")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="tool-card">
                <div class="tool-title">💬 Smart Chat</div>
                <div class="tool-text">
                    Chatte mit Mabyte, speichere deinen Verlauf und arbeite schneller.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="tool-card">
                <div class="tool-title">🎬 AI Media</div>
                <div class="tool-text">
                    Erstelle Bild-Prompts, Video-Konzepte, Musikideen und kreative Assets.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="tool-card">
                <div class="tool-title">🚀 Creator Tools</div>
                <div class="tool-text">
                    Plane Reels, baue Hooks und erstelle Content für deine Plattformen.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )