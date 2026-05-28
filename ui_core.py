import base64
from pathlib import Path

import streamlit as st

from ui.app_shell import inject_global_ui


ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


def img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def core_app_css() -> str:
    slogan = img_base64(SLOGAN_HEADER)
    slogan_css = ""
    if slogan:
        slogan_css = f"""
.custom-topbar {{
    background-image: url("data:image/png;base64,{slogan}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
"""
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

.custom-topbar {{
    display: block !important;
    visibility: visible !important;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 76px;
    min-height: 76px;
    z-index: 999999;
    background: linear-gradient(90deg, rgba(9,8,24,.97), rgba(25,8,42,.97));
    border-bottom: 1px solid rgba(255,255,255,.08);
    backdrop-filter: blur(18px);
    box-shadow: 0 4px 24px rgba(0,0,0,.25);
}}
{slogan_css}

h1, h2, h3, h4, h5, h6 {{
    color: var(--mb-gold) !important;
    font-weight: 800 !important;
}}

label, .stMarkdown, .stText, .stCaption {{
    color: var(--mb-soft) !important;
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
    background: rgba(8,10,22,.7) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: var(--mb-radius-md) !important;
    min-height: 42px !important;
}}

div[data-baseweb="textarea"], div[data-baseweb="input"] {{
    background: rgba(8,10,22,.55) !important;
    border: 1px solid rgba(255,255,255,.10) !important;
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

@media (max-width: 900px) {{
    .custom-topbar {{ height: 64px !important; min-height: 64px !important; }}
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
