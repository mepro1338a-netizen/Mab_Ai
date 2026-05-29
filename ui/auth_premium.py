"""MaByte SaaS login — pitch column + compact auth panel."""
from __future__ import annotations

import html

from config import APP_NAME, APP_POSITIONING, APP_TAGLINE
from ui.b2b_theme import MB_THEME_VARS

LOGIN_CSS = """
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {
    background: linear-gradient(160deg, #09090b 0%, #0f0f12 40%, #09090b 100%) !important;
}

.custom-topbar,
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}

/* Wide split layout */
section.main .block-container {
    max-width: 1080px !important;
    padding: 36px 28px 48px 28px !important;
}

section.main [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 2.5rem !important;
}

/* ── Pitch column (left) ─────────────────────────────────── */
section.main [data-testid="column"]:first-child [data-testid="stImage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 4px !important;
}
section.main [data-testid="column"]:first-child [data-testid="stImage"] img {
    max-width: 128px !important;
    width: 128px !important;
    display: block !important;
    filter: drop-shadow(0 12px 32px rgba(124, 58, 237, 0.22));
}

.mb-pitch-eyebrow {
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin: 0 0 14px 0;
}
.mb-pitch-title {
    font-size: clamp(34px, 4vw, 48px);
    line-height: 1.06;
    font-weight: 700;
    letter-spacing: -0.04em;
    margin: 0 0 12px 0;
    color: #fafafa !important;
}
.mb-pitch-tagline {
    font-size: 18px;
    font-weight: 500;
    color: #d4d4d8 !important;
    margin: 0 0 18px 0;
    letter-spacing: -0.02em;
    line-height: 1.35;
}
.mb-pitch-lead {
    color: #a1a1aa !important;
    font-size: 15px;
    line-height: 1.7;
    margin: 0 0 28px 0;
    max-width: 520px;
}
.mb-pitch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 520px;
    margin-bottom: 28px;
}
.mb-pitch-item {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, 0.65);
    border: 1px solid rgba(63, 63, 70, 0.75);
}
.mb-pitch-item strong {
    display: block;
    color: #e4e4e7 !important;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 4px;
}
.mb-pitch-item span {
    color: #71717a !important;
    font-size: 12px;
    line-height: 1.45;
}
.mb-pitch-proof {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    max-width: 520px;
}
.mb-pitch-pill {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    color: #a1a1aa !important;
    background: rgba(39, 39, 42, 0.8);
    border: 1px solid #3f3f46;
}

/* ── Login column (right) — compact panel ────────────────── */
section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(24, 24, 27, 0.92) !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 14px !important;
    padding: 22px 20px 18px 20px !important;
    max-width: 380px !important;
    margin-left: auto !important;
    margin-right: 0 !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 16px 48px rgba(0, 0, 0, 0.4) !important;
}

.mb-login-card-head {
    margin-bottom: 16px;
}
.mb-login-card-head h2 {
    color: #fafafa !important;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin: 0 0 4px 0;
}
.mb-login-card-head p {
    color: #71717a !important;
    font-size: 12px;
    margin: 0;
    line-height: 1.45;
}

/* Tabs — compact */
section.main [data-testid="column"]:last-child [data-testid="stTabs"] {
    margin-bottom: 2px;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 2px !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
    padding: 3px !important;
    min-height: 0 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 6px !important;
    color: #71717a !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
    min-height: 32px !important;
    background: transparent !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: #27272a !important;
    color: #fafafa !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-highlight"],
section.main [data-testid="column"]:last-child [data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

/* Google — subtle dark bar */
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    min-height: 36px;
    margin: 0 0 10px 0;
    padding: 0 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    color: #e4e4e7 !important;
    background: rgba(9, 9, 11, 0.8) !important;
    border: 1px solid #3f3f46 !important;
    box-sizing: border-box;
    transition: border-color 0.15s ease, background 0.15s ease;
}
.mb-login-google:hover {
    border-color: #52525b !important;
    background: #18181b !important;
    color: #fafafa !important;
}
.mb-login-google.disabled {
    opacity: 0.45;
    pointer-events: none;
}
.mb-login-google .g-icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}
.mb-login-trust {
    text-align: center;
    color: #52525b !important;
    font-size: 10px;
    margin: 0 0 12px 0;
    line-height: 1.4;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 12px 0;
    color: #52525b !important;
    font-size: 11px;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #3f3f46;
}

/* Compact form fields */
section.main [data-testid="column"]:last-child [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}
section.main [data-testid="column"]:last-child [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stWidgetLabel"] p,
section.main [data-testid="column"]:last-child label p {
    color: #a1a1aa !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    margin-bottom: 2px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] div[data-baseweb="input"],
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
    min-height: 36px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.18) !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] input,
section.main [data-testid="column"]:last-child [data-testid="stNumberInput"] input {
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 13px !important;
    padding: 6px 10px !important;
    min-height: 34px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stTextInput"] input::placeholder {
    color: #52525b !important;
}

/* Compact submit */
section.main [data-testid="column"]:last-child .stFormSubmitButton > button,
section.main [data-testid="column"]:last-child [data-testid="stFormSubmitButton"] > button,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"] {
    width: 100% !important;
    min-height: 36px !important;
    border-radius: 8px !important;
    border: 1px solid #6d28d9 !important;
    background: #7c3aed !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 2px 10px rgba(124, 58, 237, 0.28) !important;
    margin-top: 2px !important;
}
section.main [data-testid="column"]:last-child .stFormSubmitButton > button p,
section.main [data-testid="column"]:last-child form button[kind="primaryFormSubmit"] p {
    color: #ffffff !important;
    font-size: 13px !important;
}

section.main [data-testid="column"]:last-child .mb-login-captcha [data-testid="stFormSubmitButton"] > button {
    min-height: 36px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}

.mb-login-foot {
    text-align: center;
    color: #52525b !important;
    font-size: 10px;
    margin-top: 14px;
    line-height: 1.4;
}

section.main [data-testid="column"]:last-child [data-testid="stExpander"] {
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
    background: #09090b !important;
    margin-top: 8px !important;
}
section.main [data-testid="column"]:last-child [data-testid="stExpander"] summary {
    font-size: 11px !important;
    color: #71717a !important;
}
section.main [data-testid="stAlert"] {
    border-radius: 8px !important;
    margin-bottom: 10px !important;
    font-size: 13px !important;
}
section.main [data-testid="column"]:last-child .stCaption {
    font-size: 11px !important;
    color: #52525b !important;
}

@media (max-width: 900px) {
    section.main .block-container {
        padding: 24px 16px 40px 16px !important;
    }
    .mb-pitch-grid {
        grid-template-columns: 1fr;
    }
    section.main [data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
    section.main [data-testid="column"]:first-child [data-testid="stImage"] img {
        margin: 0 auto !important;
    }
    .mb-pitch-eyebrow,
    .mb-pitch-title,
    .mb-pitch-tagline,
    .mb-pitch-lead {
        text-align: center;
    }
    .mb-pitch-lead,
    .mb-pitch-grid,
    .mb-pitch-proof {
        margin-left: auto;
        margin-right: auto;
    }
    .mb-pitch-proof {
        justify-content: center;
    }
}
"""


def presentation_html() -> str:
    name = html.escape(APP_NAME)
    tagline = html.escape(APP_TAGLINE)
    positioning = html.escape(APP_POSITIONING)
    return f"""
<div class="mb-pitch">
    <p class="mb-pitch-eyebrow">Creator Operating System · B2B</p>
    <h1 class="mb-pitch-title">{name}</h1>
    <p class="mb-pitch-tagline">{tagline}</p>
    <p class="mb-pitch-lead">{positioning}
    Eine Plattform für Shorts &amp; Video, Image Studio, AI Chat und Code —
    ohne Tool-Zoo, mit klarem Token-Billing und Enterprise-Sessions.</p>
    <div class="mb-pitch-grid">
        <div class="mb-pitch-item">
            <strong>Produktion</strong>
            <span>Reels rendern, planen und veröffentlichen — in einem Flow.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>KI-Workspaces</strong>
            <span>Chat, Bild, Musik und Code — getrennt, aber verbunden.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>Teams &amp; Tokens</strong>
            <span>Transparente Kosten pro Aktion — planbar skalieren.</span>
        </div>
        <div class="mb-pitch-item">
            <strong>Sicher anmelden</strong>
            <span>Google OAuth oder klassische Zugangsdaten — deine Wahl.</span>
        </div>
    </div>
    <div class="mb-pitch-proof">
        <span class="mb-pitch-pill">Shorts &amp; Video</span>
        <span class="mb-pitch-pill">Image Studio</span>
        <span class="mb-pitch-pill">AI Chat</span>
        <span class="mb-pitch-pill">Code Studio</span>
        <span class="mb-pitch-pill">Queue &amp; Publish</span>
    </div>
</div>
"""


def login_card_head_html() -> str:
    return """
<div class="mb-login-card-head">
    <h2>Anmelden</h2>
    <p>Zugang zu deinem MaByte Workspace</p>
</div>
"""


def login_footer_html() -> str:
    return """
<div class="mb-login-foot">
    MaByte · Sichere Session · OAuth 2.0
</div>
"""


def auth_styles_bundle() -> str:
    return MB_THEME_VARS + LOGIN_CSS
