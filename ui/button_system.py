"""
MaByte global button styles — overrides Streamlit white BaseButtons everywhere.
"""
from __future__ import annotations

from ui.styles import inject_css

# Streamlit 1.33+ renders <button data-testid="stBaseButton-secondary"> — not only .stButton > button
_BTN = "button, [data-testid='stBaseButton-primary'], [data-testid='stBaseButton-secondary'], [data-testid='stBaseButton-tertiary']"
_BTN_P = "button p, [data-testid='stBaseButton-primary'] p, [data-testid='stBaseButton-secondary'] p"

SIDEBAR_NAV_BUTTON_CSS = f"""
/* ---- Sidebar nav (gold/purple, never white) ---- */
section[data-testid="stSidebar"] .mb-nav-item .stButton,
section[data-testid="stSidebar"] .mb-nav-item .stButton > button,
section[data-testid="stSidebar"] .mb-nav-item {_BTN} {{
    width: 100% !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN} {{
    width: 100% !important;
    min-height: 50px !important;
    max-height: none !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,231,163,.18) !important;
    background: linear-gradient(135deg, rgba(32,9,48,.96), rgba(12,6,22,.99)) !important;
    background-color: rgba(18,8,30,.99) !important;
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
    font-size: 14px !important;
    text-align: left !important;
    padding: 12px 14px 12px 54px !important;
    position: relative !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.04), 0 8px 22px rgba(0,0,0,.18) !important;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN_P} {{
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
    font-size: 14px !important;
}}
section[data-testid="stSidebar"] .mb-nav-item button[kind="secondary"],
section[data-testid="stSidebar"] .mb-nav-item [data-testid="stBaseButton-secondary"] {{
    background: linear-gradient(135deg, rgba(32,9,48,.96), rgba(12,6,22,.99)) !important;
    background-color: rgba(18,8,30,.99) !important;
    color: #ffe7a3 !important;
}}
section[data-testid="stSidebar"] .mb-nav-item button[kind="primary"],
section[data-testid="stSidebar"] .mb-nav-item [data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, rgba(32,9,48,.96), rgba(12,6,22,.99)) !important;
    background-color: rgba(18,8,30,.99) !important;
    color: #ffe7a3 !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN}:hover {{
    transform: translateY(-1px) !important;
    color: #ffffff !important;
    border-color: rgba(255,231,163,.36) !important;
    background: linear-gradient(135deg, rgba(91,33,182,.82), rgba(22,8,36,.99)) !important;
    background-color: rgba(55,20,85,.99) !important;
    box-shadow: 0 0 24px rgba(168,85,247,.28) !important;
}}
section[data-testid="stSidebar"] .mb-nav-item {_BTN}:hover p {{
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] .mb-nav-active {_BTN} {{
    color: #ffffff !important;
    border-color: rgba(255,211,106,.5) !important;
    background: linear-gradient(135deg, rgba(126,34,206,.88), rgba(38,12,62,.99)) !important;
    background-color: rgba(88,28,135,.99) !important;
    box-shadow: 0 0 30px rgba(168,85,247,.32), inset 0 0 0 1px rgba(255,255,255,.06) !important;
}}
section[data-testid="stSidebar"] .mb-nav-active {_BTN_P} {{
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN} {{
    width: 100% !important;
    min-height: 40px !important;
    padding: 8px 14px !important;
    text-align: center !important;
    border-radius: 12px !important;
    background: rgba(15,23,42,.75) !important;
    background-color: rgba(15,23,42,.75) !important;
    border: 1px solid rgba(148,163,184,.22) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN_P} {{
    color: #94a3b8 !important;
    text-align: center !important;
}}
section[data-testid="stSidebar"] .sidebar-logout-wrap {_BTN}:hover {{
    color: #f8fafc !important;
    border-color: rgba(255,231,163,.28) !important;
    background: rgba(30,27,50,.9) !important;
}}
"""

MAIN_BUTTON_CSS = f"""
/* ---- Main content: default + primary CTA ---- */
section.main .stButton > button,
section.main .stButton {_BTN},
section.main {_BTN} {{
    border-radius: 15px !important;
    font-weight: 950 !important;
    min-height: 46px !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}}
section.main .stButton > button[kind="secondary"],
section.main .stButton button[kind="secondary"],
section.main button[data-testid="stBaseButton-secondary"],
section.main [data-testid="stBaseButton-secondary"] {{
    background: linear-gradient(135deg, rgba(49,18,62,.96), rgba(12,6,22,.99)) !important;
    background-color: rgba(18,8,28,.99) !important;
    color: #ffe7a3 !important;
    border: 1px solid rgba(255,231,163,.2) !important;
    box-shadow: 0 8px 20px rgba(0,0,0,.16) !important;
}}
section.main .stButton > button[kind="secondary"] p,
section.main button[data-testid="stBaseButton-secondary"] p {{
    color: #ffe7a3 !important;
}}
section.main .stButton > button[kind="primary"],
section.main .stButton button[kind="primary"],
section.main button[data-testid="stBaseButton-primary"],
section.main [data-testid="stBaseButton-primary"],
section.main .mb-btn-gold .stButton > button,
section.main .mb-btn-gold {_BTN} {{
    background: linear-gradient(135deg, #ffd36a 0%, #f59e0b 52%, #ea580c 100%) !important;
    background-color: #f59e0b !important;
    color: #111827 !important;
    border: 1px solid rgba(255,255,255,.22) !important;
    box-shadow: 0 12px 28px rgba(245,158,11,.32), 0 0 18px rgba(255,211,106,.2) !important;
}}
section.main .stButton > button[kind="primary"] p,
section.main button[data-testid="stBaseButton-primary"] p,
section.main .mb-btn-gold {_BTN_P} {{
    color: #111827 !important;
    font-weight: 1000 !important;
}}
section.main .stButton > button:hover,
section.main .stButton {_BTN}:hover,
section.main button[data-testid="stBaseButton-secondary"]:hover {{
    transform: translateY(-1px) !important;
    border-color: rgba(255,231,163,.38) !important;
    box-shadow: 0 0 22px rgba(168,85,247,.22) !important;
}}
section.main .stButton > button[kind="primary"]:hover,
section.main button[data-testid="stBaseButton-primary"]:hover,
section.main .mb-btn-gold {_BTN}:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 16px 36px rgba(245,158,11,.42), 0 0 24px rgba(255,211,106,.28) !important;
    color: #0f172a !important;
}}
section.main .stButton > button:disabled,
section.main button[disabled],
section.main [data-testid="stBaseButton-secondary"][disabled],
section.main [data-testid="stBaseButton-primary"][disabled] {{
    opacity: .5 !important;
    background: linear-gradient(135deg, #6b7280, #4b5563) !important;
    background-color: #6b7280 !important;
    color: #e5e7eb !important;
    box-shadow: none !important;
    transform: none !important;
}}
section.main .stButton > button:disabled p,
section.main button[disabled] p {{
    color: #e5e7eb !important;
}}

/* Form submit */
section.main .stFormSubmitButton > button,
section.main .stFormSubmitButton button,
section.main [data-testid="stFormSubmitButton"] > button,
section.main [data-testid="stFormSubmitButton"] button,
section.main form button[kind="primaryFormSubmit"],
section.main form button[data-testid="stBaseButton-primaryFormSubmit"] {{
    background: linear-gradient(135deg, #ffd36a 0%, #f59e0b 50%, #ea580c 100%) !important;
    background-color: #f59e0b !important;
    color: #111827 !important;
    border: 1px solid rgba(255,255,255,.2) !important;
    font-weight: 1000 !important;
    min-height: 48px !important;
    border-radius: 15px !important;
    box-shadow: 0 12px 28px rgba(245,158,11,.3) !important;
}}
section.main .stFormSubmitButton button p,
section.main form button[kind="primaryFormSubmit"] p {{
    color: #111827 !important;
}}

/* Link buttons (Stripe etc.) */
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
    color: #111827 !important;
    background: linear-gradient(135deg, #ffd36a 0%, #f59e0b 55%, #ea580c 100%) !important;
    box-shadow: 0 12px 28px rgba(245,158,11,.35), 0 0 20px rgba(255,211,106,.22) !important;
}}
section.main a[data-testid="stLinkButtonLink"]:hover,
div[data-testid="stLinkButton"] a:hover {{
    transform: translateY(-2px) !important;
    color: #0f172a !important;
    box-shadow: 0 16px 36px rgba(245,158,11,.45) !important;
}}

/* Download */
section.main [data-testid="stDownloadButton"] > button,
section.main [data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, rgba(30,64,175,.55), rgba(12,18,42,.98)) !important;
    color: #ffe7a3 !important;
    border: 1px solid rgba(96,165,250,.28) !important;
}}

/* Tabs */
div[data-testid="stTabs"] button[data-baseweb="tab"] {{
    color: #94a3b8 !important;
    font-weight: 800 !important;
    background: transparent !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #ffe7a3 !important;
    border-color: rgba(255,211,106,.45) !important;
    background: rgba(124,58,237,.12) !important;
}}
"""


def master_button_css() -> str:
    return SIDEBAR_NAV_BUTTON_CSS + MAIN_BUTTON_CSS


def inject_master_buttons() -> None:
    """Call after page CSS so Streamlit BaseButtons stay themed."""
    inject_css(master_button_css())
