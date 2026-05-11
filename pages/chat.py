import streamlit as st
from ui_core import sync_session_user


def render_chat():
    sync_session_user()

    if not st.session_state.get("logged_in"):
        st.switch_page("pages/auth.py")
        return

    st.markdown(
        """
        <style>
        .chat-wrap{
            padding-top:20px;
        }

        .chat-hero{
            background: linear-gradient(135deg,#0f172a,#111827);
            border:1px solid rgba(59,130,246,.35);
            border-radius:28px;
            padding:38px;
            margin-bottom:30px;
            box-shadow:0 0 40px rgba(59,130,246,.18);
        }

        .chat-title{
            font-size:42px;
            font-weight:900;
            color:white;
            margin-bottom:10px;
        }

        .chat-sub{
            color:#94a3b8;
            font-size:18px;
        }

        .msg{
            background:#111827;
            border:1px solid rgba(255,255,255,.08);
            padding:18px;
            border-radius:18px;
            margin-bottom:14px;
            color:white;
        }

        .msg-user{
            border-left:4px solid #38bdf8;
        }

        .msg-ai{
            border-left:4px solid #8b5cf6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="chat-hero">
            <div class="chat-title">💬 MaByte Chat</div>
            <div class="chat-sub">
                Dein smarter AI Workspace für Ideen, Coding, Content und Automationen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(
                f'<div class="msg msg-user">🧑 {content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg msg-ai">🤖 {content}</div>',
                unsafe_allow_html=True,
            )

    prompt = st.chat_input("Schreibe eine Nachricht...")

    if prompt:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        ai_response = f"Du hast geschrieben: {prompt}"

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": ai_response,
            }
        )

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


render_chat()