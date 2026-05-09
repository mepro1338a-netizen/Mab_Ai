import streamlit as st


def render_chat():

    st.markdown(
        """
        <div class="tool-hero">
            <h1>💬 Memory Chat</h1>
            <p>Chatte mit Mabyte und speichere deinen Verlauf.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Schreibe eine Nachricht...")

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        response = f"""
Mabyte Response:

Du hast geschrieben:

> {prompt}

Diese Funktion kann später mit OpenAI verbunden werden.
"""

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        with st.chat_message("assistant"):
            st.markdown(response)