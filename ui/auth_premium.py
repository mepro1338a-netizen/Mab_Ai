"""MaByte login — centered card layout, CSS scoped to section.main only."""
from __future__ import annotations

import html

from config import APP_NAME, APP_TAGLINE
from ui.b2b_theme import MB_THEME_VARS

LOGIN_CSS = """
/* Background — no fixed overlays (breaks Streamlit hydration on Railway) */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {
    background: linear-gradient(165deg, #09090b 0%, #121215 45%, #09090b 100%) !important;
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

/* Centered login column */
section.main .block-container {
    max-width: 440px !important;
    padding: 48px 20px 64px 20px !important;
    margin: 0 auto !important;
}

/* Logo */
section.main [data-testid="stImage"] {
    text-align: center;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
section.main [data-testid="stImage"] img {
    max-width: 152px !important;
    width: 152px !important;
    margin: 0 auto 8px auto !important;
    display: block !important;
}

/* Intro text (markdown) */
section.main .mb-login-intro h1 {
    color: #fafafa !important;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.03em;
    text-align: center;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
section.main .mb-login-intro p {
    color: #71717a !important;
    font-size: 14px;
    text-align: center;
    margin: 0 0 28px 0;
    line-height: 1.55;
}

/* Card — Streamlit bordered container */
section.main [data-testid="stVerticalBlockBorderWrapper"] {
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 16px !important;
    padding: 28px 24px 24px 24px !important;
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 20px 50px rgba(0, 0, 0, 0.45) !important;
}

/* Tabs */
section.main [data-testid="stTabs"] {
    margin-bottom: 4px;
}
section.main [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    padding: 4px !important;
}
section.main [data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #71717a !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    background: transparent !important;
}
section.main [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: #27272a !important;
    color: #fafafa !important;
}
section.main [data-testid="stTabs"] [data-baseweb="tab-highlight"],
section.main [data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

/* Google OAuth link */
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 46px;
    margin: 0 0 20px 0;
    padding: 0 16px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    color: #18181b !important;
    background: #fafafa !important;
    border: 1px solid #e4e4e7 !important;
    box-sizing: border-box;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}
.mb-login-google:hover {
    background: #ffffff !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
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
.mb-login-trust {
    text-align: center;
    color: #52525b !important;
    font-size: 11px;
    margin: -12px 0 18px 0;
    line-height: 1.45;
}
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 18px 0;
    color: #52525b !important;
    font-size: 12px;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #3f3f46;
}

/* Form fields */
section.main [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}
section.main [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 16px !important;
}
section.main [data-testid="stTextInput"] label p,
section.main [data-testid="stNumberInput"] label p,
section.main [data-testid="stWidgetLabel"] p {
    color: #a1a1aa !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
section.main [data-testid="stTextInput"] div[data-baseweb="input"],
section.main [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: #09090b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}
section.main [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
section.main [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2) !important;
}
section.main [data-testid="stTextInput"] input,
section.main [data-testid="stNumberInput"] input {
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
}
section.main [data-testid="stTextInput"] input::placeholder {
    color: #52525b !important;
}

/* Submit */
section.main .stFormSubmitButton > button,
section.main [data-testid="stFormSubmitButton"] > button,
section.main form button[kind="primaryFormSubmit"] {
    width: 100% !important;
    min-height: 46px !important;
    border-radius: 10px !important;
    border: 1px solid #6d28d9 !important;
    background: #7c3aed !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3) !important;
}
section.main .stFormSubmitButton > button:hover,
section.main form button[kind="primaryFormSubmit"]:hover {
    background: #6d28d9 !important;
    color: #ffffff !important;
}
section.main .stFormSubmitButton > button p,
section.main form button[kind="primaryFormSubmit"] p {
    color: #ffffff !important;
}

/* Captcha refresh button */
section.main .mb-login-captcha [data-testid="stFormSubmitButton"] > button {
    min-height: 44px !important;
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}

/* Footer */
.mb-login-footer {
    text-align: center;
    color: #52525b !important;
    font-size: 12px;
    margin-top: 24px;
    line-height: 1.5;
}
.mb-login-footer a {
    color: #a78bfa !important;
    text-decoration: none;
}

section.main [data-testid="stExpander"] {
    border: 1px solid #3f3f46 !important;
    border-radius: 10px !important;
    background: #09090b !important;
    margin-top: 12px !important;
}
section.main [data-testid="stAlert"] {
    border-radius: 10px !important;
    margin-bottom: 12px !important;
}

@media (max-width: 520px) {
    section.main .block-container {
        padding: 32px 16px 48px 16px !important;
    }
    section.main [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 22px 18px 18px 18px !important;
    }
}
"""


def login_intro_html() -> str:
    name = html.escape(APP_NAME)
    tagline = html.escape(APP_TAGLINE)
    return f"""
<div class="mb-login-intro">
    <h1>Bei {name} anmelden</h1>
    <p>{tagline}<br>Video, Bild, Code und KI-Chat — alles in einem Workspace.</p>
</div>
"""


def login_footer_html() -> str:
    return """
<div class="mb-login-footer">
    <strong style="color:#71717a;">MaByte</strong> · Sichere Session · OAuth 2.0
</div>
"""


def auth_styles_bundle() -> str:
    return MB_THEME_VARS + LOGIN_CSS
