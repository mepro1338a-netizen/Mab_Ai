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
    max-width: 1120px !important;
    padding-top: 82px !important;
    padding-bottom: 96px !important;
}

/* ===================================================== */
/* CHAT INPUT */
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
            rgba(5,5,16,.82) 34%,
            rgba(5,5,16,.94) 100%
        ) !important;
    border-top: 1px solid rgba(255,231,163,.06) !important;
    backdrop-filter: blur(18px) !important;
    padding-top: 12px !important;
    padding-bottom: 14px !important;
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
            135deg,
            rgba(18,7,30,.98),
            rgba(9,5,16,.98)
        ) !important;
    border: 1px solid rgba(255,231,163,.22) !important;
    border-radius: 999px !important;
    box-shadow:
        0 0 28px rgba(168,85,247,.20),
        0 0 16px rgba(255,231,163,.07) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: transparent !important;
    color: #ffe7a3 !important;
    font-weight: 900 !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,231,163,.58) !important;
    font-weight: 900 !important;
}

[data-testid="stChatInput"] button {
    background:
        linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,231,163,.28) !important;
    box-shadow: 0 0 18px rgba(168,85,247,.28) !important;
}

/* ===================================================== */
/* PAGE */
/* ===================================================== */

.mb-chat-hero {
    margin-bottom: 12px;
}

.mb-chat-kicker {
    color: #d8b4fe !important;
    font-size: 11px;
    font-weight: 950;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.mb-chat-title {
    color: #ffe7a3 !important;
    font-size: 42px;
    line-height: .96;
    font-weight: 1000;
    letter-spacing: -1.7px;
}

.mb-chat-subtitle {
    max-width: 680px;
    margin-top: 10px;
    color: #aab3c5 !important;
    font-size: 14px;
    line-height: 1.45;
}

.mb-panel {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.12), transparent 28%),
        linear-gradient(145deg, rgba(24,10,42,.86), rgba(8,6,18,.98));
    border: 1px solid rgba(255,231,163,.10);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 16px 38px rgba(0,0,0,.18);
}

.mb-panel-title {
    color: #ffe7a3 !important;
    font-size: 17px;
    font-weight: 1000;
    letter-spacing: -.035em;
    margin-bottom: 7px;
}

.mb-panel-sub {
    color: #aab3c5 !important;
    font-size: 13px;
    line-height: 1.35;
}

.mb-chip-row {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-top: 10px;
}

.mb-chip {
    display: inline-flex;
    padding: 6px 9px;
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
    gap: 12px;
    padding: 7px 0;
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

.mb-empty {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.13), transparent 30%),
        linear-gradient(145deg, rgba(22,10,40,.86), rgba(8,6,18,.98));
    border: 1px solid rgba(255,231,163,.10);
    border-radius: 26px;
    padding: 22px;
    box-shadow: 0 16px 38px rgba(0,0,0,.16);
}

.mb-empty-title {
    color: #ffe7a3 !important;
    font-size: 26px;
    font-weight: 1000;
    letter-spacing: -.04em;
    margin-bottom: 7px;
}

.mb-empty-sub {
    color: #aab3c5 !important;
    font-size: 14px;
    line-height: 1.45;
    margin-bottom: 14px;
}

.mb-suggestion {
    background: linear-gradient(145deg, rgba(28,10,42,.76), rgba(10,6,18,.92));
    border: 1px solid rgba(255,231,163,.10);
    border-radius: 17px;
    padding: 14px;
    min-height: 92px;
    box-shadow: 0 10px 26px rgba(0,0,0,.12);
}

.mb-suggestion-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 1000;
    margin-bottom: 5px;
}

.mb-suggestion-sub {
    color: #aab3c5 !important;
    font-size: 13px;
    line-height: 1.35;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(24,10,42,.90), rgba(9,6,18,.98)) !important;
    border: 1px solid rgba(255,231,163,.10) !important;
    border-radius: 20px !important;
    padding: 14px !important;
    box-shadow: 0 14px 34px rgba(0,0,0,.16) !important;
}

[data-testid="metric-container"] label {
    color: #d8b4fe !important;
    font-weight: 950 !important;
    text-transform: uppercase !important;
    font-size: 10px !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(24,10,42,.84), rgba(8,6,18,.98)) !important;
    border: 1px solid rgba(255,231,163,.10) !important;
    border-radius: 22px !important;
    padding: 14px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,.15) !important;
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
    background: linear-gradient(135deg, rgba(80,20,120,.26), rgba(30,64,175,.14)) !important;
    border: 1px solid rgba(255,231,163,.10) !important;
    border-radius: 17px !important;
}

button[kind="secondary"] {
    border-radius: 15px !important;
}

@media (max-width: 1000px) {
    .mb-chat-title {
        font-size: 36px;
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
        st.info("Kein Projekt aktiv.")
        return None

    labels = [
        f"{p.get('title', 'Untitled')} · {p.get('workspace', 'Workspace')}"
        for p in projects
    ]

    ids = {labels[i]: projects[i].get("id") for i in range(len(projects))}
    selected = st.selectbox("Projekt", labels)
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
- kurz
- klar
- hochwertig
- direkt
- praktisch
- mit nächsten Schritten

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
    <div class="mb-panel-title">Session</div>
    <div class="mb-session-line">
        <div class="mb-session-label">User</div>
        <div class="mb-session-value">{safe_text(user)}</div>
    </div>
    <div class="mb-session-line">
        <div class="mb-session-label">Tool</div>
        <div class="mb-session-value">{safe_text(tool)}</div>
    </div>
    <div class="mb-session-line">
        <div class="mb-session-label">Mode</div>
        <div class="mb-session-value">AI OS</div>
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
        Frag nach Strategie, Code, Content oder Workflows.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    suggestions = [
        ("Strategie", "Angebote, Roadmaps, Entscheidungen."),
        ("Coding", "Debugging, Features, Architektur."),
        ("Content", "Hooks, Captions, Reels."),
        ("Business", "Systeme, Pricing, Prozesse."),
        ("Football AI", "Taktik, Spieler, Matchday."),
        ("Automation", "Workflows und Abläufe."),
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

    top_left, top_right = st.columns([1.65, .9], gap="large")

    with top_left:
        st.markdown(
            """
<div class="mb-chat-hero">
    <div class="mb-chat-kicker">AI Operating System</div>
    <div class="mb-chat-title">MaByte Intelligence</div>
    <div class="mb-chat-subtitle">
        Strategie. Code. Content. Workflows.
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
        st.metric("Kosten", chat_cost())

    with m3:
        st.metric("Tool", latest_tool_used(username()))

    st.write("")

    setup_left, setup_right = st.columns([1.2, .9], gap="large")

    with setup_left:
        with st.container(border=True):
            st.markdown(
                """
<div class="mb-panel-title">Projekt</div>
<div class="mb-panel-sub">
Optionaler Kontext für bessere Antworten.
</div>
""",
                unsafe_allow_html=True,
            )

            project = project_selector()

            if project:
                st.success(f"Aktiv: {project.get('title')}")
            else:
                st.info("Ohne Projektkontext.")

    with setup_right:
        st.markdown(
            """
<div class="mb-panel">
    <div class="mb-panel-title">Quick Start</div>
    <div class="mb-panel-sub">
        Kurz fragen. MaByte strukturiert.
    </div>
    <div class="mb-chip-row">
        <div class="mb-chip">Strategie</div>
        <div class="mb-chip">Code</div>
        <div class="mb-chip">Content</div>
        <div class="mb-chip">Workflow</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.write("")

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
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )

        st.rerun()