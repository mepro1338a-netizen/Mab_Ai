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
        st.error("Ungültiger Username")
        return

    if not is_valid_email(email):
        st.error("Ungültige Email")
        return

    if len(password) < 6:
        st.error("Passwort zu kurz")
        return

    if captcha != result:
        st.error("Captcha falsch")
        refresh_captcha()
        return

    ok, msg = create_user(
        username=username,
        email=email,
        password=password,
        role="user",
        plan="free",
    )

    if ok:
        st.success("Registrierung erfolgreich")
    else:
        st.error(msg)


def auth_css():

    st.markdown(
        """
<style>


#MainMenu,
header,
footer{
    display:none;
}

.stApp{
    background:
        radial-gradient(circle at top, rgba(56,189,248,.15), transparent 30%),
        linear-gradient(135deg,#020617 0%,#071427 55%,#020617 100%);
}

.main .block-container{
    max-width:1100px;
    padding-top:3rem;
}

.auth-title{
    text-align:center;
    color:white;
    font-size:68px;
    font-weight:900;
    margin-bottom:10px;
}

.auth-sub{
    text-align:center;
    color:#cbd5e1;
    font-size:20px;
    margin-bottom:40px;
}

.auth-box{
    background:rgba(2,6,23,.85);
    border:1px solid rgba(96,165,250,.25);
    border-radius:30px;
    padding:40px;
    box-shadow:0 0 40px rgba(59,130,246,.20);
}

.stTextInput input{
    background:rgba(2,6,23,.95)!important;
    border:1px solid rgba(96,165,250,.35)!important;
    color:white!important;
    border-radius:18px!important;
    min-height:55px!important;
    font-weight:700!important;
}

.stButton > button{
    min-height:55px!important;
    border-radius:18px!important;
    border:none!important;
    background:linear-gradient(135deg,#2563eb,#38bdf8)!important;
    color:white!important;
    font-weight:900!important;
    box-shadow:0 0 25px rgba(56,189,248,.25);
}

h1,h2,h3,label{
    color:white!important;
}

p,span{
    color:#cbd5e1!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


def render_auth():

    ensure_captcha()
    auth_css()

    st.markdown(
        """
<div class="auth-title">
🔒 MaByte Access
</div>

<div class="auth-sub">
Dein Login für Chat, Coding, Media Studio und AI Automation.
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])

    with left:

        st.markdown(
            """
<div class="auth-box">

## 🚀 MaByte

Deine moderne AI Plattform für:

- 💬 AI Memory Chat
- 💻 Coding AI
- 🎨 Image & Design AI
- 🎬 Reels & Video AI
- 🎵 Music AI
- 🤖 Automation

</div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown('<div class="auth-box">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["👤 Login", "📝 Registrierung"])

        with tab1:

            st.subheader("Willkommen zurück")

            username = st.text_input(
                "Username",
                placeholder="dein username",
                key="login_user",
            )

            password = st.text_input(
                "Passwort",
                type="password",
                placeholder="dein Passwort",
                key="login_pw",
            )

            if st.button("🚀 Einloggen", use_container_width=True):
                do_login(username, password)

            st.write("")

            if st.button("🌐 Google Login", use_container_width=True):
                st.info("Google Login wird vorbereitet.")

        with tab2:

            st.subheader("Account erstellen")

            reg_user = st.text_input(
                "Username",
                key="reg_user",
            )

            reg_email = st.text_input(
                "Email",
                key="reg_email",
            )

            reg_pw = st.text_input(
                "Passwort",
                type="password",
                key="reg_pw",
            )

            captcha = st.number_input(
                f"{st.session_state.captcha_a} + {st.session_state.captcha_b}",
                min_value=0,
                max_value=20,
                step=1,
            )

            if st.button("✨ Registrieren", use_container_width=True):

                do_register(
                    reg_user,
                    reg_email,
                    reg_pw,
                    captcha,
                )

        st.markdown("</div>", unsafe_allow_html=True)