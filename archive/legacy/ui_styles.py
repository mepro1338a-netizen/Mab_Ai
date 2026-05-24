import streamlit as st


def load_css():
    st.markdown(
        """
<style>
html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(14,165,233,.12), transparent 30%),
        linear-gradient(135deg, #030712 0%, #071326 45%, #081a36 100%) !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top, rgba(59,130,246,.18), transparent 25%),
        linear-gradient(180deg, #06101f 0%, #08182d 100%) !important;
    border-right: 1px solid rgba(96,165,250,.18);
}

[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

.stButton > button {
    width: 100%;
    border-radius: 18px !important;
    min-height: 52px;
    background: linear-gradient(135deg, #0f3d73 0%, #1d7ff2 100%) !important;
    border: 1px solid rgba(125,211,252,.28) !important;
    color: #ffd95e !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    letter-spacing: .3px;
    box-shadow: 0 0 22px rgba(56,189,248,.18);
    transition: all .18s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 32px rgba(56,189,248,.30);
    border-color: rgba(125,211,252,.6) !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background: rgba(10,20,40,.92) !important;
    color: white !important;
    border: 1px solid rgba(96,165,250,.28) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 18px rgba(59,130,246,.10);
    font-weight: 600 !important;
}

textarea::placeholder,
input::placeholder {
    color: #93c5fd !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(96,165,250,.12);
    border-radius: 14px;
    margin-right: 8px;
    padding: 10px 18px;
    color: white !important;
    font-weight: 800;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1d4ed8, #38bdf8) !important;
    color: #ffe27a !important;
    box-shadow: 0 0 22px rgba(56,189,248,.24);
}

[data-testid="metric-container"] {
    background: rgba(10,20,40,.86);
    border: 1px solid rgba(96,165,250,.18);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 0 25px rgba(56,189,248,.08);
}

.stDataFrame {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(96,165,250,.16);
}

[data-testid="stChatInput"] {
    background: rgba(3,7,18,.96) !important;
    border-top: 1px solid rgba(56,189,248,.18);
}

[data-testid="stChatInput"] textarea {
    background: linear-gradient(135deg, #07152e, #0f2a52) !important;
    color: white !important;
    border: 1px solid rgba(96,165,250,.35) !important;
    border-radius: 18px !important;
}

h1, h2, h3 {
    color: #ffffff !important;
    font-weight: 900 !important;
    letter-spacing: -.5px;
}

p, span, label {
    color: #dbeafe !important;
}

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #1d4ed8, #38bdf8);
    border-radius: 999px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
        """,
        unsafe_allow_html=True,
    )
