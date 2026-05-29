"""MaByte Login — Premium B2B Gateway (Deutsch, Streamlit-safe)."""
from __future__ import annotations

import html

from config import APP_NAME
from ui.b2b_theme import MB_THEME_VARS

# Scope via hero root — never collapse the markdown that contains it
_SCOPE = ".stApp:has(.mb-auth-page)"


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

.stApp:has(.mb-auth-page),
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"],
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"] > section {
    background: #09090b !important;
}

.stApp:has(.mb-auth-page) #MainMenu,
.stApp:has(.mb-auth-page) footer,
.stApp:has(.mb-auth-page) .custom-topbar,
.stApp:has(.mb-auth-page) [data-testid="stToolbar"],
.stApp:has(.mb-auth-page) [data-testid="stDecoration"],
.stApp:has(.mb-auth-page) [data-testid="stSidebar"],
.stApp:has(.mb-auth-page) [data-testid="stStatusWidget"],
.stApp:has(.mb-auth-page) [data-testid="stDeployButton"],
.stApp:has(.mb-auth-page) [data-testid="stElementToolbar"] {
    display: none !important;
}

.stApp:has(.mb-auth-page) [data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    background: transparent !important;
}

.stApp:has(.mb-auth-page) [data-testid="stAppViewBlockContainer"],
.stApp:has(.mb-auth-page) [data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}
"""
    + _s("""
section.main .block-container {
    max-width: 1240px !important;
    padding: 28px 32px 40px 32px !important;
    min-height: calc(100vh - 2rem) !important;
}

section.main > div > div > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 3rem !important;
    min-height: calc(100vh - 6rem) !important;
}

[data-testid="column"]:first-child {
    padding: 0 16px 0 0 !important;
    flex: 1.1 !important;
}

[data-testid="column"]:last-child {
    padding: 0 0 0 8px !important;
    flex: 0.9 !important;
    display: flex !important;
    justify-content: flex-end !important;
}

[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 420px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;
    max-width: 420px !important;
    background: rgba(12, 12, 14, 0.72) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 22px !important;
    padding: 0 !important;
    box-shadow:
        0 0 0 1px rgba(124, 58, 237, 0.12) inset,
        0 24px 64px rgba(0, 0, 0, 0.55),
        0 0 80px rgba(124, 58, 237, 0.06) !important;
    backdrop-filter: blur(24px) saturate(1.2);
    -webkit-backdrop-filter: blur(24px) saturate(1.2);
}

[data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    padding: 28px 28px 24px 28px !important;
    gap: 0 !important;
}

.mb-mode-switch [data-testid="stHorizontalBlock"] {
    gap: 4px !important;
    background: rgba(9, 9, 11, 0.9) !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    margin-bottom: 20px !important;
}

.mb-mode-switch .stButton > button,
.mb-mode-switch .stButton > button[kind="tertiary"],
.mb-mode-switch .stButton > button[data-testid="stBaseButton-tertiary"] {
    min-height: 38px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    background: transparent !important;
    background-color: transparent !important;
    color: #71717a !important;
}

.mb-mode-switch .stButton > button p {
    color: inherit !important;
    font-weight: 600 !important;
}

.mb-mode-login .stButton:first-of-type > button,
.mb-mode-register .stButton:last-of-type > button {
    background: #7c3aed !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.35) !important;
}

.mb-mode-login .stButton:first-of-type > button p,
.mb-mode-register .stButton:last-of-type > button p {
    color: #ffffff !important;
}

@media (max-width: 960px) {
    section.main .block-container {
        padding: 20px 16px 32px 16px !important;
        min-height: auto !important;
    }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        min-height: auto !important;
        gap: 2rem !important;
    }
    [data-testid="column"]:first-child,
    [data-testid="column"]:last-child {
        padding: 0 !important;
        flex: 1 !important;
    }
    [data-testid="column"]:last-child > [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlockBorderWrapper"] {
        max-width: 100% !important;
    }
    .mb-auth-features {
        grid-template-columns: 1fr !important;
    }
    .mb-auth-hero {
        text-align: center;
    }
    .mb-auth-brand,
    .mb-auth-lead,
    .mb-auth-features,
    .mb-auth-trust {
        margin-left: auto;
        margin-right: auto;
    }
}
""")
    + """
/* —— Page atmosphere —— */
.mb-auth-page {
    position: relative;
    width: 100%;
    font-family: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}

.mb-auth-page::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 55% 45% at 12% 18%, rgba(124, 58, 237, 0.18), transparent 55%),
        radial-gradient(ellipse 40% 35% at 88% 75%, rgba(59, 130, 246, 0.08), transparent 50%),
        linear-gradient(180deg, #09090b 0%, #0c0c0f 50%, #09090b 100%);
}

.mb-auth-page::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.35;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 64px 64px;
    mask-image: radial-gradient(ellipse 70% 60% at 30% 40%, black 20%, transparent 75%);
}

.mb-auth-hero {
    position: relative;
    z-index: 1;
    max-width: 580px;
    padding-top: 8px;
}

.mb-auth-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
}

.mb-auth-mark {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(145deg, #a855f7, #7c3aed 45%, #5b21b6);
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.12) inset,
        0 8px 32px rgba(124, 58, 237, 0.45);
    letter-spacing: -0.04em;
}

.mb-auth-brand-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.mb-auth-brand-name {
    font-size: 15px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.02em;
}

.mb-auth-brand-sub {
    font-size: 12px;
    color: #71717a !important;
}

.mb-auth-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px 6px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #c4b5fd !important;
    background: rgba(124, 58, 237, 0.1);
    border: 1px solid rgba(124, 58, 237, 0.28);
    margin-bottom: 22px;
}

.mb-auth-eyebrow-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #a78bfa;
    box-shadow: 0 0 12px #7c3aed;
    animation: mb-auth-pulse 2.2s ease-in-out infinite;
}

@keyframes mb-auth-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.55; transform: scale(0.88); }
}

.mb-auth-headline {
    font-size: clamp(36px, 4.2vw, 52px);
    font-weight: 800;
    letter-spacing: -0.045em;
    line-height: 1.05;
    margin: 0 0 16px 0;
    color: #fafafa !important;
}

.mb-auth-headline em {
    font-style: normal;
    background: linear-gradient(120deg, #ffffff 0%, #e9d5ff 35%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.mb-auth-lead {
    font-size: 17px;
    line-height: 1.6;
    color: #a1a1aa !important;
    margin: 0 0 28px 0;
    max-width: 520px;
}

.mb-auth-lead strong {
    color: #e4e4e7 !important;
    font-weight: 600;
}

.mb-auth-features {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 28px;
    max-width: 520px;
}

.mb-auth-feature {
    padding: 18px 16px;
    border-radius: 16px;
    background: rgba(24, 24, 27, 0.55);
    border: 1px solid rgba(63, 63, 70, 0.65);
    backdrop-filter: blur(12px);
    transition: border-color 0.2s, box-shadow 0.2s;
}

.mb-auth-feature:hover {
    border-color: rgba(124, 58, 237, 0.35);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.mb-auth-feature-icon {
    font-size: 20px;
    line-height: 1;
    margin-bottom: 10px;
    display: block;
}

.mb-auth-feature-title {
    display: block;
    font-size: 14px;
    font-weight: 700;
    color: #f4f4f5 !important;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}

.mb-auth-feature-desc {
    font-size: 12px;
    line-height: 1.45;
    color: #71717a !important;
}

.mb-auth-trust {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 16px 24px;
    padding-top: 8px;
    border-top: 1px solid rgba(63, 63, 70, 0.5);
    max-width: 520px;
}

.mb-auth-trust-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #52525b !important;
}

.mb-auth-trust-items {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.mb-auth-trust-pill {
    font-size: 11px;
    font-weight: 600;
    color: #a1a1aa !important;
    padding: 5px 10px;
    border-radius: 8px;
    border: 1px solid #3f3f46;
    background: rgba(9, 9, 11, 0.5);
}

/* —— Auth panel chrome (HTML) —— */
.mb-panel-kicker {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a78bfa !important;
    margin: 0 0 8px 0;
}

.mb-panel-head { margin-bottom: 24px; }

.mb-panel-head h2 {
    color: #fafafa !important;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.035em;
    margin: 0 0 8px 0;
    line-height: 1.15;
}

.mb-panel-head p {
    color: #71717a !important;
    font-size: 14px;
    margin: 0;
    line-height: 1.55;
}

.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 44px;
    padding: 0 16px;
    margin-bottom: 10px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    color: #f4f4f5 !important;
    background: rgba(24, 24, 27, 0.8) !important;
    border: 1px solid #3f3f46 !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}

.mb-login-google:hover {
    border-color: rgba(167, 139, 250, 0.5) !important;
    background: rgba(39, 39, 42, 0.9) !important;
    box-shadow: 0 0 28px rgba(124, 58, 237, 0.12);
}

.mb-login-google.disabled {
    opacity: 0.45;
    pointer-events: none;
}

.mb-login-google .g-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

.mb-login-hint {
    text-align: center;
    font-size: 11px;
    color: #52525b !important;
    margin: 0 0 18px 0;
    line-height: 1.4;
}

.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 18px 0;
    font-size: 11px;
    font-weight: 500;
    color: #52525b !important;
    letter-spacing: 0.02em;
}

.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #3f3f46, transparent);
}

.mb-panel-foot {
    text-align: center;
    font-size: 10px;
    color: #52525b !important;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(63, 63, 70, 0.45);
    line-height: 1.5;
}

.mb-notice {
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 16px;
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
)


def login_widget_css() -> str:
    gate = ".stApp:has(.mb-auth-page)"
    return f"""
{gate} [data-testid="stTextInput"] div[data-baseweb="input"],
{gate} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: #111113 !important;
    background-color: #111113 !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
}}

{gate} [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
{gate} [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.22) !important;
}}

{gate} [data-testid="stTextInput"] input,
{gate} [data-testid="stNumberInput"] input {{
    color: #f4f4f5 !important;
    -webkit-text-fill-color: #f4f4f5 !important;
    font-size: 14px !important;
}}

{gate} [data-testid="stTextInput"] input::placeholder {{
    color: #71717a !important;
    opacity: 1 !important;
}}

{gate} [data-testid="stTextInput"] input:-webkit-autofill {{
    -webkit-box-shadow: 0 0 0 1000px #111113 inset !important;
    -webkit-text-fill-color: #f4f4f5 !important;
}}

{gate} .mb-login-form [data-testid="stVerticalBlock"] {{
    gap: 14px !important;
}}

{gate} form button,
{gate} .stFormSubmitButton button {{
    width: 100% !important;
    min-height: 46px !important;
    border-radius: 12px !important;
    border: 1px solid #6d28d9 !important;
    background: linear-gradient(180deg, #9333ea, #7c3aed 50%, #6d28d9) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 6px 24px rgba(124, 58, 237, 0.38) !important;
}}

{gate} form button p {{
    color: #fff !important;
}}

{gate} .mb-login-captcha form button {{
    width: auto !important;
    min-height: 46px !important;
    background: #27272a !important;
    box-shadow: none !important;
    border: 1px solid #3f3f46 !important;
}}

{gate} [data-testid="stAlert"] {{
    display: none !important;
}}
"""


def hero_html() -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    return f"""
<div class="mb-auth-page">
    <div class="mb-auth-hero">
        <div class="mb-auth-brand">
            <div class="mb-auth-mark" aria-hidden="true">{initial}</div>
            <div class="mb-auth-brand-text">
                <span class="mb-auth-brand-name">{name}</span>
                <span class="mb-auth-brand-sub">Creator Operating System</span>
            </div>
        </div>
        <div class="mb-auth-eyebrow">
            <span class="mb-auth-eyebrow-dot"></span>
            Kreativ-Plattform · Live
        </div>
        <h1 class="mb-auth-headline">
            Produziere <em>schneller</em>.<br>Veröffentliche <em>smarter</em>.
        </h1>
        <p class="mb-auth-lead">
            <strong>{name}</strong> vereint Video, KI, Bild &amp; Code in einem Workspace —
            ohne Tool-Chaos. Von der Idee bis zum Post, professionell und fair bepreist.
        </p>
        <div class="mb-auth-features">
            <div class="mb-auth-feature">
                <span class="mb-auth-feature-icon" aria-hidden="true">▶</span>
                <span class="mb-auth-feature-title">Video &amp; Shorts</span>
                <span class="mb-auth-feature-desc">Erstellen, schneiden, planen und posten</span>
            </div>
            <div class="mb-auth-feature">
                <span class="mb-auth-feature-icon" aria-hidden="true">✦</span>
                <span class="mb-auth-feature-title">KI-Studio</span>
                <span class="mb-auth-feature-desc">Chat, Bild, Musik und Code an einem Ort</span>
            </div>
            <div class="mb-auth-feature">
                <span class="mb-auth-feature-icon" aria-hidden="true">◇</span>
                <span class="mb-auth-feature-title">Fair Pricing</span>
                <span class="mb-auth-feature-desc">Nur zahlen, was du wirklich nutzt</span>
            </div>
            <div class="mb-auth-feature">
                <span class="mb-auth-feature-icon" aria-hidden="true">⚡</span>
                <span class="mb-auth-feature-title">Ein Flow</span>
                <span class="mb-auth-feature-desc">Keine zehn Tabs, kein Kontextwechsel</span>
            </div>
        </div>
        <div class="mb-auth-trust">
            <span class="mb-auth-trust-label">Gebaut für</span>
            <div class="mb-auth-trust-items">
                <span class="mb-auth-trust-pill">Creator</span>
                <span class="mb-auth-trust-pill">Agenturen</span>
                <span class="mb-auth-trust-pill">Studios</span>
                <span class="mb-auth-trust-pill">Teams</span>
            </div>
        </div>
    </div>
</div>
"""


def panel_head_html(*, register: bool = False) -> str:
    if register:
        return """
<div class="mb-panel-head">
    <p class="mb-panel-kicker">Neu bei MaByte</p>
    <h2>Konto anlegen</h2>
    <p>In weniger als einer Minute startklar — dein Workspace wartet.</p>
</div>
"""
    return """
<div class="mb-panel-head">
    <p class="mb-panel-kicker">Workspace</p>
    <h2>Willkommen zurück</h2>
    <p>Melde dich an und setze deine nächste Produktion fort.</p>
</div>
"""


def panel_foot_html() -> str:
    return (
        '<div class="mb-panel-foot">'
        "Verschlüsselte Verbindung · DSGVO-konform · Made for Creators"
        "</div>"
    )


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}">{safe}</div>'


def auth_styles_bundle() -> str:
    return GATE_CSS + login_widget_css()
