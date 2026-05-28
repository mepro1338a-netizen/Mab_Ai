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
:root {{
    --mb-radius-sm: 12px;
    --mb-radius-md: 16px;
    --mb-radius-lg: 22px;
    --mb-glass: rgba(12, 18, 38, .62);
    --mb-glass-2: rgba(8, 10, 22, .76);
    --mb-line-strong: rgba(255,255,255,.10);
}}

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
    display:block !important;
    visibility:visible !important;
    position:fixed;
    top:0;
    left:0;
    right:0;
    height:76px;
    min-height:76px;
    z-index:999999;
    background:linear-gradient(90deg,rgba(9,8,24,.97),rgba(25,8,42,.97));
    border-bottom:1px solid rgba(255,255,255,.08);
    backdrop-filter:blur(18px);
    box-shadow:0 4px 24px rgba(0,0,0,.25);
}}

{slogan_css}

h1,h2,h3,h4,h5,h6 {{
    color:var(--mb-gold)!important;
    font-weight:1000!important;
}}

/* Typography scale */
body, p, div, span, input, textarea {{
    font-feature-settings: "ss01" 1, "ss02" 1;
    letter-spacing: -0.01em;
}}

label,
.stMarkdown,
.stText,
.stCaption {{
    color:var(--mb-soft)!important;
}}

/* Panel glass — reduces "Streamlit box" look */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:
        radial-gradient(circle at 20% 0%, rgba(168,85,247,.10), transparent 36%),
        radial-gradient(circle at 100% 100%, rgba(96,165,250,.07), transparent 40%),
        linear-gradient(180deg,var(--mb-glass),var(--mb-glass-2))!important;
    border:1px solid rgba(255,255,255,.08)!important;
    border-radius:var(--mb-radius-lg)!important;
    box-shadow:0 18px 70px rgba(0,0,0,.35), 0 0 50px rgba(168,85,247,.06)!important;
    backdrop-filter:blur(18px);
}}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {{
    background:rgba(8,10,22,.65)!important;
    color:#f8fafc!important;
    border:1px solid rgba(255,255,255,.10)!important;
    border-radius:var(--mb-radius-md)!important;
    min-height:44px!important;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.04), 0 0 0 1px rgba(168,85,247,.06)!important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color:var(--mb-muted)!important;
}}

/* Baseweb wrappers (prevents white textarea/select backgrounds) */
div[data-baseweb="textarea"],
div[data-baseweb="input"] {{
    background:rgba(8,10,22,.55)!important;
    border:1px solid rgba(255,255,255,.10)!important;
    border-radius:var(--mb-radius-md)!important;
}}
/* Force textarea wrapper to stay dark (Streamlit sometimes injects white) */
div[data-testid="stTextArea"] div[data-baseweb="textarea"] {{
    background:rgba(8,10,22,.55)!important;
}}
div[data-testid="stTextArea"] textarea {{
    background:transparent!important;
    background-color:transparent!important;
    color:#f8fafc!important;
    -webkit-text-fill-color:#f8fafc!important;
}}
div[data-testid="stTextArea"] div[data-baseweb="textarea"] > div,
div[data-testid="stTextArea"] [data-baseweb="textarea"] {{
    background-color:rgba(8,10,22,.55)!important;
}}
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within,
.stTextInput input:focus,
.stTextArea textarea:focus {{
    border-color:rgba(168,85,247,.38)!important;
    box-shadow:0 0 0 1px rgba(168,85,247,.22), 0 0 28px rgba(124,58,237,.14)!important;
}}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background:rgba(8,10,22,.65)!important;
    color:#f8fafc!important;
    border:1px solid rgba(255,255,255,.10)!important;
    border-radius:var(--mb-radius-md)!important;
    min-height:44px!important;
}}

/* Buttons — remove gray Streamlit feel */
div.stButton > button,
button[kind],
button[data-testid^="stBaseButton"] {{
    border-radius:var(--mb-radius-md)!important;
    border:1px solid rgba(255,255,255,.10)!important;
    background:rgba(10,12,24,.55)!important;
    color:#f8fafc!important;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.04), 0 10px 30px rgba(0,0,0,.22)!important;
    transition:transform .14s ease, box-shadow .14s ease, border-color .14s ease, background .14s ease;
}}
div.stButton > button:hover,
button[kind]:hover {{
    transform:translateY(-1px);
    border-color:rgba(168,85,247,.22)!important;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.05), 0 14px 44px rgba(0,0,0,.28), 0 0 26px rgba(124,58,237,.12)!important;
}}
button[kind="primary"],
button[data-testid="stBaseButton-primary"] {{
    background:linear-gradient(135deg, rgba(124,58,237,.95), rgba(168,85,247,.86))!important;
    border-color:rgba(255,255,255,.18)!important;
    box-shadow:0 18px 55px rgba(124,58,237,.18), 0 0 38px rgba(168,85,247,.16)!important;
}}

div[data-testid="stAlert"] {{
    background:linear-gradient(135deg,rgba(80,20,120,.28),rgba(30,64,175,.22))!important;
    border:1px solid rgba(255,255,255,.08)!important;
    border-radius:16px!important;
}}

/* =========================
   Radio (Format switch) as premium segmented control
   ========================= */
div[data-testid="stRadio"] > label {{
    display:none!important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] {{
    display:inline-flex !important;
    gap: 8px !important;
    padding: 6px !important;
    border-radius: var(--mb-radius-lg) !important;
    background: rgba(10,12,24,.45) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    backdrop-filter: blur(14px);
}}
div[data-testid="stRadio"] div[role="radiogroup"] label {{
    margin: 0 !important;
    padding: 8px 14px !important;
    border-radius: var(--mb-radius-md) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    background: rgba(10,12,24,.28) !important;
    transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease, background .14s ease;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover {{
    transform: translateY(-1px);
    border-color: rgba(168,85,247,.18) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,.22), 0 0 24px rgba(124,58,237,.10) !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label input {{
    display:none!important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label p {{
    margin: 0 !important;
    color: rgba(226,232,240,.92) !important;
    font-weight: 900 !important;
    letter-spacing: -0.01em;
}}
/* selected (uses :has where supported; safe fallback keeps default) */
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
    background: linear-gradient(135deg, rgba(124,58,237,.40), rgba(59,130,246,.18)) !important;
    border-color: rgba(168,85,247,.35) !important;
    box-shadow: 0 14px 44px rgba(0,0,0,.26), 0 0 30px rgba(124,58,237,.14) !important;
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