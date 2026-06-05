"""MaByte Auth — benutzerfreundliches Login & Registrierung (Streamlit)."""
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
    --ux-bg: #0b0f19;
    --ux-card: rgba(17, 24, 39, 0.82);
    --ux-border: rgba(255, 255, 255, 0.1);
    --ux-text: #f9fafb;
    --ux-muted: #9ca3af;
    --ux-hint: #6b7280;
    --ux-input: rgba(15, 23, 42, 0.85);
    --ux-input-border: rgba(255, 255, 255, 0.08);
    --ux-focus: rgba(139, 92, 246, 0.45);
    --ux-focus-ring: rgba(139, 92, 246, 0.18);
    --ux-accent: #8b5cf6;
    --ux-accent-2: #6366f1;
    --ux-pad: 2rem;
    --ux-ease: cubic-bezier(0.4, 0, 0.2, 1);
}

html:has(.auth-marker),
html:has(.auth-marker) body,
html:has(.auth-marker) .stApp,
html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"],
html:has(.auth-marker) section.main .block-container,
html:has(.auth-marker) [data-testid="stMain"] .block-container {
    background: var(--ux-bg) !important;
    background-color: var(--ux-bg) !important;
    background-image: none !important;
    color: var(--ux-text) !important;
    font-family: "Inter", system-ui, -apple-system, sans-serif !important;
}

html:has(.auth-marker) #MainMenu,
html:has(.auth-marker) footer,
html:has(.auth-marker) [data-testid="stToolbar"],
html:has(.auth-marker) [data-testid="stDecoration"],
html:has(.auth-marker) [data-testid="stSidebar"],
html:has(.auth-marker) [data-testid="stHeader"] {
    display: none !important;
}

.ux-bg {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 80% 50% at 15% 20%, rgba(139, 92, 246, 0.14), transparent 55%),
        radial-gradient(ellipse 70% 45% at 85% 75%, rgba(99, 102, 241, 0.1), transparent 50%),
        var(--ux-bg);
}

html:has(.auth-marker) [data-testid="stMain"] {
    position: relative !important;
    z-index: 1 !important;
}
html:has(.auth-marker) [data-testid="stMain"] .block-container,
html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
    max-width: 440px !important;
    width: min(440px, 100%) !important;
    margin: 0 auto !important;
    padding: clamp(1.75rem, 7vh, 3rem) 1rem 2rem !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.auth-shell-marker),
html:has(.auth-marker) .st-key-auth_shell[data-testid="stVerticalBlockBorderWrapper"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) {
    position: relative !important;
    padding: 0 !important;
    border-radius: 20px !important;
    background: var(--ux-card) !important;
    border: 1px solid var(--ux-border) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(255,255,255,0.04) inset !important;
    overflow: hidden !important;
    gap: 0 !important;
}

.ux-head {
    padding: 2rem var(--ux-pad) 0.25rem;
    text-align: center;
}
.ux-brand {
    margin: 0 0 0.35rem;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--ux-text) !important;
}
.ux-tagline {
    margin: 0;
    font-size: 0.8125rem;
    color: var(--ux-muted) !important;
    line-height: 1.4;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stHorizontalBlock"]:has(.st-key-auth_tab_login) {
    background: rgba(0, 0, 0, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    margin: 1.25rem var(--ux-pad) 0 !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_tab_login .stButton > button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_tab_register .stButton > button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_tab_login button[data-testid="baseButton-secondary"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_tab_register button[data-testid="baseButton-secondary"] {
    min-height: 44px !important;
    border-radius: 9px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    background-color: transparent !important;
    color: var(--ux-muted) !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: background 0.2s var(--ux-ease), color 0.2s var(--ux-ease), border-color 0.2s var(--ux-ease) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_tab_login .stButton > button p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_tab_register .stButton > button p {
    color: inherit !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stAlert"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stForm"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_show_pass,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-reg_show_pass,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_user,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_pass,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_submit_login,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stMarkdownContainer"]:has(.ux-form-head) {
    margin-left: var(--ux-pad) !important;
    margin-right: var(--ux-pad) !important;
}

.ux-form-head { padding: 1.25rem 0 0.25rem; }
.ux-form-title {
    margin: 0 0 0.35rem;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--ux-text) !important;
    letter-spacing: -0.02em;
}
.ux-form-sub {
    margin: 0 0 0.75rem;
    font-size: 0.875rem;
    color: var(--ux-muted) !important;
    line-height: 1.45;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stTextInput"] label p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stWidgetLabel"] p {
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    color: var(--ux-muted) !important;
    margin-bottom: 6px !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stTextInput"] input,
html:has(.auth-marker) section.main:has(.auth-marker) .stTextInput input {
    background: var(--ux-input) !important;
    background-color: var(--ux-input) !important;
    color: var(--ux-text) !important;
    -webkit-text-fill-color: var(--ux-text) !important;
    border: 1px solid var(--ux-input-border) !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    font-size: 0.9375rem !important;
    transition: border-color 0.2s var(--ux-ease), box-shadow 0.2s var(--ux-ease) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stTextInput"] input::placeholder {
    color: var(--ux-hint) !important;
    opacity: 1 !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stTextInput"] input:focus {
    border-color: var(--ux-focus) !important;
    box-shadow: 0 0 0 3px var(--ux-focus-ring) !important;
    outline: none !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) div[data-baseweb="input"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stTextInput"] > div {
    background: transparent !important;
    border: none !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_show_pass label p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-reg_show_pass label p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stCheckbox"] label p {
    font-size: 0.8125rem !important;
    color: var(--ux-muted) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_show_pass,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-reg_show_pass {
    margin-top: -0.25rem !important;
    margin-bottom: 0.25rem !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stForm"] {
    border: none !important;
    padding: 0 0 0.5rem !important;
    background: transparent !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stFormSubmitButton"] button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_submit_login .stButton > button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) button[data-testid="baseButton-primary"] {
    width: 100% !important;
    min-height: 48px !important;
    margin-top: 0.5rem !important;
    border-radius: 10px !important;
    border: none !important;
    background: linear-gradient(135deg, var(--ux-accent), var(--ux-accent-2)) !important;
    background-image: linear-gradient(135deg, var(--ux-accent), var(--ux-accent-2)) !important;
    color: #fff !important;
    font-size: 0.9375rem !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.28) !important;
    transition: transform 0.18s var(--ux-ease), box-shadow 0.18s var(--ux-ease) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stFormSubmitButton"] button:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_submit_login .stButton > button:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 28px rgba(139, 92, 246, 0.38) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stFormSubmitButton"] button p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) .st-key-auth_submit_login .stButton > button p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) button[data-testid="baseButton-primary"] p {
    color: #fff !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-shell-marker) [data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.5rem !important;
}

.ux-foot {
    padding: 0.75rem var(--ux-pad) 1.25rem;
    text-align: center;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.ux-foot p {
    margin: 0;
    font-size: 0.6875rem;
    color: var(--ux-hint) !important;
    line-height: 1.4;
}

@media (max-width: 480px) {
    html:has(.auth-marker) { --ux-pad: 1.25rem; }
    html:has(.auth-marker) [data-testid="stMain"] .block-container {
        padding: 1.25rem 0.75rem 1.5rem !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    html:has(.auth-marker) [data-testid="stFormSubmitButton"] button {
        transition: none !important;
    }
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
    _set_notice("error", login_msg or "Benutzername oder Passwort stimmen nicht. Bitte erneut versuchen.")


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
        _set_notice(
            "error",
            "Benutzername: 3–40 Zeichen, nur Buchstaben, Zahlen oder Unterstrich (_).",
        )
        return

    if not is_valid_email(email):
        _set_notice("error", "Bitte gib eine gültige E-Mail-Adresse ein.")
        return

    if not terms:
        _set_notice("error", "Bitte bestätige AGB und Datenschutz, um fortzufahren.")
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


def _tab_active_css(mode: str) -> str:
    key = "auth_tab_login" if mode == "login" else "auth_tab_register"
    return f"""
html:has(.auth-marker) .st-key-{key} .stButton > button,
html:has(.auth-marker) .st-key-{key} button[data-testid="baseButton-secondary"] {{
    background: rgba(139, 92, 246, 0.15) !important;
    background-color: rgba(139, 92, 246, 0.15) !important;
    border-color: rgba(139, 92, 246, 0.35) !important;
    color: var(--ux-text) !important;
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.12) !important;
}}
html:has(.auth-marker) .st-key-{key} .stButton > button p {{
    color: var(--ux-text) !important;
}}
"""


def _render_tabs(mode: str) -> None:
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("Anmelden", key="auth_tab_login", use_container_width=True, type="secondary"):
            if mode != "login":
                _set_mode("login")
                st.rerun()
    with c2:
        if st.button("Registrieren", key="auth_tab_register", use_container_width=True, type="secondary"):
            if mode != "register":
                _set_mode("register")
                st.rerun()


def _password_type(show_key: str) -> str:
    return "default" if st.session_state.get(show_key) else "password"


def _render_login_form() -> None:
    st.markdown(
        '<div class="ux-form-head">'
        '<p class="ux-form-title">Schön, dass du da bist</p>'
        '<p class="ux-form-sub">Melde dich an, um in deinem Workspace weiterzumachen.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    username = st.text_input(
        "Benutzername",
        key="auth_user",
        placeholder="Dein Benutzername",
    )
    st.checkbox("Passwort anzeigen", key="auth_show_pass")
    password = st.text_input(
        "Passwort",
        type=_password_type("auth_show_pass"),
        key="auth_pass",
        placeholder="Dein Passwort",
    )
    if st.button("Anmelden", key="auth_submit_login", type="primary", use_container_width=True):
        do_login(username, password)


def _render_register_form() -> None:
    st.markdown(
        '<div class="ux-form-head">'
        '<p class="ux-form-title">Konto erstellen</p>'
        '<p class="ux-form-sub">In weniger als einer Minute startklar — kostenlos registrieren.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.checkbox("Passwörter anzeigen", key="reg_show_pass")
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input(
            "Benutzername",
            key="reg_user",
            placeholder="z. B. max_mustermann",
            help="3–40 Zeichen: Buchstaben, Zahlen oder Unterstrich",
        )
        email = st.text_input(
            "E-Mail",
            key="reg_email",
            placeholder="name@beispiel.de",
        )
        pw_type = _password_type("reg_show_pass")
        password = st.text_input(
            "Passwort",
            type=pw_type,
            key="reg_pass",
            placeholder="Sicheres Passwort wählen",
        )
        password2 = st.text_input(
            "Passwort bestätigen",
            type=pw_type,
            key="reg_pass2",
            placeholder="Passwort wiederholen",
        )
        terms = st.checkbox(
            "Ich akzeptiere die AGB und die Datenschutzerklärung",
            key="reg_terms",
        )
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

    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">',
        unsafe_allow_html=True,
    )
    inject_css(_AUTH_CSS)
    inject_css(_tab_active_css(mode))

    st.markdown('<div class="ux-bg" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    with st.container(key="auth_shell", border=False):
        st.markdown('<span class="auth-shell-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ux-head">'
            f'<p class="ux-brand">{_APP}</p>'
            f'<p class="ux-tagline">Dein KI-Workspace — einfach anmelden und loslegen.</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
        _render_tabs(mode)
        _show_notice()
        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()
        st.markdown(
            '<div class="ux-foot"><p>Deine Daten werden verschlüsselt übertragen.</p></div>',
            unsafe_allow_html=True,
        )
