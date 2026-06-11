import base64
from pathlib import Path

import streamlit as st

from ui.app_shell import inject_global_ui
from ui.styles import MB_APP_BACKGROUND


ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


def img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def core_app_css() -> str:
    return f"""
:root {{
    --mb-radius-sm: 12px;
    --mb-radius-md: 16px;
    --mb-radius-lg: 18px;
    --mb-line: rgba(255,255,255,.09);
}}

#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
button[title="View fullscreen"],
button[title="Fullscreen"],
[data-testid="StyledFullScreenButton"] {{
    display: none !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

html, body, .stApp, .main,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 24%),
        radial-gradient(circle at top right, rgba(96,165,250,.08), transparent 26%),
        linear-gradient(180deg, #050816 0%, #081226 48%, #050711 100%) !important;
    background-attachment: fixed !important;
}}

h1, h2, h3, h4, h5, h6 {{
    color: #fafafa !important;
    font-weight: 800 !important;
}}

label, .stMarkdown, .stText, .stCaption {{
    color: #e4e4e7 !important;
}}

/* Flat panels — no default Streamlit card chrome */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    padding: 0 !important;
}}

.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stDateInput input, .stTimeInput input {{
    background: #27272a !important;
    color: #fafafa !important;
    border: 1px solid #3f3f46 !important;
    border-radius: var(--mb-radius-md) !important;
    min-height: 42px !important;
}}

div[data-baseweb="textarea"], div[data-baseweb="input"] {{
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: var(--mb-radius-md) !important;
}}

div[data-testid="stTextArea"] textarea {{
    background: transparent !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
}}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background: rgba(8,10,22,.7) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: var(--mb-radius-md) !important;
    min-height: 42px !important;
}}

div[data-testid="stAlert"] {{
    background: rgba(30,20,50,.85) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 14px !important;
}}

div[data-testid="stRadio"] > label {{ display: none !important; }}
div[data-testid="stRadio"] div[role="radiogroup"] {{
    display: inline-flex !important;
    gap: 6px !important;
    padding: 4px !important;
    border-radius: var(--mb-radius-lg) !important;
    background: rgba(10,12,24,.45) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label {{
    margin: 0 !important;
    padding: 8px 12px !important;
    border-radius: var(--mb-radius-md) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    background: rgba(10,12,24,.28) !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label input {{ display: none !important; }}
div[data-testid="stRadio"] div[role="radiogroup"] label p {{
    margin: 0 !important;
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
    background: rgba(124,58,237,.35) !important;
    border-color: rgba(168,85,247,.35) !important;
}}

[data-testid="metric-container"] {{
    background: rgba(10,12,24,.5) !important;
    border-radius: 14px !important;
    border: 1px solid var(--mb-line) !important;
    padding: 14px !important;
}}

section.main [data-testid="stExpander"] {{
    background: rgba(10, 14, 28, 0.92) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}}
section.main [data-testid="stExpander"] summary {{
    background: rgba(15, 23, 42, 0.85) !important;
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}}
section.main [data-testid="stExpander"] summary:hover {{
    background: rgba(30, 41, 59, 0.9) !important;
    color: #f8fafc !important;
}}
section.main [data-testid="stExpander"] summary svg {{
    fill: #94a3b8 !important;
}}
section.main [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
    background: rgba(8, 12, 24, 0.95) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
}}

section.main [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: var(--mb-radius-md) !important;
}}
section.main [data-testid="stNumberInput"] button {{
    background: #27272a !important;
    border-color: #3f3f46 !important;
    color: #e2e8f0 !important;
}}

section.main .stButton > button,
section.main button[data-testid="stBaseButton-secondary"],
section.main button[data-testid="stBaseButton-tertiary"] {{
    background-color: rgba(39, 39, 42, 0.98) !important;
    color: #fafafa !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
}}
section.main .stButton > button p,
section.main .stButton > button span {{
    color: #fafafa !important;
}}

section.main [data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background: rgba(10, 12, 24, 0.6) !important;
    border-radius: 12px !important;
    gap: 4px !important;
    padding: 4px !important;
}}
section.main [data-testid="stTabs"] button {{
    background: transparent !important;
    color: #94a3b8 !important;
}}
section.main [data-testid="stTabs"] button[aria-selected="true"] {{
    background: rgba(124, 58, 237, 0.25) !important;
    color: #f8fafc !important;
}}

"""


def load_css() -> None:
    inject_global_ui()


def require_login() -> None:
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.session_state.page = "auth"
        st.stop()


def sync_session_user(user: dict | None) -> None:
    from services.session_auth import sync_from_user_record
    sync_from_user_record(user)


def is_admin_user() -> bool:
    from services.session_auth import server_is_admin
    return server_is_admin()
