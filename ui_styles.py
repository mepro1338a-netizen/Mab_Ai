import streamlit as st


def load_css():
    st.markdown(
        """
<style>

html, body, .stApp {
    background: #05050a !important;
    color: white !important;
}

[data-testid="stHeader"] {
    background: #000000 !important;
}

.block-container {
    max-width: 1400px !important;
    padding-top: 100px !important;
}

section[data-testid="stSidebar"] {
    background: #050509 !important;
    border-right: 1px solid rgba(255,215,0,.20);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    background: #000 !important;
    color: white !important;
    border: 1px solid rgba(255,215,0,.45) !important;
    border-radius: 16px !important;
    min-height: 48px !important;
    font-weight: 700 !important;
}

.stButton button:hover {
    border-color: #ffd700 !important;
    color: #ffd700 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #0b0b12 !important;
    color: white !important;
    border-radius: 14px !important;
}

.page-card {
    background: #101018;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 24px;
}

.hero-box {
    background:
        radial-gradient(circle at top left, rgba(0,183,255,.25), transparent 35rem),
        radial-gradient(circle at top right, rgba(168,85,247,.25), transparent 35rem),
        linear-gradient(135deg, #10253c 0%, #171e36 55%, #42206a 100%);
    border-radius: 42px;
    padding: 80px 60px;
    text-align: center;
    margin-bottom: 34px;
}

.hero-title {
    font-size: 72px;
    font-weight: 900;
    color: white;
}

.hero-subtitle {
    font-size: 26px;
    color: #e5e7eb;
    margin-top: 18px;
}

.result-box {
    background: #080812;
    border: 1px solid rgba(0,183,255,.25);
    border-radius: 24px;
    padding: 24px;
    margin-top: 24px;
}

.stChatInputContainer {
    background: #05050a !important;
}

.stChatInputContainer textarea {
    background: #0b0b12 !important;
    color: white !important;
    border: 1px solid rgba(255,215,0,.25) !important;
}

[data-testid="stChatMessage"] {
    background: #0b0b12 !important;
    border-radius: 18px !important;
    padding: 14px !important;
}

[data-testid="stChatMessage"] * {
    color: white !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )