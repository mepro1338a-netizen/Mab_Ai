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

/* =========================
   GLOBAL LAYOUT
========================= */

.main .block-container {
    max-width: 1120px !important;
    padding-top: 105px !important;
    padding-bottom: 150px !important;
}

/* =========================
   PAGE BACKGROUND
========================= */

.stApp {
    background:
        radial-gradient(circle at top left, rgba(0,120,255,.12), transparent 35%),
        linear-gradient(180deg, #020817 0%, #04112b 100%);
}

/* =========================
   HEADINGS
========================= */

h1 {
    font-size: 44px !important;
    font-weight: 950 !important;
    color: #ffe7a3 !important;
    letter-spacing: -1.4px !important;
}

h2, h3, p, span, label {
    color: #ffe7a3 !important;
}

/* =========================
   METRICS
========================= */

[data-testid="metric-container"] {
    background: linear-gradient(
        180deg,
        rgba(12,24,44,.95),
        rgba(8,16,30,.98)
    ) !important;

    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 22px !important;
    padding: 16px !important;
}

/* =========================
   CONTAINERS
========================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(
        180deg,
        rgba(12,24,44,.88),
        rgba(8,16,30,.96)
    ) !important;

    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 24px !important;
}

/* =========================
   CHAT MESSAGES
========================= */

[data-testid="stChatMessage"] {
    background: linear-gradient(
        180deg,
        rgba(12,24,44,.82),
        rgba(8,16,30,.94)
    ) !important;

    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 22px !important;

    padding: 16px !important;
    margin-bottom: 12px !important;
}

[data-testid="stChatMessage"] * {
    color: #ffe7a3 !important;
}

/* =========================
   CHAT INPUT FIX
========================= */

/* Bottom area */
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: linear-gradient(
        180deg,
        rgba(2,8,23,0),
        rgba(2,8,23,.95)
    ) !important;

    border-top: 1px solid rgba(255,255,255,.06) !important;

    padding-top: 18px !important;
    padding-bottom: 18px !important;
}

/* Remove white wrapper */
[data-testid="stChatInput"] {
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background: transparent !important;
}

/* Input box */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,.95) !important;

    color: #0b1220 !important;

    border: 1px solid rgba(255, 70, 90, .75) !important;

    border-radius: 999px !important;

    padding-top: 14px !important;
    padding-bottom: 14px !important;
    padding-left: 18px !important;

    font-size: 15px !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: #5f6b85 !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(
        135deg,
        #3b82f6,
        #9333ea
    ) !important;

    border-radius: 999px !important;
}

/* Prevent content overlap */
section.main {
    padding-bottom: 120px !important;
}

/* =========================
   SELECTBOX
========================= */

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(12,24,44,.95) !important;
    color: #ffe7a3 !important;
    border-radius: 18px !important;
    border: 1px solid rgba(255,255,255,.08) !important;
}

/* =========================
   INFO BOX
========================= */

.stAlert {
    border-radius: 18px !important;
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

    ids = {
        labels[i]: projects[i].get("id")
        for i in range(len(projects))
    }

    selected = st.selectbox(
        "Projekt Memory",
        labels,
        label_visibility="collapsed",
    )

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

        history = list_project_chat_memory(
            project.get("id"),
            limit=30,
        )

        if not history:

            with st.container(border=True):
                st.subheader("Starte eine Unterhaltung")
                st.write(
                    "Dieses Projekt ist bereit für projektbezogene Antworten."
                )

            return

        for msg in history:

            with st.chat_message(msg.get("role", "assistant")):
                st.markdown(msg.get("message", ""))

        return

    if not st.session_state.chat_messages:

        with st.container(border=True):

            st.subheader("MaByte hilft dir bei Allem.")

            st.write(
                "Dein smarter AI Assistant für jede Herausforderung."
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write("### Strategie")
                st.caption(
                    "Positionierung, Wachstum, Entscheidungen"
                )

                st.write("### Content")
                st.caption(
                    "Texte, Posts, Hooks, Scripts"
                )

            with col2:

                st.write("### Coding")
                st.caption(
                    "Code, Debugging, Automatisierung"
                )

                st.write("### Workflows")
                st.caption(
                    "Prozesse, Systeme, Abläufe"
                )

            with col3:

                st.write("### Football AI")
                st.caption(
                    "Analysen, Taktik, Scouting"
                )

                st.write("### Daten")
                st.caption(
                    "Reports, Insights, Auswertungen"
                )

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

    top_left, top_right = st.columns(
        [1.7, 1],
        gap="large",
    )

    with top_left:

        st.caption("AI OPERATING SYSTEM")

        st.title("MaByte Intelligence")

        st.write(
            "AI Assistant für Strategie, Projekte, Content, Coding und Workflows."
        )

    with top_right:

        with st.container(border=True):

            st.caption("Aktives Setup")

            project = project_selector()

            if project:

                st.write(f"### {project.get('title')}")

                st.caption(
                    project.get("workspace", "Workspace")
                )

            else:

                st.info("Kein Projekt aktiv.")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Tokens", get_tokens())

    with m2:
        st.metric("Chat Kosten", chat_cost())

    with m3:
        st.metric(
            "Letztes Tool",
            latest_tool_used(username())
        )

    st.write("")

    render_history(project)

    prompt = st.chat_input(
        "Schreib etwas an MaByte..."
    )

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

            answer = ai_response(
                prompt,
                project,
            )

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


render_chat()