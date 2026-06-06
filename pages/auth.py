"""MaByte Auth — Login & Registrierung."""
from __future__ import annotations

import html

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

_AUTH_CSS = """
:root {
    --auth-bg: #09090b;
    --auth-surface: rgba(24, 24, 27, 0.97);
    --auth-line: rgba(255, 255, 255, 0.09);
    --auth-text: #fafafa;
    --auth-muted: #a1a1aa;
    --auth-hint: #71717a;
    --auth-field: #0c0c0f;
    --auth-field-line: rgba(255, 255, 255, 0.11);
    --auth-accent: #7c3aed;
    --auth-accent-hover: #6d28d9;
    --auth-radius: 10px;
    --auth-input-h: 44px;
    --auth-pad: 36px;
    --auth-w: 420px;
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
        radial-gradient(ellipse 75% 55% at 50% -18%, rgba(124, 58, 237, 0.15), transparent 60%),
        var(--auth-bg);
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
    padding: 24px 16px !important;
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
    border-radius: 14px !important;
    border: 1px solid var(--auth-line) !important;
    background: var(--auth-surface) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.06),
        0 24px 48px -16px rgba(0, 0, 0, 0.55) !important;
    padding: var(--auth-pad) !important;
    gap: 0 !important;
    align-items: stretch !important;
    overflow: hidden !important;
}

html:has(.auth-marker) .st-key-auth_card > [data-testid="stVerticalBlock"]:has(.auth-card-marker)::before {
    content: "";
    position: absolute;
    top: 0;
    left: 15%;
    right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.5), transparent);
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

.auth-brand {
    margin: 0;
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.15;
    color: var(--auth-text) !important;
}

.auth-tagline {
    margin: 6px 0 0;
    text-align: center;
    font-size: 13px;
    font-weight: 400;
    line-height: 1.4;
    color: var(--auth-hint) !important;
}

.auth-header {
    margin: 0 0 24px;
}

html:has(.auth-marker) .st-key-auth_seg_wrap {
    margin: 0 0 24px !important;
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
    background: rgba(0, 0, 0, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: var(--auth-radius) !important;
    padding: 3px !important;
    gap: 2px !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] button,
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] button {
    flex: 1 !important;
    min-height: 36px !important;
    height: 36px !important;
    border: none !important;
    outline: none !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--auth-muted) !important;
    box-shadow: none !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] button[aria-selected="true"],
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] button[aria-selected="true"] {
    background: rgba(255, 255, 255, 0.11) !important;
    color: var(--auth-text) !important;
}

.auth-intro {
    margin: 0 0 16px;
    text-align: center;
}

.auth-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.3;
    color: var(--auth-text) !important;
}

.auth-sub {
    margin: 6px 0 0;
    font-size: 13px;
    line-height: 1.45;
    color: var(--auth-muted) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    gap: 16px !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] {
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] label p,
html:has(.auth-marker) .st-key-auth_card [data-testid="stWidgetLabel"] p {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--auth-muted) !important;
    margin: 0 0 6px !important;
    line-height: 1.35 !important;
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
    font-size: 14px !important;
    padding: 0 40px 0 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_card .st-key-auth_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_email input {
    padding-right: 12px !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input::placeholder {
    color: var(--auth-hint) !important;
    opacity: 1 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:focus {
    border-color: rgba(124, 58, 237, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.14) !important;
    outline: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] {
    position: absolute !important;
    right: 4px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 30px !important;
    height: 30px !important;
    min-height: 30px !important;
    padding: 0 !important;
    border: none !important;
    border-radius: 6px !important;
    background: transparent !important;
    color: var(--auth-muted) !important;
    box-shadow: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: var(--auth-text) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] label p {
    font-size: 12px !important;
    color: var(--auth-muted) !important;
    line-height: 1.4 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] {
    margin-top: 8px !important;
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
    font-size: 14px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button:hover,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"]:hover {
    background: var(--auth-accent-hover) !important;
    background-image: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button p,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"] p {
    color: #fff !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stAlert"] {
    border-radius: var(--auth-radius) !important;
    font-size: 13px !important;
    margin: 0 0 16px !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

.auth-footer {
    margin: 20px 0 0;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    font-size: 11px;
    color: var(--auth-hint) !important;
}

html:has(.auth-marker) .stApp {
    --background-color: #09090b !important;
    --primary-color: #7c3aed !important;
}

@media (max-width: 640px) {
    html:has(.auth-marker) {
        --auth-pad: 24px;
    }
    html:has(.auth-marker) .auth-brand { font-size: 24px; }
    html:has(.auth-marker) [data-testid="stMain"] {
        justify-content: flex-start !important;
        padding-top: 16px !important;
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


def _render_login_form() -> None:
    st.markdown(
        '<div class="auth-intro">'
        '<p class="auth-title">Willkommen zurück</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", placeholder="Benutzername", key="auth_user")
        password = st.text_input("Passwort", type="password", placeholder="Passwort", key="auth_pass")
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
        username = st.text_input("Benutzername", placeholder="z. B. max_mustermann", key="reg_user")
        email = st.text_input("E-Mail", placeholder="name@beispiel.de", key="reg_email")
        password = st.text_input("Passwort", type="password", placeholder="Sicheres Passwort", key="reg_pass")
        password2 = st.text_input(
            "Passwort bestätigen",
            type="password",
            placeholder="Passwort wiederholen",
            key="reg_pass2",
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
            f'<p class="auth-tagline">Dein KI-Workspace</p>'
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

        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()

        st.markdown(
            '<p class="auth-footer">Verschlüsselte Übertragung</p>',
            unsafe_allow_html=True,
        )
