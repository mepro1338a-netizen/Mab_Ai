import streamlit as st


def load_css():
    st.markdown(
        """
<style>
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 32%),
        radial-gradient(circle at bottom right, rgba(37,99,235,.18), transparent 36%),
        linear-gradient(135deg, #020617 0%, #061126 45%, #0b1d3a 100%);
    color: white;
}

.block-container {
    max-width: 1450px !important;
    padding-top: 42px !important;
    padding-bottom: 80px !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

#MainMenu, footer {
    visibility: hidden;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.16), transparent 28%),
        linear-gradient(180deg, #051027 0%, #071a33 100%) !important;
    border-right: 1px solid rgba(125,211,252,.22);
}

.sidebar-subtitle {
    color: #93c5fd;
    text-align: center;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 18px;
}

/* BUTTONS */
.stButton > button {
    width: 100%;
    border-radius: 18px !important;
    border: 1px solid rgba(125,211,252,.34) !important;
    background: linear-gradient(135deg, #0f3c73, #126ab8) !important;
    color: white !important;
    font-weight: 850 !important;
    min-height: 48px !important;
    box-shadow: 0 0 22px rgba(56,189,248,.16) !important;
    transition: .22s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    border-color: #7dd3fc !important;
    box-shadow: 0 0 35px rgba(56,189,248,.38) !important;
}

/* INPUTS */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background: linear-gradient(135deg, #07152e, #10284d) !important;
    color: white !important;
    border: 1px solid rgba(96,165,250,.45) !important;
    border-radius: 16px !important;
}

input::placeholder,
textarea::placeholder {
    color: #93c5fd !important;
}

/* CHAT */
[data-testid="stChatInput"] {
    background: rgba(2,6,23,.96) !important;
    border-top: 1px solid rgba(96,165,250,.25) !important;
}

[data-testid="stChatInput"] textarea {
    background: linear-gradient(135deg, #07152e, #10284d) !important;
    color: white !important;
    border: 1px solid rgba(96,165,250,.55) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 28px rgba(56,189,248,.20) !important;
}

[data-testid="stChatMessage"] {
    background: rgba(8,14,30,.88) !important;
    border: 1px solid rgba(96,165,250,.16) !important;
    border-radius: 20px !important;
    padding: 16px !important;
}

/* CARDS */
.page-card,
.media-card,
.output-box {
    background: linear-gradient(145deg, rgba(8,15,35,.96), rgba(13,35,72,.90));
    border: 1px solid rgba(96,165,250,.22);
    border-radius: 28px;
    padding: 32px;
    box-shadow: 0 0 38px rgba(37,99,235,.14);
}

.badge {
    display: inline-block;
    padding: 9px 16px;
    border-radius: 999px;
    background: rgba(37,99,235,.18);
    border: 1px solid rgba(125,211,252,.35);
    color: #7dd3fc;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: .8px;
    margin-bottom: 18px;
}

.sidebar-user-card {
    background: linear-gradient(145deg, rgba(8,15,35,.98), rgba(13,35,72,.90));
    border: 1px solid rgba(96,165,250,.32);
    border-radius: 18px;
    padding: 14px;
    margin: 16px 0;
    color: white;
    font-size: 13px;
    line-height: 1.65;
    box-shadow: 0 0 24px rgba(56,189,248,.16);
}

.sidebar-user-name {
    color: #7dd3fc;
    font-weight: 900;
    font-size: 15px;
    margin-bottom: 6px;
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #07111f;
}

::-webkit-scrollbar-thumb {
    background: #1d4ed8;
    border-radius: 999px;
}
</style>
        """,
        unsafe_allow_html=True,
    )