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
from ui.prompt_ui import ma_chat_input, render_chat_quickstarts, render_os_ready_hint
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
    inject_css(page_layout_css(980, 92, 130) + """
[data-testid="stChatMessage"] {
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 14px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
}
[data-testid="stChatMessage"] * { color: #f4f4f5 !important; }
div[data-testid="stAlert"] {
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 14px !important;
    color: #e4e4e7 !important;
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
Du bist MaByte AI Chat — ein professioneller Assistent für Text, Ideen,
Zusammenfassungen, E-Mails und Erklärungen.
Antworte klar, höflich und praxisnah. Kein Sport-, Wett- oder Nischen-Football-Content,
außer der Nutzer fragt explizit danach.
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

    project = get_active_project()
    st.markdown(
        '<div class="mb-ws-head"><div class="mb-ws-kicker">Workspace</div>'
        '<div class="mb-ws-title">AI Chat</div></div>',
        unsafe_allow_html=True,
    )
    render_messages(project)

    clicked = render_chat_quickstarts()
    if clicked:
        handle_prompt(clicked, project)

    pending = st.session_state.pop("chat_pending_prompt", None)
    prompt = ma_chat_input("Nachricht eingeben…")

    if pending:
        handle_prompt(pending, project)
    if prompt:
        handle_prompt(prompt, project)
