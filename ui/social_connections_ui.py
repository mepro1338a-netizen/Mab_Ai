"""Connected Accounts UI — YouTube, Instagram, TikTok."""
from __future__ import annotations

import html

import streamlit as st

from services.social_oauth import (
    SOCIAL_PLATFORMS,
    connect_auth_url,
    platform_configured,
    social_oauth_ready,
)
from services.social_publish import SocialPublishService


def _badge(status: str) -> str:
    labels = {
        "connected": ("verbunden", "ready"),
        "expired": ("Token abgelaufen", "failed"),
        "disconnected": ("nicht verbunden", "draft"),
        "api_pending": ("API Review", "scheduled"),
        "not_configured": ("Server nicht konfiguriert", "failed"),
    }
    text, cls = labels.get(status, (status, "draft"))
    return f'<span class="ve-badge {cls}">{html.escape(text)}</span>'


def _format_expires(iso: str) -> str:
    if not iso:
        return "—"
    try:
        return iso.replace("T", " ")[:16] + " UTC"
    except Exception:
        return "—"


def render_connected_accounts(username: str) -> None:
    svc = SocialPublishService(username)
    states = svc.connection_states()

    if not social_oauth_ready():
        st.warning(
            "OAUTH_STATE_SECRET fehlt in Railway — Verbindungen können nicht sicher gespeichert werden."
        )

    for st_info in states:
        pid = st_info["id"]
        label = st_info["label"]
        status = st_info["status"]
        meta = SOCIAL_PLATFORMS.get(pid) or {}

        st.markdown(
            f'<div style="margin:12px 0 8px 0;">{_badge(status)} '
            f'<strong style="color:#fff;">{html.escape(label)}</strong></div>',
            unsafe_allow_html=True,
        )

        if st_info.get("account_label") and status in ("connected", "expired"):
            st.caption(f"Kanal: **{st_info['account_label']}**")
        if st_info.get("channel_id") and pid == "youtube_shorts":
            st.caption(f"Channel-ID: `{st_info['channel_id']}`")

        if status == "connected" and pid == "youtube_shorts":
            if st_info.get("has_refresh_token"):
                st.caption(
                    f"Token gültig bis ca. {_format_expires(st_info.get('token_expires_at', ''))} "
                    "(Refresh aktiv)"
                )
            else:
                st.warning("Kein Refresh-Token — bitte erneut verbinden.")

            cache_key = f"yt_ch_{username}"
            if st.button("Kanalstatus aktualisieren", key=f"soc_ch_{pid}", width="stretch"):
                with st.spinner("Lade Kanal…"):
                    info, err = svc.youtube_channel_status(pid)
                if err:
                    st.error(err)
                else:
                    st.session_state[cache_key] = info

            info = st.session_state.get(cache_key)
            if info:
                st.markdown(
                    f"**{html.escape(str(info.get('title', '')))}** · "
                    f"{html.escape(str(info.get('subscriber_count', '—')))} Abonnenten · "
                    f"{html.escape(str(info.get('video_count', '—')))} Videos"
                )
                if info.get("thumbnail"):
                    st.image(info["thumbnail"], width=72)

        if status == "expired":
            st.caption("Bitte erneut verbinden — Access-Token ist abgelaufen.")

        if not platform_configured(pid):
            st.caption("API-Keys fehlen auf dem Server (Railway Variables).")
        elif not meta.get("api_ready"):
            st.caption(meta.get("review_note", "Publishing API in Vorbereitung."))

        c1, c2 = st.columns(2)
        with c1:
            if status in ("connected", "expired"):
                if st.button(
                    "Erneut verbinden" if status == "expired" else "Verbindung aktualisieren",
                    key=f"soc_re_{pid}",
                    width="stretch",
                ):
                    url = connect_auth_url(username, pid)
                    if url:
                        st.link_button("OAuth öffnen", url, key=f"soc_link_{pid}")
                    else:
                        st.error("OAuth nicht konfiguriert.")
            else:
                if st.button(
                    f"{label} verbinden",
                    key=f"soc_conn_{pid}",
                    type="primary",
                    width="stretch",
                ):
                    url = connect_auth_url(username, pid)
                    if url:
                        st.link_button("Weiter zu OAuth", url, key=f"soc_go_{pid}")
                    else:
                        st.error(
                            "Verbindung nicht verfügbar — "
                            "YOUTUBE_OAUTH_CLIENT_ID und OAUTH_STATE_SECRET prüfen."
                        )
        with c2:
            if status == "connected":
                if st.button("Trennen", key=f"soc_disc_{pid}", width="stretch"):
                    svc.disconnect(pid)
                    st.session_state.pop(f"yt_ch_{username}", None)
                    st.success("Getrennt.")
                    st.rerun()

        st.divider()
