import streamlit as st
from datetime import datetime

from auth import require_login
from subscriptions import can_use
from tokens import TOKEN_COSTS
from ai_runner import run_ai_task
from video_generator import generate_video
from ui_helpers import render_download

from reels_service import generate_reel_plan
from reels_db import init_reels_table, save_reel, list_reels
from reels_scheduler import (
    init_scheduler_table,
    schedule_reel,
    list_scheduled_reels,
)


# =========================
# VIDEO GENERATOR
# =========================

def render_video_page():
    require_login()

    if not can_use("grand"):
        st.warning("Dieses Feature benötigt mindestens GRAND.")
        st.stop()

    cost = TOKEN_COSTS.get("video", 150)

    st.markdown(
        """
        <div class="tool-hero video-hero">
            <div>
                <span class="badge">GRAND FEATURE</span>
                <h1>🎬 AI Video Studio</h1>
                <p>
                    Erstelle professionelle Videos für Reels, Ads,
                    Branding, Produktvideos und Social Media Kampagnen.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([2, 1])

    with left:
        prompt = st.text_area(
            "Video Prompt",
            key="video_prompt",
            height=220,
            placeholder=(
                "Beschreibe dein Video: Szene, Kamera, Licht, "
                "Bewegung, Stimmung, Produkt, Zielgruppe..."
            ),
        )

        video_mode = st.selectbox(
            "Video Modus",
            [
                "Realistisch",
                "Cinematic",
                "TikTok/Reel",
                "Luxury Ad",
                "Produktvideo",
                "3D Animation",
                "Anime",
            ],
            key="video_mode",
        )

        camera_style = st.selectbox(
            "Kamera Stil",
            [
                "Smooth cinematic camera movement",
                "Slow zoom in",
                "Handheld realistic motion",
                "Drone shot",
                "Product close-up",
                "Fast social media cuts",
            ],
            key="video_camera_style",
        )

        aspect_ratio = st.selectbox(
            "Format",
            [
                "9:16 Vertical Reel",
                "16:9 YouTube",
                "1:1 Square",
            ],
            key="video_aspect_ratio",
        )

    with right:
        st.markdown(
            f"""
            <div class="tool-side-card">
                <h3>⚡ Video Setup</h3>

                <p><b>Modus:</b> Professionelle AI-Generierung</p>
                <p><b>Kosten:</b> {cost} Tokens</p>
                <p><b>Ideal für:</b> Reels, Ads, Produktvideos</p>

                <hr>

                <p class="muted">
                    Tipp: Je genauer Szene, Kamera und Stil beschrieben sind,
                    desto besser wird das Ergebnis.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    mode_prompts = {
        "Realistisch": (
            "Ultra realistic, natural lighting, realistic humans, "
            "real camera footage, high detail."
        ),
        "Cinematic": (
            "Cinematic movie scene, dramatic lighting, smooth camera movement, "
            "premium film look."
        ),
        "TikTok/Reel": (
            "Vertical viral social media reel, fast cuts, trendy pacing, "
            "hook in first second."
        ),
        "Luxury Ad": (
            "Luxury advertisement, elegant lighting, premium brand visuals, "
            "high-end commercial."
        ),
        "Produktvideo": (
            "Professional product commercial, clean studio lighting, "
            "product close-ups."
        ),
        "3D Animation": (
            "High quality 3D animated video, detailed rendering, smooth motion."
        ),
        "Anime": (
            "Anime style animation, vibrant colors, smooth anime motion."
        ),
    }

    final_prompt = f"""
{mode_prompts[video_mode]}

Camera:
{camera_style}

Format:
{aspect_ratio}

User Prompt:
{prompt}
"""

    if st.button("🚀 Video generieren", key="generate_video_btn"):
        if not prompt.strip():
            st.error("Bitte Video Prompt eingeben.")
            return

        with st.spinner("Video wird generiert. Das kann etwas dauern..."):
            success, result, updated_user = run_ai_task(
                username=st.session_state.user,
                tool="video",
                prompt=final_prompt,
                provider="replicate",
                generator_func=generate_video,
            )

        if success:
            st.session_state.last_video_path = result

            if updated_user:
                st.session_state.tokens = updated_user["tokens"]

            st.success("Video erfolgreich generiert.")
        else:
            st.error(result)

    if st.session_state.get("last_video_path"):
        st.markdown('<div class="result-box">', unsafe_allow_html=True)

        st.subheader("🎞️ Ergebnis")

        if str(st.session_state.last_video_path).startswith("http"):
            st.video(st.session_state.last_video_path)

            st.markdown(
                f"[Video öffnen]({st.session_state.last_video_path})"
            )
        else:
            st.video(st.session_state.last_video_path)

            render_download(
                st.session_state.last_video_path,
                "Video herunterladen",
            )

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# REELS GENERATOR
# =========================

def render_reels_page():
    require_login()

    if not can_use("pro"):
        st.warning("Dieses Feature benötigt mindestens PRO.")
        st.stop()

    init_reels_table()
    init_scheduler_table()

    st.markdown(
        """
        <div class="tool-hero reels-hero">
            <div>
                <span class="badge">PRO FEATURE</span>

                <h1>🎞️ AI Reels Studio</h1>

                <p>
                    Plane, schreibe und speichere virale Reels
                    mit Hook, Skript, Caption, Hashtags und Video-Prompt.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([2, 1])

    with left:
        topic = st.text_input(
            "Reel Thema",
            placeholder="z.B. Wie man mit AI online Geld verdient",
            key="reel_topic",
        )

        c1, c2 = st.columns(2)

        with c1:
            niche = st.selectbox(
                "Nische",
                [
                    "AI",
                    "Business",
                    "Fitness",
                    "Gaming",
                    "Luxury",
                    "Motivation",
                    "Fashion",
                    "Food",
                    "Tech",
                ],
                key="reel_niche",
            )

            platform = st.selectbox(
                "Plattform",
                [
                    "TikTok",
                    "Instagram Reels",
                    "YouTube Shorts",
                ],
                key="reel_platform",
            )

        with c2:
            style = st.selectbox(
                "Stil",
                [
                    "Viral",
                    "Cinematic",
                    "Luxury",
                    "Motivational",
                    "Funny",
                    "Educational",
                    "Dark Aesthetic",
                ],
                key="reel_style",
            )

            duration = st.selectbox(
                "Dauer",
                [15, 30, 45, 60],
                key="reel_duration",
            )

        schedule_enabled = st.checkbox(
            "Automatisch posten planen",
            key="schedule_enabled",
        )

        scheduled_date = None
        scheduled_time = None

        if schedule_enabled:
            d1, d2 = st.columns(2)

            with d1:
                scheduled_date = st.date_input(
                    "Datum",
                    key="scheduled_date",
                )

            with d2:
                scheduled_time = st.time_input(
                    "Uhrzeit",
                    key="scheduled_time",
                )

    with right:
        st.markdown(
            """
            <div class="tool-side-card">
                <h3>📱 Reel Pipeline</h3>

                <p>✅ Hook</p>
                <p>✅ Szene-für-Szene Skript</p>
                <p>✅ Voiceover</p>
                <p>✅ Caption</p>
                <p>✅ Hashtags</p>
                <p>✅ Video Prompt</p>

                <hr>

                <p class="muted">
                    Später verbinden wir hier Auto-Posting
                    für TikTok, Instagram und YouTube Shorts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("🚀 Reel Konzept generieren", key="generate_reel_btn"):
        if not topic.strip():
            st.error("Bitte ein Thema eingeben.")
            return

        with st.spinner("Mabyte erstellt dein virales Reel-Konzept..."):
            success, result = generate_reel_plan(
                topic,
                niche,
                platform,
                style,
                duration,
            )

        if success:
            st.markdown("### ✨ Dein Reel Konzept")

            st.markdown(
                f"""
                <div class="result-box">
                    {result}
                </div>
                """,
                unsafe_allow_html=True,
            )

            save_reel(
                st.session_state.user,
                topic,
                niche,
                platform,
                style,
                duration,
                result,
            )

            st.success("Reel Konzept gespeichert.")

            if (
                schedule_enabled
                and scheduled_date
                and scheduled_time
            ):
                scheduled_datetime = datetime.combine(
                    scheduled_date,
                    scheduled_time,
                )

                schedule_reel(
                    st.session_state.user,
                    platform,
                    result,
                    scheduled_datetime,
                )

                st.success("Reel wurde geplant.")

            st.download_button(
                "⬇️ Reel Konzept herunterladen",
                data=result,
                file_name="Mabyte_reel_konzept.txt",
                mime="text/plain",
                use_container_width=True,
            )

        else:
            st.error(result)

    st.markdown("### 📂 Gespeicherte Reels")

    saved = list_reels(st.session_state.user)

    if saved:
        for reel in saved[:10]:
            with st.expander(
                f"🎞️ {reel['topic']} · "
                f"{reel['platform']} · "
                f"{reel['status']}"
            ):
                st.markdown(reel["content"])
    else:
        st.info("Noch keine gespeicherten Reels.")

    st.markdown("### 📅 Geplante Reels")

    scheduled = list_scheduled_reels(st.session_state.user)

    if scheduled:
        for reel in scheduled[:10]:
            with st.expander(
                f"📅 {reel['platform']} · "
                f"{reel['scheduled_time']} · "
                f"{reel['status']}"
            ):
                st.markdown(reel["content"])
    else:
        st.info("Keine geplanten Reels.")