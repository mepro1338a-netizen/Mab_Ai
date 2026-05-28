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
from ui.prompt_ui import (
    inject_ma_prompt_css,
    ma_chat_input,
    render_os_hero,
    render_os_ready_hint,
    render_quickstart_grid,
)
from ui.styles import inject_css, page_layout_css


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
    inject_css(page_layout_css(980, 24, 130) + """
[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(18,14,34,.84), rgba(8,6,18,.98)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 22px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
}
[data-testid="stChatMessage"] * { color: #f8fafc !important; }
div[data-testid="stAlert"] {
    background: linear-gradient(145deg, rgba(12,10,30,.88), rgba(7,6,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.24) !important;
    border-radius: 22px !important;
    color: #ffe7a3 !important;
}
""")


def get_active_project():
    project_id = st.session_state.get("active_project_id")
    if not project_id:
        return None
    try:
        return get_project(project_id, username=username())
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
Antworte: modern, hochwertig, kurz, direkt, praktisch.
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


def render_messages(project) -> None:
    if project:
        history = list_project_chat_memory(project.get("id"), limit=30)
        if not history:
            render_os_ready_hint()
            return
        for msg in history:
            with st.chat_message(msg.get("role", "assistant")):
                st.markdown(msg.get("message", ""))
        return

    if not st.session_state.chat_messages:
        render_os_ready_hint()
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
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

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
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})

    st.rerun()


def render_chat() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_messages()
    load_chat_css()
    inject_ma_prompt_css()

    project = get_active_project()

    render_os_hero()
    quick_prompt = render_quickstart_grid("chat")
    render_messages(project)

    pending = st.session_state.pop("chat_pending_prompt", None)
    prompt = ma_chat_input("Nachricht eingeben…")

    if pending:
        handle_prompt(pending, project)
    if quick_prompt:
        handle_prompt(quick_prompt, project)
    if prompt:
        handle_prompt(prompt, project)
