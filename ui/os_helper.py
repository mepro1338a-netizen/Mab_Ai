"""MaByte OS Guide — sidebar copilot for safe navigation (Mab AI Beta)."""
from __future__ import annotations

import html

import streamlit as st

from services.os_guide import (
    QUICK_PROMPTS,
    build_guide_reply,
    format_reply_html,
    sanitize_user_message,
)


def _session_defaults() -> None:
    st.session_state.setdefault("os_guide_open", True)
    st.session_state.setdefault("os_guide_history", [])
    st.session_state.setdefault("os_guide_last_reply", "")


def render_os_helper() -> None:
    """Sidebar-only — rule-based guide, no API keys required."""
    if not st.session_state.get("logged_in"):
        return

    _session_defaults()

    st.markdown(
        """
<div class="os-helper-wrap">
    <div class="os-helper-title">Mab AI · OS Guide</div>
    <div class="os-helper-name">Production Beta Assistant</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Guide öffnen", expanded=bool(st.session_state.get("os_guide_open"))):
        for label, action in QUICK_PROMPTS:
            if st.button(label, key=f"os_chip_{action}", width="stretch"):
                st.session_state.os_guide_pending_query = label
                st.rerun()

        pending = st.session_state.pop("os_guide_pending_query", None)
        user_q = st.text_input(
            "Frage an den Guide",
            placeholder="z.B. Wo ist Odds Lab?",
            key="os_guide_input",
            label_visibility="collapsed",
        )

        if st.button("Antworten", key="os_guide_ask", width="stretch"):
            pending = user_q or pending

        if pending:
            reply = build_guide_reply(
                sanitize_user_message(str(pending)),
                current_page=str(st.session_state.get("page") or "home"),
                plan=str(st.session_state.get("plan") or "free"),
                football_plan=str(st.session_state.get("football_plan") or "none"),
                tokens=int(st.session_state.get("tokens") or 0),
            )
            st.session_state.os_guide_last_reply = reply.get("text") or ""
            hist = list(st.session_state.get("os_guide_history") or [])
            hist.append({"q": str(pending)[:120], "a": st.session_state.os_guide_last_reply[:400]})
            st.session_state.os_guide_history = hist[-8:]
            nav = reply.get("navigate")
            if nav:
                st.session_state.page = nav
                st.rerun()

        last = st.session_state.get("os_guide_last_reply")
        if last:
            st.markdown(
                f'<div class="os-helper-msg">{format_reply_html(last)}</div>',
                unsafe_allow_html=True,
            )

        if st.button("Support öffnen", key="os_guide_support", width="stretch"):
            st.session_state.page = "support"
            st.rerun()
