"""B2B zinc/anthracite theme — single source for MaByte surfaces + Streamlit overrides."""
from __future__ import annotations

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
}
"""

MB_APP_BACKGROUND = """
    linear-gradient(180deg, #09090b 0%, #18181b 42%, #09090b 100%)
"""

AUTH_EXTRA_VARS = """
:root {
    --mb-auth-surface: rgba(24, 24, 27, .98);
}
"""


def streamlit_force_dark_css() -> str:
    """Kill light Streamlit defaults (sidebar, main, widgets, deploy)."""
    return """
html, body {
    color-scheme: dark !important;
    background-color: #09090b !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section.main,
section.main > div,
.main,
.main .block-container {
    background: linear-gradient(180deg, #09090b 0%, #18181b 42%, #09090b 100%) !important;
    background-color: #09090b !important;
    color: #e4e4e7 !important;
}

/* Sidebar — always anthracite */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: #18181b !important;
    background-color: #18181b !important;
    color: #e4e4e7 !important;
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

/* Widgets on zinc */
.stCheckbox label,
.stCheckbox label span,
.stCheckbox label p,
.stToggle label,
.stToggle label span,
.stRadio label p,
label[data-testid="stWidgetLabel"] p,
.stCaption,
[data-testid="stWidgetLabel"] p {
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

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(24, 24, 27, .55) !important;
    border-color: rgba(63, 63, 70, .75) !important;
}

/* Streamlit chrome */
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
"""
