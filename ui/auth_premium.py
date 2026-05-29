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

.stApp:has(.mb-gate) [data-testid="stAppViewBlockContainer"],
.stApp:has(.mb-gate) [data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}

"""
    + _s("""
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-bottom: 1.25rem !important;
}

.block-container {
    max-width: 1180px !important;
    padding: 0 24px 20px 24px !important;
    padding-top: 0 !important;
    min-height: auto !important;
}

> div > div > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Marker div for :has() — must not consume layout space */
[data-testid="stMarkdown"]:has(> .mb-gate),
[data-testid="stMarkdownContainer"]:has(.mb-gate),
[data-testid="stElementContainer"]:has(.mb-gate) {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}
.mb-gate {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}

> div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 2.5rem !important;
    min-height: auto !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
}

[data-testid="column"]:first-child {
    padding: 0 24px 16px 8px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-self: flex-start !important;
    align-items: flex-start !important;
}

[data-testid="column"]:first-child > [data-testid="stVerticalBlock"] {
    justify-content: flex-start !important;
    align-items: flex-start !important;
    gap: 0 !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="column"]:first-child [data-testid="stMarkdown"],
[data-testid="column"]:first-child [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="column"]:last-child {
    padding: 0 8px 16px 16px !important;
    display: flex !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    align-self: flex-start !important;
}

[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 400px !important;
    margin: 0 0 0 auto !important;
    padding: 0 !important;
}
""")
    + """
.mb-gate-hero {
    position: relative;
    max-width: 560px;
}
.mb-gate-glow {
    position: absolute;
    top: -40px;
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
    font-size: clamp(44px, 5vw, 58px);
    font-weight: 800;
    letter-spacing: -0.05em;
    line-height: 0.95;
    margin: 0 0 14px 0;
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
    font-size: 14px;
    line-height: 1.65;
    margin: 0 0 20px 0;
    max-width: 480px;
}
.mb-gate-story strong {
    color: #e4e4e7 !important;
    font-weight: 600;
}

.mb-gate-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    max-width: 480px;
    margin-bottom: 16px;
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
    padding: 22px 22px 20px 22px !important;
    gap: 0 !important;
    overflow: visible !important;
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
    gap: 5px !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    margin-bottom: 18px !important;
}
.mb-mode-switch .stButton > button,
.mb-mode-switch .stButton > button[kind="primary"],
.mb-mode-switch .stButton > button[kind="secondary"],
.mb-mode-switch .stButton > button[kind="tertiary"],
.mb-mode-switch .stButton > button[data-testid="stBaseButton-primary"],
.mb-mode-switch .stButton > button[data-testid="stBaseButton-secondary"],
.mb-mode-switch .stButton > button[data-testid="stBaseButton-tertiary"] {
    min-height: 36px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    color: #71717a !important;
}
.mb-mode-switch .stButton > button p,
.mb-mode-switch .stButton > button[kind="primary"] p,
.mb-mode-switch .stButton > button[kind="secondary"] p,
.mb-mode-switch .stButton > button[kind="tertiary"] p {
    color: inherit !important;
    font-weight: 600 !important;
}
.mb-mode-login .stButton:first-of-type > button,
.mb-mode-register .stButton:last-of-type > button {
    background: #7c3aed !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
}
.mb-mode-login .stButton:first-of-type > button p,
.mb-mode-register .stButton:last-of-type > button p {
    color: #ffffff !important;
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
    gate = ".stApp:has(.mb-gate)"
    return (
        f"""
{gate} [data-testid="stTextInput"],
{gate} [data-testid="stNumberInput"] {{
    background: transparent !important;
}}
{gate} [data-testid="stTextInput"] > div,
{gate} [data-testid="stNumberInput"] > div,
{gate} [data-testid="stTextInput"] > div > div,
{gate} [data-testid="stTextInput"] fieldset,
{gate} [data-testid="stNumberInput"] fieldset {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

{gate} [data-testid="stTextInput"] div[data-baseweb="input"],
{gate} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: #141416 !important;
    background-color: #141416 !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}}
{gate} [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
{gate} [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.28) !important;
}}

{gate} [data-testid="stTextInput"] input,
{gate} [data-testid="stNumberInput"] input {{
    background: transparent !important;
    background-color: transparent !important;
    color: #f4f4f5 !important;
    -webkit-text-fill-color: #f4f4f5 !important;
    caret-color: #f4f4f5 !important;
    font-size: 14px !important;
}}
{gate} [data-testid="stTextInput"] input::placeholder,
{gate} [data-testid="stNumberInput"] input::placeholder {{
    color: #71717a !important;
    opacity: 1 !important;
}}
{gate} [data-testid="stTextInput"] input:-webkit-autofill,
{gate} [data-testid="stTextInput"] input:-webkit-autofill:focus {{
    -webkit-box-shadow: 0 0 0 1000px #141416 inset !important;
    -webkit-text-fill-color: #f4f4f5 !important;
}}
{gate} [data-testid="stTextInput"] button {{
    color: #a1a1aa !important;
    background: transparent !important;
}}

{gate} [data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
}}
{gate} .mb-login-form [data-testid="stVerticalBlock"] {{
    gap: 12px !important;
}}

{gate} .stFormSubmitButton > button,
{gate} .stFormSubmitButton button,
{gate} [data-testid="stFormSubmitButton"] button,
{gate} form button,
{gate} form button[kind="primaryFormSubmit"],
{gate} form button[kind="secondaryFormSubmit"],
{gate} button[data-testid="stBaseButton-primaryFormSubmit"],
{gate} button[data-testid="stBaseButton-secondaryFormSubmit"] {{
    width: 100% !important;
    min-height: 44px !important;
    border-radius: 10px !important;
    border: 1px solid #6d28d9 !important;
    background: linear-gradient(180deg, #9333ea, #7c3aed 55%, #6d28d9) !important;
    background-color: #7c3aed !important;
    background-image: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 18px rgba(124, 58, 237, 0.4) !important;
}}
{gate} .stFormSubmitButton button p,
{gate} form button p,
{gate} form button span {{
    color: #ffffff !important;
}}

{gate} .mb-login-captcha .stFormSubmitButton button,
{gate} .mb-login-captcha form button {{
    width: auto !important;
    min-height: 44px !important;
    background: #27272a !important;
    background-image: none !important;
    border: 1px solid #3f3f46 !important;
    color: #d4d4d8 !important;
    box-shadow: none !important;
}}

{gate} [data-testid="stAlert"] {{
    display: none !important;
}}

@media (max-height: 800px) {{
    .mb-gate-stats {{ display: none; }}
    .mb-gate-tags {{ display: none; }}
    .mb-gate-story {{ margin-bottom: 14px; }}
}}
"""
    )


def hero_html() -> str:
    name = html.escape(APP_NAME)
    return f"""
<div class="mb-gate" aria-hidden="true"></div>
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
