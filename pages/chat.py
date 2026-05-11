import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL, TOKEN_COSTS
from database import spend_tokens, save_usage, get_user
from ui_core import require_login, sync_session_user


client = OpenAI(api_key=OPENAI_API_KEY)


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


def ensure_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_memory_enabled" not in st.session_state:
        st.session_state.chat_memory_enabled = True

    if "chat_prompt_text" not in st.session_state:
        st.session_state.chat_prompt_text = ""


def clear_chat():
    st.session_state.messages = []
    st.rerun()


def charge_chat_tokens(prompt):
    cost = chat_cost()

    if get_tokens() < cost:
        st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
        st.stop()

    ok, msg = spend_tokens(username(), cost)

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


def build_messages(user_prompt):
    system_prompt = """
Du bist MaByte, ein professioneller AI-Assistent.
Antworte klar, direkt und hochwertig.
Sprich Deutsch.
Hilf bei Coding, Business, Content, SaaS, Social Media und Strategie.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if st.session_state.get("chat_memory_enabled", True):
        for msg in st.session_state.messages[-12:]:
            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

    messages.append({"role": "user", "content": user_prompt})
    return messages


def ai_response(prompt):
    if not OPENAI_API_KEY:
        return f"""
### Demo Antwort

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

    with st.spinner("MaByte denkt..."):
        response = ai_response(prompt)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    st.rerun()


def quick_prompt(text):
    st.session_state.chat_prompt_text = text
    st.rerun()


def render_header():
    st.title("💬 Memory Chat")
    st.write("Dein AI Workspace für Ideen, Code, Content, Business und Projekte.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("🪙 Tokens", get_tokens())

    with c2:
        st.metric("⚡ Kosten", f"{chat_cost()} Token")

    with c3:
        st.metric("💬 Nachrichten", len(st.session_state.messages))


def render_controls():
    with st.container(border=True):
        c1, c2 = st.columns([2, 1])

        with c1:
            st.toggle(
                "🧠 Memory für diese Sitzung aktiv",
                key="chat_memory_enabled",
            )

        with c2:
            if st.button("🧹 Chat leeren", use_container_width=True):
                clear_chat()


def render_quick_prompts():
    st.subheader("⚡ Quick Prompts")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("💡 Content Ideen", use_container_width=True):
            quick_prompt("Gib mir 10 virale Content-Ideen für TikTok über AI.")

    with c2:
        if st.button("💻 Code Hilfe", use_container_width=True):
            quick_prompt("Hilf mir, diesen Python-Code zu verbessern.")

    with c3:
        if st.button("📈 Business Plan", use_container_width=True):
            quick_prompt("Erstelle mir einen einfachen Businessplan für meine AI-SaaS Plattform.")

    c4, c5, c6 = st.columns(3)

    with c4:
        if st.button("🎬 Reel Hooks", use_container_width=True):
            quick_prompt("Schreibe mir 5 starke Hooks für ein Reel über AI Business.")

    with c5:
        if st.button("🛠️ Debugging", use_container_width=True):
            quick_prompt("Ich habe einen Fehler in meiner Streamlit App. Hilf mir beim Debuggen.")

    with c6:
        if st.button("🚀 SaaS Strategie", use_container_width=True):
            quick_prompt("Gib mir eine Roadmap, wie ich meine AI SaaS Plattform skalieren kann.")


def render_messages():
    st.subheader("💬 Verlauf")

    if not st.session_state.messages:
        st.info("Noch keine Nachrichten. Starte unten deinen Chat.")
        return

    for msg in st.session_state.messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)


def render_prompt_box():
    st.subheader("✍️ Nachricht")

    with st.form("chat_form", clear_on_submit=True):
        prompt = st.text_area(
            "Nachricht",
            value=st.session_state.get("chat_prompt_text", ""),
            height=140,
            placeholder="Schreibe deine Nachricht an MaByte...",
        )

        c1, c2 = st.columns([3, 1])

        with c1:
            st.caption(
                f"Kosten: {chat_cost()} Token pro Nachricht. "
                "Memory nutzt die letzten 12 Nachrichten."
            )

        with c2:
            submitted = st.form_submit_button(
                "🚀 Senden",
                use_container_width=True,
            )

        if submitted:
            st.session_state.chat_prompt_text = ""
            send_prompt(prompt)


def render_chat():
    require_login()
    ensure_chat_state()

    render_header()
    st.divider()

    render_controls()
    st.divider()

    render_quick_prompts()
    st.divider()

    render_messages()
    st.divider()

    render_prompt_box()