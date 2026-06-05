"""MaByte Auth — Premium Enterprise Login (Streamlit + Tailwind-Design-Tokens)."""
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
_SLOGAN_HEADER = Path(__file__).resolve().parent.parent / "assets" / "sloganheader.png"

_LOGO_SVG = (
    '<svg class="auth-logo-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" '
    'width="44" height="44" aria-hidden="true">'
    '<defs><linearGradient id="authLogo" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#a78bfa"/><stop offset="50%" stop-color="#7c3aed"/>'
    '<stop offset="100%" stop-color="#6366f1"/></linearGradient></defs>'
    '<rect width="44" height="44" rx="12" fill="url(#authLogo)"/>'
    '<path d="M13 31V13l7 9 7-9v18" fill="none" stroke="#fff" stroke-width="2.5" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)

# Tailwind-inspirierte Design-Tokens (scoped CSS — optimiert für Streamlit)
_AUTH_CSS = """
:root {
    --auth-bg: #030712;
    --auth-surface: rgba(12, 12, 18, 0.72);
    --auth-border: rgba(255, 255, 255, 0.08);
    --auth-border-focus: rgba(167, 139, 250, 0.55);
    --auth-input: rgba(9, 9, 11, 0.92);
    --auth-muted: #71717a;
    --auth-text: #fafafa;
    --auth-soft: #d4d4d8;
    --auth-violet: #7c3aed;
    --auth-indigo: #6366f1;
    --auth-ring: rgba(124, 58, 237, 0.35);
    --auth-ease: cubic-bezier(0.4, 0, 0.2, 1);
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: var(--auth-bg) !important;
    color: var(--auth-text) !important;
}
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    display: none !important;
}

.auth-glow {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    overflow: hidden;
}
.auth-glow::before {
    content: "";
    position: absolute;
    width: 680px; height: 680px;
    top: -220px; left: 50%;
    transform: translateX(-50%);
    background: radial-gradient(circle, rgba(124, 58, 237, 0.22) 0%, transparent 68%);
    animation: authGlowPulse 9s var(--auth-ease) infinite;
}
.auth-glow::after {
    content: "";
    position: absolute;
    width: 520px; height: 520px;
    bottom: -180px; right: -120px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.14) 0%, transparent 70%);
    animation: authGlowDrift 12s var(--auth-ease) infinite alternate;
}
@keyframes authGlowPulse {
    0%, 100% { opacity: 0.55; transform: translateX(-50%) scale(1); }
    50% { opacity: 0.95; transform: translateX(-50%) scale(1.08); }
}
@keyframes authGlowDrift {
    from { opacity: 0.35; transform: translate(0, 0); }
    to { opacity: 0.7; transform: translate(-40px, -20px); }
}

[data-testid="stMain"] {
    position: relative !important;
    z-index: 1 !important;
}
[data-testid="stMain"] .block-container,
[data-testid="stMainBlockContainer"] {
    max-width: 440px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: clamp(1.75rem, 7vh, 3.5rem) 1.15rem 2rem !important;
}

[data-testid="stVerticalBlock"]:has(.auth-marker) { gap: 0 !important; }

[data-testid="stVerticalBlock"]:has(.auth-glass-marker) {
    padding: 0 !important;
    border-radius: 20px !important;
    background: var(--auth-surface) !important;
    border: 1px solid var(--auth-border) !important;
    backdrop-filter: blur(24px) saturate(1.25) !important;
    -webkit-backdrop-filter: blur(24px) saturate(1.25) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.06),
        0 0 0 1px rgba(139, 92, 246, 0.1),
        0 24px 56px rgba(0, 0, 0, 0.42) !important;
    overflow: hidden !important;
    gap: 0 !important;
}

.auth-card-head {
    padding: 1.35rem 1.35rem 1.1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, transparent 100%);
}
.auth-slogan {
    margin: 0 0 1rem;
    line-height: 0;
    text-align: center;
}
.auth-slogan img {
    width: 100%;
    max-height: 40px;
    height: auto;
    object-fit: contain;
    display: inline-block;
    opacity: 0.95;
}
.auth-brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
}
.auth-logo-wrap {
    position: relative;
    flex-shrink: 0;
    line-height: 0;
}
.auth-logo-wrap::after {
    content: "";
    position: absolute;
    inset: -6px;
    border-radius: 16px;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.35), transparent 70%);
    filter: blur(8px);
    z-index: -1;
}
.auth-logo-svg { display: block; filter: drop-shadow(0 6px 16px rgba(124, 58, 237, 0.35)); }
.auth-brand-name {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.035em;
    line-height: 1.1;
    color: var(--auth-text);
}
.auth-brand-tag {
    margin: 4px 0 0;
    font-size: 0.6875rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--auth-muted);
}

.auth-card-body {
    padding: 1.15rem 1.35rem 1.25rem;
}

.auth-mode-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 1.1rem;
    padding: 4px;
    border-radius: 12px;
    background: rgba(9, 9, 11, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register {
    margin: 0 !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton>button,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton>button {
    width: 100% !important;
    min-height: 38px !important;
    border-radius: 9px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: var(--auth-muted) !important;
    font-size: 0.8125rem !important;
    font-weight: 600 !important;
    transition: color 0.2s var(--auth-ease), background 0.2s var(--auth-ease),
                border-color 0.2s var(--auth-ease), box-shadow 0.2s var(--auth-ease) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton>button p,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton>button p {
    color: inherit !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton>button:hover,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton>button:hover {
    color: var(--auth-soft) !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}

.auth-form-title {
    margin: 0 0 0.35rem;
    font-size: 1.0625rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--auth-text);
}
.auth-form-sub {
    margin: 0 0 1rem;
    font-size: 0.8125rem;
    color: var(--auth-muted);
    line-height: 1.45;
}

[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] label p,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stWidgetLabel"] p {
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    color: var(--auth-soft) !important;
    margin-bottom: 6px !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] textarea {
    background: var(--auth-input) !important;
    background-color: var(--auth-input) !important;
    color: var(--auth-text) !important;
    border: 1px solid rgba(63, 63, 70, 0.85) !important;
    border-radius: 10px !important;
    min-height: 46px !important;
    font-size: 0.9375rem !important;
    caret-color: #c4b5fd !important;
    transition: border-color 0.2s var(--auth-ease), box-shadow 0.2s var(--auth-ease),
                background 0.2s var(--auth-ease) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:hover {
    border-color: rgba(113, 113, 122, 0.95) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:focus,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:focus-visible {
    border-color: var(--auth-border-focus) !important;
    box-shadow: 0 0 0 3px var(--auth-ring) !important;
    outline: none !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill:hover,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #09090b inset !important;
    -webkit-text-fill-color: #fafafa !important;
    transition: background-color 9999s ease-out 0s !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) div[data-baseweb="input"],
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] > div {
    background: transparent !important;
    border: none !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stCheckbox"] label p {
    font-size: 0.8125rem !important;
    color: var(--auth-soft) !important;
}

[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"] {
    width: 100% !important;
    min-height: 46px !important;
    margin-top: 0.35rem !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 48%, #6366f1 100%) !important;
    color: #fff !important;
    font-size: 0.9375rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.32) !important;
    transition: transform 0.18s var(--auth-ease), box-shadow 0.18s var(--auth-ease),
                filter 0.18s var(--auth-ease) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button:hover,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 28px rgba(124, 58, 237, 0.42) !important;
    filter: brightness(1.04) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button:active,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button p,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"] p {
    color: #fff !important;
    font-weight: 600 !important;
}

[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stAlert"] {
    margin-bottom: 0.75rem !important;
    border-radius: 10px !important;
    font-size: 0.875rem !important;
}

.auth-card-foot {
    padding: 0.85rem 1.35rem 1.1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    background: rgba(0, 0, 0, 0.15);
}
.auth-ssl {
    margin: 0;
    font-size: 0.6875rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    color: #52525b;
}

@media (max-width: 480px) {
    [data-testid="stMain"] .block-container {
        padding: 1.25rem 0.85rem 1.75rem !important;
    }
    .auth-card-head { padding: 1.1rem 1rem 0.95rem; }
    .auth-card-body { padding: 1rem 1rem 1.1rem; }
    .auth-brand-name { font-size: 1.3rem; }
    .auth-slogan img { max-height: 34px; }
}

@media (prefers-reduced-motion: reduce) {
    .auth-glow::before, .auth-glow::after { animation: none !important; }
    [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input,
    [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button {
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


def _card_head_html() -> str:
    encoded = _img_base64(_SLOGAN_HEADER)
    slogan = ""
    if encoded:
        slogan = (
            f'<div class="auth-slogan">'
            f'<img src="data:image/png;base64,{encoded}" '
            'alt="One System. Infinite Intelligence." />'
            "</div>"
        )
    return (
        '<div class="auth-card-head">'
        f"{slogan}"
        '<div class="auth-brand">'
        f'<div class="auth-logo-wrap">{_LOGO_SVG}</div>'
        "<div>"
        f'<p class="auth-brand-name">{_APP}</p>'
        '<p class="auth-brand-tag">Enterprise AI Platform</p>'
        "</div></div></div>"
    )


def _tab_highlight_css(mode: str) -> str:
    active = (
        ".st-key-auth_tab_login button[kind=\"secondary\"],"
        ".st-key-auth_tab_login button[kind=\"tertiary\"]"
        if mode == "login"
        else ".st-key-auth_tab_register button[kind=\"secondary\"],"
        ".st-key-auth_tab_register button[kind=\"tertiary\"]"
    )
    return f"""
{active} {{
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.28), rgba(99, 102, 241, 0.18)) !important;
    border: 1px solid rgba(167, 139, 250, 0.35) !important;
    color: #fafafa !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.2) !important;
}}
{active} p {{ color: #fafafa !important; }}
"""


def _render_mode_tabs(mode: str) -> None:
    tab_cols = st.columns(2, gap="small")
    with tab_cols[0]:
        if st.button("Anmelden", key="auth_tab_login", use_container_width=True, type="secondary"):
            if mode != "login":
                _set_mode("login")
                st.rerun()
    with tab_cols[1]:
        if st.button("Registrieren", key="auth_tab_register", use_container_width=True, type="secondary"):
            if mode != "register":
                _set_mode("register")
                st.rerun()


def _render_login_form() -> None:
    st.markdown(
        '<p class="auth-form-title">Willkommen zurück</p>'
        '<p class="auth-form-sub">Melde dich mit deinem MaByte-Konto an.</p>',
        unsafe_allow_html=True,
    )
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="auth_user")
        password = st.text_input("Passwort", type="password", key="auth_pass")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
    if submitted:
        do_login(username, password)


def _render_register_form() -> None:
    st.markdown(
        '<p class="auth-form-title">Konto erstellen</p>'
        '<p class="auth-form-sub">Registriere dich und starte direkt in der Plattform.</p>',
        unsafe_allow_html=True,
    )
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="reg_user")
        email = st.text_input("E-Mail", key="reg_email")
        password = st.text_input("Passwort", type="password", key="reg_pass")
        password2 = st.text_input("Passwort bestätigen", type="password", key="reg_pass2")
        terms = st.checkbox("AGB und Datenschutz akzeptieren", key="reg_terms")
        submitted = st.form_submit_button("Registrieren", type="primary", use_container_width=True)
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

    inject_css(_AUTH_CSS)
    mode = _get_mode()
    inject_css(_tab_highlight_css(mode))

    st.markdown('<div class="auth-glow" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<span class="auth-glass-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)
        st.markdown(_card_head_html(), unsafe_allow_html=True)
        st.markdown('<div class="auth-card-body">', unsafe_allow_html=True)
        st.markdown('<div class="auth-mode-row">', unsafe_allow_html=True)
        _render_mode_tabs(mode)
        st.markdown("</div>", unsafe_allow_html=True)
        _show_notice()
        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-card-foot">'
            '<p class="auth-ssl">🔒 SSL-verschlüsselte Verbindung</p>'
            "</div>",
            unsafe_allow_html=True,
        )
