"""MaByte Auth — pixel-matched reference login (Streamlit + scoped CSS)."""
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

# Scoped CSS — values extracted from auth-reference.png
# All rules scoped under html:has(.auth-marker) for reliable override of Streamlit defaults.
_AUTH_CSS = """
:root {
    --auth-bg: #020617;
    --auth-card: rgba(15, 23, 42, 0.6);
    --auth-card-border-tl: rgba(168, 85, 247, 0.35);
    --auth-card-border-br: rgba(59, 130, 246, 0.35);
    --auth-text: #ffffff;
    --auth-muted: #94a3b8;
    --auth-placeholder: #475569;
    --auth-input-bg: rgba(15, 23, 42, 0.92);
    --auth-input-border: rgba(255, 255, 255, 0.06);
    --auth-byte: #e9d5ff;
    --auth-violet: #8b5cf6;
    --auth-blue: #3b82f6;
    --auth-ssl: #64748b;
    --auth-ease: cubic-bezier(0.4, 0, 0.2, 1);
    --auth-pad-x: 2.5rem;
}

html:has(.auth-marker),
html:has(.auth-marker) body,
html:has(.auth-marker) .stApp,
html:has(.auth-marker) [data-testid="stAppViewContainer"],
html:has(.auth-marker) [data-testid="stAppViewBlockContainer"],
html:has(.auth-marker) section.main,
html:has(.auth-marker) [data-testid="stMain"],
html:has(.auth-marker) [data-testid="stMainBlockContainer"],
html:has(.auth-marker) section.main .block-container,
html:has(.auth-marker) [data-testid="stMain"] .block-container {
    background: var(--auth-bg) !important;
    background-color: var(--auth-bg) !important;
    background-image: none !important;
    color: var(--auth-text) !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

html:has(.auth-marker) #MainMenu,
html:has(.auth-marker) footer,
html:has(.auth-marker) [data-testid="stToolbar"],
html:has(.auth-marker) [data-testid="stDecoration"],
html:has(.auth-marker) [data-testid="stSidebar"],
html:has(.auth-marker) [data-testid="stHeader"] {
    display: none !important;
}

/* ── Full-screen neon background (reference waves) ── */
.auth-scene {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
    background: var(--auth-bg);
}
.auth-wave {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.55;
}
.auth-wave--purple {
    width: 720px;
    height: 520px;
    top: 8%;
    left: -12%;
    background: radial-gradient(ellipse at 30% 50%, rgba(168, 85, 247, 0.55) 0%, rgba(139, 92, 246, 0.2) 45%, transparent 72%);
    transform: rotate(-18deg);
    animation: authWavePurple 16s var(--auth-ease) infinite alternate;
}
.auth-wave--blue {
    width: 680px;
    height: 500px;
    top: 10%;
    right: -14%;
    background: radial-gradient(ellipse at 70% 50%, rgba(59, 130, 246, 0.5) 0%, rgba(99, 102, 241, 0.18) 42%, transparent 70%);
    transform: rotate(14deg);
    animation: authWaveBlue 18s var(--auth-ease) infinite alternate;
}
.auth-horizon {
    position: absolute;
    left: 50%;
    bottom: 8%;
    width: 680px;
    height: 180px;
    transform: translateX(-50%);
    background: radial-gradient(ellipse at center bottom, rgba(147, 197, 253, 0.22) 0%, rgba(139, 92, 246, 0.12) 35%, transparent 70%);
    filter: blur(24px);
}
.auth-stars {
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at 12% 18%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 78% 22%, rgba(255,255,255,0.25) 0%, transparent 100%),
        radial-gradient(1px 1px at 45% 8%, rgba(255,255,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 88% 65%, rgba(255,255,255,0.18) 0%, transparent 100%),
        radial-gradient(1px 1px at 22% 72%, rgba(255,255,255,0.15) 0%, transparent 100%),
        radial-gradient(1px 1px at 62% 88%, rgba(255,255,255,0.2) 0%, transparent 100%);
    opacity: 0.7;
}
@keyframes authWavePurple {
    from { transform: rotate(-18deg) translateY(0); opacity: 0.45; }
    to { transform: rotate(-14deg) translateY(-24px); opacity: 0.62; }
}
@keyframes authWaveBlue {
    from { transform: rotate(14deg) translateY(0); opacity: 0.42; }
    to { transform: rotate(18deg) translateY(-20px); opacity: 0.58; }
}

html:has(.auth-marker) [data-testid="stMain"] {
    position: relative !important;
    z-index: 1 !important;
}
html:has(.auth-marker) [data-testid="stMain"] .block-container,
html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
    max-width: 500px !important;
    width: min(500px, 100%) !important;
    margin: 0 auto !important;
    padding: clamp(2rem, 6vh, 3.5rem) 1.25rem 2.5rem !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-marker) {
    gap: 0 !important;
}

/* ── Glass card (container + border wrapper, Streamlit 1.50) ── */
html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.auth-glass-marker),
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) {
    position: relative !important;
    padding: 0 !important;
    border-radius: 24px !important;
    background: var(--auth-card) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(20px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(20px) saturate(1.2) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 0 0 1px rgba(139, 92, 246, 0.08),
        0 0 48px rgba(139, 92, 246, 0.12),
        0 0 80px rgba(59, 130, 246, 0.08),
        0 24px 64px rgba(0, 0, 0, 0.45) !important;
    overflow: hidden !important;
    gap: 0 !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.auth-glass-marker)::before,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker)::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 24px;
    padding: 1px;
    background: linear-gradient(135deg, var(--auth-card-border-tl) 0%, rgba(255,255,255,0.06) 50%, var(--auth-card-border-br) 100%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    pointer-events: none;
    z-index: 0;
}
html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.auth-glass-marker) > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}

html:has(.auth-marker) .auth-card-head {
    position: relative;
    z-index: 1;
    padding: 2.75rem var(--auth-pad-x) 0;
    text-align: center;
    background: transparent;
    border: none;
}
html:has(.auth-marker) .auth-wordmark {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
    text-shadow: 0 0 24px rgba(255, 255, 255, 0.12);
    color: var(--auth-text) !important;
}
html:has(.auth-marker) .auth-wordmark-ma { color: #ffffff !important; }
html:has(.auth-marker) .auth-wordmark-byte { color: var(--auth-byte) !important; }

/* Card body padding via scoped widget margins (no broken HTML wrappers) */
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stHorizontalBlock"]:has(.st-key-auth_tab_login),
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stAlert"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stForm"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stMarkdownContainer"]:has(.auth-form-title),
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="element-container"]:has(.auth-form-title) {
    margin-left: var(--auth-pad-x) !important;
    margin-right: var(--auth-pad-x) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stForm"] {
    padding-bottom: 0.25rem !important;
}

/* ── Segmented tabs ── */
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stHorizontalBlock"]:has(.st-key-auth_tab_login) {
    background: rgba(2, 6, 23, 0.55) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    margin-top: 1.75rem !important;
    margin-bottom: 1.75rem !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register {
    margin: 0 !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton > button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton > button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login button[data-testid="baseButton-secondary"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register button[data-testid="baseButton-secondary"] {
    width: 100% !important;
    min-height: 42px !important;
    border-radius: 9px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    background-color: transparent !important;
    color: #64748b !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: color 0.2s var(--auth-ease), background 0.2s var(--auth-ease),
                border-color 0.2s var(--auth-ease), box-shadow 0.2s var(--auth-ease) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton > button:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton > button:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login button[data-testid="baseButton-secondary"]:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register button[data-testid="baseButton-secondary"]:hover {
    color: var(--auth-muted) !important;
    background: rgba(255, 255, 255, 0.03) !important;
    background-color: rgba(255, 255, 255, 0.03) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login .stButton > button p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register .stButton > button p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_login button[data-testid="baseButton-secondary"] p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_tab_register button[data-testid="baseButton-secondary"] p {
    color: inherit !important;
}

html:has(.auth-marker) .auth-form-title {
    margin: 0 0 0.5rem;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.2;
    color: var(--auth-text) !important;
}
html:has(.auth-marker) .auth-form-sub {
    margin: 0 0 1.25rem;
    font-size: 0.875rem;
    font-weight: 400;
    color: var(--auth-muted) !important;
    line-height: 1.5;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stVerticalBlock"] {
    gap: 1.1rem !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] label p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stWidgetLabel"] p {
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    color: var(--auth-muted) !important;
    margin-bottom: 8px !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] textarea,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stTextInput input {
    background: var(--auth-input-bg) !important;
    background-color: var(--auth-input-bg) !important;
    color: var(--auth-text) !important;
    -webkit-text-fill-color: var(--auth-text) !important;
    border: 1px solid var(--auth-input-border) !important;
    border-radius: 8px !important;
    min-height: 46px !important;
    font-size: 0.875rem !important;
    caret-color: #c4b5fd !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    transition: border-color 0.2s var(--auth-ease), box-shadow 0.2s var(--auth-ease) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input::placeholder,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stTextInput input::placeholder {
    color: var(--auth-placeholder) !important;
    opacity: 1 !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:focus,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:focus-visible,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stTextInput input:focus {
    border-color: rgba(139, 92, 246, 0.45) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    outline: none !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px rgba(15, 23, 42, 0.95) inset !important;
    -webkit-text-fill-color: #fafafa !important;
    transition: background-color 9999s ease-out 0s !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) div[data-baseweb="input"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] > div,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Input icons */
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_user input,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-reg_user input {
    padding-left: 42px !important;
    background-color: var(--auth-input-bg) !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: 14px center !important;
    background-size: 18px 18px !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-auth_pass input,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-reg_pass input,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-reg_pass2 input {
    padding-left: 42px !important;
    padding-right: 42px !important;
    background-color: var(--auth-input-bg) !important;
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E"),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat, no-repeat !important;
    background-position: 14px center, calc(100% - 14px) center !important;
    background-size: 18px 18px, 18px 18px !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .st-key-reg_email input {
    padding-left: 42px !important;
    background-color: var(--auth-input-bg) !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='2' y='4' width='20' height='16' rx='2'/%3E%3Cpath d='m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: 14px center !important;
    background-size: 18px 18px !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stCheckbox"] label p {
    font-size: 0.8125rem !important;
    color: var(--auth-muted) !important;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button[data-testid="baseButton-primary"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"],
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[data-testid="baseButton-primary"] {
    width: 100% !important;
    min-height: 48px !important;
    margin-top: 0.25rem !important;
    border-radius: 10px !important;
    border: none !important;
    background: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%) !important;
    background-color: transparent !important;
    background-image: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%) !important;
    color: #fff !important;
    font-size: 0.9375rem !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 28px rgba(139, 92, 246, 0.35), 0 0 24px rgba(59, 130, 246, 0.15) !important;
    transition: transform 0.2s var(--auth-ease), box-shadow 0.2s var(--auth-ease), filter 0.2s var(--auth-ease) !important;
    position: relative !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"]:hover,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 32px rgba(139, 92, 246, 0.45), 0 0 32px rgba(59, 130, 246, 0.2) !important;
    filter: brightness(1.04) !important;
    background-image: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button:active,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"]:active {
    transform: translateY(0) scale(0.995) !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) .stButton > button[kind="primary"] p,
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) button[data-testid="baseButton-primary"] p {
    color: #fff !important;
    font-weight: 600 !important;
}
html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button::after {
    content: "→";
    position: absolute;
    right: 1.25rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.125rem;
    font-weight: 400;
    color: #fff;
    pointer-events: none;
}

html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stAlert"] {
    margin-bottom: 0.75rem !important;
    border-radius: 10px !important;
    font-size: 0.875rem !important;
}

html:has(.auth-marker) .auth-card-foot {
    position: relative;
    z-index: 1;
    padding: 0.75rem var(--auth-pad-x) 1.25rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    text-align: center;
    background: transparent;
}
html:has(.auth-marker) .auth-ssl {
    margin: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--auth-ssl) !important;
}
html:has(.auth-marker) .auth-ssl svg {
    flex-shrink: 0;
    opacity: 0.85;
}

@media (max-width: 640px) {
    html:has(.auth-marker) {
        --auth-pad-x: 1.5rem;
    }
    html:has(.auth-marker) [data-testid="stMain"] .block-container,
    html:has(.auth-marker) [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding: 1.5rem 1rem 2rem !important;
    }
    html:has(.auth-marker) .auth-card-head { padding-top: 2rem; }
}
@media (max-width: 480px) {
    html:has(.auth-marker) {
        --auth-pad-x: 1.25rem;
    }
    html:has(.auth-marker) .auth-wordmark { font-size: 1.5rem; }
    html:has(.auth-marker) .auth-form-title { font-size: 1.375rem; }
}

html:has(.auth-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-auth_card),
html:has(.auth-marker) .st-key-auth_card[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative !important;
    padding: 0 !important;
    border-radius: 24px !important;
    background: var(--auth-card) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(20px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(20px) saturate(1.2) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 0 0 1px rgba(139, 92, 246, 0.08),
        0 0 48px rgba(139, 92, 246, 0.12),
        0 0 80px rgba(59, 130, 246, 0.08),
        0 24px 64px rgba(0, 0, 0, 0.45) !important;
    overflow: hidden !important;
}

html:has(.auth-marker) .stApp {
    --background-color: #020617 !important;
    --secondary-background-color: rgba(15, 23, 42, 0.6) !important;
    --text-color: #ffffff !important;
    --primary-color: #8b5cf6 !important;
    --border-color: rgba(255, 255, 255, 0.1) !important;
}

/* Final lock — beat Streamlit widget defaults on auth route */
html:has(.auth-marker) section.main .stTextInput input,
html:has(.auth-marker) section.main div[data-baseweb="input"] input {
    background-color: var(--auth-input-bg) !important;
    color: var(--auth-text) !important;
    border-color: var(--auth-input-border) !important;
}
html:has(.auth-marker) section.main [data-testid="stFormSubmitButton"] button,
html:has(.auth-marker) section.main button[data-testid="baseButton-primary"] {
    background-image: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%) !important;
}

@media (prefers-reduced-motion: reduce) {
    html:has(.auth-marker) .auth-wave--purple,
    html:has(.auth-marker) .auth-wave--blue { animation: none !important; }
    html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stTextInput"] input,
    html:has(.auth-marker) [data-testid="stVerticalBlock"]:has(.auth-glass-marker) [data-testid="stFormSubmitButton"] button {
        transition: none !important;
    }
}
"""

_SSL_LOCK_SVG = (
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<rect x="3" y="11" width="18" height="11" rx="2"/>'
    '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    "</svg>"
)


def _get_mode() -> str:
    mode = str(st.session_state.get("gate_mode") or st.session_state.get("auth_mode") or "login")
    return mode if mode in ("login", "register") else "login"


def _set_mode(mode: str) -> None:
    st.session_state.gate_mode = mode
    st.session_state.auth_mode = mode


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
    _set_notice("error", login_msg or "Benutzername oder Passwort falsch.")


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
        _set_notice("error", "Passwörter stimmen nicht überein.")
        return

    if not is_valid_username(username):
        _set_notice(
            "error",
            "Benutzername: 3–40 Zeichen, nur Buchstaben, Zahlen oder Unterstrich.",
        )
        return

    if not is_valid_email(email):
        _set_notice("error", "Bitte eine gültige E-Mail-Adresse eingeben.")
        return

    if not terms:
        _set_notice("error", "Bitte AGB und Datenschutz bestätigen.")
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


def _card_head_html() -> str:
    return (
        '<div class="auth-card-head">'
        f'<h1 class="auth-wordmark">'
        f'<span class="auth-wordmark-ma">Ma</span><span class="auth-wordmark-byte">Byte</span>'
        "</h1></div>"
    )


def _tab_highlight_css(mode: str) -> str:
    active_key = "auth_tab_login" if mode == "login" else "auth_tab_register"
    return f"""
html:has(.auth-marker) .st-key-{active_key} .stButton > button,
html:has(.auth-marker) .st-key-{active_key} button[kind="secondary"],
html:has(.auth-marker) .st-key-{active_key} button[kind="tertiary"],
html:has(.auth-marker) .st-key-{active_key} button[data-testid="baseButton-secondary"] {{
    background: rgba(139, 92, 246, 0.12) !important;
    background-color: rgba(139, 92, 246, 0.12) !important;
    border: 1px solid rgba(139, 92, 246, 0.45) !important;
    color: #ffffff !important;
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.2), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}}
html:has(.auth-marker) .st-key-{active_key} .stButton > button p,
html:has(.auth-marker) .st-key-{active_key} button[data-testid="baseButton-secondary"] p {{
    color: #ffffff !important;
}}
"""


def _render_mode_tabs(mode: str) -> None:
    tab_cols = st.columns(2, gap="small")
    with tab_cols[0]:
        if st.button("Anmelden", key="auth_tab_login", use_container_width=True, type="secondary"):
            if mode != "login":
                _set_mode("login")
                st.rerun()
    with tab_cols[1]:
        if st.button("Registrieren", key="auth_tab_register", use_container_width=True, type="secondary"):
            if mode != "register":
                _set_mode("register")
                st.rerun()


def _render_login_form() -> None:
    st.markdown(
        '<p class="auth-form-title">Willkommen zurück</p>'
        '<p class="auth-form-sub">Melde dich mit deinem MaByte-Konto an.</p>',
        unsafe_allow_html=True,
    )
    with st.form("auth_login_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="auth_user", placeholder="Benutzername eingeben")
        password = st.text_input("Passwort", type="password", key="auth_pass", placeholder="Passwort eingeben")
        submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
    if submitted:
        do_login(username, password)


def _render_register_form() -> None:
    st.markdown(
        '<p class="auth-form-title">Konto erstellen</p>'
        '<p class="auth-form-sub">Registriere dich und starte direkt in der Plattform.</p>',
        unsafe_allow_html=True,
    )
    with st.form("auth_register_form", clear_on_submit=False, border=False):
        username = st.text_input("Benutzername", key="reg_user", placeholder="Benutzername eingeben")
        email = st.text_input("E-Mail", key="reg_email", placeholder="name@beispiel.de")
        password = st.text_input("Passwort", type="password", key="reg_pass", placeholder="Passwort eingeben")
        password2 = st.text_input("Passwort bestätigen", type="password", key="reg_pass2", placeholder="Passwort wiederholen")
        terms = st.checkbox("AGB und Datenschutz akzeptieren", key="reg_terms")
        submitted = st.form_submit_button("Registrieren", type="primary", use_container_width=True)
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

    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">',
        unsafe_allow_html=True,
    )
    inject_css(_AUTH_CSS)
    mode = _get_mode()
    inject_css(_tab_highlight_css(mode))

    st.markdown(
        '<div class="auth-scene" aria-hidden="true">'
        '<div class="auth-wave auth-wave--purple"></div>'
        '<div class="auth-wave auth-wave--blue"></div>'
        '<div class="auth-horizon"></div>'
        '<div class="auth-stars"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown('<span class="auth-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)

    with st.container(key="auth_card", border=False):
        st.markdown('<span class="auth-glass-marker" hidden aria-hidden="true"></span>', unsafe_allow_html=True)
        st.markdown(_card_head_html(), unsafe_allow_html=True)
        _render_mode_tabs(mode)
        _show_notice()
        if mode == "register":
            _render_register_form()
        else:
            _render_login_form()
        st.markdown(
            '<div class="auth-card-foot">'
            f'<p class="auth-ssl">{_SSL_LOCK_SVG}SSL-verschlüsselte Verbindung</p>'
            "</div>",
            unsafe_allow_html=True,
        )
