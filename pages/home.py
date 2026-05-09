import os
import streamlit as st


def show_logo():
    for name in ["LogoMAIN.png", "LogoMain.png", "logoMAIN.png", "Logo.png"]:
        if os.path.exists(name):
            st.image(name, width=320)
            return


def render_home():
    st.markdown('<div class="home-shell">', unsafe_allow_html=True)

    c1, c2 = st.columns([1.15, 0.85])

    with c1:
        show_logo()

        st.markdown(
            """
            <div class="home-hero">
                <span class="badge">NEXT GENERATION AI PLATFORM</span>

                <h1>MABYTE</h1>

                <h2>Mehr als nur eine AI.</h2>

                <p>
                    Dein persönlicher Begleiter für Ideen, Projekte und Visionen.
                    MABYTE denkt mit, inspiriert dich und hilft dir,
                    Gedanken in echte Ergebnisse zu verwandeln.
                </p>

                <p>
                    Egal ob du programmierst, ein Business aufbaust,
                    Content erschaffst oder neue Möglichkeiten entdeckst:
                    MABYTE begleitet dich auf deinem Weg.
                </p>

                <div class="claim">
                    Schneller. Kreativer. Grenzenloser.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="home-glass-card">
                <div class="orbit">✦</div>
                <h3>BEYOND LIMITS</h3>
                <p>
                    Chat, Coding, Images, Video, Reels, Music und Automation
                    in einer modernen Creator-Plattform.
                </p>

                <div class="mini-stat">
                    <b>24/7</b><span>AI Tools</span>
                </div>

                <div class="mini-stat">
                    <b>PRO</b><span>Creator Workflow</span>
                </div>

                <div class="mini-stat">
                    <b>∞</b><span>Ideas to Reality</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## Was du mit MABYTE machen kannst")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown(
            """
            <div class="modern-feature">
                <div class="feature-icon">💬</div>
                <h3>Smart Chat</h3>
                <p>Chatte mit deiner AI, speichere deinen Verlauf und arbeite schneller.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            """
            <div class="modern-feature">
                <div class="feature-icon">🎬</div>
                <h3>AI Media</h3>
                <p>Erstelle Bilder, Videos, Musik, Prompts und kreative Assets.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            """
            <div class="modern-feature">
                <div class="feature-icon">🚀</div>
                <h3>Creator Tools</h3>
                <p>Plane Reels, baue Workflows und automatisiere deinen Content.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )