import streamlit as st
import base64
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
BASE_DIR = Path(__file__).parent

HEADER_PATH = BASE_DIR / "header.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"


def img_to_b64(path):
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
st.markdown("""
<style>

/* =======================================================
GLOBAL
======================================================= */

html, body, .stApp {
    background: #0b0b0f !important;
    color: white !important;
}

/* =======================================================
HEADER
======================================================= */

[data-testid="stHeader"] {
    background: white !important;
    height: 82px !important;
}

/* =======================================================
HEADER LOGO
======================================================= */

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

/* =======================================================
SIDEBAR
======================================================= */

section[data-testid="stSidebar"] {
    background: #07070b !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* =======================================================
BUTTONS
======================================================= */

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

/* =======================================================
INPUTS
======================================================= */

input, textarea {
    background: #000 !important;
    color: white !important;
}

/* =======================================================
CONTAINER
======================================================= */

.block-container {
    padding-top: 105px !important;
    max-width: 1200px !important;
}

/* =======================================================
HERO
======================================================= */

.hero-box {
    background: linear-gradient(135deg,#101827,#1e293b);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 28px;
    padding: 50px;
    text-align: center;
    margin-bottom: 30px;
}

.hero-box h1 {
    font-size: 4rem;
    margin-bottom: 20px;
}

.hero-box p {
    color: #d4d4d8;
    font-size: 1.1rem;
}

/* =======================================================
CARDS
======================================================= */

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
}

.plan-card h3 {
    margin-bottom: 15px;
}

.locked {
    opacity: .55;
}

@media(max-width:900px) {
    .plan-grid {
        grid-template-columns: 1fr;
    }

    .hero-box h1 {
        font-size: 2.4rem;
    }
}

</style>
""", unsafe_allow_html=True)

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
# NAVIGATION BUTTON
# =========================================================
def nav_button(label, page, required_plan="free"):

    ranks = {
        "free": 1,
        "pro": 2,
        "grand": 3,
        "elite": 4
    }

    current_rank = ranks.get(st.session_state.plan, 1)
    needed_rank = ranks.get(required_plan, 1)

    locked = current_rank < needed_rank

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
        st.image(str(FAVICON_PATH), width=100)

    st.markdown("## MAB.AI")

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
# HOME
# =========================================================
if st.session_state.page == "home":

    st.markdown("""
    <div class="hero-box">
        <h1>Hallo willkommen auf MAB.AI</h1>

        <p>
        Was können wir für dich tun?<br><br>

        Starte mit Memory Chat, erstelle Texte, plane Projekte,
        sammle Ideen oder lass dir direkt helfen.<br><br>

        Egal ob Programmierung, Monetarisierung oder künstliche
        Intelligenz — in jedem Bereich können wir dir helfen.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="plan-grid">

        <div class="plan-card">
            <h3>Free</h3>
            <p>Memory Chat inklusive.</p>
        </div>

        <div class="plan-card locked">
            <h3>🔒 Pro</h3>
            <p>1200 Tokens<br>
            Coding, Images, Musik & Reels.</p>
        </div>

        <div class="plan-card locked">
            <h3>🔒 Grand</h3>
            <p>4000 Tokens<br>
            AI Video Generator.</p>
        </div>

        <div class="plan-card locked">
            <h3>🔒 Elite</h3>
            <p>Alles freigeschaltet.<br>
            Höchste API Leistung.</p>
        </div>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# CHAT
# =========================================================
elif st.session_state.page == "chat":

    st.title("💬 Memory Chat")

    user_input = st.text_area("Nachricht")

    if st.button("Senden"):
        st.success("Chat API kommt hier rein.")

# =========================================================
# CODING
# =========================================================
elif st.session_state.page == "coding":

    st.title("💻 Coding Area")

    code_input = st.text_area("Was soll gebaut werden?")

    if st.button("Run Coding Assistant"):
        st.success("Coding API kommt hier rein.")

# =========================================================
# IMAGE
# =========================================================
elif st.session_state.page == "image":

    st.title("🎨 Image Generator")

    prompt = st.text_area("Bildbeschreibung")

    if st.button("Generate Image"):
        st.success("OpenAI Image API kommt hier rein.")

# =========================================================
# MUSIC
# =========================================================
elif st.session_state.page == "music":

    st.title("🎵 Music Generator")

    prompt = st.text_area("Musikbeschreibung")

    if st.button("Generate Music"):
        st.success("Music API kommt hier rein.")

# =========================================================
# REELS
# =========================================================
elif st.session_state.page == "reels":

    st.title("🎞️ Short Reels Creator")

    prompt = st.text_area("Reel Beschreibung")

    if st.button("Generate Reel"):
        st.success("Reels API kommt hier rein.")

# =========================================================
# VIDEO
# =========================================================
elif st.session_state.page == "video":

    st.title("🎬 AI Video Generator")

    prompt = st.text_area("Videobeschreibung")

    if st.button("Generate Video"):
        st.success("Video API kommt hier rein.")

# =========================================================
# DASHBOARD
# =========================================================
elif st.session_state.page == "dashboard":

    st.title("📊 User Dashboard")

    st.info(f"Aktueller Plan: {st.session_state.plan}")

# =========================================================
# SUPPORT
# =========================================================
elif st.session_state.page == "support":

    st.title("🆘 Support")

    subject = st.text_input("Betreff")
    msg = st.text_area("Nachricht")

    if st.button("Ticket senden"):
        st.success("Support Ticket gesendet.")

# =========================================================
# PREMIUM
# =========================================================
elif st.session_state.page == "premium":

    st.title("💳 Buy Premium")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### Pro
        9.99€ / Monat

        1200 Tokens
        """)
        st.button("Buy Pro")

    with col2:
        st.markdown("""
        ### Grand
        49.99€ / Monat

        4000 Tokens
        """)
        st.button("Buy Grand")

    with col3:
        st.markdown("""
        ### Elite
        199€ / Monat

        Alles freigeschaltet
        """)
        st.button("Buy Elite")