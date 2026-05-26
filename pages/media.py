import uuid
import sqlite3

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_IMAGE_MODEL, OPENAI_TEXT_MODEL, DB_PATH
from database import spend_tokens, save_usage, get_user, update_tokens
from ui_core import sync_session_user
from ui.image_studio import render_image_studio
from ui.video_studio import render_video_studio
from ui.prompt_ui import inject_ma_prompt_css, prompt_text_area, prompt_text_input
from ui.styles import inject_css, page_layout_css, gradient_title_css

try:
    from database import unlock_automation, has_automation_access
except Exception:
    unlock_automation = None
    has_automation_access = None

from pricing import (
    get_reel_script_cost,
    get_reel_video_cost,
    get_automation_unlock_cost,
    get_music_cost,
    get_coding_cost,
)


client = OpenAI(api_key=OPENAI_API_KEY)


def ensure_logged_in():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()


def username():
    return str(st.session_state.get("user") or "")


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user():
    user = get_user(username())
    if user:
        sync_session_user(user)


def fallback_unlock_automation():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE users ADD COLUMN automation_unlocked INTEGER DEFAULT 0")
    except Exception:
        pass

    cur.execute(
        "UPDATE users SET automation_unlocked = 1 WHERE username = ?",
        (username().strip().lower(),),
    )

    conn.commit()
    conn.close()


def fallback_has_automation_access():
    user = get_user(username())
    if not user:
        return False
    return int(user.get("automation_unlocked") or 0) == 1


def automation_unlocked():
    if has_automation_access:
        try:
            return bool(has_automation_access(username()))
        except Exception:
            return fallback_has_automation_access()
    return fallback_has_automation_access()


def unlock_user_automation():
    if unlock_automation:
        try:
            unlock_automation(username())
            return
        except Exception:
            pass
    fallback_unlock_automation()


def charge_tokens(tool, prompt, cost):
    cost = int(cost)

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
        prompt=str(prompt)[:1000],
        tokens_used=cost,
        cost_tokens=cost,
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
        prompt=str(prompt)[:1000],
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
                "content": (
                    "Du bist MaByte Creator Studio. "
                    "Erstelle professionelle, kurze, moderne und direkt nutzbare Outputs."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_download(result, prefix):
    filename = f"{prefix}_{uuid.uuid4().hex[:6]}.txt"

    st.download_button(
        "Download",
        data=result.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        width="stretch",
    )


def run_paid_ai(tool, prompt, cost, filename_prefix):
    charge_tokens(tool, prompt, cost)

    try:
        with st.spinner("MaByte generiert..."):
            result = ai_generate(prompt)

        save_usage(
            username=username(),
            tool=tool,
            prompt=str(prompt)[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider="openai",
            status="success",
        )

        st.success("Fertig generiert.")

        with st.container(border=True):
            st.markdown(result)

        render_download(result, filename_prefix)

    except Exception as e:
        refund_tokens(cost, tool, prompt)
        st.error(f"Fehler: {e}")


def media_css():
    inject_css(page_layout_css(1180, 28, 100) + gradient_title_css("mb-title") + """
.mb-sub {
    text-align: center;
    color: #cbd5e1 !important;
    margin-top: 10px;
    margin-bottom: 26px;
    font-size: 16px;
    font-weight: 800;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.92), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.16) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 40px rgba(0,0,0,.22) !important;
}

.stTextArea textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(14,10,28,.96) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 18px !important;
    color: #ffe7a3 !important;
    min-height: 54px !important;
}

.stTextArea textarea {
    padding-top: 14px !important;
}

[data-testid="metric-container"] {
    background:
        linear-gradient(145deg, rgba(18,14,34,.88), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.18) !important;
    border-radius: 22px !important;
    padding: 18px !important;
}

[data-testid="metric-container"] label {
    color: #c084fc !important;
    font-size: 11px !important;
    font-weight: 1000 !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(168,85,247,.10) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
    font-weight: 900 !important;
    padding: 12px 18px !important;
}

div[data-testid="stAlert"] {
    background: rgba(30,20,70,.72) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
}
"""
    )


def render_hero(title, subtitle):
    st.markdown(
        f"""
<div class="mb-title">{title}</div>
<div class="mb-sub">{subtitle}</div>
""",
        unsafe_allow_html=True,
    )


def render_reel_script():
    cost = get_reel_script_cost()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Preis", f"{cost} Tokens")

    with c2:
        st.metric("Output", "Script")

    with c3:
        st.metric("Tokens", get_tokens())

    st.write("")

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        with st.container(border=True):
            topic = prompt_text_area(
                placeholder="Frag MaByte… z.B. Warum Arsenal dieses Jahr gefährlich ist…",
                key="script_topic",
                height=160,
            )

            platform = st.selectbox(
                "Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
                key="script_platform",
            )

            category = st.selectbox(
                "Kategorie",
                ["Football", "Business", "Luxury", "Meme", "Faceless", "Storytelling", "AI News", "Motivation"],
                key="script_category",
            )

    with right:
        with st.container(border=True):
            style = st.selectbox(
                "Style",
                ["Fast Cut", "Aggressive", "Cinematic", "Premium", "Funny", "Dark"],
                key="script_style",
            )

            target = st.selectbox(
                "Ziel",
                ["Viralität", "Follower", "Kommentare", "Sales", "Branding", "Retention"],
                key="script_target",
            )

            cta = st.text_input("CTA", placeholder="Folge für mehr", key="script_cta")

            st.info("Script, Hook, Caption, Szenenplan und Hashtags.")

    if st.button("Reel Script generieren", width="stretch", key="btn_reel_script", type="primary"):
        if not topic:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle ein virales Shortform Reel Script.

Thema:
{topic}

Plattform:
{platform}

Kategorie:
{category}

Style:
{style}

Ziel:
{target}

CTA:
{cta}

Erstelle exakt:

# Viral Score
# Hook Strength
# Viral Hook
# Full Script
# Scene Breakdown
# On Screen Text
# Caption
# Hashtags
# Posting Time
# Thumbnail Text
# CTA
"""

        run_paid_ai("reel_script", prompt, cost, "mabyte_reel_script")


def render_reel_video():
    seconds = st.slider("Videolänge", min_value=3, max_value=7, value=5, key="video_seconds")

    cost = get_reel_video_cost(seconds)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Preis", f"{cost} Tokens")

    with c2:
        st.metric("Länge", f"{seconds}s")

    with c3:
        st.metric("Tokens", get_tokens())

    st.write("")

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        with st.container(border=True):
            topic = prompt_text_area(
                placeholder="Frag MaByte… Video-Idee beschreiben…",
                key="video_topic",
                height=160,
            )

            platform = st.selectbox(
                "Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
                key="video_platform",
            )

            category = st.selectbox(
                "Video Kategorie",
                ["Football Edit", "Luxury", "Meme", "Business", "Cinematic", "Storytelling"],
                key="video_category",
            )

    with right:
        with st.container(border=True):
            style = st.selectbox(
                "Video Style",
                ["Fast Cut", "Aggressive", "Premium", "Dark", "Cinematic"],
                key="video_style",
            )

            provider = st.selectbox("Provider später", ["Kling", "Runway"], key="video_provider")

            audio = st.checkbox("Audio vorbereiten", value=True, key="video_audio")

            st.info("Bereitet ein echtes Video-Paket vor. API-Anbindung kommt danach.")

    if st.button("Reel Video vorbereiten", width="stretch", key="btn_reel_video", type="primary"):
        if not topic:
            st.warning("Bitte Video Idee eingeben.")
            return

        prompt = f"""
Erstelle ein vollständiges AI Reel Video Paket.

Thema:
{topic}

Länge:
{seconds} Sekunden

Plattform:
{platform}

Provider:
{provider}

Kategorie:
{category}

Style:
{style}

Audio:
{audio}

Erstelle exakt:

# Final Video Prompt
# Shot List
# Camera Movement
# Motion Direction
# Voiceover
# Caption
# Hashtags
# Thumbnail Text
# Quality Checklist
# Delivery Package
"""

        run_paid_ai("reel_video", prompt, cost, "mabyte_reel_video")


def render_automation():
    unlock_cost = get_automation_unlock_cost()
    unlocked = automation_unlocked()

    if not unlocked:
        st.warning("Automation System ist gesperrt.")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Einmaliger Unlock", f"{unlock_cost} Tokens")

        with c2:
            st.metric("Tokens", get_tokens())

        with st.container(border=True):
            st.markdown(
                """
### Automation Unlock

Einmalig freischalten. Danach kannst du Reel-Workflows vorbereiten:

- Auto Caption Flow
- Posting Vorbereitung
- Scheduling Struktur
- Creator Pipeline
- Retry Regeln
- Quality Check
"""
            )

        if st.button("Automation für 1000 Tokens freischalten", width="stretch", key="btn_unlock_auto"):
            charge_tokens("automation_unlock", "Automation Unlock", unlock_cost)
            unlock_user_automation()
            sync_user()

            save_usage(
                username=username(),
                tool="automation_unlock",
                prompt="Automation unlocked",
                tokens_used=0,
                cost_tokens=0,
                api_provider="internal",
                status="success",
            )

            st.success("Automation freigeschaltet.")
            st.rerun()

        return

    st.success("Automation System ist aktiv.")

    with st.container(border=True):
        idea = prompt_text_area(
            placeholder="Frag MaByte… Automation beschreiben…",
            key="auto_idea",
            height=150,
        )

        platform = st.selectbox(
            "Plattform",
            ["TikTok", "Instagram Reels", "YouTube Shorts"],
            key="auto_platform",
        )

        frequency = st.selectbox(
            "Frequenz",
            ["Täglich", "3x pro Woche", "Wöchentlich"],
            key="auto_frequency",
        )

    if st.button("Automation Flow erstellen", width="stretch", key="btn_auto_flow", type="primary"):
        if not idea:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle einen professionellen Reel Automation Workflow.

Idee:
{idea}

Plattform:
{platform}

Frequenz:
{frequency}

Erstelle exakt:

# Automation Name
# Trigger
# Workflow Steps
# Reel Script Step
# Video Step
# Caption Step
# Posting Step
# Quality Check
# Retry Rules
# User Output
"""

        run_paid_ai("automation_flow", prompt, 40, "mabyte_automation")


def run_image_generation(
    user_prompt: str,
    cost: int,
    *,
    preset: dict,
    quality: str,
    style: str,
    use_case: str,
) -> None:
    from services.image_generate import generate_from_studio_options

    charge_tokens("image", user_prompt, cost)

    try:
        with st.spinner("MaByte generiert dein Bild…"):
            image_bytes, err, visual_prompt = generate_from_studio_options(
                user_prompt,
                preset=preset,
                quality=quality,
                style=style,
                use_case=use_case,
            )

        if err or not image_bytes:
            refund_tokens(cost, "image", user_prompt)
            st.error(err or "Bild konnte nicht erstellt werden.")
            return

        save_usage(
            username=username(),
            tool="image",
            prompt=str(user_prompt)[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider=OPENAI_IMAGE_MODEL if OPENAI_API_KEY else "image",
            status="success",
        )

        st.session_state.image_last_bytes = image_bytes
        st.session_state.image_last_meta = {
            "prompt": user_prompt,
            "visual_prompt": visual_prompt,
            "preset": preset,
            "quality": quality,
        }
        st.success("Bild fertig generiert.")
        st.rerun()

    except Exception as exc:
        refund_tokens(cost, "image", user_prompt)
        st.error(f"Fehler: {exc}")


def render_image_ai():
    from config import OPENAI_API_KEY

    if not OPENAI_API_KEY:
        st.warning(
            "Bildgenerierung: OPENAI_API_KEY fehlt auf dem Server. "
            "Bitte in Railway/.env setzen."
        )

    def _generate(user_prompt: str, cost: int, **opts) -> None:
        run_image_generation(
            user_prompt,
            cost,
            preset=opts.get("preset") or {},
            quality=opts.get("quality") or "standard",
            style=opts.get("style") or "",
            use_case=opts.get("use_case") or "",
        )

    render_image_studio(
        tokens_available=get_tokens(),
        on_generate=_generate,
    )


def render_music_ai():
    render_hero("Music AI", "Create music concepts and song packages.")

    with st.container(border=True):
        topic = prompt_text_input(placeholder="Frag MaByte… Song-Thema…", key="music_topic")
        genre = st.selectbox("Genre", ["Rap", "Trap", "Pop", "EDM", "Phonk", "Afro", "Rock"], key="music_genre")
        length = st.selectbox("Länge", ["short", "medium", "long"], key="music_length")
        cost = get_music_cost(length=length)
        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Song Package generieren", width="stretch", key="btn_music", type="primary"):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return
        run_paid_ai("music", topic, cost, "mabyte_music")


def render_coding_ai():
    render_hero("Coding Studio", "Build, debug and ship code faster.")

    with st.container(border=True):
        task = prompt_text_area(
            placeholder="Frag MaByte… Was soll gebaut oder gefixt werden?",
            key="coding_task",
            height=160,
        )
        complexity = st.selectbox("Komplexität", ["normal", "advanced", "fullstack"], key="coding_complexity")
        cost = get_coding_cost(complexity=complexity)
        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Code Assistant starten", width="stretch", key="btn_coding", type="primary"):
        if not task:
            st.warning("Bitte Aufgabe eingeben.")
            return
        run_paid_ai("coding", task, cost, "mabyte_code")


def run_video_generation(
    user_prompt: str,
    cost: int,
    *,
    seconds: int,
    platform: str,
    style: str,
    quality: str,
    generate_clip: bool,
) -> None:
    from services.video_studio import (
        build_en_clip_prompt,
        download_video_url,
        generate_production_package,
        generate_replicate_clip,
    )

    charge_tokens("video", user_prompt, cost)

    try:
        with st.spinner("MaByte erstellt dein Video-Paket…"):
            package, err = generate_production_package(
                user_prompt,
                seconds=seconds,
                platform=platform,
                style=style,
            )

        if err or not package:
            refund_tokens(cost, "video", user_prompt)
            st.error(err or "Paket konnte nicht erstellt werden.")
            return

        clip_url = ""
        clip_bytes = None
        if generate_clip:
            with st.spinner("Optional: KI-Clip wird generiert (Replicate)…"):
                en = build_en_clip_prompt(user_prompt, style=style, platform=platform)
                clip_url, clip_err = generate_replicate_clip(
                    en, seconds=min(seconds, 10)
                )
                if clip_err:
                    st.warning(f"Clip: {clip_err}")
                elif clip_url and clip_url.startswith("http"):
                    clip_bytes, dl_err = download_video_url(clip_url)
                    if dl_err:
                        st.warning(f"Clip-Download: {dl_err}")

        save_usage(
            username=username(),
            tool="video",
            prompt=str(user_prompt)[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider="openai+replicate" if generate_clip else "openai",
            status="success",
        )

        st.session_state.video_last_package = package
        st.session_state.video_last_meta = {
            "prompt": user_prompt,
            "seconds": seconds,
            "platform": platform,
            "style": style,
            "quality": quality,
            "clip_url": clip_url,
        }
        if clip_bytes:
            st.session_state.video_last_clip_bytes = clip_bytes
        else:
            st.session_state.pop("video_last_clip_bytes", None)

        st.success("Video-Paket fertig.")
        st.rerun()

    except Exception as exc:
        refund_tokens(cost, "video", user_prompt)
        st.error(f"Fehler: {exc}")


def render_video_ai():
    def _generate(user_prompt: str, cost: int, **opts) -> None:
        run_video_generation(
            user_prompt,
            cost,
            seconds=int(opts.get("seconds") or 15),
            platform=str(opts.get("platform") or "YouTube"),
            style=str(opts.get("style") or "Cinematic"),
            quality=str(opts.get("quality") or "standard"),
            generate_clip=bool(opts.get("generate_clip")),
        )

    render_video_studio(
        tokens_available=get_tokens(),
        on_generate=_generate,
    )


def render_reels_studio():
    from pages.reels import render_reels_studio_page

    render_reels_studio_page()


def render_media(active_tool="reels"):
    ensure_logged_in()
    media_css()
    inject_ma_prompt_css()

    if active_tool == "image":
        render_image_ai()
        return
    elif active_tool == "music":
        render_music_ai()
    elif active_tool == "coding":
        render_coding_ai()
    elif active_tool == "video":
        render_video_ai()
        return
    else:
        render_reels_studio()