"""MaByte Auth — Login default, Registrierung on demand, optional Google OAuth."""
from __future__ import annotations

import random

import streamlit as st

from database import record_login_event, register_account, verify_login_identifier
from oauth_service import auth_url, complete_oauth, friendly_oauth_error, make_state, provider_configured, verify_state
from security import check_login_rate, is_valid_email, is_valid_username, record_login_failure
from services.session_auth import rotate_session_on_login
from logger import log_auth
from ui.auth_premium import (
    auth_grid_marker_html,
    auth_styles_bundle,
    forgot_password_html,
    hero_html,
    login_card_marker_html,
    notice_html,
    oauth_divider_html,
    page_close_html,
    page_open_html,
    panel_close_html,
    panel_shell_html,
)
from ui.styles import inject_css

USE_CASE_OPTIONS = (
    "Creator & Content",
    "Football & Sport",
    "Business & Teams",
    "Developer & Code",
    "Sonstiges",
)

COUNTRY_OPTIONS = (
    "Deutschland",
    "Österreich",
    "Schweiz",
    "Andere",
)


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


def _set_gate_notice(level: str, message: str) -> None:
    st.session_state.gate_notice = {"level": level, "message": message}


def _show_gate_notice() -> None:
    notice = st.session_state.pop("gate_notice", None)
    if notice:
        st.markdown(notice_html(notice["level"], notice["message"]), unsafe_allow_html=True)


def _check_captcha(captcha: int) -> bool:
    expected = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)
    if int(captcha) != expected:
        _set_gate_notice("error", "Rechenaufgabe falsch — bitte erneut versuchen.")
        refresh_captcha()
        return False
    return True


def do_login(identifier: str, password: str, *, captcha: int) -> None:
    if not _check_captcha(captcha):
        return

    identifier = (identifier or "").strip()
    password = password or ""
    if not identifier or not password:
        _set_gate_notice("error", "Bitte Benutzername/E-Mail und Passwort eingeben.")
        return

    allowed, msg = check_login_rate(identifier)
    if not allowed:
        _set_gate_notice("error", msg)
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
    _set_gate_notice("error", login_msg or "Benutzername/E-Mail oder Passwort falsch.")
    refresh_captcha()


def do_register(
    *,
    full_name: str,
    username: str,
    email: str,
    password: str,
    password2: str,
    company: str,
    phone: str,
    country: str,
    use_case: str,
    terms: bool,
    marketing: bool,
    captcha: int,
) -> None:
    if not _check_captcha(captcha):
        return

    username = (username or "").strip()
    email = (email or "").strip()
    password = password or ""
    password2 = password2 or ""

    if password != password2:
        _set_gate_notice("error", "Passwörter stimmen nicht überein.")
        return

    if not is_valid_username(username):
        _set_gate_notice(
            "error",
            "Benutzername: 3–40 Zeichen, nur Buchstaben, Zahlen oder Unterstrich.",
        )
        return

    if not is_valid_email(email):
        _set_gate_notice("error", "Bitte eine gültige E-Mail-Adresse eingeben.")
        return

    if not terms:
        _set_gate_notice("error", "Bitte AGB und Datenschutz bestätigen.")
        return

    ip_address, user_agent = client_meta()
    ok, msg, user = register_account(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        company=company,
        phone=phone,
        country=country,
        use_case=use_case,
        marketing_opt_in=marketing,
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

    _set_gate_notice("error", msg)
    refresh_captcha()


def handle_google_oauth_callback() -> None:
    """Complete Google login OAuth redirect (called from ui.py before auth gate)."""
    params = st.query_params
    code = str(params.get("code") or "").strip()
    state = str(params.get("state") or "").strip()
    error = str(params.get("error") or "").strip()
    error_desc = str(params.get("error_description") or "").strip()

    st.session_state.gate_mode = "login"
    inject_css(auth_styles_bundle())
    st.markdown(page_open_html("mb-mode-login"), unsafe_allow_html=True)

    if error:
        st.markdown(
            notice_html("error", friendly_oauth_error(error, error_desc)),
            unsafe_allow_html=True,
        )
        st.query_params.clear()
        if st.button("Zurück zum Login", type="primary", key="oauth_err_back"):
            st.rerun()
        st.markdown(page_close_html(), unsafe_allow_html=True)
        return

    provider = verify_state(state)
    if provider != "google" or not code:
        st.markdown(notice_html("error", "OAuth-Session ungültig oder abgelaufen."), unsafe_allow_html=True)
        st.query_params.clear()
        if st.button("Zurück zum Login", type="primary", key="oauth_invalid_back"):
            st.rerun()
        st.markdown(page_close_html(), unsafe_allow_html=True)
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

    st.markdown(notice_html("error", msg), unsafe_allow_html=True)
    if st.button("Zurück zum Login", type="primary", key="oauth_fail_back"):
        st.rerun()
    st.markdown(page_close_html(), unsafe_allow_html=True)


def _render_captcha_fields(*, refresh_key: str) -> tuple[int, bool]:
    a, b = st.session_state.captcha_a, st.session_state.captcha_b
    st.markdown(
        f'<p class="auth-captcha-label">Sicherheitsfrage: {a} + {b} = ?</p>',
        unsafe_allow_html=True,
    )
    cap_col, ref_col = st.columns([5, 1], gap="small")
    with cap_col:
        captcha = st.number_input(
            "Ergebnis",
            min_value=0,
            max_value=30,
            step=1,
            value=0,
            label_visibility="collapsed",
        )
    with ref_col:
        refresh = st.form_submit_button("↻", help="Neue Aufgabe", key=refresh_key)
    return int(captcha), refresh


def render_google_login() -> None:
    st.markdown(oauth_divider_html(), unsafe_allow_html=True)
    if provider_configured("google"):
        url = auth_url("google", make_state("google"))
        if url:
            st.link_button(
                "Mit Google anmelden",
                url,
                width="stretch",
                type="secondary",
            )
            return
    st.markdown(
        '<a class="mb-login-google disabled" href="#" onclick="return false;">'
        "Mit Google anmelden (nicht konfiguriert)</a>",
        unsafe_allow_html=True,
    )


def render_login_form() -> None:
    with st.form("gate_login_form", clear_on_submit=False, border=False):
        st.markdown(
            '<p class="auth-field-label">Benutzername oder E-Mail</p>',
            unsafe_allow_html=True,
        )
        identifier = st.text_input(
            "Benutzername oder E-Mail",
            placeholder="name@firma.de oder dein_name",
            label_visibility="collapsed",
        )
        st.markdown('<p class="auth-field-label">Passwort</p>', unsafe_allow_html=True)
        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="Passwort",
            label_visibility="collapsed",
        )
        captcha, refresh = _render_captcha_fields(refresh_key="gate_login_cap_refresh")
        ex1, ex2 = st.columns([1.2, 0.8], gap="small")
        with ex1:
            st.checkbox("Angemeldet bleiben", key="gate_remember", label_visibility="visible")
        with ex2:
            st.markdown(forgot_password_html(), unsafe_allow_html=True)
        submitted = st.form_submit_button("Anmelden", type="primary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_login(identifier, password, captcha=captcha)

    render_google_login()


def render_register_form() -> None:
    with st.form("gate_register_form", clear_on_submit=False, border=False):
        st.markdown('<p class="auth-field-label">Vollständiger Name *</p>', unsafe_allow_html=True)
        full_name = st.text_input(
            "Name",
            placeholder="Max Mustermann",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown('<p class="mb-field-label">E-Mail *</p>', unsafe_allow_html=True)
            email = st.text_input("E-Mail", placeholder="name@firma.de", label_visibility="collapsed")
        with c2:
            st.markdown('<p class="auth-field-label">Benutzername *</p>', unsafe_allow_html=True)
            username = st.text_input(
                "Benutzername",
                placeholder="dein_name",
                label_visibility="collapsed",
            )
        c3, c4 = st.columns(2, gap="small")
        with c3:
            st.markdown('<p class="auth-field-label">Unternehmen</p>', unsafe_allow_html=True)
            company = st.text_input(
                "Unternehmen",
                placeholder="Firma GmbH",
                label_visibility="collapsed",
            )
        with c4:
            st.markdown('<p class="auth-field-label">Telefon</p>', unsafe_allow_html=True)
            phone = st.text_input(
                "Telefon",
                placeholder="+49 …",
                label_visibility="collapsed",
            )
        c5, c6 = st.columns(2, gap="small")
        with c5:
            st.markdown('<p class="auth-field-label">Land *</p>', unsafe_allow_html=True)
            country = st.selectbox(
                "Land",
                COUNTRY_OPTIONS,
                label_visibility="collapsed",
            )
        with c6:
            st.markdown('<p class="auth-field-label">Nutzungszweck *</p>', unsafe_allow_html=True)
            use_case = st.selectbox(
                "Nutzungszweck",
                USE_CASE_OPTIONS,
                label_visibility="collapsed",
            )
        p1, p2 = st.columns(2, gap="small")
        with p1:
            st.markdown('<p class="mb-field-label">Passwort * (min. 8)</p>', unsafe_allow_html=True)
            password = st.text_input(
                "Passwort",
                type="password",
                placeholder="Min. 8 Zeichen",
                label_visibility="collapsed",
            )
        with p2:
            st.markdown('<p class="auth-field-label">Passwort bestätigen *</p>', unsafe_allow_html=True)
            password2 = st.text_input(
                "Passwort bestätigen",
                type="password",
                placeholder="Wiederholen",
                label_visibility="collapsed",
            )
        terms = st.checkbox(
            "Ich akzeptiere die AGB und Datenschutzerklärung. *",
            value=False,
        )
        marketing = st.checkbox(
            "Produktnews per E-Mail (optional).",
            value=False,
        )
        captcha, refresh = _render_captcha_fields(refresh_key="gate_reg_cap_refresh")
        submitted = st.form_submit_button("Konto erstellen", type="primary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_register(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            password2=password2,
            company=company,
            phone=phone,
            country=country,
            use_case=use_case,
            terms=terms,
            marketing=marketing,
            captcha=captcha,
        )


def render_auth_switch() -> None:
    mode = st.session_state.get("gate_mode", "login")
    if mode == "register":
        st.markdown(
            '<p class="auth-register-line">Bereits registriert?</p>',
            unsafe_allow_html=True,
        )
        if st.button("Zum Login", key="switch_login", type="tertiary"):
            st.session_state.gate_mode = "login"
            refresh_captcha()
            st.rerun()
    else:
        st.markdown(
            '<p class="auth-register-line">Noch kein Konto?</p>',
            unsafe_allow_html=True,
        )
        if st.button("Jetzt registrieren", key="switch_register", type="tertiary"):
            st.session_state.gate_mode = "register"
            refresh_captcha()
            st.rerun()


def render_gate_panel() -> None:
    mode = st.session_state.get("gate_mode", "login")
    st.markdown(login_card_marker_html(), unsafe_allow_html=True)
    st.markdown(panel_shell_html(register=(mode == "register")), unsafe_allow_html=True)
    _show_gate_notice()
    if mode == "register":
        render_register_form()
    else:
        render_login_form()
    render_auth_switch()
    st.markdown(panel_close_html(), unsafe_allow_html=True)


def render_auth() -> None:
    ensure_captcha()
    if "gate_mode" not in st.session_state:
        st.session_state.gate_mode = "login"
    if st.session_state.gate_mode not in ("login", "register"):
        st.session_state.gate_mode = "login"

    inject_css(auth_styles_bundle())

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
