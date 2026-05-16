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


# =========================================================
# HELPERS
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


def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def active_project_id():
    return st.session_state.get("active_project_id")


# =========================================================
# PREMIUM CHAT CSS
# =========================================================

def chat_css():

    st.markdown(
        """
<style>

/* =========================================================
CHAT HERO
========================================================= */

.chat-hero{
    padding:28px;
    border-radius:30px;

    background:
        radial-gradient(circle at top right, rgba(56,189,248,.16), transparent 28%),
        linear-gradient(
            135deg,
            rgba(8,18,34,.98),
            rgba(15,23,42,.96)
        );

    border:
        1px solid rgba(255,255,255,.06);

    margin-bottom:22px;

    box-shadow:
        0 0 40px rgba(0,140,255,.08);
}

.chat-kicker{
    color:#7dd3fc;
    font-size:12px;
    font-weight:900;
    letter-spacing:.16em;
    text-transform:uppercase;
}

.chat-title{
    color:#ffe7a3;
    font-size:42px;
    font-weight:1000;
    line-height:1;
    margin-top:10px;
}

.chat-sub{
    color:#cbd5e1;
    font-size:15px;
    line-height:1.6;
    margin-top:14px;
    max-width:850px;
}

/* =========================================================
CHAT MESSAGES
========================================================= */

.user-bubble{
    background:
        linear-gradient(
            135deg,
            rgba(37,99,235,.24),
            rgba(56,189,248,.18)
        );

    border:
        1px solid rgba(56,189,248,.18);

    border-radius:24px 24px 8px 24px;

    padding:18px;

    margin-bottom:14px;
}

.assistant-bubble{
    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,.96),
            rgba(30,41,59,.92)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:24px 24px 24px 8px;

    padding:18px;

    margin-bottom:14px;
}

.message-role{
    color:#7dd3fc;
    font-size:11px;
    font-weight:900;
    letter-spacing:.14em;
    text-transform:uppercase;
    margin-bottom:10px;
}

.message-content{
    color:#ffe7a3;
    line-height:1.75;
    font-size:15px;
}

/* =========================================================
SIDEPANEL
========================================================= */

.chat-panel{
    background:
        linear-gradient(
            180deg,
            rgba(11,24,44,.98),
            rgba(8,16,30,.98)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:26px;

    padding:20px;

    margin-bottom:18px;
}

.chat-panel-title{
    color:#ffffff;
    font-size:18px;
    font-weight:900;
    margin-bottom:12px;
}

.memory-chip{
    background:
        rgba(56,189,248,.12);

    border:
        1px solid rgba(56,189,248,.18);

    border-radius:14px;

    padding:10px 12px;

    margin-bottom:10px;

    color:#ffe7a3;
    font-size:13px;
}

/* =========================================================
CHAT INPUT
========================================================= */

[data-testid="stChatInput"]{
    position:sticky;
    bottom:18px;
    z-index:999;
}

[data-testid="stChatInput"] textarea{
    background:
        rgba(15,23,42,.96)!important;

    border:
        1px solid rgba(56,189,248,.18)!important;

    border-radius:20px!important;

    color:#ffe7a3!important;
}

/* =========================================================
TOKEN BAR
========================================================= */

.token-bar{
    display:flex;
    gap:14px;
    margin-top:18px;
}

.token-card{
    flex:1;

    background:
        linear-gradient(
            135deg,
            rgba(11,24,44,.98),
            rgba(8,16,30,.98)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:22px;

    padding:18px;
}

.token-label{
    color:#7dd3fc;
    font-size:11px;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.12em;
}

.token-value{
    color:#ffe7a3;
    font-size:30px;
    font-weight:1000;
    margin-top:8px;
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
        st.info(
            "Kein Projekt aktiv. "
            "Erstelle unter Projects ein Projekt."
        )
        return None

    options = {
        f"{p.get('title')} · {p.get('workspace')}":
        p.get("id")

        for p in projects
    }

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


# =========================================================
# TOKENS
# =========================================================

def charge_chat(prompt):

    cost = chat_cost()

    if get_tokens() < cost:

        st.error(
            f"Nicht genug Tokens. "
            f"Benötigt: {cost}"
        )

        st.stop()

    ok, msg = spend_tokens(
        username(),
        cost
    )

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


# =========================================================
# MEMORY
# =========================================================

def build_global_memory(user):

    memories = list_global_memory(
        user,
        limit=25
    )

    if not memories:
        return "Keine globale Memory vorhanden."

    text = ""

    for mem in memories:

        text += (
            f"- "
            f"{mem.get('memory_type')}: "
            f"{mem.get('content')}\n"
        )

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


# =========================================================
# CONTEXT
# =========================================================

def build_project_context(project):

    if not project:
        return "Kein aktives Projekt."

    memories = list_project_memory(
        project.get("id")
    )

    grouped = {}

    for memory in memories[:20]:

        memory_type = memory.get(
            "memory_type",
            "memory"
        )

        if memory_type not in grouped:
            grouped[memory_type] = []

        grouped[memory_type].append(
            memory.get("content", "")
        )

    memory_text = ""

    for memory_type, entries in grouped.items():

        memory_text += f"\n[{memory_type.upper()}]\n"

        for entry in entries[:5]:
            memory_text += f"- {entry}\n"

    if not memory_text:
        memory_text = "Keine Memory."

    return f"""
PROJEKT

Titel:
{project.get('title')}

Workspace:
{project.get('workspace')}

Beschreibung:
{project.get('description')}

MEMORY:
{memory_text}
"""


def build_chat_history(project):

    history_messages = []

    if project:

        history = list_project_chat_memory(
            project.get("id"),
            limit=20
        )

        for msg in history:

            role = msg.get(
                "role",
                "assistant"
            )

            content = msg.get(
                "message",
                ""
            )

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


# =========================================================
# AI
# =========================================================

def build_messages(prompt, project):

    system_prompt = f"""
Du bist MaByte.

Ein professioneller AI Operating System Assistant.

Arbeite:
- strategisch
- hochwertig
- workflow-orientiert
- intelligent
- konkret
"""

    messages = [
        {
            "role": "system",
            "content":
                system_prompt
                + "\n\nGLOBAL MEMORY:\n"
                + build_global_memory(username())
                + "\n\nPROJECT CONTEXT:\n"
                + build_project_context(project)
        }
    ]

    messages.extend(
        build_chat_history(project)
    )

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

Projekt:
{project.get('title') if project else 'Kein Projekt'}

Prompt:
{prompt}

OPENAI_API_KEY fehlt.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(
            prompt,
            project
        ),
        temperature=0.7,
    )

    return response.choices[0].message.content


# =========================================================
# CHAT HISTORY
# =========================================================

def render_history(project):

    if project:

        history = list_project_chat_memory(
            project.get("id"),
            limit=40
        )

        if not history:
            return

        for msg in history:

            role = msg.get(
                "role",
                "assistant"
            )

            content = msg.get(
                "message",
                ""
            )

            bubble = (
                "user-bubble"
                if role == "user"
                else "assistant-bubble"
            )

            role_label = (
                "You"
                if role == "user"
                else "MaByte"
            )

            st.markdown(
                f"""
<div class="{bubble}">

    <div class="message-role">
        {role_label}
    </div>

    <div class="message-content">
        {content}
    </div>

</div>
                """,
                unsafe_allow_html=True,
            )

    else:

        for msg in st.session_state.messages:

            role = msg.get(
                "role",
                "assistant"
            )

            content = msg.get(
                "content",
                ""
            )

            bubble = (
                "user-bubble"
                if role == "user"
                else "assistant-bubble"
            )

            role_label = (
                "You"
                if role == "user"
                else "MaByte"
            )

            st.markdown(
                f"""
<div class="{bubble}">

    <div class="message-role">
        {role_label}
    </div>

    <div class="message-content">
        {content}
    </div>

</div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# SIDEPANELS
# =========================================================

def render_project_panel(project):

    st.markdown(
        """
<div class="chat-panel">
<div class="chat-panel-title">
Project Intelligence
</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if not project:

        st.info(
            "Kein aktives Projekt."
        )

        return

    st.metric(
        "Workspace Score",
        f"{workspace_activity_score(username())}/100"
    )

    st.metric(
        "Chat Tokens",
        get_tokens()
    )

    memories = list_project_memory(
        project.get("id")
    )

    if memories:

        st.write("### Letzte Memory")

        for memory in memories[:4]:

            st.markdown(
                f"""
<div class="memory-chip">
{memory.get('content', '')[:120]}
</div>
                """,
                unsafe_allow_html=True,
            )


def render_global_memory_panel():

    memories = list_global_memory(
        username(),
        limit=8
    )

    st.markdown(
        """
<div class="chat-panel">
<div class="chat-panel-title">
Global Memory
</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if not memories:
        st.caption("Noch keine globale Memory.")
        return

    for mem in memories[:5]:

        st.markdown(
            f"""
<div class="memory-chip">
{mem.get('content', '')[:90]}
</div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# MAIN
# =========================================================

def render_chat():

    if not st.session_state.get("logged_in"):

        st.session_state.page = "auth"

        st.rerun()

        return

    ensure_state()

    chat_css()

    st.markdown(
        """
<div class="chat-hero">

    <div class="chat-kicker">
        AI OPERATING SYSTEM
    </div>

    <div class="chat-title">
        MaByte Intelligence
    </div>

    <div class="chat-sub">
        Persistent AI Memory, Project Context,
        Workspace Intelligence und Workflow Awareness.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # TOP STATS
    # =====================================================

    st.markdown(
        f"""
<div class="token-bar">

    <div class="token-card">
        <div class="token-label">
            Available Tokens
        </div>

        <div class="token-value">
            {get_tokens():,}
        </div>
    </div>

    <div class="token-card">
        <div class="token-label">
            Chat Cost
        </div>

        <div class="token-value">
            {chat_cost()}
        </div>
    </div>

    <div class="token-card">
        <div class="token-label">
            Last Tool
        </div>

        <div class="token-value">
            {latest_tool_used(username())}
        </div>
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    left, right = st.columns(
        [1.65, .8],
        gap="large"
    )

    with left:

        project = project_selector()

        st.divider()

        render_history(project)

    with right:

        render_project_panel(project)

        render_global_memory_panel()

    prompt = st.chat_input(
        "Schreibe an MaByte..."
    )

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

        with st.spinner(
            "MaByte analysiert Memory..."
        ):

            answer = ai_response(
                prompt,
                project
            )

        answer += (
            f"\n\n---\n"
            f"🪙 Verbrauchte Tokens: {cost}"
        )

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