"""MaByte Auth — stable login/register (default: login)."""
from __future__ import annotations

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
from ui.auth_premium import (
    auth_card_header_html,
    auth_card_marker_html,
    auth_divider_html,
    auth_forgot_link_html,
    auth_label_html,
    auth_notice_html,
    auth_page_close,
    auth_page_open,
    auth_styles_bundle,
    auth_switch_note_html,
    brand_panel_html,
)
from ui.styles import inject_css

_DEFAULT_USE_CASE = "Sonstiges"
_DEFAULT_COUNTRY = "Deutschland"


def _get_auth_mode() -> str:
    mode = str(st.session_state.get("auth_mode") or st.session_state.get("gate_mode") or "login")
    return mode if mode in ("login", "register") else "login"


def _set_auth_mode(mode: str) -> None:
    st.session_state.auth_mode = mode
    st.session_state.gate_mode = mode


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
    st.session_state.auth_notice = {"level": level, "message": message}


def _show_notice() -> None:
    notice = st.session_state.pop("auth_notice", None) or st.session_state.pop("gate_notice", None)
    if notice:
        st.markdown(auth_notice_html(notice["level"], notice["message"]), unsafe_allow_html=True)


def _check_captcha(captcha: int) -> bool:
    expected = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)
    if int(captcha) != expected:
        _set_notice("error", "Rechenaufgabe falsch — bitte erneut versuchen.")
        refresh_captcha()
        return False
    return True


def do_login(identifier: str, password: str, *, captcha: int) -> None:
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
    full_name: str,
    username: str,
    email: str,
    password: str,
    password2: str,
    company: str,
    terms: bool,
    captcha: int,
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
        full_name=full_name,
        company=(company or "").strip(),
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
        st.session_state.pop("auth_notice", None)
        st.session_state.pop("gate_notice", None)
        st.rerun()
        return

    _set_notice("error", msg)
    refresh_captcha()


def handle_google_oauth_callback() -> None:
    """Complete Google OAuth redirect (called from ui.py before auth gate)."""
    params = st.query_params
    code = str(params.get("code") or "").strip()
    state = str(params.get("state") or "").strip()
    error = str(params.get("error") or "").strip()
    error_desc = str(params.get("error_description") or "").strip()

    _set_auth_mode("login")
    inject_css(auth_styles_bundle())
    st.markdown(auth_page_open("login"), unsafe_allow_html=True)

    if error:
        st.markdown(auth_notice_html("error", friendly_oauth_error(error, error_desc)), unsafe_allow_html=True)
        st.query_params.clear()
        if st.button("Zurück zum Login", type="primary", key="oauth_err_back"):
            st.rerun()
        st.markdown(auth_page_close(), unsafe_allow_html=True)
        return

    provider = verify_state(state)
    if provider != "google" or not code:
        st.markdown(auth_notice_html("error", "OAuth-Session ungültig oder abgelaufen."), unsafe_allow_html=True)
        st.query_params.clear()
        if st.button("Zurück zum Login", type="primary", key="oauth_invalid_back"):
            st.rerun()
        st.markdown(auth_page_close(), unsafe_allow_html=True)
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

    st.markdown(auth_notice_html("error", msg), unsafe_allow_html=True)
    if st.button("Zurück zum Login", type="primary", key="oauth_fail_back"):
        st.rerun()
    st.markdown(auth_page_close(), unsafe_allow_html=True)


def _render_captcha(*, refresh_key: str) -> tuple[int, bool]:
    a, b = st.session_state.captcha_a, st.session_state.captcha_b
    st.markdown(auth_label_html(f"Sicherheitsfrage: {a} + {b} = ?"), unsafe_allow_html=True)
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


def _render_google_button() -> None:
    st.markdown(auth_divider_html(), unsafe_allow_html=True)
    if provider_configured("google"):
        url = auth_url("google", make_state("google"))
        if url:
            st.link_button("Mit Google anmelden", url, width="stretch", type="secondary")
            return
    st.caption("Google-Anmeldung ist derzeit nicht konfiguriert.")


def _render_login_form() -> None:
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        st.markdown(auth_label_html("Benutzername oder E-Mail"), unsafe_allow_html=True)
        identifier = st.text_input(
            "Benutzername oder E-Mail",
            placeholder="name@firma.de oder dein_name",
            label_visibility="collapsed",
        )
        st.markdown(auth_label_html("Passwort"), unsafe_allow_html=True)
        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="Passwort",
            label_visibility="collapsed",
        )
        captcha, refresh = _render_captcha(refresh_key="auth_login_cap_refresh")
        row1, row2 = st.columns([1.2, 0.8], gap="small")
        with row1:
            st.checkbox("Angemeldet bleiben", key="auth_remember")
        with row2:
            st.markdown(auth_forgot_link_html(), unsafe_allow_html=True)
        submitted = st.form_submit_button("Anmelden", type="primary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_login(identifier, password, captcha=captcha)

    _render_google_button()


def _render_register_form() -> None:
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        st.markdown(auth_label_html("Vollständiger Name *"), unsafe_allow_html=True)
        full_name = st.text_input("Name", placeholder="Max Mustermann", label_visibility="collapsed")
        st.markdown(auth_label_html("E-Mail *"), unsafe_allow_html=True)
        email = st.text_input("E-Mail", placeholder="name@firma.de", label_visibility="collapsed")
        st.markdown(auth_label_html("Benutzername *"), unsafe_allow_html=True)
        username = st.text_input("Benutzername", placeholder="dein_name", label_visibility="collapsed")
        st.markdown(auth_label_html("Unternehmen (optional)"), unsafe_allow_html=True)
        company = st.text_input("Unternehmen", placeholder="Firma GmbH", label_visibility="collapsed")
        st.markdown(auth_label_html("Passwort * (min. 8)"), unsafe_allow_html=True)
        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="Min. 8 Zeichen",
            label_visibility="collapsed",
        )
        st.markdown(auth_label_html("Passwort bestätigen *"), unsafe_allow_html=True)
        password2 = st.text_input(
            "Passwort bestätigen",
            type="password",
            placeholder="Wiederholen",
            label_visibility="collapsed",
        )
        captcha, refresh = _render_captcha(refresh_key="auth_reg_cap_refresh")
        terms = st.checkbox("Ich akzeptiere die AGB und Datenschutzerklärung. *", value=False)
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
            terms=terms,
            captcha=captcha,
        )


def _render_auth_card() -> None:
    mode = _get_auth_mode()
    st.markdown(auth_card_marker_html(), unsafe_allow_html=True)
    st.markdown(auth_card_header_html(register=(mode == "register")), unsafe_allow_html=True)
    _show_notice()
    if mode == "register":
        _render_register_form()
    else:
        _render_login_form()
    st.markdown(auth_switch_note_html(register=(mode == "register")), unsafe_allow_html=True)
    if mode == "register":
        if st.button("Zurück zum Login", key="auth_switch_login", type="tertiary"):
            _set_auth_mode("login")
            refresh_captcha()
            st.rerun()
    else:
        if st.button("Jetzt registrieren", key="auth_switch_register", type="tertiary"):
            _set_auth_mode("register")
            refresh_captcha()
            st.rerun()


def render_auth() -> None:
    ensure_captcha()
    if "auth_mode" not in st.session_state:
        _set_auth_mode("login")
    else:
        st.session_state.gate_mode = _get_auth_mode()

    mode = _get_auth_mode()
    inject_css(auth_styles_bundle())
    st.markdown(auth_page_open(mode), unsafe_allow_html=True)

    if mode == "register":
        _, center, _ = st.columns([0.12, 0.76, 0.12])
        with center:
            _render_auth_card()
    else:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown(brand_panel_html(), unsafe_allow_html=True)
        with right:
            _render_auth_card()

    st.markdown(auth_page_close(), unsafe_allow_html=True)
