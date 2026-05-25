import streamlit as st

from database import ensure_db_ready, get_user
from payments import confirm_checkout_session
from ui_core import load_css, sync_session_user
from ui.sidebar import render_sidebar
from ui.stripe_checkout import process_pending_stripe_redirect
from ui.error_boundary import safe_render
from ui.seo import inject_seo_meta
from services.session_auth import enforce_active_session

from pages.auth import render_auth
from pages.home import render_home
from pages.chat import render_chat
from pages.football import render_football
from pages.projects import render_projects
from pages.automation_lab import render_automation_lab
from pages.premium import render_premium

from pages.account import (
    render_dashboard,
    render_support,
    render_redeem,
)

from pages.admin import render_admin


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


def _oauth_callback_pending() -> bool:
    """Google redirects with ?code=&state= (path /oauth/google/callback via proxy)."""
    params = st.query_params
    code = params.get("code")
    state = params.get("state")
    if isinstance(code, list):
        code = code[0] if code else None
    if isinstance(state, list):
        state = state[0] if state else None
    return bool(code and state) or bool(params.get("error"))


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

if _oauth_callback_pending():
    st.session_state.page = "auth"
    render_auth()
    st.stop()

if not logged_in:
    st.session_state.page = "auth"
    render_auth()
    st.stop()


if process_pending_stripe_redirect():
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


# =========================================================
# SIDEBAR
# =========================================================

render_sidebar()

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

PAGE_HANDLERS = {
    "home": ("Mission Control", render_home),
    "chat": ("AI Assistant", render_chat),
    "projects": ("Projects", render_projects),
    "football": ("Football AI", render_football),
    "automation_lab": ("Automations", render_automation_lab),
    "automations": ("Automations", render_automations),
    "coding": ("Code Studio", lambda: render_media("coding")),
    "image": ("Image Studio", lambda: render_media("image")),
    "music": ("Music Studio", lambda: render_media("music")),
    "reels": ("Reels Studio", lambda: render_media("reels")),
    "video": ("Video Studio", lambda: render_media("video")),
    "dashboard": ("Dashboard", render_dashboard),
    "support": ("Support", render_support),
    "premium": ("Premium", render_premium),
    "redeem": ("Redeem", render_redeem),
    "admin": ("Admin Panel", render_admin),
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
