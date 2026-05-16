import streamlit as st

from config import TOKEN_COSTS
from database import get_user, update_tokens, save_usage
from ui_core import sync_session_user


def user_plan():
    return st.session_state.get("plan", "free")


def username():
    return st.session_state.get("user")


def can_use_auto_posting_plan():
    return user_plan() in ["grand", "elite"]


def auto_posting_unlocked():
    return bool(st.session_state.get("auto_posting_unlocked", False))


def unlock_auto_posting():
    cost = int(TOKEN_COSTS.get("auto_posting_unlock", 1000))

    user = get_user(username())

    if not user:
        return False, "User nicht gefunden."

    tokens = int(user.get("tokens", 0) or 0)

    if tokens < cost:
        return False, f"Nicht genug Tokens. BenÃ¶tigt: {cost}, verfÃ¼gbar: {tokens}"

    update_tokens(username(), tokens - cost)

    save_usage(
        username=username(),
        tool="auto_posting_unlock",
        prompt="Auto-Posting einmalig freigeschaltet",
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="internal",
        status="success",
    )

    updated_user = get_user(username())

    if updated_user:
        sync_session_user(updated_user)

    st.session_state.auto_posting_unlocked = True

    return True, "Auto-Posting wurde freigeschaltet."


def render_social_connect_panel():
    st.subheader("ðŸ”— Auto-Posting")

    if not can_use_auto_posting_plan():
        st.warning("Auto-Posting ist erst ab Grand verfÃ¼gbar.")
        return False

    if not auto_posting_unlocked():
        cost = int(TOKEN_COSTS.get("auto_posting_unlock", 1000))

        st.info(
            f"Auto-Posting kostet einmalig {cost} Tokens zum Freischalten."
        )

        if st.button("âš¡ Auto-Posting freischalten", width="stretch"):
            ok, msg = unlock_auto_posting()

            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        return False

    st.success("Auto-Posting ist freigeschaltet.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.checkbox("Instagram Reels", key="connect_instagram")

    with c2:
        st.checkbox("TikTok", key="connect_tiktok")

    with c3:
        st.checkbox("YouTube Shorts", key="connect_youtube")

    st.caption(
        "Aktuell vorbereitet. SpÃ¤ter werden hier echte OAuth/API-Verbindungen eingebaut."
    )

    return True


def get_selected_platforms():
    platforms = []

    if st.session_state.get("connect_instagram"):
        platforms.append("Instagram Reels")

    if st.session_state.get("connect_tiktok"):
        platforms.append("TikTok")

    if st.session_state.get("connect_youtube"):
        platforms.append("YouTube Shorts")

    return platforms


def build_auto_posting_note(enabled, post_time):
    if not enabled:
        return "Auto-Posting deaktiviert"

    platforms = get_selected_platforms()

    if not platforms:
        return "Auto-Posting aktiv, aber keine Plattform gewÃ¤hlt"

    return f"Auto-Posting aktiv | Plattformen: {', '.join(platforms)} | Zeit: {post_time}"
