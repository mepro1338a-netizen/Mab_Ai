import html
import random

import streamlit as st

from config import APP_NAME
from database import create_user, record_login_event, verify_login
from security import check_login_rate, record_login_failure, is_valid_email, is_valid_username
from services.session_auth import rotate_session_on_login
from logger import log_auth, log_oauth, user_friendly_error
from oauth_service import (
    auth_url,
    complete_oauth,
    friendly_oauth_error,
    make_state,
    oauth_state_ready,
    provider_configured,
    verify_state,
)
from ui.auth_premium import (
    access_card_close_html,
    access_card_open_html,
    auth_styles_bundle,
    header_html,
    hero_html,
    notice_html,
    page_close_html,
    panel_foot_html,
    panel_head_html,
)
from ui.styles import inject_css


def refresh_captcha() -> None:
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


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


def show_notice(level: str, message: str) -> None:
    st.markdown(notice_html(level, message), unsafe_allow_html=True)


def do_login(username: str, password: str) -> None:
    username = (username or "").strip().lower()
    allowed, msg = check_login_rate(username)
    if not allowed:
        show_notice("error", msg)
        return

    ok, msg, user = verify_login(username, password)
    ip_address, user_agent = client_meta()
    try:
        record_login_event(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=ok,
        )
    except Exception:
        pass

    if ok and user:
        rotate_session_on_login(user)
        log_auth("login_success", username=username, success=True)
        from pages.social_oauth import resume_pending_social_connect

        if resume_pending_social_connect():
            return
        st.session_state.page = "home"
        st.rerun()

    record_login_failure(username)
    log_auth("login_failed", username=username, success=False)
    show_notice("error", user_friendly_error("auth"))


def do_register(username: str, email: str, password: str, captcha: int) -> None:
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()
    result = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)

    if not is_valid_username(username):
        show_notice("error", "Bitte einen gültigen Benutzernamen wählen.")
        return
    if not is_valid_email(email):
        show_notice("error", "Bitte eine gültige E-Mail-Adresse eingeben.")
        return
    if len(password or "") < 6:
        show_notice("error", "Das Passwort muss mindestens 6 Zeichen haben.")
        return
    if int(captcha or 0) != result:
        show_notice("error", "Die Rechenaufgabe war falsch — bitte erneut versuchen.")
        refresh_captcha()
        return

    ok, msg = create_user(username=username, email=email, password=password)
    if ok:
        st.session_state.gate_mode = "login"
        show_notice("success", "Konto erstellt! Wechsle zu «Anmelden» und starte durch.")
        refresh_captcha()
    else:
        show_notice("error", msg)


def _set_gate_notice(level: str, message: str) -> None:
    st.session_state.gate_notice = (level, message)


def _show_gate_notice() -> None:
    notice = st.session_state.pop("gate_notice", None)
    if notice:
        show_notice(notice[0], notice[1])


def finish_oauth_login(user: dict, *, provider: str) -> None:
    username = str(user.get("username") or "")
    ip_address, user_agent = client_meta()
    try:
        record_login_event(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )
    except Exception:
        pass
    rotate_session_on_login(user)
    log_oauth("oauth_success", provider=provider, success=True, user=username)
    from pages.social_oauth import resume_pending_social_connect

    if resume_pending_social_connect():
        return
    st.session_state.page = "home"
    st.rerun()


def handle_oauth_callback() -> bool:
    params = st.query_params
    oauth_error = params.get("error")
    if oauth_error:
        desc = params.get("error_description") or ""
        if isinstance(desc, list):
            desc = desc[0] if desc else ""
        if isinstance(oauth_error, list):
            oauth_error = oauth_error[0] if oauth_error else ""
        _set_gate_notice("error", friendly_oauth_error(str(oauth_error), str(desc)))
        st.query_params.clear()
        return False

    code = params.get("code")
    state = params.get("state")
    if isinstance(code, list):
        code = code[0] if code else None
    if isinstance(state, list):
        state = state[0] if state else None

    if not code and not state:
        return False
    if not code or not state:
        _set_gate_notice("error", "Anmeldung fehlgeschlagen. Bitte erneut versuchen.")
        st.query_params.clear()
        return False

    provider = verify_state(str(state))
    if not provider:
        _set_gate_notice("error", "Sitzung abgelaufen — bitte «Mit Google anmelden» erneut klicken.")
        st.query_params.clear()
        return False

    ok, msg, user = complete_oauth(provider, str(code))
    st.query_params.clear()
    if ok and user:
        finish_oauth_login(user, provider=provider)
        return True

    _set_gate_notice("error", user_friendly_error("oauth", msg))
    return False


GOOGLE_ICON_SVG = """
<svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
</svg>
"""


def google_login_link() -> str:
    label = "Mit Google anmelden"
    if provider_configured("google"):
        state = make_state("google")
        url = html.escape(auth_url("google", state), quote=True)
        return (
            f'<a class="mb-login-google" href="{url}" rel="noopener noreferrer">'
            f"{GOOGLE_ICON_SVG}{html.escape(label)}</a>"
        )
    return (
        f'<span class="mb-login-google disabled">'
        f"{GOOGLE_ICON_SVG}{html.escape(label)}</span>"
    )


def render_mode_switch() -> str:
    mode = st.session_state.get("gate_mode", "login")
    css_class = "mb-mode-register" if mode == "register" else "mb-mode-login"
    st.markdown(f'<div class="mb-mode-switch {css_class}">', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("Anmelden", key="gate_login", width="stretch", type="tertiary"):
            st.session_state.gate_mode = "login"
            st.rerun()
    with c2:
        if st.button("Registrieren", key="gate_register", width="stretch", type="tertiary"):
            st.session_state.gate_mode = "register"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    return mode


def render_google_block() -> None:
    st.markdown(google_login_link(), unsafe_allow_html=True)
    st.markdown('<p class="mb-login-hint">Schnell starten — kein Passwort bei uns gespeichert</p>', unsafe_allow_html=True)
    st.markdown('<div class="mb-login-divider">oder mit Zugangsdaten</div>', unsafe_allow_html=True)


def render_login_form() -> None:
    st.markdown('<div class="mb-login-form">', unsafe_allow_html=True)
    with st.form("gate_login_form", clear_on_submit=False, border=False):
        st.markdown('<div class="mb-field-group"><label class="mb-field-label">Benutzername</label>', unsafe_allow_html=True)
        user = st.text_input("Benutzername", placeholder="dein-benutzername", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="mb-field-group"><label class="mb-field-label">Passwort</label>', unsafe_allow_html=True)
        pw = st.text_input("Passwort", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.form_submit_button("Zukunft starten →", type="primary", width="stretch"):
            do_login(user, pw)
    st.markdown("</div>", unsafe_allow_html=True)


def render_register_form() -> None:
    with st.form("gate_register_form", clear_on_submit=False, border=False):
        user = st.text_input("Benutzername", placeholder="Benutzername wählen", label_visibility="collapsed")
        email = st.text_input("E-Mail", placeholder="deine@email.de", label_visibility="collapsed")
        pw = st.text_input("Passwort", type="password", placeholder="Passwort (min. 6 Zeichen)", label_visibility="collapsed")
        a, b = st.session_state.captcha_a, st.session_state.captcha_b
        st.markdown(
            f'<p style="color:#71717a;font-size:11px;margin:0 0 6px 0">Rechenaufgabe: {a} + {b} = ?</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="mb-login-captcha">', unsafe_allow_html=True)
        cap_col, ref_col = st.columns([0.82, 0.18], gap="small")
        with cap_col:
            captcha = st.number_input(
                "Ergebnis",
                min_value=0,
                max_value=20,
                step=1,
                label_visibility="collapsed",
            )
        with ref_col:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            refresh = st.form_submit_button("↻")
        st.markdown("</div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Zukunft erschaffen →", type="primary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_register(user, email, pw, captcha)


def render_gate_panel() -> None:
    mode = st.session_state.get("gate_mode", "login")
    with st.container(border=True):
        st.markdown(panel_head_html(register=(mode == "register")), unsafe_allow_html=True)
        _show_gate_notice()
        mode = render_mode_switch()

        if mode == "register":
            render_register_form()
        else:
            render_google_block()
            render_login_form()

        st.markdown(panel_foot_html(), unsafe_allow_html=True)


def render_auth() -> None:
    ensure_captcha()
    if "gate_mode" not in st.session_state:
        st.session_state.gate_mode = "login"

    inject_css(auth_styles_bundle())
    handle_oauth_callback()

    st.markdown(header_html(), unsafe_allow_html=True)

    hero_col, panel_col = st.columns([1.12, 0.88], gap="large")

    with hero_col:
        st.markdown(hero_html(), unsafe_allow_html=True)

    with panel_col:
        render_gate_panel()

    st.markdown(page_close_html(), unsafe_allow_html=True)
