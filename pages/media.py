import uuid

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import spend_tokens, save_usage, get_user, update_tokens
from ui_core import sync_session_user

try:
    from database import unlock_automation, has_automation_access
except Exception:
    unlock_automation = None
    has_automation_access = None

try:
    from pricing import (
        get_reel_script_cost,
        get_reel_video_cost,
        get_automation_unlock_cost,
    )
except Exception:
    def get_reel_script_cost():
        return 90

    def get_reel_video_cost(seconds=7):
        seconds = int(seconds)
        if seconds <= 3:
            return 90
        if seconds == 4:
            return 95
        if seconds == 5:
            return 100
        if seconds == 6:
            return 110
        return 120

    def get_automation_unlock_cost():
        return 1000


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


def fallback_has_automation_access():
    user = get_user(username())
    if not user:
        return False
    return int(user.get("automation_unlocked") or 0) == 1


def fallback_unlock_automation():
    user = get_user(username())
    if not user:
        return

    try:
        import sqlite3
        from config import DB_PATH

        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        cur = conn.cursor()

        try:
            cur.execute(
                "ALTER TABLE users ADD COLUMN automation_unlocked INTEGER DEFAULT 0"
            )
        except Exception:
            pass

        cur.execute(
            "UPDATE users SET automation_unlocked = 1 WHERE username = ?",
            (username().strip().lower(),),
        )

        conn.commit()
        conn.close()
    except Exception:
        pass


def automation_is_unlocked():
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
                "content": "Du bist MaByte Reels Studio. Erstelle hochwertige Creator Outputs.",
            },
            {
                "role": "user",
                "content": prompt,
            },
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

        st.success("Generierung abgeschlossen.")

        with st.container(border=True):
            st.markdown(result)

        render_download(result, filename_prefix)

    except Exception as e:
        refund_tokens(cost, tool, prompt)
        st.error(f"Fehler: {e}")


def media_css():
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1180px !important;
    padding-top: 28px !important;
    padding-bottom: 90px !important;
}

.mb-title {
    text-align: center;
    font-size: 56px;
    font-weight: 1000;
    letter-spacing: -3px;
    line-height: .92;
    margin-top: 10px;
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-sub {
    text-align: center;
    color: #cbd5e1 !important;
    margin-top: 10px;
    margin-bottom: 28px;
    font-size: 16px;
    font-weight: 800;
}

.mb-section {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.92), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.14) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 40px rgba(0,0,0,.22) !important;
}

.stTextArea textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(14,10,28,.96) !important;
    border: 1px solid rgba(168,85,247,.24) !important;
    border-radius: 18px !important;
    color: #ffe7a3 !important;
    min-height: 54px !important;
}

.stTextArea textarea {
    padding-top: 14px !important;
}

.stButton > button {
    min-height: 52px !important;
    border-radius: 18px !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.20), transparent 34%),
        linear-gradient(145deg, rgba(36,8,56,.98), rgba(12,3,25,.98)) !important;
    border: 1px solid rgba(168,85,247,.30) !important;
    color: #ffe7a3 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
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

div[data-testid="stAlert"] {
    background: rgba(30,20,70,.72) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_media_hero(title="Reels Studio"):
    st.markdown(
        f"""
<div class="mb-title">{title}</div>
<div class="mb-sub">Create viral shortform content with AI.</div>
""",
        unsafe_allow_html=True,
    )


def render_reel_script():
    cost = get_reel_script_cost()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Preis", f"{cost} Tokens")

    with c2:
        st.metric("Typ", "Script")

    with c3:
        st.metric("Tokens", get_tokens())

    st.write("")

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        with st.container(border=True):
            topic = st.text_area(
                "Reel Idee",
                height=160,
                placeholder="z.B. Warum Arsenal dieses Jahr gefährlich ist...",
            )

            platform = st.selectbox(
                "Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
            )

            reel_type = st.selectbox(
                "Kategorie",
                [
                    "Football",
                    "Business",
                    "Luxury",
                    "Meme",
                    "Faceless",
                    "Storytelling",
                    "AI News",
                    "Motivation",
                ],
            )

    with right:
        with st.container(border=True):
            style = st.selectbox(
                "Style",
                ["Fast Cut", "Aggressive", "Cinematic", "Premium", "Funny", "Dark"],
            )

            cta = st.text_input(
                "CTA",
                placeholder="Folge für mehr",
            )

            st.info("Erzeugt Hook, Script, Caption, Szenenplan und Hashtags.")

    st.write("")

    if st.button("Reel Script generieren", width="stretch"):
        if not topic:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle ein virales Shortform Reel.

THEMA:
{topic}

PLATTFORM:
{platform}

KATEGORIE:
{reel_type}

STYLE:
{style}

CTA:
{cta}

Erstelle exakt:

# VIRAL HOOK
# FULL SCRIPT
# SCENE BREAKDOWN
# ON SCREEN TEXT
# CAPTION
# HASHTAGS
# POSTING TIME
# THUMBNAIL TEXT
"""

        run_paid_ai(
            tool="reel_script",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_reel_script",
        )


def render_reel_video():
    seconds = st.slider(
        "Videolänge",
        min_value=3,
        max_value=7,
        value=5,
    )

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
            topic = st.text_area(
                "Video Idee",
                height=160,
                placeholder="z.B. Schneller Football Edit mit Stadion Shots...",
            )

            platform = st.selectbox(
                "Plattform",
                ["TikTok", "Instagram Reels", "YouTube Shorts"],
            )

            reel_type = st.selectbox(
                "Video Kategorie",
                [
                    "Football Edit",
                    "Luxury",
                    "Meme",
                    "Business",
                    "Cinematic",
                    "Storytelling",
                ],
            )

    with right:
        with st.container(border=True):
            style = st.selectbox(
                "Video Style",
                ["Fast Cut", "Aggressive", "Premium", "Dark", "Cinematic"],
            )

            audio = st.checkbox(
                "Audio vorbereiten",
                value=True,
            )

            st.info("Video Generation wird auf Kling/Runway vorbereitet.")

    st.write("")

    if st.button("Reel Video vorbereiten", width="stretch"):
        if not topic:
            st.warning("Bitte Video Idee eingeben.")
            return

        prompt = f"""
Erstelle ein vollständiges AI Reel Video Paket.

THEMA:
{topic}

LÄNGE:
{seconds} Sekunden

PLATTFORM:
{platform}

STYLE:
{style}

AUDIO:
{audio}

KATEGORIE:
{reel_type}

Erstelle exakt:

# FINAL VIDEO PROMPT
# SHOT LIST
# CAMERA MOVEMENT
# MOTION DIRECTION
# VOICEOVER
# CAPTION
# HASHTAGS
# THUMBNAIL TEXT
# DELIVERY PACKAGE
"""

        run_paid_ai(
            tool="reel_video",
            prompt=prompt,
            cost=cost,
            filename_prefix="mabyte_reel_video",
        )


def render_automation():
    unlocked = automation_is_unlocked()
    unlock_cost = get_automation_unlock_cost()

    if not unlocked:
        st.warning("Automation System gesperrt.")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Unlock Preis", f"{unlock_cost} Tokens")

        with c2:
            st.metric("Tokens", get_tokens())

        st.write("")

        with st.container(border=True):
            st.markdown(
                """
### Automation System

Nach dem Unlock bekommst du dauerhaft:

- Reel Pipelines
- Auto Caption Flows
- Posting Systeme
- Scheduling
- Creator Workflows
- Auto Reel Strukturen
"""
            )

        st.write("")

        if st.button("Automation freischalten", width="stretch"):
            charge_tokens(
                tool="automation_unlock",
                prompt="Automation Unlock",
                cost=unlock_cost,
            )

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

            st.success("Automation wurde freigeschaltet.")
            st.rerun()

        return

    st.success("Automation System aktiv.")

    with st.container(border=True):
        idea = st.text_area(
            "Automation Idee",
            height=150,
            placeholder="z.B. Jeden Tag automatisch Football Reels vorbereiten...",
        )

        frequency = st.selectbox(
            "Frequenz",
            ["Täglich", "3x pro Woche", "Wöchentlich"],
        )

    st.write("")

    if st.button("Automation Flow erstellen", width="stretch"):
        if not idea:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle einen Creator Automation Workflow.

IDEE:
{idea}

FREQUENZ:
{frequency}

Erstelle exakt:

# AUTOMATION NAME
# TRIGGER
# WORKFLOW
# REEL STEP
# CAPTION STEP
# POSTING STEP
# QUALITY CHECK
# RETRY RULES
"""

        run_paid_ai(
            tool="automation_flow",
            prompt=prompt,
            cost=40,
            filename_prefix="mabyte_automation",
        )


def render_placeholder(title):
    st.info(f"{title} wird als nächstes sauber ausgebaut.")


def render_media(active_tool="reels"):
    ensure_logged_in()
    media_css()

    if active_tool == "reels":
        render_media_hero("Reels Studio")

        mode = st.radio(
            "Studio",
            ["Reel Scripts", "Reel Videos", "Automation"],
            horizontal=True,
        )

        st.write("")

        if mode == "Reel Scripts":
            render_reel_script()
        elif mode == "Reel Videos":
            render_reel_video()
        else:
            render_automation()

    elif active_tool == "video":
        render_media_hero("Video AI")
        render_reel_video()

    elif active_tool == "image":
        render_media_hero("Image AI")
        render_placeholder("Image AI")

    elif active_tool == "music":
        render_media_hero("Music AI")
        render_placeholder("Music AI")

    elif active_tool == "coding":
        render_media_hero("Coding Studio")
        render_placeholder("Coding Studio")

    else:
        render_media_hero("Reels Studio")
        render_reel_script()