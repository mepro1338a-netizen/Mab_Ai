"""Global page error boundary — UI must never hard-crash."""
from __future__ import annotations

import traceback
from typing import Callable

import streamlit as st


def safe_render(page_name: str, render_fn: Callable[[], None]) -> None:
    ui_msg = "Ein Fehler ist aufgetreten."
    try:
        render_fn()
    except Exception as exc:
        try:
            from logger import log_exception, user_friendly_error
            import streamlit as st
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
        if st.button("Support öffnen", key=f"err_support_{page_name}", width="stretch"):
            st.session_state.page = "support"
            st.rerun()
        with st.expander("Details (Beta)"):
            st.code(traceback.format_exc())
