import uuid

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import spend_tokens, save_usage, get_user, update_tokens
from pricing import (
    get_reel_script_cost,
    get_reel_automation_cost,
    get_video_cost,
    get_image_cost,
    get_music_cost,
    get_coding_cost,
)
from ui_core import sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


def ensure_logged_in() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()


def username() -> str:
    return str(st.session_state.get("user") or "")


def get_tokens() -> int:
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user() -> None:
    user = get_user(username())
    if user:
        sync_session_user(user)


def charge_tokens(tool: str, prompt: str, cost: int) -> None:
    if get_tokens() < cost:
        st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
        st.stop()

    ok, msg = spend_tokens(username(), cost)

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=username(),
        tool=tool,
        prompt=prompt[:1000],
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="openai",
        status="charged",
    )

    sync_user()


def refund_tokens(cost: int, tool: str, prompt: str) -> None:
    user = get_user(username())

    if not user:
        return

    current = int(user.get("tokens") or 0)
    update_tokens(username(), current + cost)

    save_usage(
        username=username(),
        tool=tool,
        prompt=prompt[:1000],
        tokens_used=0,
        cost_tokens=-cost,
        api_provider="refund",
        status="refunded",
    )

    sync_user()


def ai_generate(prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY fehlt.")

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Du bist MaByte, ein professioneller AI Creator Assistent.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_download(result: str, prefix: str) -> None:
    filename = f"{prefix}_{uuid.uuid4().hex[:6]}.txt"

    st.download_button(
        "Download",
        data=result.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        width="stretch",
    )


def run_paid_ai(tool: str, prompt: str, cost: int, filename_prefix: str) -> None:
    charge_tokens(tool, prompt, cost)

    try:
        with st.spinner("MaByte generiert..."):
            result = ai_generate(prompt)

        save_usage(
            username=username(),
            tool=tool,
            prompt=prompt[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider="openai",
            status="success",
        )

        st.success("Fertig generiert.")
        st.markdown(result)
        render_download(result, filename_prefix)

    except Exception as e:
        refund_tokens(cost, tool, prompt)
        st.error(f"Fehler: {e}")


def media_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1180px !important;
    padding-top: 26px !important;
    padding-bottom: 90px !important;
}

.mb-media-title {
    text-align: center;
    font-size: 54px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -3px;
    margin-top: 12px;
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-media-sub {
    text-align: center;
    margin-top: 10px;
    margin-bottom: 24px;
    color: #cbd5e1 !important;
    font-size: 16px;
    font-weight: 800;
}

.mb-section-title {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.90), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.16) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 42px rgba(0,0,0,.22) !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(15,10,28,.96) !important;
    border: 1px solid rgba(168,85,247,.28) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: rgba(255,231,163,.55) !important;
}

.stButton > button {
    min-height: 48px !important;
    border-radius: 16px !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.20), transparent 34%),
        linear-gradient(145deg, rgba(36,8,56,.98), rgba(12,3,25,.98)) !important;
    border: 1px solid rgba(168,85,247,.32) !important;
    color: #ffe7a3 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
    box-shadow: 0 10px 24px rgba(0,0,0,.18) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(255,231,163,.34) !important;
    box-shadow: 0 0 24px rgba(168,85,247,.25) !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(18,14,34,.88), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.18) !important;
    border-radius: 20px !important;
    padding: 17px !important;
}

[data-testid="metric-container"] label {
    color: #c084fc !important;
    font-weight: 1000 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

div[data-testid="stAlert"] {
    background: rgba(30,20,70,.72) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_media_hero(active_tool: str) -> None:
    labels = {
        "image": "Image AI",
        "video": "Video AI",
        "reels": "Reels Studio",
        "music": "Music AI",
        "coding": "Coding Studio",
    }

    st.markdown(
        f"""
<div class="mb-media-title">{labels.get(active_tool, "Media Studio")}</div>
<div class="mb-media-sub">Creator Tools für Reels, Video, Bilder, Musik und Code.</div>
""",
        unsafe_allow_html=True,
    )


def render_reels_creator() -> None:
    st.markdown('<div class="mb-section-title">Premium Reels Studio</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Reel Modus",
        ["Script Package", "Automation Flow"],
        horizontal=True,
    )

    if mode == "Script Package":
        render_reel_script_package()
    else:
        render_reel_automation_flow()


def render_reel_script_package() -> None:
    seconds = st.slider("Reel Länge", min_value=5, max_value=15, value=7)
    cost = get_reel_script_cost(seconds)

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Kosten", f"{cost} Tokens")

    with m2:
        st.metric("Länge", f"{seconds}s")

    with m3:
        st.metric("Tokens", get_tokens())

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        with st.container(border=True):
            topic = st.text_area(
                "Reel Idee",
                height=150,
                placeholder="z.B. Warum Arsenal dieses Jahr gefährlich ist...",
            )

            audience = st.selectbox(
                "Zielgruppe",
                [
                    "Football Fans",
                    "TikTok Audience",
                    "Business Audience",
                    "Luxury Audience",
                    "Creators",
                    "Gen Z",
                    "Meme Audience",
                ],
            )

            platform = st.selectbox(
                "Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
            )

            reel_type = st.selectbox(
                "Reel Kategorie",
                [
                    "Football Edit",
                    "Faceless Storytelling",
                    "Luxury Reel",
                    "Meme Reel",
                    "Motivation Reel",
                    "AI News",
                    "Business Reel",
                    "Personal Brand",
                    "Educational",
                ],
            )

    with right:
        with st.container(border=True):
            template = st.selectbox(
                "Template",
                [
                    "Football TikTok",
                    "Fast Meme Edit",
                    "Dark Cinematic",
                    "News Style",
                    "Luxury Edit",
                    "Alex Hormozi",
                    "Iman Gadzhi",
                ],
            )

            style = st.selectbox(
                "Style",
                ["Aggressive", "Fast Cut", "Cinematic", "Emotional", "Premium", "Funny"],
            )

            voice = st.selectbox(
                "Voice",
                ["Narrator", "Creator", "Coach", "Analyst", "Hype", "News Reporter"],
            )

            cta = st.text_input("CTA", placeholder="Folge für mehr / Link in Bio")

            st.info("Erzeugt Script, Hook, Szenenplan, Caption, Hashtags und Posting-Tipp.")

    if st.button("Premium Reel Script generieren", width="stretch"):
        if not topic:
            st.warning("Bitte Reel Idee eingeben.")
            return

        prompt = f"""
Du bist MaByte Reels Studio.

Erstelle ein hochwertiges virales Reel Script.

Thema:
{topic}

Plattform:
{platform}

Länge:
{seconds} Sekunden

Kategorie:
{reel_type}

Template:
{template}

Style:
{style}

Voice:
{voice}

Zielgruppe:
{audience}

CTA:
{cta}

Erstelle exakt:

# Viral Score
# Hook Strength
# Retention Score
# Viral Hook
# Full Script
# Scene Breakdown
# B-Roll Ideas
# On Screen Text
# Caption
# Hashtags
# Posting Strategy
# Best Posting Time
# Thumbnail Text
# CTA
"""

        run_paid_ai(
            tool="premium_reels_script",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_reel_script",
        )


def render_reel_automation_flow() -> None:
    left, right = st.columns([1.2, .8], gap="large")

    with left:
        with st.container(border=True):
            idea = st.text_area(
                "Reel Video Idee",
                height=150,
                placeholder="z.B. 7 Sekunden Football Reel mit Stadion, schnellen Cuts und Hook...",
            )

            platform = st.selectbox(
                "Posting Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
            )

            provider = st.selectbox(
                "Video Provider",
                ["kling", "runway"],
            )

            seconds = st.slider(
                "Videolänge",
                min_value=5,
                max_value=15,
                value=7,
            )

    with right:
        with st.container(border=True):
            quality = st.selectbox(
                "Qualität",
                ["standard", "premium", "cinematic"],
            )

            with_audio = st.checkbox("Audio / Voice vorbereiten", value=True)
            auto_caption = st.checkbox("Caption automatisch erzeugen", value=True)
            auto_schedule = st.checkbox("Posting vorbereiten", value=True)

            cost = get_reel_automation_cost(
                seconds=seconds,
                provider=provider,
                quality=quality,
                with_audio=with_audio,
                auto_caption=auto_caption,
                auto_schedule=auto_schedule,
            )

            st.metric("Sicherer Preis", f"{cost} Tokens")
            st.metric("Deine Tokens", get_tokens())

            st.info("Dieser Preis enthält Sicherheitsaufschlag, damit API-Kosten gedeckt bleiben.")

    if st.button("Automation Flow vorbereiten", width="stretch"):
        if not idea:
            st.warning("Bitte Reel Video Idee eingeben.")
            return

        prompt = f"""
Du bist MaByte Reel Automation Engine.

Baue einen vollständigen Automation Flow für ein Reel.

Idee:
{idea}

Plattform:
{platform}

Provider:
{provider}

Länge:
{seconds} Sekunden

Qualität:
{quality}

Audio:
{with_audio}

Auto Caption:
{auto_caption}

Posting Vorbereitung:
{auto_schedule}

Erstelle exakt:

# API Cost Safety Check
# Final Video Prompt
# Shot List
# Motion Direction
# Voiceover Script
# Caption
# Hashtags
# Thumbnail Text
# Posting Time
# Automation Steps
# Quality Checklist
# Retry Rules
# User Delivery Package
"""

        run_paid_ai(
            tool="reel_automation_flow",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_reel_automation",
        )


def render_video_generator() -> None:
    st.markdown('<div class="mb-section-title">Video AI</div>', unsafe_allow_html=True)

    with st.container(border=True):
        idea = st.text_area(
            "Video Idee",
            height=150,
            placeholder="z.B. Cinematic football promo, fast cuts, neon stadium...",
        )

        provider = st.selectbox("Provider", ["kling", "runway"])
        seconds = st.slider("Sekunden", min_value=5, max_value=15, value=7)
        quality = st.selectbox("Qualität", ["standard", "premium", "cinematic"])
        with_audio = st.checkbox("Mit Audio", value=False)

        cost = get_video_cost(
            provider=provider,
            seconds=seconds,
            quality=quality,
            with_audio=with_audio,
        )

        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Video Prompt vorbereiten", width="stretch"):
        if not idea:
            st.warning("Bitte Video Idee eingeben")
            return

        prompt = f"""
Erstelle einen professionellen Video Generation Prompt.

Provider:
{provider}

Sekunden:
{seconds}

Qualität:
{quality}

Audio:
{with_audio}

Idee:
{idea}

Erstelle:
# Video Prompt
# Camera Movement
# Scene Structure
# Lighting
# Negative Prompt
# Caption
# Quality Checklist
"""

        run_paid_ai(
            tool="video_prompt",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_video_prompt",
        )


def render_image_ai() -> None:
    st.markdown('<div class="mb-section-title">Image AI</div>', unsafe_allow_html=True)

    with st.container(border=True):
        prompt = st.text_area("Image Prompt", height=150)
        quality = st.selectbox("Qualität", ["standard", "hd"])
        size = st.selectbox("Größe", ["1024", "2048"])
        cost = get_image_cost(quality=quality, size=size)

        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Image Prompt vorbereiten", width="stretch"):
        if not prompt:
            st.warning("Bitte Prompt eingeben.")
            return

        full_prompt = f"""
Optimiere diesen Image Prompt.

Qualität:
{quality}

Größe:
{size}

Prompt:
{prompt}

Erstelle:
# Final Image Prompt
# Negative Prompt
# Format Empfehlung
# Social Usage
"""

        run_paid_ai("image_prompt", full_prompt, cost, "mabyte_image_prompt")


def render_music_generator() -> None:
    st.markdown('<div class="mb-section-title">Music AI</div>', unsafe_allow_html=True)

    with st.container(border=True):
        topic = st.text_input("Song Thema")
        genre = st.selectbox("Genre", ["Rap", "Trap", "Pop", "EDM", "Phonk", "Afro", "Rock"])
        length = st.selectbox("Länge", ["short", "medium", "long"])
        mood = st.selectbox("Mood", ["Viral", "Dark", "Emotional", "Luxury", "Energetic"])
        cost = get_music_cost(length=length)

        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Song Package generieren", width="stretch"):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle ein Song Package.

Thema:
{topic}

Genre:
{genre}

Mood:
{mood}

Länge:
{length}

Erstelle:
# Song Title
# Hook
# Chorus
# Verse
# Lyrics
# Music Prompt
# Social Caption
# Hashtags
"""

        run_paid_ai("music", prompt, cost, "mabyte_song")


def render_coding_ai() -> None:
    st.markdown('<div class="mb-section-title">Coding Studio</div>', unsafe_allow_html=True)

    with st.container(border=True):
        task = st.text_area("Was soll MaByte bauen oder fixen?", height=160)
        complexity = st.selectbox("Komplexität", ["normal", "advanced", "fullstack"])
        stack = st.selectbox("Stack", ["Python", "Streamlit", "HTML/CSS", "JavaScript", "API Backend"])
        cost = get_coding_cost(complexity=complexity)

        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Code Assistant starten:", width="stretch"):
        if not task:
            st.warning("Bitte Aufgabe eingeben.")
            return

        prompt = f"""
Du bist MaByte Coding Studio.

Stack:
{stack}

Komplexität:
{complexity}

Aufgabe:
{task}

Antworte mit:
# Architektur
# Schrittfolge
# Code
# Test
# Deployment Hinweis
"""

        run_paid_ai("coding", prompt, cost, "mabyte_code")


def render_media(active_tool: str = "reels") -> None:
    ensure_logged_in()
    media_css()
    render_media_hero(active_tool)

    if active_tool == "coding":
        render_coding_ai()
    elif active_tool == "image":
        render_image_ai()
    elif active_tool == "music":
        render_music_generator()
    elif active_tool == "video":
        render_video_generator()
    elif active_tool == "reels":
        render_reels_creator()
    else:
        render_reels_creator()