"""MaByte Auth — Login & Registrierung."""
from __future__ import annotations

import html

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from database import record_login_event, register_account, verify_login_identifier
from logger import log_auth
from oauth_service import (
    auth_url,
    complete_oauth,
    friendly_oauth_error,
    make_state,
    oauth_state_ready,
    provider_configured,
    verify_state,
)
from security import check_login_rate, is_valid_email, is_valid_username, record_login_failure
from services.session_auth import rotate_session_on_login
from ui.styles import inject_css

_DEFAULT_USE_CASE = "Sonstiges"
_DEFAULT_COUNTRY = "Deutschland"
_APP = html.escape(APP_NAME or "MaByte")
_TAGLINE = html.escape(APP_TAGLINE or "Dein KI-Workspace")

_AUTH_CSS = """
/* MaByte Auth — aligned with app zinc/violet theme */
:root {
    --auth-bg: #09090b;
    --auth-surface: rgba(24, 24, 27, 0.98);
    --auth-line: rgba(255, 255, 255, 0.08);
    --auth-text: #fafafa;
    --auth-muted: #a1a1aa;
    --auth-hint: #71717a;
    --auth-field: #18181b;
    --auth-field-line: rgba(255, 255, 255, 0.1);
    --auth-accent: #7c3aed;
    --auth-accent-hover: #6d28d9;
    --auth-glow: rgba(124, 58, 237, 0.18);
    --auth-radius: 12px;
    --auth-input-h: 44px;
    --auth-pad: 40px;
    --auth-w: 480px;
    --s1: 8px;
    --s2: 16px;
    --s3: 24px;
    --s4: 32px;
}

html:has(.auth-marker),
html:has(.auth-marker) body,
html:has(.auth-marker) .stApp,
html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"],
html:has(.auth-marker) section.main .block-container,
html:has(.auth-marker) [data-testid="stMain"] .block-container {
    background: var(--auth-bg) !important;
    background-color: var(--auth-bg) !important;
    background-image: none !important;
    color: var(--auth-text) !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

html:has(.auth-marker) #MainMenu,
html:has(.auth-marker) footer,
html:has(.auth-marker) [data-testid="stToolbar"],
html:has(.auth-marker) [data-testid="stDecoration"],
html:has(.auth-marker) [data-testid="stSidebar"],
html:has(.auth-marker) [data-testid="stHeader"] {
    display: none !important;
}

.auth-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 80% 50% at 50% -20%, var(--auth-glow), transparent 65%),
        radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.06), transparent 40%),
        var(--auth-bg);
}

.auth-bg::after {
    content: "";
    position: absolute;
    inset: 0;
    opacity: 0.35;
    background-image: radial-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px);
    background-size: 24px 24px;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, black, transparent);
}

html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"] {
    min-height: 100dvh !important;
}

html:has(.auth-marker) [data-testid="stMain"] {
    position: relative !important;
    z-index: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: var(--s3) var(--s2) !important;
    overflow-y: auto !important;
}

html:has(.auth-marker) [data-testid="stMain"] .block-container,
html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
    max-width: var(--auth-w) !important;
    width: min(var(--auth-w), 100%) !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card {
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card > [data-testid="stVerticalBlock"]:has(.auth-card-marker) {
    position: relative !important;
    border-radius: 16px !important;
    border: 1px solid var(--auth-line) !important;
    background: var(--auth-surface) !important;
    backdrop-filter: blur(32px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(32px) saturate(150%) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.07),
        0 0 0 1px rgba(0, 0, 0, 0.4),
        0 32px 64px -24px rgba(0, 0, 0, 0.65) !important;
    padding: var(--auth-pad) !important;
    gap: 0 !important;
    align-items: stretch !important;
    overflow: hidden !important;
}

html:has(.auth-marker) .st-key-auth_card > [data-testid="stVerticalBlock"]:has(.auth-card-marker)::before {
    content: "";
    position: absolute;
    top: 0;
    left: 10%;
    right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.55), transparent);
    pointer-events: none;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

.auth-header {
    margin: 0 0 var(--s3);
    text-align: center;
}

.auth-brand {
    margin: 0;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.035em;
    line-height: 1.1;
    color: var(--auth-text) !important;
}

.auth-tagline {
    margin: var(--s1) 0 0;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.45;
    color: var(--auth-muted) !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap {
    margin: 0 0 var(--s3) !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stWidgetLabel"],
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stWidgetLabel"] {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"],
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] {
    width: 100% !important;
    background: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: var(--auth-radius) !important;
    padding: 4px !important;
    gap: 4px !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] button,
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] button {
    flex: 1 !important;
    min-height: 40px !important;
    height: 40px !important;
    border: none !important;
    outline: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--auth-muted) !important;
    box-shadow: none !important;
    transition: background 0.15s ease, color 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] button[aria-selected="true"],
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] button[aria-selected="true"] {
    background: rgba(255, 255, 255, 0.1) !important;
    color: var(--auth-text) !important;
}

.auth-intro {
    margin: 0 0 var(--s2);
    text-align: center;
}

.auth-title {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.25;
    color: var(--auth-text) !important;
}

.auth-sub {
    margin: 6px 0 0;
    font-size: 14px;
    line-height: 1.5;
    color: var(--auth-muted) !important;
}

.auth-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 var(--s2);
    font-size: 12px;
    font-weight: 500;
    color: var(--auth-hint) !important;
    text-transform: lowercase;
}

.auth-divider::before,
.auth-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
}

html:has(.auth-marker) .st-key-auth_oauth {
    margin: 0 0 var(--s2) !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_oauth a,
html:has(.auth-marker) .st-key-auth_oauth [data-testid="stLinkButton"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: var(--auth-input-h) !important;
    border-radius: var(--auth-radius) !important;
    border: 1px solid var(--auth-field-line) !important;
    background: var(--auth-field) !important;
    color: var(--auth-text) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    transition: border-color 0.15s ease, background 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_oauth a:hover {
    border-color: rgba(255, 255, 255, 0.18) !important;
    background: #27272a !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    gap: var(--s2) !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] {
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stWidgetLabel"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] label[data-testid="stWidgetLabel"] {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] > div:last-of-type {
    position: relative !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] > div,
html:has(.auth-marker) .st-key-auth_card div[data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input {
    background: var(--auth-field) !important;
    color: var(--auth-text) !important;
    -webkit-text-fill-color: var(--auth-text) !important;
    border: 1px solid var(--auth-field-line) !important;
    border-radius: var(--auth-radius) !important;
    min-height: var(--auth-input-h) !important;
    height: var(--auth-input-h) !important;
    font-size: 15px !important;
    padding: 0 44px 0 14px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_card .st-key-auth_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_email input {
    padding-right: 14px !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input::placeholder {
    color: var(--auth-hint) !important;
    opacity: 1 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:hover {
    border-color: rgba(255, 255, 255, 0.16) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:focus {
    border-color: rgba(124, 58, 237, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
    outline: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] {
    position: absolute !important;
    right: 6px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 32px !important;
    height: 32px !important;
    min-height: 32px !important;
    padding: 0 !important;
    border: none !important;
    border-radius: 8px !important;
    background: transparent !important;
    color: var(--auth-muted) !important;
    box-shadow: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: var(--auth-text) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] {
    margin: var(--s1) 0 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] label p {
    font-size: 13px !important;
    color: var(--auth-muted) !important;
    line-height: 1.45 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] {
    margin-top: var(--s1) !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"] {
    width: 100% !important;
    min-height: var(--auth-input-h) !important;
    height: var(--auth-input-h) !important;
    border: none !important;
    border-radius: var(--auth-radius) !important;
    background: var(--auth-accent) !important;
    background-image: none !important;
    color: #fff !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    transition: background 0.15s ease, transform 0.12s ease !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button:hover,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"]:hover {
    background: var(--auth-accent-hover) !important;
    transform: translateY(-1px) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button p,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"] p {
    color: #fff !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stAlert"] {
    border-radius: var(--auth-radius) !important;
    font-size: 14px !important;
    margin: 0 0 var(--s2) !important;
    width: 100% !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

.auth-footer {
    margin: var(--s3) 0 0;
    padding-top: var(--s2);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    font-size: 12px;
    color: var(--auth-hint) !important;
    letter-spacing: 0.01em;
}

html:has(.auth-marker) .stApp {
    --background-color: #09090b !important;
    --primary-color: #7c3aed !important;
}

@media (max-width: 640px) {
    html:has(.auth-marker) {
        --auth-pad: 28px;
        --auth-w: 100%;
    }
    html:has(.auth-marker) .auth-brand { font-size: 26px; }
    html:has(.auth-marker) .auth-title { font-size: 20px; }
    html:has(.auth-marker) [data-testid="stMain"] {
        justify-content: flex-start !important;
        padding-top: var(--s2) !important;
    }
}
"""


def _get_mode() -> str:
    mode = str(st.session_state.get("gate_mode") or st.session_state.get("auth_mode") or "login")
    return mode if mode in ("login", "register") else "login"


def _set_mode(mode: str) -> None:
    st.session_state.gate_mode = mode
    st.session_state.auth_mode = mode
    st.session_state["auth_mode_seg"] = "Registrieren" if mode == "register" else "Anmelden"


def _google_login_url() -> str:
    if not provider_configured("google") or not oauth_state_ready():
        return ""
    state = make_state("google")
    return auth_url("google", state) if state else ""


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
    _set_notice("error", login_msg or "Benutzername oder Passwort stimmen nicht.")


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
        _set_notice("error", "Die Passwörter stimmen nicht überein.")
        return

    if not is_valid_username(username):
        _set_notice("error", "Benutzername: 3–40 Zeichen, Buchstaben, Zahlen oder Unterstrich (_).")
        return

    if not is_valid_email(email):
        _set_notice("error", "Bitte gib eine gültige E-Mail-Adresse ein.")
        return

    if not terms:
        _set_notice("error", "Bitte bestätige AGB und Datenschutz.")
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


def _render_oauth_section() -> None:
    url = _google_login_url()
    if not url:
        return
    with st.container(key="auth_oauth"):
        st.link_button("Mit Google fortfahren", url, use_container_width=True)
    st.markdown('<div class="auth-divider">oder</div>', unsafe_allow_html=True)


def _render_login_form() -> None:
    st.markdown(
        '<div class="auth-intro"><p class="auth-title">Willkommen zurück</p></div>',
        unsafe_allow_html=True,
    )
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input(
            "Benutzername",
            placeholder="Benutzername",
            key="auth_user",
            label_visibility="collapsed",
        )
        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="Passwort",
            key="auth_pass",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
    if submitted:
        do_login(username, password)


def _render_register_form() -> None:
    st.markdown(
        '<div class="auth-intro">'
        '<p class="auth-title">Konto erstellen</p>'
        '<p class="auth-sub">Kostenlos starten — in unter einer Minute.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input(
            "Benutzername",
            placeholder="Benutzername wählen",
            key="reg_user",
            label_visibility="collapsed",
        )
        email = st.text_input(
            "E-Mail",
            placeholder="name@beispiel.de",
            key="reg_email",
            label_visibility="collapsed",
        )
        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="Passwort",
            key="reg_pass",
            label_visibility="collapsed",
        )
        password2 = st.text_input(
            "Passwort bestätigen",
            type="password",
            placeholder="Passwort bestätigen",
            key="reg_pass2",
            label_visibility="collapsed",
        )
        terms = st.checkbox("Ich akzeptiere die AGB und die Datenschutzerklärung", key="reg_terms")
        submitted = st.form_submit_button("Kostenlos registrieren", type="primary", use_container_width=True)
    if submitted:
        do_register(
            username=username,
            email=email,
            password=password,
            password2=password2,
            terms=terms,
        )


def render_auth() -> None:
    if _get_mode() not in ("login", "register"):
        _set_mode("login")
    elif "gate_mode" not in st.session_state:
        _set_mode("login")

    if "auth_mode_seg" not in st.session_state:
        st.session_state.auth_mode_seg = "Registrieren" if _get_mode() == "register" else "Anmelden"

    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">',
        unsafe_allow_html=True,
    )
    inject_css(_AUTH_CSS)
    st.markdown('<div class="auth-bg" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    with st.container(key="auth_card", border=False):
        st.markdown('<span class="auth-card-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="auth-header">'
            f'<p class="auth-brand">{_APP}</p>'
            f'<p class="auth-tagline">{_TAGLINE}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )

        with st.container(key="auth_seg_wrap"):
            choice = st.segmented_control(
                label=" ",
                options=["Anmelden", "Registrieren"],
                key="auth_mode_seg",
                label_visibility="collapsed",
            )

        mode = "register" if choice == "Registrieren" else "login"
        st.session_state.gate_mode = mode
        st.session_state.auth_mode = mode

        _show_notice()
        _render_oauth_section()

        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()

        st.markdown(
            '<p class="auth-footer">Verschlüsselte Übertragung · SSL/TLS</p>',
            unsafe_allow_html=True,
        )
