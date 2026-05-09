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
        st.session_state.captcha_a = random.randint(1, 5)

    if "captcha_b" not in st.session_state:
        st.session_state.captcha_b = random.randint(1, 5)


def render_auth():
    ensure_captcha()

    st.title("🔐 Login / Register")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
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
                    sync_session_user(user)
                    st.session_state.page = "home"

                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_register:
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
