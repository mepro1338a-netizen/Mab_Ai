"""MaByte OS Guide — Dashboard copilot (Mab AI Beta)."""
from __future__ import annotations

import streamlit as st

from services.os_guide import (
    QUICK_PROMPTS,
    build_guide_reply,
    format_reply_html,
    sanitize_user_message,
)


def _session_defaults() -> None:
    st.session_state.setdefault("os_guide_history", [])
    st.session_state.setdefault("os_guide_last_reply", "")


def render_os_guide_dashboard() -> None:
    """Mab AI Guide — shown on Dashboard only."""
    if not st.session_state.get("logged_in"):
        return

    _session_defaults()

    st.markdown(
        """
<div class="os-guide-panel">
    <div class="os-guide-kicker">Mab AI · OS Guide</div>
    <div class="os-guide-title">Production Beta Assistant</div>
    <div class="os-guide-sub">Navigation, Premium, Football & Support — sicher, ohne Admin-Rechte.</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    chips = st.columns(5)
    for i, (label, action) in enumerate(QUICK_PROMPTS):
        with chips[i % 5]:
            if st.button(label, key=f"os_dash_chip_{action}", width="stretch"):
                st.session_state.os_guide_pending_query = label
                st.rerun()

    c1, c2 = st.columns([1.2, 1])
    with c1:
        pending = st.session_state.pop("os_guide_pending_query", None)
        user_q = st.text_input(
            "Frage an den Guide",
            placeholder="z.B. Wo ist Odds Lab? · Premium upgraden?",
            key="os_guide_dash_input",
        )
        if st.button("Antworten", key="os_guide_dash_ask", type="primary", width="stretch"):
            pending = user_q or pending

        if pending:
            reply = build_guide_reply(
                sanitize_user_message(str(pending)),
                current_page=str(st.session_state.get("page") or "dashboard"),
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

    with c2:
        last = st.session_state.get("os_guide_last_reply")
        if last:
            st.markdown(
                f'<div class="os-guide-reply">{format_reply_html(last)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="os-guide-reply os-guide-empty">Stelle eine Frage oder wähle einen Quick-Link.</div>',
                unsafe_allow_html=True,
            )
        if st.button("Support öffnen", key="os_guide_dash_support", width="stretch"):
            st.session_state.page = "support"
            st.rerun()
