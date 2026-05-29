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
    auth_styles_bundle,
    login_card_head_html,
    login_footer_html,
    presentation_html,
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


def do_login(username: str, password: str) -> None:
    username = (username or "").strip().lower()

    allowed, msg = check_login_rate(username)

    if not allowed:
        st.error(msg)
        try:
            record_login_event(
                username=username,
                ip_address="rate_limited",
                user_agent="blocked",
                success=False,
            )
        except Exception:
            pass
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
    st.error(user_friendly_error("auth"))


def do_register(username: str, email: str, password: str, captcha: int) -> None:
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()

    result = int(st.session_state.captcha_a) + int(st.session_state.captcha_b)

    if not is_valid_username(username):
        st.error("Bitte einen gültigen Benutzernamen wählen (3–20 Zeichen, Buchstaben/Zahlen).")
        return

    if not is_valid_email(email):
        st.error("Bitte eine gültige E-Mail-Adresse eingeben.")
        return

    if len(password or "") < 6:
        st.error("Das Passwort muss mindestens 6 Zeichen lang sein.")
        return

    if int(captcha or 0) != result:
        st.error("Die Rechenaufgabe war leider falsch — bitte erneut versuchen.")
        refresh_captcha()
        return

    ok, msg = create_user(username=username, email=email, password=password)

    if ok:
        st.success("Dein Konto wurde erstellt. Wechsle zum Tab «Anmelden» und logge dich ein.")
        refresh_captcha()
    else:
        st.error(msg)


def _set_oauth_notice(level: str, message: str) -> None:
    st.session_state.oauth_notice = (level, message)


def _show_oauth_notice() -> None:
    notice = st.session_state.pop("oauth_notice", None)
    if not notice:
        return
    level, text = notice
    if level == "success":
        st.success(text)
    elif level == "info":
        st.info(text)
    else:
        st.error(text)


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
    _set_oauth_notice("success", "Willkommen zurück — du bist angemeldet.")
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
        _set_oauth_notice("error", friendly_oauth_error(str(oauth_error), str(desc)))
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
        _set_oauth_notice("error", "Die Anmeldung konnte nicht abgeschlossen werden. Bitte versuche es erneut.")
        st.query_params.clear()
        return False

    provider = verify_state(str(state))
    if not provider:
        log_oauth("oauth_invalid_state", success=False)
        _set_oauth_notice(
            "error",
            "Anmelde-Sitzung abgelaufen oder ungültig. Bitte «Mit Google anmelden» erneut klicken.",
        )
        st.query_params.clear()
        return False

    ok, msg, user = complete_oauth(provider, str(code))
    st.query_params.clear()

    if ok and user:
        finish_oauth_login(user, provider=provider)
        return True

    ip_address, user_agent = client_meta()
    try:
        record_login_event(
            username=str(user.get("username") if user else "oauth"),
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
        )
    except Exception:
        pass

    log_oauth("oauth_failed", provider=provider or "?", success=False)
    _set_oauth_notice("error", user_friendly_error("oauth", msg))
    return False


def auth_css() -> None:
    inject_css(auth_styles_bundle())


def auth_css_final() -> None:
    """Injected last so it overrides Streamlit widget inline styles."""
    from ui.auth_premium import login_override_css

    css = login_override_css()
    inject_css(css)
    st.html(f"<style id='mb-login-final'>{css}</style>", height=0)


GOOGLE_ICON_SVG = """
<svg class="g-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
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
        f'<span class="mb-login-google disabled" title="Derzeit nicht verfügbar">'
        f"{GOOGLE_ICON_SVG}{html.escape(label)}</span>"
    )


def render_google_login() -> None:
    st.markdown(google_login_link(), unsafe_allow_html=True)
    st.markdown(
        '<p class="mb-login-trust">Sicher über Google — wir speichern kein Google-Passwort.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="mb-login-divider">oder mit Zugangsdaten</div>', unsafe_allow_html=True)

    if not provider_configured("google"):
        st.caption("Google-Anmeldung derzeit nicht verfügbar — nutze Benutzername und Passwort.")


def render_login_form() -> None:
    with st.form("login_form", clear_on_submit=False, border=False):
        user = st.text_input("Benutzername", placeholder="dein-benutzername")
        pw = st.text_input("Passwort", type="password", placeholder="Dein Passwort")
        if st.form_submit_button("Anmelden", type="secondary", width="stretch"):
            do_login(user, pw)


def render_register_form() -> None:
    with st.form("register_form", clear_on_submit=False, border=False):
        user = st.text_input("Benutzername", placeholder="z. B. creator123")
        email = st.text_input("E-Mail", placeholder="name@firma.de")
        pw = st.text_input("Passwort", type="password", placeholder="Mindestens 6 Zeichen")

        st.markdown('<div class="mb-login-captcha">', unsafe_allow_html=True)
        cap_col, ref_col = st.columns([0.84, 0.16], gap="small")
        with cap_col:
            captcha = st.number_input(
                f"Rechenaufgabe: {st.session_state.captcha_a} + {st.session_state.captcha_b} = ?",
                min_value=0,
                max_value=20,
                step=1,
            )
        with ref_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            refresh = st.form_submit_button("Neu")
        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Konto erstellen", type="secondary", width="stretch")

    if refresh:
        refresh_captcha()
        st.rerun()
    if submitted:
        do_register(user, email, pw, captcha)


def render_pitch_column() -> None:
    from ui.auth_premium import brand_mark_html

    st.markdown(brand_mark_html(), unsafe_allow_html=True)
    st.markdown(presentation_html(), unsafe_allow_html=True)


def render_login_column() -> None:
    with st.container(border=True):
        st.markdown(login_card_head_html(), unsafe_allow_html=True)

        mode = st.segmented_control(
            "Modus",
            options=["Anmelden", "Registrieren"],
            default="Anmelden",
            label_visibility="collapsed",
            width="stretch",
        )

        if mode == "Registrieren":
            st.caption("Kostenlos registrieren — dauert unter einer Minute.")
            render_register_form()
        else:
            render_google_login()
            render_login_form()

        st.markdown(login_footer_html(), unsafe_allow_html=True)


def render_auth() -> None:
    ensure_captcha()
    st.markdown('<div class="mb-login-route" aria-hidden="true"></div>', unsafe_allow_html=True)
    auth_css()
    handle_oauth_callback()

    pitch_col, login_col = st.columns([1.15, 0.85], gap="large")

    with pitch_col:
        render_pitch_column()

    with login_col:
        _show_oauth_notice()
        render_login_column()

    auth_css_final()
