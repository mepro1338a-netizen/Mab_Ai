import streamlit as st


def render_home():
    st.markdown(
        """
        <style>
        .home-hero {
            background: linear-gradient(145deg, rgba(5,12,28,.98), rgba(9,30,62,.94));
            border: 1px solid rgba(96,165,250,.28);
            border-radius: 34px;
            padding: 38px;
            margin-bottom: 34px;
            box-shadow: 0 0 55px rgba(56,189,248,.16);
            text-align: center;
        }

        .home-badge {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 999px;
            background: rgba(14,165,233,.14);
            border: 1px solid rgba(125,211,252,.35);
            color: #7dd3fc;
            font-size: 13px;
            font-weight: 900;
            letter-spacing: .8px;
            margin-bottom: 18px;
        }

        .home-logo {
            display: flex;
            justify-content: center;
            margin: 6px 0 22px 0;
        }

        .home-text {
            color: #dbeafe;
            font-size: 22px;
            line-height: 1.55;
            font-weight: 750;
            max-width: 880px;
            margin: 0 auto 26px auto;
        }

        .home-pill {
            background: linear-gradient(135deg, #0f6fc7, #0ea5e9);
            border: 1px solid rgba(125,211,252,.35);
            border-radius: 18px;
            padding: 14px 18px;
            color: white;
            font-weight: 900;
            text-align: center;
            box-shadow: 0 0 20px rgba(56,189,248,.18);
        }

        .section-title {
            color: white;
            font-size: 34px;
            font-weight: 950;
            margin: 10px 0 22px 0;
        }

        .tool-card {
            min-height: 235px;
            background: linear-gradient(145deg, rgba(7,18,42,.98), rgba(12,36,75,.88));
            border: 1px solid rgba(96,165,250,.24);
            border-radius: 28px;
            padding: 30px;
            box-shadow: 0 0 34px rgba(37,99,235,.12);
            transition: .25s ease;
        }

        .tool-card:hover {
            transform: translateY(-6px);
            border-color: rgba(125,211,252,.75);
            box-shadow: 0 0 45px rgba(56,189,248,.28);
        }

        .tool-title {
            color: white;
            font-size: 32px;
            font-weight: 950;
            margin-bottom: 18px;
        }

        .tool-text {
            color: #dbeafe;
            font-size: 18px;
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
            <div class="home-logo">
        """,
        unsafe_allow_html=True,
    )

    st.image("logoslogan.png", width=750)

    st.markdown(
        """
            </div>
            <div class="home-text">
                Deine moderne AI Plattform für Chat, Coding, Bilder, Videos,
                Musik und Creator Workflows. Schnell. Kreativ. Übersichtlich.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown('<div class="home-pill">⚡ Smart AI</div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="home-pill">💎 Pro Workflow</div>', unsafe_allow_html=True)
    with p3:
        st.markdown('<div class="home-pill">🚀 Creator Ready</div>', unsafe_allow_html=True)
    with p4:
        st.markdown('<div class="home-pill">🎬 Media Suite</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Deine Tools</div>', unsafe_allow_html=True)

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