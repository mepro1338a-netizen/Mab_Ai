import streamlit as st
from pathlib import Path


def is_logged_in():
    return bool(st.session_state.get("user"))


def require_login():
    if not is_logged_in():
        st.warning("Bitte zuerst einloggen.")
        st.session_state.page = "login"
        st.rerun()


def is_admin():
    return (
        st.session_state.get("role") in ["supporter", "moderator", "admin", "owner"]
        or int(st.session_state.get("admin_level", 0)) > 0
    )


def is_owner():
    return (
        st.session_state.get("role") == "owner"
        or int(st.session_state.get("admin_level", 0)) >= 999
    )


def plan_rank(plan):
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


def can_use(required_plan):
    return plan_rank(st.session_state.get("plan", "free")) >= plan_rank(required_plan) or is_admin()


def sync_session_user(user):
    if user:
        st.session_state.user = user["username"]
        st.session_state.email = user.get("email", "")
        st.session_state.plan = user["plan"]
        st.session_state.tokens = user["tokens"]
        st.session_state.role = user["role"]
        st.session_state.admin_level = user["admin_level"]


def read_file_bytes(path):
    path = Path(path)
    if path.exists():
        return path.read_bytes()
    return None


def render_download(path, label):
    data = read_file_bytes(path)

    if not data:
        st.error("Datei konnte nicht gefunden werden.")
        return

    suffix = Path(path).suffix.lower()

    if suffix in [".png", ".jpg", ".jpeg", ".webp"]:
        mime = "image/png"
    elif suffix in [".mp4", ".mov"]:
        mime = "video/mp4"
    else:
        mime = "application/octet-stream"

    st.download_button(
        label=label,
        data=data,
        file_name=Path(path).name,
        mime=mime,
        use_container_width=True,
    )
