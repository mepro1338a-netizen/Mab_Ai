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
        sync_session_user(user)
        st.session_state.logged_in = True
        st.session_state.page = "home"
        st.success(msg)
        st.rerun()
    else:
        st.error(msg)


def do_register(username, email, password, captcha):
    result = st.session_state.captcha_a + st.session_state.captcha_b

    if not is_valid_username(username):
        st.error("Username ungültig.")
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


def render_auth():
    ensure_captcha()

    st.title("🔐 MaByte Access")
    st.caption("Login für Chat, Coding, Media Studio und AI Automation.")

    left, right = st.columns([0.75, 1.25], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("AI Workspace")
            st.write("💬 Memory Chat")
            st.write("💻 Coding AI")
            st.write("🎬 Reels & Video")
            st.write("🎵 Music AI")
            st.write("📊 Dashboard")

            st.info("Einloggen und direkt starten.")

    with right:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["👤 Login", "👥 Registrierung"])

            with tab_login:
                st.subheader("Willkommen zurück")

                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="dein username")
                    password = st.text_input("Passwort", type="password", placeholder="dein Passwort")

                    submitted = st.form_submit_button("🚀 Einloggen", use_container_width=True)

                    if submitted:
                        do_login(username, password)

                st.divider()

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("🌐 Google", use_container_width=True):
                        st.info("Google Login wird vorbereitet.")

                with c2:
                    if st.button("📸 Instagram", use_container_width=True):
                        st.info("Instagram Login wird vorbereitet.")

            with tab_register:
                st.subheader("Account erstellen")

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