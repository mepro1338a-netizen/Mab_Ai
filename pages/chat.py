import html

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
# SESSION / USER HELPERS
# =========================================================

def username() -> str:
    return str(st.session_state.get("user") or "")


def safe_text(value) -> str:
    return html.escape(str(value or ""))


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


# =========================================================
# CSS
# =========================================================

def load_chat_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1260px !important;
    padding-top: 96px !important;
    padding-bottom: 92px !important;
}

.mb-chat-hero {
    margin-bottom: 20px;
}

.mb-chat-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #7dd3fc !important;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mb-chat-title {
    color: #ffe7a3 !important;
    font-size: 48px;
    line-height: .96;
    font-weight: 950;
    letter-spacing: -1.8px;
}

.mb-chat-subtitle {
    max-width: 780px;
    margin-top: 12px;
    color: #94a3b8 !important;
    font-size: 16px;
    line-height: 1.55;
}

.mb-panel {
    background: linear-gradient(145deg, rgba(10,24,45,.92), rgba(8,16,30,.97));
    border: 1px solid rgba(255,255,255,.075);
    border-radius: 24px;
    padding: 19px;
    box-shadow: 0 18px 44px rgba(0,0,0,.18);
}

.mb-panel-title {
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 950;
    letter-spacing: -.035em;
    margin-bottom: 8px;
}

.mb-panel-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.45;
}

.mb-chip-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 12px;
}

.mb-chip {
    display: inline-flex;
    padding: 7px 10px;
    border-radius: 999px;
    background: rgba(56,189,248,.10);
    border: 1px solid rgba(56,189,248,.18);
    color: #7dd3fc !important;
    font-size: 12px;
    font-weight: 850;
}

.mb-session-line {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,.06);
}

.mb-session-line:last-child {
    border-bottom: 0;
}

.mb-session-label {
    color: #94a3b8 !important;
    font-size: 12px;
    font-weight: 800;
}

.mb-session-value {
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 850;
    text-align: right;
}

.mb-empty {
    background:
        radial-gradient(circle at top right, rgba(56,189,248,.12), transparent 30%),
        linear-gradient(145deg, rgba(10,24,45,.90), rgba(8,16,30,.98));
    border: 1px solid rgba(255,255,255,.075);
    border-radius: 26px;
    padding: 24px;
    box-shadow: 0 18px 44px rgba(0,0,0,.16);
}

.mb-empty-title {
    color: #ffe7a3 !important;
    font-size: 26px;
    font-weight: 950;
    letter-spacing: -.04em;
    margin-bottom: 8px;
}

.mb-empty-sub {
    color: #94a3b8 !important;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 18px;
}

.mb-suggestion {
    background: rgba(15,23,42,.58);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 18px;
    padding: 15px;
    min-height: 112px;
}

.mb-suggestion-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 900;
    margin-bottom: 6px;
}

.mb-suggestion-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.4;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(9,20,38,.96), rgba(11,35,62,.88)) !important;
    border: 1px solid rgba(56,189,248,.16) !important;
    border-radius: 22px !important;
    padding: 18px !important;
    box-shadow: 0 18px 42px rgba(0,0,0,.18) !important;
}

[data-testid="metric-container"] label {
    color: #7dd3fc !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(9,20,38,.90), rgba(8,16,30,.98)) !important;
    border: 1px solid rgba(255,255,255,.075) !important;
    border-radius: 22px !important;
    padding: 14px !important;
    margin-bottom: 11px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,.13) !important;
}

[data-testid="stChatMessage"] * {
    color: #f8e7b0 !important;
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

@media (max-width: 1000px) {
    .mb-chat-title {
        font-size: 38px;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PROJECT / TOKEN LOGIC
# =========================================================

def project_selector():
    projects = list_projects(username())

    if not projects:
        st.info("Noch kein Projekt vorhanden. Chat läuft ohne Projektkontext.")
        return None

    labels = [
        f"{p.get('title', 'Untitled')} · {p.get('workspace', 'Workspace')}"
        for p in projects
    ]

    ids = {
        labels[i]: projects[i].get("id")
        for i in range(len(projects))
    }

    selected = st.selectbox("Projektkontext", labels)
    project_id = ids[selected]

    st.session_state.active_project_id = project_id
    return get_project(project_id)


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


# =========================================================
# AI
# =========================================================

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


def ai_response(prompt: str, project) -> str:
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY fehlt."

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt, project),
        temperature=0.7,
    )

    return response.choices[0].message.content


# =========================================================
# UI COMPONENTS
# =========================================================

def session_panel() -> None:
    user = username()
    tool = latest_tool_used(user)

    st.markdown(
        f"""
<div class="mb-panel">
    <div class="mb-panel-title">Session Core</div>

    <div class="mb-session-line">
        <div class="mb-session-label">User</div>
        <div class="mb-session-value">{safe_text(user)}</div>
    </div>

    <div class="mb-session-line">
        <div class="mb-session-label">Letztes Tool</div>
        <div class="mb-session-value">{safe_text(tool)}</div>
    </div>

    <div class="mb-session-line">
        <div class="mb-session-label">Modus</div>
        <div class="mb-session-value">AI Workspace</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
<div class="mb-empty">
    <div class="mb-empty-title">MaByte ist bereit.</div>
    <div class="mb-empty-sub">
        Starte mit einer Frage, einem Projekt, einer Idee oder einem Workflow.
        MaByte denkt mit Kontext, Struktur und klaren nächsten Schritten.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    suggestions = [
        (
            "Strategie",
            "Entwickle Positionierung, Angebote, Roadmaps oder Entscheidungen.",
        ),
        (
            "Coding",
            "Debugge Code, plane Features oder verbessere deine App-Struktur.",
        ),
        (
            "Content",
            "Erstelle Hooks, Captions, Scripts, Reels und Kampagnen.",
        ),
        (
            "Business",
            "Optimiere Prozesse, Systeme, Pricing und Workflows.",
        ),
        (
            "Football AI",
            "Analysiere Taktik, Spieler, Scouting oder Matchday-Pläne.",
        ),
        (
            "Automation",
            "Plane wiederholbare Abläufe und AI-gestützte Systeme.",
        ),
    ]

    cols = [c1, c2, c3]

    for index, item in enumerate(suggestions):
        title, sub = item
        with cols[index % 3]:
            st.markdown(
                f"""
<div class="mb-suggestion">
    <div class="mb-suggestion-title">{safe_text(title)}</div>
    <div class="mb-suggestion-sub">{safe_text(sub)}</div>
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


# =========================================================
# MAIN
# =========================================================

def render_chat() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    ensure_messages()
    load_chat_css()

    top_left, top_right = st.columns([1.55, 1], gap="large")

    with top_left:
        st.markdown(
            """
<div class="mb-chat-hero">
    <div class="mb-chat-kicker">◆ AI Operating System</div>
    <div class="mb-chat-title">MaByte Intelligence</div>
    <div class="mb-chat-subtitle">
        Dein AI Workspace für Strategie, Content, Coding, Business,
        Projekte und Football Intelligence.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with top_right:
        session_panel()

    m1, m2, m3 = st.columns(3, gap="medium")

    with m1:
        st.metric("Tokens", get_tokens())

    with m2:
        st.metric("Chat Kosten", chat_cost())

    with m3:
        st.metric("Letztes Tool", latest_tool_used(username()))

    st.write("")

    setup_left, setup_right = st.columns([1.25, 1], gap="large")

    with setup_left:
        with st.container(border=True):
            st.markdown(
                """
<div class="mb-panel-title">Aktives Setup</div>
<div class="mb-panel-sub">
Wähle optional ein Projekt aus. Dann antwortet MaByte mit Projektkontext.
</div>
""",
                unsafe_allow_html=True,
            )

            project = project_selector()

            if project:
                st.success(f"Projekt aktiv: {project.get('title')}")
            else:
                st.info("Chat läuft ohne Projektkontext.")

    with setup_right:
        st.markdown(
            """
<div class="mb-panel">
    <div class="mb-panel-title">Quick Start</div>
    <div class="mb-panel-sub">
        Nutze kurze Prompts. MaByte strukturiert daraus klare nächste Schritte.
    </div>
    <div class="mb-chip-row">
        <div class="mb-chip">Strategie</div>
        <div class="mb-chip">Code</div>
        <div class="mb-chip">Content</div>
        <div class="mb-chip">Workflow</div>
        <div class="mb-chip">Analyse</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

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