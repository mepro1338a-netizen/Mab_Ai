import html
import random

import streamlit as st

from database import create_user, record_login_event, verify_login
from security import check_login_rate, record_login_failure, is_valid_email, is_valid_username
from services.session_auth import rotate_session_on_login
from logger import log_auth, log_oauth, user_friendly_error
from oauth_service import (
    auth_url,
    complete_oauth,
    make_state,
    oauth_state_ready,
    provider_configured,
    verify_state,
)
from ui.auth_premium import (
    auth_grid_marker_html,
    auth_styles_bundle,
    forgot_password_html,
    hero_html,
    login_card_marker_html,
    notice_html,
    page_close_html,
    page_open_html,
    panel_close_html,
    panel_shell_html,
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


def _set_gate_notice(level: str, message: str) -> None:
    st.session_state.gate_notice = {"level": level, "message": message}


def _show_gate_notice() -> None:
    notice = st.session_state.pop("gate_notice", None)
    if notice:
        st.markdown(notice_html(notice["level"], notice["message"]), unsafe_allow_html=True)


def finish_oauth_login(user: dict, *, provider: str) -> None:
    ip_address, user_agent = client_meta()
    record_login_event(user["id"], ip_address, user_agent, provider)
    rotate_session_on_login(user)
    log_oauth(f"Login via {provider}: {user.get('username')}")
    st.session_state.pop("gate_notice", None)
    st.rerun()


def do_login(username: str, password: str) -> None:
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        _set_gate_notice("error", "Bitte Benutzername und Passwort eingeben.")
        return
    allowed, msg = check_login_rate(username)
    if not allowed:
        _set_gate_notice("error", msg)
        return
    result = verify_login(username, password)
    if len(result) >= 3:
        ok, login_msg, user = result[0], result[1], result[2]
    else:
        ok, user = result[0], result[1]
        login_msg = ""
    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user["id"], ip_address, user_agent, "password")
        rotate_session_on_login(user)
        log_auth(f"Login: {username}")
        st.rerun()
        return
    record_login_failure(username)
    _set_gate_notice("error", login_msg or "Benutzername oder Passwort falsch.")


def do_register(username: str, email: str, password: str, captcha: int) -> None:
    username = (username or "").strip()
    email = (email or "").strip()
    password = password or ""
    expected = st.session_state.captcha_a + st.session_state.captcha_b
    if captcha != expected:
        _set_gate_notice("error", "Rechenaufgabe falsch — bitte erneut versuchen.")
        refresh_captcha()
        return
    if not is_valid_username(username):
        _set_gate_notice("error", "Benutzername: 3–20 Zeichen, Buchstaben, Zahlen, _ oder -.")
        return
    if not is_valid_email(email):
        _set_gate_notice("error", "Bitte eine gültige E-Mail-Adresse eingeben.")
        return
    if len(password) < 6:
        _set_gate_notice("error", "Passwort muss mindestens 6 Zeichen haben.")
        return
    ok, msg = create_user(username, email, password)
    if ok:
        _set_gate_notice("success", "Konto erstellt — du kannst dich jetzt anmelden.")
        st.session_state.gate_mode = "login"
        refresh_captcha()
        return
    _set_gate_notice("error", msg)


def handle_oauth_callback() -> bool:
    params = st.query_params
    code = params.get("code")
    state = params.get("state")
    if not code or not state:
        return False
    if not oauth_state_ready():
        _set_gate_notice("error", "Anmeldung noch nicht bereit — bitte Seite neu laden.")
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


GOOGLE_ICON_SVG = (
    '<svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>'
    '<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>'
    '<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>'
    '<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>'
    '</svg>'
)


def google_login_link() -> str:
    label = "Mit Google anmelden"
    if provider_configured("google"):
        state = make_state("google")
        url = html.escape(auth_url("google", state), quote=True)
        return f'<a class="mb-login-google" href="{url}" rel="noopener noreferrer">{GOOGLE_ICON_SVG}{html.escape(label)}</a>'
    return f'<span class="mb-login-google disabled">{GOOGLE_ICON_SVG}{html.escape(label)}</span>'


def render_google_block() -> None:
    st.markdown(
        '<div class="mb-oauth-zone">'
        + google_login_link()
        + '<div class="mb-login-divider">ODER</div>'
        + '</div>',
        unsafe_allow_html=True,
    )


def render_login_form() -> None:
    with st.form("gate_login_form", clear_on_submit=False, border=False):
        user = st.text_input(
            "Benutzername",
            placeholder="Benutzername oder E-Mail",
            label_visibility="collapsed",
        )
        pw = st.text_input(
            "Passwort",
            type="password",
            placeholder="Passwort",
            label_visibility="collapsed",
        )
        ex1, ex2 = st.columns([1.2, 0.8], gap="small")
        with ex1:
            st.checkbox("Angemeldet bleiben", key="gate_remember", label_visibility="visible")
        with ex2:
            st.markdown(forgot_password_html(), unsafe_allow_html=True)
        submitted = st.form_submit_button("In MaByte einloggen", type="secondary", width="stretch")
    if submitted:
        do_login(user, pw)


def render_register_form() -> None:
    with st.form("gate_register_form", clear_on_submit=False, border=False):
        user = st.text_input("Benutzername", placeholder="Benutzername wählen", label_visibility="collapsed")
        email = st.text_input("E-Mail", placeholder="deine@email.de", label_visibility="collapsed")
        pw = st.text_input("Passwort", type="password", placeholder="Min. 6 Zeichen", label_visibility="collapsed")
        a, b = st.session_state.captcha_a, st.session_state.captcha_b
        st.markdown(
            f'<p class="mb-captcha-label">Rechenaufgabe: {a} + {b} = ?</p>',
            unsafe_allow_html=True,
        )
        cap_col, ref_col = st.columns([0.82, 0.18], gap="small")
        with cap_col:
            captcha = st.number_input("Ergebnis", min_value=0, max_value=20, step=1, label_visibility="collapsed")
        with ref_col:
            refresh = st.form_submit_button("↻")
        submitted = st.form_submit_button("Konto erstellen", type="secondary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_register(user, email, pw, captcha)


def render_auth_switch() -> None:
    mode = st.session_state.get("gate_mode", "login")
    _, center, _ = st.columns([0.08, 0.84, 0.08])
    with center:
        if mode == "login":
            note_col, btn_col = st.columns([0.52, 0.48], gap="small")
            with note_col:
                st.markdown(
                    '<p class="mb-panel-switch-note">Noch kein Konto?</p>',
                    unsafe_allow_html=True,
                )
            with btn_col:
                if st.button("Jetzt registrieren →", key="switch_register", type="tertiary"):
                    st.session_state.gate_mode = "register"
                    st.rerun()
        else:
            note_col, btn_col = st.columns([0.52, 0.48], gap="small")
            with note_col:
                st.markdown(
                    '<p class="mb-panel-switch-note">Bereits ein Konto?</p>',
                    unsafe_allow_html=True,
                )
            with btn_col:
                if st.button("Anmelden →", key="switch_login", type="tertiary"):
                    st.session_state.gate_mode = "login"
                    st.rerun()


def render_gate_panel() -> None:
    mode = st.session_state.get("gate_mode", "login")
    st.markdown(login_card_marker_html(), unsafe_allow_html=True)
    st.markdown(panel_shell_html(register=(mode == "register")), unsafe_allow_html=True)
    _show_gate_notice()
    if mode == "register":
        render_register_form()
    else:
        render_google_block()
        render_login_form()
    render_auth_switch()
    st.markdown(panel_close_html(), unsafe_allow_html=True)


def render_auth() -> None:
    ensure_captcha()
    if "gate_mode" not in st.session_state:
        st.session_state.gate_mode = "login"

    inject_css(auth_styles_bundle())
    handle_oauth_callback()

    mode_class = "mb-mode-register" if st.session_state.gate_mode == "register" else "mb-mode-login"
    st.markdown(page_open_html(mode_class), unsafe_allow_html=True)

    hero_col, panel_col = st.columns([11, 9], gap="small")
    with hero_col:
        st.markdown(auth_grid_marker_html(), unsafe_allow_html=True)
        st.markdown(hero_html(), unsafe_allow_html=True)
    with panel_col:
        with st.container():
            render_gate_panel()

    st.markdown(page_close_html(), unsafe_allow_html=True)
    inject_css(auth_styles_bundle())
