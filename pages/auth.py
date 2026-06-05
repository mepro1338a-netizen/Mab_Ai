"""MaByte Auth — premium login (username + password)."""
from __future__ import annotations

import html

import streamlit as st

from config import APP_NAME
from database import record_login_event, register_account, verify_login_identifier
from logger import log_auth
from oauth_service import (
    auth_url,
    complete_oauth,
    friendly_oauth_error,
    make_state,
    provider_configured,
    verify_state,
)
from security import check_login_rate, is_valid_email, is_valid_username, record_login_failure
from services.session_auth import rotate_session_on_login
from ui.styles import inject_css

_DEFAULT_USE_CASE = "Sonstiges"
_DEFAULT_COUNTRY = "Deutschland"
_APP = html.escape(APP_NAME or "MaByte")
_INITIAL = html.escape(APP_NAME[:1] if APP_NAME else "M")

_AUTH_CSS = """
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: linear-gradient(180deg, #09090b 0%, #121214 50%, #09090b 100%) !important;
    color: #fafafa !important;
    overflow-x: hidden !important;
}
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stMain"] .block-container,
[data-testid="stMainBlockContainer"] {
    max-width: 440px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: clamp(1.75rem, 6vh, 3.5rem) 1.25rem 2rem !important;
}

[data-testid="stVerticalBlock"]:has(.auth-v2-marker) {
    gap: 0 !important;
}

.auth-topbar {
    display: flex;
    align-items: center;
    margin-bottom: 1.75rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.auth-topbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.auth-logo-mark {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 17px;
    color: #fff;
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    flex-shrink: 0;
}
.auth-topbar-name {
    display: block;
    font-size: 18px;
    font-weight: 800;
    color: #fafafa;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.auth-topbar-tag {
    display: block;
    font-size: 11px;
    font-weight: 500;
    color: #a1a1aa;
    line-height: 1.35;
    margin-top: 2px;
}

.auth-hero-title {
    margin: 0 0 1.5rem;
    font-size: 1.5rem;
    font-weight: 800;
    color: #fafafa;
    line-height: 1.25;
    letter-spacing: -0.03em;
    text-align: center;
}
.auth-hero-title span {
    color: #8b5cf6;
}

.auth-v2-card {
    width: 100%;
    padding: 1.75rem 1.5rem 1.35rem;
    border-radius: 16px;
    background: rgba(24, 24, 27, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.09);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.32);
    box-sizing: border-box;
}
.auth-v2-title {
    margin: 0 0 1.25rem;
    font-size: 1rem;
    font-weight: 700;
    color: #e4e4e7;
    letter-spacing: -0.01em;
}

[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stTextInput"] label p,
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stWidgetLabel"] p {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #d4d4d8 !important;
    margin-bottom: 4px !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stTextInput"] input {
    background: #18181b !important;
    color: #fafafa !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    min-height: 46px !important;
    font-size: 15px !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stTextInput"] input:focus {
    border-color: rgba(139, 92, 246, 0.55) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.14) !important;
    outline: none !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) div[data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stTextInput"] {
    margin-bottom: 2px !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stCheckbox"] label p {
    font-size: 0.84rem !important;
    color: #a1a1aa !important;
}

[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stFormSubmitButton"] button,
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .stButton > button[kind="primary"] {
    width: 100% !important;
    min-height: 46px !important;
    margin-top: 6px !important;
    border-radius: 10px !important;
    border: none !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6366f1 100%) !important;
    color: #fff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(139, 92, 246, 0.32) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stFormSubmitButton"] button p,
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .stButton > button[kind="primary"] p {
    color: #fff !important;
    font-weight: 700 !important;
}

.auth-v2-divider {
    display: flex; align-items: center; gap: 12px;
    margin: 1rem 0 0.75rem; color: #52525b; font-size: 12px;
}
.auth-v2-divider::before, .auth-v2-divider::after {
    content: ""; flex: 1; height: 1px; background: rgba(255,255,255,.08);
}
a.auth-v2-google {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    width: 100%; min-height: 44px; padding: 0 16px; border-radius: 10px;
    background: #18181b; border: 1px solid #3f3f46;
    color: #e4e4e7 !important; text-decoration: none !important;
    font-size: 14px; font-weight: 600; box-sizing: border-box;
}
a.auth-v2-google:hover {
    background: #27272a; border-color: #52525b;
}

.auth-v2-foot {
    text-align: center; margin-top: 1.15rem; padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,.06);
}
.auth-v2-foot p {
    margin: 0 0 0.4rem; font-size: 0.85rem; color: #71717a;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .st-key-auth_v2_switch .stButton>button,
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .st-key-auth_v2_forgot .stButton>button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #8b5cf6 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    padding: 0 !important;
    min-height: auto !important;
    height: auto !important;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .st-key-auth_v2_forgot {
    display: flex; justify-content: flex-end; margin: 0.1rem 0 0.35rem;
}
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .st-key-auth_v2_switch .stButton>button p,
[data-testid="stVerticalBlock"]:has(.auth-v2-marker) .st-key-auth_v2_forgot .stButton>button p {
    color: #8b5cf6 !important;
}

[data-testid="stVerticalBlock"]:has(.auth-v2-marker) [data-testid="stAlert"] {
    margin-bottom: 0.85rem !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
}

.auth-v2-copy {
    text-align: center; margin-top: 1.25rem;
    font-size: 0.72rem; color: #52525b;
}

@media (max-width: 480px) {
    [data-testid="stMain"] .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .auth-v2-card { padding: 1.35rem 1.15rem 1.15rem; }
    .auth-hero-title { font-size: 1.3rem; }
}
"""

_GOOGLE_ICON = (
    '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
    '<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>'
    '<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>'
    '<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>'
    '<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>'
    "</svg>"
)


def _get_mode() -> str:
    mode = str(st.session_state.get("gate_mode") or st.session_state.get("auth_mode") or "login")
    return mode if mode in ("login", "register") else "login"


def _set_mode(mode: str) -> None:
    st.session_state.gate_mode = mode
    st.session_state.auth_mode = mode


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


def _utm_from_query() -> dict:
    params = st.query_params
    keys = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")
    return {k: str(params.get(k) or "").strip() for k in keys if params.get(k)}


def _set_notice(level: str, message: str) -> None:
    st.session_state.gate_notice = {"level": level, "message": message}


def _show_notice() -> None:
    notice = st.session_state.pop("gate_notice", None) or st.session_state.pop("auth_notice", None)
    if not notice:
        return
    level = notice.get("level", "info")
    message = notice.get("message", "")
    if level == "error":
        st.error(message)
    elif level == "success":
        st.success(message)
    else:
        st.info(message)


def do_login(username: str, password: str) -> None:
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        _set_notice("error", "Bitte Benutzername und Passwort eingeben.")
        return

    allowed, msg = check_login_rate(username)
    if not allowed:
        _set_notice("error", msg)
        return

    ok, login_msg, user = verify_login_identifier(username, password)
    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user.get("username") or username, ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth(f"Login: {username}")
        st.rerun()
        return

    record_login_failure(username)
    _set_notice("error", login_msg or "Benutzername oder Passwort falsch.")


def _refresh_register_captcha() -> tuple[int, int]:
    import random

    a, b = random.randint(2, 9), random.randint(2, 9)
    st.session_state["reg_cap_a"] = a
    st.session_state["reg_cap_b"] = b
    return a, b


def _register_captcha_values() -> tuple[int, int]:
    a = int(st.session_state.get("reg_cap_a") or 0)
    b = int(st.session_state.get("reg_cap_b") or 0)
    if a < 1 or b < 1:
        return _refresh_register_captcha()
    return a, b


def do_register(
    *,
    username: str,
    email: str,
    password: str,
    password2: str,
    terms: bool,
    captcha_answer: str,
) -> None:
    username = (username or "").strip()
    email = (email or "").strip()
    password = password or ""
    password2 = password2 or ""

    cap_a = int(st.session_state.get("reg_cap_a") or 0)
    cap_b = int(st.session_state.get("reg_cap_b") or 0)
    try:
        cap_ok = int(str(captcha_answer or "").strip()) == cap_a + cap_b
    except ValueError:
        cap_ok = False
    if not cap_ok:
        _refresh_register_captcha()
        _set_notice("error", "Captcha falsch — bitte erneut versuchen.")
        return

    if password != password2:
        _set_notice("error", "Passwörter stimmen nicht überein.")
        return

    if not is_valid_username(username):
        _set_notice(
            "error",
            "Benutzername: 3–40 Zeichen, nur Buchstaben, Zahlen oder Unterstrich.",
        )
        return

    if not is_valid_email(email):
        _set_notice("error", "Bitte eine gültige E-Mail-Adresse eingeben.")
        return

    if not terms:
        _set_notice("error", "Bitte AGB und Datenschutz bestätigen.")
        return

    ip_address, user_agent = client_meta()
    ok, msg, user = register_account(
        username=username,
        email=email,
        password=password,
        full_name=username,
        company="",
        phone="",
        country=_DEFAULT_COUNTRY,
        use_case=_DEFAULT_USE_CASE,
        marketing_opt_in=False,
        terms_accepted=terms,
        ip_address=ip_address,
        user_agent=user_agent,
        utm=_utm_from_query(),
    )

    if ok and user:
        record_login_event(user.get("username") or username, ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth(f"Register+Login: {username}")
        st.session_state.pop("gate_notice", None)
        st.rerun()
        return

    _set_notice("error", msg)


def handle_google_oauth_callback() -> None:
    params = st.query_params
    code = str(params.get("code") or "").strip()
    state = str(params.get("state") or "").strip()
    error = str(params.get("error") or "").strip()
    error_desc = str(params.get("error_description") or "").strip()

    _set_mode("login")
    inject_css(_AUTH_CSS)
    st.markdown('<span class="auth-v2-marker" hidden></span>', unsafe_allow_html=True)
    st.markdown(_topbar_html(), unsafe_allow_html=True)

    if error:
        st.error(friendly_oauth_error(error, error_desc))
        st.query_params.clear()
        if st.button("Zurück zum Login", type="primary", key="oauth_err_back"):
            st.rerun()
        return

    provider = verify_state(state)
    if provider != "google" or not code:
        st.error("OAuth-Session ungültig oder abgelaufen.")
        st.query_params.clear()
        if st.button("Zurück zum Login", type="primary", key="oauth_invalid_back"):
            st.rerun()
        return

    ok, msg, user = complete_oauth("google", code)
    st.query_params.clear()

    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user.get("username") or "", ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth("Login: google_oauth")
        st.rerun()
        return

    st.error(msg)
    if st.button("Zurück zum Login", type="primary", key="oauth_fail_back"):
        st.rerun()


def _topbar_html() -> str:
    return (
        '<header class="auth-topbar">'
        '<div class="auth-topbar-brand">'
        f'<span class="auth-logo-mark">{_INITIAL}</span>'
        "<div>"
        f'<span class="auth-topbar-name">{_APP}</span>'
        '<span class="auth-topbar-tag">Enterprise AI Platform</span>'
        "</div></div></header>"
    )


def _hero_slogan_html() -> str:
    return (
        '<h1 class="auth-hero-title">One System. <span>Infinite Intelligence.</span></h1>'
    )


def _render_google_button() -> None:
    if not provider_configured("google"):
        return
    url = auth_url("google", make_state("google"))
    if not url:
        return
    st.markdown('<div class="auth-v2-divider">oder</div>', unsafe_allow_html=True)
    st.markdown(
        f'<a class="auth-v2-google" href="{html.escape(url)}">'
        f"{_GOOGLE_ICON}<span>Google</span></a>",
        unsafe_allow_html=True,
    )


def _render_login_form() -> None:
    st.markdown('<p class="auth-v2-title">Anmelden</p>', unsafe_allow_html=True)

    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="auth_v2_user")
        password = st.text_input(
            "Passwort",
            type="default" if st.session_state.get("auth_show_password") else "password",
            key="auth_v2_pass",
        )
        st.checkbox("Passwort anzeigen", key="auth_show_password", value=False)
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)

    if st.button("Passwort vergessen?", key="auth_v2_forgot", type="tertiary"):
        _set_notice("info", "Passwort-Reset folgt in Kürze. Bitte Support kontaktieren.")

    if submitted:
        do_login(username, password)

    _render_google_button()

    st.markdown('<div class="auth-v2-foot">', unsafe_allow_html=True)
    st.markdown('<p>Noch kein Konto?</p>', unsafe_allow_html=True)
    if st.button("Registrieren", key="auth_v2_switch", type="tertiary"):
        _set_mode("register")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_register_form() -> None:
    cap_a, cap_b = _register_captcha_values()
    st.markdown('<p class="auth-v2-title">Registrieren</p>', unsafe_allow_html=True)

    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="reg_v2_user")
        email = st.text_input("E-Mail", key="reg_v2_email")
        password = st.text_input("Passwort", type="password", key="reg_v2_pass")
        password2 = st.text_input("Passwort bestätigen", type="password", key="reg_v2_pass2")
        captcha = st.text_input(f"Sicherheit: {cap_a} + {cap_b} = ?", key="reg_v2_cap")
        terms = st.checkbox("AGB und Datenschutz akzeptieren", key="reg_v2_terms")
        submitted = st.form_submit_button("Account erstellen", type="primary", use_container_width=True)

    if submitted:
        do_register(
            username=username,
            email=email,
            password=password,
            password2=password2,
            terms=terms,
            captcha_answer=captcha,
        )

    st.markdown('<div class="auth-v2-foot">', unsafe_allow_html=True)
    st.markdown('<p>Bereits ein Konto?</p>', unsafe_allow_html=True)
    if st.button("Zum Login", key="auth_v2_switch", type="tertiary"):
        _set_mode("login")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_auth() -> None:
    if _get_mode() not in ("login", "register"):
        _set_mode("login")
    elif "gate_mode" not in st.session_state:
        _set_mode("login")

    inject_css(_AUTH_CSS)
    mode = _get_mode()

    st.markdown('<span class="auth-v2-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)
    st.markdown(_topbar_html(), unsafe_allow_html=True)
    st.markdown(_hero_slogan_html(), unsafe_allow_html=True)
    st.markdown('<div class="auth-v2-card">', unsafe_allow_html=True)

    _show_notice()

    if mode == "register":
        _render_register_form()
    else:
        _render_login_form()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<p class="auth-v2-copy">© 2026 MaByte</p>', unsafe_allow_html=True)
