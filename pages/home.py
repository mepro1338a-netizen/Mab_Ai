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
    max-width: 1180px;
    padding-top: 4rem;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,.20), transparent 30%),
        radial-gradient(circle at bottom right, rgba(37,99,235,.18), transparent 30%),
        linear-gradient(135deg, #020617 0%, #071427 48%, #0f172a 100%) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(5,15,35,.96), rgba(9,35,75,.90)) !important;
    border: 1px solid rgba(125,211,252,.20) !important;
    border-radius: 30px !important;
    box-shadow: 0 0 45px rgba(56,189,248,.14);
}

.stTextInput input,
.stNumberInput input {
    background: rgba(2,6,23,.90) !important;
    border: 1px solid rgba(125,211,252,.30) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    border-radius: 18px !important;
    min-height: 52px !important;
    font-weight: 800 !important;
}

.stTextInput input::placeholder {
    color: #bfdbfe !important;
    opacity: 1 !important;
}

.stButton > button,
.stFormSubmitButton > button {
    min-height: 54px !important;
    border-radius: 18px !important;
    background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
    border: 1px solid rgba(125,211,252,.35) !important;
    color: white !important;
    font-weight: 950 !important;
    box-shadow: 0 0 24px rgba(56,189,248,.20);
}

h1, h2, h3, label {
    color: white !important;
}

p, span {
    color: #dbeafe !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_auth():
    ensure_captcha()
    auth_css()

    left, right = st.columns([1, 1], gap="large")

    with left:
        with st.container(border=True):
            st.title("🚀 MaByte")
            st.subheader("Deine AI Plattform")
            st.write("Chat, Coding, Bilder, Musik, Reels, Content und Automation in einer Plattform.")

            st.divider()

            st.write("💬 AI Memory Chat")
            st.write("💻 Coding AI")
            st.write("🎨 Image & Design AI")
            st.write("🎬 Reels & Video AI")
            st.write("🎵 Music AI")

    with right:
        with st.container(border=True):
            st.title("🔐 MaByte Access")
            st.caption("Öffne deinen AI Workspace.")

            tab_login, tab_register = st.tabs(["👤 Login", "📝 Registrierung"])

            with tab_login:
                st.subheader("Willkommen zurück")

                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="dein username")
                    password = st.text_input("Passwort", type="password", placeholder="dein Passwort")

                    submitted = st.form_submit_button("🚀 Einloggen", use_container_width=True)

                    if submitted:
                        do_login(username, password)

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("🌐 Google Login", use_container_width=True):
                        st.info("Google Login wird vorbereitet.")

                with c2:
                    if st.button("📸 Instagram Login", use_container_width=True):
                        st.info("Instagram Login wird vorbereitet.")

            with tab_register:
                st.subheader("Account erstellen")

                with st.form("register_form"):
                    reg_user = st.text_input("Username", placeholder="3-40 Zeichen")
                    reg_email = st.text_input("Email", placeholder="deine@email.de")
                    reg_pw = st.text_input("Passwort", type="password", placeholder="mindestens 6 Zeichen")

                    captcha = st.number_input(
                        f"Sicherheitsfrage: {st.session_state.captcha_a} + {st.session_state.captcha_b}",
                        min_value=0,
                        max_value=10,
                        step=1,
                    )

                    submitted = st.form_submit_button("✨ Registrieren", use_container_width=True)

                    if submitted:
                        do_register(reg_user, reg_email, reg_pw, captcha)