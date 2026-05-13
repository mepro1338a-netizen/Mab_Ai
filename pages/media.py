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
    has_feature as plan_has_feature,
)

from database import (
    spend_tokens,
    save_usage,
    get_user,
    update_tokens,
    list_usage,
)

from ui_core import sync_session_user

from queue_manager import create_job, list_user_jobs
from abuse_guard import validate_request
from costs import record_cost, emergency_cost_limit_reached

from social_integrations import (
    render_social_connect_panel,
    get_selected_platforms,
    build_auto_posting_note,
    auto_posting_unlocked,
)


client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# USER / PLAN
# =========================================================

def ensure_logged_in():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()


def username():
    return st.session_state.get("user")


def user_plan():
    return st.session_state.get("plan", "free")


def require_feature(feature):
    ensure_logged_in()

    plan = user_plan()

    if plan_has_feature(plan, feature):
        return

    st.title("🔒 Premium Workspace")

    st.error("Dieser Workspace ist in deinem aktuellen Plan gesperrt.")

    st.info(
        f"Aktueller Plan: {plan.upper()} | "
        f"Benötigtes Feature: {feature}"
    )

    st.divider()

    st.subheader("🚀 Upgrade dein AI Operating System")

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.subheader("💎 Pro")
            st.write("Creator & Developer Workflows")
            st.write("✅ Developer OS")
            st.write("✅ Creative Workspace")
            st.write("✅ Music Studio")

    with c2:
        with st.container(border=True):
            st.subheader("🚀 Grand")
            st.write("Content & Automation")
            st.write("✅ Content Engine")
            st.write("✅ Media Studio")
            st.write("✅ Automation Lab")

    with c3:
        with st.container(border=True):
            st.subheader("⚡ Elite")
            st.write("Full AI Operating System")
            st.write("✅ Football Intelligence")
            st.write("✅ Highest Limits")
            st.write("✅ Agent Workflows")

    if st.button("💎 Upgrade öffnen", use_container_width=True):
        st.session_state.page = "premium"
        st.rerun()

    st.stop()


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user():
    user = get_user(username())
    if user:
        sync_session_user(user)


# =========================================================
# COSTS
# =========================================================

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

        if (
            created.startswith(today)
            and tool in ["video", "reels_video"]
            and status in ["charged", "success"]
        ):
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


# =========================================================
# TOKENS
# =========================================================

def charge_tokens(tool, prompt, cost, provider="openai"):
    blocked, today_cost = emergency_cost_limit_reached(max_daily_cost=50)

    if blocked:
        st.error(
            f"Systemschutz aktiv: heutige API-Kosten sind bei ca. {today_cost}€. "
            "Generierung pausiert."
        )
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


# =========================================================
# AI
# =========================================================

def ai_text(prompt):
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


def render_output(result, filename_prefix):
    st.success("Fertig generiert.")
    st.markdown(result)

    filename = f"{filename_prefix}_{uuid.uuid4().hex[:6]}.txt"

    st.download_button(
        "⬇️ Download",
        data=result.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )


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
            f"Umsatz: {cost_info['revenue_eur']}€"
        )

        render_output(result, filename_prefix)

    except Exception as e:
        refund_tokens(cost, tool, prompt)
        st.error(f"Fehler: {e}")


# =========================================================
# JOBS
# =========================================================

def render_recent_jobs():
    jobs = list_user_jobs(username(), limit=8)

    if not jobs:
        return

    st.divider()
    st.subheader("📋 Recent AI Jobs")

    for job in jobs:
        with st.container(border=True):

            c1, c2 = st.columns([2, 1])

            with c1:
                st.markdown(f"### {job.get('tool', '')}")
                st.caption(job.get("created_at", ""))

            with c2:
                st.metric("Tokens", job.get("tokens_charged", 0))


# =========================================================
# WORKSPACES
# =========================================================

def render_coding_ai():
    require_feature("coding")

    st.title("💻 Developer OS")
    st.caption("AI Coding Workspace")

    task = st.text_area(
        "Coding Aufgabe",
        height=180,
        placeholder="Beschreibe deinen Coding-Wunsch...",
    )

    language = st.selectbox(
        "Sprache",
        ["Python", "Streamlit", "JavaScript", "HTML/CSS", "SQL"],
    )

    cost = calc_tool_cost("coding")

    st.metric("Token Kosten", cost)

    if st.button("💻 Code generieren", use_container_width=True):
        if not task:
            st.warning("Bitte Aufgabe eingeben.")
            return

        prompt = f"""
Erstelle professionellen Code.

Sprache:
{language}

Aufgabe:
{task}
"""

        run_paid_text_task(
            "coding",
            prompt,
            cost,
            "mabyte_code",
        )


def render_image_ai():
    require_feature("image")

    st.title("🎨 Creative Workspace")
    st.caption("Image Prompts, Branding und Visual AI")

    idea = st.text_area(
        "Bildidee",
        height=150,
    )

    style = st.selectbox(
        "Style",
        ["Cinematic", "Luxury", "Cyberpunk", "Realistic", "3D"],
    )

    cost = calc_tool_cost("image")

    st.metric("Token Kosten", cost)

    if st.button("🎨 Prompt generieren", use_container_width=True):
        if not idea:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle professionellen AI Bildprompt.

Idee:
{idea}

Style:
{style}
"""

        run_paid_text_task(
            "image",
            prompt,
            cost,
            "mabyte_image",
        )


def render_music_generator():
    require_feature("music")

    st.title("🎵 Music Studio")
    st.caption("Lyrics, Hooks und Song-Konzepte")

    topic = st.text_input("Song Thema")

    genre = st.selectbox(
        "Genre",
        ["Rap", "Trap", "Pop", "EDM", "Phonk"],
    )

    cost = calc_tool_cost("music")

    st.metric("Token Kosten", cost)

    if st.button("🎵 Song generieren", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle professionelles Song-Konzept.

Thema:
{topic}

Genre:
{genre}
"""

        run_paid_text_task(
            "music",
            prompt,
            cost,
            "mabyte_music",
        )


def render_reels_creator():
    require_feature("reels")

    st.title("📣 Content Engine")
    st.caption("Reels, Hooks, Scripts und Social Content")

    topic = st.text_input("Thema")

    platform = st.selectbox(
        "Plattform",
        ["TikTok", "Instagram", "YouTube Shorts"],
    )

    seconds = st.slider(
        "Länge",
        min_value=5,
        max_value=60,
        value=15,
    )

    quality = st.selectbox(
        "Qualität",
        ["Standard", "High"],
    )

    st.divider()

    render_social_connect_panel()

    auto_post = st.checkbox(
        "Auto Posting",
        disabled=not auto_posting_unlocked(),
    )

    post_time = st.text_input(
        "Posting Zeit",
        disabled=not auto_post,
    )

    selected_platforms = get_selected_platforms()

    cost = calc_tool_cost("reels_video", seconds, quality)

    st.metric("Token Kosten", cost)

    if st.button("📣 Content generieren", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle virales Reel Paket.

Thema:
{topic}

Plattform:
{platform}

Länge:
{seconds}

Qualität:
{quality}

Auto Posting:
{build_auto_posting_note(auto_post, post_time)}

Plattformen:
{", ".join(selected_platforms)}
"""

        run_paid_text_task(
            "reels_video",
            prompt,
            cost,
            "mabyte_reels",
        )


def render_video_generator():
    require_feature("video")

    st.title("🎬 Media Studio")
    st.caption("Cinematic AI Video Workflows")

    video_prompt = st.text_area(
        "Video Idee",
        height=160,
    )

    seconds = st.slider(
        "Videolänge",
        min_value=3,
        max_value=120,
        value=10,
    )

    quality = st.selectbox(
        "Qualität",
        ["Standard", "High", "Business Level"],
    )

    cost = calc_video_cost(seconds, quality)

    st.metric("Token Kosten", cost)

    if st.button("🎬 Video generieren", use_container_width=True):
        if not video_prompt:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle professionellen AI Video Prompt.

Idee:
{video_prompt}

Länge:
{seconds}

Qualität:
{quality}
"""

        run_paid_text_task(
            "video",
            prompt,
            cost,
            "mabyte_video",
        )


# =========================================================
# MAIN
# =========================================================

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

    render_recent_jobs()