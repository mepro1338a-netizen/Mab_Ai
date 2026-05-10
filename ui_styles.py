import streamlit as st


def load_css():
    st.markdown(
        """
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 30%),
        radial-gradient(circle at bottom right, rgba(139,92,246,0.12), transparent 30%),
        linear-gradient(135deg, #050816 0%, #081120 45%, #0a1630 100%);
    color: white;
}

[data-testid="stSidebar"] {
    background: rgba(8, 12, 26, 0.96);
    border-right: 1px solid rgba(96,165,250,0.18);
}

.sidebar-subtitle {
    color: #93c5fd;
    text-align: center;
    margin-top: 4px;
    margin-bottom: 16px;
    font-size: 13px;
    font-weight: 700;
}

.sidebar-user-card {
    background: linear-gradient(145deg, rgba(12,18,40,.98), rgba(18,36,74,.88));
    border: 1px solid rgba(96,165,250,.35);
    border-radius: 16px;
    padding: 13px;
    margin: 14px 0 18px 0;
    color: white;
    font-size: 13px;
    line-height: 1.65;
    box-shadow: 0 0 24px rgba(59,130,246,.18);
}

.sidebar-user-name {
    font-size: 15px;
    font-weight: 800;
    color: #7dd3fc;
    margin-bottom: 6px;
}

.stButton > button {
    width: 100%;
    border-radius: 18px;
    border: 1px solid rgba(96,165,250,0.35);
    background: linear-gradient(135deg, #14315f, #1d4f91);
    color: white;
    font-weight: 700;
    padding: 14px;
    transition: 0.25s ease;
    box-shadow: 0 0 18px rgba(59,130,246,0.18);
}

.stButton > button:hover {
    transform: translateY(-2px);
    border: 1px solid #60a5fa;
    box-shadow: 0 0 28px rgba(59,130,246,0.45);
}

.hero-title {
    text-align: center;
    font-size: 58px;
    font-weight: 900;
    color: white;
    margin-bottom: 10px;
}

.hero-subtitle {
    text-align: center;
    font-size: 24px;
    color: #cbd5e1;
    margin-bottom: 55px;
    font-weight: 600;
}

.tool-card {
    background: linear-gradient(145deg, rgba(12,18,40,0.95), rgba(15,25,55,0.95));
    border: 1px solid rgba(96,165,250,0.15);
    border-radius: 28px;
    padding: 35px;
    min-height: 260px;
    transition: 0.3s ease;
    box-shadow: 0 0 35px rgba(59,130,246,0.08), inset 0 0 25px rgba(255,255,255,0.02);
}

.tool-card:hover {
    transform: translateY(-6px);
    border: 1px solid rgba(96,165,250,0.45);
    box-shadow: 0 0 45px rgba(59,130,246,0.24), 0 0 90px rgba(59,130,246,0.12);
}

.tool-title {
    font-size: 42px;
    font-weight: 900;
    color: white;
    margin-bottom: 22px;
}

.tool-text {
    color: #cbd5e1;
    font-size: 22px;
    line-height: 1.7;
}

/* CHAT INPUT FIX */
[data-testid="stChatInput"] {
    background: rgba(8, 14, 30, 0.96) !important;
    border-top: 1px solid rgba(96,165,250,.25) !important;
}

[data-testid="stChatInput"] > div {
    background: transparent !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input,
[data-testid="stChatInput"] div[contenteditable="true"] {
    background: linear-gradient(135deg, #0b1633, #10284d) !important;
    color: white !important;
    border: 1px solid rgba(96,165,250,.55) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 28px rgba(59,130,246,.22) !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: #93c5fd !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
    color: white !important;
    border-radius: 14px !important;
}

/* NORMAL INPUTS */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background: linear-gradient(135deg, #0b1633, #10284d) !important;
    color: white !important;
    border: 1px solid rgba(96,165,250,.45) !important;
    border-radius: 16px !important;
}

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #09111f;
}

::-webkit-scrollbar-thumb {
    background: #1d4ed8;
    border-radius: 20px;
}
</style>
        """,
        unsafe_allow_html=True,
    )