import streamlit as st


def load_css():
    st.markdown(
        """
<style>
html, body, .stApp {
    background:
        radial-gradient(circle at top left, rgba(0, 140, 255, 0.16), transparent 28rem),
        radial-gradient(circle at bottom right, rgba(80, 120, 255, 0.18), transparent 30rem),
        linear-gradient(135deg, #020617, #050816, #08152e) !important;
    color: #ffffff !important;
}

[data-testid="stHeader"] {
    background: rgba(2, 6, 23, 0.84) !important;
    backdrop-filter: blur(18px);
}

.block-container {
    max-width: 1440px !important;
    padding-top: 80px !important;
    padding-bottom: 80px !important;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #050816 0%, #091124 45%, #0c1730 100%) !important;
    border-right: 1px solid rgba(0, 140, 255, 0.18) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    min-height: 48px !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #0f1729, #14345c) !important;
    color: #ffffff !important;
    border: 1px solid rgba(80, 150, 255, 0.28) !important;
    font-weight: 850 !important;
    font-size: 15px !important;
    transition: all .2s ease-in-out !important;
    box-shadow: 0 0 18px rgba(0, 140, 255, 0.08) !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    border-color: #4ea1ff !important;
    background: linear-gradient(135deg, #13223f, #1a4f86) !important;
    box-shadow: 0 0 28px rgba(0, 140, 255, 0.32) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background: rgba(8, 14, 30, 0.95) !important;
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid rgba(100, 180, 255, 0.18) !important;
}

.page-card {
    background: rgba(8, 14, 30, 0.76);
    border: 1px solid rgba(100, 180, 255, 0.14);
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 24px;
    backdrop-filter: blur(14px);
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.32);
}

.sidebar-user {
    background: linear-gradient(180deg, rgba(15, 25, 45, 0.95), rgba(10, 16, 32, 0.95));
    border: 1px solid rgba(80, 150, 255, 0.22);
    border-radius: 18px;
    padding: 18px;
    margin-top: 20px;
    color: white;
    box-shadow: 0 0 25px rgba(0, 100, 255, 0.10);
}

.hero-box {
    text-align: center;
    padding: 40px 0;
}

.hero-title {
    font-size: 72px;
    font-weight: 900;
    color: white !important;
    margin-bottom: 10px;
    letter-spacing: -2px;
}

.hero-sub,
.hero-subtitle {
    font-size: 22px;
    color: #dbeafe !important;
}

.feature-card {
    background: rgba(8, 14, 30, 0.82);
    border: 1px solid rgba(100, 180, 255, 0.12);
    border-radius: 28px;
    padding: 34px;
    min-height: 240px;
    transition: 0.28s ease;
    margin-top: 20px;
    box-shadow: 0 20px 55px rgba(0, 0, 0, 0.24);
}

.feature-card:hover {
    border-color: rgba(96, 165, 250, 0.75);
    transform: translateY(-6px);
    box-shadow: 0 0 35px rgba(0, 140, 255, 0.18);
}

.feature-card h3 {
    font-size: 34px;
    color: white;
    margin-bottom: 20px;
}

.feature-card p {
    color: #dbeafe;
    font-size: 20px;
    line-height: 1.55;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.16);
    border: 1px solid rgba(96, 165, 250, 0.38);
    color: #93c5fd;
    font-weight: 900;
    margin-bottom: 14px;
}

.result-box {
    background: rgba(8, 14, 30, 0.92);
    border: 1px solid rgba(0, 183, 255, 0.22);
    border-radius: 26px;
    padding: 26px;
    margin-top: 24px;
}

[data-testid="stChatMessage"] {
    background: rgba(8, 14, 30, 0.88) !important;
    border: 1px solid rgba(100, 180, 255, 0.14) !important;
    border-radius: 20px !important;
    padding: 16px !important;
    margin-bottom: 14px !important;
}

[data-testid="stChatMessage"] * {
    color: white !important;
}

.mabyte-hero {
    min-height: 620px;
    border-radius: 36px;
    padding: 70px;
    display: flex;
    align-items: center;
    margin-bottom: 42px;
    border: 1px solid rgba(90, 170, 255, 0.22);
    box-shadow: 0 30px 90px rgba(0, 0, 0, 0.45);
}

.mabyte-hero-content {
    max-width: 900px;
    background: rgba(2, 6, 23, 0.62);
    border: 1px solid rgba(100, 180, 255, 0.18);
    border-radius: 30px;
    padding: 42px;
    backdrop-filter: blur(14px);
}

.mabyte-hero-content h1 {
    font-size: 58px;
    font-weight: 900;
    margin-bottom: 24px;
    color: white;
}

.mabyte-hero-content p {
    font-size: 21px;
    line-height: 1.7;
    color: #dbeafe;
}

.mabyte-hero-content .lead {
    font-size: 28px;
    font-weight: 800;
    color: white;
}

.mabyte-hero-content h3 {
    margin-top: 28px;
    margin-bottom: 18px;
    font-size: 30px;
    color: #7dd3fc;
}

.mabyte-claim {
    margin-top: 30px;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 2px;
    color: #60a5fa;
}

@media(max-width: 900px) {
    .block-container {
        padding-top: 60px !important;
    }

    .mabyte-hero {
        padding: 28px;
        min-height: auto;
        border-radius: 28px;
    }

    .mabyte-hero-content {
        padding: 28px;
    }

    .mabyte-hero-content h1 {
        font-size: 38px;
    }

    .mabyte-hero-content p {
        font-size: 17px;
    }

    .feature-card {
        min-height: auto;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )