"""MaByte Login — Premium Gateway, minimal Streamlit footprint."""
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
    padding: 0 24px 32px 24px !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] { gap: 0 !important; }
section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 2rem !important;
}
[data-testid="column"]:first-child { padding: 0 8px 0 0 !important; flex: 1.05 !important; }
[data-testid="column"]:last-child {
    padding: 0 !important;
    flex: 0.95 !important;
    display: flex !important;
    justify-content: flex-end !important;
}
[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 420px !important;
    gap: 0 !important;
}
[data-testid="column"]:last-child [data-testid="stElementContainer"],
[data-testid="column"]:last-child [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
@media (max-width: 900px) {
    section.main .block-container { padding: 0 16px 24px 16px !important; }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    .mb-auth-nav { display: none !important; }
    .mb-auth-header { margin: 0 -16px 24px -16px !important; padding: 0 16px !important; }
}
""")
    + """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&display=swap');

.mb-auth-page {
    position: relative;
    width: 100%;
    font-family: "Inter", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}
.mb-auth-aurora {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 45% 35% at 10% 8%, rgba(124,58,237,0.28), transparent 55%),
        radial-gradient(ellipse 35% 30% at 90% 85%, rgba(99,102,241,0.12), transparent 50%),
        #09090b;
}

/* Header */
.mb-auth-header {
    position: relative;
    z-index: 2;
    margin: 0 -24px 28px -24px;
    padding: 0 24px;
    border-bottom: 1px solid rgba(167,139,250,0.12);
    background: rgba(9,9,11,0.85);
    backdrop-filter: blur(18px);
}
.mb-auth-header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 58px;
    max-width: 1200px;
    margin: 0 auto;
    gap: 16px;
}
.mb-auth-header-brand { display: flex; align-items: center; gap: 11px; }
.mb-auth-mark {
    width: 38px; height: 38px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; font-weight: 800; color: #fff !important;
    background: linear-gradient(145deg, #e9d5ff, #7c3aed, #5b21b6);
    box-shadow: 0 6px 24px rgba(124,58,237,0.45);
}
.mb-auth-header-name {
    font-size: 15px; font-weight: 700; color: #fafafa !important;
    letter-spacing: -0.02em; white-space: nowrap;
}
.mb-auth-header-tag {
    font-size: 11px; color: #71717a !important; white-space: nowrap;
}
.mb-auth-nav { display: flex; gap: 24px; }
.mb-auth-nav span { font-size: 13px; color: #71717a !important; white-space: nowrap; }
.mb-auth-nav span:first-child { color: #e4e4e7 !important; }
.mb-auth-header-actions { display: flex; align-items: center; gap: 10px; }
.mb-auth-header-badge {
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #a78bfa !important;
    padding: 5px 9px; border-radius: 7px;
    border: 1px solid rgba(167,139,250,0.3);
    background: rgba(124,58,237,0.1); white-space: nowrap;
}
.mb-auth-header-cta {
    font-size: 12px; font-weight: 700; color: #fff !important;
    padding: 8px 14px; border-radius: 9px; white-space: nowrap;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    box-shadow: 0 4px 18px rgba(124,58,237,0.45);
}

/* Hero — kompakt, wenig Umbrüche */
.mb-auth-hero { position: relative; z-index: 1; max-width: 540px; }
.mb-auth-eyebrow {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 5px 12px 5px 9px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #c4b5fd !important;
    background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.25);
    margin-bottom: 16px; white-space: nowrap;
}
.mb-auth-eyebrow-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #a78bfa; box-shadow: 0 0 8px #7c3aed;
}
.mb-auth-headline {
    font-size: clamp(30px, 3.6vw, 44px);
    font-weight: 800; letter-spacing: -0.04em;
    line-height: 1.12; margin: 0 0 14px 0;
    color: #fafafa !important;
}
.mb-auth-headline em {
    font-style: normal;
    background: linear-gradient(90deg, #f0abfc, #a78bfa, #7c3aed);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.mb-auth-lead {
    font-size: 15px; line-height: 1.6; color: #d4d4d8 !important;
    margin: 0 0 20px 0; max-width: 500px;
}
.mb-auth-lead strong { color: #fff !important; }
.mb-auth-feats {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px;
}
.mb-auth-feat {
    flex: 1 1 calc(50% - 4px); min-width: 200px;
    padding: 14px 14px; border-radius: 14px;
    background: linear-gradient(160deg, rgba(30,27,45,0.85), rgba(12,12,16,0.95));
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 28px rgba(0,0,0,0.3);
}
.mb-auth-feat b {
    display: block; font-size: 13px; font-weight: 700;
    color: #fafafa !important; margin-bottom: 3px;
}
.mb-auth-feat span { font-size: 11px; color: #a1a1aa !important; line-height: 1.4; }
.mb-auth-manifest {
    padding: 14px 16px; border-radius: 14px;
    border: 1px solid rgba(167,139,250,0.2);
    background: rgba(124,58,237,0.08);
    font-size: 13px; color: #d4d4d8 !important;
    line-height: 1.5; font-style: italic;
}

/* Access card */
.mb-access-card {
    position: relative; z-index: 1;
    border-radius: 22px; padding: 1px;
    background: linear-gradient(145deg, rgba(196,181,253,0.55), rgba(124,58,237,0.2), rgba(63,63,70,0.4));
    box-shadow: 0 28px 70px rgba(0,0,0,0.55), 0 0 80px rgba(124,58,237,0.12);
}
.mb-access-card-inner {
    border-radius: 21px;
    padding: 26px 24px 22px 24px;
    background: linear-gradient(180deg, rgba(14,14,18,0.98), rgba(8,8,10,0.99));
    backdrop-filter: blur(24px);
}
.mb-access-top {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 18px; padding-bottom: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 10px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase;
}
.mb-access-live { color: #86efac !important; }
.mb-access-live::before {
    content: ""; display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: #22c55e; margin-right: 6px;
    box-shadow: 0 0 8px rgba(34,197,94,0.6); vertical-align: middle;
}
.mb-access-tag { color: #52525b !important; }
.mb-panel-kicker {
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #a78bfa !important; margin: 0 0 5px 0;
}
.mb-panel-head h2 {
    font-size: 22px; font-weight: 800; color: #fafafa !important;
    letter-spacing: -0.03em; margin: 0 0 5px 0; line-height: 1.15;
}
.mb-panel-head p {
    font-size: 13px; color: #a1a1aa !important; margin: 0 0 18px 0; line-height: 1.45;
}
.mb-login-google {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    width: 100%; min-height: 46px; padding: 0 16px; margin-bottom: 10px;
    border-radius: 12px; font-size: 13px; font-weight: 700;
    text-decoration: none !important; color: #fafafa !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.mb-login-google:hover {
    border-color: rgba(167,139,250,0.45) !important;
    box-shadow: 0 0 28px rgba(124,58,237,0.15);
}
.mb-login-google.disabled { opacity: 0.4; pointer-events: none; }
.mb-login-google .g-icon { width: 17px; height: 17px; }
.mb-login-hint {
    text-align: center; font-size: 10px; color: #52525b !important; margin: 0 0 14px 0;
}
.mb-login-divider {
    display: flex; align-items: center; gap: 10px; margin: 0 0 14px 0;
    font-size: 10px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #52525b !important;
}
.mb-login-divider::before, .mb-login-divider::after {
    content: ""; flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}
.mb-panel-foot {
    text-align: center; font-size: 10px; color: #52525b !important;
    margin-top: 16px; padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.mb-notice {
    padding: 10px 12px; border-radius: 10px; font-size: 12px; margin-bottom: 12px;
}
.mb-notice-error { color: #fecaca !important; background: rgba(127,29,29,0.35); border: 1px solid rgba(248,113,113,0.3); }
.mb-notice-success { color: #bbf7d0 !important; background: rgba(20,83,45,0.35); border: 1px solid rgba(74,222,128,0.3); }
.mb-notice-info { color: #bfdbfe !important; background: rgba(30,58,138,0.3); border: 1px solid rgba(96,165,250,0.3); }
.mb-captcha-label {
    font-size: 11px; color: #71717a !important; margin: 0 0 6px 2px;
}
"""
)


def widget_css() -> str:
    g = _G
    return f"""
/* Streamlit chrome kill */
{g} [data-testid="stForm"] {{
    border: none !important; padding: 0 !important; background: transparent !important;
}}
{g} [data-testid="stWidgetLabel"],
{g} label[data-testid="stWidgetLabel"] {{
    display: none !important; height: 0 !important; margin: 0 !important;
}}
{g} [data-testid="stTextInput"],
{g} [data-testid="stNumberInput"] {{
    margin-bottom: 12px !important;
}}
{g} [data-testid="stTextInput"] > div,
{g} [data-testid="stTextInput"] fieldset,
{g} [data-testid="stNumberInput"] > div {{
    background: transparent !important; border: none !important; padding: 0 !important;
}}
{g} [data-testid="stTextInput"] div[data-baseweb="input"],
{g} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3) !important;
}}
{g} [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
    border-color: rgba(167,139,250,0.55) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
}}
{g} [data-testid="stTextInput"] input,
{g} [data-testid="stNumberInput"] input {{
    color: #fafafa !important; -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important; font-family: inherit !important;
}}
{g} [data-testid="stTextInput"] input::placeholder {{ color: #52525b !important; opacity: 1 !important; }}
{g} [data-testid="stTextInput"] input:-webkit-autofill {{
    -webkit-box-shadow: 0 0 0 1000px #0c0c0e inset !important;
    -webkit-text-fill-color: #fafafa !important;
}}
{g} [data-testid="stTextInput"] button {{ color: #71717a !important; background: transparent !important; }}

/* Mode tabs — first 2-col row in panel */
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type {{
    gap: 4px !important; padding: 4px !important; margin-bottom: 16px !important;
    background: rgba(0,0,0,0.45) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}}
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button,
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="tertiary"] {{
    min-height: 38px !important; border-radius: 9px !important;
    font-size: 13px !important; font-weight: 700 !important;
    border: none !important; box-shadow: none !important;
    background: transparent !important; color: #52525b !important;
}}
{g} [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton > button p {{
    color: inherit !important; font-weight: 700 !important;
}}
{g}:has(.mb-auth-page.mb-mode-login) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:first-child > button,
{g}:has(.mb-auth-page.mb-mode-register) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:last-child > button {{
    background: linear-gradient(135deg, #a855f7, #7c3aed) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.4) !important;
}}
{g}:has(.mb-auth-page.mb-mode-login) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:first-child > button p,
{g}:has(.mb-auth-page.mb-mode-register) [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type .stButton:last-child > button p {{
    color: #fff !important;
}}

/* Submit */
{g} .stFormSubmitButton,
{g} [data-testid="stFormSubmitButton"] {{
    margin-top: 4px !important;
}}
{g} form button,
{g} .stFormSubmitButton button {{
    width: 100% !important; min-height: 48px !important;
    border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.12) !important;
    background: linear-gradient(135deg, #c084fc, #7c3aed, #6d28d9) !important;
    color: #fff !important; font-weight: 800 !important; font-size: 14px !important;
    font-family: inherit !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.45) !important;
}}
{g} form button p {{ color: #fff !important; font-weight: 800 !important; }}
{g} .mb-captcha-row form button {{
    width: auto !important; min-height: 46px !important;
    background: #27272a !important; box-shadow: none !important;
    border: 1px solid #3f3f46 !important;
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
        f'<div class="mb-auth-aurora" aria-hidden="true"></div>'
        f'<header class="mb-auth-header"><div class="mb-auth-header-inner">'
        f'<div class="mb-auth-header-brand">'
        f'<div class="mb-auth-mark" aria-hidden="true">{initial}</div>'
        f'<div><span class="mb-auth-header-name">{name}</span>'
        f'<span class="mb-auth-header-tag">Creator Operating System</span></div></div>'
        f'<nav class="mb-auth-nav" aria-label="Nav">'
        f'<span>Plattform</span><span>Zukunft</span><span>Ökosystem</span></nav>'
        f'<div class="mb-auth-header-actions">'
        f'<span class="mb-auth-header-badge">Live</span>'
        f'<span class="mb-auth-header-cta">Zugang</span></div>'
        f'</div></header>'
    )


def hero_html() -> str:
    name = html.escape(APP_NAME)
    return (
        f'<div class="mb-auth-hero">'
        f'<div class="mb-auth-eyebrow"><span class="mb-auth-eyebrow-dot"></span>Neue Ära · Live</div>'
        f'<h1 class="mb-auth-headline">{name} — der <em>Grundstein</em> deiner Zukunft.</h1>'
        f'<p class="mb-auth-lead"><strong>{name}</strong> vereint Video, KI, Bild &amp; Code '
        f'in einem Workspace — ohne Tool-Chaos, ohne Tab-Hopping.</p>'
        f'<div class="mb-auth-feats">'
        f'<div class="mb-auth-feat"><b>All-in-One Engine</b><span>Produzieren statt wechseln</span></div>'
        f'<div class="mb-auth-feat"><b>KI-Native</b><span>Chat, Bild, Code integriert</span></div>'
        f'<div class="mb-auth-feat"><b>Produktions-Flow</b><span>Idee bis Post in einem Flow</span></div>'
        f'<div class="mb-auth-feat"><b>Fair Pricing</b><span>Nur zahlen, was du nutzt</span></div>'
        f'</div>'
        f'<p class="mb-auth-manifest">„Die Zukunft gehört denen, die produzieren — nicht denen, die tabben."</p>'
        f'</div>'
    )


def panel_shell_html(*, register: bool) -> str:
    if register:
        head = (
            '<div class="mb-panel-head"><p class="mb-panel-kicker">Neu starten</p>'
            '<h2>Workspace erschaffen</h2>'
            '<p>In einer Minute bereit — deine Zukunft beginnt hier.</p></div>'
        )
    else:
        head = (
            '<div class="mb-panel-head"><p class="mb-panel-kicker">Secure Gateway</p>'
            '<h2>Willkommen zurück</h2>'
            '<p>Melde dich an und setze deine Produktion fort.</p></div>'
        )
    return (
        f'<div class="mb-access-card">'
        f'<div class="mb-access-card-inner">'
        f'<div class="mb-access-top">'
        f'<span class="mb-access-live">System bereit</span>'
        f'<span class="mb-access-tag">Verschlüsselt</span></div>'
        f'{head}'
    )


def panel_close_html() -> str:
    return (
        '<div class="mb-panel-foot">Ende-zu-Ende verschlüsselt · DSGVO-konform</div>'
        '</div></div>'
    )


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}">{safe}</div>'


def page_close_html() -> str:
    return "</div>"


def auth_styles_bundle() -> str:
    return GATE_CSS + widget_css()
