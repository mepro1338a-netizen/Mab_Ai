import base64
import html
from pathlib import Path

import streamlit as st

from ui.styles import MB_THEME_VARS, inject_css
from ui.premium_foundation import inject_beta_global_css
from ui.design_system import inject_design_system


ASSET_DIR = Path("assets")
WORDMARK = ASSET_DIR / "wordmark.png"
SLOGAN_HEADER = ASSET_DIR / "sloganheader.png"


def img_base64(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def load_css() -> None:
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

    inject_beta_global_css()
    inject_design_system(1480, 88)
    inject_css(f"""
{MB_THEME_VARS}

#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
button[title="View fullscreen"],
button[title="Fullscreen"],
[data-testid="StyledFullScreenButton"] {{
    display:none!important;
}}

[data-testid="stHeader"] {{
    background:transparent!important;
}}

html,
body,
.stApp,
.main,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 24%),
        radial-gradient(circle at top right, rgba(96,165,250,.10), transparent 26%),
        linear-gradient(180deg,#050816 0%,#081226 48%,#050711 100%)!important;
    background-attachment:fixed!important;
}}

.main .block-container {{
    max-width:1480px!important;
    padding-top:88px!important;
    padding-bottom:42px!important;
}}

.custom-topbar {{
    position:fixed;
    top:0;
    left:0;
    right:0;
    height:76px;
    z-index:999999;
    background:linear-gradient(90deg,rgba(9,8,24,.96),rgba(25,8,42,.96));
    border-bottom:1px solid rgba(255,255,255,.07);
    backdrop-filter:blur(18px);
}}

{slogan_css}

h1,h2,h3,h4,h5,h6 {{
    color:var(--mb-gold)!important;
    font-weight:1000!important;
}}

label,
.stMarkdown,
.stText,
.stCaption {{
    color:var(--mb-soft)!important;
}}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {{
    background:rgba(15,23,42,.92)!important;
    color:var(--mb-gold)!important;
    border:1px solid rgba(96,165,250,.24)!important;
    border-radius:15px!important;
    min-height:44px!important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color:var(--mb-muted)!important;
}}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background:rgba(15,23,42,.92)!important;
    color:var(--mb-gold)!important;
    border:1px solid rgba(96,165,250,.24)!important;
    border-radius:15px!important;
    min-height:44px!important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 32%),
        linear-gradient(180deg,rgba(12,18,38,.90),rgba(8,12,26,.98))!important;
    border:1px solid var(--mb-line)!important;
    border-radius:24px!important;
    box-shadow:0 0 36px rgba(0,140,255,.075)!important;
}}

div[data-testid="stAlert"] {{
    background:linear-gradient(135deg,rgba(80,20,120,.28),rgba(30,64,175,.22))!important;
    border:1px solid rgba(255,255,255,.08)!important;
    border-radius:16px!important;
}}

[data-testid="metric-container"] {{
    background:linear-gradient(180deg,rgba(18,10,32,.96),rgba(10,8,20,.96))!important;
    border-radius:22px!important;
    border:1px solid var(--mb-line)!important;
    padding:18px!important;
}}

::-webkit-scrollbar {{
    width:10px;
}}

::-webkit-scrollbar-thumb {{
    background:#a855f7;
    border-radius:20px;
}}

::-webkit-scrollbar-track {{
    background:#12051d;
}}

@media(max-width:900px) {{
    .main .block-container {{
        padding-top:76px!important;
        padding-left:1rem!important;
        padding-right:1rem!important;
    }}

    .custom-topbar {{
        height:64px;
    }}
}}

""")

    from ui.sidebar import inject_sidebar_styles
    inject_sidebar_styles()

    st.markdown('<div class="custom-topbar"></div>', unsafe_allow_html=True)


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


def render_sidebar(active_page: str | None = None) -> None:
    """Re-export — implementation in ui.sidebar (single source for all pages)."""
    from ui.sidebar import render_sidebar as _render
    _render(active_page)