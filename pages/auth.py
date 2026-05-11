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


def render_login_tab():
    with st.form("login_form"):
        st.subheader("Willkommen zurück")
        st.caption("Logge dich ein und öffne dein MaByte Control Center.")

        username = st.text_input(
            "Username",
            placeholder="dein username",
        )

        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="dein passwort",
        )

        submitted = st.form_submit_button(
            "🚀 Einloggen",
            use_container_width=True,
        )

        if submitted:
            do_login(username, password)


def render_register_tab():
    with st.form("register_form"):
        st.subheader("Neuen Account erstellen")
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
            "✨ Account erstellen",
            use_container_width=True,
        )

        if submitted:
            do_register(username, email, password, captcha)


def render_auth():
    ensure_captcha()

    st.title("🔐 MaByte Access")
    st.caption("Dein Login für Chat, Coding, Media Studio und AI Automation.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Start", "Free")

    with c2:
        st.metric("Tools", "AI Hub")

    with c3:
        st.metric("Security", "Protected")

    st.divider()

    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("Alles in einem AI Workspace")
        st.write("💬 Memory Chat")
        st.write("💻 Coding AI")
        st.write("🎬 Reels & Video Studio")
        st.write("🎵 Music AI")
        st.write("📊 Dashboard & Tokens")
        st.write("🛡️ Admin Panel")

        st.info("Free starten. Upgrade jederzeit möglich.")

    with right:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["Login", "Register"])

            with tab_login:
                render_login_tab()

            with tab_register:
                render_register_tab()