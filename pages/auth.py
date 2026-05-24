import html
import random

import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_POSITIONING
from database import create_user, record_login_event, verify_login
from security import check_login_rate, is_valid_email, is_valid_username
from ui_core import WORDMARK, img_base64, sync_session_user


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
.custom-topbar,
#MainMenu,
header,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"] {
    display: none !important;
}

.stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 14% 10%, rgba(168,85,247,.18), transparent 32%),
        radial-gradient(circle at 86% 8%, rgba(96,165,250,.12), transparent 30%),
        linear-gradient(165deg, #030712 0%, #070b1a 50%, #050711 100%) !important;
}

.auth-page .main .block-container {
    max-width: 1180px !important;
    padding: 48px 28px 56px 28px !important;
}

.auth-page [data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: 2rem !important;
}

.auth-hero-block {
    padding: 12px 8px 12px 4px;
}

.auth-hero-block * {
    user-select: none;
}

.auth-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 26px;
}

.auth-brand-mark {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 900;
    box-shadow: 0 0 32px rgba(168,85,247,.28);
}

.auth-brand-wordmark img {
    max-width: 200px;
    width: 100%;
    display: block;
}

.auth-kicker {
    color: #c084fc !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin: 0 0 12px 0;
}

.auth-hero-title {
    color: #f8fafc !important;
    font-size: clamp(32px, 3.4vw, 48px);
    line-height: 1.05;
    font-weight: 900;
    letter-spacing: -1.5px;
    margin: 0 0 14px 0;
}

.auth-hero-title span {
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.auth-hero-text {
    color: #94a3b8 !important;
    font-size: 16px;
    line-height: 1.6;
    font-weight: 500;
    margin: 0 0 28px 0;
    max-width: 520px;
}

.auth-features {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.auth-feature {
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(168,85,247,.14);
    border-radius: 16px;
    padding: 16px;
}

.auth-feature strong {
    display: block;
    color: #f1f5f9 !important;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 4px;
}

.auth-feature span {
    color: #94a3b8 !important;
    font-size: 12px;
    line-height: 1.45;
    font-weight: 500;
}

.auth-form-col {
    display: flex;
    align-items: center;
    justify-content: center;
}

.auth-page div[data-testid="stVerticalBlockBorderWrapper"] {
    width: 100%;
    max-width: 440px;
    margin: 0 auto;
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.10), transparent 38%),
        linear-gradient(160deg, rgba(12,10,28,.98), rgba(6,7,18,.99)) !important;
    border: 1px solid rgba(168,85,247,.22) !important;
    border-radius: 28px !important;
    padding: 8px 6px 4px 6px !important;
    box-shadow: 0 24px 70px rgba(0,0,0,.38) !important;
}

.auth-card-head {
    text-align: center;
    padding: 8px 12px 4px 12px;
}

.auth-card-head h2 {
    color: #ffffff !important;
    font-size: 26px;
    font-weight: 900;
    margin: 0 0 6px 0;
    letter-spacing: -.4px;
}

.auth-card-head p {
    color: #94a3b8 !important;
    font-size: 14px;
    margin: 0;
    font-weight: 500;
}

.auth-page [data-testid="stSegmentedControl"] {
    margin: 8px 0 4px 0;
}

.auth-page [data-testid="stSegmentedControl"] button {
    font-weight: 800 !important;
}

.auth-page .stTextInput label,
.auth-page .stNumberInput label {
    color: #cbd5e1 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}

.auth-page .stTextInput input,
.auth-page .stNumberInput input {
    background: rgba(8,12,28,.96) !important;
    border: 1px solid rgba(168,85,247,.22) !important;
    color: #f8fafc !important;
    border-radius: 14px !important;
    min-height: 48px !important;
}

.auth-page .stTextInput input::placeholder {
    color: #64748b !important;
}

.auth-page .stButton > button[kind="primary"],
.auth-page .stFormSubmitButton > button {
    min-height: 50px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,231,163,.22) !important;
    background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 15px !important;
    box-shadow: 0 10px 30px rgba(124,58,237,.28) !important;
}

.auth-page .stButton > button[kind="secondary"] {
    min-height: 44px !important;
    border-radius: 12px !important;
    background: rgba(15,23,42,.7) !important;
    border: 1px solid rgba(168,85,247,.16) !important;
    color: #e2e8f0 !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

.auth-divider-line {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0 2px 0;
    color: #64748b !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.auth-divider-line:before,
.auth-divider-line:after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(168,85,247,.16);
}

.auth-footnote {
    text-align: center;
    color: #64748b !important;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 8px;
    padding: 0 8px 4px 8px;
}

@media (max-width: 900px) {
    .auth-features {
        grid-template-columns: 1fr;
    }

    .auth-page .main .block-container {
        padding: 28px 16px 40px 16px !important;
    }
}
</style>
<div class="auth-page"></div>
""",
        unsafe_allow_html=True,
    )


def brand_html() -> str:
    if WORDMARK.exists():
        src = img_base64(WORDMARK)
        logo = (
            f'<div class="auth-brand-wordmark">'
            f'<img src="data:image/png;base64,{src}" alt="{html.escape(APP_NAME)}">'
            f"</div>"
        )
    else:
        logo = f'<div class="auth-brand-mark">{html.escape(APP_NAME[:1])}</div>'

    return f'<div class="auth-brand">{logo}</div>'


def hero_html() -> str:
    tagline = html.escape(APP_TAGLINE)
    positioning = html.escape(APP_POSITIONING)

    return f"""
<div class="auth-hero-block">
    {brand_html()}
    <p class="auth-kicker">Creator Operating System</p>
    <h1 class="auth-hero-title"><span>{tagline}</span></h1>
    <p class="auth-hero-text">{positioning}</p>
    <div class="auth-features">
        <div class="auth-feature">
            <strong>Reels Studio</strong>
            <span>Kurze AI-Videos in Minuten statt Stunden.</span>
        </div>
        <div class="auth-feature">
            <strong>Automations</strong>
            <span>Workflows, die im Hintergrund für dich laufen.</span>
        </div>
        <div class="auth-feature">
            <strong>AI Assistant</strong>
            <span>Chat, Coding und Content in einem System.</span>
        </div>
        <div class="auth-feature">
            <strong>Football AI</strong>
            <span>Analysen und Insights für deine Projekte.</span>
        </div>
    </div>
</div>
"""


def card_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="auth-card-head">
    <h2>{html.escape(title)}</h2>
    <p>{html.escape(subtitle)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_mode_switch() -> str:
    mode = st.session_state.get("auth_mode", "login")
    labels = {"login": "Anmelden", "register": "Registrieren"}
    reverse = {v: k for k, v in labels.items()}

    selected = st.segmented_control(
        "Modus",
        options=list(labels.values()),
        default=labels[mode],
        label_visibility="collapsed",
        key="auth_mode_segment",
    )

    return reverse.get(selected, "login")


def render_social_buttons() -> None:
    st.markdown('<div class="auth-divider-line">oder weiter mit</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Google", width="stretch", key="oauth_gmail", type="secondary"):
            social_login("Google")
    with c2:
        if st.button("Instagram", width="stretch", key="oauth_instagram", type="secondary"):
            social_login("Instagram")
    with c3:
        if st.button("TikTok", width="stretch", key="oauth_tiktok", type="secondary"):
            social_login("TikTok")


def render_login_form() -> None:
    card_header("Willkommen zurück", "Melde dich an und öffne dein Creator OS.")

    with st.form("login_form", clear_on_submit=False, border=False):
        login_user = st.text_input("Username", placeholder="dein username")
        login_pw = st.text_input("Passwort", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Einloggen", type="primary", width="stretch")

    if submitted:
        do_login(login_user, login_pw)


def render_register_form() -> None:
    card_header("Account erstellen", "Kostenlos starten — Premium jederzeit upgraden.")

    with st.form("register_form", clear_on_submit=False, border=False):
        reg_user = st.text_input("Username", placeholder="z.B. creator123")
        reg_email = st.text_input("Email", placeholder="name@email.com")
        reg_pw = st.text_input("Passwort", type="password", placeholder="mindestens 6 Zeichen")

        cap_col, refresh_col = st.columns([0.82, 0.18])
        with cap_col:
            captcha = st.number_input(
                f"Sicherheitsfrage: {st.session_state.captcha_a} + {st.session_state.captcha_b}",
                min_value=0,
                max_value=20,
                step=1,
            )
        with refresh_col:
            st.markdown("<br>", unsafe_allow_html=True)
            refresh = st.form_submit_button("↻", width="stretch")

        submitted = st.form_submit_button("Account erstellen", type="primary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()

    if submitted:
        do_register(reg_user, reg_email, reg_pw, captcha)


def render_auth() -> None:
    ensure_captcha()
    auth_css()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    hero_col, form_col = st.columns([1.05, 0.95], gap="large")

    with hero_col:
        st.markdown(hero_html(), unsafe_allow_html=True)

    with form_col:
        st.markdown('<div class="auth-form-col">', unsafe_allow_html=True)

        with st.container(border=True):
            mode = render_mode_switch()
            st.session_state.auth_mode = mode

            st.markdown('<div class="auth-divider-line">Zugangsdaten</div>', unsafe_allow_html=True)

            if mode == "register":
                render_register_form()
            else:
                render_login_form()

            render_social_buttons()

            st.markdown(
                """
<div class="auth-footnote">
    Sicherer Zugang · Token-System · Support Inbox<br>
    Mit dem Login akzeptierst du unsere Nutzungsbedingungen.
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)
