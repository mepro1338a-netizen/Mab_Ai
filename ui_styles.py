import streamlit as st


def load_css():
    st.markdown(
        """
<style>

/* =========================
   GLOBAL
========================= */

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.12), transparent 30%),
        linear-gradient(180deg, #071225 0%, #0b1830 45%, #07111f 100%);
    color: white;
}

/* =========================
   MAIN LAYOUT
========================= */

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1500px;
}

/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    min-width: 330px !important;
    max-width: 330px !important;
    width: 330px !important;

    background:
        radial-gradient(circle at top, rgba(56,189,248,.18), transparent 30%),
        linear-gradient(180deg, #071225 0%, #0d2448 55%, #071225 100%) !important;

    border-right: 1px solid rgba(125,211,252,.24);
}

[data-testid="collapsedControl"] {
    display: none !important;
}

button[kind="header"] {
    display: none !important;
}

.sidebar-logo-box {
    display: flex;
    justify-content: center;
    margin-top: 10px;
    margin-bottom: 12px;
}

.sidebar-subtitle {
    color: #bfdbfe;
    text-align: center;
    font-size: 14px;
    font-weight: 900;
    margin-bottom: 24px;
}

.sidebar-section {
    color: #7dd3fc;
    font-size: 15px;
    font-weight: 950;
    margin-top: 24px;
    margin-bottom: 12px;
    letter-spacing: .5px;
}

.sidebar-user-card {
    background:
        linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.88));

    border: 1px solid rgba(125,211,252,.28);

    border-radius: 24px;

    padding: 18px;

    margin-top: 20px;
    margin-bottom: 20px;

    box-shadow: 0 0 28px rgba(56,189,248,.16);
}

.sidebar-user-name {
    color: #7dd3fc;
    font-size: 20px;
    font-weight: 1000;
    margin-bottom: 12px;
}

.sidebar-line {
    color: #dbeafe;
    font-size: 15px;
    font-weight: 800;
    line-height: 1.8;
}

section[data-testid="stSidebar"] .stButton button {
    width: 100% !important;

    min-height: 54px !important;

    border-radius: 18px !important;

    border: 1px solid rgba(125,211,252,.34) !important;

    background:
        linear-gradient(135deg, #0f4f96, #0ea5e9) !important;

    color: white !important;

    font-size: 16px !important;

    font-weight: 900 !important;

    box-shadow: 0 0 18px rgba(56,189,248,.18) !important;

    transition: all .2s ease;
}

section[data-testid="stSidebar"] .stButton button:hover {
    transform: translateY(-2px);

    border-color: #7dd3fc !important;

    box-shadow: 0 0 30px rgba(56,189,248,.38) !important;
}

/* =========================
   HERO
========================= */

.hero-box {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.16), transparent 35%),
        linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.88));

    border: 1px solid rgba(125,211,252,.26);

    border-radius: 34px;

    padding: 40px;

    margin-bottom: 40px;

    box-shadow: 0 0 40px rgba(56,189,248,.14);
}

.hero-badge {
    display: inline-block;

    padding: 10px 18px;

    border-radius: 999px;

    background: rgba(14,165,233,.16);

    border: 1px solid rgba(125,211,252,.30);

    color: #7dd3fc;

    font-size: 14px;

    font-weight: 900;

    letter-spacing: 1px;

    margin-bottom: 20px;
}

.hero-title {
    font-size: 72px;

    line-height: 1;

    font-weight: 1000;

    color: white;

    margin-bottom: 22px;
}

.hero-text {
    color: #dbeafe;

    font-size: 24px;

    line-height: 1.6;

    font-weight: 700;

    max-width: 1000px;
}

/* =========================
   TOOL CARDS
========================= */

.tool-card {
    background:
        linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.90));

    border: 1px solid rgba(125,211,252,.22);

    border-radius: 28px;

    padding: 28px;

    min-height: 260px;

    box-shadow: 0 0 28px rgba(56,189,248,.12);

    transition: all .25s ease;
}

.tool-card:hover {
    transform: translateY(-6px);

    border-color: rgba(125,211,252,.55);

    box-shadow: 0 0 40px rgba(56,189,248,.24);
}

.tool-title {
    color: white;

    font-size: 34px;

    font-weight: 1000;

    margin-bottom: 16px;
}

.tool-text {
    color: #dbeafe;

    font-size: 18px;

    line-height: 1.7;

    font-weight: 700;
}

/* =========================
   PAGE CARD
========================= */

.page-card {
    background:
        linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.90));

    border: 1px solid rgba(125,211,252,.24);

    border-radius: 30px;

    padding: 34px;

    box-shadow: 0 0 36px rgba(56,189,248,.14);
}

/* =========================
   INPUTS
========================= */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background: rgba(8,20,45,.96) !important;

    color: white !important;

    border-radius: 16px !important;

    border: 1px solid rgba(125,211,252,.24) !important;

    font-weight: 700 !important;
}

/* =========================
   BUTTONS
========================= */

.stButton button {
    border-radius: 18px !important;

    border: 1px solid rgba(125,211,252,.30) !important;

    background:
        linear-gradient(135deg, #1d4ed8, #38bdf8) !important;

    color: white !important;

    font-weight: 900 !important;

    min-height: 52px;

    transition: all .2s ease;
}

.stButton button:hover {
    transform: translateY(-2px);

    box-shadow: 0 0 28px rgba(56,189,248,.34) !important;
}

/* =========================
   TABS
========================= */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(8,20,45,.88);

    border-radius: 16px;

    color: #cbd5e1;

    padding: 12px 22px;

    font-weight: 900;
}

.stTabs [aria-selected="true"] {
    background:
        linear-gradient(135deg, #1d4ed8, #38bdf8) !important;

    color: white !important;
}

/* =========================
   TABLES
========================= */

[data-testid="stDataFrame"] {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(125,211,252,.22);
}

/* =========================
   SCROLLBAR
========================= */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(56,189,248,.35);
    border-radius: 999px;
}

</style>
        """,
        unsafe_allow_html=True,
    )