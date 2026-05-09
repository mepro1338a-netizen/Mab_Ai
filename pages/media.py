import streamlit as st
from ui_helpers import require_login, render_download
from database import Database
from openai import OpenAI
import os
import uuid

db = Database()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def render_media():

    require_login()

    st.markdown(
        """
        <style>

        .media-title{
            font-size:58px;
            font-weight:800;
            color:white;
            margin-bottom:5px;
        }

        .media-sub{
            font-size:18px;
            color:#8ea3c7;
            margin-bottom:40px;
        }

        .media-card{
            background: linear-gradient(145deg,#0f172a,#111827);
            border:1px solid rgba(59,130,246,0.25);
            border-radius:28px;
            padding:35px;
            margin-bottom:35px;
            box-shadow:0 0 35px rgba(37,99,235,0.18);
        }

        .media-header{
            font-size:42px;
            font-weight:800;
            color:white;
            margin-bottom:10px;
        }

        .media-desc{
            color:#9db3d8;
            font-size:18px;
            margin-bottom:25px;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"]{
            background:#111827 !important;
            color:white !important;
            border-radius:18px !important;
            border:1px solid #2563eb !important;
        }

        .stButton button{
            width:100%;
            background:linear-gradient(90deg,#2563eb,#1d4ed8);
            color:white;
            border:none;
            border-radius:18px;
            padding:16px;
            font-size:18px;
            font-weight:700;
            transition:0.3s;
        }

        .stButton button:hover{
            transform:scale(1.02);
            box-shadow:0 0 25px rgba(37,99,235,0.4);
        }

        .output-box{
            background:#0b1120;
            border:1px solid rgba(59,130,246,0.3);
            padding:25px;
            border-radius:24px;
            margin-top:25px;
            color:white;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="media-title">AI Creator Studio</div>
        <div class="media-sub">
        Erstelle virale Inhalte, Videos, Hooks, Lyrics und komplette Creator Assets mit AI.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "🎬 Reels Creator",
            "🎥 Video Generator",
            "🎵 Music Generator"
        ]
    )

    # =========================
    # REELS CREATOR
    # =========================

    with tab1:

        st.markdown(
            """
            <div class="media-card">
                <div class="media-header">🎬 AI Reels Creator</div>
                <div class="media-desc">
                    Erstelle virale Reels mit Hook, Skript, Caption,
                    Hashtags und Video-Ideen.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        topic = st.text_input(
            "Reel Thema",
            placeholder="z.B. Wie man mit AI online Geld verdient"
        )

        niche = st.selectbox(
            "Nische",
            [
                "AI",
                "Business",
                "Fitness",
                "Lifestyle",
                "Gaming",
                "Motivation",
                "Social Media",
            ],
        )

        platform = st.selectbox(
            "Plattform",
            [
                "TikTok",
                "Instagram",
                "YouTube Shorts"
            ],
        )

        style = st.selectbox(
            "Stil",
            [
                "Viral",
                "Luxury",
                "Aggressive",
                "Funny",
                "Professional"
            ],
        )

        if st.button("🚀 Reel generieren"):

            if not topic:
                st.warning("Bitte Thema eingeben.")
            else:

                with st.spinner("Mabyte erstellt dein Reel-Konzept..."):

                    prompt = f"""
                    Erstelle ein virales Reel für {platform}.

                    Thema:
                    {topic}

                    Nische:
                    {niche}

                    Stil:
                    {style}

                    Gib aus:

                    - Hook
                    - Vollständiges Reel Skript
                    - Szenen Ideen
                    - Caption
                    - Hashtags
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    )

                    result = response.choices[0].message.content

                    st.markdown(
                        f"""
                        <div class="output-box">
                        {result}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    filename = f"mabyte_reel_{uuid.uuid4().hex[:6]}.txt"

                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(result)

                    render_download(filename)

    # =========================
    # VIDEO GENERATOR
    # =========================

    with tab2:

        st.markdown(
            """
            <div class="media-card">
                <div class="media-header">🎥 AI Video Generator</div>
                <div class="media-desc">
                    Generiere AI Video Prompts für Ads, Reels,
                    Branding und Cinematic Videos.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        video_prompt = st.text_area(
            "Video Prompt",
            placeholder="z.B. Luxury neon commercial with cinematic camera movement..."
        )

        video_style = st.selectbox(
            "Video Modus",
            [
                "Realistisch",
                "Cinematic",
                "Anime",
                "Luxury",
                "Cyberpunk",
                "Commercial",
            ],
        )

        duration = st.selectbox(
            "Videolänge",
            [
                "15 Sekunden",
                "30 Sekunden",
                "60 Sekunden",
            ],
        )

        if st.button("🎬 Video Prompt generieren"):

            if not video_prompt:
                st.warning("Bitte Prompt eingeben.")
            else:

                with st.spinner("Mabyte erstellt dein Video Konzept..."):

                    prompt = f"""
                    Erstelle einen professionellen AI Video Prompt.

                    Thema:
                    {video_prompt}

                    Stil:
                    {video_style}

                    Länge:
                    {duration}

                    Gib aus:

                    - Full AI Prompt
                    - Camera Angles
                    - Lighting
                    - Effects
                    - Music Style
                    - Scene Flow
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    )

                    result = response.choices[0].message.content

                    st.markdown(
                        f"""
                        <div class="output-box">
                        {result}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # =========================
    # MUSIC GENERATOR
    # =========================

    with tab3:

        st.markdown(
            """
            <div class="media-card">
                <div class="media-header">🎵 Music Generator</div>
                <div class="media-desc">
                    Erstelle Lyrics, Hooks, Musikideen und AI Song Konzepte.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        music_topic = st.text_input(
            "Song Thema",
            placeholder="z.B. Nachtfahrten, Erfolg, Motivation..."
        )

        genre = st.selectbox(
            "Genre",
            [
                "Rap",
                "Trap",
                "Pop",
                "Drill",
                "EDM",
                "Phonk",
                "R&B",
            ],
        )

        mood = st.selectbox(
            "Mood",
            [
                "Dark",
                "Motivational",
                "Aggressive",
                "Sad",
                "Emotional",
                "Happy",
            ],
        )

        if st.button("🎵 Song generieren"):

            if not music_topic:
                st.warning("Bitte Thema eingeben.")
            else:

                with st.spinner("Mabyte erstellt deinen Song..."):

                    prompt = f"""
                    Erstelle einen kompletten Song.

                    Thema:
                    {music_topic}

                    Genre:
                    {genre}

                    Mood:
                    {mood}

                    Gib aus:

                    - Songtitel
                    - Hook
                    - Verse
                    - Bridge
                    - Stil Beschreibung
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    )

                    result = response.choices[0].message.content

                    st.markdown(
                        f"""
                        <div class="output-box">
                        {result}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )