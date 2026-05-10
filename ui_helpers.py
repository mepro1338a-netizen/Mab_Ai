# =========================================================
# ui_helpers.py
# =========================================================

import streamlit as st


# =========================================================
# LOGIN CHECK
# =========================================================

def is_logged_in():
    return bool(st.session_state.get("user"))


# =========================================================
# REQUIRE LOGIN
# =========================================================

def require_login():
    if not is_logged_in():
        st.warning("Bitte zuerst einloggen.")
        st.session_state.page = "login"
        st.stop()


# =========================================================
# SESSION SYNC
# =========================================================

def sync_session_user(user):
    if not user:
        return

    st.session_state.user = user.get("username")
    st.session_state.email = user.get("email", "")

    st.session_state.plan = user.get("plan", "free")

    st.session_state.tokens = int(
        user.get("tokens", 0) or 0
    )

    st.session_state.role = user.get("role", "user")

    st.session_state.admin_level = int(
        user.get("admin_level", 0) or 0
    )

    st.session_state.logged_in = True


# =========================================================
# ROLE HELPERS
# =========================================================

def current_role():
    return st.session_state.get("role", "user")


def current_admin_level():
    return int(
        st.session_state.get("admin_level", 0) or 0
    )


def is_supporter():
    return current_role() in [
        "supporter",
        "moderator",
        "admin",
        "owner",
    ]


def is_moderator():
    return current_role() in [
        "moderator",
        "admin",
        "owner",
    ]


def is_admin():
    return current_role() in [
        "admin",
        "owner",
    ]


def is_owner():
    return current_role() == "owner"


# =========================================================
# REQUIRE ROLES
# =========================================================

def require_supporter():
    require_login()

    if not is_supporter():
        st.error("Keine Berechtigung.")
        st.stop()


def require_moderator():
    require_login()

    if not is_moderator():
        st.error("Keine Berechtigung.")
        st.stop()


def require_admin():
    require_login()

    if not is_admin():
        st.error("Keine Berechtigung.")
        st.stop()


def require_owner():
    require_login()

    if not is_owner():
        st.error("Nur Owner erlaubt.")
        st.stop()


# =========================================================
# NAVIGATION
# =========================================================

def go_to(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# LOGOUT
# =========================================================

def logout_user():
    keys = [
        "user",
        "email",
        "plan",
        "tokens",
        "role",
        "admin_level",
        "logged_in",
    ]

    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.page = "home"

    st.rerun()


# =========================================================
# PAGE TITLE
# =========================================================

def page_header(title, subtitle=None):
    st.title(title)

    if subtitle:
        st.caption(subtitle)


# =========================================================
# INFO BOX
# =========================================================

def premium_required(feature_name="Dieses Feature"):
    st.error(
        f"{feature_name} ist in deinem aktuellen Plan nicht verfügbar."
    )

    if st.button(
        "💎 Premium ansehen",
        use_container_width=True,
    ):
        go_to("premium")


# =========================================================
# TOKEN HELPERS
# =========================================================

def user_tokens():
    return int(
        st.session_state.get("tokens", 0) or 0
    )


def has_tokens(cost):
    return user_tokens() >= int(cost)


# =========================================================
# PLAN HELPERS
# =========================================================

def current_plan():
    return st.session_state.get("plan", "free")


def has_plan_feature(feature):
    from config import PLANS

    plan = current_plan()

    features = PLANS.get(
        plan,
        PLANS["free"],
    ).get("features", [])

    return (
        "all" in features
        or feature in features
    )


# =========================================================
# SIMPLE STATUS BOX
# =========================================================

def status_box(label, value):
    with st.container(border=True):
        st.caption(label)
        st.subheader(value)