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
    allowed, msg = check_login_rate(username)

    if not allowed:
        st.error(msg)
        return

    ok, msg, user = verify_login(username, password)

    if ok and user:
        sync_session_user(user)
        st.session_state.page = "home"
        st.success("Login erfolgreich")
        st.rerun()
    else:
        st.error(msg)


def do_register(username, email, password, captcha):
    result = st.session_state.captcha_a + st.session_state.captcha_b

    if not is_valid_username(username):
        st.error("Ungültiger Username.")
        return

    if not is_valid_email(email):
        st.error("Ungültige Email.")
        return

    if len(password or "") < 6:
        st.error("Passwort muss mindestens 6 Zeichen haben.")
        return

    if captcha != result:
        st.error("Captcha falsch.")
        refresh_captcha()
        st.rerun()

    ok, msg = create_user(
        username=username,
        email=email,
        password=password,
        role="user",
        plan="free",
    )

    if ok:
        st.success("Account erstellt. Du kannst dich jetzt einloggen.")
        refresh_captcha()
    else:
        st.error(msg)


def auth_css():
    st.markdown(
        """
<style>
[data-testid="stSidebar"] {
    display: none !important;
}

.main .block-container {
    max-width: 860px;
    padding-top: 4rem;
}

.stApp {
    background:
        radial-gradient(circle at top, rgba(56,189,248,.18), transparent 30%),
        linear-gradient(135deg, #020617 0%, #06142b 55%, #020617 100%) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(3,10,25,.95), rgba(8,25,55,.90)) !important;
    border: 1px solid rgba(96,165,250,.35) !important;
    border-radius: 30px !important;
    box-shadow: 0 0 55px rgba(56,189,248,.20);
}

.stTextInput input,
.stNumberInput input {
    background: rgba(2,6,23,.92) !important;
    border: 1px solid rgba(125,211,252,.35) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    border-radius: 18px !important;
    min-height: 56px !important;
    font-weight: 800 !important;
}

.stTextInput input::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

.stButton > button,
.stFormSubmitButton > button {
    min-height: 58px !important;
    border-radius: 18px !important;
    background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
    border: 1px solid rgba(125,211,252,.35) !important;
    color: white !important;
    font-weight: 950 !important;
    box-shadow: 0 0 28px rgba(56,189,248,.25);
}

.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: 900;
}

.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
}

h1, h2, h3, label {
    color: white !important;
}

p, span {
    color: #cbd5e1 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_auth():
    ensure_captcha()
    auth_css()

    st.markdown("# 🔒 MaByte Access")
    st.caption("Dein Login für Chat, Coding, Media Studio und AI Automation.")

    st.write("")

    with st.container(border=True):
        tab_login, tab_register = st.tabs(["👤 Login", "👥 Registrierung"])

        with tab_login:
            st.subheader("👋 Willkommen zurück")
            st.caption("Logge dich ein und öffne dein MaByte Control Center.")

            with st.form("login_form"):
                username = st.text_input("Username", placeholder="dein username")
                password = st.text_input("Passwort", type="password", placeholder="dein Passwort")

                keep_logged = st.checkbox("Angemeldet bleiben")

                submitted = st.form_submit_button("🚀 Einloggen", use_container_width=True)

                if submitted:
                    do_login(username, password)

            st.divider()
            st.caption("oder")

            if st.button("🌐 Mit Google anmelden", use_container_width=True):
                st.info("Google Login wird vorbereitet.")

        with tab_register:
            st.subheader("✨ Account erstellen")
            st.caption("Starte kostenlos mit MaByte.")

            with st.form("register_form"):
                username = st.text_input("Username", placeholder="3-40 Zeichen")
                email = st.text_input("Email", placeholder="deine@email.de")
                password = st.text_input("Passwort", type="password", placeholder="mindestens 6 Zeichen")

                captcha = st.number_input(
                    f"Sicherheitsfrage: {st.session_state.captcha_a} + {st.session_state.captcha_b}",
                    min_value=0,
                    max_value=10,
                    step=1,
                )

                submitted = st.form_submit_button("✨ Registrieren", use_container_width=True)

                if submitted:
                    do_register(username, email, password, captcha)