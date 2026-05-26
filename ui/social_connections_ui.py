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


def _render_oauth_connect(username: str, pid: str, label: str, *, reconnect: bool = False) -> None:
    """Direct OAuth link — no nested button+link_button (avoids Streamlit widget-tree crashes)."""
    url = connect_auth_url(username, pid)
    btn_label = "Erneut verbinden" if reconnect else f"{label} verbinden"
    if url:
        st.link_button(
            btn_label,
            url,
            type="primary",
            use_container_width=True,
            key=f"soc_oauth_{pid}_{'re' if reconnect else 'new'}",
        )
    else:
        st.button(
            btn_label,
            disabled=True,
            use_container_width=True,
            key=f"soc_oauth_dis_{pid}",
        )
        if not social_oauth_ready():
            st.caption("OAUTH_STATE_SECRET in Railway setzen.")
        else:
            st.caption("API-Keys für diese Plattform in Railway setzen.")


def render_connected_accounts(username: str) -> None:
    try:
        from db.video_engine import init_video_engine_tables

        init_video_engine_tables()
    except Exception:
        pass

    try:
        svc = SocialPublishService(username)
        states = svc.connection_states()
    except Exception as exc:
        st.error("Verbindungen konnten nicht geladen werden.")
        st.caption("Datenbank-Tabellen werden beim nächsten Seitenaufruf initialisiert.")
        with st.expander("Technische Details"):
            st.code(str(exc)[:400])
        return

    if not social_oauth_ready():
        st.warning(
            "**OAUTH_STATE_SECRET** fehlt in Railway — OAuth-Verbindungen sind deaktiviert. "
            "Setze ein langes zufälliges Secret und starte den Service neu."
        )

    st.caption(
        "YouTube: `YOUTUBE_OAUTH_CLIENT_ID`, `YOUTUBE_OAUTH_CLIENT_SECRET`, `OAUTH_STATE_SECRET` · "
        "Redirect: `/?page=social_oauth`"
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
            st.caption(f"Kanal: **{html.escape(str(st_info['account_label']))}**")
        if st_info.get("channel_id") and pid == "youtube_shorts":
            st.caption(f"Channel-ID: `{html.escape(str(st_info['channel_id']))}`")

        if status == "connected" and pid == "youtube_shorts":
            if st_info.get("has_refresh_token"):
                st.caption(
                    f"Token gültig bis ca. {_format_expires(st_info.get('token_expires_at', ''))} "
                    "(Refresh aktiv)"
                )
            else:
                st.warning("Kein Refresh-Token — bitte erneut verbinden.")

            cache_key = f"yt_ch_{username}"
            if st.button(
                "Kanalstatus aktualisieren",
                key=f"soc_ch_{pid}",
                use_container_width=True,
            ):
                with st.spinner("Lade Kanal…"):
                    info, err = svc.youtube_channel_status(pid)
                if err:
                    st.error(err)
                elif info:
                    st.session_state[cache_key] = info

            info = st.session_state.get(cache_key)
            if info:
                st.markdown(
                    f"**{html.escape(str(info.get('title', '')))}** · "
                    f"{html.escape(str(info.get('subscriber_count', '—')))} Abonnenten · "
                    f"{html.escape(str(info.get('video_count', '—')))} Videos"
                )
                thumb = info.get("thumbnail")
                if thumb:
                    try:
                        st.image(str(thumb), width=72)
                    except Exception:
                        pass

        if status == "expired":
            st.caption("Bitte erneut verbinden — Access-Token ist abgelaufen.")

        if status == "not_configured":
            st.caption("API-Keys fehlen auf dem Server (Railway Variables).")
        elif not meta.get("api_ready"):
            st.caption(meta.get("review_note", "Publishing API in Vorbereitung."))

        c1, c2 = st.columns(2)
        with c1:
            if status in ("connected", "expired"):
                _render_oauth_connect(username, pid, label, reconnect=True)
            elif status == "disconnected" and platform_configured(pid):
                _render_oauth_connect(username, pid, label)
            elif status == "disconnected":
                st.button(
                    f"{label} verbinden",
                    disabled=True,
                    use_container_width=True,
                    key=f"soc_dis_{pid}",
                )
            else:
                st.button(
                    "Nicht verfügbar",
                    disabled=True,
                    use_container_width=True,
                    key=f"soc_na_{pid}",
                )

        with c2:
            if status == "connected":
                if st.button("Trennen", key=f"soc_disc_{pid}", use_container_width=True):
                    svc.disconnect(pid)
                    st.session_state.pop(f"yt_ch_{username}", None)
                    st.success("Getrennt.")
                    st.rerun()

        st.divider()
