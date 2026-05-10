import streamlit as st


GLOBAL_CSS = """
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top, rgba(56,189,248,0.10), transparent 30%),
        linear-gradient(135deg, #050b18 0%, #08172e 45%, #0b1f3a 100%);
    color: white;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
    background:
        radial-gradient(circle at top, rgba(30,64,175,.22), transparent 32%),
        linear-gradient(180deg, #071225 0%, #0b1f3f 60%, #050b18 100%) !important;
    border-right: 1px solid rgba(245, 196, 81, .25);
}

section[data-testid="stSidebar"] > div {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
    padding-top: 18px;
}

button[kind="header"],
[data-testid="collapsedControl"] {
    display: none !important;
}

.sidebar-subtitle {
    color: #f5c451;
    font-size: 15px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 24px;
    font-weight: 900;
}

.sidebar-section {
    color: #f5c451;
    font-size: 14px;
    font-weight: 1000;
    margin-top: 26px;
    margin-bottom: 10px;
    letter-spacing: .6px;
    text-transform: uppercase;
}

.sidebar-user-card {
    background:
        linear-gradient(145deg, rgba(5,15,35,.98), rgba(10,31,63,.94));
    border: 1px solid rgba(245,196,81,.30);
    border-radius: 26px;
    padding: 20px;
    margin-top: 20px;
    margin-bottom: 24px;
    box-shadow:
        0 0 26px rgba(245,196,81,.10),
        inset 0 0 18px rgba(56,189,248,.05);
}

.sidebar-user-name {
    font-size: 23px;
    font-weight: 1000;
    color: #f5c451;
    margin-bottom: 16px;
}

.sidebar-line {
    color: #f8e7b0;
    font-size: 15px;
    margin-bottom: 12px;
    font-weight: 800;
}

/* BUTTONS DARK BLUE + GOLD TEXT */

.stButton > button {
    width: 100%;
    border-radius: 18px !important;
    padding: 15px 18px !important;
    border: 1px solid rgba(245,196,81,.35) !important;
    background:
        linear-gradient(135deg, #0a2a5e 0%, #0d3b7a 55%, #071a3a 100%) !important;
    color: #f5c451 !important;
    font-weight: 1000 !important;
    font-size: 16px !important;
    transition: .25s ease;
    box-shadow:
        0 0 20px rgba(13,59,122,.45),
        inset 0 0 14px rgba(56,189,248,.08);
    margin-bottom: 12px !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    color: #ffe9a3 !important;
    border-color: rgba(255,220,120,.65) !important;
    box-shadow:
        0 0 30px rgba(245,196,81,.22),
        0 0 28px rgba(56,189,248,.20);
}

/* MAIN */

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1500px;
}

h1 {
    color: white !important;
    font-size: 62px !important;
    font-weight: 1000 !important;
    letter-spacing: -.03em;
}

h2 {
    color: white !important;
    font-size: 36px !important;
    font-weight: 900 !important;
}

h3 {
    color: #e0f2fe !important;
    font-weight: 900 !important;
}

/* PAGE CARDS */

.page-card {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.12), transparent 35%),
        linear-gradient(145deg, rgba(8,20,45,.96), rgba(13,45,90,.88));
    border-radius: 30px;
    padding: 34px;
    border: 1px solid rgba(245,196,81,.18);
    box-shadow: 0 0 40px rgba(56,189,248,.10);
    margin-bottom: 30px;
}

/* INPUTS */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(5,12,28,.96) !important;
    color: white !important;
    border-radius: 18px !important;
    border: 1px solid rgba(245,196,81,.25) !important;
    padding: 14px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid #f5c451 !important;
    box-shadow: 0 0 18px rgba(245,196,81,.30) !important;
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(5,14,32,.88);
    border-radius: 16px;
    padding: 12px 24px;
    color: #cbd5e1;
    font-weight: 900;
}

.stTabs [aria-selected="true"] {
    background:
        linear-gradient(135deg, #0a2a5e, #0d3b7a) !important;
    color: #f5c451 !important;
    border: 1px solid rgba(245,196,81,.35);
    box-shadow: 0 0 22px rgba(245,196,81,.16);
}

/* AUTH */

.auth-shell {
    max-width: 780px;
    margin: 0 auto 28px auto;
    text-align: center;
}

.auth-badge {
    display: inline-block;
    padding: 10px 22px;
    border-radius: 999px;
    background: rgba(245,196,81,.12);
    border: 1px solid rgba(245,196,81,.35);
    color: #f5c451;
    font-size: 14px;
    font-weight: 1000;
    letter-spacing: 1px;
    margin-bottom: 18px;
}

.auth-title {
    color: white;
    font-size: 62px;
    font-weight: 1000;
    line-height: 1.05;
}

.auth-subtitle {
    color: #dbeafe;
    font-size: 20px;
    font-weight: 850;
    margin-top: 14px;
}

.auth-card {
    max-width: 780px;
    margin: 0 auto;
    padding: 38px;
    border-radius: 34px;
    background:
        radial-gradient(circle at top, rgba(245,196,81,.10), transparent 35%),
        linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.90));
    border: 1px solid rgba(245,196,81,.28);
    box-shadow:
        0 0 42px rgba(56,189,248,.12),
        0 0 32px rgba(245,196,81,.08);
}

/* ADMIN */

.admin-stat-card {
    background:
        linear-gradient(145deg, rgba(8,20,45,.96), rgba(13,45,90,.88));
    border-radius: 24px;
    padding: 24px;
    border: 1px solid rgba(245,196,81,.20);
    box-shadow: 0 0 24px rgba(56,189,248,.08);
}

.admin-stat-title {
    color: #f5c451;
    font-size: 16px;
    font-weight: 900;
    margin-bottom: 12px;
}

.admin-stat-value {
    color: white;
    font-size: 42px;
    font-weight: 1000;
}

[data-testid="stDataFrame"] {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(245,196,81,.18);
}

.stSuccess,
.stError,
.stWarning,
.stInfo {
    border-radius: 18px !important;
}

</style>
"""


def load_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)