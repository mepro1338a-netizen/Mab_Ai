# =========================================================
# social_integrations.py
# =========================================================

import streamlit as st

try:
    from config import (
        AUTO_POSTING_ENABLED_PLANS,
        SOCIAL_PLATFORMS,
    )
except Exception:
    AUTO_POSTING_ENABLED_PLANS = ["grand", "elite"]

    SOCIAL_PLATFORMS = {
        "instagram": {
            "label": "Instagram Reels",
            "enabled": True,
        },
        "tiktok": {
            "label": "TikTok",
            "enabled": True,
        },
        "youtube": {
            "label": "YouTube Shorts",
            "enabled": True,
        },
    }


# =========================================================
# USER PLAN
# =========================================================

def user_plan():
    return st.session_state.get("plan", "free")


# =========================================================
# ACCESS
# =========================================================

def can_use_auto_posting():
    return user_plan() in AUTO_POSTING_ENABLED_PLANS


# =========================================================
# CONNECT PANEL
# =========================================================

def render_social_connect_panel():
    st.subheader("🔗 Social Media Verbindungen")

    if not can_use_auto_posting():
        st.warning(
            "Auto-Posting ist erst ab dem Grand Plan verfügbar."
        )
        return False

    st.success(
        "Auto-Posting für TikTok, Instagram und YouTube ist freigeschaltet."
    )

    st.caption(
        "Verbinde deine Plattformen für automatisierte Uploads und Posting-Automation."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        instagram = st.checkbox(
            "Instagram verbinden",
            key="connect_instagram",
        )

    with c2:
        tiktok = st.checkbox(
            "TikTok verbinden",
            key="connect_tiktok",
        )

    with c3:
        youtube = st.checkbox(
            "YouTube verbinden",
            key="connect_youtube",
        )

    st.info(
        "Momentan ist dies ein vorbereiteter Connector. "
        "Später kannst du echte OAuth/API-Logins integrieren."
    )

    return instagram or tiktok or youtube


# =========================================================
# SELECTED PLATFORMS
# =========================================================

def get_selected_platforms():
    platforms = []

    if st.session_state.get("connect_instagram"):
        platforms.append("Instagram Reels")

    if st.session_state.get("connect_tiktok"):
        platforms.append("TikTok")

    if st.session_state.get("connect_youtube"):
        platforms.append("YouTube Shorts")

    return platforms


# =========================================================
# AUTO POSTING NOTE
# =========================================================

def build_auto_posting_note(enabled, post_time):
    if not enabled:
        return "Auto-Posting deaktiviert"

    platforms = get_selected_platforms()

    if not platforms:
        return "Auto-Posting aktiv, aber keine Plattform ausgewählt"

    return (
        f"Auto-Posting aktiv | "
        f"Plattformen: {', '.join(platforms)} | "
        f"Zeit: {post_time}"
    )


# =========================================================
# MOCK POSTING
# =========================================================

def simulate_social_upload(platforms, title):
    results = []

    for platform in platforms:
        results.append(
            {
                "platform": platform,
                "status": "queued",
                "title": title,
            }
        )

    return results


# =========================================================
# STATUS BOX
# =========================================================

def render_upload_status(results):
    if not results:
        return

    st.subheader("📤 Upload Queue")

    for result in results:
        platform = result.get("platform")
        status = result.get("status")

        st.success(
            f"{platform}: {status}"
        )


# =========================================================
# FUTURE OAUTH PLACEHOLDER
# =========================================================

def render_future_api_info():
    with st.expander("⚙️ Geplante API Integrationen"):
        st.markdown(
            """
### Instagram
- Meta Graph API
- Reel Uploads
- Geplante Posts

### TikTok
- TikTok Content Posting API
- Auto Upload
- Creator Automation

### YouTube
- YouTube Shorts Upload
- Thumbnail Automation
- Scheduled Publishing

### Später möglich
- Auto Hashtags
- Trend Analyse
- KI Post Zeiten
- Multi Upload Queue
- Vollautomatische Social Pipelines
"""
        )


# =========================================================
# AUTO POST SETTINGS
# =========================================================

def render_auto_post_settings():
    if not can_use_auto_posting():
        return None

    st.subheader("⚡ Automation")

    auto_post = st.checkbox(
        "Automatisiertes Posting aktivieren",
        key="enable_auto_posting",
    )

    if not auto_post:
        return {
            "enabled": False,
        }

    posting_mode = st.selectbox(
        "Posting Modus",
        [
            "Manuell bestätigen",
            "Automatisch posten",
            "Geplant posten",
        ],
    )

    best_time = st.text_input(
        "Optimale Posting Zeit",
        placeholder="z.B. täglich 19:00",
    )

    use_ai_caption = st.checkbox(
        "KI soll Captions automatisch optimieren",
        value=True,
    )

    use_ai_hashtags = st.checkbox(
        "KI soll Hashtags automatisch generieren",
        value=True,
    )

    return {
        "enabled": True,
        "mode": posting_mode,
        "best_time": best_time,
        "ai_caption": use_ai_caption,
        "ai_hashtags": use_ai_hashtags,
    }