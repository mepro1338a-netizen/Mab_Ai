import random

import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_POSITIONING
from database import create_user, verify_login, record_login_event
from security import is_valid_username, is_valid_email, check_login_rate
from ui_core import sync_session_user, img_base64, WORDMARK


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
        st.session_state.auth_mode = "login"
        refresh_captcha()
    else:
        st.error(msg)


def social_login(provider: str) -> None:
    st.info(f"{provider} OAuth ist vorbereitet. Die echte API-Anbindung kommt danach.")


def auth_css() -> None:
    st.markdown(
        """
<style>
.custom-topbar {
    display: none !important;
}

#MainMenu,
header,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at 12% 18%, rgba(168,85,247,.22), transparent 28%),
        radial-gradient(circle at 88% 12%, rgba(96,165,250,.16), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(124,58,237,.12), transparent 40%),
        linear-gradient(160deg, #030712 0%, #070b1a 45%, #050711 100%) !important;
}

.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

.auth-shell {
    min-height: 100vh;
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
}

.auth-hero {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 56px 56px 56px 64px;
    overflow: hidden;
    border-right: 1px solid rgba(255,255,255,.06);
}

.auth-hero:before,
.auth-hero:after {
    content: "";
    position: absolute;
    border-radius: 999px;
    filter: blur(60px);
    pointer-events: none;
}

.auth-hero:before {
    width: 320px;
    height: 320px;
    top: 8%;
    left: -80px;
    background: rgba(168,85,247,.28);
}

.auth-hero:after {
    width: 260px;
    height: 260px;
    bottom: 10%;
    right: 8%;
    background: rgba(96,165,250,.20);
}

.auth-hero-inner {
    position: relative;
    z-index: 1;
    max-width: 560px;
}

.auth-brand-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 28px;
}

.auth-brand-mark {
    width: 58px;
    height: 58px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.32), transparent 36%),
        linear-gradient(135deg, #7c3aed, #2563eb);
    color: #ffe7a3 !important;
    font-size: 26px;
    font-weight: 1000;
    box-shadow: 0 0 40px rgba(168,85,247,.36);
}

.auth-brand-wordmark img {
    max-width: 220px;
    width: 100%;
    display: block;
}

.auth-kicker {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .22em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.auth-hero-title {
    font-size: clamp(38px, 4vw, 56px);
    line-height: .98;
    font-weight: 1000;
    letter-spacing: -2.6px;
    background: linear-gradient(135deg, #ffe7a3 0%, #e9d5ff 45%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
}

.auth-hero-text {
    color: #cbd5e1 !important;
    font-size: 17px;
    line-height: 1.65;
    font-weight: 650;
    max-width: 520px;
}

.auth-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 34px;
}

.auth-feature {
    background: rgba(15,23,42,.42);
    border: 1px solid rgba(168,85,247,.16);
    border-radius: 20px;
    padding: 18px 18px 16px 18px;
    backdrop-filter: blur(12px);
}

.auth-feature-icon {
    font-size: 22px;
    margin-bottom: 10px;
}

.auth-feature-title {
    color: #ffe7a3 !important;
    font-size: 15px;
    font-weight: 1000;
    margin-bottom: 6px;
}

.auth-feature-desc {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.45;
    font-weight: 650;
}

.auth-panel {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 32px;
}

.auth-card {
    width: min(100%, 460px);
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.14), transparent 36%),
        linear-gradient(160deg, rgba(13,10,31,.97), rgba(6,7,18,.99));
    border: 1px solid rgba(168,85,247,.22);
    border-radius: 32px;
    padding: 34px 32px 28px 32px;
    box-shadow:
        0 28px 90px rgba(0,0,0,.42),
        inset 0 1px 0 rgba(255,255,255,.05);
}

.auth-card-title {
    color: #ffffff !important;
    font-size: 28px;
    font-weight: 1000;
    letter-spacing: -.8px;
    margin-bottom: 6px;
}

.auth-card-sub {
    color: #94a3b8 !important;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 22px;
}

.auth-mode-wrap {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    padding: 6px;
    border-radius: 18px;
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(168,85,247,.14);
    margin-bottom: 22px;
}

.auth-mode-wrap .stButton > button {
    min-height: 44px !important;
    border-radius: 14px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #94a3b8 !important;
    font-weight: 900 !important;
    box-shadow: none !important;
}

.auth-mode-wrap .stButton > button:hover {
    color: #ffe7a3 !important;
    border-color: rgba(168,85,247,.24) !important;
    background: rgba(168,85,247,.10) !important;
    transform: none !important;
}

.auth-mode-wrap .mode-active .stButton > button {
    background:
        linear-gradient(135deg, rgba(124,58,237,.92), rgba(37,99,235,.88)) !important;
    color: #ffffff !important;
    border-color: rgba(255,231,163,.24) !important;
    box-shadow: 0 0 24px rgba(168,85,247,.28) !important;
}

.auth-social-label {
    color: #64748b !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .16em;
    text-transform: uppercase;
    text-align: center;
    margin: 4px 0 12px 0;
}

.auth-social-row .stButton > button {
    min-height: 46px !important;
    border-radius: 14px !important;
    background: rgba(15,23,42,.72) !important;
    border: 1px solid rgba(168,85,247,.18) !important;
    color: #e2e8f0 !important;
    font-weight: 850 !important;
    font-size: 13px !important;
    box-shadow: none !important;
}

.auth-social-row .stButton > button:hover {
    border-color: rgba(255,231,163,.28) !important;
    background: rgba(168,85,247,.12) !important;
    transform: translateY(-1px) !important;
}

.auth-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 20px 0 18px 0;
    color: #64748b !important;
    font-size: 11px;
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

.auth-form label,
.auth-form .stMarkdown p {
    color: #cbd5e1 !important;
    font-weight: 800 !important;
    font-size: 13px !important;
}

.auth-form .stTextInput input,
.auth-form .stNumberInput input {
    background: rgba(8,12,28,.96) !important;
    border: 1px solid rgba(168,85,247,.24) !important;
    color: #ffe7a3 !important;
    -webkit-text-fill-color: #ffe7a3 !important;
    border-radius: 16px !important;
    min-height: 50px !important;
    font-weight: 750 !important;
}

.auth-form .stTextInput input:focus,
.auth-form .stNumberInput input:focus {
    border-color: rgba(255,231,163,.38) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,.16) !important;
}

.auth-form .stTextInput input::placeholder {
    color: rgba(148,163,184,.72) !important;
}

.auth-primary .stButton > button {
    min-height: 52px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,231,163,.28) !important;
    background:
        radial-gradient(circle at top left, rgba(255,231,163,.18), transparent 34%),
        linear-gradient(135deg, #7c3aed 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    font-weight: 1000 !important;
    font-size: 16px !important;
    box-shadow: 0 12px 36px rgba(124,58,237,.32) !important;
}

.auth-primary .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 16px 42px rgba(124,58,237,.40) !important;
}

.auth-captcha-row .stButton > button {
    min-height: 50px !important;
    border-radius: 16px !important;
    background: rgba(15,23,42,.82) !important;
    border: 1px solid rgba(168,85,247,.20) !important;
    color: #cbd5e1 !important;
    font-weight: 900 !important;
    box-shadow: none !important;
}

.auth-footnote {
    margin-top: 18px;
    text-align: center;
    color: #64748b !important;
    font-size: 12px;
    font-weight: 700;
    line-height: 1.5;
}

@media (max-width: 980px) {
    .auth-shell {
        grid-template-columns: 1fr;
    }

    .auth-hero {
        padding: 36px 24px 28px 24px;
        border-right: none;
        border-bottom: 1px solid rgba(255,255,255,.06);
    }

    .auth-feature-grid {
        grid-template-columns: 1fr;
    }

    .auth-panel {
        padding: 24px 18px 40px 18px;
    }

    .auth-card {
        padding: 26px 22px 22px 22px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_brand_mark() -> str:
    if WORDMARK.exists():
        src = img_base64(WORDMARK)
        return f'<div class="auth-brand-wordmark"><img src="data:image/png;base64,{src}" alt="{APP_NAME}"></motion>'
    return f'<div class="auth-brand-mark">{APP_NAME[:1]}</motion>'


def render_hero() -> None:
    brand = render_brand_mark()

    st.markdown(
        f"""
<div class="auth-shell">
    <section class="auth-hero">
        <div class="auth-hero-inner">
            <div class="auth-brand-row">
                {brand}
            </motion>
            <div class="auth-kicker">Creator Operating System</motion>
            <div class="auth-hero-title">{APP_TAGLINE}</motion>
            <div class="auth-hero-text">{APP_POSITIONING}</motion>
            <div class="auth-feature-grid">
                <div class="auth-feature">
                    <div class="auth-feature-icon">🎬</motion>
                    <div class="auth-feature-title">Reels Studio</motion>
                    <div class="auth-feature-desc">Kurze AI-Videos in Minuten statt Stunden.</motion>
                </motion>
                <div class="auth-feature">
                    <div class="auth-feature-icon">⚡</motion>
                    <div class="auth-feature-title">Automations</motion>
                    <div class="auth-feature-desc">Workflows, die im Hintergrund für dich laufen.</motion>
                </motion>
                <div class="auth-feature">
                    <div class="auth-feature-icon">🤖</motion>
                    <div class="auth-feature-title">AI Assistant</motion>
                    <div class="auth-feature-desc">Chat, Coding und Content in einem System.</motion>
                </motion>
                <div class="auth-feature">
                    <div class="auth-feature-icon">⚽</motion>
                    <div class="auth-feature-title">Football AI</motion>
                    <div class="auth-feature-desc">Analysen und Insights für deine Football-Projekte.</motion>
                </motion>
            </motion>
        </motion>
    </section>
    <section class="auth-panel">
        <div class="auth-card">
""",
        unsafe_allow_html=True,
    )


def render_mode_switch() -> None:
    mode = st.session_state.get("auth_mode", "login")
    login_class = "mode-active" if mode == "login" else ""
    register_class = "mode-active" if mode == "register" else ""

    st.markdown('<div class="auth-mode-wrap">', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="{login_class}">', unsafe_allow_html=True)
        if st.button("Anmelden", key="auth_mode_login", width="stretch"):
            st.session_state.auth_mode = "login"
            st.rerun()
        st.markdown("</motion>", unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="{register_class}">', unsafe_allow_html=True)
        if st.button("Registrieren", key="auth_mode_register", width="stretch"):
            st.session_state.auth_mode = "register"
            st.rerun()
        st.markdown("</motion>", unsafe_allow_html=True)

    st.markdown("</motion>", unsafe_allow_html=True)


def render_social_buttons() -> None:
    st.markdown('<div class="auth-social-label">Oder weiter mit</motion>', unsafe_allow_html=True)
    st.markdown('<div class="auth-social-row">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Google", width="stretch", key="oauth_gmail"):
            social_login("Google")
    with c2:
        if st.button("Instagram", width="stretch", key="oauth_instagram"):
            social_login("Instagram")
    with c3:
        if st.button("TikTok", width="stretch", key="oauth_tiktok"):
            social_login("TikTok")

    st.markdown("</motion>", unsafe_allow_html=True)


def render_login_form() -> None:
    st.markdown(
        """
<div class="auth-card-title">Willkommen zurück</div>
<div class="auth-card-sub">Melde dich an, um dein Creator OS zu öffnen.</motion>
<div class="auth-form">
""",
        unsafe_allow_html=True,
    )

    login_user = st.text_input(
        "Username",
        placeholder="dein username",
        key="login_user",
        label_visibility="visible",
    )
    login_pw = st.text_input(
        "Passwort",
        type="password",
        placeholder="••••••••",
        key="login_pw",
        label_visibility="visible",
    )

    st.markdown('<div class="auth-primary">', unsafe_allow_html=True)
    if st.button("Einloggen", width="stretch", key="btn_login"):
        do_login(login_user, login_pw)
    st.markdown("</motion>", unsafe_allow_html=True)
    st.markdown("</motion>", unsafe_allow_html=True)


def render_register_form() -> None:
    st.markdown(
        """
<div class="auth-card-title">Account erstellen</motion>
<div class="auth-card-sub">Starte kostenlos und upgrade später auf Premium.</motion>
<div class="auth-form">
""",
        unsafe_allow_html=True,
    )

    reg_user = st.text_input(
        "Username",
        placeholder="z.B. creator123",
        key="reg_user",
        label_visibility="visible",
    )
    reg_email = st.text_input(
        "Email",
        placeholder="name@email.com",
        key="reg_email",
        label_visibility="visible",
    )
    reg_pw = st.text_input(
        "Passwort",
        type="password",
        placeholder="mindestens 6 Zeichen",
        key="reg_pw",
        label_visibility="visible",
    )

    st.markdown('<div class="auth-captcha-row">', unsafe_allow_html=True)
    cap_col, refresh_col = st.columns([0.78, 0.22])
    with cap_col:
        captcha = st.number_input(
            f"Sicherheitsfrage: {st.session_state.captcha_a} + {st.session_state.captcha_b}",
            min_value=0,
            max_value=20,
            step=1,
            key="reg_captcha",
            label_visibility="visible",
        )
    with refresh_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↻", key="btn_refresh_captcha", width="stretch"):
            refresh_captcha()
            st.rerun()
    st.markdown("</motion>", unsafe_allow_html=True)

    st.markdown('<div class="auth-primary">', unsafe_allow_html=True)
    if st.button("Account erstellen", width="stretch", key="btn_register"):
        do_register(reg_user, reg_email, reg_pw, captcha)
    st.markdown("</motion>", unsafe_allow_html=True)
    st.markdown("</motion>", unsafe_allow_html=True)


def render_auth() -> None:
    ensure_captcha()
    auth_css()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    render_hero()

    render_mode_switch()
    render_social_buttons()
    st.markdown('<div class="auth-divider">Email Login</motion>', unsafe_allow_html=True)

    if st.session_state.auth_mode == "register":
        render_register_form()
    else:
        render_login_form()

    st.markdown(
        """
<div class="auth-footnote">
    Mit dem Login akzeptierst du unsere Nutzungsbedingungen.<br>
    Sicherer Zugang · Token-System · Admin Support Inbox
</motion>
        </motion>
    </section>
</motion>
""",
        unsafe_allow_html=True,
    )
