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
:root {
    --mb-gold: #ffe7a3;
    --mb-soft: #f8e7b0;
    --mb-purple: #a855f7;
    --mb-violet: #7c3aed;
    --mb-blue: #60a5fa;
    --mb-muted: #94a3b8;
    --mb-line: rgba(168, 85, 247, .20);
    --mb-surface: rgba(12, 10, 28, .94);
}

.custom-topbar,
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"] {
    display: none !important;
}

.stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 20% 0%, rgba(168,85,247,.16), transparent 34%),
        radial-gradient(circle at 80% 10%, rgba(96,165,250,.10), transparent 32%),
        linear-gradient(180deg, #050816 0%, #070b1a 55%, #050711 100%) !important;
}

section.main .block-container {
    max-width: 920px !important;
    padding: 32px 20px 48px 20px !important;
}

section.main [data-testid="stVerticalBlock"] {
    gap: .45rem !important;
}

section.main [data-testid="stHorizontalBlock"] {
    gap: 1.25rem !important;
    align-items: center !important;
}

/* ── Brand panel (links) ── */
.mb-auth-brand {
    padding: 8px 4px;
}

.mb-auth-logo img {
    max-width: 168px;
    display: block;
    margin-bottom: 14px;
    filter: drop-shadow(0 8px 24px rgba(168,85,247,.22));
}

.mb-auth-logo-fallback {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--mb-violet), #2563eb);
    color: var(--mb-gold);
    font-size: 22px;
    font-weight: 900;
    margin-bottom: 14px;
    box-shadow: 0 0 28px rgba(168,85,247,.30);
}

.mb-auth-kicker {
    color: var(--mb-purple) !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .20em;
    text-transform: uppercase;
    margin: 0 0 8px 0;
}

.mb-auth-headline {
    font-size: clamp(26px, 2.8vw, 36px);
    line-height: 1.08;
    font-weight: 900;
    letter-spacing: -1px;
    margin: 0 0 10px 0;
    background: linear-gradient(135deg, var(--mb-gold) 0%, #e9d5ff 50%, var(--mb-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-auth-desc {
    color: var(--mb-muted) !important;
    font-size: 14px;
    line-height: 1.55;
    font-weight: 500;
    margin: 0 0 18px 0;
}

.mb-auth-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.mb-auth-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(168,85,247,.10);
    border: 1px solid var(--mb-line);
    color: #e2e8f0 !important;
    font-size: 12px;
    font-weight: 700;
}

.mb-auth-pill em {
    font-style: normal;
    color: var(--mb-gold) !important;
}

/* ── Login card (rechts) ── */
section.main div[data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.12), transparent 42%),
        linear-gradient(165deg, rgba(14,10,32,.98), rgba(6,7,18,.99)) !important;
    border: 1px solid var(--mb-line) !important;
    border-radius: 22px !important;
    padding: 22px 20px 16px 20px !important;
    box-shadow:
        0 20px 50px rgba(0,0,0,.35),
        inset 0 1px 0 rgba(255,255,255,.04) !important;
}

.mb-auth-card-top {
    text-align: center;
    margin-bottom: 4px;
}

.mb-auth-card-top h2 {
    color: #fff !important;
    font-size: 20px;
    font-weight: 900;
    margin: 0 0 4px 0;
    letter-spacing: -.3px;
}

.mb-auth-card-top p {
    color: var(--mb-muted) !important;
    font-size: 12px;
    margin: 0 0 10px 0;
    font-weight: 500;
}

/* Segmented control */
section.main [data-testid="stSegmentedControl"] {
    margin: 0 0 12px 0 !important;
    background: rgba(15,23,42,.65) !important;
    border: 1px solid var(--mb-line) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

section.main [data-testid="stSegmentedControl"] button {
    font-weight: 800 !important;
    font-size: 13px !important;
    background: transparent !important;
    color: var(--mb-muted) !important;
    border: none !important;
    border-radius: 9px !important;
    min-height: 36px !important;
}

section.main [data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: linear-gradient(135deg, var(--mb-violet), #2563eb) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(124,58,237,.30) !important;
}

/* Inputs */
section.main .stTextInput label,
section.main .stNumberInput label,
section.main .stTextInput p,
section.main .stNumberInput p {
    color: var(--mb-soft) !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    margin-bottom: 2px !important;
}

section.main .stTextInput input,
section.main .stNumberInput input {
    background: rgba(8,12,28,.92) !important;
    border: 1px solid var(--mb-line) !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    border-radius: 12px !important;
    min-height: 42px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 8px 14px !important;
}

section.main .stTextInput input:focus,
section.main .stNumberInput input:focus {
    border-color: rgba(255,231,163,.35) !important;
    box-shadow: 0 0 0 2px rgba(168,85,247,.18) !important;
}

section.main .stTextInput input::placeholder {
    color: #64748b !important;
}

section.main [data-testid="stForm"] {
    margin-top: -4px;
}

section.main [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: .35rem !important;
}

/* Primary button */
section.main .stFormSubmitButton > button,
section.main .stButton > button[kind="primary"] {
    min-height: 44px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,231,163,.20) !important;
    background: linear-gradient(135deg, var(--mb-violet) 0%, #2563eb 100%) !important;
    color: #fff !important;
    font-weight: 900 !important;
    font-size: 14px !important;
    box-shadow: 0 8px 24px rgba(124,58,237,.26) !important;
    margin-top: 4px !important;
}

section.main .stFormSubmitButton > button:hover,
section.main .stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 28px rgba(124,58,237,.34) !important;
}

/* Social buttons */
section.main .stButton > button[kind="secondary"] {
    min-height: 36px !important;
    border-radius: 10px !important;
    background: rgba(168,85,247,.08) !important;
    border: 1px solid var(--mb-line) !important;
    color: #cbd5e1 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    padding: 0 8px !important;
}

section.main .stButton > button {
    width: 100% !important;
}

.mb-auth-divider {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 10px 0 6px 0;
    color: #64748b !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.mb-auth-divider::before,
.mb-auth-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--mb-line);
}

.mb-auth-foot {
    text-align: center;
    color: #64748b !important;
    font-size: 10px;
    line-height: 1.5;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(168,85,247,.10);
}

.mb-auth-foot strong {
    color: var(--mb-gold) !important;
    font-weight: 700;
}

@media (max-width: 768px) {
    section.main .block-container {
        padding: 20px 14px 36px 14px !important;
    }

    .mb-auth-brand {
        text-align: center;
        margin-bottom: 8px;
    }

    .mb-auth-logo img,
    .mb-auth-logo-fallback {
        margin-left: auto;
        margin-right: auto;
    }

    .mb-auth-pills {
        justify-content: center;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def brand_panel_html() -> str:
    if WORDMARK.exists():
        src = img_base64(WORDMARK)
        logo = f'<div class="mb-auth-logo"><img src="data:image/png;base64,{src}" alt="{html.escape(APP_NAME)}"></div>'
    else:
        logo = f'<div class="mb-auth-logo"><div class="mb-auth-logo-fallback">{html.escape(APP_NAME[:1])}</div></div>'

    tagline = html.escape(APP_TAGLINE)
    desc = html.escape(APP_POSITIONING)

    return f"""
<div class="mb-auth-brand">
    {logo}
    <p class="mb-auth-kicker">{html.escape(APP_NAME)} · Creator OS</p>
    <h1 class="mb-auth-headline">{tagline}</h1>
    <p class="mb-auth-desc">{desc}</p>
    <div class="mb-auth-pills">
        <span class="mb-auth-pill"><em>🎬</em> Reels</span>
        <span class="mb-auth-pill"><em>⚡</em> Automations</span>
        <span class="mb-auth-pill"><em>🤖</em> AI Chat</span>
        <span class="mb-auth-pill"><em>⚽</em> Football</span>
    </div>
</div>
"""


def card_intro(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="mb-auth-card-top">
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


def render_social_row() -> None:
    st.markdown('<div class="mb-auth-divider">Social Login</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        if st.button("Google", key="oauth_gmail", type="secondary", width="stretch"):
            social_login("Google")
    with c2:
        if st.button("Instagram", key="oauth_instagram", type="secondary", width="stretch"):
            social_login("Instagram")
    with c3:
        if st.button("TikTok", key="oauth_tiktok", type="secondary", width="stretch"):
            social_login("TikTok")


def render_login_form() -> None:
    card_intro("Willkommen zurück", "Melde dich an und starte deine Workflows.")

    with st.form("login_form", clear_on_submit=False, border=False):
        user = st.text_input("Username", placeholder="dein username")
        pw = st.text_input("Passwort", type="password", placeholder="••••••••")
        if st.form_submit_button("Einloggen", type="primary", width="stretch"):
            do_login(user, pw)


def render_register_form() -> None:
    card_intro("Account erstellen", "Kostenlos starten — jederzeit upgraden.")

    with st.form("register_form", clear_on_submit=False, border=False):
        user = st.text_input("Username", placeholder="z.B. creator123")
        email = st.text_input("Email", placeholder="name@email.com")
        pw = st.text_input("Passwort", type="password", placeholder="min. 6 Zeichen")

        cap_col, ref_col = st.columns([0.84, 0.16], gap="small")
        with cap_col:
            captcha = st.number_input(
                f"{st.session_state.captcha_a} + {st.session_state.captcha_b} = ?",
                min_value=0,
                max_value=20,
                step=1,
            )
        with ref_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            refresh = st.form_submit_button("↻")

        submitted = st.form_submit_button("Account erstellen", type="primary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_register(user, email, pw, captcha)


def render_auth() -> None:
    ensure_captcha()
    auth_css()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    brand_col, login_col = st.columns([1, 1], gap="medium")

    with brand_col:
        st.markdown(brand_panel_html(), unsafe_allow_html=True)

    with login_col:
        with st.container(border=True):
            mode = render_mode_switch()
            st.session_state.auth_mode = mode

            if mode == "register":
                render_register_form()
            else:
                render_login_form()

            render_social_row()

            st.markdown(
                """
<div class="mb-auth-foot">
    <strong>MaByte</strong> · Sicherer Zugang · Token-System · Support Inbox
</div>
""",
                unsafe_allow_html=True,
            )
