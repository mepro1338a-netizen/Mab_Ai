"""MaByte Login — Enterprise B2B Gateway (Deutsch, Streamlit-safe)."""
from __future__ import annotations

import html

from config import APP_NAME
from ui.b2b_theme import MB_THEME_VARS

_G = ".stApp:has(.mb-auth-page)"


def _s(css: str) -> str:
    return _G + " " + css


GATE_CSS = (
    MB_THEME_VARS
    + """
html { color-scheme: dark !important; }
.stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
    --primary-color: #7c3aed !important;
    --background-color: #09090b !important;
    --text-color: #fafafa !important;
}
.stApp:has(.mb-auth-page),
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"],
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"] > section {
    background: #09090b !important;
}
.stApp:has(.mb-auth-page) #MainMenu,
.stApp:has(.mb-auth-page) footer,
.stApp:has(.mb-auth-page) [data-testid="stToolbar"],
.stApp:has(.mb-auth-page) [data-testid="stDecoration"],
.stApp:has(.mb-auth-page) [data-testid="stSidebar"],
.stApp:has(.mb-auth-page) [data-testid="stStatusWidget"],
.stApp:has(.mb-auth-page) [data-testid="stDeployButton"],
.stApp:has(.mb-auth-page) [data-testid="stElementToolbar"],
.stApp:has(.mb-auth-page) [data-testid="stHeader"] {
    display: none !important; height: 0 !important;
}
.stApp:has(.mb-auth-page) [data-testid="stAppViewBlockContainer"],
.stApp:has(.mb-auth-page) [data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}
"""
    + _s("""
section.main .block-container {
    max-width: 1140px !important;
    padding: 0 32px 40px 32px !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] { gap: 0 !important; }
section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 4rem !important;
}
[data-testid="column"]:first-child { padding: 0 16px 0 0 !important; flex: 1.1 !important; }
[data-testid="column"]:last-child {
    padding: 0 !important; flex: 0.9 !important;
    display: flex !important; justify-content: flex-end !important;
}
[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important; max-width: 400px !important; gap: 0 !important;
}
[data-testid="column"]:last-child [data-testid="stElementContainer"],
[data-testid="column"]:last-child [data-testid="stMarkdownContainer"],
[data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    margin: 0 !important; padding: 0 !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
}
@media (max-width: 900px) {
    section.main .block-container { padding: 0 20px 32px 20px !important; }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important; gap: 2.5rem !important;
    }
    .mb-nav { display: none !important; }
    .mb-topbar { margin: 0 -20px 28px -20px !important; padding: 0 20px !important; }
}
""")
    + """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.mb-auth-page {
    position: relative;
    width: 100%;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-feature-settings: "cv11", "ss01";
    -webkit-font-smoothing: antialiased;
    color: #fafafa;
}

/* Subtle depth — no disco */
.mb-auth-page::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 60% 45% at 0% 0%, rgba(124, 58, 237, 0.07), transparent 55%),
        radial-gradient(ellipse 40% 35% at 100% 100%, rgba(99, 102, 241, 0.04), transparent 50%),
        #09090b;
}

/* —— Top bar —— */
.mb-topbar {
    position: relative;
    z-index: 2;
    margin: 0 -32px 40px -32px;
    padding: 0 32px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(9, 9, 11, 0.8);
    backdrop-filter: blur(12px);
}
.mb-topbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 56px;
    max-width: 1140px;
    margin: 0 auto;
}
.mb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.mb-brand-mark {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    color: #fff !important;
    background: #7c3aed;
    box-shadow: 0 1px 2px rgba(0,0,0,0.4);
}
.mb-brand-name {
    font-size: 14px;
    font-weight: 600;
    color: #fafafa !important;
    letter-spacing: -0.02em;
}
.mb-nav {
    display: flex;
    gap: 28px;
}
.mb-nav span {
    font-size: 13px;
    font-weight: 500;
    color: #71717a !important;
}
.mb-nav span.is-active {
    color: #e4e4e7 !important;
}
.mb-topbar-meta {
    font-size: 12px;
    font-weight: 500;
    color: #52525b !important;
    letter-spacing: 0.02em;
}

/* —— Hero —— */
.mb-hero {
    position: relative;
    z-index: 1;
    max-width: 520px;
    padding-top: 4px;
}
.mb-hero-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #71717a !important;
    margin: 0 0 12px 0;
}
.mb-hero-title {
    font-size: clamp(32px, 3.5vw, 42px);
    font-weight: 700;
    letter-spacing: -0.035em;
    line-height: 1.15;
    margin: 0 0 16px 0;
    color: #fafafa !important;
}
.mb-hero-title span {
    color: #a78bfa !important;
}
.mb-hero-text {
    font-size: 16px;
    line-height: 1.65;
    color: #a1a1aa !important;
    margin: 0 0 28px 0;
    max-width: 480px;
}
.mb-hero-text strong {
    color: #e4e4e7 !important;
    font-weight: 600;
}
.mb-hero-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.02);
    margin-bottom: 24px;
}
.mb-hero-strip-item {
    flex: 1;
    min-width: 120px;
    padding: 16px 18px;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
.mb-hero-strip-item:last-child {
    border-right: none;
}
.mb-hero-strip-item b {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #fafafa !important;
    margin-bottom: 2px;
    letter-spacing: -0.01em;
}
.mb-hero-strip-item span {
    font-size: 12px;
    color: #71717a !important;
    line-height: 1.35;
}
.mb-hero-proof {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: #52525b !important;
}
.mb-hero-proof-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    flex-shrink: 0;
}

/* —— Auth panel —— */
.mb-auth-panel {
    position: relative;
    z-index: 1;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(12, 12, 14, 0.95);
    box-shadow:
        0 0 0 1px rgba(0, 0, 0, 0.4),
        0 24px 48px rgba(0, 0, 0, 0.4);
}
.mb-auth-panel-inner {
    padding: 28px 28px 24px 28px;
}
.mb-auth-panel-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #71717a !important;
    margin: 0 0 6px 0;
}
.mb-auth-panel-title {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.025em;
    color: #fafafa !important;
    margin: 0 0 6px 0;
    line-height: 1.25;
}
.mb-auth-panel-sub {
    font-size: 13px;
    color: #71717a !important;
    margin: 0 0 22px 0;
    line-height: 1.5;
}
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 44px;
    padding: 0 16px;
    margin-bottom: 12px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    color: #fafafa !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: background 0.15s, border-color 0.15s;
}
.mb-login-google:hover {
    background: rgba(255, 255, 255, 0.07) !important;
    border-color: rgba(255, 255, 255, 0.14) !important;
}
.mb-login-google.disabled { opacity: 0.45; pointer-events: none; }
.mb-login-google .g-icon { width: 16px; height: 16px; }
.mb-login-hint {
    text-align: center;
    font-size: 11px;
    color: #52525b !important;
    margin: 0 0 16px 0;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 16px 0;
    font-size: 11px;
    font-weight: 500;
    color: #52525b !important;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255, 255, 255, 0.06);
}
.mb-auth-foot {
    text-align: center;
    font-size: 11px;
    color: #52525b !important;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    line-height: 1.45;
}
.mb-notice {
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 13px;
    margin-bottom: 14px;
    line-height: 1.4;
}
.mb-notice-error {
    color: #fca5a5 !important;
    background: rgba(127, 29, 29, 0.25);
    border: 1px solid rgba(248, 113, 113, 0.25);
}
.mb-notice-success {
    color: #86efac !important;
    background: rgba(20, 83, 45, 0.25);
    border: 1px solid rgba(74, 222, 128, 0.25);
}
.mb-notice-info {
    color: #93c5fd !important;
    background: rgba(30, 58, 138, 0.25);
    border: 1px solid rgba(96, 165, 250, 0.25);
}
.mb-captcha-label {
    font-size: 12px;
    color: #71717a !important;
    margin: 0 0 8px 0;
}
"""
)


def widget_css() -> str:
    g = _G
    return f"""
{g} [data-testid="stForm"] {{
    border: none !important; padding: 0 !important; background: transparent !important;
}}
{g} [data-testid="stWidgetLabel"],
{g} label[data-testid="stWidgetLabel"] {{
    display: none !important;
}}
{g} [data-testid="stTextInput"],
{g} [data-testid="stNumberInput"] {{
    margin-bottom: 12px !important;
}}
{g} [data-testid="stTextInput"] > div,
{g} [data-testid="stTextInput"] > div > div,
{g} [data-testid="stTextInput"] fieldset,
{g} [data-testid="stNumberInput"] > div {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}}
{g} div[data-baseweb="input"],
{g} [data-testid="stTextInput"] div[data-baseweb="input"],
{g} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: #18181b !important;
    background-color: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    box-shadow: none !important;
}}
{g} div[data-baseweb="input"]:focus-within {{
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
}}
{g} [data-testid="stTextInput"] input,
{g} [data-testid="stNumberInput"] input {{
    background: transparent !important;
    background-color: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    font-family: inherit !important;
}}
{g} [data-testid="stTextInput"] input::placeholder {{
    color: #52525b !important;
    opacity: 1 !important;
}}
{g} [data-testid="stTextInput"] input:-webkit-autofill {{
    -webkit-box-shadow: 0 0 0 1000px #18181b inset !important;
    -webkit-text-fill-color: #fafafa !important;
}}
{g} [data-testid="stTextInput"] button {{
    color: #71717a !important;
    background: transparent !important;
}}

/* Mode switch */
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type {{
    gap: 0 !important;
    padding: 3px !important;
    margin-bottom: 18px !important;
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
}}
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button,
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="tertiary"] {{
    min-height: 36px !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    color: #71717a !important;
}}
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button p {{
    color: inherit !important;
    font-weight: 600 !important;
}}
{g}:has(.mb-auth-page.mb-mode-login) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:first-child > button,
{g}:has(.mb-auth-page.mb-mode-register) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:last-child > button {{
    background: #27272a !important;
    color: #fafafa !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06) !important;
}}
{g}:has(.mb-auth-page.mb-mode-login) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:first-child > button p,
{g}:has(.mb-auth-page.mb-mode-register) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:last-child > button p {{
    color: #fafafa !important;
}}

/* Submit — solid, no shimmer */
{g} form button,
{g} .stFormSubmitButton button {{
    width: 100% !important;
    min-height: 44px !important;
    margin-top: 4px !important;
    border-radius: 10px !important;
    border: none !important;
    background: #7c3aed !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    font-family: inherit !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    transition: background 0.15s !important;
}}
{g} form button:hover {{
    background: #6d28d9 !important;
}}
{g} form button p {{
    color: #fff !important;
    font-weight: 600 !important;
}}
{g} .mb-captcha-row form button {{
    width: auto !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    box-shadow: none !important;
}}
{g} [data-testid="stAlert"] {{ display: none !important; }}
{g} [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
"""


def header_html(mode_class: str = "") -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    extra = html.escape(mode_class)
    return (
        f'<div class="mb-auth-page {extra}">'
        f'<header class="mb-topbar"><div class="mb-topbar-inner">'
        f'<div class="mb-brand">'
        f'<div class="mb-brand-mark" aria-hidden="true">{initial}</div>'
        f'<span class="mb-brand-name">{name}</span></div>'
        f'<nav class="mb-nav" aria-label="Navigation">'
        f'<span class="is-active">Produkt</span><span>Preise</span><span>Unternehmen</span></nav>'
        f'<span class="mb-topbar-meta">Enterprise-ready</span>'
        f'</div></header>'
    )


def hero_html() -> str:
    name = html.escape(APP_NAME)
    return (
        f'<div class="mb-hero">'
        f'<p class="mb-hero-label">Creator Operating System</p>'
        f'<h1 class="mb-hero-title">Eine Plattform für <span>professionelle</span> Creator-Produktion.</h1>'
        f'<p class="mb-hero-text"><strong>{name}</strong> bündelt Video, KI, Bild und Code '
        f'in einem Workspace — gebaut für Selbstständige, Agenturen und Teams, die ernsthaft skalieren wollen.</p>'
        f'<div class="mb-hero-strip">'
        f'<div class="mb-hero-strip-item"><b>Video &amp; Shorts</b><span>Erstellen bis Veröffentlichung</span></div>'
        f'<div class="mb-hero-strip-item"><b>KI-Studio</b><span>Chat, Bild, Code</span></div>'
        f'<div class="mb-hero-strip-item"><b>Fair Pricing</b><span>Nutzungsbasiert</span></div>'
        f'</div>'
        f'<div class="mb-hero-proof">'
        f'<span class="mb-hero-proof-dot"></span>'
        f'<span>Verschlüsselt · DSGVO-konform · Made in Germany</span></div>'
        f'</div>'
    )


def panel_shell_html(*, register: bool) -> str:
    if register:
        return (
            '<div class="mb-auth-panel"><div class="mb-auth-panel-inner">'
            '<p class="mb-auth-panel-label">Registrierung</p>'
            '<h2 class="mb-auth-panel-title">Workspace anlegen</h2>'
            '<p class="mb-auth-panel-sub">Konto erstellen und direkt mit der Produktion starten.</p>'
        )
    return (
        '<div class="mb-auth-panel"><div class="mb-auth-panel-inner">'
        '<p class="mb-auth-panel-label">Anmeldung</p>'
        '<h2 class="mb-auth-panel-title">In deinen Workspace</h2>'
        '<p class="mb-auth-panel-sub">Melde dich an, um fortzufahren.</p>'
    )


def panel_close_html() -> str:
    return (
        '<div class="mb-auth-foot">'
        '256-bit TLS · Keine Passwörter bei Google · DSGVO-konform'
        '</div></div></div>'
    )


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}">{safe}</div>'


def page_close_html() -> str:
    return "</div>"


def auth_styles_bundle() -> str:
    return GATE_CSS + widget_css()
