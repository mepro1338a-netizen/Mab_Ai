import uuid
import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import spend_tokens, save_usage, get_user, update_tokens
from ui_core import sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


REEL_COST = 25
SONG_COST = 100
MAX_REEL_SECONDS = 7


def ensure_logged_in():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()


def username():
    return st.session_state.get("user")


def user_plan():
    return st.session_state.get("plan", "free")


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user():
    user = get_user(username())
    if user:
        sync_session_user(user)


def can_afford(cost):
    return get_tokens() >= int(cost)


def charge_tokens(tool, prompt, cost):
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
        prompt=prompt,
        tokens_used=int(cost),
        cost_tokens=int(cost),
        api_provider="openai",
        status="charged",
    )

    sync_user()


def refund_tokens(cost, tool, prompt):
    user = get_user(username())

    if not user:
        return

    current = int(user.get("tokens") or 0)
    update_tokens(username(), current + int(cost))

    save_usage(
        username=username(),
        tool=tool,
        prompt=prompt,
        tokens_used=0,
        cost_tokens=-int(cost),
        api_provider="refund",
        status="refunded",
    )

    sync_user()


def ai_generate(prompt):
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
    )

    return response.choices[0].message.content


def render_download(result, prefix):
    filename = f"{prefix}_{uuid.uuid4().hex[:6]}.txt"

    st.download_button(
        "Download",
        data=result.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )


def run_paid_ai(tool, prompt, cost, filename_prefix):
    charge_tokens(tool, prompt, cost)

    try:
        with st.spinner("MaByte generiert..."):
            result = ai_generate(prompt)

        save_usage(
            username=username(),
            tool=tool,
            prompt=prompt,
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


def render_reels_creator():
    ensure_logged_in()

    st.title("AI Content Studio")
    st.caption("Erstelle 7-Sekunden-Reels mit AI. Kostengünstig über OpenAI Text API.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Max Länge", f"{MAX_REEL_SECONDS}s")

    with c2:
        st.metric("Kosten", f"{REEL_COST} Tokens")

    with c3:
        st.metric("Deine Tokens", get_tokens())

    st.divider()

    left, mid, right = st.columns([1.1, 1.2, 0.9], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Creative Brief")

            topic = st.text_area(
                "Thema",
                height=130,
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

    with mid:
        with st.container(border=True):
            st.subheader("Output Design")

            style = st.selectbox(
                "Style",
                [
                    "Fast Cut",
                    "Cinematic",
                    "Aggressive",
                    "Funny",
                    "Premium",
                    "Emotional",
                ],
            )

            voice = st.selectbox(
                "Voice",
                [
                    "Creator",
                    "Narrator",
                    "Coach",
                    "Analyst",
                    "Hype",
                    "News",
                ],
            )

            cta = st.text_input(
                "CTA",
                placeholder="Folge für mehr / Link in Bio / Jetzt testen",
            )

            seconds = st.slider(
                "Videolänge",
                min_value=3,
                max_value=MAX_REEL_SECONDS,
                value=MAX_REEL_SECONDS,
            )

    with right:
        with st.container(border=True):
            st.subheader("7s Struktur")

            st.write("0–2s: Hook")
            st.write("2–5s: Main Point")
            st.write("5–7s: CTA")

            st.info("Ein Reel = ein AI API Call.")

    st.divider()

    if st.button("Reel Package generieren", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle ein professionelles 7-Sekunden-Reel-Package.

WICHTIG:
Das Reel darf maximal {seconds} Sekunden lang sein.
Plane niemals länger als 7 Sekunden.

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

Erstelle exakt diese Struktur:

## Viral Hook

## 7 Second Script
0-2s:
2-5s:
5-7s:

## Scene Plan

## On-Screen Text

## Voiceover

## Caption

## Hashtags

## Thumbnail Text

## Posting Tipp
"""

        run_paid_ai(
            tool="reels",
            prompt=prompt,
            cost=REEL_COST,
            filename_prefix="mabyte_reel",
        )


def render_music_generator():
    ensure_logged_in()

    st.title("Music Studio")
    st.caption("Songs kosten 100 Tokens.")

    c1, c2 = st.columns(2)

    with c1:
        topic = st.text_input("Song Thema")

        genre = st.selectbox(
            "Genre",
            ["Rap", "Trap", "Pop", "EDM", "Phonk", "Afro", "Rock"],
        )

    with c2:
        mood = st.selectbox(
            "Mood",
            ["Viral", "Dark", "Emotional", "Luxury", "Energetic"],
        )

        st.metric("Kosten", f"{SONG_COST} Tokens")

    if st.button("Song Package generieren", use_container_width=True):
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
            cost=SONG_COST,
            filename_prefix="mabyte_song",
        )


def render_coding_ai():
    ensure_logged_in()
    st.title("Developer OS")
    st.info("Coding Workspace kommt als nächstes wieder rein.")


def render_image_ai():
    ensure_logged_in()
    st.title("Creative Workspace")
    st.info("Image Workspace kommt als nächstes wieder rein.")


def render_video_generator():
    ensure_logged_in()
    st.title("Media Studio")
    st.info("Video Generator kommt später. Reels laufen aktuell kostengünstig über 1 Text API Call.")


def render_media(active_tool="reels"):
    ensure_logged_in()

    if active_tool == "coding":
        render_coding_ai()

    elif active_tool == "image":
        render_image_ai()

    elif active_tool == "music":
        render_music_generator()

    elif active_tool == "reels":
        render_reels_creator()

    elif active_tool == "video":
        render_video_generator()

    else:
        render_reels_creator()