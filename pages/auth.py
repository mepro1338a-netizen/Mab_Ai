"""MaByte Auth — Login & Registrierung (Streamlit, sauberes Layout)."""
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
/* ── 8px Grid Design System (Enterprise SaaS) ── */
:root {
    --auth-bg: #09090b;
    --auth-card: rgba(24, 24, 27, 0.92);
    --auth-border: rgba(255, 255, 255, 0.08);
    --auth-text: #fafafa;
    --auth-muted: #a1a1aa;
    --auth-hint: #71717a;
    --auth-field: rgba(9, 9, 11, 0.85);
    --auth-field-border: rgba(255, 255, 255, 0.1);
    --auth-accent: #8b5cf6;
    --auth-accent-2: #6366f1;
    --s-1: 8px;
    --s-2: 16px;
    --s-3: 24px;
    --s-4: 32px;
    --s-5: 40px;
    --s-6: 48px;
    --auth-pad: 44px;
    --auth-radius: 12px;
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
        radial-gradient(ellipse 80% 55% at 50% -10%, rgba(139, 92, 246, 0.09), transparent 55%),
        var(--auth-bg);
}

html:has(.auth-marker) [data-testid="stMain"] {
    position: relative !important;
    z-index: 1 !important;
}

html:has(.auth-marker) [data-testid="stMain"] .block-container,
html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
    max-width: 560px !important;
    width: min(560px, 100%) !important;
    margin: 0 auto !important;
    padding: var(--s-6) var(--s-3) var(--s-5) !important;
}

/* ── Card ── */
html:has(.auth-marker) .st-key-auth_card[data-testid="stVerticalBlockBorderWrapper"],
html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.auth-card-marker) {
    border-radius: var(--auth-radius) !important;
    border: 1px solid var(--auth-border) !important;
    background: var(--auth-card) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 24px 48px rgba(0, 0, 0, 0.4) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card[data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"],
html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.auth-card-marker) > [data-testid="stVerticalBlock"] {
    padding: var(--auth-pad) !important;
    gap: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Brand (36px) ── */
.auth-brand {
    margin: 0 0 var(--s-4);
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--auth-text) !important;
}

/* ── Segmented control ── */
html:has(.auth-marker) .st-key-auth_seg_wrap {
    margin: 0 0 var(--s-4) !important;
}
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"],
html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] {
    width: 100% !important;
    background: rgba(0, 0, 0, 0.35) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] button,
html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] button {
    flex: 1 !important;
    min-height: 44px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--auth-muted) !important;
}
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stSegmentedControl"] button[aria-selected="true"],
html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stSegmentedControl"] button[aria-selected="true"] {
    background: rgba(255, 255, 255, 0.08) !important;
    color: var(--auth-text) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

/* ── Intro: Headline 30px → Sub 16px (12px gap) → Form 32px ── */
.auth-intro {
    margin: 0 0 var(--s-4);
    text-align: left;
}
.auth-headline {
    margin: 0 0 12px;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.2;
    color: var(--auth-text) !important;
}
.auth-desc {
    margin: 0;
    font-size: 16px;
    font-weight: 400;
    line-height: 1.5;
    color: var(--auth-muted) !important;
}

/* ── Form stack ── */
html:has(.auth-marker) .st-key-auth_card [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    gap: var(--s-3) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] label p,
html:has(.auth-marker) .st-key-auth_card [data-testid="stWidgetLabel"] p {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--auth-muted) !important;
    margin: 0 0 var(--s-1) !important;
    line-height: 1.4 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] > div,
html:has(.auth-marker) .st-key-auth_card div[data-baseweb="input"] {
    position: relative !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input {
    background: var(--auth-field) !important;
    background-color: var(--auth-field) !important;
    color: var(--auth-text) !important;
    -webkit-text-fill-color: var(--auth-text) !important;
    border: 1px solid var(--auth-field-border) !important;
    border-radius: var(--auth-radius) !important;
    min-height: var(--s-6) !important;
    height: var(--s-6) !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
    box-shadow: none !important;
    padding: 0 48px 0 var(--s-2) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_card .st-key-auth_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_email input {
    padding-right: var(--s-2) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input::placeholder {
    color: var(--auth-hint) !important;
    opacity: 1 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:focus {
    border-color: rgba(139, 92, 246, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.12) !important;
    outline: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] {
    position: absolute !important;
    right: var(--s-1) !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 36px !important;
    height: 36px !important;
    min-height: 36px !important;
    padding: 0 !important;
    border: none !important;
    border-radius: var(--s-1) !important;
    background: transparent !important;
    color: var(--auth-muted) !important;
    box-shadow: none !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    color: var(--auth-text) !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button svg {
    width: 18px !important;
    height: 18px !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] {
    margin: 0 !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] label p {
    font-size: 14px !important;
    font-weight: 400 !important;
    color: var(--auth-muted) !important;
    line-height: 1.5 !important;
}

/* Form → Button = 32px (24px gap + 8px) */
html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] {
    margin-top: var(--s-1) !important;
    padding-top: 0 !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"] {
    width: 100% !important;
    min-height: var(--s-6) !important;
    height: var(--s-6) !important;
    border: none !important;
    border-radius: var(--auth-radius) !important;
    background: linear-gradient(135deg, var(--auth-accent), var(--auth-accent-2)) !important;
    background-image: linear-gradient(135deg, var(--auth-accent), var(--auth-accent-2)) !important;
    color: #fff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2), 0 8px 24px rgba(139, 92, 246, 0.22) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button:hover,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2), 0 12px 28px rgba(139, 92, 246, 0.3) !important;
}
html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] button p,
html:has(.auth-marker) .st-key-auth_card button[data-testid="baseButton-primary"] p {
    color: #fff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stAlert"] {
    border-radius: var(--auth-radius) !important;
    font-size: 14px !important;
    margin: 0 0 var(--s-2) !important;
}

/* Button → Footer = 24px (margin) + divider + 12px (padding) */
.auth-footer {
    margin: var(--s-3) 0 0;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.5;
    color: var(--auth-hint) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}

html:has(.auth-marker) .stApp {
    --background-color: #09090b !important;
    --primary-color: #8b5cf6 !important;
}

@media (max-width: 640px) {
    html:has(.auth-marker) {
        --auth-pad: var(--s-5);
    }
    html:has(.auth-marker) .auth-brand { font-size: 30px; }
    html:has(.auth-marker) .auth-headline { font-size: 24px; }
    html:has(.auth-marker) [data-testid="stMain"] .block-container {
        padding: var(--s-4) var(--s-2) var(--s-5) !important;
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
        '<p class="auth-headline">Willkommen zurück</p>'
        '<p class="auth-desc">Melde dich an, um in deinem Workspace weiterzumachen.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", placeholder="Dein Benutzername", key="auth_user")
        password = st.text_input("Passwort", type="password", placeholder="Dein Passwort", key="auth_pass")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
    if submitted:
        do_login(username, password)


def _render_register_form() -> None:
    st.markdown(
        '<div class="auth-intro">'
        '<p class="auth-headline">Konto erstellen</p>'
        '<p class="auth-desc">Registriere dich kostenlos und starte sofort.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input(
            "Benutzername",
            placeholder="z. B. max_mustermann",
            key="reg_user",
        )
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

    mode = _get_mode()
    if "auth_mode_seg" not in st.session_state:
        st.session_state.auth_mode_seg = "Registrieren" if mode == "register" else "Anmelden"

    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">',
        unsafe_allow_html=True,
    )
    inject_css(_AUTH_CSS)

    st.markdown('<div class="auth-bg" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    with st.container(key="auth_card", border=False):
        st.markdown('<span class="auth-card-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

        st.markdown(f'<p class="auth-brand">{_APP}</p>', unsafe_allow_html=True)

        with st.container(key="auth_seg_wrap"):
            choice = st.segmented_control(
                label="Modus",
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
            '<p class="auth-footer">Deine Daten werden verschlüsselt übertragen.</p>',
            unsafe_allow_html=True,
        )
