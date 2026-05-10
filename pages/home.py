import streamlit as st


def render_home():

    st.markdown(
        """
        <style>

        .hero-box{
            background:
            radial-gradient(circle at top left, rgba(59,130,246,.22), transparent 30%),
            radial-gradient(circle at bottom right, rgba(37,99,235,.18), transparent 35%),
            linear-gradient(145deg,#07111f,#0b1730);

            border:1px solid rgba(96,165,250,.20);
            border-radius:36px;
            padding:55px;
            margin-bottom:40px;
            box-shadow:0 0 55px rgba(59,130,246,.14);
        }

        .badge{
            display:inline-block;
            padding:10px 18px;
            border-radius:999px;
            background:rgba(59,130,246,.16);
            border:1px solid rgba(125,211,252,.30);
            color:#7dd3fc;
            font-weight:800;
            margin-bottom:24px;
            letter-spacing:.5px;
        }

        .hero-title{
            font-size:78px;
            font-weight:1000;
            color:white;
            line-height:1;
            margin-bottom:22px;
            text-shadow:0 0 24px rgba(59,130,246,.25);
        }

        .hero-text{
            color:#dbeafe;
            font-size:24px;
            line-height:1.6;
            font-weight:700;
            max-width:900px;
        }

        .pill-row{
            display:flex;
            gap:14px;
            flex-wrap:wrap;
            margin-top:34px;
        }

        .pill{
            padding:14px 22px;
            border-radius:18px;
            background:linear-gradient(145deg,#1d4ed8,#2563eb);
            color:white;
            font-weight:800;
            box-shadow:0 0 18px rgba(37,99,235,.25);
        }

        .section-title{
            font-size:34px;
            font-weight:900;
            color:white;
            margin-bottom:24px;
        }

        .tool-card{
            background:
            linear-gradient(145deg,#091327,#0d2247);

            border:1px solid rgba(96,165,250,.24);
            border-radius:30px;
            padding:34px;
            min-height:270px;

            box-shadow:
            0 0 30px rgba(37,99,235,.12),
            inset 0 0 22px rgba(255,255,255,.02);

            transition:.25s;
        }

        .tool-card:hover{
            transform:translateY(-6px);
            border-color:#60a5fa;
            box-shadow:0 0 38px rgba(56,189,248,.28);
        }

        .tool-title{
            font-size:36px;
            color:white;
            font-weight:950;
            margin-bottom:20px;
        }

        .tool-text{
            color:#dbeafe;
            font-size:20px;
            line-height:1.6;
            font-weight:700;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # HERO

    st.markdown(
        """
        <div class="hero-box">

            <div class="badge">
                NEXT GENERATION AI PLATFORM
            </div>

            <div class="hero-title">
                Mabyte
            </div>

            <div class="hero-text">
                Deine moderne AI Plattform für Chat, Coding,
                Bilder, Videos, Musik und Creator Workflows.
                Schnell. Kreativ. Übersichtlich.
            </div>

            <div class="pill-row">
                <div class="pill">⚡ Smart AI</div>
                <div class="pill">💎 Pro Workflow</div>
                <div class="pill">🚀 Creator Tools</div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-title">
            Deine Tools
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="tool-card">
                <div class="tool-title">
                    💬 Smart Chat
                </div>

                <div class="tool-text">
                    Chatte mit Mabyte,
                    speichere deinen Verlauf
                    und arbeite schneller.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="tool-card">
                <div class="tool-title">
                    🎬 AI Media
                </div>

                <div class="tool-text">
                    Erstelle Bild-Prompts,
                    Video-Konzepte,
                    Musikideen und kreative Assets.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="tool-card">
                <div class="tool-title">
                    🚀 Creator Tools
                </div>

                <div class="tool-text">
                    Plane Reels,
                    baue Hooks und erstelle
                    Content für deine Plattformen.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )