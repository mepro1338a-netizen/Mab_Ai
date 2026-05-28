"""MaByte global premium design system — single injection point."""
from __future__ import annotations

from ui.styles import inject_css, page_layout_css


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
        padding-top: 72px !important;
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


def inject_design_system(max_width: int = 1480, padding_top: int = 92) -> None:
    """Page-specific layout override — global shell via ui.app_shell.inject_global_ui()."""
    inject_css(page_layout_css(max_width, padding_top, 42) + GLOBAL_DESIGN_CSS)
