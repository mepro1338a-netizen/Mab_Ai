import random
import streamlit as st

from database import create_user, verify_login
from security import is_valid_username, is_valid_email, check_login_rate
from ui_core import sync_session_user


def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def ensure_captcha():
    if "captcha_a" not in st.session_state:
        refresh_captcha()


def do_login(username, password):
    allowed, rate_msg = check_login_rate(username)

    if not allowed:
        st.error(rate_msg)
        return

    ok, msg, user = verify_login(username, password)

    if ok and user:
        st.session_state.logged_in = True
        sync_session_user(user)
        st.session_state.page = "home"
        st.success(msg)
        st.rerun()
    else:
        st.error(msg)


def do_register(username, email, password, captcha):
    result = st.session_state.captcha_a + st.session_state.captcha_b

    if not is_valid_username(username):
        st.error("Username ungültig. Nutze 3-40 Zeichen: Buchstaben, Zahlen oder _.")
        return

    if not is_valid_email(email):
        st.error("Bitte eine gültige Email eingeben.")
        return

    if len(password or "") < 6:
        st.error("Passwort muss mindestens 6 Zeichen haben.")
        return

    if captcha != result:
        st.error("Captcha falsch.")
        refresh_captcha()
        st.rerun()

    ok, msg = create_user(username, email, password)

    if ok:
        st.success("Account erstellt. Du kannst dich jetzt einloggen.")
        refresh_captcha()
    else:
        st.error(msg)


def auth_css():
    st.markdown(
        """
<style>
.auth-wrap {
    max-width: 1250px;
    margin: 0 auto;
    padding-top: 20px;
}

.auth-hero {
    text-align: center;
    margin-bottom: 34px;
}

.auth-title {
    font-size: 58px;
    font-weight: 1000;
    color: white;
    margin: 0;
    text-shadow: 0 0 34px rgba(56,189,248,.28);
}

.auth-sub {
    color: #c7d2fe;
    font-size: 20px;
    font-weight: 700;
    margin-top: 10px;
}

.auth-panel {
    padding: 34px;
    border-radius: 32px;
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 34%),
        linear-gradient(145deg, rgba(5,15,35,.96), rgba(8,28,62,.90));
    border: 1px solid rgba(96,165,250,.35);
    box-shadow: 0 0 55px rgba(37,99,235,.20);
}

.auth-side {
    padding: 34px;
    border-radius: 30px;
    background:
        linear-gradient(145deg, rgba(7,18,42,.85), rgba(12,38,78,.58));
    border: 1px solid rgba(96,165,250,.20);
    box-shadow: 0 0 35px rgba(56,189,248,.10);
}

.auth-side h2 {
    font-size: 34px;
    font-weight: 1000;
    color: white;
    margin-bottom: 16px;
}

.auth-side p {
    color: #dbeafe;
    font-size: 17px;
    font-weight: 700;
    line-height: 1.65;
}

.auth-point {
    padding: 14px 16px;
    border-radius: 18px;
    background: rgba(15,42,82,.55);
    border: 1px solid rgba(96,165,250,.18);
    color: #e0f2fe;
    font-weight: 850;
    margin-bottom: 12px;
}

.auth-security {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 24px;
}

.auth-security span {
    padding: 10px 14px;
    border-radius: 999px;
    background: rgba(14,165,233,.14);
    border: 1px solid rgba(125,211,252,.25);
    color: #bfdbfe !important;
    font-weight: 800;
}

[data-testid="stForm"] {
    border: none !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 18px;
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    justify-content: center;
    border-radius: 18px !important;
    min-height: 58px;
    font-size: 18px;
}

.stTextInput input,
.stNumberInput input {
    min-height: 58px !important;
    font-size: 17px !important;
    border-radius: 18px !important;
}

.stFormSubmitButton > button {
    min-height: 62px !important;
    font-size: 20px !important;
    border-radius: 20px !important;
    background: linear-gradient(135deg, #2563eb, #22d3ee) !important;
    color: white !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_login_tab():
    with st.form("login_form"):
        st.subheader("👋 Willkommen zurück")
        st.caption("Logge dich ein und öffne dein MaByte Control Center.")

        username = st.text_input(
            "Username",
            placeholder="dein username",
        )

        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="dein Passwort",
        )

        submitted = st.form_submit_button(
            "🚀 Einloggen",
            use_container_width=True,
        )

        if submitted:
            do_login(username, password)


def render_register_tab():
    with st.form("register_form"):
        st.subheader("✨ Account erstellen")
        st.caption("Starte kostenlos und upgrade später auf Pro, Grand oder Elite.")

        username = st.text_input(
            "Username",
            placeholder="3-40 Zeichen",
        )

        email = st.text_input(
            "Email",
            placeholder="deine@email.de",
        )

        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="mind. 6 Zeichen",
        )

        captcha = st.number_input(
            f"Sicherheitsfrage: {st.session_state.captcha_a} + {st.session_state.captcha_b}",
            min_value=0,
            max_value=10,
            step=1,
        )

        submitted = st.form_submit_button(
            "✨ Registrierung abschließen",
            use_container_width=True,
        )

        if submitted:
            do_register(username, email, password, captcha)


def render_auth():
    ensure_captcha()
    auth_css()

    st.markdown(
        """
<div class="auth-wrap">
    <div class="auth-hero">
        <div style="font-size:72px;">🔐</div>
        <h1 class="auth-title">MaByte Access</h1>
        <div class="auth-sub">
            Dein Login für Chat, Coding, Media Studio und AI Automation.
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([0.95, 1.15], gap="large")

    with left:
        st.markdown(
            """
<div class="auth-side">
    <h2>Alles in einem AI Workspace</h2>
    <p>
        MaByte verbindet Chat, Coding, Content, Reels,
        Video-Ideen und Business-Workflows in einer Plattform.
    </p>

    <div class="auth-point">💬 Memory Chat mit Verlauf</div>
    <div class="auth-point">💻 Coding AI für Projekte</div>
    <div class="auth-point">🎬 Reels & Video Studio</div>
    <div class="auth-point">🎵 Music AI & Content Tools</div>
    <div class="auth-point">📊 Tokens, Dashboard & Premium</div>

    <div class="auth-security">
        <span>🛡️ Geschützt</span>
        <span>⚡ Schnell</span>
        <span>🔒 Sicher</span>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="auth-panel">', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["👤 Login", "👥 Registrierung"])

        with tab_login:
            render_login_tab()

        with tab_register:
            render_register_tab()

        st.markdown("</div>", unsafe_allow_html=True)