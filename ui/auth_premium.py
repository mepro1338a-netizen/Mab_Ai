"""MaByte Auth — Enterprise login (gray zinc theme, 2-column)."""
from __future__ import annotations

import base64
import html
from pathlib import Path

from config import APP_NAME, APP_TAGLINE

_APP = html.escape(APP_NAME)
_TAGLINE = html.escape(APP_TAGLINE)
_INITIAL = html.escape(APP_NAME[:1] if APP_NAME else "M")
_ASSETS = Path("assets")
_WORDMARK = _ASSETS / "wordmark.png"

# Gray zinc app background (matches ui/b2b_theme.py)
_MB_BG = "linear-gradient(180deg, #09090b 0%, #18181b 42%, #09090b 100%)"


def _img_b64(path: Path) -> str:
    if path.is_file():
        return base64.b64encode(path.read_bytes()).decode("ascii")
    return ""


def _logo_mark(initial: str) -> str:
    return (
        f'<div class="mb-logo-mark" aria-hidden="true">{html.escape(initial)}</div>'
    )


def _topbar_logo_html() -> str:
    wm = _img_b64(_WORDMARK)
    if wm:
        return (
            f'<img class="mb-topbar-wordmark" src="data:image/png;base64,{wm}" '
            f'alt="{_APP}" />'
        )
    return _logo_mark(_INITIAL)


def _hex_logo(initial: str) -> str:
    return f'<div class="mb-panel-logo" aria-hidden="true">{html.escape(initial)}</div>'


_SVG_REELS = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<rect x="2" y="4" width="20" height="16" rx="2"/>'
    '<path d="M10 9l6 3-6 3V9z"/></svg>'
)
_SVG_BALL = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/>'
    '<path d="M12 3c2 2.5 2 6.5 0 9M12 3c-2 2.5-2 6.5 0 9M3 12h18"/>'
    '</svg>'
)
_SVG_ROCKET = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>'
    '<path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>'
    '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>'
    '</svg>'
)
_SVG_TEAM = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
    '<circle cx="9" cy="7" r="4"/>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>'
    '</svg>'
)


def _feat_card(icon: str, title: str, desc: str) -> str:
    return (
        f'<div class="mb-feat-card">'
        f'<div class="mb-feat-icon">{icon}</div>'
        f'<span class="mb-feat-title">{html.escape(title)}</span>'
        f'<span class="mb-feat-desc">{desc}</span>'
        f"</div>"
    )


_AUTH_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html { color-scheme: dark !important; }

/* ── Shell: hide Streamlit chrome, gray background ── */
.stApp:has(.mb-auth-shell),
.stApp:has(.mb-auth-shell) [data-testid="stAppViewContainer"],
.stApp:has(.mb-auth-shell) [data-testid="stAppViewContainer"] > section,
.stApp:has(.mb-auth-shell) [data-testid="stMainBlockContainer"],
.stApp:has(.mb-auth-shell) [data-testid="stAppViewBlockContainer"] {
    background: """ + _MB_BG + """ !important;
    color: #fafafa !important;
    font-family: Inter, system-ui, sans-serif !important;
}

.stApp:has(.mb-auth-shell) #MainMenu,
.stApp:has(.mb-auth-shell) footer,
.stApp:has(.mb-auth-shell) [data-testid="stToolbar"],
.stApp:has(.mb-auth-shell) [data-testid="stDecoration"],
.stApp:has(.mb-auth-shell) [data-testid="stSidebar"],
.stApp:has(.mb-auth-shell) [data-testid="stStatusWidget"],
.stApp:has(.mb-auth-shell) [data-testid="stDeployButton"],
.stApp:has(.mb-auth-shell) [data-testid="stHeader"] {
    display: none !important;
}

.stApp:has(.mb-auth-shell) [data-testid="stMain"] .block-container,
.stApp:has(.mb-auth-shell) [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    padding: 0 !important;
}

.stApp:has(.mb-auth-shell) [data-testid="stAlert"] {
    display: none !important;
}

.stApp:has(.mb-auth-shell) [data-testid="stMarkdownContainer"]:has(.mb-topbar),
.stApp:has(.mb-auth-shell) [data-testid="stMarkdownContainer"]:has(.mb-page-foot) {
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Header (classic MaByte topbar, in document flow) ── */
.mb-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 76px;
    min-height: 76px;
    padding: 0 32px;
    box-sizing: border-box;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background: linear-gradient(90deg, rgba(24, 24, 27, 0.98), rgba(39, 39, 42, 0.96));
}
.mb-topbar-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}
.mb-topbar-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
}
.mb-topbar-name {
    font-size: 18px;
    font-weight: 800;
    color: #fafafa !important;
    letter-spacing: -0.04em;
    line-height: 1.2;
    white-space: nowrap;
}
.mb-topbar-tagline {
    font-size: 11px;
    font-weight: 500;
    color: #a1a1aa !important;
    letter-spacing: 0.02em;
    white-space: nowrap;
}
.mb-topbar-wordmark {
    height: 36px;
    width: auto;
    max-width: 140px;
    object-fit: contain;
    display: block;
}
.mb-logo-mark {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 17px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(135deg, #a855f7 0%, #7c3aed 50%, #6366f1 100%);
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.35);
}
.mb-topbar-lang {
    font-size: 13px;
    font-weight: 500;
    color: #a1a1aa !important;
    padding: 8px 14px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(39, 39, 42, 0.6);
}

/* ── 2-column layout ── */
.stApp:has(.mb-auth-shell) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) 520px !important;
    align-items: center !important;
    gap: 72px !important;
    max-width: 1440px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 48px 64px 64px 64px !important;
    min-height: calc(100vh - 76px) !important;
    box-sizing: border-box !important;
}
.stApp:has(.mb-auth-shell) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:first-child {
    min-width: 0 !important;
    width: auto !important;
    max-width: none !important;
    flex: unset !important;
    padding: 0 !important;
}
.stApp:has(.mb-auth-shell) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:last-child {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 520px !important;
    flex: unset !important;
    padding: 0 !important;
    justify-self: end !important;
}

.stApp:has(.mb-mode-register) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
    grid-template-columns: 1fr !important;
    max-width: 520px !important;
    padding: 32px 24px 48px 24px !important;
}
.stApp:has(.mb-mode-register) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:first-child {
    display: none !important;
}
.stApp:has(.mb-mode-register) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:last-child {
    max-width: 100% !important;
    justify-self: center !important;
}

.stApp:has(.mb-mode-login) .mb-stats-row {
    display: none !important;
}

@media (max-width: 1100px) {
    .stApp:has(.mb-auth-shell) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
        grid-template-columns: 1fr !important;
        gap: 40px !important;
        padding: 32px 24px 48px 24px !important;
        min-height: auto !important;
    }
    .stApp:has(.mb-auth-shell) [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:last-child {
        max-width: 520px !important;
        justify-self: center !important;
    }
}

/* ── Left branding ── */
.mb-hero {
    min-width: 0;
    width: 100%;
}
.mb-hero-brand {
    display: block;
    font-size: clamp(26px, 2.5vw, 34px);
    font-weight: 900;
    letter-spacing: -0.04em;
    color: #fafafa !important;
    margin: 0 0 10px 0;
    line-height: 1.1;
    white-space: normal !important;
    word-break: normal !important;
}
.mb-hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    margin-bottom: 14px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a1a1aa !important;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(39, 39, 42, 0.55);
}
.mb-hero-pill-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #7c3aed;
}
.mb-hero-title {
    font-size: clamp(22px, 2vw, 30px);
    font-weight: 800;
    line-height: 1.25;
    margin: 0 0 12px 0;
    color: #fafafa !important;
    white-space: normal !important;
    word-break: normal !important;
}
.mb-hero-title .mb-grad {
    display: block;
    color: #c4b5fd !important;
    -webkit-text-fill-color: #c4b5fd !important;
}
.mb-hero-sub {
    font-size: 14px;
    line-height: 1.6;
    color: #a1a1aa !important;
    margin: 0 0 22px 0;
    max-width: 520px;
    white-space: normal !important;
    word-break: normal !important;
}
.mb-feat-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    max-width: 560px;
}
.mb-feat-card {
    padding: 16px 14px;
    border-radius: 14px;
    background: rgba(39, 39, 42, 0.55);
    border: 1px solid rgba(63, 63, 70, 0.7);
    box-sizing: border-box;
}
.mb-feat-icon svg {
    width: 18px;
    height: 18px;
    stroke: #a78bfa;
    fill: none;
    stroke-width: 1.75;
}
.mb-feat-title {
    display: block;
    font-size: 13px;
    font-weight: 700;
    color: #fafafa !important;
    margin: 8px 0 4px 0;
    white-space: normal !important;
}
.mb-feat-desc {
    font-size: 11px;
    color: #71717a !important;
    line-height: 1.4;
    white-space: normal !important;
}

/* ── Login card (HTML head) ── */
.mb-login-head {
    text-align: center;
    margin-bottom: 22px;
}
.mb-panel-logo {
    width: 42px;
    height: 42px;
    margin: 0 auto 14px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, #a855f7, #7c3aed, #6366f1);
    font-size: 16px;
    font-weight: 800;
    color: #fff !important;
}
.mb-panel-title {
    font-size: 22px;
    font-weight: 700;
    color: #fafafa !important;
    margin: 0 0 6px 0;
    line-height: 1.25;
    text-align: center;
    white-space: normal !important;
    word-break: normal !important;
}
.mb-panel-title .mb-panel-brand {
    color: #c4b5fd !important;
}
.mb-panel-sub {
    font-size: 13px;
    color: #a1a1aa !important;
    margin: 0;
    line-height: 1.45;
    text-align: center;
    white-space: normal !important;
}
.mb-field-label,
.auth-field-label {
    display: block !important;
    color: #d4d4d8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    margin: 12px 0 6px 0 !important;
    white-space: normal !important;
}
.mb-captcha-label,
.auth-captcha-label {
    display: block !important;
    color: #a1a1aa !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    margin: 14px 0 8px 0 !important;
    white-space: normal !important;
}
.mb-forgot-link,
.auth-forgot-link {
    font-size: 13px;
    font-weight: 500;
    color: #a78bfa !important;
    text-decoration: none !important;
    white-space: nowrap !important;
}
.mb-login-divider,
.auth-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 18px 0 14px 0;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #71717a !important;
}
.mb-login-divider::before,
.mb-login-divider::after,
.auth-divider::before,
.auth-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
}
.mb-panel-switch-note,
.auth-register-line {
    text-align: center;
    margin: 16px 0 6px 0;
    font-size: 14px;
    color: #71717a !important;
    white-space: normal !important;
}
.mb-notice,
.auth-notice {
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 14px;
    white-space: normal !important;
    word-break: normal !important;
}
.mb-notice-error, .auth-notice-error {
    color: #fecaca !important;
    background: rgba(127, 29, 29, 0.35);
    border: 1px solid rgba(248, 113, 113, 0.3);
}
.mb-notice-success, .auth-notice-success {
    color: #bbf7d0 !important;
    background: rgba(20, 83, 45, 0.35);
    border: 1px solid rgba(74, 222, 128, 0.3);
}
.mb-notice-info, .auth-notice-info {
    color: #bfdbfe !important;
    background: rgba(30, 58, 138, 0.35);
    border: 1px solid rgba(96, 165, 250, 0.3);
}
.mb-page-foot {
    text-align: center;
    padding: 20px 24px 28px 24px;
    font-size: 11px;
    color: #71717a !important;
    border-top: 1px solid rgba(63, 63, 70, 0.5);
    background: rgba(9, 9, 11, 0.6);
}
.mb-page-foot a {
    color: #a1a1aa !important;
    text-decoration: none !important;
    margin: 0 8px;
}
.mb-page-foot-sep {
    color: #52525b !important;
}

/* Streamlit card wrapper */
.stApp:has(.mb-auth-shell) [data-testid="stVerticalBlock"]:has(.login-card-root),
.stApp:has(.mb-auth-shell) [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root) {
    width: 100% !important;
    max-width: 520px !important;
    padding: 44px !important;
    border-radius: 20px !important;
    background: rgba(24, 24, 27, 0.96) !important;
    border: 1px solid rgba(63, 63, 70, 0.9) !important;
    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.45) !important;
    box-sizing: border-box !important;
}
.stApp:has(.mb-auth-shell) [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root) > [data-testid="stVerticalBlock"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

@media (max-width: 640px) {
    .mb-feat-grid { grid-template-columns: 1fr !important; }
    .stApp:has(.mb-auth-shell) [data-testid="stVerticalBlock"]:has(.login-card-root),
    .stApp:has(.mb-auth-shell) [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root) {
        padding: 32px 24px !important;
    }
}
"""


def _widget_css() -> str:
    c = '.stApp:has(.mb-auth-shell) [data-testid="stVerticalBlock"]:has(.login-card-root)'
    w = '.stApp:has(.mb-auth-shell) [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-root)'
    return f"""
{c} [data-testid="stForm"], {w} [data-testid="stForm"] {{
    border: none !important; padding: 0 !important; background: transparent !important;
}}
{c} [data-testid="stWidgetLabel"], {w} [data-testid="stWidgetLabel"] {{ display: none !important; }}
{c} [data-testid="stTextInput"], {c} [data-testid="stNumberInput"], {c} [data-testid="stSelectbox"],
{w} [data-testid="stTextInput"], {w} [data-testid="stNumberInput"], {w} [data-testid="stSelectbox"] {{
    margin-bottom: 10px !important;
}}
{c} div[data-baseweb="input"], {c} div[data-baseweb="select"] > div,
{w} div[data-baseweb="input"], {w} div[data-baseweb="select"] > div {{
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 12px !important;
    min-height: 44px !important;
}}
{c} input, {w} input {{
    background: #27272a !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
}}
{c} input::placeholder, {w} input::placeholder {{ color: #71717a !important; }}
{c} [data-testid="stNumberInput"] button, {w} [data-testid="stNumberInput"] button {{
    background: #27272a !important;
    border-color: #3f3f46 !important;
    color: #a1a1aa !important;
}}
{c} [data-testid="stTextInput"] button, {w} [data-testid="stTextInput"] button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #a1a1aa !important;
    min-width: 36px !important;
    width: 36px !important;
}}
{c} [data-testid="stTextInput"] button svg, {w} [data-testid="stTextInput"] button svg {{
    fill: #a1a1aa !important;
}}
{c} [data-testid="stCheckbox"] label, {c} [data-testid="stCheckbox"] label p,
{w} [data-testid="stCheckbox"] label, {w} [data-testid="stCheckbox"] label p {{
    color: #a1a1aa !important; font-size: 13px !important; background: transparent !important;
}}
{c} [data-baseweb="checkbox"], {w} [data-baseweb="checkbox"] {{
    border-color: #52525b !important; background: #27272a !important;
}}

{c} [data-testid="stFormSubmitButton"] button[kind="primary"],
{c} [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"],
{w} [data-testid="stFormSubmitButton"] button[kind="primary"] {{
    width: 100% !important;
    min-height: 50px !important;
    border: none !important;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #a855f7, #3b82f6) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 18px rgba(124, 58, 237, 0.35) !important;
}}
{c} [data-testid="stFormSubmitButton"] button[kind="primary"] p,
{w} [data-testid="stFormSubmitButton"] button[kind="primary"] p {{
    color: #ffffff !important; font-weight: 700 !important;
}}

{c} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button,
{w} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button {{
    min-height: 44px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}}

{c} [data-testid="stLinkButton"] a, {w} [data-testid="stLinkButton"] a {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 44px !important;
    border-radius: 12px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #fafafa !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}}
{c} [data-testid="stLinkButton"] a:hover, {w} [data-testid="stLinkButton"] a:hover {{
    border-color: #52525b !important;
    background: #3f3f46 !important;
}}

{c} .stButton > button, {w} .stButton > button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #a78bfa !important;
    min-height: auto !important;
    height: auto !important;
    padding: 4px 0 !important;
}}
{c} .stButton > button p, {w} .stButton > button p {{ color: #a78bfa !important; font-weight: 600 !important; }}

{c} [data-baseweb="popover"], {w} [data-baseweb="popover"] {{
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
}}
{c} [data-baseweb="popover"] li, {w} [data-baseweb="popover"] li {{ color: #e4e4e7 !important; }}
"""


def auth_styles_bundle() -> str:
    return _AUTH_CSS + _widget_css()


def auth_page_marker_html() -> str:
    return auth_grid_marker_html()


def auth_grid_marker_html() -> str:
    return '<span class="auth-grid-marker" hidden aria-hidden="true"></span>'


def login_card_marker_html() -> str:
    return '<span class="login-card-root" hidden aria-hidden="true"></span>'


def page_open_html(mode_class: str = "") -> str:
    extra = html.escape(mode_class)
    return (
        f'<div class="mb-auth-shell {extra}"></div>'
        f'<header class="mb-topbar">'
        f'<div class="mb-topbar-brand">{_topbar_logo_html()}'
        f'<div class="mb-topbar-text">'
        f'<span class="mb-topbar-name">{_APP}</span>'
        f'<span class="mb-topbar-tagline">Enterprise AI Platform</span>'
        f"</div></div>"
        f'<span class="mb-topbar-lang">DE</span>'
        f"</header>"
    )


def page_close_html() -> str:
    return (
        '<footer class="mb-page-foot">'
        f"<span>© 2026 {_APP} GmbH · Alle Rechte vorbehalten.</span>"
        '<div class="mb-page-foot-links">'
        '<a href="#">Datenschutz</a><span class="mb-page-foot-sep">|</span>'
        '<a href="#">AGB</a><span class="mb-page-foot-sep">|</span>'
        '<a href="#">Impressum</a><span class="mb-page-foot-sep">|</span>'
        '<a href="#">Support</a>'
        "</div></footer>"
    )


def panel_close_html() -> str:
    return ""


def hero_html() -> str:
    return (
        '<div class="mb-hero">'
        f'<span class="mb-hero-brand">{_APP}</span>'
        '<div class="mb-hero-pill"><span class="mb-hero-pill-dot"></span>'
        "AI · FOOTBALL · AUTOMATION</div>"
        '<h1 class="mb-hero-title">'
        "One system.<br>"
        '<span class="mb-grad">Infinite intelligence.</span>'
        "</h1>"
        '<p class="mb-hero-sub">'
        "Die Enterprise-Plattform für AI-gestützte Content-Produktion, "
        "Football Intelligence und skalierbare Automatisierung."
        "</p>"
        '<div class="mb-feat-grid">'
        + _feat_card(_SVG_REELS, "AI Reels Studio", "Video &amp; Shorts mit KI")
        + _feat_card(_SVG_BALL, "Football Intelligence", "Analyse &amp; Prognosen")
        + _feat_card(_SVG_ROCKET, "Auto Publishing", "Omnichannel aus einem Flow")
        + _feat_card(_SVG_TEAM, "Team Workspaces", "Gemeinsam skalieren")
        + "</div>"
        "</div>"
    )


def panel_shell_html(*, register: bool) -> str:
    if register:
        return (
            '<div class="mb-login-head">'
            f"{_hex_logo(_INITIAL)}"
            '<h2 class="mb-panel-title">Konto bei <span class="mb-panel-brand">MaByte</span> erstellen</h2>'
            '<p class="mb-panel-sub">E-Mail-Registrierung — Zugang zu AI, Football &amp; Creator Tools.</p>'
            "</div>"
        )
    return (
        '<div class="mb-login-head">'
        f"{_hex_logo(_INITIAL)}"
        '<h2 class="mb-panel-title">Anmelden</h2>'
        '<p class="mb-panel-sub">Melden Sie sich in Ihrem MaByte Workspace an.</p>'
        "</div>"
    )


def forgot_password_html() -> str:
    return (
        '<a class="mb-forgot-link" href="#" onclick="return false;" '
        'title="Passwort-Reset folgt">Passwort vergessen?</a>'
    )


def oauth_divider_html() -> str:
    return '<div class="mb-login-divider">oder</div>'


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}" role="alert">{safe}</div>'
