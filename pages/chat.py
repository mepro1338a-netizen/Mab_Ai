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
    max-width: 1180px !important;
    padding-top: 82px !important;
    padding-bottom: 132px !important;
}

/* ===================================================== */
/* PROMPT BAR - PURPLE FIX */
/* ===================================================== */

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
}

[data-testid="stBottomBlockContainer"] {
    border-top: 0 !important;
    backdrop-filter: none !important;
    padding-top: 10px !important;
    padding-bottom: 18px !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
    padding-left: 2.2rem !important;
    padding-right: 2.2rem !important;
}

[data-testid="stChatInput"] > div {
    background:
        radial-gradient(circle at left, rgba(168,85,247,.24), transparent 25%),
        linear-gradient(135deg, rgba(34,10,58,.98), rgba(14,6,26,.99)) !important;
    border: 1px solid rgba(168,85,247,.65) !important;
    border-radius: 999px !important;
    box-shadow:
        0 0 34px rgba(168,85,247,.38),
        inset 0 0 0 1px rgba(255,231,163,.06) !important;
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
    color: rgba(255,231,163,.62) !important;
    font-weight: 900 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,231,163,.28) !important;
    box-shadow: 0 0 22px rgba(168,85,247,.42) !important;
}

/* extra Streamlit input internals */
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] section,
[data-testid="stChatInput"] form {
    background-color: transparent !important;
}

[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    caret-color: #ffe7a3 !important;
}

/* ===================================================== */
/* PAGE SHELL */
/* ===================================================== */

.mb-ai-shell {
    min-height: calc(100vh - 220px);
}

.mb-hero-grid {
    display: grid;
    grid-template-columns: 1fr 290px;
    gap: 28px;
    align-items: start;
    margin-bottom: 26px;
}

.mb-kicker {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.mb-title {
    color: #ffe7a3 !important;
    font-size: 52px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -2px;
    margin-bottom: 14px;
}

.mb-subtitle {
    color: #c7d2fe !important;
    font-size: 17px;
    line-height: 1.45;
}

.mb-session-card {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.16), transparent 30%),
        linear-gradient(145deg, rgba(18,14,34,.82), rgba(8,7,18,.96));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 18px 44px rgba(0,0,0,.22);
}

.mb-session-title {
    color: #ffe7a3 !important;
    font-size: 20px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.mb-session-line {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,.07);
}

.mb-session-line:last-child {
    border-bottom: 0;
}

.mb-session-label {
    color: #aab3c5 !important;
    font-size: 13px;
    font-weight: 800;
}

.mb-session-value {
    color: #ffe7a3 !important;
    font-size: 13px;
    font-weight: 1000;
    text-align: right;
}

.mb-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-bottom: 22px;
}

.mb-metric {
    background:
        radial-gradient(circle at left, rgba(168,85,247,.16), transparent 28%),
        linear-gradient(145deg, rgba(18,14,34,.76), rgba(8,7,18,.94));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 20px;
    padding: 18px;
    min-height: 92px;
    box-shadow: 0 14px 34px rgba(0,0,0,.18);
}

.mb-metric-label {
    color: #c4b5fd !important;
    font-size: 11px;
    font-weight: 950;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mb-metric-value {
    color: #ffffff !important;
    font-size: 28px;
    font-weight: 1000;
    line-height: 1;
}

.mb-project-card {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.15), transparent 26%),
        linear-gradient(145deg, rgba(15,10,34,.80), rgba(8,6,18,.96));
    border: 1px solid rgba(168,85,247,.38);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 28px;
    box-shadow:
        0 20px 48px rgba(0,0,0,.24),
        0 0 28px rgba(168,85,247,.10);
}

.mb-card-head {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.mb-card-title {
    color: #ffe7a3 !important;
    font-size: 20px;
    font-weight: 1000;
    margin-bottom: 6px;
}

.mb-card-sub {
    color: #c7d2fe !important;
    font-size: 14px;
    line-height: 1.4;
    margin-bottom: 14px;
}

.mb-quick-title {
    color: #c084fc !important;
    font-size: 13px;
    font-weight: 1000;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.mb-quick-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 28px;
}

.mb-quick {
    background: linear-gradient(145deg, rgba(18,14,34,.78), rgba(9,7,18,.96));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 16px;
    padding: 14px 16px;
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 950;
    text-align: center;
    box-shadow: 0 12px 26px rgba(0,0,0,.16);
}

.mb-ready {
    background:
        radial-gradient(circle at bottom, rgba(168,85,247,.18), transparent 42%),
        linear-gradient(145deg, rgba(12,10,30,.78), rgba(7,6,18,.96));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 26px;
    min-height: 230px;
    padding: 42px 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    box-shadow:
        0 20px 54px rgba(0,0,0,.22),
        0 18px 40px rgba(168,85,247,.08);
}

.mb-ready-icon {
    color: #c084fc !important;
    font-size: 38px;
    margin-bottom: 14px;
}

.mb-ready-title {
    color: #ffe7a3 !important;
    font-size: 28px;
    font-weight: 1000;
    letter-spacing: -.04em;
    margin-bottom: 8px;
}

.mb-ready-sub {
    color: #c7d2fe !important;
    font-size: 14px;
}

[data-testid="stChatMessage"] {
    background:
        linear-gradient(145deg, rgba(18,14,34,.84), rgba(8,6,18,.98)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 22px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 12px 30px rgba(0,0,0,.16) !important;
}

[data-testid="stChatMessage"] * {
    color: #f8e7b0 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(10,8,22,.98) !important;
    border: 1px solid rgba(168,85,247,.34) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
}

div[data-testid="stAlert"] {
    background: rgba(30,20,70,.72) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
}

@media (max-width: 1050px) {
    .mb-hero-grid {
        grid-template-columns: 1fr;
    }

    .mb-metrics,
    .mb-quick-row {
        grid-template-columns: 1fr;
    }

    .mb-title {
        font-size: 40px;
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


def render_session_card() -> None:
    user = username()
    tool = latest_tool_used(user)

    st.markdown(
        f"""
<div class="mb-session-card">
    <div class="mb-session-title">Session</div>
    <div class="mb-session-line">
        <div class="mb-session-label">User</div>
        <div class="mb-session-value">{safe_text(user)}</div>
    </div>
    <div class="mb-session-line">
        <div class="mb-session-label">Mode</div>
        <div class="mb-session-value">AI OS</div>
    </div>
    <div class="mb-session-line">
        <div class="mb-session-label">Tool</div>
        <div class="mb-session-value">{safe_text(tool)}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_metrics() -> None:
    st.markdown(
        f"""
<div class="mb-metrics">
    <div class="mb-metric">
        <div class="mb-metric-label">Tokens</div>
        <div class="mb-metric-value">{get_tokens()}</div>
    </div>
    <div class="mb-metric">
        <div class="mb-metric-label">Kosten</div>
        <div class="mb-metric-value">{chat_cost()}</div>
    </div>
    <div class="mb-metric">
        <div class="mb-metric-label">Letztes Tool</div>
        <div class="mb-metric-value">{safe_text(latest_tool_used(username()))}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_quick_start() -> None:
    st.markdown(
        """
<div class="mb-quick-title">Quick Start</div>
<div class="mb-quick-row">
    <div class="mb-quick">Strategie</div>
    <div class="mb-quick">Code</div>
    <div class="mb-quick">Content</div>
    <div class="mb-quick">Workflow</div>
    <div class="mb-quick">Analyse</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
<div class="mb-ready">
    <div>
        <div class="mb-ready-icon">✦</div>
        <div class="mb-ready-title">MaByte ist bereit.</div>
        <div class="mb-ready-sub">Frag nach Strategie, Code, Content oder Workflows.</div>
    </div>
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

    st.markdown('<div class="mb-ai-shell">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="mb-hero-grid">
    <div>
        <div class="mb-kicker">● AI Operating System</div>
        <div class="mb-title">MaByte Intelligence</div>
        <div class="mb-subtitle">Strategie. Code. Content. Workflows.</div>
    </div>
""",
        unsafe_allow_html=True,
    )

    render_session_card()

    st.markdown("</div>", unsafe_allow_html=True)

    render_metrics()

    st.markdown(
        """
<div class="mb-project-card">
    <div class="mb-card-head">Projekt</div>
    <div class="mb-card-title">Kontext wählen</div>
    <div class="mb-card-sub">Optional für bessere Antworten.</div>
""",
        unsafe_allow_html=True,
    )

    project = project_selector()

    st.markdown("</div>", unsafe_allow_html=True)

    render_quick_start()

    render_history(project)

    st.markdown("</div>", unsafe_allow_html=True)

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