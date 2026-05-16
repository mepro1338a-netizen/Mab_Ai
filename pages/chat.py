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
    max-width: 1250px !important;
    padding-top: 105px !important;
    padding-bottom: 130px !important;
}

h1 {
    color: #ffe7a3 !important;
    font-size: 56px !important;
    font-weight: 1000 !important;
    letter-spacing: -2px !important;
}

h2, h3, h4 {
    color: #ffe7a3 !important;
}

p, span, label, div {
    color: #f8e7b0 !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(180deg, rgba(12,24,44,.98), rgba(8,16,30,.98)) !important;
    border: 1px solid rgba(56,189,248,.12) !important;
    border-radius: 26px !important;
    padding: 22px !important;
    box-shadow: 0 0 34px rgba(0,140,255,.12) !important;
}

[data-testid="metric-container"] label {
    color: #7dd3fc !important;
    font-size: 12px !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, rgba(12,24,44,.90), rgba(8,16,30,.96)) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 28px !important;
    box-shadow: 0 0 34px rgba(0,140,255,.10) !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(15,23,42,.96) !important;
    border: 1px solid rgba(56,189,248,.20) !important;
    border-radius: 18px !important;
    color: #ffe7a3 !important;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(180deg, rgba(12,24,44,.88), rgba(8,16,30,.96)) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 24px !important;
    padding: 18px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 0 24px rgba(0,0,0,.18) !important;
}

[data-testid="stChatMessage"] * {
    color: #ffe7a3 !important;
}

[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg,#38bdf8,#0ea5e9) !important;
    border-radius: 15px !important;
}

[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 18px !important;
    left: 330px !important;
    right: 28px !important;
    z-index: 999999 !important;
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background: linear-gradient(135deg, rgba(8,15,28,.99), rgba(13,22,40,.99)) !important;
    border: 1px solid rgba(56,189,248,.28) !important;
    border-radius: 24px !important;
    box-shadow: 0 0 40px rgba(0,140,255,.20) !important;
    padding: 8px 10px !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffe7a3 !important;
    border: none !important;
    font-size: 15px !important;
    padding-top: 10px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(248,231,176,.50) !important;
}

[data-testid="stChatInput"] button {
    width: 44px !important;
    height: 44px !important;
    border-radius: 14px !important;
    background: linear-gradient(135deg,#38bdf8,#0ea5e9) !important;
}

div[data-testid="stAlert"] {
    background: linear-gradient(135deg, rgba(14,116,144,.32), rgba(30,64,175,.22)) !important;
    border: 1px solid rgba(56,189,248,.18) !important;
    border-radius: 20px !important;
}

@media(max-width:900px) {
    [data-testid="stChatInput"] {
        left: 12px !important;
        right: 12px !important;
    }

    h1 {
        font-size: 36px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def project_selector():
    projects = list_projects(username())

    if not projects:
        st.info("Kein Projekt aktiv. Du kannst trotzdem normal chatten.")
        return None

    labels = [f"{p.get('title')} · {p.get('workspace')}" for p in projects]
    ids = {labels[i]: projects[i].get("id") for i in range(len(projects))}

    selected = st.selectbox("Aktives Projekt", labels)
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
- modern
- professionell
- strategisch
- hilfreich
- kompakt
- mit konkreten nächsten Schritten

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


def render_history(project):
    if project:
        history = list_project_chat_memory(project.get("id"), limit=40)

        if not history:
            with st.container(border=True):
                st.subheader("Starte eine Unterhaltung")
                st.write("Stelle deine erste Frage oder arbeite mit deinem Projektkontext.")
            return

        for msg in history:
            with st.chat_message(msg.get("role", "assistant")):
                st.markdown(msg.get("message", ""))

        return

    if not st.session_state.chat_messages:
        with st.container(border=True):
            st.subheader("MaByte hilft dir bei Allem.")
            st.write("Dein smarter AI Assistant für jede Herausforderung.")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write("**AI Strategien**")
                st.caption("Vision, Positionierung, Wachstum")

                st.write("**Content Creation**")
                st.caption("Texte, Posts, Hooks, Scripts")

                st.write("**Reels & Videos**")
                st.caption("Ideen, Skripte, Konzepte")

            with c2:
                st.write("**Coding**")
                st.caption("Code, Debugging, Automatisierung")

                st.write("**Business Workflows**")
                st.caption("Prozesse, Systeme, Abläufe")

                st.write("**Automation**")
                st.caption("Smarte Aufgaben und Integrationen")

            with c3:
                st.write("**Football Intelligence**")
                st.caption("Analysen, Taktik, Scouting")

                st.write("**Daten & Analysen**")
                st.caption("Reports, Auswertungen, Insights")

                st.write("**Und vieles mehr**")
                st.caption("Frag MaByte einfach alles.")

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

    st.caption("AI OPERATING SYSTEM")
    st.title("MaByte Intelligence")
    st.write("AI Assistant für Strategie, Projekte, Content, Coding und Workflows.")

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Tokens", get_tokens())

    with c2:
        st.metric("Chat Kosten", chat_cost())

    with c3:
        st.metric("Letztes Tool", latest_tool_used(username()))

    st.write("")

    with st.container(border=True):
        project = project_selector()

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
                {
                    "role": "user",
                    "content": prompt,
                }
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
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        st.rerun()