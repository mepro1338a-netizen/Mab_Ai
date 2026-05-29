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
    background: rgba(10, 12, 24, .85) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(168, 85, 247, .28) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, .2), inset 0 1px 0 rgba(255, 255, 255, .04) !important;
}
.stApp:has(.mb-dash) [data-testid="stChatInput"] > div,
.stApp:has(.mb-dash) [data-testid="stChatInput"] div[data-baseweb="textarea"] {
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, .18) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: transparent !important;
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    box-shadow: none !important;
    outline: none !important;
    min-height: 24px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(148, 163, 184, .85) !important;
    font-weight: 500 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, .1) !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, .25) !important;
}

/* Legacy prompt marker — prefer labeled st.text_input in workspaces */
.mb-prompt-marker { display: none; }

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
        '<div class="mb-os-ready">✦ MaByte Chat ist bereit. Wähle einen Vorschlag oder schreib deine Frage.</div>',
        unsafe_allow_html=True,
    )


CHAT_QUICKSTARTS = [
    ("Zusammenfassen", "Fasse diesen Text in 5 klaren Bulletpoints zusammen."),
    ("Code erklären", "Erkläre diesen Code Schritt für Schritt und nenne Verbesserungen."),
    ("E-Mail", "Formuliere eine professionelle E-Mail zu folgendem Anlass:"),
    ("Brainstorm", "Gib mir 10 konkrete Ideen zu folgendem Thema:"),
    ("Übersetzen", "Übersetze den folgenden Text ins Deutsche (natürlich, professionell):"),
    ("Struktur", "Erstelle eine klare Gliederung für folgendes Dokument:"),
]


def render_chat_quickstarts(key_prefix: str = "chat_qs") -> str | None:
    return render_quickstart_grid(key_prefix=key_prefix, prompts=CHAT_QUICKSTARTS)


def render_quickstart_grid(
    key_prefix: str = "qs",
    *,
    prompts: list[tuple[str, str]] | None = None,
) -> str | None:
    st.markdown('<div class="mb-quick-label">Vorschläge</div>', unsafe_allow_html=True)
    items = prompts or CHAT_QUICKSTARTS
    st.markdown('<div class="mb-quick-grid">', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    clicked = None
    for i, (label, prompt) in enumerate(items):
        with cols[i % 3]:
            if st.button(label, key=f"{key_prefix}_quick_{i}", width="stretch"):
                clicked = prompt
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked


def ma_chat_input(placeholder: str = "Nachricht eingeben…") -> str | None:
    return st.chat_input(placeholder)


def prompt_text_area(
    *,
    placeholder: str = "",
    key: str,
    height: int = 120,
    label: str = "Beschreibung",
) -> str:
    return st.text_area(
        label,
        placeholder=placeholder,
        key=key,
        height=height,
    )


def prompt_text_input(
    *,
    placeholder: str = "",
    key: str,
    label: str = "Eingabe",
) -> str:
    return st.text_input(
        label,
        placeholder=placeholder,
        key=key,
    )


def prompt_submit_button(label: str = "Senden", *, key: str) -> bool:
    st.markdown('<div class="mb-prompt-submit">', unsafe_allow_html=True)
    clicked = st.button(label, key=key, width="stretch", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked
