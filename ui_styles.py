import streamlit as st


GLOBAL_CSS = """
<style>

/* =========================
   MAIN APP
========================= */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top, rgba(56,189,248,0.12), transparent 30%),
        linear-gradient(135deg, #06111f 0%, #08192d 45%, #0b2242 100%);
    color: white;
}

/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;

    background:
        linear-gradient(
            180deg,
            rgba(8,20,45,0.98),
            rgba(10,25,55,0.96)
        ) !important;

    border-right: 1px solid rgba(125,211,252,0.18);
}

section[data-testid="stSidebar"] > div {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
    padding-top: 18px;
}

button[kind="header"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

/* =========================
   SIDEBAR TEXT
========================= */

.sidebar-subtitle {
    color: #93c5fd;
    font-size: 15px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 22px;
    font-weight: 700;
}

.sidebar-section {
    color: #7dd3fc;
    font-size: 14px;
    font-weight: 900;
    margin-top: 28px;
    margin-bottom: 10px;
    letter-spacing: .5px;
    text-transform: uppercase;
}

/* =========================
   USER CARD
========================= */

.sidebar-user-card {
    background:
        linear-gradient(
            145deg,
            rgba(8,20,45,.98),
            rgba(13,45,90,.90)
        );

    border: 1px solid rgba(125,211,252,.22);

    border-radius: 28px;

    padding: 22px;

    margin-top: 22px;
    margin-bottom: 24px;

    box-shadow:
        0 0 30px rgba(56,189,248,.10),
        inset 0 0 18px rgba(56,189,248,.06);
}

.sidebar-user-name {
    font-size: 24px;
    font-weight: 1000;
    color: white;
    margin-bottom: 18px;
}

.sidebar-line {
    color: #dbeafe;
    font-size: 15px;
    margin-bottom: 12px;
    font-weight: 700;
}

/* =========================
   BUTTONS
========================= */

.stButton > button {
    width: 100%;
    border-radius: 18px !important;

    padding: 16px 18px !important;

    border: 1px solid rgba(125,211,252,.25) !important;

    background:
        linear-gradient(
            90deg,
            #38bdf8,
            #22d3ee
        ) !important;

    color: white !important;

    font-weight: 900 !important;
    font-size: 16px !important;

    transition: .25s ease;

    box-shadow:
        0 0 22px rgba(56,189,248,.22);

    margin-bottom: 12px !important;
}

.stButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 0 34px rgba(56,189,248,.40);

    border: 1px solid rgba(255,255,255,.4) !important;
}

/* =========================
   HEADINGS
========================= */

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

/* =========================
   CARDS
========================= */

.page-card {
    background:
        linear-gradient(
            145deg,
            rgba(8,20,45,.96),
            rgba(13,45,90,.88)
        );

    border-radius: 30px;

    padding: 32px;

    border: 1px solid rgba(125,211,252,.20);

    box-shadow:
        0 0 40px rgba(56,189,248,.10);

    margin-bottom: 30px;
}

/* =========================
   INPUTS
========================= */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(7,15,30,.95) !important;

    color: white !important;

    border-radius: 18px !important;

    border: 1px solid rgba(125,211,252,.18) !important;

    padding: 14px !important;

    font-size: 15px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid #38bdf8 !important;

    box-shadow:
        0 0 18px rgba(56,189,248,.35) !important;
}

/* =========================
   TABS
========================= */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(10,20,40,.85);

    border-radius: 16px;

    padding: 12px 24px;

    color: #cbd5e1;

    font-weight: 900;
}

.stTabs [aria-selected="true"] {
    background:
        linear-gradient(
            90deg,
            #38bdf8,
            #22d3ee
        ) !important;

    color: white !important;

    box-shadow:
        0 0 22px rgba(56,189,248,.30);
}

/* =========================
   TABLES / DATAFRAMES
========================= */

[data-testid="stDataFrame"] {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(125,211,252,.18);
}

/* =========================
   METRICS
========================= */

[data-testid="metric-container"] {
    background:
        linear-gradient(
            145deg,
            rgba(8,20,45,.96),
            rgba(13,45,90,.88)
        );

    border-radius: 24px;

    padding: 18px;

    border: 1px solid rgba(125,211,252,.18);

    box-shadow:
        0 0 24px rgba(56,189,248,.08);
}

/* =========================
   ALERTS
========================= */

.stSuccess,
.stError,
.stWarning,
.stInfo {
    border-radius: 18px !important;
}

/* =========================
   LOGIN PAGE
========================= */

.auth-shell {
    max-width: 760px;
    margin: 0 auto 28px auto;
    text-align: center;
}

.auth-badge {
    display: inline-block;

    padding: 10px 22px;

    border-radius: 999px;

    background: rgba(14,165,233,.16);

    border: 1px solid rgba(125,211,252,.35);

    color: #7dd3fc;

    font-size: 14px;

    font-weight: 1000;

    letter-spacing: 1px;

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
    max-width: 760px;

    margin: 0 auto;

    padding: 34px;

    border-radius: 32px;

    background:
        radial-gradient(circle at top, rgba(56,189,248,.16), transparent 35%),
        linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.90));

    border: 1px solid rgba(125,211,252,.28);

    box-shadow:
        0 0 42px rgba(56,189,248,.16);
}

/* =========================
   ADMIN
========================= */

.admin-stat-card {
    background:
        linear-gradient(
            145deg,
            rgba(8,20,45,.96),
            rgba(13,45,90,.88)
        );

    border-radius: 24px;

    padding: 24px;

    border: 1px solid rgba(125,211,252,.20);

    box-shadow:
        0 0 24px rgba(56,189,248,.10);
}

.admin-stat-title {
    color: #bfdbfe;

    font-size: 16px;

    font-weight: 800;

    margin-bottom: 12px;
}

.admin-stat-value {
    color: white;

    font-size: 42px;

    font-weight: 1000;
}

</style>
"""


def load_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)