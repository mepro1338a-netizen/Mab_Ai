"""MaByte B2B Premium Login — Creator + Football AI Gateway."""
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
    --background-color: #050508 !important;
    --text-color: #fafafa !important;
}
.stApp:has(.mb-auth-page),
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"],
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"] > section {
    background: #050508 !important;
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
    display: none !important;
    height: 0 !important;
}
.stApp:has(.mb-auth-page) [data-testid="stAppViewBlockContainer"],
.stApp:has(.mb-auth-page) [data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}
"""
    + _s("""
section.main .block-container {
    max-width: 1200px !important;
    padding: 0 28px 36px 28px !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] { gap: 0 !important; }
section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 3rem !important;
}
[data-testid="column"]:first-child { padding: 0 12px 0 0 !important; flex: 1.12 !important; }
[data-testid="column"]:last-child {
    padding: 0 !important; flex: 0.88 !important;
    display: flex !important; justify-content: flex-end !important;
}
[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important; max-width: 420px !important; gap: 0 !important;
}
[data-testid="column"]:last-child [data-testid="stElementContainer"],
[data-testid="column"]:last-child [data-testid="stMarkdownContainer"],
[data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    margin: 0 !important; padding: 0 !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
}
@media (max-width: 960px) {
    section.main .block-container { padding: 0 18px 28px 18px !important; }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important; gap: 2rem !important;
    }
    [data-testid="column"]:first-child,
    [data-testid="column"]:last-child { flex: 1 !important; padding: 0 !important; }
    [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] { max-width: 100% !important; }
    .mb-header-tagline { display: none !important; }
    .mb-feat-grid { grid-template-columns: 1fr !important; }
    .mb-header { margin: 0 -18px 24px -18px !important; padding: 0 18px !important; }
}
""")
    + """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.mb-auth-page {
    position: relative;
    width: 100%;
    font-family: "Inter", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Ambient + grid */
.mb-auth-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 50% 40% at 8% 10%, rgba(124, 58, 237, 0.22), transparent 55%),
        radial-gradient(ellipse 45% 35% at 92% 80%, rgba(59, 130, 246, 0.14), transparent 50%),
        radial-gradient(ellipse 30% 25% at 50% 50%, rgba(139, 92, 246, 0.06), transparent 60%),
        #050508;
}
.mb-auth-grid {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.25;
    background-image:
        linear-gradient(rgba(139, 92, 246, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(139, 92, 246, 0.05) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(ellipse 80% 70% at 40% 30%, black 15%, transparent 75%);
}

/* Header */
.mb-header {
    position: relative;
    z-index: 2;
    margin: 0 -28px 32px -28px;
    padding: 0 28px;
    border-bottom: 1px solid rgba(139, 92, 246, 0.15);
    background: rgba(8, 8, 12, 0.72);
    backdrop-filter: blur(20px) saturate(1.4);
    -webkit-backdrop-filter: blur(20px) saturate(1.4);
    box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 32px rgba(0,0,0,0.35);
}
.mb-header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 60px;
    max-width: 1200px;
    margin: 0 auto;
    gap: 16px;
}
.mb-header-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.mb-logo {
    width: 40px;
    height: 40px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(135deg, #a855f7, #6366f1);
    box-shadow: 0 0 24px rgba(124, 58, 237, 0.45), 0 0 0 1px rgba(255,255,255,0.12) inset;
}
.mb-header-text { display: flex; flex-direction: column; gap: 1px; }
.mb-header-name {
    font-size: 16px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.mb-header-tagline {
    font-size: 12px;
    font-weight: 500;
    color: #a78bfa !important;
    letter-spacing: 0.01em;
}
.mb-header-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #86efac !important;
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid rgba(34, 197, 94, 0.25);
    background: rgba(34, 197, 94, 0.08);
}
.mb-header-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.7);
}

/* Hero left */
.mb-hero {
    position: relative;
    z-index: 1;
    max-width: 560px;
}
.mb-hero-logo-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}
.mb-hero-logo-row .mb-logo { width: 36px; height: 36px; font-size: 16px; }
.mb-hero-logo-label {
    font-size: 13px;
    font-weight: 600;
    color: #e4e4e7 !important;
    letter-spacing: -0.02em;
}
.mb-hero-title {
    font-size: clamp(30px, 3.6vw, 44px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.12;
    margin: 0 0 14px 0;
    color: #fafafa !important;
}
.mb-hero-title em {
    font-style: normal;
    background: linear-gradient(90deg, #e9d5ff, #a78bfa, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.mb-hero-sub {
    font-size: 15px;
    line-height: 1.65;
    color: #a1a1aa !important;
    margin: 0 0 24px 0;
    max-width: 500px;
}
.mb-feat-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}
.mb-feat-card {
    padding: 16px 16px;
    border-radius: 14px;
    background: rgba(12, 12, 18, 0.55);
    border: 1px solid rgba(139, 92, 246, 0.18);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.2s, box-shadow 0.2s;
}
.mb-feat-card:hover {
    border-color: rgba(167, 139, 250, 0.35);
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.12), inset 0 1px 0 rgba(255,255,255,0.06);
}
.mb-feat-icon {
    font-size: 18px;
    line-height: 1;
    margin-bottom: 10px;
    display: block;
    filter: drop-shadow(0 0 8px rgba(124, 58, 237, 0.4));
}
.mb-feat-title {
    display: block;
    font-size: 13px;
    font-weight: 700;
    color: #fafafa !important;
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}
.mb-feat-desc {
    font-size: 11px;
    color: #71717a !important;
    line-height: 1.4;
}
.mb-hero-trust {
    font-size: 11px;
    color: #52525b !important;
    letter-spacing: 0.04em;
}

/* Glass login card */
.mb-glass-wrap {
    position: relative;
    z-index: 1;
}
.mb-glass-wrap::before {
    content: "";
    position: absolute;
    inset: -16px -8px;
    background: radial-gradient(ellipse at 50% 30%, rgba(124, 58, 237, 0.25), transparent 65%);
    filter: blur(28px);
    z-index: -1;
    pointer-events: none;
}
.mb-glass-card {
    border-radius: 20px;
    padding: 1px;
    background: linear-gradient(135deg, rgba(167,139,250,0.45), rgba(99,102,241,0.2), rgba(139,92,246,0.35));
    box-shadow: 0 0 40px rgba(124, 58, 237, 0.15), 0 24px 64px rgba(0,0,0,0.45);
}
.mb-glass-inner {
    border-radius: 19px;
    padding: 28px 26px 24px 26px;
    background: rgba(10, 10, 14, 0.82);
    backdrop-filter: blur(24px) saturate(1.3);
    -webkit-backdrop-filter: blur(24px) saturate(1.3);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}
.mb-panel-title {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fafafa !important;
    margin: 0 0 6px 0;
}
.mb-panel-sub {
    font-size: 13px;
    color: #71717a !important;
    margin: 0 0 20px 0;
    line-height: 1.45;
}
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 46px;
    padding: 0 16px;
    margin-bottom: 10px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    color: #fafafa !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.mb-login-google:hover {
    border-color: rgba(167, 139, 250, 0.4) !important;
    box-shadow: 0 0 24px rgba(124, 58, 237, 0.15);
}
.mb-login-google.disabled { opacity: 0.4; pointer-events: none; }
.mb-login-google .g-icon { width: 17px; height: 17px; }
.mb-login-hint {
    text-align: center;
    font-size: 10px;
    color: #52525b !important;
    margin: 0 0 14px 0;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 14px 0;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #52525b !important;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.2), transparent);
}
.mb-panel-foot {
    text-align: center;
    font-size: 10px;
    color: #52525b !important;
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
    line-height: 1.45;
}
.mb-notice {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 14px;
    backdrop-filter: blur(8px);
}
.mb-notice::before {
    flex-shrink: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    content: "";
}
.mb-notice-error {
    color: #fecaca !important;
    background: rgba(127, 29, 29, 0.35);
    border: 1px solid rgba(248, 113, 113, 0.3);
}
.mb-notice-error::before { background: #f87171; box-shadow: 0 0 8px rgba(248,113,113,0.5); }
.mb-notice-success {
    color: #bbf7d0 !important;
    background: rgba(20, 83, 45, 0.35);
    border: 1px solid rgba(74, 222, 128, 0.3);
}
.mb-notice-success::before { background: #4ade80; box-shadow: 0 0 8px rgba(74,222,128,0.5); }
.mb-notice-info {
    color: #bfdbfe !important;
    background: rgba(30, 58, 138, 0.35);
    border: 1px solid rgba(96, 165, 250, 0.3);
}
.mb-notice-info::before { background: #60a5fa; }
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
{g} label[data-testid="stWidgetLabel"] {{ display: none !important; }}
{g} [data-testid="stTextInput"],
{g} [data-testid="stNumberInput"] {{ margin-bottom: 12px !important; }}
{g} [data-testid="stTextInput"] > div,
{g} [data-testid="stTextInput"] > div > div,
{g} [data-testid="stTextInput"] fieldset,
{g} [data-testid="stNumberInput"] > div,
{g} [data-testid="stNumberInput"] > div > div {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}}
{g} div[data-baseweb="input"],
{g} [data-testid="stTextInput"] div[data-baseweb="input"],
{g} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: rgba(8, 8, 12, 0.9) !important;
    background-color: rgba(8, 8, 12, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.22) !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.35) !important;
}}
{g} div[data-baseweb="input"]:focus-within {{
    border-color: rgba(167, 139, 250, 0.65) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2), 0 0 20px rgba(124, 58, 237, 0.12) !important;
}}
{g} [data-testid="stTextInput"] input,
{g} [data-testid="stNumberInput"] input,
{g} input[type="text"],
{g} input[type="password"] {{
    background: transparent !important;
    background-color: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    font-family: inherit !important;
    caret-color: #c4b5fd !important;
}}
{g} [data-testid="stTextInput"] input::placeholder {{ color: #52525b !important; opacity: 1 !important; }}
{g} [data-testid="stTextInput"] input:-webkit-autofill,
{g} [data-testid="stTextInput"] input:-webkit-autofill:focus {{
    -webkit-box-shadow: 0 0 0 1000px #08080c inset !important;
    -webkit-text-fill-color: #fafafa !important;
}}
{g} [data-testid="stTextInput"] button {{ color: #71717a !important; background: transparent !important; }}

/* Mode tabs */
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type {{
    gap: 4px !important;
    padding: 4px !important;
    margin-bottom: 18px !important;
    background: rgba(0,0,0,0.35) !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px);
}}
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button,
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="tertiary"] {{
    min-height: 38px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    color: #71717a !important;
}}
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button p {{
    color: inherit !important; font-weight: 600 !important;
}}
{g}:has(.mb-auth-page.mb-mode-login) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:first-child > button,
{g}:has(.mb-auth-page.mb-mode-register) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:last-child > button {{
    background: linear-gradient(135deg, rgba(124,58,237,0.35), rgba(99,102,241,0.25)) !important;
    color: #fafafa !important;
    box-shadow: 0 0 16px rgba(124, 58, 237, 0.25), inset 0 1px 0 rgba(255,255,255,0.08) !important;
}}
{g}:has(.mb-auth-page.mb-mode-login) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:first-child > button p,
{g}:has(.mb-auth-page.mb-mode-register) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:last-child > button p {{
    color: #fafafa !important;
}}

/* CTA */
{g} form button,
{g} .stFormSubmitButton button {{
    width: 100% !important;
    min-height: 46px !important;
    margin-top: 4px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(167, 139, 250, 0.35) !important;
    background: linear-gradient(135deg, #9333ea, #7c3aed, #6366f1) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    font-family: inherit !important;
    box-shadow: 0 8px 28px rgba(124, 58, 237, 0.4), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    transition: box-shadow 0.2s !important;
}}
{g} form button:hover {{
    box-shadow: 0 10px 36px rgba(124, 58, 237, 0.5), inset 0 1px 0 rgba(255,255,255,0.15) !important;
}}
{g} form button p {{ color: #fff !important; font-weight: 700 !important; }}
{g} [data-testid="stAlert"] {{ display: none !important; }}
{g} [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
"""


def _logo(initial: str) -> str:
    return f'<div class="mb-logo" aria-hidden="true">{html.escape(initial)}</div>'


def header_html(mode_class: str = "") -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    extra = html.escape(mode_class)
    return (
        f'<div class="mb-auth-page {extra}">'
        f'<div class="mb-auth-bg" aria-hidden="true"></div>'
        f'<div class="mb-auth-grid" aria-hidden="true"></div>'
        f'<header class="mb-header"><div class="mb-header-inner">'
        f'<div class="mb-header-brand">'
        f'{_logo(initial)}'
        f'<div class="mb-header-text">'
        f'<span class="mb-header-name">{name}</span>'
        f'<span class="mb-header-tagline">One system. Infinite intelligence.</span>'
        f'</div></div>'
        f'<span class="mb-header-status">'
        f'<span class="mb-header-status-dot"></span>Live</span>'
        f'</div></header>'
    )


def hero_html() -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    return (
        f'<div class="mb-hero">'
        f'<div class="mb-hero-logo-row">{_logo(initial)}'
        f'<span class="mb-hero-logo-label">{name}</span></div>'
        f'<h1 class="mb-hero-title">Ein System für <em>Creator, Football &amp; Automation.</em></h1>'
        f'<p class="mb-hero-sub">Erstelle Videos, analysiere Fußball, automatisiere Content '
        f'und veröffentliche auf allen Plattformen.</p>'
        f'<div class="mb-feat-grid">'
        f'<div class="mb-feat-card"><span class="mb-feat-icon" aria-hidden="true">▶</span>'
        f'<span class="mb-feat-title">AI Reels Studio</span>'
        f'<span class="mb-feat-desc">Shorts &amp; Video mit KI-Power</span></div>'
        f'<div class="mb-feat-card"><span class="mb-feat-icon" aria-hidden="true">⚽</span>'
        f'<span class="mb-feat-title">Football Intelligence</span>'
        f'<span class="mb-feat-desc">Analyse, Insights &amp; Predictions</span></div>'
        f'<div class="mb-feat-card"><span class="mb-feat-icon" aria-hidden="true">↗</span>'
        f'<span class="mb-feat-title">Auto Publishing</span>'
        f'<span class="mb-feat-desc">Multi-Plattform in einem Flow</span></div>'
        f'<div class="mb-feat-card"><span class="mb-feat-icon" aria-hidden="true">◈</span>'
        f'<span class="mb-feat-title">Team Workspaces</span>'
        f'<span class="mb-feat-desc">Collaboration für Agenturen</span></div>'
        f'</div>'
        f'<p class="mb-hero-trust">Verschlüsselt · DSGVO-konform · Enterprise-ready</p>'
        f'</div>'
    )


def panel_shell_html(*, register: bool) -> str:
    if register:
        return (
            '<div class="mb-glass-wrap"><div class="mb-glass-card"><div class="mb-glass-inner">'
            '<h2 class="mb-panel-title">Workspace anlegen</h2>'
            '<p class="mb-panel-sub">Erstelle dein Konto und starte in Minuten.</p>'
        )
    return (
        '<div class="mb-glass-wrap"><div class="mb-glass-card"><div class="mb-glass-inner">'
        '<h2 class="mb-panel-title">Willkommen zurück</h2>'
        '<p class="mb-panel-sub">Melde dich an, um fortzufahren.</p>'
    )


def panel_close_html() -> str:
    return (
        '<div class="mb-panel-foot">256-bit TLS · Keine Passwörter bei Google · DSGVO-konform</div>'
        '</div></div></div>'
    )


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}" role="alert">{safe}</div>'


def page_close_html() -> str:
    return "</div>"


def auth_styles_bundle() -> str:
    return GATE_CSS + widget_css()
