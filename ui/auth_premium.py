"""MaByte SaaS login — pitch + auth panel (Deutsch, premium)."""
from __future__ import annotations

import html

from config import APP_NAME
from ui.b2b_theme import MB_THEME_VARS

# Login route marker (see pages/auth.py)
_SCOPE = "html body .stApp section.main:has(.mb-login-route)"

LOGIN_CSS = (
    MB_THEME_VARS
    + """
html {
    color-scheme: dark !important;
}
.stApp,
.stApp[data-theme="light"],
.stApp[data-theme="dark"] {
    --primary-color: #7c3aed !important;
    --background-color: #09090b !important;
    --secondary-background-color: #18181b !important;
    --text-color: #fafafa !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {
    background:
        radial-gradient(ellipse 90% 55% at 6% -5%, rgba(124, 58, 237, 0.11), transparent 55%),
        radial-gradient(ellipse 65% 45% at 98% 105%, rgba(99, 102, 241, 0.07), transparent 50%),
        linear-gradient(168deg, #09090b 0%, #0b0b0e 45%, #09090b 100%) !important;
}

.custom-topbar, #MainMenu, footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"], [data-testid="stStatusWidget"],
[data-testid="stDeployButton"] {
    display: none !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}

"""
    + _SCOPE
    + """ .block-container {
    max-width: 1140px !important;
    padding: 28px 32px 44px 32px !important;
    min-height: calc(100vh - 4rem) !important;
}

"""
    + _SCOPE
    + """ > div > div > [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 3.5rem !important;
    min-height: min(720px, calc(100vh - 8rem)) !important;
}

.mb-brand-mark {
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -0.05em;
    line-height: 1;
    margin: 0 0 22px 0;
    display: inline-block;
    background: linear-gradient(135deg, #fafafa 0%, #c4b5fd 55%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 8px 24px rgba(124, 58, 237, 0.35));
}

.mb-pitch-eyebrow {
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0 0 12px 0;
}
.mb-pitch-title {
    font-size: clamp(36px, 4vw, 50px);
    line-height: 1.05;
    font-weight: 700;
    letter-spacing: -0.04em;
    margin: 0 0 10px 0;
    background: linear-gradient(120deg, #ffffff 0%, #e4e4e7 45%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.mb-pitch-tagline {
    font-size: 18px;
    font-weight: 500;
    color: #e4e4e7 !important;
    margin: 0 0 14px 0;
    line-height: 1.35;
}
.mb-pitch-lead {
    color: #a1a1aa !important;
    font-size: 14px;
    line-height: 1.72;
    margin: 0 0 22px 0;
    max-width: 470px;
}
.mb-pitch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 470px;
    margin-bottom: 20px;
}
.mb-pitch-item {
    position: relative;
    padding: 14px 15px 14px 18px;
    border-radius: 12px;
    background: linear-gradient(160deg, rgba(30, 30, 34, 0.95), rgba(20, 20, 23, 0.98));
    border: 1px solid rgba(63, 63, 70, 0.85);
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.mb-pitch-item::before {
    content: "";
    position: absolute;
    left: 10px;
    top: 17px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #7c3aed;
    box-shadow: 0 0 8px rgba(124, 58, 237, 0.6);
}
.mb-pitch-item:hover {
    border-color: rgba(124, 58, 237, 0.4);
    transform: translateY(-1px);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
}
.mb-pitch-item strong {
    display: block;
    color: #f4f4f5 !important;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 4px;
}
.mb-pitch-item span {
    color: #71717a !important;
    font-size: 11px;
    line-height: 1.45;
}
.mb-pitch-proof {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    max-width: 470px;
}
.mb-pitch-pill {
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 600;
    color: #d4d4d8 !important;
    background: rgba(39, 39, 42, 0.9);
    border: 1px solid rgba(82, 82, 91, 0.6);
}

/* Login card */
"""
    + _SCOPE
    + """ [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(165deg, #1e1e22 0%, #161618 55%, #18181b 100%) !important;
    border: 1px solid rgba(82, 82, 91, 0.55) !important;
    border-radius: 18px !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 392px !important;
    margin-left: auto !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.05) inset,
        0 28px 64px rgba(0, 0, 0, 0.5),
        0 0 100px rgba(124, 58, 237, 0.07) !important;
}
"""
    + _SCOPE
    + """ [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    padding: 24px 24px 20px 24px !important;
    gap: 0 !important;
}

.mb-login-card-head {
    margin: 0 0 18px 0;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(63, 63, 70, 0.55);
}
.mb-login-card-head h2 {
    color: #fafafa !important;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.03em;
    margin: 0 0 5px 0;
}
.mb-login-card-head p {
    color: #71717a !important;
    font-size: 12px;
    margin: 0;
}

/* Segmented control */
"""
    + _SCOPE
    + """ [data-testid="stSegmentedControl"] {
    margin-bottom: 16px !important;
}
"""
    + _SCOPE
    + """ [data-testid="stSegmentedControl"] [data-baseweb="button-group"] {
    width: 100% !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 3px !important;
}
"""
    + _SCOPE
    + """ [data-testid="stSegmentedControl"] button {
    flex: 1 !important;
    border-radius: 7px !important;
    min-height: 34px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #71717a !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
"""
    + _SCOPE
    + """ [data-testid="stSegmentedControl"] button[aria-checked="true"],
"""
    + _SCOPE
    + """ [data-testid="stSegmentedControl"] button[aria-selected="true"] {
    background: #27272a !important;
    color: #fafafa !important;
}

.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    width: 100%;
    min-height: 38px;
    margin: 0 0 6px 0;
    padding: 0 14px;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    color: #f4f4f5 !important;
    background: #0a0a0c !important;
    border: 1px solid #3f3f46 !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.mb-login-google:hover {
    border-color: rgba(124, 58, 237, 0.55) !important;
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.12);
}
.mb-login-google.disabled { opacity: 0.45; pointer-events: none; }
.mb-login-google .g-icon { width: 16px; height: 16px; }

.mb-login-trust {
    text-align: center;
    color: #52525b !important;
    font-size: 10px;
    margin: 0 0 14px 0;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 14px 0;
    color: #52525b !important;
    font-size: 10px;
    line-height: 1;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #3f3f46;
}

.mb-login-foot {
    text-align: center;
    color: #52525b !important;
    font-size: 10px;
    margin: 16px 0 0 0;
    padding-top: 14px;
    border-top: 1px solid rgba(63, 63, 70, 0.45);
}

@media (max-width: 900px) {
"""
    + _SCOPE
    + """ .block-container { padding: 20px 16px 36px 16px !important; min-height: auto !important; }
"""
    + _SCOPE
    + """ > div > div > [data-testid="stHorizontalBlock"] { min-height: auto !important; gap: 2rem !important; }
    .mb-pitch-grid { grid-template-columns: 1fr; }
"""
    + _SCOPE
    + """ [data-testid="stVerticalBlockBorderWrapper"] { max-width: 100% !important; margin-left: 0 !important; }
    .mb-brand-mark { display: block; text-align: center; margin-left: auto; margin-right: auto; }
    .mb-pitch-eyebrow, .mb-pitch-tagline, .mb-pitch-lead, .mb-pitch-title { text-align: center; }
    .mb-pitch-lead, .mb-pitch-grid, .mb-pitch-proof { margin-left: auto; margin-right: auto; }
    .mb-pitch-proof { justify-content: center; }
}
"""
)


def login_override_css() -> str:
    """Final cascade — inputs + buttons on login route only."""
    return (
        """
/* Login route final overrides */
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] input,
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] textarea,
"""
        + _SCOPE
        + """ [data-testid="stNumberInput"] input {
    background: transparent !important;
    background-color: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    caret-color: #fafafa !important;
    border: none !important;
    box-shadow: none !important;
}
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] input:-webkit-autofill,
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] input:-webkit-autofill:hover,
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #09090b inset !important;
    -webkit-text-fill-color: #fafafa !important;
    transition: background-color 9999s ease-out 0s;
}
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] > div,
"""
        + _SCOPE
        + """ [data-testid="stNumberInput"] > div,
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] fieldset,
"""
        + _SCOPE
        + """ [data-testid="stNumberInput"] fieldset,
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] [data-testid="stWidgetLabel"],
"""
        + _SCOPE
        + """ [data-testid="stNumberInput"] [data-testid="stWidgetLabel"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] div[data-baseweb="input"],
"""
        + _SCOPE
        + """ [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background-color: #09090b !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 9px !important;
    min-height: 38px !important;
}
"""
        + _SCOPE
        + """ [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
"""
        + _SCOPE
        + """ [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.22) !important;
}
"""
        + _SCOPE
        + """ [data-testid="stWidgetLabel"] p {
    color: #a1a1aa !important;
    font-size: 11px !important;
}
"""
        + _SCOPE
        + """ [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 11px !important;
}

/* Violet CTA — all submit buttons in login card */
"""
        + _SCOPE
        + """ .stFormSubmitButton button,
"""
        + _SCOPE
        + """ [data-testid="stFormSubmitButton"] button,
"""
        + _SCOPE
        + """ form button,
"""
        + _SCOPE
        + """ button[kind="primaryFormSubmit"],
"""
        + _SCOPE
        + """ button[kind="secondaryFormSubmit"],
"""
        + _SCOPE
        + """ button[data-testid="stBaseButton-primaryFormSubmit"],
"""
        + _SCOPE
        + """ button[data-testid="stBaseButton-secondaryFormSubmit"],
"""
        + _SCOPE
        + """ button[data-testid="stBaseButton-primary"],
"""
        + _SCOPE
        + """ button[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 48%, #6d28d9 100%) !important;
    background-color: #7c3aed !important;
    background-image: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 48%, #6d28d9 100%) !important;
    border: 1px solid #6d28d9 !important;
    color: #ffffff !important;
    border-radius: 9px !important;
    min-height: 38px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35) !important;
    width: 100% !important;
}
"""
        + _SCOPE
        + """ .stFormSubmitButton button:hover,
"""
        + _SCOPE
        + """ form button:hover {
    background: linear-gradient(180deg, #a78bfa 0%, #8b5cf6 50%, #7c3aed 100%) !important;
    background-color: #8b5cf6 !important;
    color: #ffffff !important;
    border-color: #7c3aed !important;
}
"""
        + _SCOPE
        + """ .stFormSubmitButton button p,
"""
        + _SCOPE
        + """ form button p,
"""
        + _SCOPE
        + """ button p {
    color: #ffffff !important;
}

/* Captcha refresh = neutral */
"""
        + _SCOPE
        + """ .mb-login-captcha .stFormSubmitButton button,
"""
        + _SCOPE
        + """ .mb-login-captcha form button {
    background: #27272a !important;
    background-color: #27272a !important;
    background-image: none !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
    min-width: 44px !important;
    width: auto !important;
}
"""
        + _SCOPE
        + """ [data-baseweb="tab-border"],
"""
        + _SCOPE
        + """ [data-baseweb="tab-highlight"],
"""
        + _SCOPE
        + """ [data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
    opacity: 0 !important;
    height: 0 !important;
    background: transparent !important;
}
"""
        + _SCOPE
        + """ [data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: #27272a !important;
    color: #fafafa !important;
    border: none !important;
    box-shadow: none !important;
}
"""
        + _SCOPE
        + """ [data-testid="stSegmentedControl"] button {
    color: #71717a !important;
    background: transparent !important;
}
"""
    )


def brand_mark_html() -> str:
    name = html.escape(APP_NAME)
    return f'<div class="mb-brand-mark">{name}</div>'


def presentation_html() -> str:
    name = html.escape(APP_NAME)
    return f"""
<div class="mb-pitch">
    <p class="mb-pitch-eyebrow">Kreativ-Plattform für Profis</p>
    <h1 class="mb-pitch-title">{name}</h1>
    <p class="mb-pitch-tagline">Ein KI-System. Unendlich viele Workflows.</p>
    <p class="mb-pitch-lead">
        Video, Bild, Code und KI-Chat in einer Plattform — für Creator und Teams,
        die professionell arbeiten. Ein Arbeitsbereich, faire Nutzung pro Aktion.
    </p>
    <div class="mb-pitch-grid">
        <div class="mb-pitch-item">
            <strong>Video &amp; Shorts</strong>
            <span>Clips erstellen, planen und veröffentlichen.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>KI-Studios</strong>
            <span>Chat, Bild, Musik und Code — verbunden.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>Für Teams</strong>
            <span>Transparente Kosten pro Aktion.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>Sicher &amp; einfach</strong>
            <span>Mit Google oder Benutzername &amp; Passwort.</span>
        </div>
    </div>
    <div class="mb-pitch-proof">
        <span class="mb-pitch-pill">Shorts &amp; Video</span>
        <span class="mb-pitch-pill">Bildstudio</span>
        <span class="mb-pitch-pill">KI-Chat</span>
        <span class="mb-pitch-pill">Code</span>
        <span class="mb-pitch-pill">Planen &amp; Posten</span>
    </div>
</div>
"""


def login_card_head_html() -> str:
    return """
<div class="mb-login-card-head">
    <h2>Willkommen</h2>
    <p>Melde dich an und starte in deinem Arbeitsbereich.</p>
</div>
"""


def login_footer_html() -> str:
    return """
<div class="mb-login-foot">
    Verschlüsselte Verbindung · Geschützte Anmeldung
</div>
"""


def auth_styles_bundle() -> str:
    return LOGIN_CSS
