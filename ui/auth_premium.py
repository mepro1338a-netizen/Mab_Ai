"""Minimal MaByte auth UI — stable Streamlit layout, no layout hacks."""
from __future__ import annotations

import html

from config import APP_NAME

_APP = html.escape(APP_NAME)
_INITIAL = html.escape(APP_NAME[:1] if APP_NAME else "M")


def auth_styles_bundle() -> str:
    """Single CSS bundle for the auth route."""
    return """
html { color-scheme: dark; }

.stApp:has(.auth-page) {
    background: linear-gradient(180deg, #09090b 0%, #18181b 42%, #09090b 100%) !important;
    color: #fafafa !important;
    font-family: Inter, system-ui, sans-serif !important;
}

.stApp:has(.auth-page) #MainMenu,
.stApp:has(.auth-page) footer,
.stApp:has(.auth-page) [data-testid="stToolbar"],
.stApp:has(.auth-page) [data-testid="stDecoration"],
.stApp:has(.auth-page) [data-testid="stSidebar"],
.stApp:has(.auth-page) [data-testid="stStatusWidget"],
.stApp:has(.auth-page) [data-testid="stDeployButton"],
.stApp:has(.auth-page) [data-testid="stHeader"] {
    display: none !important;
}

.stApp:has(.auth-page) [data-testid="stMain"] .block-container,
.stApp:has(.auth-page) [data-testid="stMainBlockContainer"] {
    max-width: 1100px !important;
    padding: 1.5rem 1.25rem 2.5rem !important;
}

.stApp:has(.auth-page) [data-testid="stAlert"] {
    display: none !important;
}

/* Branding (left column HTML) */
.brand-panel {
    width: 100%;
    max-width: 520px;
    padding: 0.5rem 0;
}
.brand-panel .logo-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1rem;
}
.brand-panel .logo-mark {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    flex-shrink: 0;
}
.brand-panel .logo-name {
    font-size: 1.5rem;
    font-weight: 800;
    color: #fafafa;
    letter-spacing: -0.03em;
    white-space: nowrap;
}
.brand-panel h1 {
    font-size: 1.75rem;
    font-weight: 800;
    line-height: 1.25;
    margin: 0 0 0.75rem 0;
    color: #fafafa;
    white-space: normal;
    word-break: normal;
}
.brand-panel h1 span {
    color: #a78bfa;
}
.brand-panel p {
    font-size: 0.9rem;
    line-height: 1.55;
    color: #a1a1aa;
    margin: 0 0 1.25rem 0;
    white-space: normal;
    word-break: normal;
}
.brand-panel .feat {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.brand-panel .feat-item {
    padding: 12px;
    border-radius: 12px;
    background: rgba(39, 39, 42, 0.6);
    border: 1px solid #3f3f46;
    font-size: 12px;
    color: #d4d4d8;
    white-space: normal;
    word-break: normal;
}
.brand-panel .feat-item strong {
    display: block;
    color: #fafafa;
    margin-bottom: 4px;
    font-size: 13px;
}

/* Login card — Streamlit column wrapper */
.stApp:has(.auth-page) [data-testid="stVerticalBlock"]:has(.auth-card-root) {
    width: 100%;
    max-width: 440px;
    margin-left: auto;
    margin-right: 0;
    padding: 2rem;
    border-radius: 18px;
    background: rgba(24, 24, 27, 0.98);
    border: 1px solid #3f3f46;
    box-sizing: border-box;
}

.stApp:has(.auth-mode-register) [data-testid="stVerticalBlock"]:has(.auth-card-root) {
    margin-left: auto;
    margin-right: auto;
}

.auth-card-head {
    text-align: center;
    margin-bottom: 1.25rem;
}
.auth-card-head .logo-mark {
    width: 40px;
    height: 40px;
    margin: 0 auto 10px auto;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
}
.auth-card-head h2 {
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    color: #fafafa;
    white-space: normal;
    word-break: normal;
}
.auth-card-head p {
    margin: 0;
    font-size: 0.85rem;
    color: #a1a1aa;
    white-space: normal;
    word-break: normal;
}

.auth-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 600;
    color: #d4d4d8;
    margin: 0.75rem 0 0.35rem 0;
    white-space: normal;
}

.auth-link {
    color: #a78bfa;
    text-decoration: none;
    font-size: 0.85rem;
    white-space: nowrap;
}

.auth-divider {
    text-align: center;
    color: #71717a;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.25rem 0 1rem 0;
}

.auth-switch {
    text-align: center;
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #71717a;
    white-space: normal;
}

.auth-notice {
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 0.85rem;
    margin-bottom: 12px;
    white-space: normal;
    word-break: normal;
}
.auth-notice-error {
    color: #fecaca;
    background: rgba(127, 29, 29, 0.4);
    border: 1px solid rgba(248, 113, 113, 0.35);
}
.auth-notice-success {
    color: #bbf7d0;
    background: rgba(20, 83, 45, 0.4);
    border: 1px solid rgba(74, 222, 128, 0.35);
}
.auth-notice-info {
    color: #bfdbfe;
    background: rgba(30, 58, 138, 0.4);
    border: 1px solid rgba(96, 165, 250, 0.35);
}

.auth-foot {
    text-align: center;
    margin-top: 2rem;
    font-size: 0.7rem;
    color: #52525b;
}

/* Widgets on auth page */
.stApp:has(.auth-page) [data-testid="stTextInput"] input,
.stApp:has(.auth-page) [data-testid="stNumberInput"] input {
    background: #27272a !important;
    color: #fafafa !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
}

.stApp:has(.auth-page) div[data-baseweb="input"] {
    background: #27272a !important;
    border-color: #3f3f46 !important;
    border-radius: 10px !important;
}

.stApp:has(.auth-page) [data-testid="stNumberInput"] button {
    background: #27272a !important;
    color: #a1a1aa !important;
    border-color: #3f3f46 !important;
}

.stApp:has(.auth-page) [data-testid="stCheckbox"] label,
.stApp:has(.auth-page) [data-testid="stCheckbox"] label p {
    color: #a1a1aa !important;
    font-size: 0.85rem !important;
}

.stApp:has(.auth-page) [data-testid="stFormSubmitButton"] button[kind="primary"],
.stApp:has(.auth-page) [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"] {
    width: 100% !important;
    min-height: 46px !important;
    border: none !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}

.stApp:has(.auth-page) [data-testid="stFormSubmitButton"] button[kind="primary"] p {
    color: #ffffff !important;
}

.stApp:has(.auth-page) [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button {
    min-height: 44px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}

.stApp:has(.auth-page) [data-testid="stLinkButton"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 44px !important;
    border-radius: 10px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #fafafa !important;
    text-decoration: none !important;
    font-weight: 600 !important;
}

.stApp:has(.auth-page) .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #a78bfa !important;
    box-shadow: none !important;
    min-height: auto !important;
    height: auto !important;
    padding: 0.25rem 0 !important;
}

.stApp:has(.auth-page) .stButton > button p {
    color: #a78bfa !important;
    font-weight: 600 !important;
}

@media (max-width: 900px) {
    .brand-panel .feat {
        grid-template-columns: 1fr;
    }
    .stApp:has(.auth-page) [data-testid="stVerticalBlock"]:has(.auth-card-root) {
        margin-left: auto;
        margin-right: auto;
        max-width: 100%;
    }
}
"""


def auth_page_open(mode: str = "login") -> str:
    safe = "auth-mode-register" if mode == "register" else "auth-mode-login"
    return f'<div class="auth-page {safe}"></div>'


def auth_page_close() -> str:
    return f'<p class="auth-foot">© 2026 {_APP} GmbH</p>'


def brand_panel_html() -> str:
    return f"""
<div class="brand-panel">
  <div class="logo-row">
    <span class="logo-mark">{_INITIAL}</span>
    <span class="logo-name">{_APP}</span>
  </div>
  <h1>One system.<br><span>Infinite intelligence.</span></h1>
  <p>Enterprise-Plattform für AI Content, Football Intelligence und Automatisierung.</p>
  <div class="feat">
    <div class="feat-item"><strong>AI Reels</strong>Video & Shorts mit KI</div>
    <div class="feat-item"><strong>Football AI</strong>Analyse & Prognosen</div>
    <div class="feat-item"><strong>Publishing</strong>Omnichannel Flow</div>
    <div class="feat-item"><strong>Teams</strong>Gemeinsam skalieren</div>
  </div>
</div>
"""


def auth_card_header_html(*, register: bool) -> str:
    if register:
        title = "Konto erstellen"
        sub = "Registrierung für Ihren MaByte Workspace."
    else:
        title = "Anmelden"
        sub = "Melden Sie sich in Ihrem MaByte Workspace an."
    return f"""
<div class="auth-card-head">
  <div class="logo-mark">{_INITIAL}</div>
  <h2>{html.escape(title)}</h2>
  <p>{html.escape(sub)}</p>
</div>
"""


def auth_card_marker_html() -> str:
    return '<span class="auth-card-root" hidden aria-hidden="true"></span>'


def auth_notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    lvl = html.escape(level)
    return f'<div class="auth-notice auth-notice-{lvl}" role="alert">{safe}</div>'


def auth_divider_html() -> str:
    return '<p class="auth-divider">oder</p>'


def auth_forgot_link_html() -> str:
    return '<a class="auth-link" href="#" onclick="return false;">Passwort vergessen?</a>'


def auth_label_html(text: str) -> str:
    return f'<p class="auth-label">{html.escape(text)}</p>'


def auth_switch_note_html(*, register: bool) -> str:
    if register:
        return '<p class="auth-switch">Bereits registriert?</p>'
    return '<p class="auth-switch">Noch kein Konto?</p>'


# Legacy aliases (ui.py OAuth callback, older imports)
page_open_html = auth_page_open
page_close_html = auth_page_close
notice_html = auth_notice_html
oauth_divider_html = auth_divider_html
forgot_password_html = auth_forgot_link_html
panel_shell_html = lambda *, register: auth_card_header_html(register=register)
login_card_marker_html = auth_card_marker_html
panel_close_html = lambda: ""
hero_html = brand_panel_html
auth_grid_marker_html = lambda: ""
