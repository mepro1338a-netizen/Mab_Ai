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
    save_project_chat_message,
    list_project_chat_memory,
    spend_tokens,
    save_usage,
    get_user,
    workspace_activity_score,
    latest_tool_used,
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


# =========================================================
# CLEAN PREMIUM CSS
# =========================================================

def load_chat_css():

    st.markdown(
        """
<style>

/* =========================================================
REMOVE STREAMLIT UGLY STUFF
========================================================= */

.block-container{
    padding-top:110px!important;
    max-width:1400px!important;
}

hr{
    display:none!important;
}

/* =========================================================
MAIN HERO
========================================================= */

.chat-shell{
    background:
        radial-gradient(circle at top right, rgba(56,189,248,.14), transparent 30%),
        linear-gradient(
            135deg,
            rgba(5,10,20,.98),
            rgba(8,15,28,.98)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:34px;

    padding:34px;

    margin-bottom:22px;

    box-shadow:
        0 0 40px rgba(0,0,0,.35);
}

.chat-kicker{
    color:#7dd3fc;
    font-size:12px;
    font-weight:900;
    letter-spacing:.18em;
    text-transform:uppercase;
}

.chat-title{
    color:#ffe7a3;
    font-size:52px;
    font-weight:1000;
    line-height:1;
    margin-top:12px;
}

.chat-sub{
    color:#94a3b8;
    font-size:15px;
    line-height:1.7;
    margin-top:14px;
    max-width:720px;
}

/* =========================================================
TOP CARDS
========================================================= */

.top-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:16px;
    margin-top:24px;
}

.top-card{
    background:
        linear-gradient(
            180deg,
            rgba(15,23,42,.95),
            rgba(9,14,24,.95)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:24px;

    padding:20px;
}

.top-label{
    color:#7dd3fc;
    font-size:11px;
    font-weight:900;
    letter-spacing:.14em;
    text-transform:uppercase;
}

.top-value{
    color:#ffe7a3;
    font-size:32px;
    font-weight:1000;
    margin-top:8px;
}

/* =========================================================
CHAT AREA
========================================================= */

.chat-wrap{
    margin-top:28px;
}

.user-msg{
    margin-left:auto;
    width:fit-content;
    max-width:75%;

    background:
        linear-gradient(
            135deg,
            rgba(37,99,235,.24),
            rgba(56,189,248,.16)
        );

    border:
        1px solid rgba(56,189,248,.18);

    border-radius:26px 26px 10px 26px;

    padding:18px;

    margin-bottom:14px;
}

.ai-msg{
    width:fit-content;
    max-width:78%;

    background:
        linear-gradient(
            180deg,
            rgba(15,23,42,.96),
            rgba(9,14,24,.98)
        );

    border:
        1px solid rgba(255,255,255,.05);

    border-radius:26px 26px 26px 10px;

    padding:18px;

    margin-bottom:14px;
}

.msg-role{
    color:#7dd3fc;
    font-size:11px;
    font-weight:900;
    text-transform:uppercase;
    margin-bottom:10px;
}

.msg-content{
    color:#ffe7a3;
    line-height:1.8;
    font-size:15px;
}

/* =========================================================
INPUT
========================================================= */

[data-testid="stChatInput"]{
    position:fixed!important;
    bottom:18px!important;
    left:320px!important;
    right:30px!important;
    z-index:999999!important;
}

[data-testid="stChatInput"] textarea{
    background:
        linear-gradient(
            180deg,
            rgba(15,23,42,.98),
            rgba(8,12,20,.98)
        )!important;

    color:#ffe7a3!important;

    border:
        1px solid rgba(56,189,248,.16)!important;

    border-radius:22px!important;

    min-height:58px!important;
}

[data-testid="stChatInput"] button{
    background:
        linear-gradient(
            135deg,
            #0ea5e9,
            #38bdf8
        )!important;

    color:white!important;

    border-radius:14px!important;
}

/* =========================================================
SELECTBOX
========================================================= */

.stSelectbox > div > div{
    background:
        rgba(15,23,42,.96)!important;

    color:#ffe7a3!important;

    border:
        1px solid rgba(255,255,255,.06)!important;

    border-radius:18px!important;
}

/* =========================================================
MOBILE
========================================================= */

@media(max-width:900px){

.top-grid{
    grid-template-columns:1fr;
}

[data-testid="stChatInput"]{
    left:14px!important;
    right:14px!important;
}

.chat-title{
    font-size:38px;
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
        return None

    options = {
        f"{p.get('title')} · {p.get('workspace')}":
        p.get("id")

        for p in projects
    }

    labels = list(options.keys())

    selected = st.selectbox(
        "Workspace",
        labels
    )

    project_id = options[selected]

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
Projekt:
{project.get('title')}

Workspace:
{project.get('workspace')}

Beschreibung:
{project.get('description')}
"""

    return [
        {
            "role": "system",
            "content": f"""
Du bist MaByte.

Ein hochwertiger AI Operating System Assistant.

Arbeite:
- modern
- strategisch
- klar
- intelligent
- premium

{project_context}
"""
        },
        {
            "role": "user",
            "content": prompt
        }
    ]


def ai_response(prompt, project):

    if not OPENAI_API_KEY:

        return "OPENAI_API_KEY fehlt."

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
# HISTORY
# =========================================================

def render_history(project):

    if not project:
        return

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

        bubble = (
            "user-msg"
            if role == "user"
            else "ai-msg"
        )

        role_name = (
            "YOU"
            if role == "user"
            else "MABYTE"
        )

        st.markdown(
            f"""
<div class="{bubble}">

<div class="msg-role">
{role_name}
</div>

<div class="msg-content">
{content}
</div>

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

    load_chat_css()

    st.markdown(
        f"""
<div class="chat-shell">

<div class="chat-kicker">
AI OPERATING SYSTEM
</div>

<div class="chat-title">
MaByte Intelligence
</div>

<div class="chat-sub">
Persistent AI Memory, Project Awareness,
Workspace Intelligence und AI Workflow Control.
</div>

<div class="top-grid">

<div class="top-card">
<div class="top-label">
Available Tokens
</div>

<div class="top-value">
{get_tokens():,}
</div>
</div>

<div class="top-card">
<div class="top-label">
Chat Cost
</div>

<div class="top-value">
{chat_cost()}
</div>
</div>

<div class="top-card">
<div class="top-label">
Last Tool
</div>

<div class="top-value">
{latest_tool_used(username())}
</div>
</div>

</div>

</div>
        """,
        unsafe_allow_html=True,
    )

    project = project_selector()

    st.markdown(
        """
<div class="chat-wrap">
        """,
        unsafe_allow_html=True,
    )

    render_history(project)

    st.markdown(
        """
</div>
        """,
        unsafe_allow_html=True,
    )

    prompt = st.chat_input(
        "Schreibe an MaByte..."
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

        with st.spinner(
            "MaByte denkt nach..."
        ):

            answer = ai_response(
                prompt,
                project
            )

        answer += (
            f"\n\n---\n"
            f"🪙 Tokens: {cost}"
        )

        if project:

            save_project_chat_message(
                project_id=project.get("id"),
                username=username(),
                role="assistant",
                message=answer,
            )

        st.rerun()