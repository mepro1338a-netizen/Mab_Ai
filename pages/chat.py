import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS

from database import (
    get_project,
    list_projects,
    save_project_chat_message,
    list_project_chat_memory,
    spend_tokens,
    save_usage,
    get_user,
    latest_tool_used,
)

from ui_core import sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


def username():
    return st.session_state.get("user")


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def chat_cost():
    return int(TOKEN_COSTS.get("chat", 1))


def sync_user():
    user = get_user(username())
    if user:
        sync_session_user(user)


def ensure_messages():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


def load_chat_css():
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1180px !important;
    padding-top: 105px !important;
    padding-bottom: 120px !important;
}

[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 18px !important;
    left: 320px !important;
    right: 34px !important;
    z-index: 999999 !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(15,23,42,.98) !important;
    color: #ffe7a3 !important;
    border: 1px solid rgba(56,189,248,.22) !important;
    border-radius: 22px !important;
    min-height: 58px !important;
}

[data-testid="stChatMessage"] {
    background: rgba(15,23,42,.55) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 22px !important;
    padding: 14px !important;
    margin-bottom: 14px !important;
}

[data-testid="stChatMessage"] * {
    color: #ffe7a3 !important;
}

@media(max-width:900px){
    [data-testid="stChatInput"] {
        left: 12px !important;
        right: 12px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def project_selector():
    projects = list_projects(username())

    if not projects:
        return None

    labels = [f"{p.get('title')} · {p.get('workspace')}" for p in projects]
    ids = {labels[i]: projects[i].get("id") for i in range(len(projects))}

    selected = st.selectbox("Projekt Memory", labels)
    project_id = ids[selected]

    st.session_state.active_project_id = project_id
    return get_project(project_id)


def charge_chat(prompt):
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


def build_messages(prompt, project):
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
Du bist MaByte, ein hochwertiger AI Operating System Assistant.

Antworte:
- klar
- direkt
- hochwertig
- praxisnah
- strategisch
- nicht zu lang

{project_context}
""",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]


def ai_response(prompt, project):
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY fehlt."

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt, project),
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_project_history(project):
    if not project:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        return

    history = list_project_chat_memory(project.get("id"), limit=30)

    for msg in history:
        role = msg.get("role", "assistant")
        content = msg.get("message", "")

        with st.chat_message(role):
            st.markdown(content)


def render_chat():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_messages()
    load_chat_css()

    st.title("MaByte Intelligence")
    st.caption("AI Assistant mit Projekt-Memory, Tokens und Workspace Awareness.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Tokens", get_tokens())

    with c2:
        st.metric("Chat Kosten", chat_cost())

    with c3:
        st.metric("Letztes Tool", latest_tool_used(username()))

    st.divider()

    project = project_selector()

    if not project:
        st.info("Kein Projekt aktiv. Du kannst trotzdem normal chatten.")

    st.divider()

    render_project_history(project)

    prompt = st.chat_input("Schreibe an MaByte...")

    if prompt:
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
                {"role": "user", "content": prompt}
            )

        with st.spinner("MaByte denkt nach..."):
            answer = ai_response(prompt, project)

        answer = f"{answer}\n\n---\nTokens: {cost}"

        if project:
            save_project_chat_message(
                project_id=project.get("id"),
                username=username(),
                role="assistant",
                message=answer,
            )
        else:
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )

        st.rerun()