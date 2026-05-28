"""
MaByte global button styles — einheitlich grau mit weißer Schrift.
"""
from __future__ import annotations

from ui.styles import inject_css

_BTN = (
    "button, [data-testid='stBaseButton-primary'], "
    "[data-testid='stBaseButton-secondary'], [data-testid='stBaseButton-tertiary']"
)
_BTN_P = (
    "button p, [data-testid='stBaseButton-primary'] p, "
    "[data-testid='stBaseButton-secondary'] p, [data-testid='stBaseButton-tertiary'] p"
)

# Dunkleres Grau + weiße Schrift (alle Buttons)
_GRAY_BG = "linear-gradient(135deg, rgba(52,52,56,.98) 0%, rgba(36,36,40,.99) 52%, rgba(26,26,30,.99) 100%)"
_GRAY_BG_HOVER = "linear-gradient(135deg, rgba(68,68,72,.98) 0%, rgba(48,48,52,.99) 52%, rgba(34,34,38,.99) 100%)"
_GRAY_BG_ACTIVE = "linear-gradient(135deg, rgba(82,82,88,.98) 0%, rgba(58,58,62,.99) 52%, rgba(42,42,46,.99) 100%)"
_GRAY_COLOR = "#ffffff"
_GRAY_BORDER = "rgba(255,255,255,.1)"
_GRAY_BORDER_HOVER = "rgba(255,255,255,.2)"
_GRAY_GLOW = "0 8px 20px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.06)"
_GRAY_GLOW_HOVER = "0 0 18px rgba(255,255,255,.08), 0 10px 24px rgba(0,0,0,.22)"

SIDEBAR_NAV_BUTTON_CSS = f"""
/* Sidebar — grau, weiße Schrift */
section[data-testid="stSidebar"] .mb-nav-item .stButton,
section[data-testid="stSidebar"] .mb-nav-item {_BTN} {{
    width: 100% !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN} {{
    width: 100% !important;
    min-height: 42px !important;
    border-radius: 14px !important;
    border: 1px solid {_GRAY_BORDER} !important;
    background: {_GRAY_BG} !important;
    background-color: rgba(32,32,36,.99) !important;
    color: {_GRAY_COLOR} !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    text-align: left !important;
    padding: 9px 10px 9px 48px !important;
    position: relative !important;
    box-shadow: {_GRAY_GLOW} !important;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN_P} {{
    color: {_GRAY_COLOR} !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}}
section[data-testid="stSidebar"] .mb-nav-item button[kind="primary"],
section[data-testid="stSidebar"] .mb-nav-item button[kind="secondary"],
section[data-testid="stSidebar"] .mb-nav-item [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] .mb-nav-item [data-testid="stBaseButton-secondary"] {{
    background: {_GRAY_BG} !important;
    background-color: rgba(32,32,36,.99) !important;
    color: {_GRAY_COLOR} !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN}:hover {{
    transform: translateY(-1px) !important;
    color: {_GRAY_COLOR} !important;
    border-color: {_GRAY_BORDER_HOVER} !important;
    background: {_GRAY_BG_HOVER} !important;
    background-color: rgba(44,44,48,.99) !important;
    box-shadow: {_GRAY_GLOW_HOVER} !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN}:hover p {{
    color: {_GRAY_COLOR} !important;
}}
section[data-testid="stSidebar"] .mb-nav-active {_BTN} {{
    color: {_GRAY_COLOR} !important;
    border-color: {_GRAY_BORDER_HOVER} !important;
    background: {_GRAY_BG_ACTIVE} !important;
    background-color: rgba(52,52,56,.99) !important;
    box-shadow: {_GRAY_GLOW_HOVER} !important;
}}
section[data-testid="stSidebar"] .mb-nav-active {_BTN_P} {{
    color: {_GRAY_COLOR} !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN} {{
    width: 100% !important;
    min-height: 40px !important;
    padding: 8px 14px !important;
    text-align: center !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, rgba(40,40,44,.95), rgba(28,28,32,.98)) !important;
    background-color: rgba(30,30,34,.98) !important;
    border: 1px solid {_GRAY_BORDER} !important;
    color: {_GRAY_COLOR} !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN_P} {{
    color: {_GRAY_COLOR} !important;
    text-align: center !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN}:hover {{
    color: {_GRAY_COLOR} !important;
    border-color: {_GRAY_BORDER_HOVER} !important;
    background: {_GRAY_BG_HOVER} !important;
}}
"""

MAIN_BUTTON_CSS = f"""
/* Main — grau (nicht im Reels Creator Studio; dort premium_studio_css) */
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton {_BTN},
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main {_BTN} {{
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
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton {_BTN_P},
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main {_BTN_P} {{
    color: {_GRAY_COLOR} !important;
    font-weight: 700 !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button[kind="secondary"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button[kind="primary"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[data-testid="stBaseButton-secondary"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[data-testid="stBaseButton-primary"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stBaseButton-secondary"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stBaseButton-primary"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .mb-btn-gold .stButton > button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .mb-btn-gold {_BTN} {{
    background: {_GRAY_BG} !important;
    background-color: rgba(32,32,36,.99) !important;
    color: {_GRAY_COLOR} !important;
    border: 1px solid {_GRAY_BORDER} !important;
    box-shadow: {_GRAY_GLOW} !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button[kind="secondary"] p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button[kind="primary"] p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[data-testid="stBaseButton-secondary"] p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[data-testid="stBaseButton-primary"] p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .mb-btn-gold {_BTN_P} {{
    color: {_GRAY_COLOR} !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button:hover,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton {_BTN}:hover,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[data-testid="stBaseButton-secondary"]:hover,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[data-testid="stBaseButton-primary"]:hover,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .mb-btn-gold {_BTN}:hover {{
    transform: translateY(-1px) !important;
    color: {_GRAY_COLOR} !important;
    border-color: {_GRAY_BORDER_HOVER} !important;
    background: {_GRAY_BG_HOVER} !important;
    background-color: rgba(44,44,48,.99) !important;
    box-shadow: {_GRAY_GLOW_HOVER} !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button:hover p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .mb-btn-gold {_BTN}:hover p {{
    color: {_GRAY_COLOR} !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button:disabled,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[disabled],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stBaseButton-secondary"][disabled],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stBaseButton-primary"][disabled] {{
    opacity: .45 !important;
    background: linear-gradient(135deg, rgba(38,38,42,.9), rgba(28,28,32,.95)) !important;
    background-color: rgba(32,32,36,.95) !important;
    color: rgba(255,255,255,.55) !important;
    border-color: rgba(255,255,255,.08) !important;
    box-shadow: none !important;
    transform: none !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stButton > button:disabled p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main button[disabled] p {{
    color: rgba(255,255,255,.55) !important;
}}

/* Form submit */
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stFormSubmitButton > button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stFormSubmitButton button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stFormSubmitButton"] > button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stFormSubmitButton"] button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main form button[kind="primaryFormSubmit"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main form button[data-testid="stBaseButton-primaryFormSubmit"] {{
    background: {_GRAY_BG} !important;
    background-color: rgba(32,32,36,.99) !important;
    color: {_GRAY_COLOR} !important;
    border: 1px solid {_GRAY_BORDER} !important;
    font-weight: 700 !important;
    min-height: 48px !important;
    border-radius: 15px !important;
    box-shadow: {_GRAY_GLOW} !important;
}}
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .stFormSubmitButton button p,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main form button[kind="primaryFormSubmit"] p {{
    color: {_GRAY_COLOR} !important;
}}

/* Link buttons */
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main a[data-testid="stLinkButtonLink"],
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) div[data-testid="stLinkButton"] a,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main .mb-stripe-checkout-wrap a {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 48px !important;
    border-radius: 15px !important;
    font-weight: 700 !important;
    text-decoration: none !important;
    color: {_GRAY_COLOR} !important;
    background: {_GRAY_BG_ACTIVE} !important;
    border: 1px solid {_GRAY_BORDER_HOVER} !important;
    box-shadow: {_GRAY_GLOW} !important;
}}
section.main a[data-testid="stLinkButtonLink"]:hover,
div[data-testid="stLinkButton"] a:hover {{
    transform: translateY(-1px) !important;
    color: {_GRAY_COLOR} !important;
    background: {_GRAY_BG_HOVER} !important;
    box-shadow: {_GRAY_GLOW_HOVER} !important;
}}

/* Download */
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stDownloadButton"] > button,
.stApp:not(:has(.rs-studio)):not(:has(.mb-dash)) section.main [data-testid="stDownloadButton"] button {{
    background: {_GRAY_BG} !important;
    color: {_GRAY_COLOR} !important;
    border: 1px solid {_GRAY_BORDER} !important;
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
    return SIDEBAR_NAV_BUTTON_CSS + MAIN_BUTTON_CSS


def inject_master_buttons() -> None:
    """Call after page CSS so Streamlit BaseButtons stay themed."""
    inject_css(master_button_css())
