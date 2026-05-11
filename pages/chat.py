import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS
from database import spend_tokens, save_usage, get_user
from ui_core import require_login, sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# USER HELPERS
# =========================================================

def username():
    return st.session_state.get("user")


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user():
    user = get_user(username())

    if user:
        sync_session_user(user)


def chat_cost():
    return int(TOKEN_COSTS.get("chat", 1))


# =========================================================
# CHAT STATE
# =========================================================

def ensure_chat_state():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_memory_enabled" not in st.session_state:
        st.session_state.chat_memory_enabled = True

    if "chat_prompt_box" not in st.session_state:
        st.session_state.chat_prompt_box = ""


def clear_chat():
    st.session_state.messages = []
    st.rerun()


# =========================================================
# TOKEN CHARGE
# =========================================================

def charge_chat_tokens(prompt):

    cost = chat_cost()

    if get_tokens() < cost:
        st.error(
            f"Nicht genug Tokens. "
            f"Benötigt: {cost}, verfügbar: {get_tokens()}"
        )
        st.stop()

    ok, msg = spend_tokens(
        username(),
        cost,
    )

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=username(),
        tool="chat",
        prompt=prompt,
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="openai",
        status="success",
    )

    sync_user()


# =========================================================
# MESSAGE BUILD
# =========================================================

def build_messages(user_prompt):

    system_prompt = """
Du bist MaByte, ein moderner professioneller AI Assistent.

Du hilfst bei:
- AI Business
- SaaS
- Content
- TikTok
- Instagram
- Coding
- Streamlit
- Python
- Marketing
- Branding

Antworte strukturiert, hochwertig und direkt.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    if st.session_state.get(
        "chat_memory_enabled",
        True,
    ):

        for msg in st.session_state.messages[-12:]:

            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

    messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    return messages


# =========================================================
# AI RESPONSE
# =========================================================

def ai_response(prompt):

    if not OPENAI_API_KEY:

        return f"""
### MaByte Demo Antwort

Du hast geschrieben:

> {prompt}

OPENAI_API_KEY fehlt aktuell noch in Railway.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt),
        temperature=0.7,
    )

    return response.choices[0].message.content


# =========================================================
# QUICK PROMPTS
# =========================================================

def set_prefill(text):

    st.session_state.chat_prompt_box = text


# =========================================================
# SEND
# =========================================================

def send_prompt(prompt):

    prompt = (prompt or "").strip()

    if not prompt:
        st.warning("Bitte Nachricht eingeben.")
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    charge_chat_tokens(prompt)

    with st.spinner("🧠 MaByte denkt nach..."):

        response = ai_response(prompt)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    st.session_state.chat_prompt_box = ""

    st.rerun()


# =========================================================
# HERO
# =========================================================

def render_hero():

    st.markdown(
        """
        <div style="
            padding: 34px;
            border-radius: 28px;
            background:
                linear-gradient(
                    135deg,
                    rgba(17,24,39,.92),
                    rgba(15,42,82,.92)
                );
            border: 1px solid rgba(96,165,250,.25);
            box-shadow: 0 0 40px rgba(56,189,248,.12);
            margin-bottom: 22px;
        ">
            <h1 style="
                color:white;
                margin-bottom:10px;
                font-size:42px;
                font-weight:900;
            ">
                💬 MaByte Memory Chat
            </h1>

            <p style="
                color:#cbd5e1;
                font-size:18px;
                line-height:1.6;
                margin:0;
            ">
                Dein AI Workspace für Business, Coding,
                Content, Ideen und Strategie.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# STATS
# =========================================================

def render_stats():

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🪙 Tokens",
            get_tokens(),
        )

    with c2:
        st.metric(
            "⚡ Kosten",
            f"{chat_cost()} Token",
        )

    with c3:
        st.metric(
            "💬 Nachrichten",
            len(st.session_state.messages),
        )

    with c4:
        st.metric(
            "🧠 Memory",
            "Aktiv"
            if st.session_state.get("chat_memory_enabled")
            else "Aus",
        )


# =========================================================
# SETTINGS
# =========================================================

def render_settings():

    with st.container(border=True):

        left, right = st.columns([2, 1])

        with left:

            st.toggle(
                "🧠 Verlauf & Kontext speichern",
                key="chat_memory_enabled",
            )

        with right:

            if st.button(
                "🧹 Chat leeren",
                use_container_width=True,
            ):
                clear_chat()


# =========================================================
# QUICK ACTIONS
# =========================================================

def render_quick_actions():

    st.markdown("### ⚡ Quick Actions")

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "💡 TikTok Ideen",
            use_container_width=True,
        ):
            set_prefill(
                "Gib mir 10 virale TikTok Ideen über AI."
            )
            st.rerun()

    with c2:

        if st.button(
            "💻 Coding Hilfe",
            use_container_width=True,
        ):
            set_prefill(
                "Hilf mir meinen Python Code zu optimieren."
            )
            st.rerun()

    with c3:

        if st.button(
            "📈 SaaS Strategie",
            use_container_width=True,
        ):
            set_prefill(
                "Gib mir eine SaaS Wachstumsstrategie."
            )
            st.rerun()

    c4, c5, c6 = st.columns(3)

    with c4:

        if st.button(
            "🎬 Reel Hooks",
            use_container_width=True,
        ):
            set_prefill(
                "Schreibe mir starke Reel Hooks."
            )
            st.rerun()

    with c5:

        if st.button(
            "🛠️ Debugging",
            use_container_width=True,
        ):
            set_prefill(
                "Hilf mir beim Debuggen meiner Streamlit App."
            )
            st.rerun()

    with c6:

        if st.button(
            "🚀 Startup Idee",
            use_container_width=True,
        ):
            set_prefill(
                "Gib mir eine profitable AI Startup Idee."
            )
            st.rerun()


# =========================================================
# CHAT MESSAGES
# =========================================================

def render_messages():

    if not st.session_state.messages:

        st.info(
            "Noch keine Nachrichten vorhanden."
        )

        return

    st.markdown("### 💬 Verlauf")

    for msg in st.session_state.messages:

        role = msg.get("role")
        content = msg.get("content")

        if role == "user":

            st.markdown(
                f"""
                <div style="
                    margin-bottom:18px;
                    padding:22px;
                    border-radius:22px;
                    background:
                        linear-gradient(
                            135deg,
                            rgba(15,23,42,.96),
                            rgba(30,41,59,.96)
                        );
                    border:
                        1px solid rgba(96,165,250,.18);
                ">
                    <div style="
                        font-weight:900;
                        color:#facc15;
                        margin-bottom:10px;
                    ">
                        👤 Du
                    </div>

                    <div style="
                        color:white;
                        line-height:1.7;
                    ">
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
                <div style="
                    margin-bottom:22px;
                    padding:26px;
                    border-radius:24px;
                    background:
                        linear-gradient(
                            135deg,
                            rgba(8,23,47,.96),
                            rgba(15,44,86,.96)
                        );
                    border:
                        1px solid rgba(59,130,246,.28);

                    box-shadow:
                        0 0 24px rgba(56,189,248,.10);
                ">
                    <div style="
                        font-weight:900;
                        color:#38bdf8;
                        margin-bottom:12px;
                    ">
                        🤖 MaByte
                    </div>

                    <div style="
                        color:white;
                        line-height:1.8;
                    ">
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# PROMPT BOX
# =========================================================

def render_prompt_box():

    st.markdown("### ✍️ Nachricht")

    with st.container(border=True):

        prompt = st.text_area(
            "Prompt",
            key="chat_prompt_box",
            height=170,
            placeholder="Schreibe deine Nachricht an MaByte...",
            label_visibility="collapsed",
        )

        left, right = st.columns([4, 1])

        with left:

            st.caption(
                f"""
Kosten:
{chat_cost()} Token pro Prompt
• Verlauf nutzt die letzten 12 Nachrichten
                """
            )

        with right:

            if st.button(
                "🚀 Senden",
                use_container_width=True,
            ):
                send_prompt(prompt)


# =========================================================
# MAIN
# =========================================================

def render_chat():

    require_login()

    ensure_chat_state()

    render_hero()

    render_stats()

    st.divider()

    render_settings()

    st.divider()

    render_quick_actions()

    st.divider()

    render_messages()

    st.divider()

    render_prompt_box()