"""
MaByte global button styles — einheitlich dunkel-gold auf allen Seiten.
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

# Dunkel-Gold Basis (alle Buttons)
_DG_BG = "linear-gradient(135deg, rgba(78,56,14,.98) 0%, rgba(42,28,6,.99) 52%, rgba(28,18,4,.99) 100%)"
_DG_BG_HOVER = "linear-gradient(135deg, rgba(118,84,22,.98) 0%, rgba(68,46,10,.99) 52%, rgba(38,24,6,.99) 100%)"
_DG_BG_ACTIVE = "linear-gradient(135deg, rgba(148,106,28,.96) 0%, rgba(88,58,12,.99) 52%, rgba(48,30,6,.99) 100%)"
_DG_COLOR = "#ffe7a3"
_DG_COLOR_HOVER = "#fff8e7"
_DG_BORDER = "rgba(255,211,106,.28)"
_DG_BORDER_HOVER = "rgba(255,211,106,.48)"
_DG_GLOW = "0 8px 22px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,231,163,.1)"
_DG_GLOW_HOVER = "0 0 26px rgba(245,158,11,.28), 0 10px 28px rgba(0,0,0,.25)"

SIDEBAR_NAV_BUTTON_CSS = f"""
/* Sidebar — dunkel-gold */
section[data-testid="stSidebar"] .mb-nav-item .stButton,
section[data-testid="stSidebar"] .mb-nav-item {_BTN} {{
    width: 100% !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN} {{
    width: 100% !important;
    min-height: 50px !important;
    border-radius: 16px !important;
    border: 1px solid {_DG_BORDER} !important;
    background: {_DG_BG} !important;
    background-color: rgba(42,28,6,.99) !important;
    color: {_DG_COLOR} !important;
    font-weight: 1000 !important;
    font-size: 14px !important;
    text-align: left !important;
    padding: 12px 14px 12px 54px !important;
    position: relative !important;
    box-shadow: {_DG_GLOW} !important;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN_P} {{
    color: {_DG_COLOR} !important;
    font-weight: 1000 !important;
    font-size: 14px !important;
}}
section[data-testid="stSidebar"] .mb-nav-item button[kind="primary"],
section[data-testid="stSidebar"] .mb-nav-item button[kind="secondary"],
section[data-testid="stSidebar"] .mb-nav-item [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] .mb-nav-item [data-testid="stBaseButton-secondary"] {{
    background: {_DG_BG} !important;
    background-color: rgba(42,28,6,.99) !important;
    color: {_DG_COLOR} !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN}:hover {{
    transform: translateY(-1px) !important;
    color: {_DG_COLOR_HOVER} !important;
    border-color: {_DG_BORDER_HOVER} !important;
    background: {_DG_BG_HOVER} !important;
    background-color: rgba(68,46,10,.99) !important;
    box-shadow: {_DG_GLOW_HOVER} !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN}:hover p {{
    color: {_DG_COLOR_HOVER} !important;
}}
section[data-testid="stSidebar"] .mb-nav-active {_BTN} {{
    color: {_DG_COLOR_HOVER} !important;
    border-color: {_DG_BORDER_HOVER} !important;
    background: {_DG_BG_ACTIVE} !important;
    background-color: rgba(88,58,12,.99) !important;
    box-shadow: {_DG_GLOW_HOVER} !important;
}}
section[data-testid="stSidebar"] .mb-nav-active {_BTN_P} {{
    color: {_DG_COLOR_HOVER} !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN} {{
    width: 100% !important;
    min-height: 40px !important;
    padding: 8px 14px !important;
    text-align: center !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, rgba(36,26,8,.95), rgba(20,14,4,.98)) !important;
    background-color: rgba(28,18,4,.98) !important;
    border: 1px solid rgba(255,211,106,.18) !important;
    color: #c9a86c !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN_P} {{
    color: #c9a86c !important;
    text-align: center !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN}:hover {{
    color: {_DG_COLOR} !important;
    border-color: {_DG_BORDER} !important;
    background: {_DG_BG_HOVER} !important;
}}
"""

MAIN_BUTTON_CSS = f"""
/* Main — alle Buttons dunkel-gold (primary = secondary) */
section.main .stButton > button,
section.main .stButton {_BTN},
section.main {_BTN} {{
    border-radius: 15px !important;
    font-weight: 950 !important;
    min-height: 46px !important;
    border: 1px solid {_DG_BORDER} !important;
    background: {_DG_BG} !important;
    background-color: rgba(42,28,6,.99) !important;
    color: {_DG_COLOR} !important;
    box-shadow: {_DG_GLOW} !important;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease !important;
}}
section.main .stButton > button p,
section.main .stButton {_BTN_P},
section.main {_BTN_P} {{
    color: {_DG_COLOR} !important;
    font-weight: 1000 !important;
}}
section.main .stButton > button[kind="secondary"],
section.main .stButton > button[kind="primary"],
section.main button[data-testid="stBaseButton-secondary"],
section.main button[data-testid="stBaseButton-primary"],
section.main [data-testid="stBaseButton-secondary"],
section.main [data-testid="stBaseButton-primary"],
section.main .mb-btn-gold .stButton > button,
section.main .mb-btn-gold {_BTN} {{
    background: {_DG_BG} !important;
    background-color: rgba(42,28,6,.99) !important;
    color: {_DG_COLOR} !important;
    border: 1px solid {_DG_BORDER} !important;
    box-shadow: {_DG_GLOW} !important;
}}
section.main .stButton > button[kind="secondary"] p,
section.main .stButton > button[kind="primary"] p,
section.main button[data-testid="stBaseButton-secondary"] p,
section.main button[data-testid="stBaseButton-primary"] p,
section.main .mb-btn-gold {_BTN_P} {{
    color: {_DG_COLOR} !important;
}}
section.main .stButton > button:hover,
section.main .stButton {_BTN}:hover,
section.main button[data-testid="stBaseButton-secondary"]:hover,
section.main button[data-testid="stBaseButton-primary"]:hover,
section.main .mb-btn-gold {_BTN}:hover {{
    transform: translateY(-1px) !important;
    color: {_DG_COLOR_HOVER} !important;
    border-color: {_DG_BORDER_HOVER} !important;
    background: {_DG_BG_HOVER} !important;
    background-color: rgba(68,46,10,.99) !important;
    box-shadow: {_DG_GLOW_HOVER} !important;
}}
section.main .stButton > button:hover p,
section.main .mb-btn-gold {_BTN}:hover p {{
    color: {_DG_COLOR_HOVER} !important;
}}
section.main .stButton > button:disabled,
section.main button[disabled],
section.main [data-testid="stBaseButton-secondary"][disabled],
section.main [data-testid="stBaseButton-primary"][disabled] {{
    opacity: .45 !important;
    background: linear-gradient(135deg, rgba(55,48,38,.9), rgba(35,30,24,.95)) !important;
    background-color: rgba(45,40,32,.95) !important;
    color: #9ca3af !important;
    border-color: rgba(148,163,184,.2) !important;
    box-shadow: none !important;
    transform: none !important;
}}
section.main .stButton > button:disabled p,
section.main button[disabled] p {{
    color: #9ca3af !important;
}}

/* Form submit */
section.main .stFormSubmitButton > button,
section.main .stFormSubmitButton button,
section.main [data-testid="stFormSubmitButton"] > button,
section.main [data-testid="stFormSubmitButton"] button,
section.main form button[kind="primaryFormSubmit"],
section.main form button[data-testid="stBaseButton-primaryFormSubmit"] {{
    background: {_DG_BG} !important;
    background-color: rgba(42,28,6,.99) !important;
    color: {_DG_COLOR} !important;
    border: 1px solid {_DG_BORDER_HOVER} !important;
    font-weight: 1000 !important;
    min-height: 48px !important;
    border-radius: 15px !important;
    box-shadow: {_DG_GLOW_HOVER} !important;
}}
section.main .stFormSubmitButton button p,
section.main form button[kind="primaryFormSubmit"] p {{
    color: {_DG_COLOR} !important;
}}

/* Link buttons */
section.main a[data-testid="stLinkButtonLink"],
div[data-testid="stLinkButton"] a,
section.main .mb-stripe-checkout-wrap a {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 48px !important;
    border-radius: 15px !important;
    font-weight: 1000 !important;
    text-decoration: none !important;
    color: {_DG_COLOR} !important;
    background: {_DG_BG_ACTIVE} !important;
    border: 1px solid {_DG_BORDER_HOVER} !important;
    box-shadow: {_DG_GLOW_HOVER} !important;
}}
section.main a[data-testid="stLinkButtonLink"]:hover,
div[data-testid="stLinkButton"] a:hover {{
    transform: translateY(-2px) !important;
    color: {_DG_COLOR_HOVER} !important;
    background: {_DG_BG_HOVER} !important;
    box-shadow: {_DG_GLOW_HOVER} !important;
}}

/* Download */
section.main [data-testid="stDownloadButton"] > button,
section.main [data-testid="stDownloadButton"] button {{
    background: {_DG_BG} !important;
    color: {_DG_COLOR} !important;
    border: 1px solid {_DG_BORDER} !important;
}}

/* Tabs */
div[data-testid="stTabs"] button[data-baseweb="tab"] {{
    color: #94a3b8 !important;
    font-weight: 800 !important;
    background: transparent !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {_DG_COLOR} !important;
    border-color: {_DG_BORDER_HOVER} !important;
    background: rgba(78,56,14,.35) !important;
}}
"""


def master_button_css() -> str:
    return SIDEBAR_NAV_BUTTON_CSS + MAIN_BUTTON_CSS


def inject_master_buttons() -> None:
    """Call after page CSS so Streamlit BaseButtons stay themed."""
    inject_css(master_button_css())
