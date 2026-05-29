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
        radial-gradient(ellipse 90% 60% at 10% 0%, rgba(124, 58, 237, 0.09), transparent 50%),
        radial-gradient(ellipse 70% 50% at 95% 90%, rgba(99, 102, 241, 0.06), transparent 45%),
        linear-gradient(165deg, #09090b 0%, #0c0c0f 42%, #09090b 100%) !important;
}

.custom-topbar,
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
[data-testid="stStatusWidget"],
#MainMenu {
    display: none !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}

section.main .block-container {
    max-width: 1080px !important;
    padding: 40px 28px 52px 28px !important;
}

section.main [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 3rem !important;
}

/* Pitch column */
section.main [data-testid="column"]:first-child [data-testid="stImage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 8px !important;
}
section.main [data-testid="column"]:first-child [data-testid="stImage"] img {
    max-width: 132px !important;
    width: 132px !important;
    display: block !important;
    filter: drop-shadow(0 14px 36px rgba(124, 58, 237, 0.25));
}

.mb-pitch-eyebrow {
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 16px 0;
}
.mb-pitch-title {
    font-size: clamp(36px, 4.2vw, 52px);
    line-height: 1.05;
    font-weight: 700;
    letter-spacing: -0.045em;
    margin: 0 0 14px 0;
    background: linear-gradient(135deg, #fafafa 0%, #e4e4e7 55%, #c4b5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.mb-pitch-tagline {
    font-size: 19px;
    font-weight: 500;
    color: #e4e4e7 !important;
    margin: 0 0 16px 0;
    letter-spacing: -0.02em;
    line-height: 1.4;
}
.mb-pitch-lead {
    color: #a1a1aa !important;
    font-size: 15px;
    line-height: 1.75;
    margin: 0 0 30px 0;
    max-width: 500px;
}
.mb-pitch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    max-width: 500px;
    margin-bottom: 26px;
}
.mb-pitch-item {
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(145deg, rgba(24, 24, 27, 0.9), rgba(18, 18, 20, 0.95));
    border: 1px solid rgba(63, 63, 70, 0.8);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.mb-pitch-item:hover {
    border-color: rgba(124, 58, 237, 0.35);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}
.mb-pitch-item strong {
    display: block;
    color: #f4f4f5 !important;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 5px;
    letter-spacing: -0.01em;
}
.mb-pitch-item span {
    color: #71717a !important;
    font-size: 12px;
    line-height: 1.5;
}
.mb-pitch-proof {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    max-width: 500px;
}
.mb-pitch-pill {
    padding: 7px 14px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    color: #d4d4d8 !important;
    background: rgba(39, 39, 42, 0.85);
    border: 1px solid rgba(63, 63, 70, 0.9);
}

/* Login panel */
section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, rgba(28, 28, 31, 0.98) 0%, rgba(24, 24, 27, 0.98) 100%) !important;
    border: 1px solid rgba(63, 63, 70, 0.9) !important;
    border-radius: 16px !important;
    padding: 24px 22px 20px 22px !important;
    max-width: 368px !important;
    margin-left: auto !important;
    margin-right: 0 !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.05) inset,
        0 20px 56px rgba(0, 0, 0, 0.45),
        0 0 80px rgba(124, 58, 237, 0.06) !important;
}

.mb-login-card-head {
    margin-bottom: 18px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(63, 63, 70, 0.5);
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
    font-size: 13px;
    margin: 0;
    line-height: 1.45;
}

section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 3px !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    padding: 4px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 7px !important;
    color: #71717a !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    padding: 7px 14px !important;
    min-height: 34px !important;
    background: transparent !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: #27272a !important;
    color: #fafafa !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2) !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-highlight"],
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 38px;
    margin: 0 0 8px 0;
    padding: 0 14px;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    color: #f4f4f5 !important;
    background: rgba(9, 9, 11, 0.9) !important;
    border: 1px solid #3f3f46 !important;
    box-sizing: border-box;
    transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}
.mb-login-google:hover {
    border-color: rgba(124, 58, 237, 0.45) !important;
    background: #18181b !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.12);
    color: #fafafa !important;
}
.mb-login-google.disabled {
    opacity: 0.5;
    pointer-events: none;
}
.mb-login-google .g-icon {
    width: 17px;
    height: 17px;
    flex-shrink: 0;
}
.mb-login-trust {
    text-align: center;
    color: #52525b !important;
    font-size: 11px;
    margin: 0 0 14px 0;
    line-height: 1.45;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 14px 0;
    color: #52525b !important;
    font-size: 11px;
    font-weight: 500;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #3f3f46, transparent);
}

section.main [data-testid="column"]:last-child [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 11px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stWidgetLabel"] p,
section.main [data-testid="column"]:last-child label p {
    color: #a1a1aa !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] div[data-baseweb="input"],
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 9px !important;
    min-height: 38px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2) !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] input,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] input {
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 13px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] input::placeholder {
    color: #52525b !important;
}

section.main [data-testid="column"]:last-child .stFormSubmitButton > button,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"] {
    width: 100% !important;
    min-height: 38px !important;
    border-radius: 9px !important;
    border: 1px solid #6d28d9 !important;
    background: linear-gradient(180deg, #7c3aed 0%, #6d28d9 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.32) !important;
}
section.main [data-testid="column"]:last-child .stFormSubmitButton > button:hover,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%) !important;
}
section.main [data-testid="column"]:last-child .stFormSubmitButton > button p,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"] p {
    color: #ffffff !important;
}

section.main [data-testid="column"]:last-child .mb-login-captcha [data-testid="stFormSubmitButton"] > button {
    min-height: 38px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}

.mb-login-foot {
    text-align: center;
    color: #52525b !important;
    font-size: 11px;
    margin-top: 16px;
    line-height: 1.5;
}
.mb-login-help {
    text-align: center;
    color: #52525b !important;
    font-size: 11px;
    margin-top: 10px;
    line-height: 1.5;
}
.mb-login-help a {
    color: #a78bfa !important;
    text-decoration: none;
}

section.main [data-testid="stAlert"] {
    border-radius: 10px !important;
    margin-bottom: 12px !important;
    font-size: 13px !important;
}

@media (max-width: 900px) {
    section.main .block-container { padding: 28px 16px 44px 16px !important; }
    .mb-pitch-grid { grid-template-columns: 1fr; }
    section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
        max-width: 100% !important;
        margin-left: 0 !important;
    }
    section.main [data-testid="column"]:first-child [data-testid="stImage"] img {
        margin: 0 auto !important;
    }
    .mb-pitch-eyebrow, .mb-pitch-tagline, .mb-pitch-lead { text-align: center; }
    .mb-pitch-title { text-align: center; }
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
        Die All-in-One-Plattform für Video, Bild, Code und KI-Chat — gebaut für Creator
        und Teams, die professionell arbeiten wollen. Kein Tool-Chaos, ein klarer
        Arbeitsbereich, faire Nutzung pro Aktion.
    </p>
    <div class="mb-pitch-grid">
        <div class="mb-pitch-item">
            <strong>Video &amp; Shorts</strong>
            <span>Clips erstellen, planen und veröffentlichen — alles an einem Ort.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>KI-Studios</strong>
            <span>Chat, Bild, Musik und Code — übersichtlich getrennt, nahtlos verbunden.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>Für Teams</strong>
            <span>Transparente Kosten — du siehst genau, was jede Aktion verbraucht.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>Sicher &amp; einfach</strong>
            <span>Mit Google anmelden oder klassisch mit Benutzername und Passwort.</span>
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
