import base64
from pathlib import Path
import streamlit as st

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

if "page" not in st.session_state:
    st.session_state.page = "home"
if "plan" not in st.session_state:
    st.session_state.plan = "free"
if "user" not in st.session_state:
    st.session_state.user = None


st.markdown("""
<style>
/* APP */
html, body, .stApp {
    background: #07070b !important;
    color: #ffffff !important;
}

/* STREAMLIT HEADER */
[data-testid="stHeader"] {
    background: #ffffff !important;
    height: 86px !important;
    border-bottom: 1px solid rgba(0,0,0,.08) !important;
}

/* HEADER LOGO */
.header-logo-fixed {
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    pointer-events: none;
}

.header-logo-fixed img {
    height: 62px;
    width: auto;
    object-fit: contain;
    border-radius: 14px;
}

/* MAIN */
.block-container {
    max-width: 1180px !important;
    padding-top: 120px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 4rem !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #050509 !important;
    border-right: 1px solid rgba(255,215,0,.22) !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] img {
    border-radius: 18px;
    margin-bottom: 1rem;
}

/* BUTTONS */
.stButton button {
    width: 100% !important;
    background: #000000 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,215,0,.55) !important;
    border-radius: 16px !important;
    min-height: 46px !important;
    font-weight: 800 !important;
}

.stButton button:hover {
    color: #ffd700 !important;
    border-color: #ffd700 !important;
    box-shadow: 0 0 18px rgba(255,215,0,.18) !important;
}

/* INPUTS */
input, textarea,
.stTextInput input,
.stTextArea textarea {
    background: #000000 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,215,0,.35) !important;
    border-radius: 14px !important;
}

input::placeholder,
textarea::placeholder {
    color: #999999 !important;
}

/* TITLES */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #ffffff;
}

/* HERO */
.hero-box {
    background:
        radial-gradient(circle at top left, rgba(0,183,255,.20), transparent 32rem),
        radial-gradient(circle at top right, rgba(168,85,247,.22), transparent 30rem),
        linear-gradient(135deg, #101827 0%, #171a2e 55%, #2d1247 100%);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 34px;
    padding: 54px 46px;
    text-align: center;
    margin: 0 auto 30px auto;
    box-shadow: 0 30px 90px rgba(0,0,0,.35);
}

.hero-box h1 {
    font-size: clamp(2.4rem, 5vw, 4.8rem);
    line-height: 1.05;
    margin: 0 0 26px 0;
    color: #ffffff !important;
    font-weight: 950;
    letter-spacing: -.04em;
}

.hero-box p {
    color: #e5e7eb !important;
    font-size: clamp(1rem, 1.7vw, 1.25rem);
    line-height: 1.7;
    margin: 0 auto 14px auto;
    max-width: 900px;
}

.hero-subtitle {
    font-size: clamp(1.25rem, 2.2vw, 1.65rem) !important;
    font-weight: 850 !important;
    color: #ffffff !important;
}

/* PLAN GRID */
.plan-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 18px;
    margin-top: 24px;
}

.plan-card {
    background: #11111a;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 24px;
    padding: 24px;
    min-height: 150px;
    box-shadow: 0 20px 50px rgba(0,0,0,.22);
}

.plan-card h3 {
    color: #ffffff !important;
    margin-top: 0;
    margin-bottom: 12px;
    font-size: 1.45rem;
}

.plan-card p {
    color: #d4d4d8 !important;
    line-height: 1.55;
}

.locked {
    opacity: .72;
    border-color: rgba(255,215,0,.25);
}

/* PREMIUM CARDS */
.premium-card {
    background: #11111a;
    border: 1px solid rgba(255,215,0,.25);
    border-radius: 24px;
    padding: 26px;
    min-height: 260px;
}

/* MOBILE */
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
        padding: 34px 22px;
        border-radius: 26px;
    }

    .plan-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)


if HEADER_B64:
    st.markdown(
        f"""
        <div class="header-logo-fixed">
            <img src="data:image/png;base64,{HEADER_B64}">
        </div>
        """,
        unsafe_allow_html=True,
    )


def plan_rank(plan: str) -> int:
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


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
        st.session_state.page = "premium" if locked else page
        st.rerun()


with st.sidebar:
    if FAVICON_PATH.exists():
        st.image(str(FAVICON_PATH), use_container_width=True)

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
    nav_button("User Dashboard", "dashboard", "free")
    nav_button("Support", "support", "free")
    nav_button("Buy Premium", "premium", "free")


if st.session_state.page == "home":
    st.markdown(
        """
        <section class="hero-box">
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
        </section>
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
            <div class="premium-card">
                <h3>Pro</h3>
                <p><b>9.99€ / Monat</b></p>
                <p>1200 Tokens</p>
                <p>Coding, Images, Musik & Reels.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buy Pro", key="buy_pro")

    with col2:
        st.markdown(
            """
            <div class="premium-card">
                <h3>Grand</h3>
                <p><b>49.99€ / Monat</b></p>
                <p>4000 Tokens</p>
                <p>AI Video Generator.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buy Grand", key="buy_grand")

    with col3:
        st.markdown(
            """
            <div class="premium-card">
                <h3>Elite</h3>
                <p><b>199€ / Monat</b></p>
                <p>Alles freigeschaltet.</p>
                <p>Höchste API-Leistung.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buy Elite", key="buy_elite")