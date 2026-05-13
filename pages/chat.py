import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS
from database import (
    get_project,
    list_projects,
    list_project_memory,
    save_project_chat_message,
    list_project_chat_memory,
    spend_tokens,
    save_usage,
    get_user,
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


def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def active_project_id():
    return st.session_state.get("active_project_id")


def get_active_project():
    project_id = active_project_id()
    if not project_id:
        return None
    return get_project(project_id)


def project_selector():
    projects = list_projects(username())

    if not projects:
        st.info("Kein Projekt aktiv. Du kannst unter Projects eins erstellen.")
        return None

    options = {f"{p.get('title')} · {p.get('workspace')}": p.get("id") for p in projects}

    current_id = active_project_id()

    labels = list(options.keys())
    default_index = 0

    if current_id:
        for i, label in enumerate(labels):
            if int(options[label]) == int(current_id):
                default_index = i
                break

    selected = st.selectbox(
        "Aktives Projekt",
        labels,
        index=default_index,
    )

    st.session_state.active_project_id = options[selected]

    return get_project(options[selected])


def charge_chat(prompt):
    cost = chat_cost()

    if get_tokens() < cost:
        st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
        st.stop()

    ok, msg = spend_tokens(username(), cost)

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=username(),
        tool="chat",
        prompt=prompt[:2000],
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="openai",
        status="success",
    )

    sync_user()
    return cost


def build_project_context(project):
    if not project:
        return "Kein aktives Projekt."

    memories = list_project_memory(project.get("id"))

    memory_text = ""

    for m in memories[:12]:
        memory_text += f"- {m.get('memory_type')}: {m.get('content')}\n"

    if not memory_text:
        memory_text = "Keine gespeicherte Projekt-Memory vorhanden."

    return f"""
Aktives Projekt:
Titel: {project.get('title')}
Workspace: {project.get('workspace')}
Beschreibung: {project.get('description')}

Gespeicherte Projekt-Memory:
{memory_text}
"""


def build_messages(prompt, project):
    system_prompt = """
Du bist MaByte, der zentrale AI Assistant eines AI Operating Systems.
Du arbeitest projektbezogen, strategisch, präzise und professionell.
Nutze den Projektkontext aktiv.
Antworte auf Deutsch, klar und hochwertig.
Wenn sinnvoll: gib konkrete nächste Schritte.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt + "\n\n" + build_project_context(project),
        }
    ]

    if project:
        history = list_project_chat_memory(project.get("id"), limit=16)

        for msg in history:
            role = msg.get("role", "assistant")
            content = msg.get("message", "")

            if role in ["user", "assistant"]:
                messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )
    else:
        for msg in st.session_state.messages[-12:]:
            messages.append(msg)

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    return messages


def ai_response(prompt, project):
    if not OPENAI_API_KEY:
        return f"""
### Demo Antwort

Aktives Projekt:
{project.get('title') if project else 'Kein Projekt'}

Du hast geschrieben:
{prompt}

OPENAI_API_KEY fehlt aktuell noch.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt, project),
        temperature=0.65,
    )

    return response.choices[0].message.content


def render_history(project):
    if project:
        history = list_project_chat_memory(project.get("id"), limit=30)

        if not history:
            st.info("Noch kein Projekt-Chat vorhanden.")
            return

        for msg in history:
            role = msg.get("role", "assistant")
            content = msg.get("message", "")

            with st.chat_message(role):
                st.markdown(content)

    else:
        if not st.session_state.messages:
            st.info("Noch kein Chat vorhanden.")
            return

        for msg in st.session_state.messages:
            with st.chat_message(msg.get("role", "assistant")):
                st.markdown(msg.get("content", ""))


def render_project_panel(project):
    with st.container(border=True):
        st.subheader("🧠 Project Context")

        if not project:
            st.write("Kein Projekt aktiv.")
            st.caption("Öffne Projects und erstelle ein Projekt, um projektbezogene Memory zu nutzen.")
            return

        st.write(f"**Projekt:** {project.get('title')}")
        st.write(f"**Workspace:** {project.get('workspace')}")
        st.caption(project.get("description", ""))

        memories = list_project_memory(project.get("id"))

        st.write(f"Memory Items: {len(memories)}")
        st.write(f"Chat Memory: {len(list_project_chat_memory(project.get('id'), limit=999))}")


def render_chat():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_state()

    st.title("🧠 AI Assistant")
    st.caption("Central AI Layer mit Project Memory und Workspace Awareness.")

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        project = project_selector()

    with right:
        render_project_panel(project)

    st.divider()

    render_history(project)

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
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

        with st.spinner("MaByte denkt im Projektkontext..."):
            answer = ai_response(prompt, project)

        answer += f"\n\n---\nVerbraucht: {cost} Token"

        if project:
            save_project_chat_message(
                project_id=project.get("id"),
                username=username(),
                role="assistant",
                message=answer,
            )
        else:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        st.rerun()