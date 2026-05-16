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
    padding-top: 98px !important;
    padding-bottom: 90px !important;
}

h1 {
    font-size: 42px !important;
    font-weight: 950 !important;
    color: #ffe7a3 !important;
    letter-spacing: -1.4px !important;
}

h2, h3 {
    color: #ffe7a3 !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(9,20,38,.96), rgba(11,35,62,.88)) !important;
    border: 1px solid rgba(56,189,248,.16) !important;
    border-radius: 22px !important;
    padding: 18px !important;
    box-shadow: 0 18px 42px rgba(0,0,0,.22) !important;
}

[data-testid="metric-container"] label {
    color: #7dd3fc !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(9,20,38,.94), rgba(8,16,30,.98)) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 26px !important;
    box-shadow: 0 18px 44px rgba(0,0,0,.18) !important;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(9,20,38,.92), rgba(8,16,30,.98)) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 22px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
}

[data-testid="stChatMessage"] * {
    color: #ffe7a3 !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background: linear-gradient(145deg, rgba(8,16,30,.98), rgba(12,30,54,.98)) !important;
    border: 1px solid rgba(56,189,248,.24) !important;
    border-radius: 22px !important;
    box-shadow: 0 0 34px rgba(0,140,255,.18) !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffe7a3 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg,#38bdf8,#0ea5e9) !important;
    border-radius: 14px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(15,23,42,.96) !important;
    border: 1px solid rgba(56,189,248,.20) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
}

div[data-testid="stAlert"] {
    background: linear-gradient(135deg, rgba(14,116,144,.30), rgba(30,64,175,.22)) !important;
    border: 1px solid rgba(56,189,248,.18) !important;
    border-radius: 18px !important;
}

button[kind="secondary"] {
    border-radius: 16px !important;
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

    selected = st.selectbox("Projekt auswählen", labels)
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
Du bist MaByte, ein professioneller AI Operating System Assistant.

Antworte:
- klar
- modern
- hochwertig
- strategisch
- kompakt
- praktisch
- mit konkreten nächsten Schritten

{project_context}
""",
        },
        {"role": "user", "content": prompt},
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


def render_empty_state():
    with st.container(border=True):
        st.subheader("MaByte hilft dir bei Allem.")
        st.caption("Starte mit einer Frage oder wähle einen Workspace.")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.write("**Strategie**")
            st.caption("Ideen, Positionierung, Entscheidungen")

            st.write("**Content**")
            st.caption("Hooks, Captions, Scripts, Posts")

        with c2:
            st.write("**Coding**")
            st.caption("Code, Debugging, Automatisierung")

            st.write("**Business**")
            st.caption("Workflows, Systeme, Prozesse")

        with c3:
            st.write("**Football AI**")
            st.caption("Analyse, Taktik, Scouting")

            st.write("**Daten**")
            st.caption("Reports, Insights, Auswertungen")


def render_history(project):
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


def render_chat():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_messages()
    load_chat_css()

    top_left, top_right = st.columns([1.5, 1], gap="large")

    with top_left:
        st.caption("AI OPERATING SYSTEM")
        st.title("MaByte Intelligence")
        st.write("Dein smarter AI Assistant für Strategie, Content, Coding, Business und Football.")

    with top_right:
        with st.container(border=True):
            st.caption("Session")
            st.write(f"**User:** {username()}")
            st.write(f"**Tool:** {latest_tool_used(username())}")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Tokens", get_tokens())

    with m2:
        st.metric("Chat Kosten", chat_cost())

    with m3:
        st.metric("Letztes Tool", latest_tool_used(username()))

    st.write("")

    setup_left, setup_right = st.columns([1.2, 1], gap="large")

    with setup_left:
        with st.container(border=True):
            st.subheader("Aktives Setup")
            project = project_selector()

            if project:
                st.success(f"Projekt aktiv: {project.get('title')}")
            else:
                st.info("Kein Projekt aktiv. Du kannst trotzdem normal chatten.")

    with setup_right:
        with st.container(border=True):
            st.subheader("Quick Start")
            st.caption("Beispiele:")
            st.write("• Erstelle mir eine Content-Strategie")
            st.write("• Analysiere meinen Workflow")
            st.write("• Hilf mir mit Code")
            st.write("• Plane ein 7s Reel")

    st.write("")

    render_history(project)

    prompt = st.chat_input("Schreib etwas an MaByte...")

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
                {"role": "assistant", "content": answer}
            )

        st.rerun()