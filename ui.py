import base64
import random
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).parent

HEADER_PATH = BASE_DIR / "neuerheader.png"
LOGO_PATH = BASE_DIR / "logo.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"


def image_to_base64(path: Path) -> str:
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


HEADER_B64 = image_to_base64(HEADER_PATH)
LOGO_B64 = image_to_base64(LOGO_PATH)

st.set_page_config(
    page_title="MAB.AI",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "plan" not in st.session_state:
    st.session_state.plan = "free"
if "user" not in st.session_state:
    st.session_state.user = None
if "captcha_a" not in st.session_state:
    st.session_state.captcha_a = random.randint(1, 5)
if "captcha_b" not in st.session_state:
    st.session_state.captcha_b = random.randint(1, 5)


def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


st.markdown(
    """
<style>
html, body, .stApp {
    background: #05050a !important;
    color: white !important;
}

[data-testid="stHeader"] {
    background: #000000 !important;
    height: 86px !important;
    border-bottom: 1px solid rgba(255,255,255,.08);
}

.header-logo-fixed {
    position: fixed;
    top: 11px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    pointer-events: none;
}

.header-logo-fixed img {
    height: 60px;
    width: auto;
    object-fit: contain;
}

.block-container {
    max-width: 1400px !important;
    padding-top: 120px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 80px !important;
}

section[data-testid="stSidebar"] {
    background: #050509 !important;
    border-right: 1px solid rgba(255,215,0,.20);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    background: #000 !important;
    color: white !important;
    border: 1px solid rgba(255,215,0,.45) !important;
    border-radius: 16px !important;
    min-height: 48px !important;
    font-weight: 800 !important;
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
    border: 1px solid rgba(255,215,0,.30) !important;
}

.hero-box {
    background:
        radial-gradient(circle at top left, rgba(0,183,255,.25), transparent 35rem),
        radial-gradient(circle at top right, rgba(168,85,247,.25), transparent 35rem),
        linear-gradient(135deg, #10253c 0%, #171e36 55%, #42206a 100%);
    border-radius: 42px;
    padding: 80px 60px;
    text-align: center;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 30px 90px rgba(0,0,0,.45);
    margin-bottom: 34px;
}

.hero-title {
    font-size: clamp(46px, 5.5vw, 90px);
    line-height: 1.08;
    font-weight: 950;
    letter-spacing: -4px;
    color: white !important;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    flex-wrap: wrap;
}

.hero-title img {
    height: 82px;
    width: auto;
    object-fit: contain;
    border-radius: 16px;
    background: #000;
    padding: 6px 14px;
}

.hero-subtitle {
    margin-top: 52px;
    font-size: 34px;
    font-weight: 900;
    color: white !important;
}

.hero-text {
    margin: 26px auto 0 auto;
    max-width: 1000px;
    font-size: 24px;
    line-height: 1.65;
    color: #e5e7eb !important;
    text-align: center;
}

.plan-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin-top: 34px;
    margin-bottom: 80px;
}

.plan-card {
    background: #101018;
    border-radius: 26px;
    padding: 32px;
    min-height: 190px;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 24px 70px rgba(0,0,0,.30);
}

.plan-card h3 {
    font-size: 36px;
    margin: 0 0 20px 0;
    color: white !important;
}

.plan-card p {
    font-size: 19px;
    line-height: 1.6;
    color: #d4d4d8 !important;
}

.locked {
    opacity: .82;
}

@media(max-width: 900px) {
    .block-container {
        padding-top: 105px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .header-logo-fixed img {
        height: 52px;
    }

    .hero-box {
        padding: 42px 24px;
        border-radius: 30px;
    }

    .hero-title {
        font-size: 42px;
        letter-spacing: -2px;
    }

    .hero-title img {
        height: 58px;
    }

    .hero-subtitle {
        font-size: 24px;
    }

    .hero-text {
        font-size: 18px;
    }

    .plan-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

if HEADER_B64:
    st.markdown(
        f"""
        <div class="header-logo-fixed">
            <img src="data:image/png;base64,{HEADER_B64}">
        </div>
        """,
        unsafe_allow_html=True,
    )


def plan_rank(plan):
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


def nav_button(label, page, required_plan="free"):
    locked = plan_rank(st.session_state.plan) < plan_rank(required_plan)
    text = f"🔒 {label}" if locked else label

    button_key = (
        f"nav_{page}_{required_plan}_{label}"
        .replace(" ", "_")
        .replace("/", "_")
        .replace("🔒", "")
    )

    if st.button(text, use_container_width=True, key=button_key):
        st.session_state.page = "premium" if locked else page
        st.rerun()


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## MAB.AI")

    if st.session_state.user:
        st.success(f"👤 {st.session_state.user}")
        st.caption(f"Plan: {st.session_state.plan}")

        if st.button("Logout", key="logout_btn"):
            st.session_state.user = None
            st.session_state.plan = "free"
            st.session_state.page = "home"
            st.rerun()
    else:
        if st.button("Login / Register", key="login_register_btn"):
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


if st.session_state.page == "home":
    logo_html = "MAB.AI"
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}">'

    st.markdown(
        f"""
        <section class="hero-box">
            <div class="hero-title">
                <span>Hallo willkommen auf</span>
                {logo_html}
            </div>

            <div class="hero-subtitle">
                Was können wir für dich tun?
            </div>

            <div class="hero-text">
                Starte mit Memory Chat, erstelle Texte, plane Projekte,
                sammle Ideen oder lass dir direkt helfen.
            </div>

            <div class="hero-text">
                Egal ob Programmierung, Monetarisierung oder künstliche Intelligenz —
                in jedem Bereich können wir dir helfen.
            </div>
        </section>

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

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            if username:
                st.session_state.user = username
                st.session_state.plan = "free"
                st.session_state.page = "home"
                st.success("Login erfolgreich.")
                st.rerun()
            else:
                st.error("Bitte Username eingeben.")

    with tab2:
        reg_user = st.text_input("Username", key="register_user")
        reg_mail = st.text_input("Email", key="register_mail")
        reg_pw = st.text_input("Password", type="password", key="register_pw")

        result = st.session_state.captcha_a + st.session_state.captcha_b

        captcha = st.number_input(
            f"Was ist {st.session_state.captcha_a} + {st.session_state.captcha_b}?",
            min_value=0,
            max_value=10,
            step=1,
            key="captcha_input",
        )

        if st.button("Register", key="register_btn"):
            if captcha != result:
                st.error("Captcha falsch.")
                refresh_captcha()
                st.rerun()

            if reg_user and reg_mail and reg_pw:
                st.success("Account erfolgreich erstellt.")
                refresh_captcha()
            else:
                st.error("Bitte alles ausfüllen.")


elif st.session_state.page == "chat":
    st.title("💬 Memory Chat")
    prompt = st.text_area("Nachricht", key="chat_prompt")

    if st.button("Senden", key="chat_send"):
        st.success("Chat API kommt hier rein.")


elif st.session_state.page == "coding":
    st.title("💻 Coding Area")
    prompt = st.text_area("Was soll gebaut werden?", key="coding_prompt")

    if st.button("Code generieren", key="code_generate"):
        st.success("Coding API kommt hier rein.")


elif st.session_state.page == "image":
    st.title("🎨 Image Generator")
    prompt = st.text_area("Bildbeschreibung", key="image_prompt")

    if st.button("Bild generieren", key="img_generate"):
        st.success("OpenAI Image API kommt hier rein.")


elif st.session_state.page == "music":
    st.title("🎵 Music Generator")
    prompt = st.text_area("Musikbeschreibung", key="music_prompt")

    if st.button("Musik generieren", key="music_generate"):
        st.success("Music API kommt hier rein.")


elif st.session_state.page == "reels":
    st.title("🎞️ Short Reels Creator")
    prompt = st.text_area("Reel Beschreibung", key="reels_prompt")

    if st.button("Reel erstellen", key="reel_generate"):
        st.success("Reels API kommt hier rein.")


elif st.session_state.page == "video":
    st.title("🎬 AI Video Generator")
    prompt = st.text_area("Videobeschreibung", key="video_prompt")

    if st.button("Video generieren", key="video_generate"):
        st.success("Video API kommt hier rein.")


elif st.session_state.page == "dashboard":
    st.title("📊 User Dashboard")
    st.metric("Plan", st.session_state.plan)
    st.metric("Tokens", "0")


elif st.session_state.page == "support":
    st.title("🆘 Support")
    subject = st.text_input("Betreff", key="support_subject")
    msg = st.text_area("Nachricht", key="support_msg")

    if st.button("Ticket senden", key="ticket_send"):
        if subject and msg:
            st.success("Ticket gesendet.")
        else:
            st.error("Bitte alles ausfüllen.")


elif st.session_state.page == "premium":
    st.title("💳 Buy Premium")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### Pro\n**9.99€ / Monat**\n\n1200 Tokens")
        st.button("Buy Pro", key="buy_pro")

    with c2:
        st.markdown("### Grand\n**49.99€ / Monat**\n\n4000 Tokens")
        st.button("Buy Grand", key="buy_grand")

    with c3:
        st.markdown("### Elite\n**199€ / Monat**\n\nAlles freigeschaltet. Höchste API-Leistung.")
        st.button("Buy Elite", key="buy_elite")