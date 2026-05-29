"""MaByte Login — Futuristisches B2B Gateway mit integriertem Header."""
from __future__ import annotations

import html

from config import APP_NAME
from ui.b2b_theme import MB_THEME_VARS

_SCOPE = ".stApp:has(.mb-auth-page)"


def _s(css: str) -> str:
    return _SCOPE + " " + css


def _brand_mark(initial: str) -> str:
    return f'<div class="mb-auth-mark" aria-hidden="true">{html.escape(initial)}</div>'


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
    max-width: 1280px !important;
    padding: 0 28px 36px 28px !important;
    min-height: 100vh !important;
}

section.main > div > div > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* First markdown = page shell header */
section.main > div > div > [data-testid="stVerticalBlock"] > [data-testid="stMarkdown"]:first-child {
    width: 100% !important;
    max-width: 100% !important;
}

section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 2.75rem !important;
    margin-top: 0 !important;
}

[data-testid="column"]:first-child {
    padding: 0 12px 0 0 !important;
    flex: 1.08 !important;
}

[data-testid="column"]:last-child {
    padding: 0 !important;
    flex: 0.92 !important;
    display: flex !important;
    justify-content: flex-end !important;
}

[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 440px !important;
}

.mb-access-wrap [data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;
    max-width: 440px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.mb-access-wrap [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    background: transparent !important;
}

.mb-mode-switch [data-testid="stHorizontalBlock"] {
    gap: 4px !important;
    background: rgba(0, 0, 0, 0.35) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    margin-bottom: 22px !important;
}

.mb-mode-switch .stButton > button,
.mb-mode-switch .stButton > button[kind="tertiary"] {
    min-height: 40px !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    background: transparent !important;
    color: #71717a !important;
}

.mb-mode-switch .stButton > button p {
    color: inherit !important;
    font-weight: 600 !important;
}

.mb-mode-login .stButton:first-of-type > button,
.mb-mode-register .stButton:last-of-type > button {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4) !important;
}

.mb-mode-login .stButton:first-of-type > button p,
.mb-mode-register .stButton:last-of-type > button p {
    color: #fff !important;
}

@media (max-width: 960px) {
    section.main .block-container { padding: 0 16px 28px 16px !important; }
    .mb-auth-header-inner { flex-wrap: wrap; gap: 12px !important; }
    .mb-auth-nav { display: none !important; }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 2rem !important;
    }
    [data-testid="column"]:first-child,
    [data-testid="column"]:last-child { flex: 1 !important; padding: 0 !important; }
    .mb-auth-hero { text-align: center; }
    .mb-auth-lead, .mb-auth-pillars, .mb-auth-quote { margin-left: auto; margin-right: auto; }
    .mb-auth-pillars { grid-template-columns: 1fr !important; }
}
""")
    + """
/* —— Atmosphere —— */
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
        radial-gradient(ellipse 50% 40% at 8% 0%, rgba(124, 58, 237, 0.2), transparent 50%),
        radial-gradient(ellipse 45% 40% at 95% 90%, rgba(99, 102, 241, 0.1), transparent 45%),
        linear-gradient(180deg, #09090b, #0a0a0e 40%, #09090b);
}

.mb-auth-page::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.28;
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 72px 72px;
    mask-image: linear-gradient(180deg, black 0%, transparent 85%);
}

/* —— Header —— */
.mb-auth-header {
    position: relative;
    z-index: 2;
    margin: 0 -28px 32px -28px;
    padding: 0 28px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(9, 9, 11, 0.65);
    backdrop-filter: blur(16px) saturate(1.3);
    -webkit-backdrop-filter: blur(16px) saturate(1.3);
}

.mb-auth-header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    min-height: 64px;
    max-width: 1280px;
    margin: 0 auto;
}

.mb-auth-header-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none !important;
}

.mb-auth-mark {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(145deg, #c084fc, #7c3aed 50%, #5b21b6);
    box-shadow: 0 0 0 1px rgba(255,255,255,0.1) inset, 0 6px 24px rgba(124,58,237,0.45);
}

.mb-auth-header-name {
    font-size: 16px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.03em;
}

.mb-auth-header-tag {
    font-size: 11px;
    color: #71717a !important;
    display: block;
    margin-top: 1px;
}

.mb-auth-nav {
    display: flex;
    align-items: center;
    gap: 28px;
}

.mb-auth-nav span {
    font-size: 13px;
    font-weight: 500;
    color: #71717a !important;
    letter-spacing: -0.01em;
}

.mb-auth-nav span:first-child {
    color: #e4e4e7 !important;
}

.mb-auth-header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.mb-auth-header-badge {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a78bfa !important;
    padding: 6px 10px;
    border-radius: 8px;
    border: 1px solid rgba(167, 139, 250, 0.35);
    background: rgba(124, 58, 237, 0.12);
}

.mb-auth-header-cta {
    font-size: 13px;
    font-weight: 600;
    color: #fafafa !important;
    padding: 8px 16px;
    border-radius: 10px;
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* —— Hero (Zukunft-Narrativ) —— */
.mb-auth-hero {
    position: relative;
    z-index: 1;
    max-width: 600px;
    padding-top: 4px;
}

.mb-auth-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px 6px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c4b5fd !important;
    background: rgba(124, 58, 237, 0.12);
    border: 1px solid rgba(124, 58, 237, 0.3);
    margin-bottom: 20px;
}

.mb-auth-eyebrow-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #a78bfa;
    box-shadow: 0 0 10px #7c3aed;
    animation: mb-auth-pulse 2s ease-in-out infinite;
}

@keyframes mb-auth-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.mb-auth-headline {
    font-size: clamp(34px, 3.8vw, 48px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.08;
    margin: 0 0 18px 0;
    color: #fafafa !important;
}

.mb-auth-headline .mb-auth-gradient {
    display: block;
    margin-top: 4px;
    background: linear-gradient(105deg, #fff 0%, #e9d5ff 30%, #a78bfa 60%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.mb-auth-lead {
    font-size: 16px;
    line-height: 1.65;
    color: #a1a1aa !important;
    margin: 0 0 24px 0;
    max-width: 540px;
}

.mb-auth-lead strong {
    color: #f4f4f5 !important;
    font-weight: 600;
}

.mb-auth-pillars {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 24px;
    max-width: 540px;
}

.mb-auth-pillar {
    padding: 14px 12px;
    border-radius: 14px;
    background: rgba(18, 18, 22, 0.7);
    border: 1px solid rgba(63, 63, 70, 0.6);
    text-align: center;
}

.mb-auth-pillar-num {
    display: block;
    font-size: 20px;
    font-weight: 800;
    color: #a78bfa !important;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}

.mb-auth-pillar-label {
    font-size: 10px;
    font-weight: 600;
    color: #71717a !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    line-height: 1.3;
}

.mb-auth-quote {
    position: relative;
    padding: 18px 20px 18px 22px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(24,24,27,0.6));
    border: 1px solid rgba(124, 58, 237, 0.2);
    max-width: 540px;
}

.mb-auth-quote::before {
    content: "\\201C";
    position: absolute;
    left: 14px;
    top: 6px;
    font-size: 40px;
    line-height: 1;
    color: rgba(167, 139, 250, 0.35);
    font-family: Georgia, serif;
}

.mb-auth-quote p {
    margin: 0;
    font-size: 14px;
    line-height: 1.55;
    color: #d4d4d8 !important;
    font-style: italic;
}

.mb-auth-quote cite {
    display: block;
    margin-top: 10px;
    font-size: 11px;
    font-style: normal;
    font-weight: 600;
    color: #71717a !important;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* —— Access card (Login) —— */
.mb-access-card {
    position: relative;
    z-index: 1;
    border-radius: 24px;
    padding: 1px;
    background: linear-gradient(
        145deg,
        rgba(167, 139, 250, 0.45),
        rgba(124, 58, 237, 0.15) 40%,
        rgba(63, 63, 70, 0.4)
    );
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 32px 80px rgba(0, 0, 0, 0.5),
        0 0 100px rgba(124, 58, 237, 0.08);
}

.mb-access-card-inner {
    border-radius: 23px;
    padding: 30px 28px 26px 28px;
    background: rgba(10, 10, 12, 0.92);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
}

.mb-access-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
    padding-bottom: 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.mb-access-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    color: #86efac !important;
    letter-spacing: 0.04em;
}

.mb-access-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 10px rgba(34, 197, 94, 0.6);
}

.mb-access-version {
    font-size: 10px;
    font-weight: 600;
    color: #52525b !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.mb-panel-kicker {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #a78bfa !important;
    margin: 0 0 6px 0;
}

.mb-panel-head { margin-bottom: 22px; }

.mb-panel-head h2 {
    color: #fafafa !important;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.035em;
    margin: 0 0 6px 0;
}

.mb-panel-head p {
    color: #71717a !important;
    font-size: 13px;
    margin: 0;
    line-height: 1.5;
}

.mb-field-label {
    display: block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #71717a !important;
    margin: 0 0 6px 2px;
}

.mb-field-group {
    margin-bottom: 4px;
}

.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    min-height: 48px;
    padding: 0 18px;
    margin-bottom: 12px;
    border-radius: 14px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    color: #f4f4f5 !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.2s ease;
}

.mb-login-google:hover {
    background: rgba(124, 58, 237, 0.12) !important;
    border-color: rgba(167, 139, 250, 0.45) !important;
    box-shadow: 0 0 32px rgba(124, 58, 237, 0.15);
}

.mb-login-google.disabled { opacity: 0.4; pointer-events: none; }
.mb-login-google .g-icon { width: 18px; height: 18px; }

.mb-login-hint {
    text-align: center;
    font-size: 11px;
    color: #52525b !important;
    margin: 0 0 20px 0;
}

.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 0 0 20px 0;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #52525b !important;
}

.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}

.mb-panel-foot {
    text-align: center;
    font-size: 10px;
    color: #52525b !important;
    margin-top: 22px;
    padding-top: 18px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    line-height: 1.5;
}

.mb-notice {
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 13px;
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
    g = ".stApp:has(.mb-auth-page)"
    return f"""
{g} [data-testid="stTextInput"] > div,
{g} [data-testid="stTextInput"] > div > div,
{g} [data-testid="stTextInput"] fieldset {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}

{g} [data-testid="stTextInput"] div[data-baseweb="input"],
{g} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: rgba(0, 0, 0, 0.45) !important;
    background-color: rgba(0, 0, 0, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    min-height: 48px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}

{g} [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
    border-color: rgba(167, 139, 250, 0.65) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2), 0 8px 24px rgba(124, 58, 237, 0.12) !important;
}}

{g} [data-testid="stTextInput"] input {{
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    padding-left: 4px !important;
}}

{g} [data-testid="stTextInput"] input::placeholder {{
    color: #52525b !important;
    opacity: 1 !important;
}}

{g} [data-testid="stTextInput"] input:-webkit-autofill {{
    -webkit-box-shadow: 0 0 0 1000px #0c0c0e inset !important;
    -webkit-text-fill-color: #fafafa !important;
}}

{g} .mb-login-form [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
}}

{g} .mb-field-group + [data-testid="stTextInput"],
{g} .mb-field-group + [data-testid="stNumberInput"] {{
    margin-bottom: 14px !important;
}}

{g} form button,
{g} .stFormSubmitButton button {{
    width: 100% !important;
    min-height: 50px !important;
    margin-top: 8px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: linear-gradient(135deg, #a855f7 0%, #7c3aed 45%, #6d28d9 100%) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.45), 0 0 0 1px rgba(255,255,255,0.08) inset !important;
    transition: transform 0.15s, box-shadow 0.2s !important;
}}

{g} form button:hover {{
    box-shadow: 0 12px 40px rgba(124, 58, 237, 0.55) !important;
}}

{g} form button p {{ color: #fff !important; }}

{g} .mb-login-captcha form button {{
    width: auto !important;
    min-height: 48px !important;
    margin-top: 0 !important;
    background: rgba(39, 39, 42, 0.9) !important;
    box-shadow: none !important;
}}

{g} [data-testid="stAlert"] {{ display: none !important; }}
"""


def header_html() -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    return f"""
<div class="mb-auth-page">
<header class="mb-auth-header">
    <div class="mb-auth-header-inner">
        <div class="mb-auth-header-brand">
            {_brand_mark(initial)}
            <div>
                <span class="mb-auth-header-name">{name}</span>
                <span class="mb-auth-header-tag">Die neue Ära der Creator-Produktion</span>
            </div>
        </div>
        <nav class="mb-auth-nav" aria-label="Navigation">
            <span>Plattform</span>
            <span>Zukunft</span>
            <span>Ökosystem</span>
        </nav>
        <div class="mb-auth-header-actions">
            <span class="mb-auth-header-badge">Gen 2 · Live</span>
            <span class="mb-auth-header-cta">Zugang</span>
        </div>
    </div>
</header>
"""


def hero_html() -> str:
    name = html.escape(APP_NAME)
    return f"""
<div class="mb-auth-hero">
    <div class="mb-auth-eyebrow">
        <span class="mb-auth-eyebrow-dot"></span>
        Grundstein · Neue Zukunft
    </div>
    <h1 class="mb-auth-headline">
        {name} ist der Grund
        <span class="mb-auth-gradient">für deine neue Zukunft.</span>
    </h1>
    <p class="mb-auth-lead">
        Während andere noch zwischen Tools wechseln, bauen Creator auf <strong>{name}</strong> —
        dem Betriebssystem, das Video, KI, Bild und Code zu einer einzigen Zukunfts-Engine vereint.
    </p>
    <div class="mb-auth-pillars">
        <div class="mb-auth-pillar">
            <span class="mb-auth-pillar-num">01</span>
            <span class="mb-auth-pillar-label">Eine Plattform</span>
        </div>
        <div class="mb-auth-pillar">
            <span class="mb-auth-pillar-num">02</span>
            <span class="mb-auth-pillar-label">Unendlicher Flow</span>
        </div>
        <div class="mb-auth-pillar">
            <span class="mb-auth-pillar-num">03</span>
            <span class="mb-auth-pillar-label">Deine Vision</span>
        </div>
    </div>
    <blockquote class="mb-auth-quote">
        <p>Die Zukunft gehört denen, die produzieren — nicht denen, die tabben.</p>
        <cite>— MaByte Manifest</cite>
    </blockquote>
</div>
"""


def access_card_open_html() -> str:
    return """
<div class="mb-access-wrap">
<div class="mb-access-card">
<div class="mb-access-card-inner">
<div class="mb-access-card-top">
    <span class="mb-access-status"><span class="mb-access-status-dot"></span> System bereit</span>
    <span class="mb-access-version">Secure Gateway</span>
</div>
"""


def access_card_close_html() -> str:
    return "</div></div></div></div>"


def panel_head_html(*, register: bool = False) -> str:
    if register:
        return """
<div class="mb-panel-head">
    <p class="mb-panel-kicker">Einstieg in die Zukunft</p>
    <h2>Dein Workspace wartet</h2>
    <p>Erstelle dein Konto — und gehör zu den ersten, die anders produzieren.</p>
</div>
"""
    return """
<div class="mb-panel-head">
    <p class="mb-panel-kicker">Zugang zum Ökosystem</p>
    <h2>Willkommen in der neuen Ära</h2>
    <p>Ein Login. Ein Workspace. Alles, was deine Zukunft als Creator braucht.</p>
</div>
"""


def panel_foot_html() -> str:
    return (
        '<div class="mb-panel-foot">'
        "Ende-zu-Ende verschlüsselt · Keine Passwörter bei Google · DSGVO-konform"
        "</div>"
    )


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}">{safe}</div>'


def page_close_html() -> str:
    return "</div>"


def auth_styles_bundle() -> str:
    return GATE_CSS + login_widget_css()
