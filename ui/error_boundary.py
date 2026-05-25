"""Global page error boundary — UI must never hard-crash."""
from __future__ import annotations

import traceback
from typing import Callable

import streamlit as st


def safe_render(page_name: str, render_fn: Callable[[], None]) -> None:
    try:
        render_fn()
    except Exception as exc:
        try:
            from logger import log_error
            log_error(f"Page crash [{page_name}]: {exc}\n{traceback.format_exc()}")
        except Exception:
            pass

        st.markdown(
            f"""
<div class="mb-error-panel">
    <h3>Workspace vorübergehend nicht verfügbar</h3>
    <p>
        <strong>{page_name}</strong> konnte nicht geladen werden.
        Deine Session bleibt aktiv — bitte Seite neu laden oder wechsle den Workspace.
    </p>
    <p style="margin-top:12px;font-size:12px;opacity:.85;">
        Technisch: {type(exc).__name__}
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
