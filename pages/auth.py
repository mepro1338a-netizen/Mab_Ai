import random
import streamlit as st

from database import create_user, verify_login
from security import (
    is_valid_username,
    is_valid_email,
    check_login_rate,
)
from ui_core import sync_session_user


# =========================================================
# CAPTCHA
# =========================================================

def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def ensure_captcha():
    if "captcha_a" not in st.session_state:
        refresh_captcha()


# =========================================================
# LOGIN
# =========================================================

def do_login(username, password):

    allowed, msg = check_login_rate(username)

    if not allowed:
        st.error(msg)
        return

    ok, msg, user = verify_login(username, password)

    if ok and user:

        sync_session_user(user)

        st.session_state.logged_in = True
        st.session_state.page = "home"

        st.success("Login erfolgreich")
        st.rerun()

    else:
        st.error(msg)


# =========================================================
# AUTH PAGE
# =========================================================

def render_auth():

    ensure_captcha()

    st.markdown(
        """
<style>

#MainMenu,
footer,
header,
[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 30%),
        radial-gradient(circle at bottom right, rgba(37,99,235,.18), transparent 30%),
        linear-gradient(135deg, #020617 0%, #071427 45%, #0f172a 100%) !important;
}

.main .block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.auth-shell {
    margin-top: 50px;
}

.auth-box {
    background:
        linear-gradient(145deg, rgba(5,15,35,.98), rgba(9,35,75,.92));
    border: 1px solid rgba(125,211,252,.18);
    border-radius: 34px;
    padding: 45px;
    box-shadow: 0 0 45px rgba(56,189,248,.15);
}

.auth-title {
    font-size: 72px;
    font-weight: 1000;
    line-height: 1;
    color: white;
    margin-bottom: 22px;
}

.auth-sub {
    font-size: 22px;
    line-height: 1.6;
    color: #dbeafe;
    margin-bottom: 35px;
    font-weight: 700;
}

.auth-feature {
    padding: 18px 22px;
    border-radius: 18px;
    margin-bottom: 16px;
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(125,211,252,.16);
    color: white;
    font-weight: 800;
    font-size: 18px;
}

.login-title {
    font-size: 48px;
    color: white;
    font-weight: 1000;
    margin-bottom: 10px;
}

.login-sub {
    color: #cbd5e1;
    font-size: 16px;
    margin-bottom: 30px;
    font-weight: 700;
}

.stTextInput input,
.stNumberInput input {
    background: rgba(2,6,23,.88) !important;
    border: 1px solid rgba(125,211,252,.28) !important;
    color: white !important;
    border-radius: 18px !important;
    min-height: 54px !important;
    font-weight: 700 !important;
}

.stTextInput input::placeholder {
    color: #bfdbfe !important;
    opacity: 1 !important;
}

.stButton > button {
    width: 100%;
    min-height: 54px;
    border-radius: 18px !important;
    border: 1px solid rgba(125,211,252,.25) !important;
    background:
        linear-gradient(135deg, #2563eb, #38bdf8) !important;
    color: white !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    transition: .2s ease;
    box-shadow: 0 0 25px rgba(56,189,248,.22);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 35px rgba(56,189,248,.35);
}

h1, h2, h3, label {
    color: white !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1])

    # =====================================================
    # LEFT
    # =====================================================

    with left:

        st.markdown(
            """
<div class="auth-shell">
    <div class="auth-box">

        <div class="auth-title">
            🚀 MaByte
        </div>

        <div class="auth-sub">
            Deine moderne AI Plattform für Chat,
            Coding, Bilder, Musik, Reels,
            Content und Automation.
        </div>

        <div class="auth-feature">
            💬 AI Memory Chat
        </div>

        <div class="auth-feature">
            💻 Coding AI
        </div>

        <div class="auth-feature">
            🎨 Image & Design AI
        </div>

        <div class="auth-feature">
            🎬 Reels & Video AI
        </div>

        <div class="auth-feature">
            🎵 Music AI
        </div>

    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    # =====================================================
    # RIGHT
    # =====================================================

    with right:

        st.markdown(
            """
<div class="auth-shell">
    <div class="auth-box">

        <div class="login-title">
            Willkommen zurück
        </div>

        <div class="login-sub">
            Öffne dein MaByte AI Workspace.
        </div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(
            [
                "👤 Login",
                "📝 Registrierung",
            ]
        )

        # =================================================
        # LOGIN
        # =================================================

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
                st.button(
                    "🌐 Google Login",
                    use_container_width=True,
                )

            with c2:
                st.button(
                    "📸 Instagram Login",
                    use_container_width=True,
                )

        # =================================================
        # REGISTER
        # =================================================

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

        st.markdown(
            """
</div>
</div>
            """,
            unsafe_allow_html=True,
        )