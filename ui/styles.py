"""Central MaByte UI CSS helpers, B2B theme tokens, and Streamlit overrides."""
from __future__ import annotations

import streamlit as st

# Scope page-specific button CSS here so the sidebar stays identical on every route.
MAIN_CONTENT_SCOPE = "section.main"

MB_THEME_VARS = """
:root {
    --mb-zinc-950: #09090b;
    --mb-zinc-900: #18181b;
    --mb-zinc-800: #27272a;
    --mb-zinc-700: #3f3f46;
    --mb-zinc-600: #52525b;
    --mb-zinc-500: #71717a;
    --mb-zinc-400: #a1a1aa;
    --mb-zinc-300: #d4d4d8;
    --mb-bg: var(--mb-zinc-950);
    --mb-surface: var(--mb-zinc-900);
    --mb-surface-2: var(--mb-zinc-800);
    --mb-border: rgba(63, 63, 70, .9);
    --mb-line: rgba(255, 255, 255, .08);
    --mb-gold: #fafafa;
    --mb-soft: #e4e4e7;
    --mb-muted: #a1a1aa;
    --mb-purple: #a78bfa;
    --mb-violet: #7c3aed;
    --mb-blue: #60a5fa;
    --mb-accent: #7c3aed;
    --mb-auth-line: rgba(124, 58, 237, .22);
    --mb-surface-card: rgba(24, 24, 27, .96);
    --mb-content-max: 1100px;
    --mb-content-pad-x: 1.5rem;
    --mb-gap-section: 20px;
    --mb-gap-card: 12px;
    --mb-label-size: 10px;
    --mb-label-weight: 700;
    --mb-label-spacing: 0.12em;
    --mb-label-color: #a78bfa;
}
"""

MB_APP_BACKGROUND = "linear-gradient(180deg, #09090b 0%, #18181b 42%, #09090b 100%)"

AUTH_EXTRA_VARS = """
:root {
    --mb-auth-surface: rgba(24, 24, 27, .98);
}
"""

STREAMLIT_THEME_VARS = """
.stApp,
.stApp[data-theme="light"],
.stApp[data-theme="dark"] {
    --background-color: #09090b !important;
    --secondary-background-color: #18181b !important;
    --text-color: #fafafa !important;
    --primary-color: #7c3aed !important;
    --border-color: #3f3f46 !important;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] .stApp {
    --background-color: #09090b !important;
    --secondary-background-color: #18181b !important;
    --text-color: #e4e4e7 !important;
}
"""


def inject_css(css: str) -> None:
    st.markdown(f"<style>{css.strip()}</style>", unsafe_allow_html=True)


def page_layout_css(
    max_width: int,
    padding_top: int,
    padding_bottom: int = 42,
    selector: str = ".main .block-container",
) -> str:
    return f"""
{selector} {{
    max-width: {max_width}px !important;
    padding-top: {padding_top}px !important;
    padding-bottom: {padding_bottom}px !important;
}}
"""


def layout_system_css() -> str:
    """Shared content grid — aligns topbar, main pages, and dashboard."""
    return """
section.main .block-container,
.main .block-container {
    max-width: var(--mb-content-max) !important;
    padding-left: var(--mb-content-pad-x) !important;
    padding-right: var(--mb-content-pad-x) !important;
    padding-top: 20px !important;
    padding-bottom: 42px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
.stApp:has(.mb-dash) section.main .block-container,
.stApp:has(.mb-home) section.main .block-container {
    padding-top: 20px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
.stApp:has(.mb-dash) section.main .block-container {
    padding-bottom: 48px !important;
}
@media (max-width: 768px) {
    section.main .block-container,
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}
"""


def gradient_title_css(class_name: str = "mb-title") -> str:
    return f"""
.{class_name} {{
    text-align: center;
    font-size: 56px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -3px;
    margin-top: 10px;
    background: linear-gradient(135deg, #fafafa, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
"""


def streamlit_force_dark_css() -> str:
    """Kill light Streamlit defaults (sidebar, main, widgets, deploy)."""
    return (
        STREAMLIT_THEME_VARS
        + """
html, body {
    color-scheme: dark !important;
    background-color: #09090b !important;
}

.stApp,
.stApp > header,
.stApp[data-theme="light"],
.stApp[data-theme="dark"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stAppViewContainer"] > section > div,
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
section.main,
section.main > div,
section.main .block-container,
.main,
.main .block-container {
    background: """
        + MB_APP_BACKGROUND
        + """ !important;
    background-color: #09090b !important;
    color: #e4e4e7 !important;
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    background: """
        + MB_APP_BACKGROUND
        + """ !important;
    background-color: #09090b !important;
    color: #e4e4e7 !important;
}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

button[data-testid="collapsedControl"],
button[kind="header"] {
    color: #a1a1aa !important;
    background: #27272a !important;
    border: 1px solid rgba(255, 255, 255, .08) !important;
    border-radius: 8px !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.stCheckbox label,
.stCheckbox label span,
.stCheckbox label p,
.stToggle label,
.stToggle label span,
.stRadio label p,
label[data-testid="stWidgetLabel"] p,
.stCaption,
[data-testid="stWidgetLabel"] p,
section.main .stMarkdown p,
section.main .stMarkdown span {
    color: #d4d4d8 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background-color: #27272a !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    border-color: #3f3f46 !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #18181b !important;
    border-color: #3f3f46 !important;
}

#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stDeployButton"],
a[data-testid="stDeployButton"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

iframe[title="streamlit_app"] {
    background: #09090b !important;
}

.mb-error-panel {
    padding: 20px 22px;
    border-radius: 14px;
    background: #18181b;
    border: 1px solid #3f3f46;
    margin-bottom: 12px;
}
.mb-error-panel h3 {
    color: #fafafa !important;
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 8px 0;
}
.mb-error-panel p {
    color: #a1a1aa !important;
    font-size: 14px;
    line-height: 1.5;
    margin: 0;
}
"""
    )


def inject_theme_lock() -> None:
    """Final override — must run every script execution, after page widgets."""
    st.markdown(
        f"<style>{streamlit_force_dark_css().strip()}</style>",
        unsafe_allow_html=True,
    )
