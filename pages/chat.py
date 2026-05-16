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


# =========================================================
# BASIC HELPERS
# =========================================================

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


# =========================================================
# PAGE CSS — NO CUSTOM HTML REQUIRED
# =========================================================

def load_chat_css():
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1180px !important;
    padding-top: 105px !important;
    padding-bottom: 130px !important;
}

/* Page titles */
h1 {
    font-size: 46px !important;
    font-weight: 950 !important;
    color: #ffe7a3 !important;
    letter-spacing: -1.5px !important;
}

h2, h3 {
    color: #ffe7a3 !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: linear-gradient(180deg, rgba(12,24,44,.98), rgba(8,16,30,.98)) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 24px !important;
    padding: 22px !important;
    box-shadow: 0 0 34px rgba(0,140,255,.10) !important;
}

[data-testid="metric-container"] label {
    color: #7dd3fc !important;
    font-size: 12px !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 950 !important;
}

/* Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, rgba(12,24,44,.92), rgba(8,16,30,.97)) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 26px !important;
    box-shadow: 0 0 34px rgba(0,140,255,.08) !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(15,23,42,.96) !important;
    border: 1px solid rgba(56,189,248,.22) !important;
    border-radius: 18px !important;
    color: #ffe7a3 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: linear-gradient(180deg, rgba(12,24,44,.86), rgba(8,16,30,.96)) !important;
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
    border-radius: 16px !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 22px !important;
    left: 320px !important;
    right: 34px !important;
    z-index: 999999 !important;
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background: linear-gradient(135deg, rgba(15,23,42,.98), rgba(8,16,30,.98)) !important;
    border: 1px solid rgba(56,189,248,.28) !important;
    border-radius: 26px !important;
    box-shadow: 0 0 35px rgba(0,140,255,.22) !important;
    padding: 8px !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffe7a3 !important;
    border: none !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(248,231,176,.55) !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg,#38bdf8,#0ea5e9) !important;
    border-radius: 16px !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    background: linear-gradient(135deg, rgba(14,116,144,.34), rgba(30,64,175,.26)) !important;
    border: 1px solid rgba(56,189,248,.22) !important;
    border-radius: 18px !important;
}

div[data-testid="stAlert"] * {
    color: #ffe7a3 !important;
}

/* Mobile */
@media(max-width:900px) {
    [data-testid="stChatInput"] {
        left: 12px !important;
        right: 12px !important;
    }

    h1 {
        font-size: 34px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PROJECTS
# =========================================================

def project_selector():
    projects = list_projects(username())

    if not projects:
        st.info("Kein Projekt aktiv. Du kannst trotzdem normal chatten.")
        return None

    labels = [f"{p.get('title')} · {p.get('workspace')}" for p in projects]
    ids = {labels[i]: projects[i].get("id") for i in range(len(projects))}

    selected = st.selectbox("Projekt Memory", labels)
    project_id = ids[selected]

    st.session_state.active_project_id = project_id
    return get_project(project_id)


# =========================================================
# TOKENS
# =========================================================

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


# =========================================================
# AI
# =========================================================

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
- strategisch
- hilfreich
- nicht unnötig lang
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


# =========================================================
# HISTORY
# =========================================================

def render_history(project):
    if project:
        history = list_project_chat_memory(project.get("id"), limit=40)

        if not history:
            st.info("Noch kein Chat in diesem Projekt.")
            return

        for msg in history:
            role = msg.get("role", "assistant")
            content = msg.get("message", "")

            with st.chat_message(role):
                st.markdown(content)

        return

    if not st.session_state.chat_messages:
        with st.container(border=True):
            st.subheader("Willkommen bei MaByte")
            st.write(
                "Schreib unten deine erste Nachricht. "
                "MaByte hilft dir bei Strategie, Content, Coding, Football AI und Workflows."
            )
        return

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


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

    st.title("MaByte Intelligence")
    st.caption("AI Assistant für Strategie, Projekte, Content, Coding und Workflows.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Tokens", get_tokens())

    with c2:
        st.metric("Chat Kosten", chat_cost())

    with c3:
        st.metric("Letztes Tool", latest_tool_used(username()))

    st.divider()

    with st.container(border=True):
        project = project_selector()

    st.divider()

    render_history(project)

    prompt = st.chat_input("Frag MaByte...")

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