import html

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS

from database import (
    get_project,
    save_project_chat_message,
    list_project_chat_memory,
    spend_tokens,
    save_usage,
    get_user,
)

from ui_core import sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# HELPERS
# =========================================================

def username() -> str:
    return str(st.session_state.get("user") or "")


def get_tokens() -> int:
    return int(st.session_state.get("tokens", 0) or 0)


def chat_cost() -> int:
    return int(TOKEN_COSTS.get("chat", 1))


def sync_user() -> None:
    user = get_user(username())
    if user:
        sync_session_user(user)


def ensure_messages() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


# =========================================================
# STYLE
# =========================================================

def load_chat_css() -> None:

    st.markdown("""
<style>

/* =========================================================
REMOVE STREAMLIT DEFAULT
========================================================= */

header,
footer,
#MainMenu {
    display: none !important;
}

.stDeployButton {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    right: 14px !important;
    top: 10px !important;
}

/* =========================================================
PAGE
========================================================= */

html,
body,
[data-testid="stAppViewContainer"],
.main {

    background:
        radial-gradient(circle at top left, rgba(37,99,235,.16), transparent 30%),
        radial-gradient(circle at bottom, rgba(168,85,247,.10), transparent 35%),
        linear-gradient(180deg, #020617 0%, #030b1f 40%, #020617 100%) !important;

    color: white !important;
}

.main .block-container {

    max-width: 1180px !important;

    padding-top: 22px !important;

    padding-bottom: 140px !important;
}

/* =========================================================
TOP BANNER
========================================================= */

.mb-banner {

    width: 100%;

    border-radius: 26px;

    overflow: hidden;

    margin-bottom: 26px;

    border: 1px solid rgba(96,165,250,.18);

    box-shadow:
        0 0 40px rgba(96,165,250,.06),
        0 20px 60px rgba(0,0,0,.28);
}

.mb-banner img {
    width: 100%;
    display: block;
}

/* =========================================================
HERO
========================================================= */

.mb-hero {

    padding: 42px;

    border-radius: 34px;

    background:
        radial-gradient(circle at top right, rgba(96,165,250,.14), transparent 30%),
        radial-gradient(circle at bottom, rgba(168,85,247,.16), transparent 35%),
        linear-gradient(145deg, rgba(8,15,35,.96), rgba(5,8,22,.98));

    border: 1px solid rgba(255,255,255,.06);

    box-shadow:
        0 20px 70px rgba(0,0,0,.34);

    text-align: center;

    margin-bottom: 22px;
}

.mb-kicker {

    color: #c084fc;

    font-size: 12px;

    font-weight: 900;

    letter-spacing: .25em;

    text-transform: uppercase;

    margin-bottom: 16px;
}

.mb-title {

    font-size: 72px;

    line-height: .95;

    font-weight: 1000;

    letter-spacing: -4px;

    margin-bottom: 18px;

    background:
        linear-gradient(135deg, #ffe7a3 0%, #c084fc 45%, #60a5fa 100%);

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-sub {

    color: #cbd5e1;

    font-size: 19px;

    font-weight: 600;

    max-width: 720px;

    margin: auto;

    line-height: 1.7;
}

/* =========================================================
QUICK START
========================================================= */

.mb-section {

    margin-top: 34px;
}

.mb-section-title {

    color: #c084fc;

    font-size: 12px;

    font-weight: 900;

    letter-spacing: .22em;

    text-transform: uppercase;

    margin-bottom: 14px;
}

div[data-testid="stButton"] > button {

    width: 100% !important;

    min-height: 78px !important;

    border-radius: 24px !important;

    background:
        linear-gradient(145deg, rgba(20,16,38,.96), rgba(8,8,20,.98)) !important;

    border: 1px solid rgba(168,85,247,.24) !important;

    color: #ffffff !important;

    font-size: 15px !important;

    font-weight: 900 !important;

    transition: all .18s ease !important;

    box-shadow:
        0 12px 34px rgba(0,0,0,.18) !important;
}

div[data-testid="stButton"] > button:hover {

    transform: translateY(-3px) !important;

    border-color: rgba(255,231,163,.34) !important;

    box-shadow:
        0 0 24px rgba(168,85,247,.22),
        0 16px 40px rgba(0,0,0,.24) !important;
}

/* =========================================================
EMPTY STATE
========================================================= */

.mb-ready {

    margin-top: 28px;

    border-radius: 34px;

    padding: 54px 30px;

    text-align: center;

    background:
        radial-gradient(circle at center, rgba(168,85,247,.16), transparent 35%),
        linear-gradient(145deg, rgba(14,12,32,.96), rgba(6,7,18,.98));

    border: 1px solid rgba(255,255,255,.06);

    box-shadow:
        0 20px 70px rgba(0,0,0,.30);
}

.mb-ready-icon {

    font-size: 38px;

    margin-bottom: 12px;

    color: #c084fc;
}

.mb-ready-title {

    color: #ffe7a3;

    font-size: 34px;

    font-weight: 1000;

    margin-bottom: 8px;
}

.mb-ready-sub {

    color: #cbd5e1;

    font-size: 16px;
}

/* =========================================================
MESSAGES
========================================================= */

[data-testid="stChatMessage"] {

    background:
        linear-gradient(145deg, rgba(14,12,32,.94), rgba(8,8,18,.98)) !important;

    border: 1px solid rgba(255,255,255,.06) !important;

    border-radius: 24px !important;

    padding: 18px !important;

    margin-bottom: 14px !important;

    box-shadow:
        0 14px 34px rgba(0,0,0,.18) !important;
}

[data-testid="stChatMessage"] * {
    color: #f8fafc !important;
}

/* =========================================================
PROMPT
========================================================= */

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] {

    background: transparent !important;

    border: 0 !important;
}

[data-testid="stChatInput"] {

    padding-left: 1rem !important;

    padding-right: 1rem !important;
}

[data-testid="stChatInput"] > div {

    background:
        radial-gradient(circle at left, rgba(168,85,247,.20), transparent 25%),
        linear-gradient(145deg, rgba(35,12,58,.98), rgba(14,6,28,.98)) !important;

    border: 1px solid rgba(168,85,247,.55) !important;

    border-radius: 999px !important;

    box-shadow:
        0 0 40px rgba(168,85,247,.30),
        inset 0 0 0 1px rgba(255,255,255,.03) !important;
}

[data-testid="stChatInput"] textarea {

    background: transparent !important;

    color: #ffe7a3 !important;

    font-weight: 900 !important;
}

[data-testid="stChatInput"] textarea::placeholder {

    color: rgba(255,231,163,.58) !important;

    font-weight: 900 !important;
}

[data-testid="stChatInput"] button {

    background:
        linear-gradient(135deg, #7c3aed, #a855f7) !important;

    border-radius: 999px !important;

    border: 1px solid rgba(255,255,255,.10) !important;

    box-shadow:
        0 0 24px rgba(168,85,247,.34) !important;
}

/* =========================================================
RESPONSIVE
========================================================= */

@media (max-width: 900px) {

    .mb-title {
        font-size: 50px;
    }

    .mb-sub {
        font-size: 16px;
    }

    .main .block-container {
        padding-top: 12px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# PROJECT
# =========================================================

def get_active_project():

    project_id = st.session_state.get("active_project_id")

    if not project_id:
        return None

    try:
        return get_project(project_id)
    except Exception:
        return None


# =========================================================
# AI
# =========================================================

def charge_chat(prompt: str) -> int:

    cost = chat_cost()

    if get_tokens() < cost:
        st.error("Nicht genug Tokens.")
        st.stop()

    ok, msg = spend_tokens(username(), cost)

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=username(),
        tool="chat",
        prompt=prompt[:1000],
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="openai",
        status="success",
    )

    sync_user()

    return cost


def build_messages(prompt: str, project):

    project_context = ""

    if project:

        project_context = f"""
Projekt:
{project.get("title")}

Beschreibung:
{project.get("description")}
"""

    return [
        {
            "role": "system",
            "content": f"""
Du bist MaByte.

Antworte:
- modern
- klar
- hochwertig
- kurz
- konkret

{project_context}
""",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]


def ai_response(prompt: str, project) -> str:

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt, project),
        temperature=0.7,
    )

    return response.choices[0].message.content


# =========================================================
# UI
# =========================================================

def render_banner():

    st.markdown("""
<div class="mb-banner">
    <img src="https://i.imgur.com/5kZ0KxA.png">
</div>
""", unsafe_allow_html=True)


def render_hero():

    st.markdown("""
<div class="mb-hero">

    <div class="mb-kicker">
        AI OPERATING SYSTEM
    </div>

    <div class="mb-title">
        MaByte
    </div>

    <div class="mb-sub">
        Strategie. Content. Automationen. Projekte.
    </div>

</div>
""", unsafe_allow_html=True)


def render_quickstart():

    st.markdown(
        '<div class="mb-section"><div class="mb-section-title">Quick Start</div></div>',
        unsafe_allow_html=True,
    )

    quick_prompts = [
        (
            "🚀 Growth Strategie",
            "Erstelle mir eine Growth-Strategie für mein Business."
        ),
        (
            "🎯 Content Plan",
            "Erstelle mir einen viralen Content-Plan."
        ),
        (
            "💸 Mehr Kunden",
            "Wie bekomme ich mehr Kunden online?"
        ),
        (
            "⚡ AI Workflow",
            "Baue mir einen AI Workflow für mein Business."
        ),
        (
            "📈 Analyse",
            "Analysiere mein Business und finde Schwächen."
        ),
        (
            "🔥 Viral Hooks",
            "Gib mir 20 virale Hooks für Social Media."
        ),
    ]

    cols = st.columns(3)

    clicked_prompt = None

    for i, (label, prompt) in enumerate(quick_prompts):

        with cols[i % 3]:

            if st.button(label, key=f"quick_{i}"):

                clicked_prompt = prompt

    return clicked_prompt


def render_empty():

    st.markdown("""
<div class="mb-ready">

    <div class="mb-ready-icon">
        ✦
    </div>

    <div class="mb-ready-title">
        MaByte ist bereit.
    </div>

    <div class="mb-ready-sub">
        Starte mit einem Quick Start oder frag direkt unten.
    </div>

</div>
""", unsafe_allow_html=True)


def render_messages(project):

    if project:

        history = list_project_chat_memory(
            project.get("id"),
            limit=30,
        )

        if not history:
            render_empty()
            return

        for msg in history:

            with st.chat_message(msg.get("role", "assistant")):

                st.markdown(msg.get("message", ""))

        return

    if not st.session_state.chat_messages:

        render_empty()

        return

    for msg in st.session_state.chat_messages:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])


# =========================================================
# CHAT
# =========================================================

def handle_prompt(prompt: str, project):

    cost = charge_chat(prompt)

    if project:

        save_project_chat_message(
            project_id=project.get("id"),
            username=username(),
            role="user",
            message=prompt,
        )

    else:

        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt,
        })

    with st.spinner("MaByte denkt..."):

        answer = ai_response(prompt, project)

    answer += f"\n\n---\nTokens: {cost}"

    if project:

        save_project_chat_message(
            project_id=project.get("id"),
            username=username(),
            role="assistant",
            message=answer,
        )

    else:

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer,
        })

    st.rerun()


# =========================================================
# MAIN
# =========================================================

def render_chat():

    if not st.session_state.get("logged_in"):

        st.session_state.page = "auth"

        st.rerun()

        return

    ensure_messages()

    load_chat_css()

    project = get_active_project()

    render_banner()

    render_hero()

    quick_prompt = render_quickstart()

    render_messages(project)

    prompt = st.chat_input("Frag MaByte...")

    if quick_prompt:
        handle_prompt(quick_prompt, project)

    if prompt:
        handle_prompt(prompt, project)