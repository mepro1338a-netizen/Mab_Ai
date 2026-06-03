import html
import traceback
from typing import Callable

import streamlit as st

from config import APP_BASE_URL, APP_NAME, APP_TAGLINE
from database import ensure_db_ready, get_user
from payments import confirm_checkout_session
from services.session_auth import enforce_active_session
from ui.sidebar import LEGACY_PAGE_ALIASES, render_sidebar
from ui_core import load_css, sync_session_user

from pages.auth import render_auth
from pages.chat import render_chat
from ui.dashboard import render_home
from ui.football import render_football_betting_board
from pages.projects import render_projects
from pages.automation_lab import render_automation_lab
from pages.premium import render_premium

from pages.account import render_dashboard


def render_football() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    def _open_premium() -> None:
        st.session_state.page = "premium"
        st.rerun()

    render_football_betting_board(
        username=str(st.session_state.get("user") or ""),
        session_plan=str(st.session_state.get("football_plan") or "none"),
        open_premium=_open_premium,
    )


# =========================================================
# INLINE: ui.seo (single consumer: ui.py)
# =========================================================

def inject_seo_meta() -> None:
    title = f"{APP_NAME} — AI Operating System"
    desc = APP_TAGLINE or "One AI system. Infinite workflows."
    url = APP_BASE_URL or "https://mabyte.de"
    image = f"{url.rstrip('/')}/static/og-preview.png"

    st.markdown(
        f"""
<meta name="description" content="{html.escape(desc)}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{html.escape(title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{html.escape(url)}" />
<meta property="og:site_name" content="{html.escape(APP_NAME)}" />
<meta property="og:image" content="{html.escape(image)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(title)}" />
<meta name="twitter:description" content="{html.escape(desc)}" />
<meta name="theme-color" content="#09090b" />
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# INLINE: ui.error_boundary (single consumer: ui.py)
# =========================================================

def safe_render(page_name: str, render_fn: Callable[[], None]) -> None:
    ui_msg = "Ein Fehler ist aufgetreten."
    try:
        render_fn()
    except Exception as exc:
        try:
            from logger import log_exception, user_friendly_error

            log_exception(
                exc,
                category="system",
                page=page_name,
                user=str(st.session_state.get("user") or ""),
            )
            ui_msg = user_friendly_error("system")
        except Exception:
            pass

        st.markdown(
            f"""
<div class="mb-error-panel">
    <h3>Workspace vorübergehend nicht verfügbar</h3>
    <p>{ui_msg}</p>
    <p style="margin-top:10px;font-size:13px;opacity:.9;">
        Workspace: <strong>{page_name}</strong> — Session bleibt aktiv.
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Zur Startseite", key=f"err_home_{page_name}", width="stretch"):
            st.session_state.page = "home"
            st.rerun()
        with st.expander("Details (Beta)"):
            st.code(traceback.format_exc())

# =========================================================
# SAFE MEDIA IMPORT
# =========================================================

try:
    from pages.media import render_media
    MEDIA_IMPORT_ERROR = None
except Exception as e:
    MEDIA_IMPORT_ERROR = e

    def render_media(active_tool="reels"):
        st.error("Media Workspace konnte nicht geladen werden.")
        st.code(str(MEDIA_IMPORT_ERROR))
        st.info(
            "Prüfe pages/media.py: Dort darf NICHT `from pages.media import render_media` stehen "
            "und ganz unten muss `def render_media(...)` existieren."
        )


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MaByte",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# INIT
# =========================================================

if not ensure_db_ready():
    st.error(
        "Datenbank konnte nicht gestartet werden. "
        "Bitte kurz warten und neu laden — oder Support kontaktieren."
    )
    st.stop()


def _qp_first(value) -> str:
    if isinstance(value, list):
        return str(value[0] if value else "").strip()
    return str(value or "").strip()


def _is_social_oauth_callback() -> bool:
    """YouTube/IG/TikTok connect — must not be handled as login OAuth."""
    page = _qp_first(st.query_params.get("page"))
    if page == "social_oauth":
        return True
    if st.session_state.get("page") == "social_oauth":
        return bool(_qp_first(st.query_params.get("code")))
    return False


def _is_google_login_oauth_callback() -> bool:
    """Google account login — not social publishing OAuth."""
    if _is_social_oauth_callback():
        return False
    code = _qp_first(st.query_params.get("code"))
    state = _qp_first(st.query_params.get("state"))
    if not code and not _qp_first(st.query_params.get("error")):
        return False
    if not state:
        return bool(_qp_first(st.query_params.get("error")))
    from oauth_service import verify_state

    return verify_state(state) == "google"


# =========================================================
# SESSION DEFAULTS
# =========================================================

DEFAULTS = {
    "page": "auth",
    "logged_in": False,
    "user": None,
    "email": "",
    "plan": "free",
    "football_plan": "none",
    "tokens": 0,
    "role": "user",
    "admin_level": 0,
    "active_project_id": None,
    # Football AI workspace
    "fb_v": 9,
    "fb_mode": "curated",
    "fb_competition": "deutschland",
    "fb_time": "heute",
    "fb_payload": None,
    "fb_detail": None,
    "fb_sel": None,
    "fb_cache_key": "",
    "fb_displayed_topspiele_count": 0,
    "fb_displayed_allspiele_count": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOCAL FALLBACK PAGE
# =========================================================

def render_automations():
    st.title("Automations")
    st.caption("Geplante Abläufe, Posting Flows und System Actions.")

    with st.container(border=True):
        st.subheader("Automation Center")
        st.info("Noch keine Automationen aktiv.")


# =========================================================
# AUTH CHECK
# =========================================================

logged_in = bool(
    st.session_state.get("logged_in")
    and st.session_state.get("user")
)

# Social platform OAuth (YouTube/IG/TikTok — not login)
if _is_social_oauth_callback():
    from pages.social_oauth import render_social_oauth_callback

    render_social_oauth_callback()
    st.stop()

# Google login OAuth callback
if not logged_in and _is_google_login_oauth_callback():
    from pages.auth import handle_google_oauth_callback

    handle_google_oauth_callback()
    st.stop()

if not logged_in:
    st.session_state.page = "auth"
    render_auth()
    st.stop()


def handle_payment_callback() -> None:
    params = st.query_params
    if params.get("checkout") == "cancel" or params.get("payment_cancel") == "1":
        st.query_params.clear()
        st.session_state.payment_notice = ("info", "Checkout abgebrochen.")
        return

    if params.get("checkout") != "success" and params.get("payment_success") != "1":
        return

    session_id = params.get("session_id") or ""
    st.query_params.clear()

    if not session_id:
        st.session_state.payment_notice = ("error", "Keine Stripe-Session gefunden.")
        return

    ok, msg = confirm_checkout_session(session_id)
    user = get_user(st.session_state.get("user"))
    if user:
        sync_session_user(user)

    level = "success" if ok else "warning"
    st.session_state.payment_notice = (level, msg)


handle_payment_callback()

enforce_active_session()

load_css()
inject_seo_meta()


notice = st.session_state.pop("payment_notice", None)
if notice:
    level, text = notice
    if level == "success":
        st.success(text)
    elif level == "error":
        st.error(text)
    elif level == "info":
        st.info(text)
    else:
        st.warning(text)


# =========================================================
# ROUTER
# =========================================================

page = st.session_state.get("page", "home")
if page in LEGACY_PAGE_ALIASES:
    page = LEGACY_PAGE_ALIASES[page]
    st.session_state.page = page

# =========================================================
# SIDEBAR (single component for all routes)
# =========================================================

render_sidebar(page)

PAGE_HANDLERS = {
    "social_oauth": ("Social Connect", lambda: None),
    "home": ("Dashboard", render_home),
    "chat": ("AI Assistant", render_chat),
    "projects": ("Projects", render_projects),
    "football": ("Football AI", render_football),
    "automation_lab": ("Automations", render_automation_lab),
    "automations": ("Automations", render_automations),
    "coding": ("Code Studio", lambda: render_media("coding")),
    "image": ("Image Studio", lambda: render_media("image")),
    "music": ("Music Studio", lambda: render_media("music")),
    "video": ("Video Studio", lambda: render_media("video")),
    "dashboard": ("Dashboard", render_dashboard),
    "premium": ("Premium", render_premium),
}

if page == "auth":
    st.session_state.page = "home"
    st.rerun()
elif page in PAGE_HANDLERS:
    label, handler = PAGE_HANDLERS[page]
    safe_render(label, handler)
else:
    st.session_state.page = "home"
    st.rerun()

from ui.styles import inject_theme_lock

inject_theme_lock()
