import base64
from pathlib import Path

import streamlit as st


# =========================================================
# CONFIG
# =========================================================
BASE_DIR = Path(__file__).parent

HEADER_PATH = BASE_DIR / "header.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"


def img_to_b64(path: Path) -> str:
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


HEADER_B64 = img_to_b64(HEADER_PATH)

st.set_page_config(
    page_title="MAB.AI",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "plan" not in st.session_state:
    st.session_state.plan = "free"

if "user" not in st.session_state:
    st.session_state.user = None


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
html, body, .stApp {
    background: #0b0b0f !important;
    color: white !important;
}

/* Header */
[data-testid="stHeader"] {
    background: #ffffff !important;
    height: 82px !important;
}

/* Header logo */
.header-logo-fixed {
    position: fixed;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    pointer-events: none;
}

.header-logo-fixed img {
    height: 64px;
    width: auto;
    object-fit: contain;
    border-radius: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #07070b !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Buttons */
.stButton button {
    width: 100%;
    border-radius: 14px !important;
    border: 1px solid rgba(255,215,0,.5) !important;
    background: #000 !important;
    color: white !important;
    font-weight: 700 !important;
    min-height: 45px;
}

.stButton button:hover {
    border-color: #ffd700 !important;
}

/* Inputs */
input, textarea {
    background: #000 !important;
    color: white !important;
}

/* Main container */
.block-container {
    padding-top: 105px !important;
    max-width: 1200px !important;
}

/* Hero */
.hero-box {
    background: linear-gradient(135deg,#101827,#1e293b);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 28px;
    padding: 60px;
    text-align: center;
    margin-bottom: 30px;
}

.hero-box h1 {
    font-size: clamp(2.6rem, 6vw, 4.5rem);
    margin-bottom: 28px;
    color: white !important;
    font-weight: 900;
}

.hero-box p {
    color: #e5e7eb !important;
    font-size: 1.25rem;
    line-height: 1.7;
}

.hero-subtitle {
    font-size: 1.6rem !important;
    font-weight: 700;
}

/* Plans */
.plan-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 20px;
}

.plan-card {
    background: #11111a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 25px;
    min-height: 160px;
}

.plan-card h3 {
    margin-bottom: 15px;
    color: white !important;
}

.plan-card p {
    color: #d4d4d8 !important;
}

.locked {
    opacity: .6;
}

/* Mobile */
@media(max-width:900px) {
    .plan-grid {
        grid-template-columns: 1fr;
    }

    .hero-box {
        padding: 35px 22px;
    }

    .hero-box h1 {
        font-size: 2.4rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HEADER LOGO
# =========================================================
if HEADER_B64:
    st.markdown(
        f"""
        <div class="header-logo-fixed">
            <img src="data:image/png;base64,{HEADER_B64}">
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# NAVIGATION
# =========================================================
def plan_rank(plan: str) -> int:
    return {
        "free": 1,
        "pro": 2,
        "grand": 3,
        "elite": 4,
    }.get(plan, 1)


def nav_button(label: str, page: str, required_plan: str = "free"):
    locked = plan_rank(st.session_state.plan) < plan_rank(required_plan)
    text = f"🔒 {label}" if locked else label

    button_key = (
        f"nav_{page}_{required_plan}_{label}"
        .replace(" ", "_")
        .replace("/", "_")
        .replace("🔒", "")
    )

    if st.button(text, use_container_width=True, key=button_key):
        if locked:
            st.session_state.page = "premium"
        else:
            st.session_state.page = page


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if FAVICON_PATH.exists():
        st.image(str(FAVICON_PATH), width=110)

    st.markdown("## MAB.AI")

    if st.session_state.user:
        st.success(f"👤 {st.session_state.user}")
        st.caption(f"Plan: {st.session_state.plan}")
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.session_state.plan = "free"
            st.session_state.page = "home"
            st.rerun()
    else:
        if st.button("Login / Register", use_container_width=True, key="login_register_btn"):
            st.session_state.page = "login"

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
    nav_button("User Dashboard", "dashboard", "free")
    nav_button("Support", "support", "free")
    nav_button("Buy Premium", "premium", "free")


# =========================================================
# PAGES
# =========================================================
if st.session_state.page == "home":
    st.markdown(
        """
        <div class="hero-box">
            <h1>Hallo willkommen auf MAB.AI</h1>
            <p class="hero-subtitle">Was können wir für dich tun?</p>
            <p>
                Starte mit Memory Chat, erstelle Texte, plane Projekte,
                sammle Ideen oder lass dir direkt helfen.
            </p>
            <p>
                Egal ob Programmierung, Monetarisierung oder künstliche Intelligenz —
                in jedem Bereich können wir dir helfen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="plan-grid">
            <div class="plan-card">
                <h3>Free</h3>
                <p>Memory Chat inklusive.</p>
            </div>

            <div class="plan-card locked">
                <h3>🔒 Pro</h3>
                <p>1200 Tokens<br>Coding, Images, Musik & Reels.</p>
            </div>

            <div class="plan-card locked">
                <h3>🔒 Grand</h3>
                <p>4000 Tokens<br>AI Video Generator.</p>
            </div>

            <div class="plan-card locked">
                <h3>🔒 Elite</h3>
                <p>Alles freigeschaltet.<br>Höchste API-Leistung.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


elif st.session_state.page == "login":
    st.title("🔐 Login / Register")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_submit"):
            if username:
                st.session_state.user = username
                st.session_state.plan = "free"
                st.session_state.page = "home"
                st.success("Login erfolgreich.")
                st.rerun()
            else:
                st.error("Bitte Username eingeben.")

    with tab_register:
        new_username = st.text_input("Username", key="register_username")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")

        if st.button("Register", key="register_submit"):
            if new_username and new_email and new_password:
                st.success("Account erstellt. Du kannst dich jetzt einloggen.")
            else:
                st.error("Bitte alle Felder ausfüllen.")


elif st.session_state.page == "chat":
    st.title("💬 Memory Chat")

    user_input = st.text_area("Nachricht", key="chat_input")

    if st.button("Senden", key="chat_send"):
        st.success("Chat API kommt hier rein.")


elif st.session_state.page == "coding":
    st.title("💻 Coding Area")

    code_input = st.text_area("Was soll gebaut oder gefixt werden?", key="coding_input")

    if st.button("Run Coding Assistant", key="coding_run"):
        st.success("Coding API kommt hier rein.")


elif st.session_state.page == "image":
    st.title("🎨 Image Generator")

    prompt = st.text_area("Bildbeschreibung", key="image_prompt")

    if st.button("Generate Image", key="image_generate"):
        st.success("OpenAI Image API kommt hier rein.")


elif st.session_state.page == "music":
    st.title("🎵 Music Generator")

    prompt = st.text_area("Musikbeschreibung", key="music_prompt")

    if st.button("Generate Music", key="music_generate"):
        st.success("Music API kommt hier rein.")


elif st.session_state.page == "reels":
    st.title("🎞️ Short Reels Creator")

    prompt = st.text_area("Reel Beschreibung", key="reels_prompt")

    if st.button("Generate Reel", key="reels_generate"):
        st.success("Reels API kommt hier rein.")


elif st.session_state.page == "video":
    st.title("🎬 AI Video Generator")

    prompt = st.text_area("Videobeschreibung", key="video_prompt")

    if st.button("Generate Video", key="video_generate"):
        st.success("Video API kommt hier rein.")


elif st.session_state.page == "dashboard":
    st.title("📊 User Dashboard")

    st.metric("Aktueller Plan", st.session_state.plan)
    st.metric("Tokens", "0")
    st.info("Redeem Codes und Billing kommen hier rein.")


elif st.session_state.page == "support":
    st.title("🆘 Support")

    subject = st.text_input("Betreff", key="support_subject")
    msg = st.text_area("Nachricht", key="support_msg")

    if st.button("Ticket senden", key="support_send"):
        if subject and msg:
            st.success("Support Ticket gesendet.")
        else:
            st.error("Bitte Betreff und Nachricht ausfüllen.")


elif st.session_state.page == "premium":
    st.title("💳 Buy Premium")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### Pro
            **9.99€ / Monat**

            1200 Tokens  
            Coding, Images, Musik & Reels.
            """
        )
        st.button("Buy Pro", key="buy_pro")

    with col2:
        st.markdown(
            """
            ### Grand
            **49.99€ / Monat**

            4000 Tokens  
            AI Video Generator.
            """
        )
        st.button("Buy Grand", key="buy_grand")

    with col3:
        st.markdown(
            """
            ### Elite
            **199€ / Monat**

            Alles freigeschaltet.  
            Höchste API-Leistung.
            """
        )
        st.button("Buy Elite", key="buy_elite")