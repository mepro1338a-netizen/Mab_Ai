import streamlit as st

from chat_service import generate_chat
from chat_memory import (
    init_chat_memory,
    save_chat_message,
    load_chat_history,
    clear_chat_history,
)
from database import spend_tokens, save_usage, add_audit_log
from config import TOKEN_COSTS
from ui_helpers import require_login, sync_session_user
from database import get_user


def render_chat():
    require_login()
    init_chat_memory()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">FREE FEATURE</span>
            <h1>💬 Memory Chat</h1>
            <p style="font-size:20px;color:#d4d4d8;line-height:1.7;">
                Chatte mit Mabyte. Dein Verlauf wird dauerhaft gespeichert.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = load_chat_history(st.session_state.user)

    for msg in history:
        if msg["role"] == "system":
            continue

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Schreibe eine Nachricht...")

    if prompt:
        cost = TOKEN_COSTS.get("chat", 1)

        ok, token_msg = spend_tokens(st.session_state.user, cost)

        if not ok:
            st.error(token_msg)
            return

        save_chat_message(st.session_state.user, "user", prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Mabyte denkt nach..."):
                success, answer = generate_chat(prompt, history=history)

            if success:
                save_chat_message(st.session_state.user, "assistant", answer)
                st.markdown(answer)

                save_usage(
                    username=st.session_state.user,
                    tool="chat",
                    prompt=prompt,
                    tokens_used=0,
                    cost_tokens=cost,
                    api_provider="openai",
                    status="success",
                )

                add_audit_log(
                    actor=st.session_state.user,
                    action="chat_message",
                    target="chat",
                    details=prompt[:250],
                )

                user = get_user(st.session_state.user)
                sync_session_user(user)

            else:
                st.error(answer)

                save_usage(
                    username=st.session_state.user,
                    tool="chat",
                    prompt=prompt,
                    tokens_used=0,
                    cost_tokens=cost,
                    api_provider="openai",
                    status="failed",
                )

    if st.button("🗑 Chat Verlauf löschen", key="clear_chat_history"):
        clear_chat_history(st.session_state.user)
        st.rerun()
