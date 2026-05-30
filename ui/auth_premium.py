"""MaByte Auth UI — clean 2-column login (Beta)."""
from __future__ import annotations

import html

from config import APP_NAME

_APP = html.escape(APP_NAME)
_INITIAL = html.escape(APP_NAME[:1] if APP_NAME else "M")

# ── Streamlit shell + page grid (no absolute positioning on layout) ──
_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html { color-scheme: dark !important; }

.stApp,
.stApp [data-testid="stAppViewContainer"],
.stApp [data-testid="stAppViewContainer"] > section,
.stApp [data-testid="stMainBlockContainer"],
.stApp [data-testid="stAppViewBlockContainer"] {
    background: #050816 !important;
    background-image:
        radial-gradient(ellipse 70% 50% at 15% 10%, rgba(168, 85, 247, 0.18), transparent 55%),
        radial-gradient(ellipse 60% 45% at 88% 8%, rgba(91, 140, 255, 0.14), transparent 50%),
        linear-gradient(180deg, #050816 0%, #0a1024 50%, #050816 100%) !important;
    color: #fafafa !important;
    font-family: Inter, system-ui, sans-serif !important;
}

.stApp #MainMenu,
.stApp footer,
.stApp [data-testid="stToolbar"],
.stApp [data-testid="stDecoration"],
.stApp [data-testid="stSidebar"],
.stApp [data-testid="stStatusWidget"],
.stApp [data-testid="stDeployButton"],
.stApp [data-testid="stHeader"] {
    display: none !important;
}

.stApp [data-testid="stMain"] .block-container,
.stApp [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    padding: 0 !important;
}

.stApp [data-testid="stAlert"] {
    display: none !important;
}

/* Top bar — normal flow */
.auth-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    padding: 0 32px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(5, 8, 22, 0.92);
    box-sizing: border-box;
}
.auth-topbar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 17px;
    font-weight: 800;
    color: #fafafa !important;
    letter-spacing: -0.03em;
}
.auth-topbar-mark {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(135deg, #a855f7, #7b61ff, #3b82f6);
}

/* 2-column auth page grid */
.stApp [data-testid="stHorizontalBlock"]:has(.auth-page-marker) {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) 520px !important;
    align-items: center !important;
    gap: 72px !important;
    max-width: 1440px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 72px 64px !important;
    min-height: calc(100vh - 80px) !important;
    box-sizing: border-box !important;
}
.stApp [data-testid="stHorizontalBlock"]:has(.auth-page-marker) > [data-testid="stColumn"]:first-child {
    min-width: 0 !important;
    width: auto !important;
    max-width: none !important;
    flex: unset !important;
    padding: 0 !important;
}
.stApp [data-testid="stHorizontalBlock"]:has(.auth-page-marker) > [data-testid="stColumn"]:last-child {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 520px !important;
    flex: unset !important;
    padding: 0 !important;
    justify-self: end !important;
}

.stApp:has(.mb-mode-register) [data-testid="stHorizontalBlock"]:has(.auth-page-marker) {
    grid-template-columns: 1fr !important;
    max-width: 520px !important;
    padding: 40px 24px 64px 24px !important;
}
.stApp:has(.mb-mode-register) [data-testid="stHorizontalBlock"]:has(.auth-page-marker) > [data-testid="stColumn"]:first-child {
    display: none !important;
}
.stApp:has(.mb-mode-register) [data-testid="stHorizontalBlock"]:has(.auth-page-marker) > [data-testid="stColumn"]:last-child {
    max-width: 100% !important;
    justify-self: center !important;
}

@media (max-width: 1100px) {
    .stApp [data-testid="stHorizontalBlock"]:has(.auth-page-marker) {
        grid-template-columns: 1fr !important;
        gap: 40px !important;
        padding: 48px 28px !important;
        min-height: auto !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has(.auth-page-marker) > [data-testid="stColumn"]:last-child {
        max-width: 520px !important;
        justify-self: center !important;
    }
}
"""

# ── Branding (left column) ──
_BRAND_CSS = """
.auth-brand {
    min-width: 0;
    width: 100%;
}
.auth-brand-name {
    display: block;
    font-size: clamp(28px, 3vw, 36px);
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin: 0 0 12px 0;
    color: #fafafa !important;
    white-space: normal !important;
    word-break: normal !important;
}
.auth-brand-name .grad {
    display: block;
    background: linear-gradient(135deg, #fafafa 0%, #c4b5fd 45%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.auth-brand-kicker {
    display: inline-block;
    padding: 5px 12px;
    margin-bottom: 14px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94a3b8 !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(10, 16, 36, 0.55);
}
.auth-brand-title {
    font-size: clamp(22px, 2.2vw, 30px);
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 12px 0;
    color: #fafafa !important;
    white-space: normal !important;
    word-break: normal !important;
}
.auth-brand-title .accent {
    display: block;
    background: linear-gradient(135deg, #a855f7, #7b61ff, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.auth-brand-sub {
    font-size: 14px;
    line-height: 1.6;
    color: #94a3b8 !important;
    margin: 0 0 22px 0;
    max-width: 520px;
    white-space: normal !important;
    word-break: normal !important;
}
.auth-feat-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    max-width: 560px;
}
.auth-feat-card {
    padding: 14px;
    border-radius: 14px;
    background: rgba(10, 16, 36, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-sizing: border-box;
}
.auth-feat-card .t {
    display: block;
    font-size: 13px;
    font-weight: 700;
    color: #f8fafc !important;
    margin-bottom: 4px;
    white-space: normal !important;
}
.auth-feat-card .d {
    font-size: 11px;
    color: #64748b !important;
    line-height: 1.4;
    white-space: normal !important;
}
@media (max-width: 640px) {
    .auth-feat-grid { grid-template-columns: 1fr !important; }
}
"""

# ── Login card chrome (HTML + Streamlit wrapper) ──
_CARD_CSS = """
.login-card-head {
    text-align: center;
    margin-bottom: 20px;
}
.login-card-logo {
    width: 40px;
    height: 40px;
    margin: 0 auto 12px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, #a855f7, #7b61ff, #3b82f6);
    font-size: 15px;
    font-weight: 800;
    color: #fff !important;
}
.login-card-title {
    font-size: 20px;
    font-weight: 700;
    color: #fafafa !important;
    margin: 0 0 6px 0;
    line-height: 1.25;
    white-space: normal !important;
    word-break: normal !important;
}
.login-card-sub {
    font-size: 13px;
    color: #94a3b8 !important;
    margin: 0;
    line-height: 1.45;
    white-space: normal !important;
}
.auth-field-label {
    display: block;
    color: #e2e8f0 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    margin: 12px 0 6px 0 !important;
    white-space: normal !important;
}
.auth-captcha-label {
    display: block;
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    margin: 14px 0 8px 0 !important;
    white-space: normal !important;
}
.auth-forgot-link {
    font-size: 13px;
    font-weight: 500;
    color: #7b61ff !important;
    text-decoration: none !important;
    white-space: nowrap !important;
}
.auth-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 18px 0 14px 0;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569 !important;
}
.auth-divider::before,
.auth-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
}
.auth-register-line {
    text-align: center;
    margin-top: 16px;
    font-size: 14px;
    color: #64748b !important;
}
.auth-notice {
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 14px;
    white-space: normal !important;
    word-break: normal !important;
}
.auth-notice-error {
    color: #fecaca !important;
    background: rgba(127, 29, 29, 0.35);
    border: 1px solid rgba(248, 113, 113, 0.3);
}
.auth-notice-success {
    color: #bbf7d0 !important;
    background: rgba(20, 83, 45, 0.35);
    border: 1px solid rgba(74, 222, 128, 0.3);
}
.auth-notice-info {
    color: #bfdbfe !important;
    background: rgba(30, 58, 138, 0.35);
    border: 1px solid rgba(96, 165, 250, 0.3);
}
.auth-page-foot {
    text-align: center;
    padding: 16px 24px 24px 24px;
    font-size: 11px;
    color: #475569 !important;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.auth-page-foot a {
    color: #64748b !important;
    text-decoration: none !important;
    margin: 0 6px;
}

/* Streamlit login-card wrapper */
.stApp [data-testid="stVerticalBlock"]:has(.login-card-root),
.stApp [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .login-card-root),
.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root) {
    width: 100% !important;
    max-width: 520px !important;
    padding: 44px !important;
    border-radius: 28px !important;
    background: rgba(8, 12, 30, 0.88) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    box-shadow: 0 0 70px rgba(123, 97, 255, 0.25) !important;
    box-sizing: border-box !important;
}
.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root) > [data-testid="stVerticalBlock"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
"""

_SVG_REELS = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#c4b5fd" fill="none" stroke-width="1.75"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M10 9l6 3-6 3V9z"/></svg>'
_SVG_BALL = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#c4b5fd" fill="none" stroke-width="1.75"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg>'
_SVG_ROCKET = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#c4b5fd" fill="none" stroke-width="1.75"><path d="M12 15l-3-3a22 22 0 0 1 8-10"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2"/></svg>'
_SVG_TEAM = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#c4b5fd" fill="none" stroke-width="1.75"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>'


def _widget_css() -> str:
    card = '.stApp [data-testid="stVerticalBlock"]:has(.login-card-root)'
    card_w = '.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root)'
    return f"""
{card} [data-testid="stForm"],
{card_w} [data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}}
{card} [data-testid="stWidgetLabel"],
{card_w} [data-testid="stWidgetLabel"] {{
    display: none !important;
}}
{card} [data-testid="stTextInput"],
{card} [data-testid="stNumberInput"],
{card} [data-testid="stSelectbox"],
{card_w} [data-testid="stTextInput"],
{card_w} [data-testid="stNumberInput"],
{card_w} [data-testid="stSelectbox"] {{
    margin-bottom: 10px !important;
}}
{card} div[data-baseweb="input"],
{card} div[data-baseweb="select"] > div,
{card_w} div[data-baseweb="input"],
{card_w} div[data-baseweb="select"] > div {{
    background: rgba(5, 8, 22, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
}}
{card} input,
{card_w} input {{
    background: rgba(5, 8, 22, 0.9) !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
}}
{card} input::placeholder,
{card_w} input::placeholder {{
    color: #64748b !important;
}}
{card} [data-testid="stNumberInput"] button,
{card_w} [data-testid="stNumberInput"] button {{
    background: rgba(5, 8, 22, 0.9) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    color: #94a3b8 !important;
}}
{card} [data-testid="stCheckbox"] label,
{card} [data-testid="stCheckbox"] label p,
{card} [data-testid="stCheckbox"] label span,
{card_w} [data-testid="stCheckbox"] label,
{card_w} [data-testid="stCheckbox"] label p {{
    color: #94a3b8 !important;
    font-size: 13px !important;
    background: transparent !important;
}}
{card} [data-baseweb="checkbox"],
{card_w} [data-baseweb="checkbox"] {{
    border-color: rgba(255, 255, 255, 0.14) !important;
    background: rgba(5, 8, 22, 0.9) !important;
}}

/* Primary submit */
{card} [data-testid="stFormSubmitButton"] button[kind="primary"],
{card} [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"],
{card_w} [data-testid="stFormSubmitButton"] button[kind="primary"] {{
    width: 100% !important;
    min-height: 50px !important;
    border: none !important;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #a855f7, #3b82f6) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 20px rgba(123, 97, 255, 0.35) !important;
}}
{card} [data-testid="stFormSubmitButton"] button[kind="primary"] p,
{card} [data-testid="stFormSubmitButton"] button[kind="primary"] span,
{card_w} [data-testid="stFormSubmitButton"] button[kind="primary"] p {{
    color: #ffffff !important;
    font-weight: 700 !important;
}}

/* Captcha refresh (secondary in form row) */
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button,
{card_w} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button {{
    min-height: 44px !important;
    background: rgba(5, 8, 22, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}}

/* Google link — dark */
{card} [data-testid="stLinkButton"] a,
{card_w} [data-testid="stLinkButton"] a {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 44px !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #fafafa !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}}
{card} [data-testid="stLinkButton"] a:hover,
{card_w} [data-testid="stLinkButton"] a:hover {{
    border-color: rgba(123, 97, 255, 0.4) !important;
    background: rgba(123, 97, 255, 0.1) !important;
}}

/* Register switch — text link style */
{card} [data-testid="stHorizontalBlock"]:has(.auth-register-line) .stButton > button,
{card_w} [data-testid="stHorizontalBlock"]:has(.auth-register-line) .stButton > button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #7b61ff !important;
    min-height: auto !important;
    height: auto !important;
    padding: 0 !important;
    font-weight: 600 !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.auth-register-line) .stButton > button p,
{card_w} [data-testid="stHorizontalBlock"]:has(.auth-register-line) .stButton > button p {{
    color: #7b61ff !important;
}}

/* Popover (register select) */
{card} [data-baseweb="popover"],
{card_w} [data-baseweb="popover"] {{
    background: #0a1024 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
}}
{card} [data-baseweb="popover"] li,
{card_w} [data-baseweb="popover"] li {{
    color: #e2e8f0 !important;
}}
"""


def auth_styles_bundle() -> str:
    return _BASE_CSS + _BRAND_CSS + _CARD_CSS + _widget_css()


def auth_page_marker_html() -> str:
    return '<span class="auth-page-marker" hidden aria-hidden="true"></span>'


def auth_grid_marker_html() -> str:
    """Alias for layout marker (used by pages/auth.py)."""
    return auth_page_marker_html()


def login_card_marker_html() -> str:
    return '<span class="login-card-root" hidden aria-hidden="true"></span>'


def page_open_html(mode_class: str = "") -> str:
    extra = html.escape(mode_class)
    return (
        f'<div class="auth-page {extra}"></div>'
        f'<header class="auth-topbar">'
        f'<div class="auth-topbar-brand">'
        f'<span class="auth-topbar-mark">{_INITIAL}</span>'
        f'<span>{_APP}</span></div>'
        f'<span style="color:#64748b;font-size:12px;">DE</span>'
        f'</header>'
    )


def page_close_html() -> str:
    return (
        '<footer class="auth-page-foot">'
        f'© 2026 {_APP} GmbH · '
        '<a href="#">Datenschutz</a>'
        '<a href="#">AGB</a>'
        '<a href="#">Support</a>'
        '</footer>'
    )


def panel_close_html() -> str:
    return ""


def _feat(title: str, desc: str, icon: str) -> str:
    return (
        f'<div class="auth-feat-card">'
        f'<div style="margin-bottom:8px;">{icon}</div>'
        f'<span class="t">{html.escape(title)}</span>'
        f'<span class="d">{html.escape(desc)}</span>'
        '</div>'
    )


def hero_html() -> str:
    return (
        '<div class="auth-brand">'
        f'<span class="auth-brand-name">{_APP}</span>'
        '<span class="auth-brand-kicker">AI · Football · Automation</span>'
        '<h1 class="auth-brand-title">'
        'One system.<br>'
        '<span class="accent">Infinite intelligence.</span>'
        '</h1>'
        '<p class="auth-brand-sub">'
        'Enterprise-Plattform für AI Content, Football Intelligence und Automatisierung — '
        'für Creator, Teams und Unternehmen.'
        '</p>'
        '<div class="auth-feat-grid">'
        + _feat("AI Reels Studio", "Video & Shorts mit KI", _SVG_REELS)
        + _feat("Football Intelligence", "Analyse & Prognosen", _SVG_BALL)
        + _feat("Auto Publishing", "Omnichannel aus einem Flow", _SVG_ROCKET)
        + _feat("Team Workspaces", "Gemeinsam skalieren", _SVG_TEAM)
        + '</div>'
        '</div>'
    )


def panel_shell_html(*, register: bool) -> str:
    if register:
        return (
            '<div class="login-card-head">'
            f'<div class="login-card-logo">{_INITIAL}</div>'
            '<h2 class="login-card-title">Konto erstellen</h2>'
            '<p class="login-card-sub">Registrierung für Ihren MaByte Workspace.</p>'
            '</div>'
        )
    return (
        '<div class="login-card-head">'
        f'<div class="login-card-logo">{_INITIAL}</div>'
        '<h2 class="login-card-title">Anmelden</h2>'
        '<p class="login-card-sub">Melden Sie sich in Ihrem MaByte Workspace an.</p>'
        '</div>'
    )


def forgot_password_html() -> str:
    return (
        '<a class="auth-forgot-link" href="#" onclick="return false;" '
        'title="Passwort-Reset folgt">Passwort vergessen?</a>'
    )


def oauth_divider_html() -> str:
    return '<div class="auth-divider">oder</div>'


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    lvl = html.escape(level)
    return f'<div class="auth-notice auth-notice-{lvl}" role="alert">{safe}</div>'
