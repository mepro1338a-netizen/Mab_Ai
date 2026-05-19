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
    padding-top: 22px !important;
    padding-bottom: 130px !important;
}

/* Prompt */
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

[data-testid="stChatInput"] > div {
    background:
        radial-gradient(circle at left, rgba(168,85,247,.22), transparent 25%),
        linear-gradient(135deg, rgba(35,12,58,.98), rgba(14,6,28,.99)) !important;
    border: 1px solid rgba(168,85,247,.65) !important;
    border-radius: 999px !important;
    box-shadow:
        0 0 34px rgba(168,85,247,.34),
        inset 0 0 0 1px rgba(255,231,163,.05) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background: transparent !important;
    color: #ffe7a3 !important;
    font-weight: 900 !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,231,163,.62) !important;
    font-weight: 900 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,231,163,.24) !important;
    box-shadow: 0 0 22px rgba(168,85,247,.38) !important;
}

/* Page */
.mb-mini-hero {
    text-align: center;
    padding: 26px 18px 20px 18px;
    margin-bottom: 18px;
}

.mb-mini-title {
    font-size: 56px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -2.8px;
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-mini-sub {
    margin-top: 10px;
    color: #c7d2fe !important;
    font-size: 15px;
    font-weight: 750;
}

.mb-quick-label {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

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

.mb-ready-box {
    text-align: center;
    margin-top: 18px;
    padding: 34px 22px;
    border-radius: 28px;
    background:
        radial-gradient(circle at bottom, rgba(168,85,247,.16), transparent 42%),
        linear-gradient(145deg, rgba(12,10,30,.78), rgba(7,6,18,.96));
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 18px 48px rgba(0,0,0,.22);
}

.mb-ready-icon {
    color: #c084fc !important;
    font-size: 34px;
    margin-bottom: 8px;
}

.mb-ready-title {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    margin-bottom: 6px;
}

.mb-ready-sub {
    color: #c7d2fe !important;
    font-size: 14px;
}

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
    color: #f8e7b0 !important;
}

div[data-testid="stAlert"] {
    background: rgba(30,20,70,.72) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
}

@media (max-width: 900px) {
    .mb-mini-title {
        font-size: 42px;
    }

    [data-testid="stChatInput"] {
        padding-left: .75rem !important;
        padding-right: .75rem !important;
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

Workspace:
{project.get("workspace")}

Beschreibung:
{project.get("description")}
"""

    return [
        {
            "role": "system",
            "content": f"""
Du bist MaByte, ein professioneller AI Operating System Assistant.

Antworte:
- kurz
- klar
- hochwertig
- direkt
- praktisch
- mit nächsten Schritten

{project_context}
""",
        },
        {"role": "user", "content": prompt},
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


def render_brand() -> None:
    st.markdown(
        """
<div class="mb-mini-hero">
    <div class="mb-mini-title">MaByte</div>
    <div class="mb-mini-sub">Dein AI Operating System.</div>
</div>
""",
        unsafe_allow_html=True,
    )


def quick_prompt_buttons() -> str | None:
    st.markdown(
        '<div class="mb-quick-label">Quick Start</div>',
        unsafe_allow_html=True,
    )

    prompts = [
        (
            "Social Strategie",
            "Erstelle mir eine Social-Media-Strategie mit Content-Ideen, Hooks und Wochenplan.",
        ),
        (
            "Marketing Plan",
            "Entwickle mir einen Marketing-Plan mit Zielgruppe, Botschaft und nächsten Schritten.",
        ),
        (
            "Business Check",
            "Analysiere mein Business und gib mir klare Wachstumshebel und Prioritäten.",
        ),
        (
            "Content Ideen",
            "Gib mir 20 starke Content-Ideen mit Hook, Format und kurzer Beschreibung.",
        ),
        (
            "AI Workflow",
            "Baue mir einen einfachen AI Workflow für mein Business.",
        ),
        (
            "30 Tage Plan",
            "Erstelle mir einen klaren 30-Tage-Plan mit Zielen und täglichen Aufgaben.",
        ),
    ]

    cols = st.columns(3, gap="medium")

    for index, item in enumerate(prompts):
        label, prompt = item

        with cols[index % 3]:
            if st.button(label, key=f"quick_prompt_{index}", width="stretch"):
                return prompt

    return None


def render_empty_state() -> None:
    st.markdown(
        """
<div class="mb-ready-box">
    <div class="mb-ready-icon">✦</div>
    <div class="mb-ready-title">MaByte ist bereit.</div>
    <div class="mb-ready-sub">Wähle einen Quick Start oder frag direkt unten.</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_history(project) -> None:
    if project:
        history = list_project_chat_memory(project.get("id"), limit=30)

        if not history:
            render_empty_state()
            return

        for msg in history:
            with st.chat_message(msg.get("role", "assistant")):
                st.markdown(msg.get("message", ""))

        return

    if not st.session_state.chat_messages:
        render_empty_state()
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

    render_brand()

    quick_prompt = quick_prompt_buttons()

    render_history(project)

    prompt = st.chat_input("Frag MaByte...")

    if quick_prompt:
        handle_prompt(quick_prompt, project)

    if prompt:
        handle_prompt(prompt, project)