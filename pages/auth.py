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
    'width="52" height="52" aria-hidden="true">'
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
    --auth-surface: rgba(14, 14, 22, 0.78);
    --auth-surface-2: rgba(255, 255, 255, 0.03);
    --auth-border: rgba(255, 255, 255, 0.09);
    --auth-border-focus: rgba(167, 139, 250, 0.65);
    --auth-input: rgba(255, 255, 255, 0.04);
    --auth-input-hover: rgba(255, 255, 255, 0.06);
    --auth-muted: #71717a;
    --auth-placeholder: #6b7280;
    --auth-text: #fafafa;
    --auth-soft: #d4d4d8;
    --auth-violet: #8b5cf6;
    --auth-indigo: #6366f1;
    --auth-ring: rgba(139, 92, 246, 0.38);
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
    width: 820px; height: 820px;
    top: -280px; left: 50%;
    transform: translateX(-50%);
    background: radial-gradient(circle, rgba(139, 92, 246, 0.26) 0%, rgba(99, 102, 241, 0.08) 42%, transparent 68%);
    animation: authGlowPulse 10s var(--auth-ease) infinite;
}
.auth-glow::after {
    content: "";
    position: absolute;
    width: 640px; height: 640px;
    bottom: -220px; left: 50%;
    transform: translateX(-42%);
    background: radial-gradient(circle, rgba(99, 102, 241, 0.16) 0%, transparent 72%);
    animation: authGlowDrift 14s var(--auth-ease) infinite alternate;
}
.auth-glow-mid {
    position: absolute;
    width: 420px; height: 420px;
    top: 38%; left: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(124, 58, 237, 0.08) 0%, transparent 70%);
    animation: authGlowMid 11s var(--auth-ease) infinite alternate;
}
@keyframes authGlowMid {
    from { opacity: 0.45; transform: translate(-50%, -50%) scale(0.95); }
    to { opacity: 0.85; transform: translate(-50%, -50%) scale(1.05); }
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
    max-width: 560px !important;
    width: min(560px, 100%) !important;
    margin: 0 auto !important;
    padding: clamp(2rem, 8vh, 4rem) 1.35rem 2.5rem !important;
}

[data-testid="stVerticalBlock"]:has(.auth-marker) { gap: 0 !important; }

[data-testid="stVerticalBlock"]:has(.auth-glass-marker) {
    padding: 0 !important;
    border-radius: 22px !important;
    background: var(--auth-surface) !important;
    border: 1px solid var(--auth-border) !important;
    backdrop-filter: blur(28px) saturate(1.3) !important;
    -webkit-backdrop-filter: blur(28px) saturate(1.3) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.07),
        0 0 0 1px rgba(139, 92, 246, 0.12),
        0 4px 24px rgba(0, 0, 0, 0.28),
        0 32px 64px rgba(0, 0, 0, 0.38) !important;
    overflow: hidden !important;
    gap: 0 !important;
}

.auth-card-head {
    padding: 1.5rem 1.75rem 1.35rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: linear-gradient(180deg, var(--auth-surface-2) 0%, transparent 100%);
}
.auth-slogan {
    margin: 0 0 1.15rem;
    line-height: 0;
    text-align: center;
}
.auth-slogan img {
    width: 100%;
    max-height: 44px;
    height: auto;
    object-fit: contain;
    display: inline-block;
    opacity: 0.92;
}
.auth-brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
}
.auth-brand-copy {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 52px;
}
.auth-logo-wrap {
    position: relative;
    flex-shrink: 0;
    line-height: 0;
    display: flex;
    align-items: center;
}
.auth-logo-wrap::after {
    content: "";
    position: absolute;
    inset: -8px;
    border-radius: 18px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.4), transparent 72%);
    filter: blur(10px);
    z-index: -1;
}
.auth-logo-svg {
    display: block;
    width: 52px;
    height: 52px;
    filter: drop-shadow(0 8px 20px rgba(124, 58, 237, 0.4));
}
.auth-brand-name {
    margin: 0;
    font-size: 1.625rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1.05;
    color: var(--auth-text);
}
.auth-brand-tag {
    margin: 5px 0 0;
    font-size: 0.625rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #52525b;
}

.auth-card-body {
    padding: 1.5rem 1.75rem 1.35rem;
}

/* Segmented Control — Tabs */
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stHorizontalBlock"]:has(.st-key-auth_tab_login) {
    background: rgba(9, 9, 14, 0.72) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 6px !important;
    margin-bottom: 1.35rem !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register {
    margin: 0 !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton>button,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton>button {
    width: 100% !important;
    min-height: 40px !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: var(--auth-muted) !important;
    font-size: 0.8125rem !important;
    font-weight: 600 !important;
    transition: color 0.22s var(--auth-ease), background 0.22s var(--auth-ease),
                border-color 0.22s var(--auth-ease), box-shadow 0.22s var(--auth-ease),
                transform 0.22s var(--auth-ease) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton>button:hover,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton>button:hover {
    color: var(--auth-soft) !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(255, 255, 255, 0.06) !important;
    transform: translateY(-0.5px) !important;
}

[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton>button p,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton>button p {
    color: inherit !important;
}

.auth-form-title {
    margin: 0 0 0.625rem;
    font-size: 1.1875rem;
    font-weight: 600;
    letter-spacing: -0.025em;
    line-height: 1.25;
    color: var(--auth-text);
}
.auth-form-sub {
    margin: 0 0 1.35rem;
    font-size: 0.875rem;
    color: var(--auth-muted);
    line-height: 1.5;
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
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 11px !important;
    min-height: 48px !important;
    font-size: 0.9375rem !important;
    caret-color: #c4b5fd !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 1px 2px rgba(0, 0, 0, 0.12) !important;
    backdrop-filter: blur(8px) !important;
    transition: border-color 0.22s var(--auth-ease), box-shadow 0.22s var(--auth-ease),
                background 0.22s var(--auth-ease) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input::placeholder {
    color: var(--auth-placeholder) !important;
    opacity: 1 !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:hover {
    background: var(--auth-input-hover) !important;
    border-color: rgba(255, 255, 255, 0.14) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:focus,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:focus-visible {
    background: rgba(139, 92, 246, 0.06) !important;
    border-color: var(--auth-border-focus) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.05),
        0 0 0 3px var(--auth-ring),
        0 0 20px rgba(139, 92, 246, 0.15) !important;
    outline: none !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill:hover,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px rgba(18, 18, 24, 0.95) inset !important;
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
    min-height: 48px !important;
    margin-top: 0.5rem !important;
    border-radius: 11px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 42%, #6366f1 100%) !important;
    color: #fff !important;
    font-size: 0.9375rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.015em !important;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.15) inset,
        0 10px 28px rgba(139, 92, 246, 0.35),
        0 0 0 1px rgba(139, 92, 246, 0.2) !important;
    transition: transform 0.2s var(--auth-ease), box-shadow 0.2s var(--auth-ease),
                filter 0.2s var(--auth-ease) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button:hover,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.18) inset,
        0 14px 36px rgba(139, 92, 246, 0.48),
        0 0 32px rgba(139, 92, 246, 0.22) !important;
    filter: brightness(1.05) !important;
}
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button:active,
[data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"]:active {
    transform: translateY(0) scale(0.995) !important;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.1) inset,
        0 6px 18px rgba(139, 92, 246, 0.3) !important;
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
    padding: 0.65rem 1.75rem 0.85rem;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    text-align: center;
    background: transparent;
}
.auth-ssl {
    margin: 0;
    font-size: 0.625rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #3f3f46;
    opacity: 0.85;
}

@media (max-width: 640px) {
    [data-testid="stMain"] .block-container {
        max-width: 100% !important;
        padding: 1.5rem 1rem 2rem !important;
    }
}
@media (max-width: 480px) {
    [data-testid="stMain"] .block-container {
        padding: 1.25rem 0.85rem 1.75rem !important;
    }
    .auth-card-head { padding: 1.2rem 1.15rem 1.1rem; }
    .auth-card-body { padding: 1.1rem 1.15rem 1.15rem; }
    .auth-brand-name { font-size: 1.375rem; }
    .auth-logo-svg { width: 46px; height: 46px; }
    .auth-brand-copy { min-height: 46px; }
    .auth-slogan img { max-height: 36px; }
}

@media (prefers-reduced-motion: reduce) {
    .auth-glow::before, .auth-glow::after, .auth-glow-mid { animation: none !important; }
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
        '<div class="auth-brand-copy">'
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
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.32), rgba(99, 102, 241, 0.2)) !important;
    border: 1px solid rgba(167, 139, 250, 0.45) !important;
    color: #fafafa !important;
    box-shadow:
        0 0 0 1px rgba(139, 92, 246, 0.15),
        0 4px 16px rgba(139, 92, 246, 0.28),
        0 0 24px rgba(139, 92, 246, 0.12) !important;
    transform: translateY(-0.5px) !important;
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
        username = st.text_input("Benutzername", key="auth_user", placeholder="Dein Benutzername")
        password = st.text_input("Passwort", type="password", key="auth_pass", placeholder="••••••••")
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
        username = st.text_input("Benutzername", key="reg_user", placeholder="Dein Benutzername")
        email = st.text_input("E-Mail", key="reg_email", placeholder="name@beispiel.de")
        password = st.text_input("Passwort", type="password", key="reg_pass", placeholder="Min. 8 Zeichen")
        password2 = st.text_input("Passwort bestätigen", type="password", key="reg_pass2", placeholder="Passwort wiederholen")
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

    st.markdown(
        '<div class="auth-glow" aria-hidden="true"><div class="auth-glow-mid"></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<span class="auth-glass-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)
        st.markdown(_card_head_html(), unsafe_allow_html=True)
        st.markdown('<div class="auth-card-body">', unsafe_allow_html=True)
        _render_mode_tabs(mode)
        _show_notice()
        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-card-foot">'
            '<p class="auth-ssl">SSL-verschlüsselt</p>'
            "</div>",
            unsafe_allow_html=True,
        )
