"""MaByte Auth — stable minimal Streamlit layout with scoped polish CSS."""
from __future__ import annotations

import html
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

# Scoped polish CSS — no grid / column-width hacks on Streamlit blocks.
_AUTH_MIN_CSS = """
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: linear-gradient(180deg, #09090b 0%, #18181b 45%, #09090b 100%) !important;
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
    max-width: 1200px !important;
    padding: 2.5rem 1.75rem 2.75rem !important;
    overflow-x: hidden !important;
}

/* Left branding feature cards */
[data-testid="stColumn"]:has(.auth-brand-marker) .auth-feat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 1.5rem;
    max-width: 560px;
}
[data-testid="stColumn"]:has(.auth-brand-marker) .auth-feat-card {
    padding: 14px 14px 12px 14px;
    border-radius: 14px;
    background: rgba(39, 39, 42, 0.65);
    border: 1px solid rgba(63, 63, 70, 0.8);
    box-sizing: border-box;
}
[data-testid="stColumn"]:has(.auth-brand-marker) .auth-feat-card strong {
    display: block;
    color: #fafafa;
    font-size: 13px;
    margin-bottom: 4px;
}
[data-testid="stColumn"]:has(.auth-brand-marker) .auth-feat-card span {
    display: block;
    color: #a1a1aa;
    font-size: 12px;
    line-height: 1.45;
}

/* Glass login card — right column */
[data-testid="stColumn"]:has(.auth-glass-marker) {
    max-width: 520px !important;
    width: 100% !important;
    margin-left: auto !important;
    background: rgba(24, 24, 27, 0.78) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 22px !important;
    box-shadow:
        0 0 0 1px rgba(124, 58, 237, 0.12),
        0 8px 32px rgba(124, 58, 237, 0.18),
        0 24px 48px rgba(0, 0, 0, 0.4) !important;
    padding: 2.5rem 2.25rem 2.25rem 2.25rem !important;
    box-sizing: border-box !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stVerticalBlock"] {
    gap: 0.85rem !important;
}
.auth-card-title {
    color: #fafafa !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.4rem 0 !important;
    line-height: 1.25 !important;
}
.auth-card-sub {
    color: #a1a1aa !important;
    font-size: 0.92rem !important;
    margin: 0 0 1.25rem 0 !important;
    line-height: 1.5 !important;
}

/* Inputs */
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stTextInput"] input {
    background: #27272a !important;
    color: #fafafa !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) div[data-baseweb="input"] {
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stTextInput"] button {
    background: transparent !important;
    border: none !important;
    color: #a1a1aa !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stWidgetLabel"] p,
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stCheckbox"] label p {
    color: #d4d4d8 !important;
}

/* Primary — violet/blue gradient */
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stColumn"]:has(.auth-glass-marker) .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #a855f7 0%, #7c3aed 45%, #4f46e5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.38) !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button[kind="primary"] p,
[data-testid="stColumn"]:has(.auth-glass-marker) .stButton > button[kind="primary"] p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Google button */
[data-testid="stColumn"]:has(.auth-glass-marker) a.auth-google-btn {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    width: 100% !important;
    min-height: 46px !important;
    margin-top: 0.75rem !important;
    padding: 0 16px !important;
    border-radius: 10px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #fafafa !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-sizing: border-box !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) a.auth-google-btn:hover {
    border-color: #52525b !important;
    background: #3f3f46 !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) .auth-google-icon {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 20px !important;
    height: 20px !important;
    flex-shrink: 0 !important;
}

/* Register link area */
[data-testid="stColumn"]:has(.auth-glass-marker) .auth-register-line {
    text-align: center !important;
    margin: 1.35rem 0 0.5rem 0 !important;
    color: #a1a1aa !important;
    font-size: 0.9rem !important;
    line-height: 1.5 !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) .stButton > button[kind="tertiary"] {
    color: #c4b5fd !important;
    background: transparent !important;
    border: none !important;
    width: 100% !important;
    font-weight: 600 !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) .stButton > button[kind="tertiary"] p {
    color: #c4b5fd !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) .stButton > button[kind="secondary"] {
    background: rgba(124, 58, 237, 0.14) !important;
    border: 1px solid rgba(167, 139, 250, 0.45) !important;
    color: #c4b5fd !important;
    border-radius: 10px !important;
    min-height: 42px !important;
    width: 100% !important;
}
[data-testid="stColumn"]:has(.auth-glass-marker) .stButton > button[kind="secondary"] p {
    color: #c4b5fd !important;
    font-weight: 600 !important;
}

@media (max-width: 900px) {
    [data-testid="stColumn"]:has(.auth-glass-marker) {
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding: 2rem 1.5rem !important;
    }
    [data-testid="stColumn"]:has(.auth-brand-marker) .auth-feat-grid {
        grid-template-columns: 1fr;
        max-width: 100%;
    }
}
"""

_GOOGLE_ICON_SVG = (
    '<svg class="auth-google-icon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
    '<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>'
    '<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>'
    '<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>'
    '<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>'
    "</svg>"
)

_BRAND_FEATURES_HTML = """
<span class="auth-brand-marker" hidden aria-hidden="true"></span>
<div class="auth-feat-grid">
  <div class="auth-feat-card"><strong>AI Reels Studio</strong><span>Automatisierte Shorts &amp; Videos</span></div>
  <div class="auth-feat-card"><strong>Football Intelligence</strong><span>Datenbasierte Analysen &amp; Prognosen</span></div>
  <div class="auth-feat-card"><strong>Publishing Engine</strong><span>Omnichannel Distribution</span></div>
  <div class="auth-feat-card"><strong>Team Workspace</strong><span>Zusammenarbeit &amp; Verwaltung</span></div>
</div>
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


def _parse_captcha_answer(raw: str) -> int | None:
    text = (raw or "").strip()
    if not text or not text.isdigit():
        return None
    return int(text)


def _check_captcha(captcha_raw: str) -> bool:
    expected = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)
    answer = _parse_captcha_answer(captcha_raw)
    if answer is None or answer != expected:
        _set_notice("error", "Rechenaufgabe falsch — bitte erneut versuchen.")
        refresh_captcha()
        return False
    return True


def do_login(identifier: str, password: str, *, captcha: str) -> None:
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
    username: str,
    email: str,
    password: str,
    password2: str,
    terms: bool,
    captcha: str,
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
            "Account Name: 3–40 Zeichen, nur Buchstaben, Zahlen oder Unterstrich.",
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


def _render_google_button() -> None:
    if not provider_configured("google"):
        return
    url = auth_url("google", make_state("google"))
    if not url:
        return
    safe_url = html.escape(url)
    st.markdown(
        f'<a class="auth-google-btn" href="{safe_url}">'
        f"{_GOOGLE_ICON_SVG}"
        "<span>Mit Google anmelden</span></a>",
        unsafe_allow_html=True,
    )


def _render_login_panel() -> None:
    a, b = st.session_state.captcha_a, st.session_state.captcha_b

    with st.form("auth_login_form", clear_on_submit=False, border=False):
        identifier = st.text_input("Benutzername oder E-Mail", placeholder="name@firma.de")
        password = st.text_input("Passwort", type="password", placeholder="Passwort")
        st.markdown(f"**Sicherheitsfrage: {a} + {b} = ?**")
        captcha = st.text_input("Antwort eingeben", placeholder="Antwort eingeben", label_visibility="collapsed")
        st.checkbox("Angemeldet bleiben", key="auth_remember")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)

    if submitted:
        do_login(identifier, password, captcha=captcha)

    _render_google_button()

    st.markdown(
        '<p class="auth-register-line">Noch kein Konto?<br>Jetzt registrieren →</p>',
        unsafe_allow_html=True,
    )
    if st.button("Jetzt registrieren", key="auth_go_register", type="tertiary", use_container_width=True):
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
        st.markdown(f"**Sicherheitsfrage: {a} + {b} = ?**")
        captcha = st.text_input("Antwort eingeben", placeholder="Antwort eingeben", label_visibility="collapsed")
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
            captcha=captcha,
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
        st.markdown(_BRAND_FEATURES_HTML, unsafe_allow_html=True)

    with right:
        st.markdown(
            '<span class="auth-glass-marker" hidden aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        with st.container():
            if mode == "register":
                st.markdown('<p class="auth-card-title">Account erstellen</p>', unsafe_allow_html=True)
                st.markdown(
                    '<p class="auth-card-sub">Account Name, E-Mail und Passwort — in unter einer Minute startklar.</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<p class="auth-card-title">Willkommen zurück</p>', unsafe_allow_html=True)
                st.markdown(
                    '<p class="auth-card-sub">Melden Sie sich an, um auf Ihren MaByte Workspace zuzugreifen.</p>',
                    unsafe_allow_html=True,
                )

            _show_notice()

            if mode == "register":
                _render_register_panel()
            else:
                _render_login_panel()

    st.caption("© 2026 MaByte")
