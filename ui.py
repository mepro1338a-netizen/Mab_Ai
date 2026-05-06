import streamlit as st
import base64
import os
import random
from pathlib import Path

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="MAB.AI",
    page_icon="Logo24mp.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# IMAGE HELPERS
# =========================

def image_to_base64(path):
    try:
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except:
        return ""

BASE_DIR = Path(".")

LOGO_B64 = image_to_base64(BASE_DIR / "logo.png")
HEADER_B64 = image_to_base64(BASE_DIR / "neuerheader.png")
ICON_B64 = image_to_base64(BASE_DIR / "Logo24mp.png")

# =========================
# SESSION STATE
# =========================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "plan" not in st.session_state:
    st.session_state.plan = "free"

# =========================
# CSS
# =========================

st.markdown("""
<style>

html, body, [class*="css"] {
    background: #000814 !important;
    color: white !important;
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 0rem !important;
    max-width: 100% !important;
}

/* HEADER */

.top-header {
    width: 100%;
    background: #000000;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 18px 0;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 30px;
}

.top-header img {
    height: 72px;
    width: auto;
    object-fit: contain;
}

/* HERO */

.hero-box {
    width: 92%;
    margin: auto;
    border-radius: 34px;
    padding: 70px 50px;
    background: linear-gradient(
        135deg,
        #113a58 0%,
        #1a2248 48%,
        #47236e 100%
    );
    box-shadow: 0 20px 60px rgba(0,0,0,.45);
    text-align: center;
}

.hero-title {
    font-size: 76px;
    font-weight: 900;
    line-height: 1.1;
    color: white;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 33px;
    font-weight: 700;
    color: white;
    margin-bottom: 28px;
}

.hero-text {
    color: rgba(255,255,255,.92);
    font-size: 24px;
    line-height: 1.8;
    margin-bottom: 18px;
}

/* PLAN GRID */

.plan-grid {
    width: 92%;
    margin: 45px auto 70px auto;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 28px;
}

.plan-card {
    background: linear-gradient(
        180deg,
        rgba(17,17,35,.95),
        rgba(8,8,18,.98)
    );
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 28px;
    padding: 34px;
    min-height: 270px;
    transition: .25s ease;
}

.plan-card:hover {
    transform: translateY(-4px);
    border: 1px solid #6d42ff;
    box-shadow: 0 15px 35px rgba(109,66,255,.25);
}

.plan-card h3 {
    color: white;
    font-size: 54px;
    margin-bottom: 25px;
    font-weight: 800;
}

.plan-card p {
    color: rgba(255,255,255,.82);
    font-size: 28px;
    line-height: 1.7;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #050510 !important;
    border-right: 1px solid rgba(255,255,255,.06);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton > button {
    width: 100%;
    background: #090914 !important;
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    padding: 14px 18px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    transition: .2s ease;
}

.stButton > button:hover {
    border: 1px solid #6d42ff !important;
    background: #121225 !important;
}

/* LOGIN */

.login-box {
    width: 500px;
    margin: auto;
    margin-top: 80px;
    background: #090914;
    border-radius: 24px;
    padding: 40px;
    border: 1px solid rgba(255,255,255,.08);
}

.login-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 30px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown(f"""
<div class="top-header">
    <img src="data:image/png;base64,{HEADER_B64}">
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.markdown("## Navigation")

    if st.button("🏠 Home", key="nav_home"):
        st.session_state.page = "home"

    if st.button("💬 Memory Chat", key="nav_chat"):
        st.session_state.page = "chat"

    if st.button("🖼️ Image Generator", key="nav_img"):
        st.session_state.page = "img"

    if st.button("🎵 Music Generator", key="nav_music"):
        st.session_state.page = "music"

    if st.button("🎬 Short Reels Creator", key="nav_reels"):
        st.session_state.page = "reels"

    if st.button("👤 Login / Register", key="nav_login"):
        st.session_state.page = "login"

# =========================
# HOME PAGE
# =========================

if st.session_state.page == "home":

    logo_html = "MAB.AI"

    if LOGO_B64:
        logo_html = f'''
        <img src="data:image/png;base64,{LOGO_B64}" 
        style="
            height:90px;
            width:auto;
            object-fit:contain;
            border-radius:18px;
            background:#000;
            padding:8px 18px;
            box-shadow:0 10px 35px rgba(0,0,0,.45);
        ">
        '''

    st.markdown(f"""
    <div class="hero-box">

        <div class="hero-title">
            Hallo willkommen auf
        </div>

        <div style="
            display:flex;
            justify-content:center;
            margin-top:22px;
            margin-bottom:34px;
        ">
            {logo_html}
        </div>

        <div class="hero-subtitle">
            Die neue AI für die Revolution von Social Media,
            Business Bereiche uvm.
        </div>

        <div class="hero-text">
            Starte mit Memory Chat, erstelle Texte,
            plane Projekte, sammle Ideen oder lass dir direkt helfen.
        </div>

        <div class="hero-text">
            Egal ob Programmierung, Monetarisierung oder künstliche
            Intelligenz — in jedem Bereich können wir dir helfen.
        </div>

    </div>

    <div class="plan-grid">

        <div class="plan-card">
            <h3>Free</h3>
            <p>
                Memory Chat inklusive.
            </p>
        </div>

        <div class="plan-card">
            <h3>🔒 Pro</h3>
            <p>
                1200 Tokens<br>
                Coding, Images, Musik & Reels.
            </p>
        </div>

        <div class="plan-card">
            <h3>🔒 Grand</h3>
            <p>
                4000 Tokens<br>
                AI Video Generator.
            </p>
        </div>

        <div class="plan-card">
            <h3>🔒 Elite</h3>
            <p>
                Alles freigeschaltet.<br>
                Höchste API-Leistung.
            </p>
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN PAGE
# =========================

elif st.session_state.page == "login":

    if "captcha_a" not in st.session_state:
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        st.session_state.captcha_a = a
        st.session_state.captcha_b = b

    st.markdown("""
    <div class="login-box">
        <div class="login-title">
            Login / Register
        </div>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("E-Mail")
    password = st.text_input("Passwort", type="password")

    answer = st.text_input(
        f"Wieviel ist {st.session_state.captcha_a} + {st.session_state.captcha_b} ?"
    )

    if st.button("Einloggen / Registrieren"):

        try:
            if int(answer) == (
                st.session_state.captcha_a +
                st.session_state.captcha_b
            ):
                st.success("Erfolgreich eingeloggt.")
                st.session_state.logged_in = True
            else:
                st.error("Falsche Sicherheitsantwort.")
        except:
            st.error("Bitte richtige Zahl eingeben.")

# =========================
# OTHER PAGES
# =========================

elif st.session_state.page == "chat":
    st.title("💬 Memory Chat")

elif st.session_state.page == "img":
    st.title("🖼️ Image Generator")

elif st.session_state.page == "music":
    st.title("🎵 Music Generator")

elif st.session_state.page == "reels":
    st.title("🎬 Short Reels Creator")