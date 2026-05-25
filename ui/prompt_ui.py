"""Unified MaByte prompt bar — purple pill (chat) + matching text areas."""
from __future__ import annotations

import streamlit as st

from ui.styles import inject_css

MABYTE_PROMPT_CSS = """
/* ===== Bottom chat input (Frag MaByte…) ===== */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
    border: 0 !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    max-width: 920px !important;
    margin: 0 auto !important;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background:
        radial-gradient(circle at top left, rgba(192,132,252,.32), transparent 28%),
        radial-gradient(circle at bottom right, rgba(96,165,250,.14), transparent 34%),
        linear-gradient(135deg, rgba(58,18,92,.98), rgba(28,8,52,.99)) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(192,132,252,.55) !important;
    box-shadow:
        0 0 38px rgba(168,85,247,.42),
        0 10px 40px rgba(0,0,0,.22),
        inset 0 0 0 1px rgba(255,255,255,.04) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: transparent !important;
    color: #f5d0fe !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    box-shadow: none !important;
    outline: none !important;
    min-height: 24px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(245,208,254,.72) !important;
    font-weight: 900 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #9333ea, #c084fc) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    box-shadow: 0 0 26px rgba(192,132,252,.55) !important;
}

[data-testid="stChatInput"] button:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 0 36px rgba(192,132,252,.72) !important;
}

/* ===== Form prompt fields (studios, guide, projects) ===== */
.mb-prompt-marker { display: none; }

div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) [data-testid="stTextArea"] > div,
div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) [data-testid="stTextInput"] > div > div {
    background:
        radial-gradient(circle at top left, rgba(192,132,252,.22), transparent 30%),
        linear-gradient(135deg, rgba(58,18,92,.95), rgba(28,8,52,.98)) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(192,132,252,.45) !important;
    box-shadow:
        0 0 28px rgba(168,85,247,.28),
        inset 0 0 0 1px rgba(255,255,255,.04) !important;
}

div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) textarea,
div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) input {
    background: transparent !important;
    color: #f5d0fe !important;
    font-weight: 800 !important;
    font-size: 15px !important;
}

div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) textarea::placeholder,
div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) input::placeholder {
    color: rgba(245,208,254,.65) !important;
    font-weight: 800 !important;
}

.mb-prompt-submit .stButton > button {
    background: linear-gradient(135deg, #9333ea, #7c3aed) !important;
    color: #fff !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    font-weight: 1000 !important;
    min-height: 48px !important;
    box-shadow: 0 0 24px rgba(168,85,247,.35) !important;
}

/* OS hero (chat / dashboard) */
.mb-os-title {
    text-align: center;
    font-size: clamp(42px, 8vw, 64px);
    line-height: .9;
    font-weight: 1000;
    letter-spacing: -3px;
    margin-top: 8px;
    margin-bottom: 6px;
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.mb-os-sub {
    text-align: center;
    color: #cbd5e1 !important;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 20px;
}
.mb-os-ready {
    text-align: center;
    color: #c084fc !important;
    font-size: 13px;
    font-weight: 800;
    margin: 12px 0 20px 0;
    padding: 12px 16px;
    border-radius: 16px;
    background: rgba(88,28,135,.2);
    border: 1px solid rgba(168,85,247,.25);
}
.mb-quick-label {
    color: #c084fc !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .2em;
    text-transform: uppercase;
    margin-bottom: 10px;
    text-align: center;
}
.mb-quick-grid .stButton > button {
    min-height: 52px !important;
    border-radius: 16px !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.16), transparent 34%),
        linear-gradient(145deg, rgba(18,14,34,.9), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.22) !important;
    color: #f8fafc !important;
    font-weight: 900 !important;
}
.mb-quick-grid .stButton > button:hover {
    border-color: rgba(255,231,163,.3) !important;
    box-shadow: 0 0 20px rgba(168,85,247,.2) !important;
}
"""


def inject_ma_prompt_css() -> None:
    inject_css(MABYTE_PROMPT_CSS)


def render_os_hero() -> None:
    st.markdown(
        """
<div class="mb-os-title">MaByte</div>
<div class="mb-os-sub">Dein AI Operating System.</div>
        """,
        unsafe_allow_html=True,
    )


def render_os_ready_hint() -> None:
    st.markdown(
        '<div class="mb-os-ready">✦ MaByte ist bereit. Nutze einen Quick Start oder frag direkt unten.</div>',
        unsafe_allow_html=True,
    )


def render_quickstart_grid(key_prefix: str = "qs") -> str | None:
    st.markdown('<div class="mb-quick-label">Quick Start</div>', unsafe_allow_html=True)
    prompts = [
        ("🚀 Wachstum", "Erstelle mir eine Growth Strategie für mein Business."),
        ("🎯 Content", "Gib mir virale Content Ideen."),
        ("💸 Kunden", "Wie bekomme ich mehr Kunden online?"),
        ("⚡ Workflow", "Baue mir einen AI Workflow."),
        ("📈 Analyse", "Analysiere mein Business."),
        ("🔥 Hooks", "Gib mir virale Hooks."),
    ]
    st.markdown('<div class="mb-quick-grid">', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    clicked = None
    for i, (label, prompt) in enumerate(prompts):
        with cols[i % 3]:
            if st.button(label, key=f"{key_prefix}_quick_{i}", width="stretch"):
                clicked = prompt
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked


def ma_chat_input(placeholder: str = "Frag MaByte...") -> str | None:
    return st.chat_input(placeholder)


def prompt_text_area(
    *,
    placeholder: str = "Frag MaByte...",
    key: str,
    height: int = 120,
    label: str = "",
) -> str:
    st.markdown('<span class="mb-prompt-marker"></span>', unsafe_allow_html=True)
    return st.text_area(
        label,
        placeholder=placeholder,
        key=key,
        height=height,
        label_visibility="collapsed",
    )


def prompt_text_input(
    *,
    placeholder: str = "Frag MaByte...",
    key: str,
    label: str = "",
) -> str:
    st.markdown('<span class="mb-prompt-marker"></span>', unsafe_allow_html=True)
    return st.text_input(
        label,
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
    )


def prompt_submit_button(label: str = "Senden", *, key: str) -> bool:
    st.markdown('<div class="mb-prompt-submit">', unsafe_allow_html=True)
    clicked = st.button(label, key=key, width="stretch", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked
