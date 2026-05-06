import streamlit as st
import streamlit.components.v1 as components
import base64
import random
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(file).parent

LOGO_PATH = BASE_DIR / "logo.png"
HEADER_PATH = BASE_DIR / "neuerheader.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MAB.AI",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# HELPERS
# =========================================================

def image_to_base64(path):
    if path.exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return ""

LOGO_B64 = image_to_base64(LOGO_PATH)
HEADER_B64 = image_to_base64(HEADER_PATH)

# =========================================================
# SESSION
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "user" not in st.session_state:
    st.session_state.user = None

if "plan" not in st.session_state:
    st.session_state.plan = "free"

if "captcha_a" not in st.session_state:
    st.session_state.captcha_a = random.randint(1, 5)

if "captcha_b" not in st.session_state:
    st.session_state.captcha_b = random.randint(1, 5)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body, .stApp {
    background: #05050b !important;
    color: white !important;
}

[data-testid="stHeader"] {
    background: #000000 !important;
    height: 86px !important;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.block-container {
    padding-top: 120px !important;
    max-width: 1450px !important;
}

section[data-testid="stSidebar"] {
    background: #050509 !important;
    border-right: 1px solid rgba(255,215,0,0.18);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    border-radius: 16px !important;
    background: #000 !important;
    color: white !important;
    border: 1px solid rgba(255,215,0,.35) !important;
    min-height: 48px !important;
    font-weight: 700 !important;
}

.stButton button:hover {
    border-color: #ffd700 !important;
    color: #ffd700 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #000 !important;
    color: white !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,215,0,.25) !important;
}

.top-logo {
    position: fixed;
    top: 12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 99999;
}

.top-logo img {
    height: 58px;
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TOP HEADER LOGO
# =========================================================

if HEADER_B64:
    st.markdown(
        f"""
        <div class="top-logo">
            <img src="data:image/png;base64,{HEADER_B64}">
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# FUNCTIONS
# =========================================================

def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)

def plan_rank(plan):
    return {
        "free": 1,
        "pro": 2,
        "grand": 3,
        "elite": 4
    }.get(plan, 1)

def nav_button(label, page, required_plan="free"):

    locked = plan_rank(st.session_state.plan) < plan_rank(required_plan)

    display = f"🔒 {label}" if locked else label
unique_key = (
        f"{label}_{page}_{required_plan}"
        .replace(" ", "_")
        .replace("/", "_")
    )

    if st.button(display, key=unique_key, use_container_width=True):

        if locked:
            st.session_state.page = "premium"
        else:
            st.session_state.page = page

        st.rerun()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## MAB.AI")

    if st.session_state.user:

        st.success(f"👤 {st.session_state.user}")
        st.caption(f"Plan: {st.session_state.plan}")

        if st.button("Logout", key="logout_button"):
            st.session_state.user = None
            st.session_state.plan = "free"
            st.session_state.page = "home"
            st.rerun()

    else:

        if st.button("Login / Register", key="login_register_button"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown("---")

    st.markdown("### Free")
    nav_button("Memory Chat", "chat", "free")

    st.markdown("### Pro")
    nav_button("Coding Area", "coding", "pro")
    nav_button("Image Generator", "image", "pro")
    nav_button("Music Generator", "music", "pro")
    nav_button("Short Reels Creator", "reels", "pro")

    st.markdown("### Grand")
    nav_button("AI Video Generator", "video", "grand")

    st.markdown("### Account")
    nav_button("User Dashboard", "dashboard")
    nav_button("Support", "support")
    nav_button("Buy Premium", "premium")

# =========================================================
# HOME
# =========================================================

if st.session_state.page == "home":

    logo_html = ""

    if LOGO_B64:
        logo_html = f"""
        <img src="data:image/png;base64,{LOGO_B64}"
        style="
        height:85px;
        border-radius:18px;
        background:black;
        padding:8px 18px;
        ">
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>

    body {{
        margin:0;
        padding:0;
        background:transparent;
        font-family:Arial;
        color:white;
    }}

    .hero {{
        background:
        radial-gradient(circle at top left, rgba(0,183,255,.24), transparent 32rem),
        radial-gradient(circle at top right, rgba(168,85,247,.24), transparent 32rem),
        linear-gradient(135deg,#10253c 0%,#1a2142 55%,#43206b 100%);

        border-radius:42px;
        padding:80px 60px;
        text-align:center;
        border:1px solid rgba(255,255,255,.08);
        box-shadow:0 30px 90px rgba(0,0,0,.4);
    }}

    .title {{
        display:flex;
        justify-content:center;
        align-items:center;
        gap:28px;
        flex-wrap:wrap;

        font-size:82px;
        font-weight:900;
        letter-spacing:-4px;
        line-height:1.05;
    }}

    .subtitle {{
        margin-top:45px;
        font-size:36px;
        font-weight:900;
    }}

    .text {{
        margin:25px auto 0 auto;
        max-width:980px;
        font-size:24px;
        line-height:1.7;
        color:#e5e7eb;
    }}

    .plans {{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:22px;
        margin-top:36px;
    }}

    .plan {{
        background:#0f1018;
        border-radius:28px;
        padding:30px;
        min-height:170px;
        border:1px solid rgba(255,255,255,.08);
    }}

    .plan h3 {{
        font-size:34px;
        margin-bottom:20px;
    }}

    .plan p {{
        font-size:19px;
        line-height:1.6;
        color:#d4d4d8;
    }}

    @media(max-width:900px) {{

        .title {{
            font-size:44px;
            letter-spacing:-2px;
        }}

        .subtitle {{
            font-size:26px;
        }}

        .text {{
            font-size:18px;
        }}

        .plans {{
            grid-template-columns:1fr;
        }}

    }}

    </style>
    </head>

    <body>
<section class="hero">

        <div class="title">
            <span>Hallo willkommen auf</span>
            {logo_html}
        </div>

        <div class="subtitle">
            Was können wir für dich tun?
        </div>

        <div class="text">
            Starte mit Memory Chat, erstelle Texte,
            plane Projekte, sammle Ideen oder lass dir direkt helfen.
        </div>

        <div class="text">
            Egal ob Programmierung, Monetarisierung oder künstliche Intelligenz —
            in jedem Bereich können wir dir helfen.
        </div>

    </section>

    <div class="plans">

        <div class="plan">
            <h3>Free</h3>
            <p>
            Memory Chat inklusive.
            </p>
        </div>

        <div class="plan">
            <h3>🔒 Pro</h3>
            <p>
            1200 Tokens<br>
            Coding Area<br>
            Image Generator<br>
            Music Generator<br>
            Short Reels Creator
            </p>
        </div>

        <div class="plan">
            <h3>🔒 Grand</h3>
            <p>
            4000 Tokens<br>
            AI Video Generator
            </p>
        </div>

        <div class="plan">
            <h3>🔒 Elite</h3>
            <p>
            Alles freigeschaltet<br>
            Höchste API-Leistung<br>
            Beste Qualität
            </p>
        </div>

    </div>

    </body>
    </html>
    """

    components.html(html, height=980, scrolling=False)

# =========================================================
# LOGIN
# =========================================================

elif st.session_state.page == "login":

    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:

        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login", key="login_submit"):

            if user:
                st.session_state.user = user
                st.session_state.plan = "free"
                st.session_state.page = "home"
                st.success("Login erfolgreich.")
                st.rerun()

    with tab2:

        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pw = st.text_input("Password", type="password", key="reg_pw")

        result = (
            st.session_state.captcha_a +
            st.session_state.captcha_b
        )

        captcha = st.number_input(
            f"Was ist {st.session_state.captcha_a} + {st.session_state.captcha_b}?",
            min_value=0,
            max_value=10,
            step=1
        )

        if st.button("Register", key="register_submit"):

            if captcha != result:
                st.error("Captcha falsch.")
                refresh_captcha()
                st.rerun()

            if reg_user and reg_email and reg_pw:
                st.success("Account erstellt.")
                refresh_captcha()

# =========================================================
# CHAT
# =========================================================

elif st.session_state.page == "chat":

    st.title("💬 Memory Chat")

    prompt = st.text_area("Nachricht")

    if st.button("Senden", key="chat_send"):
        st.success("Chat API kommt hier rein.")

# =========================================================
# CODING
# =========================================================

elif st.session_state.page == "coding":

    st.title("💻 Coding Area")

    prompt = st.text_area("Was soll gebaut werden?")

    if st.button("Code generieren", key="code_generate"):
        st.success("Coding API kommt hier rein.")

# =========================================================
# IMAGE
# =========================================================

elif st.session_state.page == "image":

    st.title("🎨 Image Generator")

    prompt = st.text_area("Bildbeschreibung")

    if st.button("Bild generieren", key="img_generate"):
 # =========================================================
# MUSIC
# =========================================================

elif st.session_state.page == "music":

    st.title("🎵 Music Generator")

    prompt = st.text_area("Musikbeschreibung")

    if st.button("Musik generieren", key="music_generate"):
        st.success("Music API kommt hier rein.")

# =========================================================
# REELS
# =========================================================

elif st.session_state.page == "reels":

    st.title("🎞️ Short Reels Creator")

    prompt = st.text_area("Reel Beschreibung")

    if st.button("Reel erstellen", key="reel_generate"):
        st.success("Reels API kommt hier rein.")

# =========================================================
# VIDEO
# =========================================================

elif st.session_state.page == "video":

    st.title("🎬 AI Video Generator")

    prompt = st.text_area("Videobeschreibung")

    if st.button("Video generieren", key="video_generate"):
        st.success("Video API kommt hier rein.")

# =========================================================
# DASHBOARD
# =========================================================

elif st.session_state.page == "dashboard":

    st.title("📊 User Dashboard")

    st.metric("Plan", st.session_state.plan)
    st.metric("Tokens", "0")

# =========================================================
# SUPPORT
# =========================================================

elif st.session_state.page == "support":

    st.title("🆘 Support")

    subject = st.text_input("Betreff")
    msg = st.text_area("Nachricht")

    if st.button("Ticket senden", key="ticket_send"):

        if subject and msg:
            st.success("Ticket gesendet.")
        else:
            st.error("Bitte alles ausfüllen.")

# =========================================================
# PREMIUM
# =========================================================

elif st.session_state.page == "premium":

    st.title("💳 Buy Premium")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("""
### Pro
9.99€ / Monat

1200 Tokens

Coding Area  
Image Generator  
Music Generator  
Short Reels Creator
""")

        st.button("Buy Pro", key="buy_pro")

    with c2:

        st.markdown("""
### Grand
49.99€ / Monat

4000 Tokens

AI Video Generator  
Alles aus Pro enthalten
""")

        st.button("Buy Grand", key="buy_grand")

    with c3:

        st.markdown("""
### Elite
199€ / Monat

Alles freigeschaltet

Höchste API-Leistung  
Beste Qualität  
Unlimited Features
""")

        st.button("Buy Elite", key="buy_elite")