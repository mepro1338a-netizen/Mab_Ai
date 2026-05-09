import streamlit as st


def load_css():
    st.markdown(
        """
<style>
html, body, .stApp {
    background:
        radial-gradient(circle at top left, rgba(0,183,255,.10), transparent 28rem),
        radial-gradient(circle at top right, rgba(168,85,247,.10), transparent 28rem),
        #05050a !important;
    color: #ffffff !important;
}

[data-testid="stHeader"] {
    background: rgba(5,5,10,.85) !important;
    backdrop-filter: blur(18px);
}

.block-container {
    max-width: 1440px !important;
    padding-top: 95px !important;
    padding-bottom: 80px !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080812, #030305) !important;
    border-right: 1px solid rgba(255,215,0,.16);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    min-height: 48px !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #0f0f18, #050509) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,215,0,.35) !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    letter-spacing: .2px !important;
    transition: all .2s ease-in-out !important;
}

.stButton button:hover {
    transform: translateY(-1px);
    background: rgba(255,215,0,.08) !important;
    border-color: #ffd700 !important;
    box-shadow: 0 0 24px rgba(255,215,0,.16) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background: #090912 !important;
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,.10) !important;
}

.page-card {
    background:
        linear-gradient(180deg, rgba(255,255,255,.055), rgba(255,255,255,.025));
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 24px;
    box-shadow: 0 24px 70px rgba(0,0,0,.28);
}

.sidebar-card {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,215,0,.18);
    border-radius: 22px;
    padding: 18px;
    margin: 14px 0 18px 0;
}

.hero-box {
    background:
        radial-gradient(circle at top left, rgba(0,183,255,.35), transparent 34rem),
        radial-gradient(circle at top right, rgba(168,85,247,.32), transparent 34rem),
        linear-gradient(135deg, #10253c 0%, #171e36 55%, #42206a 100%);
    border-radius: 44px;
    padding: 84px 64px;
    text-align: center;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 35px 100px rgba(0,0,0,.42);
    margin-bottom: 34px;
}

.hero-title {
    font-size: clamp(44px, 6vw, 88px);
    line-height: 1.05;
    font-weight: 950;
    letter-spacing: -4px;
    color: white !important;
}

.hero-subtitle {
    max-width: 980px;
    margin: 24px auto 0 auto;
    font-size: 24px;
    line-height: 1.65;
    color: #e5e7eb !important;
}

.metric-card {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 24px;
    padding: 24px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,215,0,.12);
    border: 1px solid rgba(255,215,0,.35);
    color: #ffd700;
    font-weight: 900;
    margin-bottom: 14px;
}

.result-box {
    background: rgba(8,8,18,.92);
    border: 1px solid rgba(0,183,255,.22);
    border-radius: 26px;
    padding: 26px;
    margin-top: 24px;
}

.stChatInputContainer {
    background: #05050a !important;
}

.stChatInputContainer textarea {
    background: #0b0b12 !important;
    color: white !important;
    border: 1px solid rgba(255,215,0,.28) !important;
    border-radius: 18px !important;
}

[data-testid="stChatMessage"] {
    background: rgba(11,11,18,.92) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 20px !important;
    padding: 16px !important;
    margin-bottom: 14px !important;
}

[data-testid="stChatMessage"] * {
    color: white !important;
}

@media(max-width: 900px) {
    .block-container {
        padding-top: 80px !important;
    }

    .hero-box {
        padding: 42px 24px;
        border-radius: 30px;
    }

    .hero-title {
        font-size: 42px;
        letter-spacing: -2px;
    }

    .hero-subtitle {
        font-size: 18px;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )