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
# API SWITCHES
# =========================================================
# Später nur hier auf True stellen, wenn echte API aktiv ist.

ENABLE_REAL_MUSIC_API = False
ENABLE_REAL_REELS_API = False
ENABLE_REAL_VIDEO_API = False

MUSIC_TOKEN_COST = 100
AUTOMATION_UNLOCK_COST = int(TOKEN_COSTS.get("auto_posting_unlock", 1000))


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

    st.title("Premium Workspace")
    st.error("Dieser Workspace ist in deinem aktuellen Plan gesperrt.")
    st.info(f"Aktueller Plan: {plan.upper()} | Benötigtes Feature: {feature}")

    if st.button("Upgrade öffnen", use_container_width=True):
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
# CSS
# =========================================================

def media_css():
    st.markdown(
        """
<style>
.main .block-container{
    max-width:1320px;
    padding-top:5.5rem;
    padding-bottom:3rem;
}

.media-hero{
    border-radius:30px;
    padding:30px 34px;
    margin-bottom:24px;
    background:
        radial-gradient(circle at 90% 15%,rgba(56,189,248,.24),transparent 30%),
        linear-gradient(135deg,rgba(2,6,23,.96),rgba(30,64,175,.84));
    border:1px solid rgba(255,215,128,.18);
    box-shadow:0 24px 60px rgba(0,0,0,.30);
}

.media-kicker{
    color:#ffd36a;
    font-size:12px;
    font-weight:950;
    letter-spacing:.14em;
    text-transform:uppercase;
}

.media-title{
    color:#fff1c2;
    font-size:42px;
    font-weight:1000;
    letter-spacing:-1.4px;
    line-height:1.05;
    margin-top:8px;
}

.media-sub{
    color:#f8e7b0;
    font-size:15px;
    line-height:1.6;
    margin-top:12px;
    max-width:900px;
}

.stButton > button{
    border:none!important;
    border-radius:15px!important;
    min-height:44px!important;
    font-weight:950!important;
    background:linear-gradient(135deg,#ffd36a,#f59e0b)!important;
    color:#111827!important;
}

div[data-testid="stMetric"]{
    background:
        radial-gradient(circle at 85% 15%, rgba(125,211,252,.35), transparent 35%),
        linear-gradient(135deg,#00b7ff 0%,#006dff 52%,#083b9c 100%)!important;
    border:1px solid rgba(255,255,255,.30)!important;
    border-radius:22px!important;
    padding:16px!important;
    box-shadow:0 14px 30px rgba(0,102,255,.25)!important;
}

div[data-testid="stMetricLabel"]{
    color:#dff7ff!important;
    font-size:11px!important;
    font-weight:950!important;
    text-transform:uppercase!important;
}

div[data-testid="stMetricValue"]{
    color:white!important;
    font-size:28px!important;
    font-weight:1000!important;
}

.workflow-card{
    border-radius:24px;
    padding:22px;
    background:
        linear-gradient(180deg,rgba(15,107,255,.62),rgba(12,52,150,.72));
    border:1px solid rgba(255,215,128,.16);
    box-shadow:0 18px 44px rgba(0,0,0,.25);
    margin-bottom:16px;
}

.workflow-title{
    color:#fff1c2;
    font-size:20px;
    font-weight:1000;
    margin-bottom:6px;
}

.workflow-sub{
    color:#f8e7b0;
    font-size:13px;
    line-height:1.5;
}

.queue-item{
    border-radius:18px;
    padding:14px;
    background:rgba(2,6,23,.35);
    border:1px solid rgba(255,255,255,.10);
    margin-bottom:10px;
}

.queue-title{
    color:#fff1c2;
    font-weight:900;
}

.queue-sub{
    color:#cbd5e1;
    font-size:12px;
}

.output-box{
    border-radius:24px;
    padding:22px;
    background:rgba(2,6,23,.45);
    border:1px solid rgba(255,255,255,.12);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def hero(kicker, title, sub):
    st.markdown(
        f"""
<div class="media-hero">
    <div class="media-kicker">{kicker}</div>
    <div class="media-title">{title}</div>
    <div class="media-sub">{sub}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


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
    if tool == "music":
        return MUSIC_TOKEN_COST

    if tool == "video":
        return calc_video_cost(seconds, quality)

    if tool == "reels_video":
        return calc_video_cost(seconds, quality) + int(TOKEN_COSTS.get("reels", 25))

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


def unlock_automation_with_tokens():
    if not can_afford(AUTOMATION_UNLOCK_COST):
        st.error(
            f"Nicht genug Tokens. Automatisierung kostet {AUTOMATION_UNLOCK_COST} Tokens."
        )
        return False

    prompt = "automation unlock"

    charge_tokens(
        tool="auto_posting_unlock",
        prompt=prompt,
        cost=AUTOMATION_UNLOCK_COST,
        provider="internal",
    )

    st.session_state.auto_posting_unlocked_override = True
    st.success("Automatisierung freigeschaltet.")
    return True


def automation_available():
    return auto_posting_unlocked() or st.session_state.get(
        "auto_posting_unlocked_override",
        False,
    )


# =========================================================
# AI / API READY
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


def generate_song_api_ready(prompt):
    if ENABLE_REAL_MUSIC_API:
        # Hier später echte Suno/Fal/Music API anschließen.
        # return call_real_music_api(prompt)
        pass

    return ai_text(prompt)


def generate_reels_api_ready(prompt):
    if ENABLE_REAL_REELS_API:
        # Hier später echte Reels/Video API anschließen.
        # return call_real_reels_api(prompt)
        pass

    return ai_text(prompt)


def generate_video_api_ready(prompt):
    if ENABLE_REAL_VIDEO_API:
        # Hier später echte Video API anschließen.
        # return call_real_video_api(prompt)
        pass

    return ai_text(prompt)


def render_output(result, filename_prefix):
    st.success("Fertig generiert.")

    with st.container(border=True):
        st.markdown(result)

    filename = f"{filename_prefix}_{uuid.uuid4().hex[:6]}.txt"

    st.download_button(
        "Download",
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
    generator=None,
):
    job_id = charge_tokens(tool, prompt, cost, provider)

    try:
        with st.spinner("MaByte arbeitet..."):
            if generator:
                result = generator(prompt)
            else:
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
    st.subheader("Recent AI Jobs")

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
    media_css()

    hero(
        "Developer OS",
        "AI Coding Workspace",
        "Erstelle Code, debugge schneller und beschleunige Software Workflows mit MaByte.",
    )

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

    if st.button("Code generieren", use_container_width=True):
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
    media_css()

    hero(
        "Creative Workspace",
        "Visual Prompt Studio",
        "Erstelle Bildprompts, Brand Visuals und hochwertige Creative Assets.",
    )

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

    if st.button("Prompt generieren", use_container_width=True):
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
    media_css()

    hero(
        "Music Studio",
        "Songs für 100 Tokens",
        "Erstelle Song-Konzepte, Lyrics, Hooks und Musik-Ideen. Später kann hier direkt die echte Music API aktiviert werden.",
    )

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        topic = st.text_input("Song Thema")

        genre = st.selectbox(
            "Genre",
            ["Rap", "Trap", "Pop", "EDM", "Phonk", "Afro", "Rock", "Cinematic"],
        )

        mood = st.selectbox(
            "Mood",
            ["Energetic", "Dark", "Emotional", "Luxury", "Viral", "Motivational"],
        )

        language = st.selectbox(
            "Sprache",
            ["Deutsch", "Englisch", "Deutsch/Englisch"],
        )

    with right:
        st.markdown(
            """
<div class="workflow-card">
    <div class="workflow-title">Song Workflow</div>
    <div class="workflow-sub">
        MaByte erstellt Struktur, Hook, Lyrics, Style Direction und Prompt für spätere Music APIs.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.metric("Song Kosten", MUSIC_TOKEN_COST)

        if ENABLE_REAL_MUSIC_API:
            st.success("Music API aktiv")
        else:
            st.info("Music API vorbereitet — aktuell AI Song Package")

    if st.button("Song generieren", use_container_width=True):
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

Sprache:
{language}

Erstelle:

## Song Title

## Viral Hook

## Lyrics

## Chorus

## Verse 1

## Verse 2

## Style Direction

## Music API Prompt

## Social Caption

## Hashtags
"""

        run_paid_text_task(
            "music",
            prompt,
            MUSIC_TOKEN_COST,
            "mabyte_song",
            generator=generate_song_api_ready,
        )


def render_reels_creator():
    require_feature("reels")
    media_css()

    hero(
        "AI Content Studio",
        "Create viral short-form content.",
        "Erstelle Reels, Hooks, Scripts, Captions, Hashtags, Thumbnail Prompts und Posting Workflows in einem Studio.",
    )

    left, middle, right = st.columns([1.05, 1.35, 0.9], gap="large")

    with left:
        st.markdown("### Inputs")

        topic = st.text_area(
            "Thema / Idee",
            height=110,
            placeholder="z.B. Warum Arsenal dieses Jahr gefährlich ist...",
        )

        platform = st.selectbox(
            "Plattform",
            ["TikTok", "Instagram Reels", "YouTube Shorts", "X/Twitter"],
        )

        content_type = st.selectbox(
            "Content Typ",
            [
                "Viral Reel",
                "Football Reel",
                "Storytelling",
                "Educational",
                "Meme Page",
                "Product Promo",
                "Personal Brand",
            ],
        )

        style = st.selectbox(
            "Style",
            [
                "Fast Cut",
                "Cinematic",
                "Aggressive",
                "Luxury",
                "Funny",
                "Emotional",
                "Professional",
            ],
        )

        tone = st.selectbox(
            "Ton",
            ["Viral", "Bold", "Clean", "Funny", "Dramatic", "Premium"],
        )

        seconds = st.slider(
            "Länge",
            min_value=5,
            max_value=60,
            value=20,
        )

        quality = st.selectbox(
            "Qualität",
            ["Standard", "High"],
        )

    with middle:
        st.markdown("### Creator Preview")

        st.markdown(
            """
<div class="workflow-card">
    <div class="workflow-title">Output Package</div>
    <div class="workflow-sub">
        Hook, Script, Szenenplan, Caption, Hashtags, Thumbnail Prompt, CTA und Posting Empfehlung.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        template = st.selectbox(
            "Template",
            [
                "1 Hook + Full Script",
                "Full Viral Package",
                "Football Matchday Package",
                "Creator Growth Package",
                "Ad Creative Package",
            ],
        )

        cta = st.text_input(
            "CTA",
            placeholder="Folge für mehr / Link in Bio / Jetzt testen...",
        )

        voice = st.selectbox(
            "Voice Style",
            ["Creator", "Narrator", "Coach", "Analyst", "Hype", "News"],
        )

        hashtags_mode = st.selectbox(
            "Hashtag Style",
            ["Balanced", "Aggressive Viral", "Niche", "Premium Clean"],
        )

    with right:
        st.markdown("### Queue")

        st.markdown(
            """
<div class="queue-item">
    <div class="queue-title">Pending</div>
    <div class="queue-sub">Input bereit</div>
</div>

<div class="queue-item">
    <div class="queue-title">Generate</div>
    <div class="queue-sub">AI Package</div>
</div>

<div class="queue-item">
    <div class="queue-title">Export</div>
    <div class="queue-sub">TXT Download</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        render_social_connect_panel()

        if not automation_available():
            st.warning("Auto Posting ist gesperrt.")

            if st.button(
                f"Automatisierung für {AUTOMATION_UNLOCK_COST} Tokens freischalten",
                use_container_width=True,
            ):
                unlock_automation_with_tokens()

        auto_post = st.checkbox(
            "Auto Posting",
            disabled=not automation_available(),
        )

        post_time = st.text_input(
            "Posting Zeit",
            disabled=not auto_post,
            placeholder="Heute 18:00",
        )

    selected_platforms = get_selected_platforms()

    cost = calc_tool_cost("reels_video", seconds, quality)

    st.divider()

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Token Kosten", cost)

    with k2:
        st.metric("Dauer", f"{seconds}s")

    with k3:
        st.metric("Plan", user_plan().upper())

    if st.button("Content Package generieren", use_container_width=True):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return

        prompt = f"""
Erstelle ein hochwertiges AI Content Studio Package.

Thema:
{topic}

Plattform:
{platform}

Content Typ:
{content_type}

Template:
{template}

Style:
{style}

Ton:
{tone}

Länge:
{seconds} Sekunden

Qualität:
{quality}

Voice Style:
{voice}

CTA:
{cta}

Hashtag Style:
{hashtags_mode}

Auto Posting:
{build_auto_posting_note(auto_post, post_time)}

Ausgewählte Plattformen:
{", ".join(selected_platforms)}

Erstelle exakt diese Struktur:

## Viral Hook

## Short Script

## Scene Plan

## Caption

## Hashtags

## Thumbnail Prompt

## CTA

## Posting Strategy

## Repurpose Ideas

## Automation Notes
"""

        run_paid_text_task(
            "reels_video",
            prompt,
            cost,
            "mabyte_content_studio",
            seconds=seconds,
            quality=quality,
            generator=generate_reels_api_ready,
        )


def render_video_generator():
    require_feature("video")
    media_css()

    hero(
        "Media Studio",
        "Cinematic AI Video Workflows",
        "Plane Video Prompts, Short-Form Clips und Cinematic Content mit Token-Kontrolle.",
    )

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

    if st.button("Video generieren", use_container_width=True):
        if not video_prompt:
            st.warning("Bitte Idee eingeben.")
            return

        check_video_limit()

        prompt = f"""
Erstelle professionellen AI Video Prompt.

Idee:
{video_prompt}

Länge:
{seconds}

Qualität:
{quality}

Erstelle:
- Cinematic Prompt
- Camera Movement
- Lighting
- Scene Direction
- Negative Prompt
- Social Caption
"""

        run_paid_text_task(
            "video",
            prompt,
            cost,
            "mabyte_video",
            seconds=seconds,
            quality=quality,
            generator=generate_video_api_ready,
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