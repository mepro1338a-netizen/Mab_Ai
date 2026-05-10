import streamlit as st


GLOBAL_CSS = """
<style>

/* =========================
   GLOBAL
========================= */

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(14,165,233,.14), transparent 32%),
        radial-gradient(circle at bottom right, rgba(15,23,42,.95), transparent 35%),
        linear-gradient(135deg, #050b16 0%, #08172d 45%, #0b2345 100%);
    color: white;
}

.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1450px !important;
}

/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;

    background:
        radial-gradient(circle at top, rgba(56,189,248,.14), transparent 32%),
        linear-gradient(180deg, #06111f 0%, #0a1c36 55%, #050b16 100%) !important;

    border-right: 1px solid rgba(212,175,55,.22);
}

section[data-testid="stSidebar"] > div {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
    padding-top: 18px !important;
}

[data-testid="collapsedControl"],
button[kind="header"] {
    display: none !important;
}

.sidebar-logo-wrap {
    display: flex;
    justify-content: center;
    margin-top: 8px;
    margin-bottom: 12px;
}

.sidebar-logo-text {
    color: #f5c84b;
    font-size: 28px;
    font-weight: 1000;
    letter-spacing: 3px;
    text-align: center;
}

.sidebar-subtitle {
    color: #f5c84b;
    text-align: center;
    font-size: 14px;
    font-weight: 900;
    margin-bottom: 24px;
}

.sidebar-section {
    color: #f5c84b;
    font-size: 14px;
    font-weight: 950;
    margin-top: 26px;
    margin-bottom: 10px;
    letter-spacing: .7px;
    text-transform: uppercase;
}

/* =========================
   SIDEBAR USER CARD
========================= */

.sidebar-user-card {
    background:
        linear-gradient(145deg, rgba(4,12,26,.96), rgba(8,28,58,.92));

    border: 1px solid rgba(245,200,75,.34);
    border-radius: 24px;

    padding: 18px;
    margin-top: 18px;
    margin-bottom: 22px;

    box-shadow:
        0 0 28px rgba(56,189,248,.12),
        inset 0 0 18px rgba(245,200,75,.04);
}

.sidebar-user-name {
    color: #f5c84b;
    font-size: 20px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.sidebar-line {
    color: #e5eefc;
    font-size: 15px;
    font-weight: 750;
    line-height: 1.8;
}

/* =========================
   BUTTONS
========================= */

.stButton > button {
    width: 100% !important;

    min-height: 52px !important;
    border-radius: 17px !important;

    background:
        linear-gradient(135deg, #09203f 0%, #0b3c72 55%, #0d5d9f 100%) !important;

    border: 1px solid rgba(245,200,75,.28) !important;

    color: #f5c84b !important;

    font-size: 16px !important;
    font-weight: 950 !important;

    box-shadow:
        0 0 18px rgba(56,189,248,.14),
        inset 0 0 14px rgba(255,255,255,.03);

    transition: all .22s ease !important;

    margin-bottom: 12px !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    color: #ffe38a !important;
    border-color: rgba(245,200,75,.60) !important;
    box-shadow:
        0 0 30px rgba(56,189,248,.28),
        0 0 18px rgba(245,200,75,.15);
}

/* =========================
   HERO / HOME
========================= */

.home-hero,
.hero-box {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.16), transparent 35%),
        linear-gradient(145deg, rgba(6,17,31,.95), rgba(10,31,60,.92));

    border: 1px solid rgba(125,211,252,.24);
    border-radius: 34px;

    padding: 42px;
    margin-bottom: 38px;

    box-shadow: 0 0 42px rgba(56,189,248,.12);
}

.hero-badge,
.home-badge {
    display: inline-block;

    padding: 10px 22px;
    border-radius: 999px;

    background: rgba(14,165,233,.16);
    border: 1px solid rgba(125,211,252,.36);

    color: #7dd3fc;
    font-size: 14px;
    font-weight: 1000;
    letter-spacing: 1px;

    margin-bottom: 22px;
}

.hero-title,
.home-title {
    color: white;
    font-size: 64px;
    font-weight: 1000;
    letter-spacing: -.03em;
    line-height: 1.05;
}

.hero-text,
.home-text {
    color: #dbeafe;
    font-size: 22px;
    line-height: 1.55;
    font-weight: 800;
    max-width: 1000px;
}

/* =========================
   CARDS
========================= */

.page-card,
.tool-card,
.admin-stat-card {
    background:
        linear-gradient(145deg, rgba(6,17,31,.96), rgba(10,31,60,.90));

    border: 1px solid rgba(125,211,252,.22);
    border-radius: 28px;

    padding: 28px;

    box-shadow: 0 0 32px rgba(56,189,248,.10);
}

.tool-card {
    min-height: 240px;
    transition: all .25s ease;
}

.tool-card:hover {
    transform: translateY(-5px);
    border-color: rgba(245,200,75,.42);
    box-shadow:
        0 0 36px rgba(56,189,248,.18),
        0 0 20px rgba(245,200,75,.08);
}

.tool-title {
    color: white;
    font-size: 32px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.tool-text {
    color: #dbeafe;
    font-size: 18px;
    font-weight: 750;
    line-height: 1.65;
}

/* =========================
   LOGIN / REGISTER
========================= */

.auth-page {
    max-width: 780px;
    margin: 0 auto 30px auto;
    text-align: center;
}

.auth-badge {
    display: inline-block;

    padding: 10px 22px;
    border-radius: 999px;

    background: rgba(14,165,233,.16);
    border: 1px solid rgba(245,200,75,.38);

    color: #f5c84b;
    font-size: 14px;
    font-weight: 1000;
    letter-spacing: 1.2px;

    margin-bottom: 18px;
}

.auth-title {
    color: white;
    font-size: 60px;
    font-weight: 1000;
    line-height: 1.05;
}

.auth-subtitle {
    color: #bfdbfe;
    font-size: 20px;
    font-weight: 800;
    margin-top: 14px;
}

.auth-card {
    max-width: 780px;
    margin: 0 auto;

    padding: 36px;
    border-radius: 32px;

    background:
        radial-gradient(circle at top, rgba(56,189,248,.14), transparent 35%),
        linear-gradient(145deg, rgba(6,17,31,.98), rgba(10,31,60,.92));

    border: 1px solid rgba(125,211,252,.25);

    box-shadow:
        0 0 44px rgba(56,189,248,.14),
        inset 0 0 22px rgba(255,255,255,.03);
}

/* =========================
   INPUTS
========================= */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: rgba(3,10,23,.94) !important;

    color: white !important;

    border-radius: 16px !important;

    border: 1px solid rgba(125,211,252,.30) !important;

    font-size: 15px !important;
    font-weight: 750 !important;

    min-height: 48px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: rgba(245,200,75,.72) !important;
    box-shadow:
        0 0 20px rgba(56,189,248,.20),
        0 0 14px rgba(245,200,75,.12) !important;
}

.stTextInput label,
.stTextArea label,
.stNumberInput label {
    color: #f5c84b !important;
    font-weight: 850 !important;
}

/* =========================
   SELECTBOX
========================= */

.stSelectbox div[data-baseweb="select"] {
    background: rgba(3,10,23,.94) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(125,211,252,.30) !important;
    color: white !important;
}

/* =========================
   TABS
========================= */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(5,15,32,.88);
    border: 1px solid rgba(125,211,252,.14);
    border-radius: 16px;

    color: #cbd5e1;

    padding: 12px 24px;
    font-weight: 950;
}

.stTabs [aria-selected="true"] {
    background:
        linear-gradient(135deg, #0b3c72, #0d5d9f) !important;

    color: #f5c84b !important;

    border-color: rgba(245,200,75,.45) !important;
    box-shadow: 0 0 22px rgba(56,189,248,.24);
}

/* =========================
   ADMIN
========================= */

.admin-title,
.admin-hero {
    color: white;
    font-size: 58px;
    font-weight: 1000;
    line-height: 1.05;
}

.admin-subtitle,
.admin-sub {
    color: #bfdbfe;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 28px;
}

.admin-section-title {
    color: white;
    font-size: 30px;
    font-weight: 1000;
    margin-bottom: 20px;
}

.admin-stat-title {
    color: #f5c84b;
    font-size: 15px;
    font-weight: 900;
    margin-bottom: 10px;
}

.admin-stat-value {
    color: white;
    font-size: 40px;
    font-weight: 1000;
}

/* =========================
   DATAFRAME
========================= */

[data-testid="stDataFrame"] {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid rgba(125,211,252,.22);
}

/* =========================
   ALERTS
========================= */

.stAlert {
    border-radius: 18px !important;
}

/* =========================
   SCROLLBAR
========================= */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(125,211,252,.34);
    border-radius: 999px;
}

</style>
"""


def load_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)