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


def load_chat_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1220px !important;
    padding-top: 92px !important;
    padding-bottom: 120px !important;
}

/* ===================================================== */
/* CHAT INPUT / BOTTOM BAR FIX */
/* ===================================================== */

[data-testid="stBottom"] {
    background: transparent !important;
}

[data-testid="stBottom"] > div {
    background: transparent !important;
}

[data-testid="stBottomBlockContainer"] {
    background:
        linear-gradient(
            180deg,
            rgba(5,5,16,0) 0%,
            rgba(5,5,16,.94) 24%,
            rgba(5,5,16,.98) 100%
        ) !important;
    border-top: 1px solid rgba(255,231,163,.08) !important;
    backdrop-filter: blur(18px) !important;
    padding-top: 16px !important;
    padding-bottom: 18px !important;
}

[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

[data-testid="stChatInput"] > div {
    background:
        linear-gradient(
            145deg,
            rgba(24,10,42,.98),
            rgba(8,6,18,.98)
        ) !important;
    border: 1px solid rgba(255,231,163,.20) !important;
    border-radius: 26px !important;
    box-shadow:
        0 0 34px rgba(168,85,247,.22),
        0 0 14px rgba(255,231,163,.06) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: transparent !important;
    color: #ffe7a3 !important;
    font-weight: 850 !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
    font-weight: 850 !important;
}

[data-testid="stChatInput"] button {
    background:
        linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,231,163,.20) !important;
    box-shadow: 0 0 18px rgba(168,85,247,.22) !important;
}

/* ===================================================== */
/* HERO */
/* ===================================================== */

.mb-chat-hero {
    margin-bottom: 18px;
}

.mb-chat-kicker {
    color: #d8b4fe !important;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mb-chat-title {
    color: #ffe7a3 !important;
    font-size: 46px;
    line-height: .96;
    font-weight: 1000;
    letter-spacing: -1.8px;
}

.mb-chat-subtitle {
    max-width: 760px;
    margin-top: 12px;
    color: #aab3c5 !important;
    font-size: 15px;
    line-height: 1.55;
}

/* ===================================================== */
/* PANELS */
/* ===================================================== */

.mb-panel {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.12), transparent 28%),
        linear-gradient(145deg, rgba(24,10,42,.88), rgba(8,6,18,.98));
    border: 1px solid rgba(255,231,163,.10);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 18px 44px rgba(0,0,0,.18);
}

.mb-panel-title {
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
    letter-spacing: -.035em;
    margin-bottom: 8px;
}

.mb-panel-sub {
    color: #aab3c5 !important;
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
    background: rgba(168,85,247,.14);
    border: 1px solid rgba(255,231,163,.14);
    color: #ffe7a3 !important;
    font-size: 12px;
    font-weight: 900;
}

.mb-session-line {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,.07);
}

.mb-session-line:last-child {
    border-bottom: 0;
}

.mb-session-label {
    color: #94a3b8 !important;
    font-size: 12px;
    font-weight: 850;
}

.mb-session-value {
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 950;
    text-align: right;
}

/* ===================================================== */
/* EMPTY STATE */
/* ===================================================== */

.mb-empty {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.14), transparent 30%),
        radial-gradient(circle at bottom left, rgba(56,189,248,.06), transparent 28%),
        linear-gradient(145deg, rgba(22,10,40,.88), rgba(8,6,18,.98));
    border: 1px solid rgba(255,231,163,.10);
    border-radius: 28px;
    padding: 24px;
    box-shadow: 0 18px 44px rgba(0,0,0,.16);
}

.mb-empty-title {
    color: #ffe7a3 !important;
    font-size: 27px;
    font-weight: 1000;
    letter-spacing: -.04em;
    margin-bottom: 8px;
}

.mb-empty-sub {
    color: #aab3c5 !important;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 18px;
}

.mb-suggestion {
    background: linear-gradient(145deg, rgba(28,10,42,.78), rgba(10,6,18,.92));
    border: 1px solid rgba(255,231,163,.10);
    border-radius: 18px;
    padding: 15px;
    min-height: 106px;
    box-shadow: 0 12px 30px rgba(0,0,0,.12);
}

.mb-suggestion-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 1000;
    margin-bottom: 6px;
}

.mb-suggestion-sub {
    color: #aab3c5 !important;
    font-size: 13px;
    line-height: 1.4;
}

/* ===================================================== */
/* STREAMLIT ELEMENTS */
/* ===================================================== */

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(24,10,42,.92), rgba(9,6,18,.98)) !important;
    border: 1px solid rgba(255,231,163,.10) !important;
    border-radius: 22px !important;
    padding: 17px !important;
    box-shadow: 0 18px 42px rgba(0,0,0,.18) !important;
}

[data-testid="metric-container"] label {
    color: #d8b4fe !important;
    font-weight: 950 !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(24,10,42,.84), rgba(8,6,18,.98)) !important;
    border: 1px solid rgba(255,231,163,.10) !important;
    border-radius: 24px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 12px 34px rgba(0,0,0,.16) !important;
}

[data-testid="stChatMessage"] * {
    color: #f8e7b0 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(15,10,28,.96) !important;
    border: 1px solid rgba(255,231,163,.14) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
}

div[data-testid="stAlert"] {
    background: linear-gradient(135deg, rgba(80,20,120,.28), rgba(30,64,175,.16)) !important;
    border: 1px solid rgba(255,231,163,.10) !important;
    border-radius: 18px !important;
}

button[kind="secondary"] {
    border-radius: 16px !important;
}

@media (max-width: 1000px) {
    .mb-chat-title {
        font-size: 38px;
    }

    [data-testid="stChatInput"] {
        padding-left: .75rem !important;
        padding-right: .75rem !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def project_selector():
    projects = list_projects(username())

    if not projects:
        st.info("Noch kein Projekt vorhanden. Chat läuft ohne Projektkontext.")
        return None

    labels = [
        f"{p.get('title', 'Untitled')} · {p.get('workspace', 'Workspace')}"
        for p in projects
    ]

    ids = {labels[i]: projects[i].get("id") for i in range(len(projects))}
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
        ("Strategie", "Positionierung, Angebote, Roadmaps und Entscheidungen."),
        ("Coding", "Debugging, Features, Architektur und App-Struktur."),
        ("Content", "Hooks, Captions, Scripts, Reels und Kampagnen."),
        ("Business", "Prozesse, Systeme, Pricing und Workflows."),
        ("Football AI", "Taktik, Scouting, Spieler und Matchday-Pläne."),
        ("Automation", "Wiederholbare Abläufe und AI-gestützte Systeme."),
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
        Dein Premium AI Workspace für Strategie, Content, Coding,
        Business, Projekte und Football Intelligence.
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