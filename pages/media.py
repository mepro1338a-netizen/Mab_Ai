import uuid
import math
from datetime import datetime

import streamlit as st
from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_TEXT_MODEL,
    TOKEN_COSTS,
    PLANS,
    DAILY_VIDEO_LIMITS,
)

from database import (
    spend_tokens,
    save_usage,
    get_user,
    update_tokens,
    list_usage,
)

from ui_helpers import require_login, sync_session_user

from queue_manager import create_job, list_user_jobs
from abuse_guard import validate_request
from costs import record_cost, emergency_cost_limit_reached

from social_integrations import (
    render_social_connect_panel,
    get_selected_platforms,
    build_auto_posting_note,
    can_use_auto_posting,
)


client = OpenAI(api_key=OPENAI_API_KEY)


def username():
    return st.session_state.get("user")


def user_plan():
    return st.session_state.get("plan", "free")


def plan_features():
    return PLANS.get(user_plan(), PLANS["free"]).get("features", [])


def has_feature(tool):
    features = plan_features()
    return "all" in features or tool in features


def require_feature(tool):
    require_login()

    if not has_feature(tool):
        st.error("Dieses Tool ist in deinem Plan nicht freigeschaltet.")
        st.info("Upgrade deinen Account, um dieses Feature zu nutzen.")
        st.stop()


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user():
    user = get_user(username())
    if user:
        sync_session_user(user)


def get_quality_multiplier(quality):
    if quality == "High":
        return float(TOKEN_COSTS.get("video_quality_high", 1.35))
    if quality == "Business Level":
        return float(TOKEN_COSTS.get("video_quality_business", 1.75))
    return 1.0


def calc_video_cost(seconds, quality="Standard"):
    base = int(TOKEN_COSTS.get("video_base", 10))
    per_second = int(TOKEN_COSTS.get("video_second", 5))
    raw = base + (int(seconds) * per_second)
    return int(math.ceil(raw * get_quality_multiplier(quality)))


def calc_tool_cost(tool, seconds=0, quality="Standard"):
    if tool == "video":
        return calc_video_cost(seconds, quality)

    if tool == "reels_video":
        return calc_video_cost(seconds, quality) + int(TOKEN_COSTS.get("reels", 20))

    return int(TOKEN_COSTS.get(tool, 1))


def daily_video_limit():
    return int(DAILY_VIDEO_LIMITS.get(user_plan(), 0))


def videos_used_today():
    logs = list_usage(username())
    today = datetime.utcnow().date().isoformat()
    count = 0

    for log in logs:
        tool = str(log.get("tool", ""))
        created = str(log.get("created_at", ""))
        status = str(log.get("status", ""))

        if created.startswith(today) and tool in ["video", "reels_video"] and status in ["charged", "success"]:
            count += 1

    return count


def check_video_limit():
    limit = daily_video_limit()

    if limit <= 0:
        st.error("Dein aktueller Plan erlaubt keine Video-Generierungen.")
        st.stop()

    used = videos_used_today()

    if used >= limit:
        st.error(f"Tageslimit erreicht: {used}/{limit} Videos heute.")
        st.stop()

    return used, limit


def can_afford(cost):
    return get_tokens() >= int(cost)


def charge_tokens(tool, prompt, cost, provider="openai"):
    blocked, today_cost = emergency_cost_limit_reached(max_daily_cost=50)

    if blocked:
        st.error(f"Systemschutz aktiv: heutige API-Kosten sind bei ca. {today_cost}€. Generierung pausiert.")
        st.stop()

    allowed, reason = validate_request(username(), user_plan(), prompt)

    if not allowed:
        st.error(reason)
        st.stop()

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
        api_provider=provider,
        status="charged",
    )

    job_id = create_job(
        username=username(),
        tool=tool,
        prompt=prompt,
        tokens_charged=int(cost),
        provider=provider,
    )

    sync_user()
    return job_id


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


def ai_text(prompt):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY fehlt. Bitte in Railway setzen.")

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


def run_paid_text_task(
    tool,
    prompt,
    cost,
    filename_prefix,
    provider="openai",
    seconds=0,
    quality="Standard",
):
    job_id = charge_tokens(tool, prompt, cost, provider)

    try:
        with st.spinner("MaByte arbeitet..."):
            result = ai_text(prompt)

        save_usage(
            username=username(),
            tool=tool,
            prompt=prompt,
            tokens_used=0,
            cost_tokens=0,
            api_provider=provider,
            status="success",
        )

        cost_info = record_cost(
            username=username(),
            tool=tool,
            provider=provider,
            tokens_charged=int(cost),
            seconds=int(seconds or 0),
            quality=quality,
        )

        st.success(f"Job erstellt: {job_id}")
        st.caption(
            f"Geschätzte API-Kosten: {cost_info['estimated_cost_eur']}€ | "
            f"Umsatz: {cost_info['revenue_eur']}€ | "
            f"Marge: {cost_info['margin_eur']}€"
        )

        render_output(result, filename_prefix)

    except Exception as e:
        refund_tokens(cost, tool, prompt)
        st.error(f"Fehler bei der Generierung. Tokens wurden erstattet. Fehler: {e}")


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


def render_recent_jobs():
    jobs = list_user_jobs(username(), limit=8)

    if not jobs:
        return

    st.divider()
    st.subheader("🧾 Deine letzten Jobs")

    clean_jobs = []

    for job in jobs:
        clean_jobs.append(
            {
                "Job": job.get("job_id"),
                "Tool": job.get("tool"),
                "Status": job.get("status"),
                "Tokens": job.get("tokens_charged"),
                "Provider": job.get("provider"),
                "Erstellt": job.get("created_at"),
            }
        )

    st.dataframe(clean_jobs, use_container_width=True, hide_index=True)


def render_coding_ai():
    require_feature("coding")

    st.header("💻 Coding AI")
    st.write("Code schreiben, debuggen, erklären und verbessern.")

    task = st.text_area(
        "Aufgabe",
        height=170,
        placeholder="Beschreibe deinen Code-Wunsch...",
    )

    language = st.selectbox(
        "Sprache",
        ["Python", "Streamlit", "JavaScript", "HTML/CSS", "SQL", "Allgemein"],
    )

    cost = calc_tool_cost("coding")
    st.info(f"Kosten: {cost} Tokens")

    if st.button("Code generieren", use_container_width=True):
        if not task.strip():
            st.warning("Bitte Aufgabe eingeben.")
            return

        prompt = f"""
Erstelle eine professionelle Coding-Lösung.

Sprache/Bereich:
{language}

Aufgabe:
{task}

Gib vollständigen, sauberen Code aus.
"""

        run_paid_text_task("coding", prompt, cost, "mabyte_code", provider="openai")


def render_image_ai():
    require_feature("image")

    st.header("🎨 Image AI")
    st.write("Erstelle professionelle Prompts für Bilder, Ads, Thumbnails und Branding.")

    idea = st.text_area(
        "Bildidee",
        height=150,
        placeholder="z.B. Futuristisches AI Dashboard...",
    )

    style = st.selectbox(
        "Stil",
        ["Realistisch", "Cinematic", "Luxury", "Cyberpunk", "Anime", "3D Render"],
    )

    cost = calc_tool_cost("image")
    st.info(f"Kosten: {cost} Tokens")

    if st.button("Image Prompt generieren", use_container_width=True):
        if not idea.strip():
            st.warning("Bitte Bildidee eingeben.")
            return

        prompt = f"""
Erstelle einen professionellen AI Image Prompt.

Idee:
{idea}

Stil:
{style}

Gib aus:
- Final Prompt
- Negative Prompt
- Licht
- Kamera
- Details
"""

        run_paid_text_task("image", prompt, cost, "mabyte_image", provider="openai")


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

        run_paid_text_task("music", prompt, cost, "mabyte_music", provider="openai")


def render_reels_creator():
    require_feature("reels")

    st.header("🎬 Reels Creator")
    st.write("Trend-Ideen, Hook, Skript, Video-Prompt und Auto-Posting Vorbereitung.")

    used, limit = check_video_limit()
    st.info(f"Heutiges Video/Reel-Limit: {used}/{limit} genutzt")

    topic = st.text_input(
        "Thema",
        placeholder="z.B. Wie man mit AI online Geld verdient",
    )

    niche = st.selectbox(
        "Nische",
        ["AI", "Business", "Fitness", "Lifestyle", "Gaming", "Motivation", "Social Media"],
    )

    platform = st.selectbox(
        "Plattform",
        ["TikTok", "Instagram Reels", "YouTube Shorts"],
    )

    style = st.selectbox(
        "Stil",
        ["Viral", "Luxury", "Aggressiv", "Funny", "Professional"],
    )

    seconds = st.slider(
        "Reel Länge in Sekunden",
        min_value=5,
        max_value=60,
        value=15,
        step=1,
    )

    quality_options = ["Standard", "High"]
    if user_plan() == "elite":
        quality_options.append("Business Level")

    quality = st.selectbox("Video Qualität", quality_options)

    st.divider()
    render_social_connect_panel()

    auto_post = st.checkbox(
        "Automatisiertes Posting aktivieren",
        disabled=not can_use_auto_posting(),
    )

    post_time = st.text_input(
        "Posting Zeit",
        placeholder="z.B. heute 18:30 oder täglich 19:00",
        disabled=not auto_post,
    )

    selected_platforms = get_selected_platforms()

    cost = calc_tool_cost("reels_video", seconds, quality)

    st.metric("Token Kosten", cost)
    st.caption(
        f"Formel: Reels {TOKEN_COSTS.get('reels', 20)} + "
        f"Video Base {TOKEN_COSTS.get('video_base', 10)} + "
        f"{seconds} × {TOKEN_COSTS.get('video_second', 5)} Tokens"
    )

    if st.button("Reel + Video-Konzept erstellen", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        check_video_limit()

        if not can_afford(cost):
            st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
            return

        prompt = f"""
Erstelle ein komplettes Reel-Paket für {platform}.

Wichtig:
Du hast keinen Live-Zugriff auf echte TikTok/Instagram Trends.
Nutze aktuelle Creator-Patterns, virale Formate und typische Hype-Mechaniken.
Später sollen TikTok/Instagram APIs echte Trenddaten ergänzen.

Thema:
{topic}

Nische:
{niche}

Stil:
{style}

Länge:
{seconds} Sekunden

Qualität:
{quality}

Automatisiertes Posting:
{build_auto_posting_note(auto_post, post_time)}

Ausgewählte Plattformen:
{", ".join(selected_platforms) if selected_platforms else "Keine"}

Gib aus:

1. Aktuelle Trend-Ideen für die Nische
2. Beste Hook
3. Vollständiges Reel-Skript
4. Szenenplan Sekunde für Sekunde
5. Video-Prompt für AI Video Generator
6. Caption
7. Hashtags
8. Posting-Empfehlung
9. Auto-Posting Checkliste
10. Negative Prompt
"""

        run_paid_text_task(
            "reels_video",
            prompt,
            cost,
            "mabyte_reel_video",
            provider="reels_video",
            seconds=seconds,
            quality=quality,
        )


def render_video_generator():
    require_feature("video")

    st.header("🎞️ AI Video Generator")
    st.write("Sekundengenaue Tokenberechnung mit Tageslimit, Queue und Kosten-Monitor.")

    used, limit = check_video_limit()
    st.info(f"Heutiges Video-Limit: {used}/{limit} genutzt")

    video_prompt = st.text_area(
        "Video Idee",
        placeholder="z.B. Luxury AI commercial, neon city, cinematic camera...",
        height=130,
    )

    seconds = st.slider(
        "Videolänge in Sekunden",
        min_value=3,
        max_value=120,
        value=10,
        step=1,
    )

    video_style = st.selectbox(
        "Video Stil",
        ["Cinematic", "Realistisch", "Luxury", "Cyberpunk", "Commercial", "Anime"],
    )

    quality_options = ["Standard", "High"]
    if user_plan() == "elite":
        quality_options.append("Business Level")

    quality = st.selectbox("Qualität", quality_options)

    final_cost = calc_video_cost(seconds, quality)

    st.metric("Token Kosten", final_cost)
    st.caption(
        f"Formel: Base {TOKEN_COSTS.get('video_base', 10)} + "
        f"{seconds} × {TOKEN_COSTS.get('video_second', 5)} Tokens"
    )

    if st.button("Video Prompt generieren", use_container_width=True):
        if not video_prompt:
            st.warning("Bitte Video Idee eingeben.")
            return

        check_video_limit()

        if not can_afford(final_cost):
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

        run_paid_text_task(
            "video",
            prompt,
            final_cost,
            "mabyte_video",
            provider="video_prompt",
            seconds=seconds,
            quality=quality,
        )


def render_media(active_tool="reels"):
    require_login()

    st.title("🎨 AI Media Studio")
    st.write("Queue, Abuse-Schutz, Tageslimit, Cost Monitor und Rückerstattung bei Fehler.")

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

    render_recent_jobs()