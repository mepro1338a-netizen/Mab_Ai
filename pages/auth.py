import random

import streamlit as st

from database import create_user, verify_login, record_login_event
from security import is_valid_username, is_valid_email, check_login_rate
from ui_core import sync_session_user


def refresh_captcha() -> None:
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def ensure_captcha() -> None:
    if "captcha_a" not in st.session_state or "captcha_b" not in st.session_state:
        refresh_captcha()


def client_meta() -> tuple[str, str]:
    ip_address = "unknown"
    user_agent = "streamlit-client"

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        headers = getattr(ctx, "request_headers", {}) if ctx else {}

        if headers:
            ip_address = headers.get("X-Forwarded-For", "unknown")
            user_agent = headers.get("User-Agent", "streamlit-client")

    except Exception:
        pass

    return ip_address, user_agent


def do_login(username: str, password: str) -> None:
    username = (username or "").strip().lower()

    allowed, msg = check_login_rate(username)

    if not allowed:
        st.error(msg)

        try:
            record_login_event(
                username=username,
                ip_address="rate_limited",
                user_agent="blocked",
                success=False,
            )
        except Exception:
            pass

        return

    ok, msg, user = verify_login(username, password)
    ip_address, user_agent = client_meta()

    try:
        record_login_event(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=ok,
        )
    except Exception:
        pass

    if ok and user:
        sync_session_user(user)
        st.session_state.page = "home"
        st.rerun()

    st.error(msg)


def do_register(username: str, email: str, password: str, captcha: int) -> None:
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()

    result = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)

    if not is_valid_username(username):
        st.error("Ungültiger Username.")
        return

    if not is_valid_email(email):
        st.error("Ungültige Email.")
        return

    if len(password or "") < 6:
        st.error("Passwort muss mindestens 6 Zeichen haben.")
        return

    if int(captcha or 0) != result:
        st.error("Captcha falsch.")
        refresh_captcha()
        return

    ok, msg = create_user(username=username, email=email, password=password)

    if ok:
        st.success("Account erstellt. Du kannst dich jetzt einloggen.")
        refresh_captcha()
    else:
        st.error(msg)


def social_login(provider: str) -> None:
    st.info(f"{provider} OAuth ist vorbereitet. Die echte API-Anbindung kommt danach.")


def auth_css() -> None:
    st.markdown(
        """
<style>
#MainMenu,
header,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at 18% 8%, rgba(168,85,247,.20), transparent 26%),
        radial-gradient(circle at 84% 14%, rgba(96,165,250,.14), transparent 28%),
        linear-gradient(135deg,#050816 0%,#090b1f 48%,#050711 100%) !important;
}

.main .block-container {
    max-width: 980px !important;
    padding-top: 58px !important;
    padding-bottom: 60px !important;
}

.auth-wrap {
    max-width: 840px;
    margin: 0 auto;
}

.auth-top {
    text-align: center;
    margin-bottom: 24px;
}

.auth-logo {
    width: 54px;
    height: 54px;
    border-radius: 19px;
    margin: 0 auto 13px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.30), transparent 34%),
        linear-gradient(135deg,#7c3aed,#2563eb);
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    box-shadow: 0 0 36px rgba(168,85,247,.34);
}

.auth-title {
    font-size: 44px;
    line-height: .96;
    font-weight: 1000;
    letter-spacing: -2.4px;
    background: linear-gradient(135deg,#ffe7a3,#c084fc,#60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.auth-sub {
    margin-top: 10px;
    color: #cbd5e1 !important;
    font-size: 15px;
    font-weight: 750;
}

.auth-card {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.16), transparent 34%),
        linear-gradient(145deg,rgba(13,10,31,.96),rgba(6,7,18,.99));
    border: 1px solid rgba(168,85,247,.22);
    border-radius: 30px;
    padding: 30px;
    box-shadow:
        0 24px 80px rgba(0,0,0,.38),
        inset 0 1px 0 rgba(255,255,255,.04);
}

.auth-social {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 10px;
    margin-bottom: 18px;
}

.auth-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 18px 0;
    color: #64748b !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.auth-divider:before,
.auth-divider:after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(168,85,247,.18);
}

.auth-foot {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 10px;
    margin-top: 18px;
}

.auth-foot-card {
    border: 1px solid rgba(168,85,247,.14);
    background: rgba(15,23,42,.36);
    border-radius: 18px;
    padding: 13px;
    text-align: center;
    color: #cbd5e1 !important;
    font-size: 12px;
    font-weight: 850;
}

.stTextInput input,
.stNumberInput input {
    background: rgba(14,10,28,.96) !important;
    border: 1px solid rgba(168,85,247,.30) !important;
    color: #ffe7a3 !important;
    -webkit-text-fill-color: #ffe7a3 !important;
    border-radius: 16px !important;
    min-height: 50px !important;
    font-weight: 800 !important;
}

.stTextInput input::placeholder {
    color: rgba(255,231,163,.42) !important;
}

.stButton > button {
    min-height: 50px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(168,85,247,.34) !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.22), transparent 34%),
        linear-gradient(145deg, rgba(36,8,56,.98), rgba(12,3,25,.98)) !important;
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
    box-shadow: 0 0 28px rgba(168,85,247,.20);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 34px rgba(168,85,247,.30);
    border-color: rgba(255,231,163,.34) !important;
}

[data-testid="stTabs"] button {
    color: #cbd5e1 !important;
    font-weight: 900 !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffe7a3 !important;
}

@media(max-width:800px) {
    .main .block-container {
        padding-top: 32px !important;
    }

    .auth-title {
        font-size: 34px;
    }

    .auth-social,
    .auth-foot {
        grid-template-columns: 1fr;
    }

    .auth-card {
        padding: 22px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_social_buttons() -> None:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Gmail", width="stretch", key="oauth_gmail"):
            social_login("Gmail")

    with c2:
        if st.button("Instagram", width="stretch", key="oauth_instagram"):
            social_login("Instagram")

    with c3:
        if st.button("TikTok", width="stretch", key="oauth_tiktok"):
            social_login("TikTok")


def render_auth() -> None:
    ensure_captcha()
    auth_css()

    st.markdown(
        """
<div class="auth-wrap">
    <div class="auth-top">
        <div class="auth-logo">M</div>
        <div class="auth-title">Welcome to MaByte</div>
        <div class="auth-sub">Creator OS für Reels, Automationen und AI Workflows.</div>
    </div>
    <div class="auth-card">
""",
        unsafe_allow_html=True,
    )

    render_social_buttons()

    st.markdown('<div class="auth-divider">Account Login</div>', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Login", "Registrieren"])

    with tab_login:
        login_user = st.text_input(
            "Username",
            placeholder="dein username",
            key="login_user",
        )

        login_pw = st.text_input(
            "Passwort",
            type="password",
            placeholder="dein Passwort",
            key="login_pw",
        )

        if st.button("Einloggen", width="stretch", key="btn_login"):
            do_login(login_user, login_pw)

    with tab_register:
        reg_user = st.text_input(
            "Username",
            placeholder="z.B. creator123",
            key="reg_user",
        )

        reg_email = st.text_input(
            "Email",
            placeholder="name@email.com",
            key="reg_email",
        )

        reg_pw = st.text_input(
            "Passwort",
            type="password",
            placeholder="mindestens 6 Zeichen",
            key="reg_pw",
        )

        captcha = st.number_input(
            f"{st.session_state.captcha_a} + {st.session_state.captcha_b}",
            min_value=0,
            max_value=20,
            step=1,
            key="reg_captcha",
        )

        if st.button("Account erstellen", width="stretch", key="btn_register"):
            do_register(reg_user, reg_email, reg_pw, captcha)

    st.markdown(
        """
        <div class="auth-foot">
            <div class="auth-foot-card">Reels Studio</div>
            <div class="auth-foot-card">Social Automation</div>
            <div class="auth-foot-card">Football AI</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )