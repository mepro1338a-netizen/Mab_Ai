"""MaByte Auth — emergency minimal Streamlit layout (no auth_premium CSS)."""
from __future__ import annotations

import random

import streamlit as st

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

# Minimal dark styling only — no grid, :has(), transforms, or column hacks.
_AUTH_MIN_CSS = """
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
    max-width: 1200px !important;
    padding: 2rem 1.5rem !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #27272a !important;
    color: #fafafa !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
}
[data-testid="stFormSubmitButton"] button[kind="primary"],
.stButton > button[kind="primary"] {
    background: #7c3aed !important;
    color: #ffffff !important;
    border: none !important;
}
[data-testid="stFormSubmitButton"] button[kind="primary"] p,
.stButton > button[kind="primary"] p {
    color: #ffffff !important;
}
"""


def _get_mode() -> str:
    mode = str(st.session_state.get("gate_mode") or st.session_state.get("auth_mode") or "login")
    return mode if mode in ("login", "register") else "login"


def _set_mode(mode: str) -> None:
    st.session_state.gate_mode = mode
    st.session_state.auth_mode = mode


def refresh_captcha() -> None:
    st.session_state.captcha_a = random.randint(1, 9)
    st.session_state.captcha_b = random.randint(1, 9)


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


def _check_captcha(captcha: int) -> bool:
    expected = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)
    if int(captcha) != expected:
        _set_notice("error", "Rechenaufgabe falsch — bitte erneut versuchen.")
        refresh_captcha()
        return False
    return True


def do_login(identifier: str, password: str, *, captcha: int) -> None:
    if not _check_captcha(captcha):
        return

    identifier = (identifier or "").strip()
    password = password or ""
    if not identifier or not password:
        _set_notice("error", "Bitte Benutzername/E-Mail und Passwort eingeben.")
        return

    allowed, msg = check_login_rate(identifier)
    if not allowed:
        _set_notice("error", msg)
        return

    ok, login_msg, user = verify_login_identifier(identifier, password)
    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user.get("username") or identifier, ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth(f"Login: {identifier}")
        st.rerun()
        return

    record_login_failure(identifier)
    _set_notice("error", login_msg or "Benutzername/E-Mail oder Passwort falsch.")
    refresh_captcha()


def do_register(
    *,
    full_name: str,
    username: str,
    email: str,
    password: str,
    password2: str,
    company: str,
    terms: bool,
    captcha: int,
) -> None:
    if not _check_captcha(captcha):
        return

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
        full_name=full_name,
        company=(company or "").strip(),
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
    refresh_captcha()


def handle_google_oauth_callback() -> None:
    params = st.query_params
    code = str(params.get("code") or "").strip()
    state = str(params.get("state") or "").strip()
    error = str(params.get("error") or "").strip()
    error_desc = str(params.get("error_description") or "").strip()

    _set_mode("login")
    inject_css(_AUTH_MIN_CSS)
    st.title("MaByte")

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


def _render_login_panel() -> None:
    a, b = st.session_state.captcha_a, st.session_state.captcha_b

    with st.form("auth_login_form", clear_on_submit=False, border=False):
        identifier = st.text_input("Benutzername oder E-Mail", placeholder="name@firma.de")
        password = st.text_input("Passwort", type="password", placeholder="Passwort")
        captcha = st.number_input(f"Sicherheitsfrage: {a} + {b} = ?", min_value=0, max_value=30, step=1, value=0)
        st.checkbox("Angemeldet bleiben", key="auth_remember")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)

    if submitted:
        do_login(identifier, password, captcha=int(captcha))

    if st.button("Neue Rechenaufgabe", key="auth_cap_refresh"):
        refresh_captcha()
        st.rerun()

    if provider_configured("google"):
        url = auth_url("google", make_state("google"))
        if url:
            st.link_button("Mit Google anmelden", url, use_container_width=True)

    st.caption("Noch kein Konto?")
    if st.button("Jetzt registrieren", key="auth_go_register", type="secondary"):
        _set_mode("register")
        refresh_captcha()
        st.rerun()


def _render_register_panel() -> None:
    a, b = st.session_state.captcha_a, st.session_state.captcha_b

    with st.form("auth_register_form", clear_on_submit=False, border=False):
        full_name = st.text_input("Vollständiger Name", placeholder="Max Mustermann")
        email = st.text_input("E-Mail", placeholder="name@firma.de")
        username = st.text_input("Benutzername", placeholder="dein_name")
        company = st.text_input("Unternehmen (optional)", placeholder="Firma GmbH")
        password = st.text_input("Passwort (min. 8)", type="password")
        password2 = st.text_input("Passwort bestätigen", type="password")
        captcha = st.number_input(f"Sicherheitsfrage: {a} + {b} = ?", min_value=0, max_value=30, step=1, value=0)
        terms = st.checkbox("Ich akzeptiere die AGB und Datenschutzerklärung.")
        submitted = st.form_submit_button("Konto erstellen", type="primary", use_container_width=True)

    if submitted:
        do_register(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            password2=password2,
            company=company,
            terms=terms,
            captcha=int(captcha),
        )

    if st.button("Zurück zum Login", key="auth_go_login", type="secondary"):
        _set_mode("login")
        refresh_captcha()
        st.rerun()


def render_auth() -> None:
    ensure_captcha()
    if _get_mode() not in ("login", "register"):
        _set_mode("login")
    elif "gate_mode" not in st.session_state:
        _set_mode("login")

    inject_css(_AUTH_MIN_CSS)
    mode = _get_mode()

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("# MaByte")
        st.markdown("**One system. Infinite intelligence.**")
        st.markdown(
            "Enterprise-Plattform für AI Content, Football Intelligence und Automatisierung."
        )
        st.markdown("- AI Reels")
        st.markdown("- Football AI")
        st.markdown("- Publishing")
        st.markdown("- Teams")

    with right:
        with st.container():
            if mode == "register":
                st.subheader("Konto erstellen")
            else:
                st.subheader("Anmelden")

            _show_notice()

            if mode == "register":
                _render_register_panel()
            else:
                _render_login_panel()

    st.caption("© 2026 MaByte")
