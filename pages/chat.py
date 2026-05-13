import streamlit as st
from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_TEXT_MODEL,
    TOKEN_COSTS,
)

from database import (
    get_project,
    list_projects,
    list_project_memory,
    save_project_chat_message,
    list_project_chat_memory,
    spend_tokens,
    save_usage,
    get_user,
    workspace_activity_score,
    latest_tool_used,
    save_global_memory,
    list_global_memory,
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


def project_selector():
    projects = list_projects(username())

    if not projects:
        st.info("Kein Projekt aktiv. Erstelle unter Projects ein Projekt für persistent AI Memory.")
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

    selected = st.selectbox("🛰️ Aktives Projekt", labels, index=default_index)
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


def build_global_memory(user):
    memories = list_global_memory(user, limit=25)

    if not memories:
        return "Keine globale Memory vorhanden."

    text = ""

    for mem in memories:
        text += f"- {mem.get('memory_type')}: {mem.get('content')}\n"

    return text


def learn_from_prompt(prompt):
    important_keywords = [
        "projekt",
        "brand",
        "ziel",
        "content",
        "workflow",
        "automation",
        "arsenal",
        "football",
        "startup",
        "business",
        "saas",
        "style",
        "stil",
        "tone",
        "zielgruppe",
        "tiktok",
        "reels",
        "youtube",
    ]

    lower_prompt = prompt.lower()

    for keyword in important_keywords:
        if keyword in lower_prompt:
            save_global_memory(
                username=username(),
                memory_type="user_preference",
                content=prompt[:500],
                importance=2,
            )
            return


def build_project_context(project):
    if not project:
        return "Kein aktives Projekt."

    memories = list_project_memory(project.get("id"))
    grouped = {}

    for memory in memories[:20]:
        memory_type = memory.get("memory_type", "memory")

        if memory_type not in grouped:
            grouped[memory_type] = []

        grouped[memory_type].append(memory.get("content", ""))

    memory_text = ""

    for memory_type, entries in grouped.items():
        memory_text += f"\n[{memory_type.upper()}]\n"

        for entry in entries[:5]:
            memory_text += f"- {entry}\n"

    if not memory_text:
        memory_text = "Keine gespeicherte Projekt-Memory vorhanden."

    return f"""
AKTIVES PROJEKT

Titel:
{project.get('title')}

Workspace:
{project.get('workspace')}

Beschreibung:
{project.get('description')}

GESPEICHERTE MEMORY:
{memory_text}
"""


def build_chat_history(project):
    history_messages = []

    if project:
        history = list_project_chat_memory(project.get("id"), limit=20)

        for msg in history:
            role = msg.get("role", "assistant")
            content = msg.get("message", "")

            if role in ["user", "assistant"]:
                history_messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

    else:
        for msg in st.session_state.messages[-12:]:
            history_messages.append(
                {
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                }
            )

    return history_messages


def build_messages(prompt, project):
    system_prompt = f"""
Du bist MaByte.

Ein professioneller AI Operating System Assistant.

WICHTIG:
- Nutze globale Memory aktiv
- Nutze Projektkontext aktiv
- Nutze gespeicherte Memory
- Arbeite strategisch
- Denke wie ein Senior AI Operator
- Antworte hochwertig und klar
- Gib konkrete nächste Schritte
- Arbeite workflow-orientiert
- Verbinde Bereiche intelligent

User:
{username()}

Workspace Activity Score:
{workspace_activity_score(username())}/100

Zuletzt genutztes Tool:
{latest_tool_used(username())}
"""

    messages = [
        {
            "role": "system",
            "content": (
                system_prompt
                + "\n\nGLOBAL MEMORY:\n"
                + build_global_memory(username())
                + "\n\nPROJECT CONTEXT:\n"
                + build_project_context(project)
            ),
        }
    ]

    messages.extend(build_chat_history(project))

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
# Demo Antwort

Aktives Projekt:
{project.get('title') if project else 'Kein Projekt'}

Prompt:
{prompt}

OPENAI_API_KEY fehlt aktuell.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt, project),
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_history(project):
    if project:
        history = list_project_chat_memory(project.get("id"), limit=40)

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
        st.subheader("🧠 Project Intelligence")

        if not project:
            st.write("Kein aktives Projekt.")
            st.caption("Nutze Projects für persistente AI Memory und Workspace Intelligence.")
            return

        st.write(f"**Projekt:** {project.get('title')}")
        st.write(f"**Workspace:** {project.get('workspace')}")
        st.caption(project.get("description", ""))

        memories = list_project_memory(project.get("id"))

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Memory Items", len(memories))

        with c2:
            st.metric(
                "Chat Memory",
                len(list_project_chat_memory(project.get("id"), limit=999)),
            )

        st.divider()

        score = workspace_activity_score(username())
        st.progress(score / 100)
        st.caption(f"Workspace Activity Score: {score}/100")

        if memories:
            st.write("### Letzte Memory")

            for memory in memories[:3]:
                st.markdown(
                    f"""
**{memory.get('memory_type', 'memory').title()}**

{memory.get('content', '')[:120]}
"""
                )


def render_global_memory_panel():
    memories = list_global_memory(username(), limit=8)

    with st.container(border=True):
        st.subheader("🌐 Global Memory")

        if not memories:
            st.caption("Noch keine globale Memory gespeichert.")
            return

        for mem in memories[:5]:
            st.caption(f"{mem.get('memory_type')}: {mem.get('content', '')[:90]}")


def render_chat():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_state()

    st.title("🧠 AI Assistant")
    st.caption("Persistent AI Memory, Project Intelligence und Workspace Awareness.")

    left, right = st.columns([1.6, 1], gap="large")

    with left:
        project = project_selector()

    with right:
        render_project_panel(project)
        render_global_memory_panel()

    st.divider()

    render_history(project)

    prompt = st.chat_input("Schreibe an MaByte...")

    if prompt:
        cost = charge_chat(prompt)
        learn_from_prompt(prompt)

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

        with st.spinner("MaByte analysiert Memory und Projektkontext..."):
            answer = ai_response(prompt, project)

        answer += f"\n\n---\n🪙 Verbrauchte Tokens: {cost}"

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