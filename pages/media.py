import os
import uuid
import math

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS
from database import spend_tokens, save_usage, get_user
from ui_helpers import require_login, sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


def user_plan():
    return st.session_state.get("plan", "free")


def has_feature(tool):
    plan = user_plan()

    from config import PLANS

    features = PLANS.get(plan, PLANS["free"]).get("features", [])

    return "all" in features or tool in features


def require_feature(tool):
    require_login()

    if not has_feature(tool):
        st.error("Dieses Tool ist in deinem Plan nicht freigeschaltet.")
        st.info("Upgrade deinen Account, um dieses Feature zu nutzen.")
        st.stop()


def get_tokens():
    return int(st.session_state.get("tokens", 0))


def calc_video_cost(seconds):
    base = int(TOKEN_COSTS.get("video_base", 5))
    per_second = int(TOKEN_COSTS.get("video_second", 1))

    return base + math.ceil(seconds * per_second)


def calc_tool_cost(tool, seconds=0):
    if tool == "video":
        return calc_video_cost(seconds)

    return int(TOKEN_COSTS.get(tool, 1))


def charge_tokens(tool, prompt, seconds=0, provider="openai"):
    cost = calc_tool_cost(tool, seconds)

    if get_tokens() < cost:
        st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
        st.stop()

    ok, msg = spend_tokens(st.session_state.get("user"), cost)

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=st.session_state.get("user"),
        tool=tool,
        prompt=prompt,
        tokens_used=cost,
        cost_tokens=cost,
        api_provider=provider,
        status="success",
    )

    user = get_user(st.session_state.get("user"))

    if user:
        sync_session_user(user)

    return cost


def ai_text(prompt):
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY fehlt. Bitte in Railway setzen."

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


def render_output(result, filename_prefix):
    st.success("Fertig generiert.")
    st.markdown(result)

    filename = f"{filename_prefix}_{uuid.uuid4().hex[:6]}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(result)

    with open(filename, "rb") as f:
        st.download_button(
            "⬇️ Download",
            data=f,
            file_name=filename,
            use_container_width=True,
        )


def render_reels_creator():
    require_feature("reels")

    st.header("🎬 Reels Creator")
    st.write("Erstelle virale Hooks, Captions, Szenen und Reels-Konzepte.")

    topic = st.text_input(
        "Thema",
        placeholder="z.B. Wie man mit AI online Geld verdient",
    )

    platform = st.selectbox(
        "Plattform",
        ["TikTok", "Instagram Reels", "YouTube Shorts"],
    )

    style = st.selectbox(
        "Stil",
        ["Viral", "Luxury", "Aggressiv", "Funny", "Professional"],
    )

    if st.button("Reel Konzept generieren", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
        Erstelle ein professionelles virales Reel-Konzept.

        Thema:
        {topic}

        Plattform:
        {platform}

        Stil:
        {style}

        Gib aus:
        - Hook
        - Reel Skript
        - Szenenplan
        - Caption
        - Hashtags
        - Call to Action
        """

        charge_tokens("reels", prompt)

        with st.spinner("MaByte erstellt dein Reel..."):
            result = ai_text(prompt)

        render_output(result, "mabyte_reel")


def render_video_generator():
    require_feature("video")

    st.header("🎞️ AI Video Generator")
    st.write("Generiere professionelle Video-Prompts mit sekundengenauer Tokenberechnung.")

    video_prompt = st.text_area(
        "Video Idee",
        placeholder="z.B. Luxury AI commercial, neon city, cinematic camera...",
        height=130,
    )

    seconds = st.slider(
        "Videolänge in Sekunden",
        min_value=3,
        max_value=120,
        value=15,
        step=1,
    )

    video_style = st.selectbox(
        "Video Stil",
        [
            "Cinematic",
            "Realistisch",
            "Luxury",
            "Cyberpunk",
            "Commercial",
            "Anime",
        ],
    )

    quality = st.selectbox(
        "Qualität",
        [
            "Standard",
            "High",
            "Business Level",
        ],
    )

    base_cost = calc_video_cost(seconds)

    if quality == "High":
        final_cost = math.ceil(base_cost * 1.35)
    elif quality == "Business Level":
        final_cost = math.ceil(base_cost * 1.75)
    else:
        final_cost = base_cost

    st.info(
        f"Kosten: {final_cost} Tokens "
        f"({seconds} Sekunden, {quality})"
    )

    if st.button("Video Prompt generieren", use_container_width=True):
        if not video_prompt:
            st.warning("Bitte Video Idee eingeben.")
            return

        if get_tokens() < final_cost:
            st.error(f"Nicht genug Tokens. Benötigt: {final_cost}, verfügbar: {get_tokens()}")
            return

        prompt = f"""
        Erstelle einen professionellen AI Video Prompt.

        Idee:
        {video_prompt}

        Länge:
        {seconds} Sekunden

        Stil:
        {video_style}

        Qualität:
        {quality}

        Gib aus:
        - Final Video Prompt
        - Szenenablauf pro Abschnitt
        - Kameraeinstellungen
        - Licht
        - Effekte
        - Musikstil
        - Negative Prompt
        """

        ok, msg = spend_tokens(st.session_state.get("user"), final_cost)

        if not ok:
            st.error(msg)
            return

        save_usage(
            username=st.session_state.get("user"),
            tool="video",
            prompt=prompt,
            tokens_used=final_cost,
            cost_tokens=final_cost,
            api_provider="video_prompt",
            status="success",
        )

        user = get_user(st.session_state.get("user"))

        if user:
            sync_session_user(user)

        with st.spinner("MaByte erstellt dein Video-Konzept..."):
            result = ai_text(prompt)

        render_output(result, "mabyte_video")


def render_music_generator():
    require_feature("music")

    st.header("🎵 Music AI")
    st.write("Erstelle Lyrics, Hooks und komplette Song-Konzepte.")

    topic = st.text_input(
        "Song Thema",
        placeholder="z.B. Erfolg, Nachtfahrten, Motivation",
    )

    genre = st.selectbox(
        "Genre",
        ["Rap", "Trap", "Drill", "Pop", "EDM", "Phonk", "R&B"],
    )

    mood = st.selectbox(
        "Mood",
        ["Dark", "Motivational", "Aggressive", "Sad", "Emotional", "Happy"],
    )

    cost = calc_tool_cost("music")
    st.info(f"Kosten: {cost} Tokens")

    if st.button("Song generieren", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
        Erstelle einen kompletten Song.

        Thema:
        {topic}

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
        - Style Beschreibung
        - Suno/Udio Prompt
        """

        charge_tokens("music", prompt)

        with st.spinner("MaByte erstellt deinen Song..."):
            result = ai_text(prompt)

        render_output(result, "mabyte_music")


def render_media(active_tool="reels"):
    require_login()

    st.title("🎨 AI Media Studio")
    st.write("Reels, Videos und Musik mit fairem Token-System.")

    tab_reels, tab_video, tab_music = st.tabs(
        [
            "🎬 Reels Creator",
            "🎞️ Video Generator",
            "🎵 Music AI",
        ]
    )

    with tab_reels:
        render_reels_creator()

    with tab_video:
        render_video_generator()

    with tab_music:
        render_music_generator()