"""MaByte SaaS login — pitch column + compact auth panel (Deutsch)."""
from __future__ import annotations

import html

from config import APP_NAME
from ui.b2b_theme import MB_THEME_VARS

LOGIN_CSS = """
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {
    background:
        radial-gradient(ellipse 90% 60% at 8% 0%, rgba(124, 58, 237, 0.08), transparent 52%),
        radial-gradient(ellipse 70% 50% at 92% 100%, rgba(99, 102, 241, 0.05), transparent 48%),
        linear-gradient(165deg, #09090b 0%, #0c0c0f 42%, #09090b 100%) !important;
}

.custom-topbar,
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}

section.main .block-container {
    max-width: 1120px !important;
    padding: 32px 32px 48px 32px !important;
}

/* Split columns — pitch top, login vertically centered */
section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 4rem !important;
}

section.main [data-testid="column"]:first-child {
    padding-top: 8px !important;
}

section.main [data-testid="column"]:last-child {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: stretch !important;
    padding-top: 12px !important;
}

section.main [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 380px !important;
    margin-left: auto !important;
    gap: 0 !important;
}

/* Logo — no box */
section.main [data-testid="column"]:first-child [data-testid="stImage"],
section.main [data-testid="column"]:first-child [data-testid="stImage"] > div,
section.main [data-testid="column"]:first-child [data-testid="stImage"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
section.main [data-testid="column"]:first-child [data-testid="stImage"] img {
    max-width: 120px !important;
    width: 120px !important;
    display: block !important;
    margin: 0 0 20px 0 !important;
    filter: drop-shadow(0 12px 32px rgba(124, 58, 237, 0.22));
}

/* Pitch typography */
.mb-pitch-eyebrow {
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 14px 0;
}
.mb-pitch-title {
    font-size: clamp(34px, 3.8vw, 48px);
    line-height: 1.06;
    font-weight: 700;
    letter-spacing: -0.04em;
    margin: 0 0 12px 0;
    background: linear-gradient(135deg, #fafafa 0%, #e4e4e7 50%, #c4b5fd 100%);
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
    line-height: 1.7;
    margin: 0 0 24px 0;
    max-width: 480px;
}
.mb-pitch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 480px;
    margin-bottom: 22px;
}
.mb-pitch-item {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, 0.75);
    border: 1px solid rgba(63, 63, 70, 0.75);
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
    max-width: 480px;
}
.mb-pitch-pill {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 600;
    color: #d4d4d8 !important;
    background: rgba(39, 39, 42, 0.8);
    border: 1px solid rgba(63, 63, 70, 0.85);
}

/* Login card — single bordered container */
section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, #1c1c1f 0%, #18181b 100%) !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 16px !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 380px !important;
    margin: 0 0 0 auto !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 24px 48px rgba(0, 0, 0, 0.42) !important;
    overflow: hidden !important;
}

section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 22px 22px 18px 22px !important;
}

.mb-login-card-head {
    margin: 0 0 16px 0;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(63, 63, 70, 0.55);
}
.mb-login-card-head h2 {
    color: #fafafa !important;
    font-size: 19px;
    font-weight: 600;
    letter-spacing: -0.025em;
    margin: 0 0 4px 0;
}
.mb-login-card-head p {
    color: #71717a !important;
    font-size: 12px;
    margin: 0;
    line-height: 1.4;
}

/* Tabs */
section.main [data-testid="column"]:last-child [data-testid="stTabs"] {
    margin: 0 0 14px 0 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 3px !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 9px !important;
    padding: 3px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 6px !important;
    color: #71717a !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
    min-height: 32px !important;
    background: transparent !important;
    border: none !important;
    border-bottom: none !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: #27272a !important;
    color: #fafafa !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-highlight"],
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
    opacity: 0 !important;
    height: 0 !important;
    background: transparent !important;
}

/* Google */
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    width: 100%;
    min-height: 36px;
    margin: 0 0 6px 0;
    padding: 0 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    color: #e4e4e7 !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    box-sizing: border-box;
}
.mb-login-google:hover {
    border-color: rgba(124, 58, 237, 0.5) !important;
    color: #fafafa !important;
}
.mb-login-google.disabled { opacity: 0.45; pointer-events: none; }
.mb-login-google .g-icon { width: 16px; height: 16px; }

.mb-login-trust {
    text-align: center;
    color: #52525b !important;
    font-size: 10px;
    margin: 0 0 12px 0;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 12px 0;
    color: #52525b !important;
    font-size: 10px;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #3f3f46;
}

/* Forms — dark inputs, no white boxes */
section.main [data-testid="column"]:last-child [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stWidgetLabel"] p {
    color: #a1a1aa !important;
    font-size: 11px !important;
    font-weight: 500 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"],
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] {
    background: transparent !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] > div,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] > div,
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] fieldset,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] fieldset {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] div[data-baseweb="input"],
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: #09090b !important;
    background-color: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
    min-height: 36px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] input,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] input {
    background: transparent !important;
    background-color: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 13px !important;
    caret-color: #fafafa !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] input::placeholder {
    color: #52525b !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] button {
    color: #71717a !important;
    background: transparent !important;
}

/* Submit — force violet, never Streamlit red */
section.main [data-testid="column"]:last-child .stFormSubmitButton > button,
section.main [data-testid="column"]:last-child .stFormSubmitButton button,
section.main [data-testid="column"]:last-child [data-testid="stFormSubmitButton"] > button,
section.main [data-testid="column"]:last-child [data-testid="stFormSubmitButton"] button,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"],
section.main [data-testid="column"]:last-child form button[data-testid="stBaseButton-primaryFormSubmit"],
section.main [data-testid="column"]:last-child form button[data-testid="stBaseButton-primary"] {
    width: 100% !important;
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 8px !important;
    border: 1px solid #6d28d9 !important;
    background: #7c3aed !important;
    background-color: #7c3aed !important;
    background-image: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.3) !important;
    margin-top: 2px !important;
}
section.main [data-testid="column"]:last-child .stFormSubmitButton > button:hover,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"]:hover {
    background: #6d28d9 !important;
    background-color: #6d28d9 !important;
    color: #ffffff !important;
    border-color: #5b21b6 !important;
}
section.main [data-testid="column"]:last-child .stFormSubmitButton > button p,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"] p,
section.main [data-testid="column"]:last-child form button[data-testid="stBaseButton-primary"] p {
    color: #ffffff !important;
}

section.main [data-testid="column"]:last-child .mb-login-captcha .stFormSubmitButton > button,
section.main [data-testid="column"]:last-child .mb-login-captcha form button {
    min-height: 36px !important;
    background: #27272a !important;
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}

.mb-login-foot {
    text-align: center;
    color: #52525b !important;
    font-size: 10px;
    margin: 14px 0 0 0;
    padding-top: 12px;
    border-top: 1px solid rgba(63, 63, 70, 0.45);
    line-height: 1.4;
}

section.main [data-testid="column"]:last-child .stCaption {
    font-size: 11px !important;
    color: #52525b !important;
    margin-bottom: 8px !important;
}

section.main [data-testid="stAlert"] {
    border-radius: 9px !important;
    margin-bottom: 12px !important;
    max-width: 1120px;
}

@media (max-width: 900px) {
    section.main .block-container { padding: 24px 16px 40px 16px !important; }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        gap: 2rem !important;
    }
    section.main [data-testid="column"]:last-child {
        justify-content: flex-start !important;
    }
    section.main [data-testid="column"]:last-child > [data-testid="stVerticalBlock"],
    section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
        max-width: 100% !important;
        margin-left: 0 !important;
    }
    .mb-pitch-grid { grid-template-columns: 1fr; }
    section.main [data-testid="column"]:first-child [data-testid="stImage"] img {
        margin: 0 auto 20px auto !important;
    }
    .mb-pitch-eyebrow, .mb-pitch-tagline, .mb-pitch-lead, .mb-pitch-title {
        text-align: center;
    }
    .mb-pitch-lead, .mb-pitch-grid, .mb-pitch-proof {
        margin-left: auto;
        margin-right: auto;
    }
    .mb-pitch-proof { justify-content: center; }
}
"""


def presentation_html() -> str:
    name = html.escape(APP_NAME)
    return f"""
<div class="mb-pitch">
    <p class="mb-pitch-eyebrow">Kreativ-Plattform für Profis</p>
    <h1 class="mb-pitch-title">{name}</h1>
    <p class="mb-pitch-tagline">Ein KI-System. Unendlich viele Workflows.</p>
    <p class="mb-pitch-lead">
        Die All-in-One-Plattform für Video, Bild, Code und KI-Chat — für Creator und Teams,
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
            <span>Google oder Benutzername &amp; Passwort.</span>
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
    return MB_THEME_VARS + LOGIN_CSS
