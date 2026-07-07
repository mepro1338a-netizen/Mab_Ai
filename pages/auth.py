"""MaByte Auth — Login & Registrierung (Betaphase)."""
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
/* MaByte Auth — Marble edition */
:root {
    /* Marble palette (cool concrete grey) */
    --auth-marble-base: #c5c3c0;
    --auth-marble-hi: #d8d6d3;
    --auth-marble-mid: #a8a6a3;
    --auth-marble-lo: #8f8d8a;
    --auth-vein: rgba(60, 60, 58, 0.14);
    --auth-vein-strong: rgba(30, 30, 28, 0.20);

    /* Neutral tokens (legacy names preserved for cross-block usage) */
    --auth-bg: #c5c3c0;
    --auth-surface: rgba(255, 255, 255, 0.62);
    --auth-line: rgba(80, 76, 68, 0.18);
    --auth-text: #141414;
    --auth-muted: #5a564f;
    --auth-hint: #8a857c;
    --auth-field: rgba(255, 255, 255, 0.72);
    --auth-field-line: rgba(80, 76, 68, 0.22);
    --auth-accent: #1a1a1a;
    --auth-accent-hover: #050505;
    --auth-violet: #4a4640;

    /* Glass tokens (graphite on marble) */
    --auth-glass-bg: rgba(255, 255, 255, 0.55);
    --auth-glass-tray: rgba(255, 255, 255, 0.42);
    --auth-glass-inactive-text: #4a4640;
    --auth-glass-active-fill: rgba(20, 20, 18, 0.95);
    --auth-glass-border-grad: linear-gradient(
        90deg,
        rgba(70, 66, 58, 0.7),
        rgba(140, 134, 122, 0.6)
    );
    --auth-glass-submit-fill: linear-gradient(
        180deg,
        rgba(20, 20, 18, 0.98),
        rgba(56, 54, 50, 0.98)
    );

    --auth-seg-btn-h: 48px;
    --auth-submit-h: 52px;
    --auth-glass-border: rgba(80, 76, 68, 0.22);
    --auth-glass-border-hover: rgba(20, 20, 18, 0.55);
    --auth-glass-blur: blur(18px);
    --auth-radius: 10px;
    --auth-input-h: 44px;
    --auth-pad: 36px;
    --auth-w: 440px;
    --auth-banner-h: 160px;
    --s1: 8px;
    --s2: 16px;
    --s3: 24px;
}

html:has(.auth-marker) {
    background-color: var(--auth-marble-base) !important;
}

html:has(.auth-marker) body,
html:has(.auth-marker) .stApp,
html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"],
html:has(.auth-marker) section.main .block-container,
html:has(.auth-marker) [data-testid="stMain"] .block-container,
html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
    background: transparent !important;
    background-color: transparent !important;
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

/* Marble background — layered gradients simulate polished marble */
.auth-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        linear-gradient(112deg,
            transparent 41.4%, var(--auth-vein-strong) 41.7%, transparent 42.0%,
            transparent 45.4%, var(--auth-vein) 45.7%, transparent 46.0%),
        linear-gradient(82deg,
            transparent 64.4%, var(--auth-vein) 64.7%, transparent 65.0%,
            transparent 78.4%, var(--auth-vein-strong) 78.7%, transparent 79.0%),
        linear-gradient(148deg,
            transparent 11.8%, var(--auth-vein) 12.2%, transparent 12.6%,
            transparent 88.4%, var(--auth-vein) 88.8%, transparent 89.2%),
        radial-gradient(ellipse 46% 42% at 22% 28%, rgba(255, 255, 255, 0.42), transparent 65%),
        radial-gradient(ellipse 38% 32% at 78% 18%, rgba(255, 255, 255, 0.32), transparent 70%),
        radial-gradient(ellipse 52% 42% at 55% 82%, rgba(255, 255, 255, 0.28), transparent 65%),
        radial-gradient(ellipse 32% 26% at 12% 75%, rgba(80, 80, 78, 0.34), transparent 70%),
        radial-gradient(ellipse 42% 36% at 92% 88%, rgba(70, 70, 68, 0.38), transparent 65%),
        linear-gradient(135deg,
            var(--auth-marble-hi) 0%,
            var(--auth-marble-base) 45%,
            var(--auth-marble-mid) 100%);
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
    min-height: var(--auth-banner-h);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 14px;
    box-sizing: border-box;
    padding: 28px clamp(6px, 1.2vw, 16px);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0));
    border-bottom: 1px solid rgba(80, 76, 68, 0.14);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
    overflow: hidden;
}

.auth-early-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    max-width: calc(100% - 16px);
    padding: 9px 22px;
    border: 1px solid transparent;
    border-radius: 999px;
    background:
        linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.7)) padding-box,
        linear-gradient(90deg, rgba(70, 66, 58, 0.6), rgba(140, 134, 122, 0.5)) border-box;
    color: #1a1a1a;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.26em;
    text-transform: uppercase;
    line-height: 1;
    white-space: nowrap;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.7),
        0 2px 12px rgba(30, 26, 20, 0.10);
}

.auth-early-pill::before {
    content: "";
    flex-shrink: 0;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #1a1a1a;
    box-shadow: 0 0 6px rgba(30, 26, 20, 0.35);
}

.auth-slogan-line {
    margin: 0;
    width: 100%;
    text-align: center;
    font-size: clamp(17px, calc((100vw - 20px) / 15), 48px);
    font-weight: 500;
    letter-spacing: 0.04em;
    line-height: 1;
    white-space: nowrap;
}

.auth-slogan-grad {
    font-family: "Playfair Display", "Cormorant Garamond", "Times New Roman", serif;
    font-weight: 800;
    font-style: normal;
    letter-spacing: -0.01em;
    background: linear-gradient(180deg, #050505 0%, #262624 55%, #4a4640 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
}

.auth-slogan-plain {
    color: var(--auth-muted);
    font-weight: 400;
    letter-spacing: 0.08em;
    font-size: 0.72em;
}

.auth-beta-sub {
    margin: 0;
    text-align: center;
    font-size: clamp(11px, 1.8vw, 13px);
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    line-height: 1.4;
    color: var(--auth-hint);
}

html:has(.auth-marker) .st-key-auth_card {
    width: min(var(--auth-w), calc(100% - 32px)) !important;
    max-width: var(--auth-w) !important;
    margin: 0 auto !important;
}

html:has(.auth-marker) .st-key-auth_card > [data-testid="stVerticalBlock"]:has(.auth-card-marker) {
    position: relative !important;
    width: 100% !important;
    min-width: min(var(--auth-w), calc(100% - 32px)) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.65) !important;
    background: var(--auth-surface) !important;
    backdrop-filter: blur(28px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(140%) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.75),
        inset 0 -1px 0 rgba(80, 76, 68, 0.08),
        0 24px 44px -20px rgba(30, 26, 20, 0.32),
        0 4px 14px rgba(30, 26, 20, 0.08) !important;
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
    max-width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
}

html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stElementContainer"],
html:has(.auth-marker) .st-key-auth_seg_wrap [data-testid="stVerticalBlock"],
html:has(.auth-marker) .st-key-auth_mode_seg,
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stElementContainer"],
html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

html:has(.auth-marker) .st-key-auth_mode_seg [data-testid="stElementContainer"] > div {
    display: flex !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
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
    font-family: "Playfair Display", "Cormorant Garamond", "Times New Roman", serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.015em;
    line-height: 1.25;
    color: var(--auth-text) !important;
}

.auth-sub {
    margin: 6px 0 0;
    font-size: 13px;
    line-height: 1.5;
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
    padding: 0 40px 0 14px !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.65),
        inset 0 -1px 0 rgba(80, 76, 68, 0.05) !important;
    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease !important;
}

html:has(.auth-marker) .st-key-auth_card .st-key-auth_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_user input,
html:has(.auth-marker) .st-key-auth_card .st-key-reg_email input {
    padding-right: 14px !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input::placeholder {
    color: var(--auth-hint) !important;
    opacity: 1 !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:hover {
    border-color: rgba(80, 76, 68, 0.36) !important;
    background: rgba(255, 255, 255, 0.78) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stTextInput"] input:focus {
    border-color: rgba(20, 20, 18, 0.6) !important;
    background: rgba(255, 255, 255, 0.86) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.7),
        0 0 0 3px rgba(20, 20, 18, 0.09) !important;
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
    border: 1px solid rgba(80, 76, 68, 0.22) !important;
    border-radius: 999px !important;
    background: rgba(255, 255, 255, 0.6) !important;
    background-image: none !important;
    color: var(--auth-muted) !important;
    backdrop-filter: var(--auth-glass-blur) !important;
    -webkit-backdrop-filter: var(--auth-glass-blur) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
    transition:
        background 0.15s ease,
        border-color 0.15s ease,
        color 0.15s ease,
        box-shadow 0.15s ease !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:hover,
html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] button[data-testid="stBaseButton-tertiary"]:hover {
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: rgba(20, 20, 18, 0.45) !important;
    color: var(--auth-text) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.85),
        0 2px 8px rgba(30, 26, 20, 0.12) !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] [data-testid="stButton"] button:disabled,
html:has(.auth-marker) .stApp section.main .st-key-auth_card [data-testid="stTextInput"] button[data-testid="stBaseButton-tertiary"]:disabled {
    opacity: 0.4 !important;
    background: rgba(255, 255, 255, 0.4) !important;
    border-color: rgba(80, 76, 68, 0.12) !important;
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
    color: var(--auth-text) !important;
    font-weight: 600 !important;
    backdrop-filter: var(--auth-glass-blur) !important;
    -webkit-backdrop-filter: var(--auth-glass-blur) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;
}

html:has(.auth-marker) .stApp section.main .st-key-auth_card .stButton > button:not([kind="primary"]):hover,
html:has(.auth-marker) .stApp section.main .st-key-auth_card .stButton > button[kind="secondary"]:hover,
html:has(.auth-marker) .stApp section.main .st-key-auth_card button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255, 255, 255, 0.72) !important;
    border-color: var(--auth-glass-border-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.85),
        0 4px 14px rgba(30, 26, 20, 0.14) !important;
    transform: translateY(-1px) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stAlert"] {
    border-radius: var(--auth-radius) !important;
    font-size: 14px !important;
    margin: 0 0 var(--s2) !important;
    width: 100% !important;
    border: 1px solid rgba(80, 76, 68, 0.18) !important;
    background: rgba(255, 255, 255, 0.55) !important;
    color: var(--auth-text) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stAlert"] p {
    color: var(--auth-text) !important;
}

html:has(.auth-marker) .st-key-auth_card [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

.auth-footer {
    margin: 20px 0 0;
    padding-top: var(--s2);
    border-top: 1px solid rgba(80, 76, 68, 0.14);
    text-align: center;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--auth-hint) !important;
}

html:has(.auth-marker) .stApp {
    --background-color: #c5c3c0 !important;
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
        --auth-banner-h: 128px;
    }
    html:has(.auth-marker) .auth-slogan-line {
        font-size: clamp(14px, calc((100vw - 16px) / 14), 30px);
        letter-spacing: 0.03em;
    }
    html:has(.auth-marker) .auth-slogan-bar {
        gap: 10px;
        padding: 18px clamp(6px, 1.2vw, 14px);
    }
    html:has(.auth-marker) .auth-early-pill {
        font-size: 11px;
        padding: 7px 16px;
        letter-spacing: 0.2em;
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
_AUTH_SEG_CHAIN = (
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stElementContainer'], "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stVerticalBlock'], "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stElementContainer'], "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stVerticalBlock'], "
    f"{_AUTH_SCOPE} .st-key-auth_seg_wrap, "
    f"{_AUTH_SCOPE} .st-key-auth_mode_seg"
)
_AUTH_SEG_TRAY = (
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stElementContainer'] > div, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl'], "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stSegmentedControl'], "
    f"{_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stElementContainer'] > div, "
    f"{_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl']"
)
_AUTH_SEG_BTN = (
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stElementContainer'] button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap .st-key-auth_mode_seg button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_seg_wrap [data-testid='stSegmentedControl'] button, "
    f"html:has(.auth-marker) {_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stSegmentedControl'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_mode_seg [data-testid='stElementContainer'] button, "
    f"{_AUTH_SCOPE} .st-key-auth_seg_wrap .st-key-auth_mode_seg button, "
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

/* Segmented control — full-width chain (ST 1.50: no stSegmentedControl testid) */
{_AUTH_SEG_CHAIN} {{
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}}

/* Segmented control — frosted white glass tray on marble */
{_AUTH_SEG_TRAY} {{
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    background: var(--auth-glass-tray) !important;
    background-color: var(--auth-glass-tray) !important;
    background-image: none !important;
    border: 1px solid rgba(80, 76, 68, 0.20) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    backdrop-filter: blur(18px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(140%) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.75),
        0 6px 22px rgba(30, 26, 20, 0.10) !important;
}}

{_AUTH_SEG_BTN} {{
    flex: 1 1 0 !important;
    width: 50% !important;
    max-width: none !important;
    min-width: 50% !important;
    min-height: var(--auth-seg-btn-h) !important;
    height: var(--auth-seg-btn-h) !important;
    margin: 0 !important;
    padding: 0 20px !important;
    border: 1px solid transparent !important;
    outline: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    line-height: 1 !important;
    color: var(--auth-glass-inactive-text) !important;
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    transform: none !important;
    transition:
        background 0.18s ease,
        color 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease !important;
}}

{_AUTH_SEG_BTN}:hover:not([aria-selected="true"]) {{
    background: rgba(255, 255, 255, 0.55) !important;
    background-color: rgba(255, 255, 255, 0.55) !important;
    background-image: none !important;
    color: var(--auth-text) !important;
    border-color: rgba(80, 76, 68, 0.22) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
    transform: none !important;
}}

{_AUTH_SEG_BTN}:focus,
{_AUTH_SEG_BTN}:focus-visible {{
    outline: none !important;
}}

{_AUTH_SEG_BTN}[aria-selected="true"] {{
    border: 1px solid transparent !important;
    color: #fafaf6 !important;
    background:
        linear-gradient(var(--auth-glass-active-fill), var(--auth-glass-active-fill)) padding-box,
        var(--auth-glass-border-grad) border-box !important;
    background-color: transparent !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.14),
        inset 0 -1px 0 rgba(0, 0, 0, 0.5),
        0 8px 22px rgba(20, 20, 18, 0.35) !important;
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
    gap: 10px !important;
    width: 100% !important;
    min-height: var(--auth-submit-h) !important;
    height: auto !important;
    padding: 14px 22px !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    background:
        var(--auth-glass-submit-fill) padding-box,
        var(--auth-glass-border-grad) border-box !important;
    background-color: transparent !important;
    color: #fafaf6 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.15),
        inset 0 -1px 0 rgba(0, 0, 0, 0.5),
        0 12px 30px rgba(20, 20, 18, 0.34),
        0 3px 10px rgba(20, 20, 18, 0.18) !important;
    transform: none !important;
    transition:
        background 0.18s ease,
        box-shadow 0.18s ease,
        transform 0.12s ease,
        border-color 0.18s ease !important;
}}

{_AUTH_SUBMIT_BTN}::after {{
    content: "›" !important;
    font-size: 20px !important;
    line-height: 1 !important;
    opacity: 0.95 !important;
    transform: translateY(-1px) !important;
}}

{_AUTH_SUBMIT_BTN}:hover {{
    background:
        linear-gradient(180deg, rgba(6, 6, 5, 1), rgba(46, 44, 40, 1)) padding-box,
        linear-gradient(90deg, rgba(50, 46, 40, 0.9), rgba(160, 154, 142, 0.7)) border-box !important;
    background-color: transparent !important;
    border-color: transparent !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.22),
        inset 0 -1px 0 rgba(0, 0, 0, 0.6),
        0 18px 36px rgba(20, 20, 18, 0.42),
        0 4px 12px rgba(20, 20, 18, 0.22) !important;
}}

{_AUTH_SUBMIT_BTN}:active {{
    transform: translateY(0) !important;
}}

{_AUTH_SUBMIT_BTN}:disabled {{
    opacity: 0.55 !important;
    background: rgba(80, 76, 68, 0.18) !important;
    background-image: none !important;
    background-color: rgba(80, 76, 68, 0.18) !important;
    border: 1px solid rgba(80, 76, 68, 0.24) !important;
    color: rgba(20, 20, 18, 0.55) !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: not-allowed !important;
}}

{_AUTH_SUBMIT_BTN}:disabled::after {{
    opacity: 0.35 !important;
}}

{_AUTH_SUBMIT_BTN} p {{
    margin: 0 !important;
    color: #fafaf6 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
}}

{_AUTH_SUBMIT_BTN}:hover p {{
    color: #ffffff !important;
}}

{_AUTH_SUBMIT_BTN}:disabled p {{
    color: rgba(20, 20, 18, 0.55) !important;
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
  <span class="auth-early-pill">Betaphase</span>
  <p class="auth-slogan-line">
    <span class="auth-slogan-grad">MaByte</span><span class="auth-slogan-plain"> offizieller Start in die </span><span class="auth-slogan-grad">Betaphase</span>
  </p>
  <p class="auth-beta-sub">Infos coming soon.</p>
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
    st.markdown(
        '<div class="auth-intro">'
        '<p class="auth-title">Anmelden</p>'
        '<p class="auth-sub">Melde dich mit deinem bestehenden Konto an.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
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
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700'
        '&family=Playfair+Display:ital,wght@0,600;0,700;0,800;0,900;1,700;1,800'
        '&display=swap">',
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
                width="stretch",
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
