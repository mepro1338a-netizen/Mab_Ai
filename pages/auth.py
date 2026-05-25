import html
import random

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from database import create_user, record_login_event, verify_login
from security import check_login_rate, record_login_failure, is_valid_email, is_valid_username
from services.session_auth import rotate_session_on_login
from logger import log_auth, log_oauth, user_friendly_error
from oauth_service import (
    auth_url,
    complete_oauth,
    friendly_oauth_error,
    google_oauth_diagnostics,
    google_redirect_uri,
    make_state,
    oauth_state_ready,
    provider_configured,
    verify_state,
)
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
        rotate_session_on_login(user)
        log_auth("login_success", username=username, success=True)
        st.session_state.page = "home"
        st.rerun()

    record_login_failure(username)
    log_auth("login_failed", username=username, success=False)
    st.error(user_friendly_error("auth"))


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


def _set_oauth_notice(level: str, message: str) -> None:
    st.session_state.oauth_notice = (level, message)


def _show_oauth_notice() -> None:
    notice = st.session_state.pop("oauth_notice", None)
    if not notice:
        return
    level, text = notice
    if level == "success":
        st.success(text)
    elif level == "info":
        st.info(text)
    else:
        st.error(text)


def finish_oauth_login(user: dict, *, provider: str) -> None:
    username = str(user.get("username") or "")
    ip_address, user_agent = client_meta()
    try:
        record_login_event(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )
    except Exception:
        pass
    rotate_session_on_login(user)
    log_oauth("oauth_success", provider=provider, success=True, user=username)
    _set_oauth_notice("success", f"Willkommen zurück — eingeloggt via {provider.title()}.")
    st.session_state.page = "home"
    st.rerun()


def handle_oauth_callback() -> bool:
    params = st.query_params

    oauth_error = params.get("error")
    if oauth_error:
        desc = params.get("error_description") or ""
        if isinstance(desc, list):
            desc = desc[0] if desc else ""
        if isinstance(oauth_error, list):
            oauth_error = oauth_error[0] if oauth_error else ""
        _set_oauth_notice("error", friendly_oauth_error(str(oauth_error), str(desc)))
        st.query_params.clear()
        return False

    code = params.get("code")
    state = params.get("state")
    if isinstance(code, list):
        code = code[0] if code else None
    if isinstance(state, list):
        state = state[0] if state else None

    if not code and not state:
        return False

    if not code or not state:
        _set_oauth_notice("error", "OAuth-Antwort unvollständig. Bitte erneut anmelden.")
        st.query_params.clear()
        return False

    provider = verify_state(str(state))
    if not provider:
        log_oauth("oauth_invalid_state", success=False)
        _set_oauth_notice(
            "error",
            "Anmelde-Sitzung abgelaufen oder ungültig. Bitte «Mit Google anmelden» erneut klicken.",
        )
        st.query_params.clear()
        return False

    ok, msg, user = complete_oauth(provider, str(code))
    st.query_params.clear()

    if ok and user:
        finish_oauth_login(user, provider=provider)
        return True

    ip_address, user_agent = client_meta()
    try:
        record_login_event(
            username=str(user.get("username") if user else "oauth"),
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
        )
    except Exception:
        pass

    log_oauth("oauth_failed", provider=provider or "?", success=False)
    _set_oauth_notice("error", user_friendly_error("oauth", msg))
    return False


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

.mb-oauth-google .g-icon {
    width: 18px;
    height: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.mb-oauth-primary {
    margin-bottom: 4px;
}

.mb-oauth-hint {
    color: #64748b !important;
    font-size: 11px;
    line-height: 1.45;
    margin-top: 6px;
    text-align: center;
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


GOOGLE_ICON_SVG = """
<svg class="g-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
</svg>
"""


def oauth_button(provider: str, label: str, icon: str, css_class: str, *, primary: bool = False) -> str:
    if provider_configured(provider):
        state = make_state(provider)
        url = html.escape(auth_url(provider, state), quote=True)
        icon_html = GOOGLE_ICON_SVG if provider == "google" else f'<span class="mb-oauth-icon">{icon}</span>'
        extra = " mb-oauth-primary" if primary else ""
        return (
            f'<a class="mb-oauth-btn {css_class}{extra}" href="{url}" rel="noopener noreferrer">'
            f'{icon_html}{html.escape(label)}</a>'
        )
    title = "OAuth nicht konfiguriert"
    if provider == "google" and not oauth_state_ready():
        title = "OAUTH_STATE_SECRET fehlt"
    icon_html = GOOGLE_ICON_SVG if provider == "google" else f'<span class="mb-oauth-icon">{icon}</span>'
    return (
        f'<span class="mb-oauth-btn {css_class} disabled" title="{html.escape(title)}">'
        f'{icon_html}{html.escape(label)}</span>'
    )


def render_social_row() -> None:
    google_block = oauth_button(
        "google",
        "Mit Google anmelden",
        "",
        "mb-oauth-google",
        primary=True,
    )
    st.markdown(
        f"""
<div class="mb-oauth-grid">
    {google_block}
</div>
<div class="mb-oauth-hint">Sicherer Login · Kein Passwort nötig · Bestehende E-Mail bleibt geschützt</div>
<div class="mb-auth-divider">oder fortfahren mit</div>
<div class="mb-oauth-grid">
    {oauth_button("instagram", "Weiter mit Instagram", "◎", "mb-oauth-instagram")}
    {oauth_button("tiktok", "Weiter mit TikTok", "♪", "mb-oauth-tiktok")}
</div>
""",
        unsafe_allow_html=True,
    )

    if not provider_configured("google"):
        hints = []
        if not oauth_state_ready():
            hints.append("OAUTH_STATE_SECRET")
        hints.append("GOOGLE_CLIENT_ID/SECRET")
        st.caption("Google Login: " + ", ".join(hints) + " in Railway setzen.")

    with st.expander("Google Login funktioniert nicht?", expanded=False):
        diag = google_oauth_diagnostics()
        st.markdown(
            f"""
**Redirect URI (exakt in Google Console eintragen):**  
`{diag["redirect_uri"]}`

**Öffentliche Domain:** `{diag["public_origin"]}`  
**APP_BASE_URL (ENV):** `{diag["app_base_url_env"]}`  
**Status:** {diag["issues"]}
            """
        )
        st.markdown(
            """
1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → OAuth Client **Web application**
2. **Authorized redirect URIs** — exakt die URI oben (oft `https://mabyte.de/`)
3. **Authorized JavaScript origins:** `https://mabyte.de`
4. **OAuth consent screen** → Testing → Testnutzer: deine Gmail hinzufügen
5. Railway: `APP_BASE_URL=https://mabyte.de`
            """
        )


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
    handle_oauth_callback()
    _show_oauth_notice()

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

    st.caption("MaByte Production Beta · Mab AI")
    l1, l2, l3 = st.columns(3)
    with l1:
        if st.button("Datenschutz", key="auth_privacy"):
            st.session_state.page = "privacy"
            st.rerun()
    with l2:
        if st.button("AGB", key="auth_terms"):
            st.session_state.page = "terms"
            st.rerun()
    with l3:
        if st.button("Impressum", key="auth_impressum"):
            st.session_state.page = "impressum"
            st.rerun()

            render_social_row()

            st.markdown(
                """
<div class="mb-auth-foot">
    <strong>MaByte</strong> · Dein Creator OS · Token-System · Support Inbox
</div>
""",
                unsafe_allow_html=True,
            )

