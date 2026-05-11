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

    if ok:
        sync_session_user(user)
        st.session_state.page = "home"
        st.success("Login erfolgreich")
        st.rerun()

    else:
        st.error(msg)


def render_auth():

    ensure_captcha()

    st.markdown(
        """
<style>

.auth-wrap {
    margin-top: 40px;
}

.auth-box {
    background:
        linear-gradient(145deg, rgba(5,15,35,.96), rgba(9,35,75,.92));
    border: 1px solid rgba(125,211,252,.20);
    border-radius: 34px;
    padding: 45px;
    box-shadow: 0 0 50px rgba(56,189,248,.16);
}

.auth-left {
    padding-right: 30px;
}

.auth-title {
    font-size: 66px;
    font-weight: 1000;
    line-height: 1;
    color: white;
    margin-bottom: 20px;
}

.auth-sub {
    font-size: 22px;
    color: #dbeafe;
    line-height: 1.6;
    margin-bottom: 35px;
    font-weight: 700;
}

.auth-feature {
    padding: 18px 22px;
    border-radius: 20px;
    margin-bottom: 16px;
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(125,211,252,.18);
    color: white;
    font-weight: 800;
    font-size: 18px;
}

.auth-login-title {
    font-size: 44px;
    font-weight: 1000;
    color: white;
    margin-bottom: 10px;
}

.auth-small {
    color: #cbd5e1;
    margin-bottom: 30px;
    font-size: 16px;
    font-weight: 700;
}

</style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 1])

    with left:

        st.markdown(
            """
<div class="auth-wrap">
    <div class="auth-box auth-left">

        <div class="auth-title">
            MaByte AI
        </div>

        <div class="auth-sub">
            Chat, Coding, Bilder, Reels, Musik und moderne AI Tools
            in einer einzigen Plattform.
        </div>

        <div class="auth-feature">💬 Memory Chat</div>
        <div class="auth-feature">💻 Coding AI</div>
        <div class="auth-feature">🎨 Bild Generator</div>
        <div class="auth-feature">🎬 Reels & Video AI</div>
        <div class="auth-feature">🎵 Music AI</div>

    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            """
<div class="auth-wrap">
    <div class="auth-box">
        <div class="auth-login-title">
            Willkommen zurück
        </div>

        <div class="auth-small">
            Logge dich ein und öffne dein AI Workspace.
        </div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["👤 Login", "📝 Registrierung"])

        with tab1:

            with st.form("login_form"):

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

            st.markdown("###")

            c1, c2 = st.columns(2)

            with c1:
                st.button("🌐 Google Login", use_container_width=True)

            with c2:
                st.button("📸 Instagram Login", use_container_width=True)

        with tab2:

            with st.form("register_form"):

                reg_user = st.text_input(
                    "Username",
                    placeholder="3-40 Zeichen",
                )

                reg_email = st.text_input(
                    "Email",
                    placeholder="deine@email.de",
                )

                reg_pw = st.text_input(
                    "Passwort",
                    type="password",
                    placeholder="mindestens 6 Zeichen",
                )

                result = (
                    st.session_state.captcha_a
                    + st.session_state.captcha_b
                )

                captcha = st.number_input(
                    f"{st.session_state.captcha_a} + {st.session_state.captcha_b}",
                    min_value=0,
                    max_value=10,
                    step=1,
                )

                submitted = st.form_submit_button(
                    "✨ Registrieren",
                    use_container_width=True,
                )

                if submitted:

                    if not is_valid_username(reg_user):
                        st.error("Ungültiger Username")

                    elif not is_valid_email(reg_email):
                        st.error("Ungültige Email")

                    elif captcha != result:
                        st.error("Captcha falsch")
                        refresh_captcha()

                    else:

                        ok, msg = create_user(
                            reg_user,
                            reg_email,
                            reg_pw,
                        )

                        if ok:
                            st.success(msg)

                        else:
                            st.error(msg)

        st.markdown("</div></div>", unsafe_allow_html=True)