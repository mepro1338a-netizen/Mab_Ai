"""MaByte Auth — einfacher Login und Registrierung."""
from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

from config import APP_NAME
from database import record_login_event, register_account, verify_login_identifier
from logger import log_auth
from oauth_service import complete_oauth, friendly_oauth_error, verify_state
from security import check_login_rate, is_valid_email, is_valid_username, record_login_failure
from services.session_auth import rotate_session_on_login
from ui.styles import inject_css

_DEFAULT_USE_CASE = "Sonstiges"
_DEFAULT_COUNTRY = "Deutschland"
_APP = html.escape(APP_NAME or "MaByte")
_INITIAL = html.escape(APP_NAME[:1] if APP_NAME else "M")
_SLOGAN_HEADER = Path(__file__).resolve().parent.parent / "assets" / "sloganheader.png"

_AUTH_CSS = """
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: #09090b !important;
    color: #fafafa !important;
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
    max-width: 400px !important;
    margin: 0 auto !important;
    padding: 0 1rem 2rem !important;
}

[data-testid="stVerticalBlock"]:has(.auth-marker) { gap: 0 !important; }

.auth-hero {
    width: 100vw; position: relative; left: 50%; margin-left: -50vw;
    margin-bottom: 1rem; padding: 0.4rem 0.75rem 0.75rem;
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.auth-main-header {
    height: 50px; display: flex; align-items: center; justify-content: center;
    margin: 0 0 0.65rem; overflow: hidden;
}
.auth-main-header img {
    width: min(1180px, calc(100vw - 1rem)); height: 50px;
    object-fit: cover; object-position: center 42%;
}
.auth-brand-row {
    display: flex; align-items: center; justify-content: center; gap: 11px;
}
.auth-logo-mark {
    width: 48px; height: 48px; border-radius: 11px;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 20px; color: #fff;
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
}
.auth-topbar-name {
    display: block; font-size: 1.75rem; font-weight: 800; color: #fafafa;
    line-height: 1.05; letter-spacing: -0.03em;
}
.auth-topbar-tag {
    display: block; font-size: 11px; color: #71717a; margin-top: 3px;
}

[data-testid="stVerticalBlock"]:has(.auth-form-marker) {
    padding: 1.25rem 1.1rem !important;
    border-radius: 12px !important;
    background: #18181b !important;
    border: 1px solid #27272a !important;
    gap: 0.35rem !important;
}
[data-testid="stVerticalBlock"]:has(.auth-form-marker) [data-testid="stTextInput"] input {
    background: #09090b !important; color: #fafafa !important;
    border: 1px solid #3f3f46 !important; border-radius: 8px !important;
    min-height: 44px !important;
}
[data-testid="stVerticalBlock"]:has(.auth-form-marker) [data-testid="stForm"] {
    border: none !important; padding: 0 !important; background: transparent !important;
}
[data-testid="stVerticalBlock"]:has(.auth-form-marker) [data-testid="stFormSubmitButton"] button,
[data-testid="stVerticalBlock"]:has(.auth-form-marker) .stButton > button[kind="primary"] {
    width: 100% !important; min-height: 44px !important;
    border-radius: 8px !important; border: none !important;
    background: #7c3aed !important; color: #fff !important; font-weight: 700 !important;
}
[data-testid="stVerticalBlock"]:has(.auth-form-marker) .st-key-auth_mode_switch .stButton>button {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #a78bfa !important; font-size: 0.85rem !important; font-weight: 600 !important;
    padding: 0 !important; min-height: auto !important;
}
[data-testid="stVerticalBlock"]:has(.auth-form-marker) .st-key-auth_mode_switch .stButton>button p {
    color: #a78bfa !important;
}
.auth-ssl-note {
    text-align: center; margin-top: 0.85rem; font-size: 0.72rem; color: #52525b;
}
"""


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


def do_register(
    *,
    username: str,
    email: str,
    password: str,
    password2: str,
    terms: bool,
) -> None:
    username = (username or "").strip()
    email = (email or "").strip()
    password = password or ""
    password2 = password2 or ""

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
    st.query_params.clear()

    if error:
        _set_notice("error", friendly_oauth_error(error, error_desc))
        st.rerun()
        return

    provider = verify_state(state)
    if provider != "google" or not code:
        _set_notice("error", "OAuth-Session ungültig. Bitte mit Benutzername anmelden.")
        st.rerun()
        return

    ok, msg, user = complete_oauth("google", code)
    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user.get("username") or "", ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth("Login: google_oauth")
        st.rerun()
        return

    _set_notice("error", msg or "Anmeldung fehlgeschlagen.")
    st.rerun()


def _img_base64(path: Path) -> str:
    if not path.is_file():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _hero_html() -> str:
    encoded = _img_base64(_SLOGAN_HEADER)
    slogan = ""
    if encoded:
        slogan = (
            '<header class="auth-main-header">'
            f'<img src="data:image/png;base64,{encoded}" '
            'alt="One System. Infinite Intelligence." />'
            "</header>"
        )
    return (
        '<div class="auth-hero">'
        f"{slogan}"
        '<div class="auth-brand-row">'
        f'<span class="auth-logo-mark">{_INITIAL}</span>'
        '<div>'
        f'<span class="auth-topbar-name">{_APP}</span>'
        '<span class="auth-topbar-tag">Enterprise AI Platform</span>'
        "</div></div></div>"
    )


def _render_login_form() -> None:
    st.markdown('<p style="margin:0 0 0.75rem;font-weight:600;">Anmelden</p>', unsafe_allow_html=True)
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
    if submitted:
        do_login(username, password)
    if st.button("Noch kein Konto? Registrieren", key="auth_mode_switch", type="tertiary"):
        _set_mode("register")
        st.rerun()


def _render_register_form() -> None:
    st.markdown('<p style="margin:0 0 0.75rem;font-weight:600;">Registrieren</p>', unsafe_allow_html=True)
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername")
        email = st.text_input("E-Mail")
        password = st.text_input("Passwort", type="password")
        password2 = st.text_input("Passwort bestätigen", type="password")
        terms = st.checkbox("AGB und Datenschutz akzeptieren")
        submitted = st.form_submit_button("Registrieren", type="primary", use_container_width=True)
    if submitted:
        do_register(
            username=username,
            email=email,
            password=password,
            password2=password2,
            terms=terms,
        )
    if st.button("Bereits ein Konto? Anmelden", key="auth_mode_switch", type="tertiary"):
        _set_mode("login")
        st.rerun()


def render_auth() -> None:
    if _get_mode() not in ("login", "register"):
        _set_mode("login")
    elif "gate_mode" not in st.session_state:
        _set_mode("login")

    inject_css(_AUTH_CSS)
    mode = _get_mode()

    st.markdown('<span class="auth-marker" hidden></span>', unsafe_allow_html=True)
    st.markdown(_hero_html(), unsafe_allow_html=True)

    with st.container():
        st.markdown('<span class="auth-form-marker" hidden></span>', unsafe_allow_html=True)
        _show_notice()
        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()

    st.markdown(
        '<p class="auth-ssl-note">🔒 SSL-verschlüsselte Verbindung</p>',
        unsafe_allow_html=True,
    )
