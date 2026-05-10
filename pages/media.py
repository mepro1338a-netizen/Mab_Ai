import os
import uuid
import streamlit as st
from openai import OpenAI

from ui_helpers import require_login, render_download


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ai_text(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def output_result(result, filename_prefix):
    st.markdown(
        f"""
        <div class="output-box">
            {result}
        </div>
        """,
        unsafe_allow_html=True,
    )

    filename = f"{filename_prefix}_{uuid.uuid4().hex[:6]}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(result)

    render_download(filename)


def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="media-card">
            <div class="media-header">{title}</div>
            <div class="media-desc">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_media(active_tool="reels"):
    require_login()

    st.markdown(
        """
        <style>
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
            margin-bottom:5px;
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
            line-height:1.7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if active_tool == "coding":
        render_coding_page()

    elif active_tool == "image":
        render_image_page()

    elif active_tool == "music":
        render_music_page()

    elif active_tool == "reels":
        render_reels_page()

    elif active_tool == "video":
        render_video_page()

    else:
        render_reels_page()


def render_coding_page():
    page_header(
        "💻 Coding AI",
        "Erstelle Code, debugge Fehler und lass dir Projekte erklären.",
    )

    task = st.text_area(
        "Was soll Mabyte programmieren oder fixen?",
        height=180,
        placeholder="z.B. Fixe diesen Python Fehler oder erstelle eine Login-Funktion...",
    )

    language = st.selectbox(
        "Sprache / Bereich",
        ["Python", "Streamlit", "JavaScript", "HTML/CSS", "SQL", "Allgemein"],
    )

    if st.button("💻 Code generieren"):
        if not task.strip():
            st.warning("Bitte Aufgabe eingeben.")
            return

        with st.spinner("Mabyte schreibt deinen Code..."):
            result = ai_text(
                f"""
Du bist ein professioneller Coding-Assistent.

Sprache/Bereich:
{language}

Aufgabe:
{task}

Gib eine klare Lösung mit vollständigem Code, falls möglich.
"""
            )

        output_result(result, "mabyte_code")


def render_image_page():
    page_header(
        "🎨 Image Generator",
        "Erstelle starke Bild-Prompts für AI Art, Thumbnails, Ads und Branding.",
    )

    idea = st.text_area(
        "Bildidee",
        height=160,
        placeholder="z.B. Futuristisches AI Dashboard, neon blue, luxury SaaS style...",
    )

    style = st.selectbox(
        "Bildstil",
        ["Realistisch", "Cinematic", "Luxury", "Cyberpunk", "Anime", "3D Render", "Minimalistisch"],
    )

    format_type = st.selectbox(
        "Format",
        ["16:9", "9:16", "1:1", "4:5"],
    )

    if st.button("🎨 Bild-Prompt generieren"):
        if not idea.strip():
            st.warning("Bitte Bildidee eingeben.")
            return

        with st.spinner("Mabyte erstellt deinen Bild-Prompt..."):
            result = ai_text(
                f"""
Erstelle einen professionellen AI Image Prompt.

Bildidee:
{idea}

Stil:
{style}

Format:
{format_type}

Gib aus:
- Final Prompt
- Negative Prompt
- Licht
- Kamera
- Details
"""
            )

        output_result(result, "mabyte_image_prompt")


def render_music_page():
    page_header(
        "🎵 Music Generator",
        "Erstelle Lyrics, Hooks, Musikideen und komplette Song-Konzepte.",
    )

    music_topic = st.text_input(
        "Song Thema",
        placeholder="z.B. Nachtfahrten, Erfolg, Motivation...",
    )

    genre = st.selectbox(
        "Genre",
        ["Rap", "Trap", "Pop", "Drill", "EDM", "Phonk", "R&B"],
    )

    mood = st.selectbox(
        "Mood",
        ["Dark", "Motivational", "Aggressive", "Sad", "Emotional", "Happy"],
    )

    if st.button("🎵 Song generieren"):
        if not music_topic.strip():
            st.warning("Bitte Thema eingeben.")
            return

        with st.spinner("Mabyte erstellt deinen Song..."):
            result = ai_text(
                f"""
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
- Verse 1
- Verse 2
- Bridge
- Stil Beschreibung
"""
            )

        output_result(result, "mabyte_song")


def render_reels_page():
    page_header(
        "🎬 AI Reels Creator",
        "Erstelle virale Reels mit Hook, Skript, Caption, Hashtags und Video-Ideen.",
    )

    topic = st.text_input(
        "Reel Thema",
        placeholder="z.B. Wie man mit AI online Geld verdient",
    )

    niche = st.selectbox(
        "Nische",
        ["AI", "Business", "Fitness", "Lifestyle", "Gaming", "Motivation", "Social Media"],
    )

    platform = st.selectbox(
        "Plattform",
        ["TikTok", "Instagram", "YouTube Shorts"],
    )

    style = st.selectbox(
        "Stil",
        ["Viral", "Luxury", "Aggressive", "Funny", "Professional"],
    )

    if st.button("🚀 Reel generieren"):
        if not topic.strip():
            st.warning("Bitte Thema eingeben.")
            return

        with st.spinner("Mabyte erstellt dein Reel-Konzept..."):
            result = ai_text(
                f"""
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
- AI Video Prompt
"""
            )

        output_result(result, "mabyte_reel")


def render_video_page():
    page_header(
        "🎥 AI Video Generator",
        "Generiere AI Video Prompts für Ads, Reels, Branding und Cinematic Videos.",
    )

    video_prompt = st.text_area(
        "Video Prompt",
        height=170,
        placeholder="z.B. Luxury neon commercial with cinematic camera movement...",
    )

    video_style = st.selectbox(
        "Video Modus",
        ["Realistisch", "Cinematic", "Anime", "Luxury", "Cyberpunk", "Commercial"],
    )

    duration = st.selectbox(
        "Videolänge",
        ["15 Sekunden", "30 Sekunden", "60 Sekunden"],
    )

    if st.button("🎬 Video Prompt generieren"):
        if not video_prompt.strip():
            st.warning("Bitte Prompt eingeben.")
            return

        with st.spinner("Mabyte erstellt dein Video Konzept..."):
            result = ai_text(
                f"""
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
            )

        output_result(result, "mabyte_video_prompt")