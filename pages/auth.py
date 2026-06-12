"""MaByte Auth — Login & Registrierung."""
from __future__ import annotations

import streamlit as st

from database import record_login_event, register_account, verify_login_identifier
from logger import log_auth
from oauth_service import complete_oauth, friendly_oauth_error, verify_state
from security import check_login_rate, is_valid_email, is_valid_username, record_login_failure
from services.session_auth import rotate_session_on_login
from ui.styles import inject_css

_DEFAULT_USE_CASE = "Sonstiges"
_DEFAULT_COUNTRY = "Deutschland"

_AUTH_CSS = """
/* MaByte Auth */
:root {
    --auth-bg: #09090b;
    --auth-surface: rgba(24, 24, 27, 0.98);
    --auth-line: rgba(255, 255, 255, 0.09);
    --auth-text: #fafafa;
    --auth-muted: #a1a1aa;
    --auth-hint: #71717a;
    --auth-field: #18181b;
    --auth-field-line: rgba(255, 255, 255, 0.11);
    --auth-accent: #7c3aed;
    --auth-accent-hover: #6d28d9;
    --auth-violet: #8b5cf6;
    --auth-glass-bg: rgba(255, 255, 255, 0.06);
    --auth-glass-tray: rgba(255, 255, 255, 0.04);
    --auth-glass-inactive-text: #d4d4d8;
    --auth-glass-active-fill: rgba(139, 92, 246, 0.2);
    --auth-glass-border-grad: linear-gradient(
        90deg,
        rgba(139, 92, 246, 0.75),
        rgba(99, 102, 241, 0.75)
    );
    --auth-glass-submit-fill: linear-gradient(
        rgba(139, 92, 246, 0.14),
        rgba(99, 102, 241, 0.1)
    );
    --auth-seg-btn-h: 44px;
    --auth-submit-h: 48px;
    --auth-glass-border: rgba(255, 255, 255, 0.14);
    --auth-glass-border-hover: rgba(139, 92, 246, 0.45);
    --auth-glass-blur: blur(16px);
    --auth-radius: 10px;
    --auth-input-h: 44px;
    --auth-pad: 36px;
    --auth-w: 440px;
    --auth-banner-h: 140px;
    --s1: 8px;
    --s2: 16px;
    --s3: 24px;
}

html:has(.auth-marker),
html:has(.auth-marker) body,
html:has(.auth-marker) .stApp,
html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"],
html:has(.auth-marker) section.main .block-container,
html:has(.auth-marker) [data-testid="stMain"] .block-container {
    background: var(--auth-bg) !important;
    background-color: var(--auth-bg) !important;
    background-image: none !important;
    color: var(--auth-text) !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

html:has(.auth-marker) #MainMenu,
html:has(.auth-marker) footer,
html:has(.auth-marker) [data-testid="stToolbar"],
html:has(.auth-marker) [data-testid="stDecoration"],
html:has(.auth-marker) [data-testid="stSidebar"],
html:has(.auth-marker) [data-testid="stHeader"] {
    display: none !important;
}

.auth-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 70% 45% at 50% -15%, rgba(124, 58, 237, 0.12), transparent 62%),
        var(--auth-bg);
}

html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"] {
    min-height: 100dvh !important;
}

html:has(.auth-marker) [data-testid="stMain"] {
    position: relative !important;
    z-index: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    justify-content: flex-start !important;
    padding: 0 0 var(--s3) !important;
    overflow-y: auto !important;
}

html:has(.auth-marker) [data-testid="stMain"] .block-container,
html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

.auth-slogan-bar {
    position: relative;
    left: 50%;
    width: 100vw;
    min-width: 100vw;
    margin-left: -50vw;
    margin-right: -50vw;
    margin-bottom: var(--s3);
    height: var(--auth-banner-h);
    min-height: var(--auth-banner-h);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    box-sizing: border-box;
    padding: 0 clamp(6px, 1.2vw, 16px);
    background: linear-gradient(180deg, #0a1020 0%, #050816 100%);
    overflow: hidden;
}

.auth-early-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    max-width: calc(100% - 16px);
    padding: 10px 22px;
    border: 1px solid transparent;
    border-radius: 999px;
    background:
        linear-gradient(rgba(9, 9, 11, 0.88), rgba(9, 9, 11, 0.88)) padding-box,
        linear-gradient(90deg, rgba(139, 92, 246, 0.75), rgba(99, 102, 241, 0.75)) border-box;
    color: #c4b5fd;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    line-height: 1;
    white-space: nowrap;
    box-shadow: 0 0 22px rgba(139, 92, 246, 0.18);
}

.auth-early-pill::before {
    content: "";
    flex-shrink: 0;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #8b5cf6;
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.85);
}

.auth-slogan-line {
    margin: 0;
    width: 100%;
    text-align: center;
    font-size: clamp(15px, calc((100vw - 20px) / 16.5), 44px);
    font-weight: 700;
    letter-spacing: clamp(0.06em, 0.45vw, 0.16em);
    line-height: 1;
    white-space: nowrap;
}

.auth-slogan-grad {
    background: linear-gradient(90deg, #c084fc 0%, #818cf8 48%, #6366f1 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
}

.auth-slogan-plain {
    color: #f4f4f5;
}

html:has(.auth-marker) .st-key-auth_card {
    width: min(var(--auth-w), calc(100% - 32px)) !important;
    max-width: var(--auth-w) !important;
    margin: 0 auto !important;
}

html:has(.auth-marker) .st-key-auth_card > [data-testid="stVerticalBlock"]:has(.auth-card-marker) {
    position: relative !important;
    border-radius: 14px !important;
    border: 1px solid var(--auth-line) !important;
    background: var(--auth-surface) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.06),
        0 20px 40px -16px rgba(0, 0, 0, 0.55) !important;
    padding: var(--auth-pad) !important;
    gap: 0 !important;
    align-items: stretch !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap {
    margin: 0 0 24px !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stWidgetLabel"],
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stWidgetLabel"] {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.auth-intro {
    margin: 0 0 var(--s2);
    text-align: left;
}

.auth-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.015em;
    line-height: 1.3;
    color: var(--auth-text) !important;
}

.auth-sub {
    margin: 4px 0 0;
    font-size: 13px;
    line-height: 1.45;
    color: var(--auth-muted) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    gap: 14px !important;
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] {
    width: 100% !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] label p,
html:has(.auth-marker) .st-key-auth_card [data-testid="stWidgetLabel"] p {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--auth-muted) !important;
    margin: 0 0 6px !important;
    line-height: 1.35 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stWidgetLabel"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] label[data-testid="stWidgetLabel"] {
    display: block !important;
    height: auto !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] > div:last-of-type {
    position: relative !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] > div,
html:has(.auth-marker) .st-key-auth_card div[data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input {
    background: var(--auth-field) !important;
    color: var(--auth-text) !important;
    -webkit-text-fill-color: var(--auth-text) !important;
    border: 1px solid var(--auth-field-line) !important;
    border-radius: var(--auth-radius) !important;
    min-height: var(--auth-input-h) !important;
    height: var(--auth-input-h) !important;
    font-size: 14px !important;
    padding: 0 40px 0 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_card .st-key-auth_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_email input {
    padding-right: 12px !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input::placeholder {
    color: var(--auth-hint) !important;
    opacity: 1 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:hover {
    border-color: rgba(255, 255, 255, 0.16) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:focus {
    border-color: rgba(124, 58, 237, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
    outline: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] {
    position: absolute !important;
    right: 6px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button,
html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] button[data-testid="stBaseButton-tertiary"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 32px !important;
    height: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    padding: 0 !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 999px !important;
    background: var(--auth-glass-bg) !important;
    background-image: none !important;
    color: var(--auth-muted) !important;
    backdrop-filter: var(--auth-glass-blur) !important;
    -webkit-backdrop-filter: var(--auth-glass-blur) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    transition:
        background 0.15s ease,
        border-color 0.15s ease,
        color 0.15s ease,
        box-shadow 0.15s ease !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:hover,
html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] button[data-testid="stBaseButton-tertiary"]:hover {
    background: rgba(139, 92, 246, 0.12) !important;
    border-color: var(--auth-glass-border-hover) !important;
    color: var(--auth-text) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 0 10px rgba(139, 92, 246, 0.2) !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:disabled,
html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] button[data-testid="stBaseButton-tertiary"]:disabled {
    opacity: 0.4 !important;
    background: rgba(255, 255, 255, 0.03) !important;
    border-color: rgba(255, 255, 255, 0.06) !important;
    box-shadow: none !important;
    transform: none !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] {
    margin: var(--s1) 0 0 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stCheckbox"] label p {
    font-size: 13px !important;
    color: var(--auth-muted) !important;
    line-height: 1.45 !important;
}

/* Secondary / fallback buttons — excludes password-eye tertiary toggles */
html:has(.auth-marker) .stApp section.main .st-key-auth_card .stButton > button:not([kind="primary"]),
html:has(.auth-marker) .stApp section.main .st-key-auth_card .stButton > button[kind="secondary"],
html:has(.auth-marker) .stApp section.main .st-key-auth_card button[data-testid="stBaseButton-secondary"] {
    border-radius: 12px !important;
    min-height: var(--auth-input-h) !important;
    border: 1px solid var(--auth-glass-border) !important;
    background: var(--auth-glass-bg) !important;
    background-image: none !important;
    background-color: transparent !important;
    color: var(--auth-text) !important;
    font-weight: 600 !important;
    backdrop-filter: var(--auth-glass-blur) !important;
    -webkit-backdrop-filter: var(--auth-glass-blur) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card .stButton > button:not([kind="primary"]):hover,
html:has(.auth-marker) .stApp section.main .st-key-auth_card .stButton > button[kind="secondary"]:hover,
html:has(.auth-marker) .stApp section.main .st-key-auth_card button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(139, 92, 246, 0.1) !important;
    border-color: var(--auth-glass-border-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 0 14px rgba(139, 92, 246, 0.28) !important;
    transform: translateY(-1px) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stAlert"] {
    border-radius: var(--auth-radius) !important;
    font-size: 14px !important;
    margin: 0 0 var(--s2) !important;
    width: 100% !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

.auth-footer {
    margin: 20px 0 0;
    padding-top: var(--s2);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    font-size: 11px;
    color: var(--auth-hint) !important;
}

html:has(.auth-marker) .stApp {
    --background-color: #09090b !important;
}

html:has(.auth-marker) .st-key-auth_card,
html:has(.auth-marker) .st-key-auth_card [data-testid="stForm"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] {
    --primary-color: transparent !important;
}

@media (max-width: 640px) {
    html:has(.auth-marker) {
        --auth-pad: 28px;
        --auth-w: 100%;
        --auth-banner-h: 104px;
    }
    html:has(.auth-marker) .auth-slogan-line {
        font-size: clamp(13px, calc((100vw - 16px) / 15), 28px);
        letter-spacing: clamp(0.04em, 0.35vw, 0.1em);
    }
    html:has(.auth-marker) .auth-slogan-bar {
        gap: 8px;
    }
    html:has(.auth-marker) .auth-early-pill {
        font-size: 12px;
        padding: 8px 18px;
        letter-spacing: 0.14em;
    }
    html:has(.auth-marker) [data-testid="stMain"] {
        justify-content: flex-start !important;
        padding-top: var(--s2) !important;
    }
}
"""

# Injected last in render_auth() — wins over Streamlit primary theme + app_shell.
_AUTH_SCOPE = (
    ".stApp:has(.auth-marker):not(:has(.mb-dash)):not(:has(.img-studio))"
    ":not(:has(.mb-workspace)):not(:has(.mb-home)) section.main"
)
_AUTH_SEG = (
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl'], "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stSegmentedControl'], "
    f"{_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl']"
)
_AUTH_SEG_BTN = (
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl'] button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stSegmentedControl'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stSegmentedControl'] button"
)
_AUTH_SUBMIT_BTN = (
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card [data-testid='stFormSubmitButton'] button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card .st-key-auth_login_form [data-testid='stFormSubmitButton'] button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card .st-key-auth_register_form [data-testid='stFormSubmitButton'] button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card button[kind='primary'], "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card button[data-testid='stBaseButton-primary'], "
    f"{_AUTH_SCOPE} .st-key-auth_card [data-testid='stFormSubmitButton'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_card .st-key-auth_login_form [data-testid='stFormSubmitButton'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_card .st-key-auth_register_form [data-testid='stFormSubmitButton'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_card button[kind='primary'], "
    f"{_AUTH_SCOPE} .st-key-auth_card button[data-testid='stBaseButton-primary']"
)

_AUTH_BUTTONS_FINAL = f"""
/* _AUTH_BUTTONS_FINAL — tabs + submit glass (Early-Access pill language) */
html:has(.auth-marker) .st-key-auth_card,
html:has(.auth-marker) .st-key-auth_card [data-testid="stForm"],
html:has(.auth-marker) .st-key-auth_card [data-testid="stFormSubmitButton"] {{
    --primary-color: transparent !important;
}}

/* Segmented control — frosted glass tray, full card width */
{_AUTH_SEG} {{
    display: flex !important;
    width: 100% !important;
    box-sizing: border-box !important;
    background: var(--auth-glass-tray) !important;
    background-color: var(--auth-glass-tray) !important;
    background-image: none !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.06),
        0 4px 20px rgba(0, 0, 0, 0.2) !important;
}}

{_AUTH_SEG_BTN} {{
    flex: 1 1 50% !important;
    width: auto !important;
    max-width: none !important;
    min-width: 0 !important;
    min-height: var(--auth-seg-btn-h) !important;
    height: var(--auth-seg-btn-h) !important;
    margin: 0 !important;
    padding: 0 20px !important;
    border: 1px solid var(--auth-glass-border) !important;
    outline: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    line-height: 1 !important;
    color: var(--auth-glass-inactive-text) !important;
    background: var(--auth-glass-bg) !important;
    background-color: var(--auth-glass-bg) !important;
    background-image: none !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: var(--auth-glass-blur) !important;
    -webkit-backdrop-filter: var(--auth-glass-blur) !important;
    transform: none !important;
    transition:
        background 0.18s ease,
        color 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease !important;
}}

{_AUTH_SEG_BTN}:hover:not([aria-selected="true"]) {{
    background: rgba(255, 255, 255, 0.1) !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
    background-image: none !important;
    color: var(--auth-text) !important;
    border-color: var(--auth-glass-border-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 0 16px rgba(139, 92, 246, 0.28) !important;
    transform: none !important;
}}

{_AUTH_SEG_BTN}:focus,
{_AUTH_SEG_BTN}:focus-visible {{
    outline: none !important;
}}

{_AUTH_SEG_BTN}[aria-selected="true"] {{
    border: 1px solid transparent !important;
    color: var(--auth-text) !important;
    background:
        linear-gradient(var(--auth-glass-active-fill), var(--auth-glass-active-fill)) padding-box,
        var(--auth-glass-border-grad) border-box !important;
    background-color: transparent !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.12),
        0 0 22px rgba(139, 92, 246, 0.22) !important;
    transform: none !important;
}}

html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card [data-testid="stFormSubmitButton"],
html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card .st-key-auth_register_form [data-testid="stFormSubmitButton"],
html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card .st-key-auth_login_form [data-testid="stFormSubmitButton"] {{
    margin-top: var(--s1) !important;
    width: 100% !important;
}}

html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card [data-testid="stFormSubmitButton"] > div,
html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card .st-key-auth_register_form [data-testid="stFormSubmitButton"] > div,
html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_card .st-key-auth_login_form [data-testid="stFormSubmitButton"] > div {{
    width: 100% !important;
}}

{_AUTH_SUBMIT_BTN} {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    width: 100% !important;
    min-height: var(--auth-submit-h) !important;
    height: auto !important;
    padding: 12px 20px !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    background:
        var(--auth-glass-submit-fill) padding-box,
        var(--auth-glass-border-grad) border-box !important;
    background-color: transparent !important;
    color: var(--auth-text) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.12),
        0 0 22px rgba(139, 92, 246, 0.18),
        0 4px 16px rgba(0, 0, 0, 0.2) !important;
    transform: none !important;
    transition:
        background 0.18s ease,
        box-shadow 0.18s ease,
        transform 0.12s ease !important;
}}

{_AUTH_SUBMIT_BTN}::after {{
    content: "›" !important;
    font-size: 18px !important;
    line-height: 1 !important;
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}}

{_AUTH_SUBMIT_BTN}:hover {{
    background:
        linear-gradient(rgba(139, 92, 246, 0.24), rgba(99, 102, 241, 0.16)) padding-box,
        linear-gradient(90deg, rgba(167, 139, 250, 0.85), rgba(129, 140, 248, 0.85)) border-box !important;
    background-color: transparent !important;
    border-color: transparent !important;
    color: var(--auth-text) !important;
    transform: translateY(-1px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.16),
        0 0 32px rgba(139, 92, 246, 0.38),
        0 6px 20px rgba(0, 0, 0, 0.26) !important;
}}

{_AUTH_SUBMIT_BTN}:active {{
    transform: translateY(0) !important;
}}

{_AUTH_SUBMIT_BTN}:disabled {{
    opacity: 0.45 !important;
    background: rgba(255, 255, 255, 0.04) !important;
    background-image: none !important;
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: rgba(255, 255, 255, 0.55) !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: not-allowed !important;
}}

{_AUTH_SUBMIT_BTN}:disabled::after {{
    opacity: 0.35 !important;
}}

{_AUTH_SUBMIT_BTN} p {{
    margin: 0 !important;
    color: var(--auth-text) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}}

{_AUTH_SUBMIT_BTN}:disabled p {{
    color: rgba(255, 255, 255, 0.55) !important;
}}
"""


def _get_mode() -> str:
    mode = str(st.session_state.get("gate_mode") or st.session_state.get("auth_mode") or "login")
    return mode if mode in ("login", "register") else "login"


def _set_mode(mode: str) -> None:
    st.session_state.gate_mode = mode
    st.session_state.auth_mode = mode
    st.session_state["auth_mode_seg"] = "Registrieren" if mode == "register" else "Anmelden"


def _render_slogan_header() -> None:
    st.markdown(
        """
<div class="auth-slogan-bar" role="banner">
  <span class="auth-early-pill">Early Access</span>
  <p class="auth-slogan-line">
    <span class="auth-slogan-grad">One</span><span class="auth-slogan-plain"> system. </span><span class="auth-slogan-grad">Infinite</span><span class="auth-slogan-plain"> intelligence.</span>
  </p>
</div>
        """,
        unsafe_allow_html=True,
    )


def client_meta() -> tuple[str, str]:
    ip_address = "unknown"
    user_agent = "streamlit-client"
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        headers = getattr(ctx, "request_headers", {}) if ctx else {}
        if headers:
            ip_address = headers.get("X-Forwarded-For", "unknown")
            user_agent = headers.get("User-Agent", "streamlit-client")
    except Exception:
        pass
    return ip_address, user_agent


def _utm_from_query() -> dict:
    params = st.query_params
    keys = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")
    return {k: str(params.get(k) or "").strip() for k in keys if params.get(k)}


def _set_notice(level: str, message: str) -> None:
    st.session_state.gate_notice = {"level": level, "message": message}


def _show_notice() -> None:
    notice = st.session_state.pop("gate_notice", None) or st.session_state.pop("auth_notice", None)
    if not notice:
        return
    level = notice.get("level", "info")
    message = notice.get("message", "")
    if level == "error":
        st.error(message)
    elif level == "success":
        st.success(message)
    else:
        st.info(message)


def do_login(username: str, password: str) -> None:
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        _set_notice("error", "Bitte Benutzername und Passwort eingeben.")
        return

    allowed, msg = check_login_rate(username)
    if not allowed:
        _set_notice("error", msg)
        return

    ok, login_msg, user = verify_login_identifier(username, password)
    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user.get("username") or username, ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth(f"Login: {username}")
        st.rerun()
        return

    record_login_failure(username)
    _set_notice("error", login_msg or "Benutzername oder Passwort stimmen nicht.")


def do_register(
    *,
    username: str,
    email: str,
    password: str,
    password2: str,
    terms: bool,
) -> None:
    username = (username or "").strip()
    email = (email or "").strip()
    password = password or ""
    password2 = password2 or ""

    if password != password2:
        _set_notice("error", "Die Passwörter stimmen nicht überein.")
        return

    if not is_valid_username(username):
        _set_notice("error", "Benutzername: 3–40 Zeichen, Buchstaben, Zahlen oder Unterstrich (_).")
        return

    if not is_valid_email(email):
        _set_notice("error", "Bitte gib eine gültige E-Mail-Adresse ein.")
        return

    if not terms:
        _set_notice("error", "Bitte bestätige AGB und Datenschutz.")
        return

    ip_address, user_agent = client_meta()
    ok, msg, user = register_account(
        username=username,
        email=email,
        password=password,
        full_name=username,
        company="",
        phone="",
        country=_DEFAULT_COUNTRY,
        use_case=_DEFAULT_USE_CASE,
        marketing_opt_in=False,
        terms_accepted=terms,
        ip_address=ip_address,
        user_agent=user_agent,
        utm=_utm_from_query(),
    )

    if ok and user:
        record_login_event(user.get("username") or username, ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth(f"Register+Login: {username}")
        st.session_state.pop("gate_notice", None)
        st.rerun()
        return

    _set_notice("error", msg)


def handle_google_oauth_callback() -> None:
    params = st.query_params
    code = str(params.get("code") or "").strip()
    state = str(params.get("state") or "").strip()
    error = str(params.get("error") or "").strip()
    error_desc = str(params.get("error_description") or "").strip()

    _set_mode("login")
    st.query_params.clear()

    if error:
        _set_notice("error", friendly_oauth_error(error, error_desc))
        st.rerun()
        return

    provider = verify_state(state)
    if provider != "google" or not code:
        _set_notice("error", "OAuth-Session ungültig. Bitte mit Benutzername anmelden.")
        st.rerun()
        return

    ok, msg, user = complete_oauth("google", code)
    if ok and user:
        ip_address, user_agent = client_meta()
        record_login_event(user.get("username") or "", ip_address, user_agent, success=True)
        rotate_session_on_login(user)
        log_auth("Login: google_oauth")
        st.rerun()
        return

    _set_notice("error", msg or "Anmeldung fehlgeschlagen.")
    st.rerun()


def _render_login_form() -> None:
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="auth_user")
        password = st.text_input("Passwort", type="password", key="auth_pass")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
    if submitted:
        do_login(username, password)


def _render_register_form() -> None:
    st.markdown(
        '<div class="auth-intro">'
        '<p class="auth-title">Konto erstellen</p>'
        '<p class="auth-sub">Kostenlos starten — in unter einer Minute.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", placeholder="z. B. max_mustermann", key="reg_user")
        email = st.text_input("E-Mail", placeholder="name@beispiel.de", key="reg_email")
        password = st.text_input("Passwort", type="password", placeholder="Sicheres Passwort", key="reg_pass")
        password2 = st.text_input(
            "Passwort bestätigen",
            type="password",
            placeholder="Passwort wiederholen",
            key="reg_pass2",
        )
        terms = st.checkbox("Ich akzeptiere die AGB und die Datenschutzerklärung", key="reg_terms")
        submitted = st.form_submit_button("Kostenlos registrieren", type="primary", use_container_width=True)
    if submitted:
        do_register(
            username=username,
            email=email,
            password=password,
            password2=password2,
            terms=terms,
        )


def render_auth() -> None:
    if _get_mode() not in ("login", "register"):
        _set_mode("login")
    elif "gate_mode" not in st.session_state:
        _set_mode("login")

    if "auth_mode_seg" not in st.session_state:
        st.session_state.auth_mode_seg = "Registrieren" if _get_mode() == "register" else "Anmelden"

    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">',
        unsafe_allow_html=True,
    )
    inject_css(_AUTH_CSS)
    st.markdown('<div class="auth-bg" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    _render_slogan_header()

    with st.container(key="auth_card", border=False):
        st.markdown('<span class="auth-card-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

        with st.container(key="auth_seg_wrap"):
            choice = st.segmented_control(
                label=" ",
                options=["Anmelden", "Registrieren"],
                key="auth_mode_seg",
                label_visibility="collapsed",
            )

        mode = "register" if choice == "Registrieren" else "login"
        st.session_state.gate_mode = mode
        st.session_state.auth_mode = mode
        st.markdown(
            f'<span class="auth-mode-{mode}" hidden aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )

        _show_notice()

        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()

        st.markdown(
            '<p class="auth-footer">Verschlüsselte Übertragung</p>',
            unsafe_allow_html=True,
        )

    inject_css(_AUTH_BUTTONS_FINAL)
