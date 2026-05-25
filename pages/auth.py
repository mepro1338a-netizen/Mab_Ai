import html
import random

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from database import create_user, record_login_event, verify_login
from security import check_login_rate, is_valid_email, is_valid_username
from oauth_service import auth_url, complete_oauth, make_state, provider_configured, verify_state
from ui_core import WORDMARK, img_base64, sync_session_user
from ui.styles import MB_THEME_VARS, inject_css


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


def handle_oauth_callback() -> bool:
    params = st.query_params
    code = params.get("code")
    state = params.get("state")

    if not code or not state:
        return False

    provider = verify_state(state)
    if not provider:
        st.error("OAuth-Sitzung abgelaufen oder ungültig. Bitte erneut versuchen.")
        st.query_params.clear()
        return True

    ok, msg, user = complete_oauth(provider, code)
    st.query_params.clear()

    if ok and user:
        sync_session_user(user)
        st.session_state.page = "home"
        st.rerun()

    st.error(msg)
    return True


def auth_css() -> None:
    inject_css(MB_THEME_VARS + """
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
}

.mb-auth-headline span {
    background: linear-gradient(135deg, var(--mb-gold) 0%, #e9d5ff 50%, var(--mb-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.mb-auth-desc {
    color: var(--mb-muted) !important;
    font-size: 14px;
    line-height: 1.6;
    font-weight: 500;
    margin: 0 0 14px 0;
}

.mb-auth-highlight {
    color: #e2e8f0 !important;
    font-size: 13px;
    line-height: 1.55;
    font-weight: 600;
    margin: 0 0 16px 0;
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(168,85,247,.10);
    border: 1px solid rgba(168,85,247,.18);
}

.mb-auth-highlight strong {
    color: var(--mb-gold) !important;
}

.mb-auth-bullets {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 8px;
}

.mb-auth-bullets li {
    color: #cbd5e1 !important;
    font-size: 13px;
    font-weight: 600;
    padding-left: 18px;
    position: relative;
}

.mb-auth-bullets li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 7px;
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--mb-gold), var(--mb-purple));
    box-shadow: 0 0 8px rgba(168,85,247,.45);
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
    font-size: 19px;
    font-weight: 900;
    margin: 0 0 4px 0;
    letter-spacing: -.2px;
    line-height: 1.25;
}

.mb-auth-card-top p {
    color: var(--mb-muted) !important;
    font-size: 12px;
    margin: 0 0 10px 0;
    font-weight: 500;
}

/* Anmelden / Registrieren Tabs */
.mb-auth-tabs {
    margin-bottom: 16px;
}

.mb-auth-tabs [data-testid="stHorizontalBlock"] {
    gap: 8px !important;
}

/* Tab-Buttons in Auth-Card (erstes Horizontal-Block = Anmelden/Registrieren) */
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type .stButton > button,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button {
    min-height: 42px !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    width: 100% !important;
    box-shadow: none !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[data-testid="stBaseButton-secondary"] {
    background: rgba(168, 85, 247, .08) !important;
    background-color: rgba(168, 85, 247, .08) !important;
    border: 1px solid rgba(168, 85, 247, .24) !important;
    color: #94a3b8 !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 50%, #2563eb 100%) !important;
    background-color: #7c3aed !important;
    border: 1px solid rgba(168, 85, 247, .40) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, .28) !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="tertiary"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[data-testid="stBaseButton-tertiary"] {
    background: rgba(168, 85, 247, .08) !important;
    background-color: rgba(168, 85, 247, .08) !important;
    border: 1px solid rgba(168, 85, 247, .24) !important;
    color: #94a3b8 !important;
}

/* Primary — Einloggen / Account erstellen */
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton > button,
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton button,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFormSubmitButton"] > button,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFormSubmitButton"] button,
section.main div[data-testid="stVerticalBlockBorderWrapper"] form button[kind="primaryFormSubmit"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] form button[data-testid="stBaseButton-primary"] {
    min-height: 46px !important;
    border-radius: 13px !important;
    border: 1px solid rgba(168, 85, 247, .40) !important;
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 45%, #2563eb 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 14px !important;
    box-shadow: 0 10px 28px rgba(124, 58, 237, .32) !important;
    margin-top: 6px !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton > button:hover,
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton button:hover,
section.main div[data-testid="stVerticalBlockBorderWrapper"] form button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg, #a855f7 0%, #8b5cf6 45%, #3b82f6 100%) !important;
    background-color: #8b5cf6 !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 32px rgba(124, 58, 237, .38) !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton > button p,
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton button p {
    color: #ffffff !important;
}

/* Inputs — nur in Auth-Card, keine weißen Ränder */
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] {
    background: transparent !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] > div,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] > div,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] > div > div,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] > div > div,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] fieldset,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] fieldset {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] label,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] label,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] p,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] p {
    color: #cbd5e1 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    margin-bottom: 4px !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] div[data-baseweb="input"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: rgba(6, 10, 24, .96) !important;
    background-color: rgba(6, 10, 24, .96) !important;
    border: 1px solid rgba(168, 85, 247, .38) !important;
    border-radius: 12px !important;
    min-height: 42px !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] input,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] input {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    box-shadow: none !important;
    min-height: 40px !important;
    font-size: 14px !important;
    padding: 8px 14px !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: rgba(168, 85, 247, .60) !important;
    box-shadow: 0 0 0 2px rgba(168, 85, 247, .16) !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] input::placeholder {
    color: #64748b !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] button {
    background: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}

section.main [data-testid="stForm"] {
    margin-top: -4px;
}

section.main [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: .35rem !important;
}

/* OAuth — unter dem Login, SaaS-Stil (gestapelt) */
.mb-oauth-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    margin-top: 2px;
    margin-bottom: 4px;
}

.mb-oauth-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 42px;
    padding: 0 14px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 800;
    text-decoration: none !important;
    border: 1px solid rgba(168, 85, 247, .18);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
    cursor: pointer;
}

.mb-oauth-btn:hover {
    transform: translateY(-1px);
    filter: brightness(1.06);
}

.mb-oauth-btn.disabled {
    opacity: .45;
    cursor: not-allowed;
    pointer-events: none;
    filter: grayscale(.2);
}

.mb-oauth-google {
    background: rgba(255, 255, 255, .96) !important;
    color: #1e293b !important;
    border-color: rgba(255, 255, 255, .12) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, .20);
}

.mb-oauth-instagram {
    background: linear-gradient(135deg, #f58529, #dd2a7b, #8134af) !important;
    color: #fff !important;
    box-shadow: 0 6px 18px rgba(221,42,123,.28);
}

.mb-oauth-tiktok {
    background: linear-gradient(135deg, #0f172a, #111827 60%, #0891b2) !important;
    color: #f0fdfa !important;
    border-color: rgba(45,212,191,.25) !important;
    box-shadow: 0 6px 18px rgba(8,145,178,.22);
}

.mb-oauth-icon {
    font-size: 14px;
    line-height: 1;
}

.mb-auth-divider {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 16px 0 10px 0;
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
    background: rgba(168, 85, 247, .16);
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

    .mb-oauth-grid {
        grid-template-columns: 1fr;
    }
}

/* Letzter Override gegen Streamlit/ui_core auf der Auth-Card */
section.main div[data-testid="stVerticalBlockBorderWrapper"] label,
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p {
    color: #cbd5e1 !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] .stTextInput input,
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stNumberInput input {
    border: none !important;
    background: transparent !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] .stTextInput div[data-baseweb="input"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stNumberInput div[data-baseweb="input"] {
    border: 1px solid rgba(168, 85, 247, .38) !important;
    background: rgba(6, 10, 24, .96) !important;
    box-shadow: none !important;
}
"""
    )


def brand_panel_html() -> str:
    if WORDMARK.exists():
        src = img_base64(WORDMARK)
        logo = f'<div class="mb-auth-logo"><img src="data:image/png;base64,{src}" alt="{html.escape(APP_NAME)}"></div>'
    else:
        logo = f'<div class="mb-auth-logo"><div class="mb-auth-logo-fallback">{html.escape(APP_NAME[:1])}</div></div>'

    tagline = html.escape(APP_TAGLINE)

    return f"""
<div class="mb-auth-brand">
    {logo}
    <p class="mb-auth-kicker">{html.escape(APP_NAME)} · Creator Operating System</p>
    <h1 class="mb-auth-headline"><span>{tagline}</span></h1>
    <p class="mb-auth-desc">
        Baue deine eigenen AI-Videos &amp; Reels, automatisiere deinen Content
        und skaliere deine Creator-Workflows — alles in einem System.
    </p>
    <p class="mb-auth-highlight">
        <strong>Deine Idee → AI Video → Reel → Automation.</strong>
        MaByte macht aus Prompts fertige Shorts und lässt deine Workflows
        im Hintergrund laufen.
    </p>
    <ul class="mb-auth-bullets">
        <li>Eigene Reels &amp; Short-Videos mit AI erstellen</li>
        <li>Video-Studio für schnelle, professionelle Clips</li>
        <li>Automationen die posten, planen &amp; skalieren</li>
        <li>Chat, Coding &amp; Content — vereint in MaByte</li>
    </ul>
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
    tab_login, tab_register = st.columns(2, gap="small")

    with tab_login:
        if st.button("Anmelden", key="auth_tab_login", width="stretch", type="primary" if mode == "login" else "tertiary"):
            st.session_state.auth_mode = "login"
            st.rerun()

    with tab_register:
        if st.button("Registrieren", key="auth_tab_register", width="stretch", type="primary" if mode == "register" else "tertiary"):
            st.session_state.auth_mode = "register"
            st.rerun()

    return mode


def oauth_button(provider: str, label: str, icon: str, css_class: str) -> str:
    if provider_configured(provider):
        url = html.escape(auth_url(provider, make_state(provider)), quote=True)
        return (
            f'<a class="mb-oauth-btn {css_class}" href="{url}">'
            f'<span class="mb-oauth-icon">{icon}</span>{html.escape(label)}</a>'
        )
    return (
        f'<span class="mb-oauth-btn {css_class} disabled" title="API Key fehlt">'
        f'<span class="mb-oauth-icon">{icon}</span>{html.escape(label)}</span>'
    )


def render_social_row() -> None:
    st.markdown(
        f"""
<div class="mb-auth-divider">oder fortfahren mit</div>
<div class="mb-oauth-grid">
    {oauth_button("google", "Weiter mit Google", "G", "mb-oauth-google")}
    {oauth_button("instagram", "Weiter mit Instagram", "◎", "mb-oauth-instagram")}
    {oauth_button("tiktok", "Weiter mit TikTok", "♪", "mb-oauth-tiktok")}
</div>
""",
        unsafe_allow_html=True,
    )

    if not any(provider_configured(p) for p in ("google", "instagram", "tiktok")):
        st.caption("OAuth: Trage GOOGLE_CLIENT_ID/SECRET (und optional Meta/TikTok Keys) in Railway ein.")


def render_login_form() -> None:
    card_intro("Herzlich Willkommen auf MaByte", "Melde dich an und starte deine Creator-Workflows.")

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

    if handle_oauth_callback():
        return

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
    <strong>MaByte</strong> · Dein Creator OS · Token-System · Support Inbox
</div>
""",
                unsafe_allow_html=True,
            )

