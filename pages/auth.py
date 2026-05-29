import html
import random

import streamlit as st

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
from ui_core import sync_session_user
from ui.auth_premium import auth_styles_bundle, brand_panel_html, card_hero_html
from ui.styles import inject_css


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
        from pages.social_oauth import resume_pending_social_connect

        if resume_pending_social_connect():
            return
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
    from pages.social_oauth import resume_pending_social_connect

    if resume_pending_social_connect():
        return
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
    inject_css(
        auth_styles_bundle()
        + """
section.main [data-testid="stVerticalBlock"] { gap: .45rem !important; }
section.main [data-testid="stHorizontalBlock"] {
    gap: 1.25rem !important;
    align-items: stretch !important;
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
    background: #27272a !important;
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[data-testid="stBaseButton-primary"] {
    background: #7c3aed !important;
    background-color: #7c3aed !important;
    border: 1px solid #6d28d9 !important;
    color: #ffffff !important;
    box-shadow: none !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="tertiary"],
section.main div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button[data-testid="stBaseButton-tertiary"] {
    background: #27272a !important;
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
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
    background: #7c3aed !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: none !important;
    margin-top: 6px !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton > button:hover,
section.main div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton button:hover,
section.main div[data-testid="stVerticalBlockBorderWrapper"] form button[kind="primaryFormSubmit"]:hover {
    background: #6d28d9 !important;
    background-color: #6d28d9 !important;
    color: #ffffff !important;
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
    background: #27272a !important;
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
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
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, .22) !important;
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
    border: 1px solid #3f3f46 !important;
    background: #27272a !important;
    box-shadow: none !important;
}
"""
    )


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


def render_google_primary() -> None:
    google_block = oauth_button(
        "google",
        "Mit Google anmelden",
        "",
        "mb-oauth-google",
        primary=True,
    )
    st.markdown(
        f"""
<div class="mb-auth-google-block">
    <div class="mb-oauth-grid">{google_block}</div>
    <div class="mb-auth-trust">
        <strong>Empfohlen</strong> · OAuth 2.0 · Kein Passwort auf unseren Servern
    </div>
</div>
<div class="mb-auth-divider">oder mit Zugangsdaten</div>
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
    card_intro("Anmelden", "Zugang zu deinem Workspace.")

    with st.form("login_form", clear_on_submit=False, border=False):
        user = st.text_input("Username", placeholder="dein username")
        pw = st.text_input("Passwort", type="password", placeholder="••••••••")
        if st.form_submit_button("Einloggen", type="primary", width="stretch"):
            do_login(user, pw)


def render_register_form() -> None:
    card_intro("Registrieren", "Workspace in unter einer Minute anlegen.")

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

    st.markdown('<div class="mb-auth-page">', unsafe_allow_html=True)
    brand_col, login_col = st.columns([1.15, 1], gap="large")

    with brand_col:
        st.markdown(brand_panel_html(), unsafe_allow_html=True)

    with login_col:
        st.markdown('<div class="mb-auth-card-wrap">', unsafe_allow_html=True)
        st.markdown(card_hero_html(), unsafe_allow_html=True)
        render_google_primary()

        with st.container(border=True):
            mode = render_mode_switch()
            st.session_state.auth_mode = mode

            if mode == "register":
                render_register_form()
            else:
                render_login_form()

            st.markdown(
                """
<div class="mb-auth-foot">
    <strong>MaByte</strong> · Creator Operating System · Enterprise Session · Support Inbox
</div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("MaByte · Sichere Anmeldung · Production")

