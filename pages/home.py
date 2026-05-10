import streamlit as st


def render_home():

    st.markdown(
        """
        <style>

        .home-wrapper{
            padding-top:20px;
        }

        .hero-box{
            background:
            radial-gradient(circle at top left, rgba(56,189,248,.22), transparent 30%),
            linear-gradient(145deg,#050816,#0f172a,#111c44);

            border:1px solid rgba(59,130,246,.28);
            border-radius:38px;
            padding:55px;
            box-shadow:0 0 55px rgba(37,99,235,.18);
            margin-bottom:45px;
        }

        .hero-badge{
            display:inline-block;
            padding:12px 20px;
            border-radius:999px;
            background:rgba(37,99,235,.18);
            border:1px solid rgba(96,165,250,.35);
            color:#7dd3fc;
            font-size:14px;
            font-weight:900;
            letter-spacing:1px;
            margin-bottom:28px;
        }

        .hero-text{
            color:#dbeafe;
            font-size:25px;
            line-height:1.7;
            font-weight:700;
            max-width:850px;
            margin-top:25px;
        }

        .pill-row{
            display:flex;
            gap:16px;
            flex-wrap:wrap;
            margin-top:35px;
        }

        .pill{
            background:linear-gradient(135deg,#2563eb,#0ea5e9);
            padding:14px 24px;
            border-radius:18px;
            color:white;
            font-weight:800;
            font-size:16px;
            box-shadow:0 0 20px rgba(37,99,235,.25);
        }

        .section-title{
            color:white;
            font-size:38px;
            font-weight:900;
            margin-bottom:25px;
        }

        .tool-card{
            background:
            linear-gradient(145deg, rgba(8,15,35,.98), rgba(15,35,70,.92));

            border:1px solid rgba(96,165,250,.22);
            border-radius:30px;
            padding:35px;
            min-height:260px;
            box-shadow:0 0 35px rgba(37,99,235,.12);
            transition:0.3s;
        }

        .tool-card:hover{
            transform:translateY(-6px);
            box-shadow:0 0 40px rgba(56,189,248,.24);
        }

        .tool-title{
            color:white;
            font-size:34px;
            font-weight:900;
            margin-bottom:22px;
        }

        .tool-text{
            color:#dbeafe;
            font-size:19px;
            line-height:1.7;
            font-weight:700;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="home-wrapper">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-badge">
            NEXT GENERATION AI PLATFORM
        </div>
    """,
    unsafe_allow_html=True,
)

st.image("logoslogan.png", width=560)

st.markdown(
    """
    <div class="hero-text">
        Deine moderne AI Plattform für Chat, Coding,
        Bilder, Videos, Musik und Creator Workflows.
        Schnell. Kreativ. Übersichtlich.
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="pill">
            ⚡ Smart AI
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="pill">
            💎 Pro Workflow
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="pill">
            🚀 Creator Ready
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="pill">
            🎬 Media Suite
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
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
                    und arbeite schneller
                    mit AI Workflows.
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
                    Musikideen und kreative
                    Assets in Sekunden.
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
                    baue virale Hooks
                    und automatisiere
                    deinen Content.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)