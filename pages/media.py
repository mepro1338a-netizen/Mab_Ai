import uuid

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import spend_tokens, save_usage, get_user, update_tokens
from pricing import (
    get_reel_script_cost,
    get_video_cost,
    get_image_cost,
    get_music_cost,
    get_coding_cost,
)
from ui_core import sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)

MAX_REEL_SECONDS = 7


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


def can_afford(cost: int) -> bool:
    return get_tokens() >= int(cost)


def charge_tokens(tool: str, prompt: str, cost: int) -> None:
    if not can_afford(cost):
        st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
        st.stop()

    ok, msg = spend_tokens(username(), int(cost))

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=username(),
        tool=tool,
        prompt=prompt[:1000],
        tokens_used=int(cost),
        cost_tokens=int(cost),
        api_provider="openai",
        status="charged",
    )

    sync_user()


def refund_tokens(cost: int, tool: str, prompt: str) -> None:
    user = get_user(username())

    if not user:
        return

    current = int(user.get("tokens") or 0)
    update_tokens(username(), current + int(cost))

    save_usage(
        username=username(),
        tool=tool,
        prompt=prompt[:1000],
        tokens_used=0,
        cost_tokens=-int(cost),
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
            {
                "role": "user",
                "content": prompt,
            },
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
    font-size: 56px;
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
    margin-bottom: 26px;
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

@media(max-width: 900px) {
    .mb-media-title {
        font-size: 42px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_media_hero(active_tool: str) -> None:
    label_map = {
        "image": "Image AI",
        "video": "Video AI",
        "reels": "Reels Studio",
        "music": "Music AI",
        "coding": "Coding Studio",
    }

    active_label = label_map.get(active_tool, "Media Studio")

    st.markdown(
        f"""
<div class="mb-media-title">{active_label}</div>
<div class="mb-media-sub">Creator Tools für Bilder, Reels, Video, Musik und Code.</div>
""",
        unsafe_allow_html=True,
    )


def render_reels_creator() -> None:
    seconds = MAX_REEL_SECONDS
    cost = get_reel_script_cost(seconds)

    st.markdown('<div class="mb-section-title">Reels Script Package</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.metric("Max Länge", f"{seconds}s")

    with c2:
        st.metric("Kosten", f"{cost} Tokens")

    with c3:
        st.metric("Tokens", get_tokens())

    st.write("")

    left, right = st.columns([1.15, .85], gap="large")

    with left:
        with st.container(border=True):
            topic = st.text_area(
                "Creative Brief",
                height=150,
                placeholder="z.B. Warum Arsenal dieses Jahr gefährlich ist...",
            )

            platform = st.selectbox(
                "Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
            )

            content_type = st.selectbox(
                "Content Typ",
                [
                    "Football Reel",
                    "Viral Reel",
                    "Storytelling",
                    "Educational",
                    "Meme Page",
                    "Personal Brand",
                    "Product Promo",
                ],
            )

    with right:
        with st.container(border=True):
            style = st.selectbox(
                "Style",
                ["Fast Cut", "Cinematic", "Aggressive", "Funny", "Premium", "Emotional"],
            )

            voice = st.selectbox(
                "Voice",
                ["Creator", "Narrator", "Coach", "Analyst", "Hype", "News"],
            )

            cta = st.text_input(
                "CTA",
                placeholder="Folge für mehr / Link in Bio / Jetzt testen",
            )

            st.info("Dieses Modul erzeugt Script, Hook, Caption und Szenenplan.")

    if st.button("Reel Script generieren", width="stretch"):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle ein professionelles {seconds}-Sekunden-Reel-Package.

Thema:
{topic}

Plattform:
{platform}

Content Typ:
{content_type}

Style:
{style}

Voice:
{voice}

CTA:
{cta}

Erstelle exakt:

## Viral Hook
## {seconds} Second Script
## Scene Plan
## On-Screen Text
## Voiceover
## Caption
## Hashtags
## Thumbnail Text
## Posting Tipp
"""

        run_paid_ai(
            tool="reels_script",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_reel_script",
        )


def render_video_generator() -> None:
    st.markdown('<div class="mb-section-title">Reel Video Generator</div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, .85], gap="large")

    with left:
        with st.container(border=True):
            idea = st.text_area(
                "Video Idee",
                height=150,
                placeholder="z.B. Cinematic football promo, fast cuts, neon stadium...",
            )

            provider = st.selectbox(
                "Provider",
                ["kling", "runway"],
            )

            seconds = st.slider(
                "Sekunden",
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

            with_audio = st.checkbox("Mit Audio", value=False)

            cost = get_video_cost(
                provider=provider,
                seconds=seconds,
                quality=quality,
                with_audio=with_audio,
            )

            st.metric("Kosten", f"{cost} Tokens")
            st.metric("Tokens", get_tokens())

            st.info("Echte Video-API wird als nächster Schritt angebunden.")

    if st.button("Video Prompt vorbereiten", width="stretch"):
        if not idea:
            st.warning("Bitte Video Idee eingeben.")
            return

        prompt = f"""
Erstelle einen professionellen Video Generation Prompt.

Provider:
{provider}

Sekunden:
{seconds}

Qualität:
{quality}

Mit Audio:
{with_audio}

Idee:
{idea}

Erstelle:
## Video Prompt
## Kamera Bewegung
## Szenenstruktur
## Licht & Stil
## Negative Prompt
## Caption
## Posting Tipp
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
        prompt = st.text_area(
            "Image Prompt",
            height=150,
            placeholder="z.B. Premium SaaS Dashboard, dark blue purple, gold typography...",
        )

        style = st.selectbox(
            "Style",
            ["Premium SaaS", "Cinematic", "Photorealistic", "Logo", "Thumbnail", "Social Ad"],
        )

        quality = st.selectbox(
            "Qualität",
            ["standard", "hd"],
        )

        size = st.selectbox(
            "Größe",
            ["1024", "2048"],
        )

        cost = get_image_cost(quality=quality, size=size)

        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Image Prompt vorbereiten", width="stretch"):
        if not prompt:
            st.warning("Bitte Prompt eingeben.")
            return

        full_prompt = f"""
Optimiere diesen Image Prompt für OpenAI Image Generation.

Style:
{style}

Qualität:
{quality}

Größe:
{size}

Prompt:
{prompt}

Erstelle:
## Final Image Prompt
## Negative Prompt
## Format Empfehlung
## Social Usage
"""

        run_paid_ai(
            tool="image_prompt",
            prompt=full_prompt,
            cost=cost,
            filename_prefix="mabyte_image_prompt",
        )


def render_music_generator() -> None:
    st.markdown('<div class="mb-section-title">Music AI</div>', unsafe_allow_html=True)

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        with st.container(border=True):
            topic = st.text_input("Song Thema")

            genre = st.selectbox(
                "Genre",
                ["Rap", "Trap", "Pop", "EDM", "Phonk", "Afro", "Rock"],
            )

            length = st.selectbox(
                "Länge",
                ["short", "medium", "long"],
            )

    with right:
        with st.container(border=True):
            mood = st.selectbox(
                "Mood",
                ["Viral", "Dark", "Emotional", "Luxury", "Energetic"],
            )

            cost = get_music_cost(length=length)

            st.metric("Kosten", f"{cost} Tokens")
            st.metric("Tokens", get_tokens())

    if st.button("Song Package generieren", width="stretch"):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle ein professionelles Song Package.

Thema:
{topic}

Genre:
{genre}

Mood:
{mood}

Länge:
{length}

Erstelle:

## Song Title
## Hook
## Chorus
## Verse 1
## Verse 2
## Lyrics
## Music Prompt
## Social Caption
## Hashtags
"""

        run_paid_ai(
            tool="music",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_song",
        )


def render_coding_ai() -> None:
    st.markdown('<div class="mb-section-title">Coding Studio</div>', unsafe_allow_html=True)

    with st.container(border=True):
        task = st.text_area(
            "Was soll MaByte bauen oder fixen?",
            height=160,
            placeholder="z.B. Baue mir eine Streamlit Page mit Login, Cards und API Call...",
        )

        complexity = st.selectbox(
            "Komplexität",
            ["normal", "advanced", "fullstack"],
        )

        stack = st.selectbox(
            "Stack",
            ["Python", "Streamlit", "HTML/CSS", "JavaScript", "API Backend", "Debugging"],
        )

        cost = get_coding_cost(complexity=complexity)

        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Code Assistant starten", width="stretch"):
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
## Architektur
## Schrittfolge
## Code
## Test
## Deployment Hinweis
"""

        run_paid_ai(
            tool="coding",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_code",
        )


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