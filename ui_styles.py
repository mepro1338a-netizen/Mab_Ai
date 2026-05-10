import streamlit as st


def load_styles():
    st.markdown(
        """
<style>

/* GLOBAL */

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.12), transparent 25%),
        radial-gradient(circle at bottom right, rgba(37,99,235,.10), transparent 30%),
        linear-gradient(145deg, #050b18 0%, #07152f 45%, #0b1d42 100%);
    color: white;
}

/* MAIN CONTENT */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(6,18,40,.98) 0%,
            rgba(10,25,55,.96) 100%
        ) !important;

    border-right: 1px solid rgba(96,165,250,.20);
    min-width: 260px !important;
    max-width: 260px !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* SIDEBAR BUTTONS */

.stSidebar .stButton button {
    width: 100%;
    border-radius: 20px;
    min-height: 54px;

    background:
        linear-gradient(
            135deg,
            rgba(14,165,233,.95),
            rgba(37,99,235,.95)
        ) !important;

    border: 1px solid rgba(125,211,252,.35) !important;

    color: white !important;
    font-size: 17px !important;
    font-weight: 900 !important;

    transition: .25s ease;
    box-shadow: 0 0 18px rgba(56,189,248,.18);
}

.stSidebar .stButton button:hover {
    transform: translateY(-3px);
    border-color: rgba(125,211,252,.75) !important;
    box-shadow: 0 0 30px rgba(56,189,248,.35);
}

/* SIDEBAR PROFILE */

.sidebar-user-card {
    background:
        linear-gradient(
            145deg,
            rgba(8,20,45,.98),
            rgba(12,35,70,.92)
        );

    border: 1px solid rgba(96,165,250,.24);

    border-radius: 26px;

    padding: 20px;

    margin-top: 18px;
    margin-bottom: 18px;

    box-shadow: 0 0 25px rgba(37,99,235,.12);
}

.sidebar-username {
    font-size: 24px;
    font-weight: 1000;
    color: white;
    margin-bottom: 12px;
}

.sidebar-userinfo {
    color: #dbeafe;
    font-size: 15px;
    line-height: 1.8;
    font-weight: 700;
}

/* HEADINGS */

h1 {
    color: white !important;
    font-weight: 1000 !important;
}

h2, h3 {
    color: white !important;
    font-weight: 900 !important;
}

/* CARDS */

.page-card {
    background:
        linear-gradient(
            145deg,
            rgba(6,18,40,.98),
            rgba(12,35,70,.90)
        );

    border: 1px solid rgba(96,165,250,.22);

    border-radius: 30px;

    padding: 28px;

    box-shadow: 0 0 34px rgba(37,99,235,.12);
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {

    background:
        linear-gradient(
            145deg,
            rgba(5,15,35,.98),
            rgba(10,25,55,.95)
        ) !important;

    color: white !important;

    border: 1px solid rgba(125,211,252,.40) !important;

    border-radius: 18px !important;

    padding: 14px 16px !important;

    transition: .2s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {

    border-color: #7dd3fc !important;

    box-shadow:
        0 0 22px rgba(56,189,248,.28) !important;
}

/* PLACEHOLDER */

input::placeholder,
textarea::placeholder {
    color: #93c5fd !important;
    opacity: .8;
}

/* BUTTONS */

.stButton button,
.stFormSubmitButton button {

    width: 100%;

    border-radius: 18px !important;

    min-height: 54px !important;

    background:
        linear-gradient(
            135deg,
            #0ea5e9,
            #2563eb
        ) !important;

    border: 1px solid rgba(125,211,252,.35) !important;

    color: white !important;

    font-size: 17px !important;

    font-weight: 900 !important;

    transition: .25s ease;

    box-shadow:
        0 0 22px rgba(56,189,248,.18);
}

.stButton button:hover,
.stFormSubmitButton button:hover {

    transform: translateY(-2px);

    border-color: rgba(125,211,252,.75) !important;

    box-shadow:
        0 0 34px rgba(56,189,248,.32);
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 14px;
}

.stTabs [data-baseweb="tab"] {

    background: transparent !important;

    color: #93c5fd !important;

    font-size: 16px !important;

    font-weight: 900 !important;

    border-radius: 14px !important;

    padding: 10px 18px !important;
}

.stTabs [aria-selected="true"] {

    background:
        linear-gradient(
            135deg,
            rgba(14,165,233,.18),
            rgba(37,99,235,.18)
        ) !important;

    color: white !important;

    border: 1px solid rgba(125,211,252,.35);
}

/* ALERTS */

.stSuccess,
.stError,
.stWarning,
.stInfo {
    border-radius: 18px !important;
}

/* HORIZONTAL LINE */

hr {
    border-color: rgba(125,211,252,.18);
}

/* SCROLLBAR */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #081120;
}

::-webkit-scrollbar-thumb {
    background: #1d4ed8;
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: #38bdf8;
}

</style>
        """,
        unsafe_allow_html=True,
    )

import streamlit as st

def load_css():
    st.markdown(
        f"""
        <style>
        {GLOBAL_CSS}
        </style>
        """,
        unsafe_allow_html=True,
    )