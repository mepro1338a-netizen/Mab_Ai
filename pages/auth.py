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
<style>
.auth-wrap {
    max-width: 720px;
    margin: 0 auto;
    padding-top: 25px;
}

.auth-head {
    text-align: center;
    margin-bottom: 28px;
}

.auth-title {
    font-size: 58px;
    font-weight: 1000;
    color: white;
    margin-bottom: 10px;
    text-shadow: 0 0 30px rgba(56,189,248,.22);
}

.auth-sub {
    color: #bfdbfe;
    font-size: 18px;
    font-weight: 800;
}

.auth-card {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 35%),
        linear-gradient(145deg, rgba(5,15,35,.98), rgba(9,35,75,.92));
    border: 1px solid rgba(125,211,252,.30);
    border-radius: 34px;
    padding: 34px;
    box-shadow: 0 0 55px rgba(56,189,248,.18);
}

.auth-note {
    margin-top: 18px;
    color: #93c5fd;
    text-align: center;
    font-weight: 700;
    font-size: 14px;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="auth-wrap">
    <div class="auth-head">
        <div class="auth-title">🔐 Login</div>
        <div class="auth-sub">Starte deine MaByte AI Plattform.</div>
    </div>
    <div class="auth-card">
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["🔓 Login", "🆕 Register"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Dein Username")
            password = st.text_input("Password", type="password", placeholder="Dein Passwort")

            submitted = st.form_submit_button("🚀 Einloggen", use_container_width=True)

            if submitted:
                do_login(username, password)

        st.markdown(
            '<div class="auth-note">Enter drücken funktioniert hier automatisch.</div>',
            unsafe_allow_html=True,
        )

    with tab_register:
        with st.form("register_form", clear_on_submit=False):
            reg_user = st.text_input("Username", placeholder="3-40 Zeichen")
            reg_mail = st.text_input("Email", placeholder="deine@email.de")
            reg_pw = st.text_input("Password", type="password", placeholder="Sicheres Passwort")

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

    st.markdown(
        """
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )