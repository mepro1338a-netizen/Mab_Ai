"""MaByte Auth — E-Mail-Registrierung mit vollständiger Lead-Erfassung (kein Google-Login)."""
from __future__ import annotations

import html
import random

import streamlit as st

from database import record_login_event, register_account, verify_login
from security import check_login_rate, record_login_failure, is_valid_email, is_valid_username
from services.session_auth import rotate_session_on_login
from logger import log_auth
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
        record_login_event(user.get("username") or username, ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth(f"Login: {username}")
        st.rerun()
        return
    record_login_failure(username)
    _set_gate_notice("error", login_msg or "Benutzername oder Passwort falsch.")


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
    expected = st.session_state.captcha_a + st.session_state.captcha_b
    if captcha != expected:
        _set_gate_notice("error", "Rechenaufgabe falsch — bitte erneut versuchen.")
        refresh_captcha()
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


def render_login_form() -> None:
    with st.form("gate_login_form", clear_on_submit=False, border=False):
        st.markdown('<p class="mb-field-label">Benutzername</p>', unsafe_allow_html=True)
        user = st.text_input(
            "Benutzername",
            placeholder="Dein Benutzername",
            label_visibility="collapsed",
        )
        st.markdown('<p class="mb-field-label">Passwort</p>', unsafe_allow_html=True)
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
        submitted = st.form_submit_button("Anmelden", type="primary", width="stretch")
    if submitted:
        do_login(user, pw)


def render_register_form() -> None:
    with st.form("gate_register_form", clear_on_submit=False, border=False):
        st.markdown('<p class="mb-field-label">Vollständiger Name *</p>', unsafe_allow_html=True)
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
            st.markdown('<p class="mb-field-label">Benutzername *</p>', unsafe_allow_html=True)
            username = st.text_input(
                "Benutzername",
                placeholder="dein_name",
                label_visibility="collapsed",
            )
        c3, c4 = st.columns(2, gap="small")
        with c3:
            st.markdown('<p class="mb-field-label">Unternehmen</p>', unsafe_allow_html=True)
            company = st.text_input(
                "Unternehmen",
                placeholder="Firma GmbH",
                label_visibility="collapsed",
            )
        with c4:
            st.markdown('<p class="mb-field-label">Telefon</p>', unsafe_allow_html=True)
            phone = st.text_input(
                "Telefon",
                placeholder="+49 …",
                label_visibility="collapsed",
            )
        c5, c6 = st.columns(2, gap="small")
        with c5:
            st.markdown('<p class="mb-field-label">Land *</p>', unsafe_allow_html=True)
            country = st.selectbox(
                "Land",
                COUNTRY_OPTIONS,
                label_visibility="collapsed",
            )
        with c6:
            st.markdown('<p class="mb-field-label">Nutzungszweck *</p>', unsafe_allow_html=True)
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
            st.markdown('<p class="mb-field-label">Passwort bestätigen *</p>', unsafe_allow_html=True)
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
        a, b = st.session_state.captcha_a, st.session_state.captcha_b
        st.markdown(
            f'<p class="mb-captcha-label">Sicherheitsfrage: {a} + {b} = ?</p>',
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
            st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
            refresh = st.form_submit_button("↻", help="Neue Aufgabe")
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
    mode = st.session_state.get("gate_mode", "register")
    _, center, _ = st.columns([0.08, 0.84, 0.08])
    with center:
        if mode == "register":
            note_col, btn_col = st.columns([0.52, 0.48], gap="small")
            with note_col:
                st.markdown(
                    '<p class="mb-panel-switch-note">Bereits registriert?</p>',
                    unsafe_allow_html=True,
                )
            with btn_col:
                if st.button("Zum Login →", key="switch_login", type="tertiary"):
                    st.session_state.gate_mode = "login"
                    st.rerun()
        else:
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


def render_gate_panel() -> None:
    mode = st.session_state.get("gate_mode", "register")
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
        st.session_state.gate_mode = "register"

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
