import base64
import random
import textwrap
from pathlib import Path
from chat_service import generate_chat
import streamlit as st

from chat_memory import (
    init_chat_memory,
    save_chat_message,
    load_chat_history,
    clear_chat_history,
)

from session_manager import (
    init_session,
    update_activity,
    is_session_expired,
    logout as session_logout,
)

from security import (
    is_valid_username,
    is_valid_email,
    check_login_rate,
)

from config import (
    APP_NAME,
    PLANS,
    TOKEN_COSTS,
    LOGO_PATH,
    FAVICON_PATH,
    HEADER_PATH,
)

from ai_service import generate_image, generate_video, ai_health_check
from ai_pipeline import run_ai_task

from database import (
    init_db,
    create_user,
    verify_login,
    get_user,
    list_users,
    set_plan,
    update_tokens,
    set_role,
    ban_user,
    delete_user,
    create_support_message,
    list_support_messages,
    support_counts,
    set_support_status,
    delete_support_message,
    create_redeem_code,
    list_codes,
    redeem_code,
    list_usage,
    list_purchases,
    list_audit_logs,
    add_audit_log,
)

try:
    from payments import create_checkout_session
except Exception:
    create_checkout_session = None


st.set_page_config(
    page_title=APP_NAME,
    page_icon=str(FAVICON_PATH) if Path(FAVICON_PATH).exists() else "🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

if is_session_expired():
    session_logout()

update_activity()
init_db()
init_chat_memory()


def img_b64(path) -> str:
    path = Path(path)
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    return ""


def file_bytes(path):
    path = Path(path)
    if path.exists():
        return path.read_bytes()
    return None


def sync_user(username: str):
    user = get_user(username)
    if user:
        st.session_state.user = user["username"]
        st.session_state.email = user.get("email", "")
        st.session_state.plan = user["plan"]
        st.session_state.tokens = user["tokens"]
        st.session_state.role = user["role"]
        st.session_state.admin_level = user["admin_level"]


def app_logout():
    st.session_state.user = None
    st.session_state.email = ""
    st.session_state.plan = "free"
    st.session_state.tokens = 0
    st.session_state.role = "user"
    st.session_state.admin_level = 0
    st.session_state.logged_in = False
    st.session_state.page = "home"
    st.rerun()


def is_logged_in():
    return bool(st.session_state.get("user"))


def is_admin():
    return (
        st.session_state.role in ["supporter", "moderator", "admin", "owner"]
        or int(st.session_state.admin_level) > 0
    )


def is_owner():
    return st.session_state.role == "owner" or int(st.session_state.admin_level) >= 999


def plan_rank(plan):
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


def can_use(required_plan):
    return plan_rank(st.session_state.plan) >= plan_rank(required_plan) or is_admin()


def require_login():
    if not is_logged_in():
        st.warning("Bitte zuerst einloggen.")
        st.session_state.page = "login"
        st.rerun()


def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def nav_button(label, page, required_plan="free"):
    locked = is_logged_in() and not can_use(required_plan)
    text = f"🔒 {label}" if locked else label
    key = f"nav_{page}_{required_plan}_{label}".replace(" ", "_").replace("/", "_")

    if st.button(text, use_container_width=True, key=key):
        if not is_logged_in() and page not in ["home", "premium", "login"]:
            st.session_state.page = "login"
        elif locked:
            st.session_state.page = "premium"
        else:
            st.session_state.page = page
        st.rerun()


def render_file_download(path, label):
    data = file_bytes(path)
    if not data:
        st.error("Datei konnte nicht gefunden werden.")
        return

    suffix = Path(path).suffix.lower()

    if suffix in [".png", ".jpg", ".jpeg", ".webp"]:
        mime = "image/png"
    elif suffix in [".mp4", ".mov"]:
        mime = "video/mp4"
    else:
        mime = "application/octet-stream"

    st.download_button(
        label=label,
        data=data,
        file_name=Path(path).name,
        mime=mime,
        use_container_width=True,
    )


defaults = {
    "page": "home",
    "plan": "free",
    "tokens": 0,
    "user": None,
    "email": "",
    "role": "user",
    "admin_level": 0,
    "captcha_a": random.randint(1, 5),
    "captcha_b": random.randint(1, 5),
    "last_image_path": None,
    "last_video_path": None,
    "logged_in": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


HEADER_B64 = img_b64(HEADER_PATH)
LOGO_B64 = img_b64(LOGO_PATH)

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
}

.block-container {
    max-width: 1400px !important;
    padding-top: 120px !important;
    padding-bottom: 120px !important;
}

.top-logo-wrap {
    position: fixed;
    top: 12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    pointer-events: none;
}

.top-logo-wrap img {
    height: 60px;
    width: auto;
    object-fit: contain;
}

section[data-testid="stSidebar"] {
    background: #050509 !important;
    border-right: 1px solid rgba(255,215,0,.20);
    min-width: 320px !important;
    max-width: 320px !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    background: #000 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,215,0,.45) !important;
    border-radius: 16px !important;
    min-height: 48px !important;
    font-weight: 900 !important;
    font-size: 18px !important;
    letter-spacing: .2px !important;
}

.stButton button:hover {
    border-color: #ffd700 !important;
    color: #ffffff !important;
    background: rgba(255,215,0,.08) !important;
    box-shadow: 0 0 18px rgba(255,215,0,.14) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background: #000 !important;
    color: white !important;
    border-radius: 14px !important;
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
}

.hero-logo {
    margin: 28px auto 36px auto;
    display: flex;
    justify-content: center;
    align-items: center;
}

.hero-logo img {
    height: 95px;
    width: auto;
    object-fit: contain;
    border-radius: 18px;
    background: #000;
    padding: 8px 18px;
    box-shadow: 0 10px 35px rgba(0,0,0,.45);
}

.hero-subtitle {
    font-size: 34px;
    font-weight: 900;
    color: white !important;
    margin-top: 24px;
}

.hero-text {
    margin: 24px auto 0 auto;
    max-width: 1050px;
    font-size: 24px;
    line-height: 1.65;
    color: #e5e7eb !important;
    text-align: center;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin-top: 34px;
    margin-bottom: 44px;
}

.app-card {
    background: #101018;
    border-radius: 26px;
    padding: 32px;
    min-height: 210px;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 24px 70px rgba(0,0,0,.30);
}

.app-card h3 {
    font-size: 32px;
    margin: 0 0 18px 0;
    color: white !important;
}

.app-card p {
    font-size: 18px;
    line-height: 1.6;
    color: #d4d4d8 !important;
}

.page-card {
    background: #101018;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 28px;
    padding: 34px;
    box-shadow: 0 24px 70px rgba(0,0,0,.30);
    margin-bottom: 24px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,215,0,.12);
    border: 1px solid rgba(255,215,0,.35);
    color: #ffd700;
    font-weight: 800;
    margin-bottom: 16px;
}

.price-card {
    background: linear-gradient(180deg, #111127, #090914);
    border: 1px solid rgba(255,215,0,.25);
    border-radius: 30px;
    padding: 34px;
    min-height: 390px;
    box-shadow: 0 24px 70px rgba(0,0,0,.35);
}

.price-card h2 {
    color: white !important;
    font-size: 38px;
}

.price {
    font-size: 34px;
    font-weight: 950;
    color: #ffd700;
    margin: 16px 0;
}

.feature-list {
    color: #d4d4d8;
    line-height: 1.9;
    font-size: 18px;
}

.sidebar-box {
    background: #0f0f18;
    border: 1px solid rgba(255,215,0,.18);
    border-radius: 18px;
    padding: 16px;
    margin: 14px 0;
}

.result-box {
    background: #080812;
    border: 1px solid rgba(0,183,255,.25);
    border-radius: 24px;
    padding: 24px;
    margin-top: 24px;
}

@media(max-width: 900px) {
    .block-container {
        padding-top: 105px !important;
    }

    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }

    .top-logo-wrap img {
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

    .hero-logo img {
        height: 65px;
    }

    .hero-subtitle {
        font-size: 24px;
    }

    .hero-text {
        font-size: 18px;
    }

    .card-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

if HEADER_B64:
    st.markdown(
        f'<div class="top-logo-wrap"><img src="data:image/png;base64,{HEADER_B64}"></div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    if Path(LOGO_PATH).exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## MAB.AI")

    if is_logged_in():
        st.markdown(
            f"""
            <div class="sidebar-box">
                <b>👤 {st.session_state.user}</b><br>
                ⭐ Plan: {st.session_state.plan}<br>
                🪙 Tokens: {st.session_state.tokens}<br>
                🛡️ Role: {st.session_state.role}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", key="logout_btn"):
            app_logout()
    else:
        if st.button("Login / Register", key="login_register_btn"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown("---")
    nav_button("🏠 Home", "home")
    nav_button("💬 Memory Chat", "chat", "free")
    nav_button("💻 Coding Area", "coding", "pro")
    nav_button("🎨 Image Generator", "image", "pro")
    nav_button("🎵 Music Generator", "music", "pro")
    nav_button("🎞️ Short Reels Creator", "reels", "pro")
    nav_button("🎬 AI Video Generator", "video", "grand")

    st.markdown("### Account")
    nav_button("📊 User Dashboard", "dashboard")
    nav_button("🆘 Support", "support")
    nav_button("💳 Buy Premium", "premium")

    st.markdown("### Redeem Code")
    sidebar_code = st.text_input("Code eingeben", key="sidebar_redeem_code")

    if st.button("Code einlösen", key="sidebar_redeem_btn"):
        if not is_logged_in():
            st.error("Bitte zuerst einloggen.")
        elif not sidebar_code:
            st.error("Bitte Code eingeben.")
        else:
            ok, msg = redeem_code(st.session_state.user, sidebar_code)
            if ok:
                sync_user(st.session_state.user)
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    if is_admin():
        st.markdown("### Admin")
        nav_button("🛡️ Admin Panel", "admin")


page = st.session_state.page


if page == "home":
    logo_html = "MAB.AI"
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}">'

    html = f"""
<section class="hero-box">
  <div class="hero-title">Hallo willkommen auf</div>
  <div class="hero-logo">{logo_html}</div>
  <div class="hero-subtitle">
    Die neue AI für Social Media, Business, Coding und Content Creation.
  </div>
  <div class="hero-text">
    Starte mit Memory Chat, erstelle Bilder, generiere Videos,
    plane Projekte und baue digitale Workflows mit künstlicher Intelligenz.
  </div>
</section>

<div class="card-grid">
  <div class="app-card">
    <h3>Free</h3>
    <p>Memory Chat inklusive. Perfekt zum Starten, Planen und Schreiben.</p>
  </div>
  <div class="app-card">
    <h3>Pro</h3>
    <p>1200 Tokens<br>Coding, Images, Musik & Reels.</p>
  </div>
  <div class="app-card">
    <h3>Grand</h3>
    <p>4000 Tokens<br>AI Video Generator und stärkere Workflows.</p>
  </div>
  <div class="app-card">
    <h3>Elite</h3>
    <p>Alles freigeschaltet.<br>Höchste API-Leistung.</p>
  </div>
</div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


elif page == "login":
    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            allowed, rate_msg = check_login_rate(username)

            if not allowed:
                st.error(rate_msg)
            else:
                ok, msg, user = verify_login(username, password)

                if ok and user:
                    st.session_state.logged_in = True
                    st.session_state.user = user["username"]
                    st.session_state.email = user.get("email", "")
                    st.session_state.plan = user["plan"]
                    st.session_state.tokens = user["tokens"]
                    st.session_state.role = user["role"]
                    st.session_state.admin_level = user["admin_level"]
                    st.session_state.page = "home"

                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)

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
            if not is_valid_username(reg_user):
                st.error("Ungültiger Username. Nutze 3-40 Zeichen: Buchstaben, Zahlen oder _.")

            elif not is_valid_email(reg_mail):
                st.error("Ungültige Email.")

            elif captcha != result:
                st.error("Captcha falsch.")
                refresh_captcha()
                st.rerun()

            else:
                ok, msg = create_user(reg_user, reg_mail, reg_pw)

                if ok:
                    st.success(msg)
                    refresh_captcha()
                else:
                    st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)


elif page == "dashboard":
    require_login()
    sync_user(st.session_state.user)

    st.title("📊 User Dashboard")

    a, b, c = st.columns(3)
    a.metric("User", st.session_state.user)
    b.metric("Plan", st.session_state.plan)
    c.metric("Tokens", st.session_state.tokens)

    st.markdown('<div class="page-card">', unsafe_allow_html=True)
    st.markdown("### Letzte Nutzung")

    usage = list_usage(st.session_state.user)
    if usage:
        st.dataframe(usage[:20], use_container_width=True)
    else:
        st.info("Noch keine Nutzung vorhanden.")

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "image":
    require_login()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">PRO FEATURE</span>
            <h1>🎨 AI Image Generator</h1>
            <p style="font-size:20px;color:#d4d4d8;line-height:1.7;">
                Erstelle professionelle Bilder für Branding, Produkte, Social Media und Kampagnen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not can_use("pro"):
        st.warning("Dieses Feature benötigt mindestens PRO.")
        st.stop()

    cost = TOKEN_COSTS.get("image", 25)

    prompt = st.text_area(
        "Bild Prompt",
        key="image_prompt",
        height=180,
        placeholder="Beispiel: Futuristisches Luxus-Logo auf schwarzem Hintergrund, neon blue and purple, cinematic lighting...",
    )

    size = st.selectbox("Bildgröße", ["1024x1024", "1024x1536", "1536x1024"], key="image_size")

    st.info(f"Kosten: {cost} Tokens pro Bild")

    if st.button("Bild generieren", key="generate_image_btn"):
        with st.spinner("Bild wird generiert..."):
            success, result, updated_user = run_ai_task(
                username=st.session_state.user,
                tool="image",
                prompt=prompt,
                provider="openai",
                generator_func=generate_image,
                size=size,
            )

        if success:
            st.session_state.last_image_path = result

            if updated_user:
                st.session_state.tokens = updated_user["tokens"]

            st.success("Bild erfolgreich generiert.")
        else:
            st.error(result)

    if st.session_state.last_image_path:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("Ergebnis")
        st.image(st.session_state.last_image_path, use_container_width=True)
        render_file_download(st.session_state.last_image_path, "Bild herunterladen")
        st.markdown("</div>", unsafe_allow_html=True)


elif page == "video":
    require_login()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">GRAND FEATURE</span>
            <h1>🎬 AI Video Generator</h1>
            <p style="font-size:20px;color:#d4d4d8;line-height:1.7;">
                Generiere AI-Videos über Replicate für Reels, Ads, Social Media und Content-Kampagnen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not can_use("grand"):
        st.warning("Dieses Feature benötigt mindestens GRAND.")
        st.stop()

    cost = TOKEN_COSTS.get("video", 150)

    prompt = st.text_area(
        "Video Prompt",
        key="video_prompt",
        height=200,
        placeholder="Beispiel: A cinematic product video of a luxury AI platform logo, neon blue and purple energy waves, slow camera movement...",
    )

    st.info(f"Kosten: {cost} Tokens pro Video")

    if st.button("Video generieren", key="generate_video_btn"):
        with st.spinner("Video wird generiert. Das kann länger dauern..."):
            success, result, updated_user = run_ai_task(
                username=st.session_state.user,
                tool="video",
                prompt=prompt,
                provider="replicate",
                generator_func=generate_video,
            )

        if success:
            st.session_state.last_video_path = result

            if updated_user:
                st.session_state.tokens = updated_user["tokens"]

            st.success("Video erfolgreich generiert.")
        else:
            st.error(result)

    if st.session_state.last_video_path:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("Ergebnis")

        if str(st.session_state.last_video_path).startswith("http"):
            st.video(st.session_state.last_video_path)
            st.markdown(f"[Video öffnen]({st.session_state.last_video_path})")
        else:
            st.video(st.session_state.last_video_path)
            render_file_download(st.session_state.last_video_path, "Video herunterladen")

        st.markdown("</div>", unsafe_allow_html=True)



elif page == "chat":
    require_login()

    st.title("💬 Memory Chat")

    init_chat_memory()

    history = load_chat_history(st.session_state.user)

    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Schreibe eine Nachricht...")

    if prompt:
        save_chat_message(st.session_state.user, "user", prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AI denkt nach..."):
            success, answer = generate_chat(prompt)

        if success:
            save_chat_message(st.session_state.user, "assistant", answer)

            with st.chat_message("assistant"):
                st.markdown(answer)

        else:
            st.error(answer)

    if st.button("🗑 Chat löschen"):
        clear_chat_history(st.session_state.user)
        st.rerun()


elif page == "coding":
    require_login()
    st.title("💻 Coding Area")
    st.info("Coding Modul folgt als nächstes.")


elif page == "music":
    require_login()
    st.title("🎵 Music Generator")
    st.info("Music Modul folgt als nächstes.")


elif page == "reels":
    require_login()
    st.title("🎞️ Reels Generator")
    st.info("Reels Modul folgt als nächstes.")
    st.title("🆘 Support")

    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    subject = st.text_input("Betreff", key="support_subject")
    msg = st.text_area("Nachricht", key="support_msg", height=180)
    category = st.selectbox(
        "Kategorie",
        ["Allgemein", "Account", "Payment", "Technik", "Bug"],
        key="support_category",
    )

    if st.button("Ticket senden", key="ticket_send"):
        if not subject or not msg:
            st.error("Bitte alles ausfüllen.")
        else:
            ok, response = create_support_message(
                username=st.session_state.user,
                email=st.session_state.email,
                category=category,
                subject=subject,
                message=msg,
            )

            if ok:
                st.success(response)
            else:
                st.error(response)

    st.markdown("</div>", unsafe_allow_html=True)


elif page == "premium":
    st.title("💳 Buy Premium")

    plans = [
        ("pro", "Pro", "9.99€ / Monat", "1200 Tokens<br>Image Generator<br>Coding Area<br>Music Generator<br>Short Reels"),
        ("grand", "Grand", "49.99€ / Monat", "4000 Tokens<br>Alles aus Pro<br>AI Video Generator<br>Stärkere Workflows"),
        ("elite", "Elite", "199€ / Monat", "Alles freigeschaltet<br>Höchste API-Leistung<br>Beste Qualität<br>Maximaler Zugriff"),
    ]

    cols = st.columns(3)

    for col, item in zip(cols, plans):
        plan_key, title, price, features = item

        with col:
            st.markdown(
                f"""
                <div class="price-card">
                    <h2>{title}</h2>
                    <div class="price">{price}</div>
                    <div class="feature-list">{features}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(f"Buy {title}", key=f"buy_{plan_key}"):
                if not is_logged_in():
                    st.warning("Bitte zuerst einloggen.")
                    st.session_state.page = "login"
                    st.rerun()

                if create_checkout_session is None:
                    st.error("Stripe Modul ist noch nicht korrekt verbunden.")
                else:
                    url, error = create_checkout_session(st.session_state.user, plan_key)

                    if error:
                        st.error(error)
                    else:
                        st.link_button("Zur Zahlung", url, use_container_width=True)


elif page == "admin":
    require_login()

    if not is_admin():
        st.error("Kein Zugriff.")
        st.stop()

    st.title("🛡️ Admin Panel")

    counts = support_counts()
    health = ai_health_check()

    a, b, c, d = st.columns(4)
    a.metric("Tickets Gesamt", counts.get("total", 0))
    b.metric("Offen", counts.get("open", 0))
    c.metric("Geschlossen", counts.get("closed", 0))
    d.metric("Admin Level", st.session_state.admin_level)

    tab_tickets, tab_users, tab_codes, tab_logs, tab_payments, tab_system = st.tabs(
        ["Tickets", "Users", "Redeem Codes", "Logs", "Payments", "System"]
    )

    with tab_tickets:
        status_filter = st.selectbox("Status Filter", ["all", "open", "closed"], key="admin_ticket_filter")
        tickets = list_support_messages(status_filter)

        if not tickets:
            st.info("Keine Tickets vorhanden.")
        else:
            for ticket in tickets:
                with st.expander(f"#{ticket['id']} · {ticket['subject']} · {ticket['status']}"):
                    st.write(f"User: {ticket.get('username')}")
                    st.write(f"Email: {ticket.get('email')}")
                    st.write(f"Kategorie: {ticket.get('category')}")
                    st.write(f"Nachricht: {ticket.get('message')}")
                    st.write(f"Erstellt: {ticket.get('created_at')}")

                    c1, c2 = st.columns(2)

                    if c1.button("Als geschlossen markieren", key=f"close_ticket_{ticket['id']}"):
                        set_support_status(ticket["id"], "closed")
                        add_audit_log(st.session_state.user, "close_ticket", str(ticket["id"]))
                        st.rerun()

                    if c2.button("Ticket löschen", key=f"delete_ticket_{ticket['id']}"):
                        delete_support_message(ticket["id"])
                        add_audit_log(st.session_state.user, "delete_ticket", str(ticket["id"]))
                        st.rerun()

    with tab_users:
        users = list_users()
        st.dataframe(users, use_container_width=True)

        st.markdown("### User bearbeiten")

        target_user = st.text_input("Username", key="admin_target_user")
        new_plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"], key="admin_new_plan")
        new_tokens = st.number_input("Tokens setzen", min_value=0, value=0, step=100, key="admin_new_tokens")

        if is_owner():
            new_role = st.selectbox("Role", ["user", "supporter", "moderator", "admin", "owner"], key="admin_new_role")
            new_level = st.selectbox("Admin Level", [0, 1, 2, 3, 999], key="admin_new_level")
        else:
            new_role = "user"
            new_level = 0

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("Plan setzen", key="admin_set_plan"):
            set_plan(target_user, new_plan)
            add_audit_log(st.session_state.user, "set_plan", target_user, new_plan)
            st.success("Plan geändert.")

        if c2.button("Tokens setzen", key="admin_set_tokens"):
            update_tokens(target_user, new_tokens)
            add_audit_log(st.session_state.user, "set_tokens", target_user, str(new_tokens))
            st.success("Tokens geändert.")

        if c3.button("User bannen", key="admin_ban_user"):
            ban_user(target_user, True)
            add_audit_log(st.session_state.user, "ban_user", target_user)
            st.success("User gebannt.")

        if c4.button("User löschen", key="admin_delete_user"):
            delete_user(target_user)
            add_audit_log(st.session_state.user, "delete_user", target_user)
            st.success("User gelöscht.")

        if is_owner():
            if st.button("Role / Admin Level setzen", key="admin_set_role"):
                set_role(target_user, new_role, new_level)
                add_audit_log(st.session_state.user, "set_role", target_user, f"{new_role}:{new_level}")
                st.success("Role geändert.")

    with tab_codes:
        if not is_owner():
            st.info("Nur Owner/Admin Level 999 kann Codes erstellen.")
        else:
            with st.form("create_code_form"):
                code_type = st.selectbox("Typ", ["tokens", "plan", "mixed"])
                plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"])
                tokens = st.number_input("Tokens", min_value=0, value=100, step=100)
                max_uses = st.number_input("Max Uses", min_value=1, value=1)
                days_valid = st.number_input("Gültig Tage", min_value=1, value=30)

                submit = st.form_submit_button("Code erstellen")

            if submit:
                code = create_redeem_code(
                    code_type=code_type,
                    value="",
                    tokens=tokens,
                    plan=plan,
                    max_uses=max_uses,
                    created_by=st.session_state.user,
                    days_valid=days_valid,
                )
                add_audit_log(st.session_state.user, "create_redeem_code", code)
                st.success(f"Code erstellt: {code}")

        codes = list_codes()
        st.dataframe(codes, use_container_width=True)

    with tab_logs:
        st.markdown("### Usage Logs")
        st.dataframe(list_usage(), use_container_width=True)

        st.markdown("### Audit Logs")
        st.dataframe(list_audit_logs(), use_container_width=True)

    with tab_payments:
        purchases = list_purchases()
        st.dataframe(purchases, use_container_width=True)

    with tab_system:
        st.markdown("### AI Health Check")
        st.json(health)

        st.markdown("### Plans")
        st.json(PLANS)


else:
    st.error("Seite nicht gefunden.")