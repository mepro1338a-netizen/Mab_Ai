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


def load_chat_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 980px !important;
    padding-top: 24px !important;
    padding-bottom: 130px !important;
}

/* HERO */
.mb-title-clean {
    text-align: center;
    font-size: 64px;
    line-height: .9;
    font-weight: 1000;
    letter-spacing: -3px;
    margin-top: 16px;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-sub-clean {
    text-align: center;
    color: #cbd5e1 !important;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 28px;
}

.mb-quick-label {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* QUICK BUTTONS */
div[data-testid="stButton"] > button {
    min-height: 54px !important;
    border-radius: 18px !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.18), transparent 34%),
        linear-gradient(145deg, rgba(18,14,34,.88), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.22) !important;
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 1000 !important;
    box-shadow: 0 10px 24px rgba(0,0,0,.16) !important;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(255,231,163,.32) !important;
    box-shadow: 0 0 22px rgba(168,85,247,.22) !important;
}

/* EMPTY STATE - NO HTML LEAK */
div[data-testid="stAlert"] {
    background:
        radial-gradient(circle at bottom, rgba(168,85,247,.18), transparent 42%),
        linear-gradient(145deg, rgba(12,10,30,.88), rgba(7,6,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.24) !important;
    border-radius: 26px !important;
    color: #ffe7a3 !important;
}

div[data-testid="stAlert"] * {
    color: #ffe7a3 !important;
}

/* CHAT MESSAGES */
[data-testid="stChatMessage"] {
    background:
        linear-gradient(145deg, rgba(18,14,34,.84), rgba(8,6,18,.98)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 22px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 12px 30px rgba(0,0,0,.16) !important;
}

[data-testid="stChatMessage"] * {
    color: #f8fafc !important;
}

/* PURPLE PROMPT HARD FIX */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
    border: 0 !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background:
        radial-gradient(circle at top left, rgba(192,132,252,.32), transparent 28%),
        radial-gradient(circle at bottom right, rgba(96,165,250,.14), transparent 34%),
        linear-gradient(135deg, rgba(58,18,92,.98), rgba(28,8,52,.99)) !important;
    border-radius: 999px !important;
    border-color: rgba(192,132,252,.55) !important;
    box-shadow:
        0 0 38px rgba(168,85,247,.42),
        0 10px 40px rgba(0,0,0,.22),
        inset 0 0 0 1px rgba(255,255,255,.04) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: transparent !important;
    color: #f5d0fe !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    box-shadow: none !important;
    outline: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(245,208,254,.72) !important;
    font-weight: 900 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #9333ea, #c084fc) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    box-shadow: 0 0 26px rgba(192,132,252,.55) !important;
}

[data-testid="stChatInput"] button:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 0 36px rgba(192,132,252,.72) !important;
}

@media (max-width: 900px) {
    .mb-title-clean {
        font-size: 46px;
    }

    [data-testid="stChatInput"] {
        padding-left: .8rem !important;
        padding-right: .8rem !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def get_active_project():
    project_id = st.session_state.get("active_project_id")

    if not project_id:
        return None

    try:
        return get_project(project_id)
    except Exception:
        return None


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
Aktives Projekt:
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
- hochwertig
- kurz
- direkt
- praktisch

{project_context}
""",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]


def ai_response(prompt: str, project) -> str:
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY fehlt."

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt, project),
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_hero() -> None:
    st.markdown(
        """
<div class="mb-title-clean">MaByte</div>
<div class="mb-sub-clean">Dein AI Operating System.</div>
""",
        unsafe_allow_html=True,
    )


def render_quickstart() -> str | None:
    st.markdown(
        '<div class="mb-quick-label">Quick Start</div>',
        unsafe_allow_html=True,
    )

    prompts = [
        ("🚀 Wachstum", "Erstelle mir eine Growth Strategie für mein Business."),
        ("🎯 Content", "Gib mir virale Content Ideen."),
        ("💸 Kunden", "Wie bekomme ich mehr Kunden online?"),
        ("⚡ Workflow", "Baue mir einen AI Workflow."),
        ("📈 Analyse", "Analysiere mein Business."),
        ("🔥 Hooks", "Gib mir virale Hooks."),
    ]

    cols = st.columns(3, gap="medium")
    clicked_prompt = None

    for i, (label, prompt) in enumerate(prompts):
        with cols[i % 3]:
            if st.button(label, key=f"quick_{i}", width="stretch"):
                clicked_prompt = prompt

    return clicked_prompt


def render_empty() -> None:
    st.info("✦ MaByte ist bereit. Nutze einen Quick Start oder frag direkt unten.")


def render_messages(project) -> None:
    if project:
        history = list_project_chat_memory(project.get("id"), limit=30)

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


def handle_prompt(prompt: str, project) -> None:
    cost = charge_chat(prompt)

    if project:
        save_project_chat_message(
            project_id=project.get("id"),
            username=username(),
            role="user",
            message=prompt,
        )
    else:
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

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
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    st.rerun()


def render_chat() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_messages()
    load_chat_css()

    project = get_active_project()

    render_hero()

    quick_prompt = render_quickstart()

    render_messages(project)

    prompt = st.chat_input("Frag MaByte...")

    if quick_prompt:
        handle_prompt(quick_prompt, project)

    if prompt:
        handle_prompt(prompt, project)