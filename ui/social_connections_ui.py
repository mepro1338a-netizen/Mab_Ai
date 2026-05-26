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

        if st_info.get("account_label") and status == "connected":
            st.caption(f"Account: {st_info['account_label']}")

        if status == "expired":
            st.caption("Bitte erneut verbinden — Token ist abgelaufen.")

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
                        st.session_state["_oauth_redirect"] = url
                        st.query_params["page"] = "social_oauth"
                        st.markdown(
                            f'<meta http-equiv="refresh" content="0;url={html.escape(url)}">',
                            unsafe_allow_html=True,
                        )
                        st.link_button("OAuth öffnen", url, key=f"soc_link_{pid}")
                    else:
                        st.error("OAuth nicht konfiguriert.")
            else:
                if st.button(f"{label} verbinden", key=f"soc_conn_{pid}", type="primary", width="stretch"):
                    url = connect_auth_url(username, pid)
                    if url:
                        st.link_button("Weiter zu OAuth", url, key=f"soc_go_{pid}")
                    else:
                        st.error("Verbindung nicht verfügbar — Keys oder OAUTH_STATE_SECRET prüfen.")
        with c2:
            if status == "connected":
                if st.button("Trennen", key=f"soc_disc_{pid}", width="stretch"):
                    svc.disconnect(pid)
                    st.success("Getrennt.")
                    st.rerun()

        st.divider()

    redirect = st.session_state.pop("_oauth_redirect", None)
    if redirect:
        st.link_button("OAuth fortsetzen", redirect)
