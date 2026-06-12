"""Plan-basierte Feature-Gates — config.PLANS als Quelle, Admin-Bypass."""
from __future__ import annotations

import streamlit as st

from config import PLANS, has_feature, plan_rank
from security import is_admin

FEATURE_MESSAGES: dict[str, str] = {
    "image": "Bildgenerierung ist ab **Pro** verfügbar.",
    "music": "Music Studio ist ab **Pro** verfügbar.",
    "coding": "Code Studio ist ab **Pro** verfügbar.",
    "video": "Voller Video Creator ist ab **Grand** verfügbar.",
    "reels": "Reels & Shorts Creator ist ab **Grand** verfügbar.",
    "automation": "Content Automation ist ab **Grand** verfügbar.",
}


def user_plan_key(user: dict | None) -> str:
    if user:
        return str(user.get("plan") or "free").lower()
    return str(st.session_state.get("plan") or "free").lower()


def _resolve_user(user: dict | None) -> dict:
    if user:
        return user
    from services.session_auth import _cached_session_user

    return _cached_session_user() or {}


def user_is_admin(user: dict | None = None) -> bool:
    return is_admin(_resolve_user(user))


def user_has_feature(user: dict | None, feature: str) -> bool:
    if user_is_admin(user):
        return True
    return has_feature(user_plan_key(user), feature)


def is_free_plan(user: dict | None = None) -> bool:
    if user_is_admin(user):
        return False
    return plan_rank(user_plan_key(user)) == 0


def min_plan_for_feature(feature: str) -> tuple[str, str]:
    for key in ("pro", "grand", "elite"):
        if has_feature(key, feature):
            return key, str(PLANS[key].get("label", key))
    return "pro", "Pro"


def require_plan_feature(
    feature: str,
    *,
    user: dict | None = None,
    message: str | None = None,
    button_key: str = "plan_gate_upgrade",
) -> bool:
    """
    True = Zugriff erlaubt. False = Upgrade-Hinweis angezeigt, Aktion blockieren.
    """
    if user_has_feature(user, feature):
        return True

    _, label = min_plan_for_feature(feature)
    text = message or FEATURE_MESSAGES.get(
        feature,
        f"Dieses Feature erfordert mindestens **{label}**.",
    )
    st.warning(text)
    if st.button(f"Zu Premium ({label})", key=button_key, type="primary"):
        st.session_state.page = "premium"
        st.rerun()
    return False


def free_video_studio_allowed(user: dict | None = None) -> bool:
    """Free: nur kurzer MaByte Studio Export (Video-Modus, kein KI)."""
    return is_free_plan(user)


def feature_blocked_message(user: dict | None, feature: str) -> str | None:
    """Server-seitige Prüfung — Fehlermeldung oder None."""
    if user_has_feature(user, feature):
        return None
    _, label = min_plan_for_feature(feature)
    return f"Dieses Feature erfordert mindestens {label}."
