"""MaByte Login Gateway — einladendes Premium-Layout (Deutsch)."""
from __future__ import annotations

import html

from config import APP_NAME
from ui.b2b_theme import MB_THEME_VARS

_SCOPE = "html body .stApp section.main:has(.mb-gate)"


def _s(css: str) -> str:
    return _SCOPE + " " + css


GATE_CSS = (
    MB_THEME_VARS
    + """
html { color-scheme: dark !important; }

.stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
    --primary-color: #7c3aed !important;
    --background-color: #09090b !important;
    --secondary-background-color: #18181b !important;
    --text-color: #fafafa !important;
}

.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {
    background: #09090b !important;
}

#MainMenu, footer, .custom-topbar,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"], [data-testid="stStatusWidget"],
[data-testid="stDeployButton"], [data-testid="stElementToolbar"] {
    display: none !important;
}

[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    background: transparent !important;
}

"""
    + _s("""
.block-container {
    max-width: 1200px !important;
    padding: 24px 28px 40px 28px !important;
    min-height: calc(100vh - 2rem) !important;
}

> div > div > [data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: 0 !important;
    min-height: min(780px, calc(100vh - 5rem)) !important;
}

[data-testid="column"]:first-child {
    padding: 48px 48px 48px 12px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

[data-testid="column"]:last-child {
    padding: 32px 12px 32px 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
""")
    + """
.mb-gate-hero {
    position: relative;
    max-width: 560px;
}
.mb-gate-glow {
    position: absolute;
    top: -80px;
    left: -60px;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.22), transparent 70%);
    pointer-events: none;
    z-index: 0;
}
.mb-gate-hero > * { position: relative; z-index: 1; }

.mb-gate-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px 6px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #c4b5fd !important;
    background: rgba(124, 58, 237, 0.12);
    border: 1px solid rgba(124, 58, 237, 0.35);
    margin-bottom: 20px;
}
.mb-gate-badge-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #a78bfa;
    box-shadow: 0 0 10px #7c3aed;
    animation: mb-pulse 2s ease-in-out infinite;
}
@keyframes mb-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}

.mb-gate-title {
    font-size: clamp(52px, 6vw, 72px);
    font-weight: 800;
    letter-spacing: -0.05em;
    line-height: 0.95;
    margin: 0 0 16px 0;
    background: linear-gradient(135deg, #ffffff 0%, #e9d5ff 40%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.mb-gate-hook {
    font-size: clamp(20px, 2.2vw, 26px);
    font-weight: 600;
    color: #f4f4f5 !important;
    letter-spacing: -0.03em;
    line-height: 1.25;
    margin: 0 0 18px 0;
    max-width: 520px;
}

.mb-gate-story {
    color: #a1a1aa !important;
    font-size: 15px;
    line-height: 1.75;
    margin: 0 0 28px 0;
    max-width: 500px;
}
.mb-gate-story strong {
    color: #e4e4e7 !important;
    font-weight: 600;
}

.mb-gate-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    max-width: 520px;
    margin-bottom: 24px;
}
.mb-gate-stat {
    padding: 16px 14px;
    border-radius: 14px;
    background: rgba(24, 24, 27, 0.7);
    border: 1px solid rgba(63, 63, 70, 0.8);
    backdrop-filter: blur(8px);
}
.mb-gate-stat-num {
    display: block;
    font-size: 22px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}
.mb-gate-stat-label {
    font-size: 11px;
    color: #71717a !important;
    line-height: 1.35;
}

.mb-gate-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.mb-gate-tag {
    font-size: 11px;
    font-weight: 600;
    color: #a1a1aa !important;
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid #3f3f46;
    background: rgba(9, 9, 11, 0.6);
}
"""
    + _s("""
[data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;
    max-width: 400px !important;
    background: rgba(18, 18, 20, 0.85) !important;
    border: 1px solid rgba(63, 63, 70, 0.7) !important;
    border-radius: 20px !important;
    padding: 0 !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.05) inset,
        0 32px 80px rgba(0, 0, 0, 0.55),
        0 0 120px rgba(124, 58, 237, 0.08) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}

[data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    padding: 28px 26px 24px 26px !important;
    gap: 0 !important;
}
""")
    + """
.mb-panel-head { margin-bottom: 22px; }
.mb-panel-head h2 {
    color: #fafafa !important;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0 0 6px 0;
}
.mb-panel-head p {
    color: #71717a !important;
    font-size: 13px;
    margin: 0;
    line-height: 1.5;
}
"""
    + _s("""
.mb-mode-switch [data-testid="stHorizontalBlock"] {
    gap: 6px !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    margin-bottom: 20px !important;
}
.mb-mode-switch .stButton > button {
    min-height: 36px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    background: transparent !important;
    color: #71717a !important;
}
.mb-mode-switch .stButton > button p { color: inherit !important; font-weight: 600 !important; }
.mb-mode-switch .stButton > button[kind="primary"],
.mb-mode-switch .stButton > button[data-testid="stBaseButton-primary"] {
    background: #27272a !important;
    color: #fafafa !important;
}
.mb-mode-switch .stButton > button[kind="secondary"],
.mb-mode-switch .stButton > button[data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    color: #71717a !important;
}
""")
    + """
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 40px;
    padding: 0 16px;
    margin-bottom: 8px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    color: #f4f4f5 !important;
    background: linear-gradient(180deg, #141416, #0c0c0e) !important;
    border: 1px solid #3f3f46 !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.mb-login-google:hover {
    border-color: rgba(124, 58, 237, 0.55) !important;
    box-shadow: 0 0 24px rgba(124, 58, 237, 0.15);
}
.mb-login-google.disabled { opacity: 0.5; pointer-events: none; }
.mb-login-google .g-icon { width: 17px; height: 17px; }

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
    color: #52525b !important;
}
.mb-login-divider::before, .mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #3f3f46;
}

.mb-panel-foot {
    text-align: center;
    font-size: 10px;
    color: #52525b !important;
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid rgba(63, 63, 70, 0.5);
}

/* Custom notices — no Streamlit alert chrome */
.mb-notice {
    padding: 12px 14px;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 14px;
}
.mb-notice-error {
    color: #fecaca !important;
    background: rgba(127, 29, 29, 0.35);
    border: 1px solid rgba(248, 113, 113, 0.35);
}
.mb-notice-success {
    color: #bbf7d0 !important;
    background: rgba(20, 83, 45, 0.35);
    border: 1px solid rgba(74, 222, 128, 0.3);
}
.mb-notice-info {
    color: #bfdbfe !important;
    background: rgba(30, 58, 138, 0.3);
    border: 1px solid rgba(96, 165, 250, 0.3);
}
"""
    + _s("""
@media (max-width: 960px) {
.block-container { padding: 20px 16px 32px 16px !important; }
> div > div > [data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    min-height: auto !important;
}
[data-testid="column"]:first-child,
[data-testid="column"]:last-child {
    padding: 24px 8px !important;
}
.mb-gate-stats { grid-template-columns: 1fr; }
.mb-gate-hero { text-align: center; margin: 0 auto; }
.mb-gate-story, .mb-gate-hook, .mb-gate-stats, .mb-gate-tags {
    margin-left: auto;
    margin-right: auto;
}
.mb-gate-tags { justify-content: center; }
[data-testid="stVerticalBlockBorderWrapper"] { max-width: 100% !important; }
}
""")
)


def login_widget_css() -> str:
    """Overrides for Streamlit widgets on the gate page."""
    return (
        """
"""
        + _SCOPE
        + """
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] p {
    color: #a1a1aa !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

[data-testid="stTextInput"], [data-testid="stNumberInput"] {
    background: transparent !important;
}
[data-testid="stTextInput"] > div, [data-testid="stNumberInput"] > div,
[data-testid="stTextInput"] fieldset, [data-testid="stNumberInput"] fieldset {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: #0a0a0c !important;
    background-color: #0a0a0c !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    min-height: 42px !important;
}
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    caret-color: #fafafa !important;
}
[data-testid="stTextInput"] input::placeholder { color: #52525b !important; }
[data-testid="stTextInput"] input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px #0a0a0c inset !important;
    -webkit-text-fill-color: #fafafa !important;
}
[data-testid="stTextInput"] button { color: #71717a !important; background: transparent !important; }

[data-testid="stForm"] { border: none !important; padding: 0 !important; }
[data-testid="stForm"] [data-testid="stVerticalBlock"] { gap: 12px !important; }

.stFormSubmitButton button,
[data-testid="stFormSubmitButton"] button,
form button[kind="primaryFormSubmit"],
form button[kind="secondaryFormSubmit"],
form button[data-testid="stBaseButton-primaryFormSubmit"],
form button[data-testid="stBaseButton-secondaryFormSubmit"] {
    width: 100% !important;
    min-height: 42px !important;
    border-radius: 10px !important;
    border: 1px solid #5b21b6 !important;
    background: linear-gradient(180deg, #9333ea 0%, #7c3aed 50%, #6d28d9 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4) !important;
}
.stFormSubmitButton button p, form button p { color: #ffffff !important; font-weight: 700 !important; }
.stFormSubmitButton button:hover, form button:hover {
    background: linear-gradient(180deg, #a855f7 0%, #8b5cf6 50%, #7c3aed 100%) !important;
    box-shadow: 0 6px 28px rgba(124, 58, 237, 0.5) !important;
}

.mb-login-captcha .stFormSubmitButton button,
.mb-login-captcha form button {
    min-height: 42px !important;
    width: auto !important;
    background: #27272a !important;
    background-image: none !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}

.stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: #52525b !important;
    font-size: 11px !important;
}

[data-testid="stAlert"] { display: none !important; }
"""
    )


def hero_html() -> str:
    name = html.escape(APP_NAME)
    return f"""
<div class="mb-gate-hero">
    <div class="mb-gate-glow"></div>
    <div class="mb-gate-badge">
        <span class="mb-gate-badge-dot"></span>
        Kreativ-Plattform · Live
    </div>
    <h1 class="mb-gate-title">{name}</h1>
    <p class="mb-gate-hook">Dein Betriebssystem für Creator, die groß denken.</p>
    <p class="mb-gate-story">
        <strong>Stell dir vor:</strong> Shorts, Bilder, Code und KI-Chat in einem Flow —
        nicht zehn Tabs, nicht zehn Abos. {name} bündelt deine komplette Produktion
        an einem Ort. Von der Idee bis zum Post: schneller, klarer, professioneller.
        Genau dafür bist du hier.
    </p>
    <div class="mb-gate-stats">
        <div class="mb-gate-stat">
            <span class="mb-gate-stat-num">Video</span>
            <span class="mb-gate-stat-label">Erstellen, planen, veröffentlichen</span>
        </div>
        <div class="mb-gate-stat">
            <span class="mb-gate-stat-num">KI</span>
            <span class="mb-gate-stat-label">Chat, Bild, Musik &amp; Code</span>
        </div>
        <div class="mb-gate-stat">
            <span class="mb-gate-stat-num">Fair</span>
            <span class="mb-gate-stat-label">Nur zahlen, was du nutzt</span>
        </div>
    </div>
    <div class="mb-gate-tags">
        <span class="mb-gate-tag">Shorts &amp; Video</span>
        <span class="mb-gate-tag">Bildstudio</span>
        <span class="mb-gate-tag">KI-Chat</span>
        <span class="mb-gate-tag">Code</span>
        <span class="mb-gate-tag">Planen &amp; Posten</span>
    </div>
</div>
"""


def panel_head_html() -> str:
    return """
<div class="mb-panel-head">
    <h2>Bereit?</h2>
    <p>Ein Klick — und du bist in deinem Workspace.</p>
</div>
"""


def panel_foot_html() -> str:
    return '<div class="mb-panel-foot">Verschlüsselt · Geschützt · Made for Creators</div>'


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}">{safe}</div>'


def auth_styles_bundle() -> str:
    return GATE_CSS + login_widget_css()
