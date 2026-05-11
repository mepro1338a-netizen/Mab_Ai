import streamlit as st


def render_chat():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    st.markdown(
        """
<style>
.chat-wrap {
    max-width: 1100px;
    margin: auto;
    padding-top: 20px;
    padding-bottom: 40px;
}

.chat-hero {
    background: linear-gradient(135deg, #071427, #0f2747);
    border: 1px solid rgba(56,189,248,.28);
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 28px;
    box-shadow: 0 0 35px rgba(56,189,248,.16);
}

.chat-title {
    font-size: 44px;
    font-weight: 1000;
    color: white;
    margin-bottom: 8px;
}

.chat-sub {
    color: #dbeafe;
    font-size: 18px;
    font-weight: 700;
}

.msg {
    background: rgba(15,23,42,.92);
    border: 1px solid rgba(125,211,252,.14);
    padding: 18px;
    border-radius: 18px;
    margin-bottom: 14px;
    color: white;
    font-size: 16px;
}

.msg-user {
    border-left: 4px solid #38bdf8;
}

.msg-ai {
    border-left: 4px solid #8b5cf6;
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
        role = msg.get("role", "assistant")
        content = msg.get("content", "")

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