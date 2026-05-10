import random
import streamlit as st

from database import create_user, verify_login
from security import is_valid_username, is_valid_email, check_login_rate
from ui_helpers import sync_session_user


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


def render_auth():
    ensure_captcha()

    st.markdown(
        """
        <div class="auth-shell">
            <div class="auth-badge">MABYTE ACCESS</div>
            <div class="auth-title">🔐 Login / Register</div>
            <div class="auth-subtitle">
                Melde dich an und starte dein AI Control Center.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="dein username")
            password = st.text_input("Password", type="password", placeholder="dein passwort")

            submitted = st.form_submit_button("🚀 Einloggen", use_container_width=True)

            if submitted:
                do_login(username, password)

    with tab_register:
        with st.form("register_form"):
            reg_user = st.text_input("Username", placeholder="3-40 Zeichen")
            reg_mail = st.text_input("Email", placeholder="deine@email.de")
            reg_pw = st.text_input("Password", type="password", placeholder="mind. 6 Zeichen")

            result = st.session_state.captcha_a + st.session_state.captcha_b

            captcha = st.number_input(
                f"Captcha: {st.session_state.captcha_a} + {st.session_state.captcha_b}",
                min_value=0,
                max_value=10,
                step=1,
            )

            submitted = st.form_submit_button("✨ Account erstellen", use_container_width=True)

            if submitted:
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