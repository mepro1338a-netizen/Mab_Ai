import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS
from database import spend_tokens, save_usage, get_user
from ui_core import require_login, sync_session_user


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
# STATE
# =========================================================

def ensure_state():

    st.session_state.setdefault(
        "messages",
        [],
    )

    st.session_state.setdefault(
        "chat_memory_enabled",
        True,
    )

    st.session_state.setdefault(
        "quick_prompt_value",
        "",
    )


def clear_chat():

    st.session_state.messages = []

    st.rerun()


# =========================================================
# EXPORT
# =========================================================

def export_chat():

    lines = [
        "MaByte Chat Export",
        "=" * 30,
        "",
    ]

    for msg in st.session_state.messages:

        role = (
            "Du"
            if msg["role"] == "user"
            else "MaByte"
        )

        lines.append(f"{role}:")
        lines.append(msg["content"])
        lines.append("")

    return "\n".join(lines)


# =========================================================
# TOKENS
# =========================================================

def charge(prompt):

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
        prompt=prompt[:2000],
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

def build_messages(prompt):

    system_prompt = """
Du bist MaByte, ein moderner AI-Assistent.

Hilf bei:
- Business
- SaaS
- Content
- Coding
- Marketing
- Social Media
- Branding

Antworte klar, modern und hochwertig.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    if st.session_state.chat_memory_enabled:

        messages.extend(
            st.session_state.messages[-10:]
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    return messages


def ai_response(prompt):

    if not OPENAI_API_KEY:

        return f"""
### Demo Antwort

Du hast geschrieben:

> {prompt}

OPENAI_API_KEY fehlt aktuell noch.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=build_messages(prompt),
        temperature=0.65,
    )

    return response.choices[0].message.content


# =========================================================
# SEND
# =========================================================

def submit(prompt):

    prompt = (prompt or "").strip()

    if not prompt:

        st.warning(
            "Bitte Nachricht eingeben."
        )

        return

    charged = charge(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.spinner(
        "MaByte denkt..."
    ):

        answer = ai_response(prompt)

    answer += (
        f"\n\n---\n"
        f"Verbraucht: {charged} Tokens"
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    st.session_state.quick_prompt_value = ""

    st.rerun()


# =========================================================
# QUICKS
# =========================================================

def quick(text):

    st.session_state.quick_prompt_value = text

    st.rerun()


# =========================================================
# UI
# =========================================================

def render_topbar():

    left, right = st.columns([2, 1])

    with left:

        st.title("💬 Memory Chat")

        st.caption(
            "Dein persönlicher AI Workspace."
        )

    with right:

        st.download_button(
            "⬇️ Chat exportieren",
            data=export_chat(),
            file_name="mabyte_chat.txt",
            mime="text/plain",
            use_container_width=True,
        )


def render_stats():

    a, b, c = st.columns(3)

    with a:

        st.metric(
            "🪙 Guthaben",
            get_tokens(),
        )

    with b:

        st.metric(
            "⚡ Nachricht",
            f"{chat_cost()} Token",
        )

    with c:

        st.metric(
            "💬 Verlauf",
            len(st.session_state.messages),
        )


def render_quicks():

    st.caption("Quick Start")

    q1, q2, q3, q4 = st.columns(4)

    with q1:

        if st.button(
            "💡 Ideen",
            use_container_width=True,
        ):
            quick(
                "Gib mir 10 starke Content Ideen."
            )

    with q2:

        if st.button(
            "💻 Code",
            use_container_width=True,
        ):
            quick(
                "Verbessere meinen Code professionell."
            )

    with q3:

        if st.button(
            "📈 Wachstum",
            use_container_width=True,
        ):
            quick(
                "Wie skaliere ich mein SaaS Business?"
            )

    with q4:

        if st.button(
            "🎬 Reel",
            use_container_width=True,
        ):
            quick(
                "Schreibe mir starke Reel Hooks."
            )


def render_history():

    if not st.session_state.messages:

        st.info(
            "Noch kein Verlauf vorhanden."
        )

        return

    for msg in st.session_state.messages:

        with st.chat_message(
            "user"
            if msg["role"] == "user"
            else "assistant"
        ):

            st.markdown(
                msg["content"]
            )


def render_composer():

    with st.container(border=True):

        prompt = st.text_area(
            "Nachricht",
            value=st.session_state.get(
                "quick_prompt_value",
                "",
            ),
            height=120,
            placeholder="Schreibe deine Nachricht an MaByte...",
        )

        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:

            st.toggle(
                "🧠 Memory",
                key="chat_memory_enabled",
            )

        with c2:

            if st.button(
                "🧹 Leeren",
                use_container_width=True,
            ):
                clear_chat()

        with c3:

            if st.button(
                "🚀 Senden",
                use_container_width=True,
            ):
                submit(prompt)


# =========================================================
# MAIN
# =========================================================

def render_chat():

    require_login()

    ensure_state()

    render_topbar()

    render_stats()

    render_quicks()

    st.divider()

    render_history()

    st.divider()

    render_composer()