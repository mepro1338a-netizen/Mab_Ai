"""Global CSS injection — runs every Streamlit script execution."""
from __future__ import annotations

import streamlit as st

_UI_VERSION = 8


GLOBAL_DESIGN_CSS = """
/* ---- Layout & overflow ---- */
html, body, .stApp {
    overflow-x: hidden !important;
}
.main .block-container {
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 80px !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }
    .custom-topbar { height: 64px !important; }
    h1 { font-size: 1.65rem !important; }
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .mb-page-hero, .dash-hero, .mb-hero {
        padding: 20px 18px !important;
        border-radius: 22px !important;
    }
    .mb-hero-title, .dash-title { font-size: 28px !important; }
    .dash-stat-grid, .fb-odds-grid, .mb-feature-grid {
        grid-template-columns: 1fr !important;
    }
}

/* ---- Scrollbars ---- */
* {
    scrollbar-width: thin;
    scrollbar-color: #52525b #18181b;
}
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-thumb {
    background: #52525b;
    border-radius: 8px;
}
*::-webkit-scrollbar-track { background: #18181b; }

/* ---- Forms ---- */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: #27272a !important;
    color: #fafafa !important;
    border-radius: 12px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(168,85,247,.55) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,.2) !important;
}

/* ---- DataFrames / tables ---- */
.stDataFrame, [data-testid="stDataFrame"] {
    border-radius: 16px !important;
    border: 1px solid var(--mb-line) !important;
    overflow: hidden !important;
}
.stDataFrame [data-testid="stTable"] {
    background: rgba(12,16,32,.85) !important;
}

/* ---- Tabs ---- */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    color: var(--mb-muted) !important;
    font-weight: 800 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--mb-gold) !important;
    border-color: rgba(168,85,247,.5) !important;
}

/* ---- Skeleton / loading ---- */
.mb-skeleton {
    border-radius: 14px;
    height: 14px;
    margin: 8px 0;
    background: linear-gradient(90deg, rgba(30,27,50,.6), rgba(50,40,80,.4), rgba(30,27,50,.6));
    background-size: 200% 100%;
    animation: mb-shimmer 1.4s ease infinite;
}
@keyframes mb-shimmer {
    0% { background-position: 100% 0; }
    100% { background-position: -100% 0; }
}

/* ---- Locked / upgrade surfaces ---- */
.mb-locked-panel {
    border-radius: 24px;
    padding: 28px 26px;
    background:
        radial-gradient(circle at 100% 0%, rgba(168,85,247,.12), transparent 40%),
        linear-gradient(160deg, rgba(14,12,28,.98), rgba(8,8,18,.99));
    border: 1px dashed rgba(255,231,163,.22);
    text-align: center;
}
.mb-locked-panel h4 {
    color: var(--mb-gold) !important;
    font-size: 18px;
    font-weight: 1000;
    margin: 0 0 8px 0;
}
.mb-locked-panel p {
    color: var(--mb-muted) !important;
    font-size: 13px;
    line-height: 1.55;
}

/* ---- OS Helper ---- */
.os-helper-wrap {
    border-radius: 20px;
    padding: 14px 14px 10px 14px;
    margin-top: 12px;
    margin-bottom: 8px;
    background: linear-gradient(160deg, rgba(20,12,38,.96), rgba(8,8,18,.98));
    border: 1px solid rgba(168,85,247,.22);
    box-shadow: 0 12px 32px rgba(0,0,0,.2);
}
.os-helper-title {
    color: #c084fc !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .18em;
    text-transform: uppercase;
}
.os-helper-name {
    color: var(--mb-gold) !important;
    font-size: 15px;
    font-weight: 1000;
    margin-top: 6px;
}
.os-helper-msg {
    color: #cbd5e1 !important;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 10px;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(255,255,255,.06);
}
.os-helper-chip {
    display: inline-block;
    margin: 4px 4px 0 0;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
    color: #e9d5ff !important;
    background: rgba(76,29,149,.35);
    border: 1px solid rgba(168,85,247,.25);
}

/* ---- Error boundary ---- */
.mb-error-panel {
    border-radius: 24px;
    padding: 28px 26px;
    border: 1px solid rgba(239,68,68,.35);
    background: linear-gradient(160deg, rgba(40,10,20,.9), rgba(12,8,18,.98));
}
.mb-error-panel h3 { color: #fca5a5 !important; margin: 0 0 10px 0; }
.mb-error-panel p { color: #94a3b8 !important; font-size: 14px; line-height: 1.55; }
"""


_BTN = (
    "button, [data-testid='stBaseButton-primary'], "
    "[data-testid='stBaseButton-secondary'], [data-testid='stBaseButton-tertiary']"
)
_BTN_P = (
    "button p, [data-testid='stBaseButton-primary'] p, "
    "[data-testid='stBaseButton-secondary'] p, [data-testid='stBaseButton-tertiary'] p"
)
_GRAY_BG = "linear-gradient(135deg, rgba(52,52,56,.98) 0%, rgba(36,36,40,.99) 52%, rgba(26,26,30,.99) 100%)"
_GRAY_BG_HOVER = "linear-gradient(135deg, rgba(68,68,72,.98) 0%, rgba(48,48,52,.99) 52%, rgba(34,34,38,.99) 100%)"
_GRAY_BG_ACTIVE = "linear-gradient(135deg, rgba(82,82,88,.98) 0%, rgba(58,58,62,.99) 52%, rgba(42,42,46,.99) 100%)"
_GRAY_COLOR = "#ffffff"
_GRAY_BORDER = "rgba(255,255,255,.1)"
_GRAY_BORDER_HOVER = "rgba(255,255,255,.2)"
_GRAY_GLOW = "0 8px 20px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.06)"
_GRAY_GLOW_HOVER = "0 0 18px rgba(255,255,255,.08), 0 10px 24px rgba(0,0,0,.22)"


MAIN_BUTTON_CSS = f"""
/* Main — grau */
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton > button,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton {_BTN},
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main {_BTN} {{
    border-radius: 15px !important;
    font-weight: 700 !important;
    min-height: 46px !important;
    border: 1px solid {_GRAY_BORDER} !important;
    background: {_GRAY_BG} !important;
    background-color: rgba(32,32,36,.99) !important;
    color: {_GRAY_COLOR} !important;
    box-shadow: {_GRAY_GLOW} !important;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease !important;
}}
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton > button p,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton {_BTN_P},
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main {_BTN_P} {{
    color: {_GRAY_COLOR} !important;
    font-weight: 700 !important;
}}
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton > button[kind="secondary"],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton > button[kind="primary"],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main button[data-testid="stBaseButton-secondary"],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main button[data-testid="stBaseButton-primary"],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main [data-testid="stBaseButton-secondary"],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main [data-testid="stBaseButton-primary"],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .mb-btn-gold .stButton > button,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .mb-btn-gold {_BTN} {{
    background: {_GRAY_BG} !important;
    background-color: rgba(32,32,36,.99) !important;
    color: {_GRAY_COLOR} !important;
    border: 1px solid {_GRAY_BORDER} !important;
    box-shadow: {_GRAY_GLOW} !important;
}}
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton > button:hover,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton {_BTN}:hover,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main button[data-testid="stBaseButton-secondary"]:hover,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main button[data-testid="stBaseButton-primary"]:hover,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .mb-btn-gold {_BTN}:hover {{
    transform: translateY(-1px) !important;
    color: {_GRAY_COLOR} !important;
    border-color: {_GRAY_BORDER_HOVER} !important;
    background: {_GRAY_BG_HOVER} !important;
    background-color: rgba(44,44,48,.99) !important;
    box-shadow: {_GRAY_GLOW_HOVER} !important;
}}
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main .stButton > button:disabled,
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main button[disabled],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main [data-testid="stBaseButton-secondary"][disabled],
.stApp:not(:has(.mb-dash)):not(:has(.img-studio)):not(:has(.mb-workspace)) section.main [data-testid="stBaseButton-primary"][disabled] {{
    opacity: .45 !important;
    background: linear-gradient(135deg, rgba(38,38,42,.9), rgba(28,28,32,.95)) !important;
    background-color: rgba(32,32,36,.95) !important;
    color: rgba(255,255,255,.55) !important;
    border-color: rgba(255,255,255,.08) !important;
    box-shadow: none !important;
    transform: none !important;
}}

/* Tabs */
div[data-testid="stTabs"] button[data-baseweb="tab"] {{
    color: #94a3b8 !important;
    font-weight: 700 !important;
    background: transparent !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {_GRAY_COLOR} !important;
    border-color: {_GRAY_BORDER_HOVER} !important;
    background: rgba(52,52,56,.45) !important;
}}
"""


def master_button_css() -> str:
    return MAIN_BUTTON_CSS


def inject_global_ui(*, force: bool = False) -> None:
    """Inject on every run — Streamlit rebuilds the page each rerun."""
    from ui.styles import MB_THEME_VARS, streamlit_force_dark_css
    from ui.premium_foundation import BETA_GLOBAL_CSS
    from ui.prompt_ui import MABYTE_PROMPT_CSS
    from ui.sidebar import sidebar_master_css
    from ui.styles import inject_css, page_layout_css
    from ui_core import core_app_css

    _page = str(st.session_state.get("page") or "home").strip()
    if _page in ("reels", "video"):
        _page = "creator"

    inject_css(
        f"/* mb-ui-v{_UI_VERSION} */\n"
        + MB_THEME_VARS
        + streamlit_force_dark_css()
        + BETA_GLOBAL_CSS
        + page_layout_css(1480, 100, 42)
        + GLOBAL_DESIGN_CSS
        + core_app_css()
        + master_button_css()
        + sidebar_master_css(_page)
        + MABYTE_PROMPT_CSS
    )
    st.markdown('<div class="custom-topbar"></div>', unsafe_allow_html=True)
    st.session_state["_mb_ui_version"] = _UI_VERSION
