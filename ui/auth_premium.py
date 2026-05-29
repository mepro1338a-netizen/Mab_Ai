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

@keyframes mb-aurora-drift {
    0%, 100% { opacity: 0.75; transform: scale(1) translate(0, 0); }
    50% { opacity: 1; transform: scale(1.04) translate(1%, -1%); }
}
@keyframes mb-pulse-glow {
    0%, 100% { opacity: 0.5; box-shadow: 0 0 12px #7c3aed; }
    50% { opacity: 1; box-shadow: 0 0 20px #a855f7; }
}
@keyframes mb-gradient-flow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
@keyframes mb-orbit {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@keyframes mb-shimmer-btn {
    0% { background-position: 200% center; }
    100% { background-position: -200% center; }
}
@keyframes mb-scan {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}

.mb-auth-page {
    position: relative;
    width: 100%;
    font-family: "Inter", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}
.mb-auth-page::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.22;
    background-image:
        linear-gradient(rgba(167,139,250,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(167,139,250,0.06) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(ellipse 90% 80% at 50% 20%, black 10%, transparent 70%);
}
.mb-auth-aurora {
    position: fixed;
    inset: -10%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 50% 40% at 8% 5%, rgba(124,58,237,0.38), transparent 55%),
        radial-gradient(ellipse 40% 35% at 92% 15%, rgba(59,130,246,0.2), transparent 50%),
        radial-gradient(ellipse 45% 40% at 50% 100%, rgba(109,40,217,0.18), transparent 55%),
        #050506;
    animation: mb-aurora-drift 16s ease-in-out infinite;
}

/* Header */
.mb-auth-header {
    position: relative;
    z-index: 2;
    margin: 0 -24px 28px -24px;
    padding: 0 24px;
    border-bottom: 1px solid rgba(167,139,250,0.1);
    background: linear-gradient(180deg, rgba(12,12,18,0.92), rgba(9,9,11,0.78));
    backdrop-filter: blur(20px) saturate(1.4);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
.mb-auth-header::after {
    content: "";
    position: absolute;
    bottom: 0; left: 5%; right: 5%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.55), rgba(59,130,246,0.35), transparent);
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
    background: linear-gradient(145deg, #f0abfc, #a855f7, #7c3aed, #5b21b6);
    background-size: 200% 200%;
    animation: mb-gradient-flow 5s ease infinite;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.15) inset, 0 8px 28px rgba(124,58,237,0.55);
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

/* Hero */
.mb-auth-hero { position: relative; z-index: 1; max-width: 540px; }
.mb-hero-orbit {
    position: absolute;
    top: -30px; right: 0;
    width: 160px; height: 160px;
    border-radius: 50%;
    border: 1px solid rgba(167,139,250,0.15);
    box-shadow: 0 0 50px rgba(124,58,237,0.12), inset 0 0 30px rgba(124,58,237,0.05);
    animation: mb-orbit 24s linear infinite;
    pointer-events: none;
}
.mb-hero-orbit::before {
    content: "";
    position: absolute;
    inset: 18px;
    border-radius: 50%;
    border: 1px dashed rgba(124,58,237,0.25);
}
.mb-auth-eyebrow {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 5px 12px 5px 9px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #c4b5fd !important;
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(167,139,250,0.3);
    box-shadow: 0 0 24px rgba(124,58,237,0.15);
    margin-bottom: 16px; white-space: nowrap;
}
.mb-auth-eyebrow-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #a78bfa;
    animation: mb-pulse-glow 2s ease-in-out infinite;
}
.mb-auth-headline {
    font-size: clamp(30px, 3.6vw, 44px);
    font-weight: 800; letter-spacing: -0.04em;
    line-height: 1.12; margin: 0 0 14px 0;
    color: #fafafa !important;
    text-shadow: 0 0 40px rgba(124,58,237,0.2);
}
.mb-auth-headline em {
    font-style: normal;
    background: linear-gradient(90deg, #fff, #f0abfc, #a78bfa, #6366f1);
    background-size: 200% auto;
    animation: mb-gradient-flow 6s ease infinite;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 20px rgba(167,139,250,0.35));
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
    background: linear-gradient(160deg, rgba(30,27,45,0.75), rgba(12,12,16,0.9));
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 28px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
    transition: transform 0.25s ease, border-color 0.25s, box-shadow 0.25s;
    position: relative; overflow: hidden;
}
.mb-auth-feat::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.5), transparent);
}
.mb-auth-feat:hover {
    transform: translateY(-2px);
    border-color: rgba(167,139,250,0.3);
    box-shadow: 0 12px 36px rgba(124,58,237,0.18);
}
.mb-auth-feat b {
    display: block; font-size: 13px; font-weight: 700;
    color: #fafafa !important; margin-bottom: 3px;
}
.mb-auth-feat span { font-size: 11px; color: #a1a1aa !important; line-height: 1.4; }
.mb-auth-manifest {
    padding: 14px 16px 14px 18px; border-radius: 14px;
    border: 1px solid rgba(167,139,250,0.22);
    border-left: 3px solid rgba(167,139,250,0.6);
    background: linear-gradient(90deg, rgba(124,58,237,0.12), rgba(124,58,237,0.04));
    box-shadow: 0 0 30px rgba(124,58,237,0.08);
    font-size: 13px; color: #d4d4d8 !important;
    line-height: 1.5; font-style: italic;
}

/* Access card — glass + glow */
.mb-access-card {
    position: relative; z-index: 1;
    border-radius: 22px; padding: 1px;
    background: linear-gradient(135deg, #c084fc, #7c3aed, #3b82f6, #7c3aed, #c084fc);
    background-size: 300% 300%;
    animation: mb-gradient-flow 8s ease infinite;
    box-shadow:
        0 0 0 1px rgba(255,255,255,0.06) inset,
        0 32px 80px rgba(0,0,0,0.55),
        0 0 100px rgba(124,58,237,0.2);
}
.mb-access-card-inner {
    position: relative;
    border-radius: 21px;
    padding: 26px 24px 22px 24px;
    background: linear-gradient(180deg, rgba(14,14,20,0.95), rgba(6,6,8,0.98));
    backdrop-filter: blur(28px) saturate(1.3);
    overflow: hidden;
}
.mb-access-card-inner::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 40%;
    background: linear-gradient(180deg, rgba(167,139,250,0.06), transparent);
    pointer-events: none;
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
/* Kill Streamlit light inputs completely */
{g} [data-testid="stForm"] {{
    border: none !important; padding: 0 !important; background: transparent !important;
}}
{g} [data-testid="stWidgetLabel"],
{g} label[data-testid="stWidgetLabel"] {{
    display: none !important; height: 0 !important; margin: 0 !important;
}}
{g} [data-testid="stTextInput"],
{g} [data-testid="stNumberInput"] {{
    margin-bottom: 12px !important; background: transparent !important;
}}
{g} [data-testid="stTextInput"] > div,
{g} [data-testid="stTextInput"] > div > div,
{g} [data-testid="stTextInput"] fieldset,
{g} [data-testid="stNumberInput"] > div,
{g} [data-testid="stNumberInput"] > div > div {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important; padding: 0 !important; box-shadow: none !important;
}}
{g} div[data-baseweb="input"],
{g} [data-testid="stTextInput"] div[data-baseweb="input"],
{g} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: rgba(8,8,12,0.95) !important;
    background-color: rgba(8,8,12,0.95) !important;
    border: 1px solid rgba(167,139,250,0.18) !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.03) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
{g} div[data-baseweb="input"]:focus-within,
{g} [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
    border-color: rgba(167,139,250,0.65) !important;
    box-shadow:
        0 0 0 3px rgba(124,58,237,0.22),
        0 0 24px rgba(124,58,237,0.15),
        inset 0 2px 10px rgba(0,0,0,0.45) !important;
}}
{g} [data-testid="stTextInput"] input,
{g} [data-testid="stNumberInput"] input,
{g} input[type="text"],
{g} input[type="password"] {{
    background: transparent !important;
    background-color: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    font-family: inherit !important;
    caret-color: #c4b5fd !important;
}}
{g} [data-testid="stTextInput"] input::placeholder {{
    color: #52525b !important; opacity: 1 !important;
}}
{g} [data-testid="stTextInput"] input:-webkit-autofill,
{g} [data-testid="stTextInput"] input:-webkit-autofill:focus {{
    -webkit-box-shadow: 0 0 0 1000px #08080c inset !important;
    -webkit-text-fill-color: #fafafa !important;
    transition: background-color 9999s ease-out 0s;
}}
{g} [data-testid="stTextInput"] button {{
    color: #71717a !important; background: transparent !important;
}}

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
    width: 100% !important; min-height: 50px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    background: linear-gradient(135deg, #e879f9, #a855f7, #7c3aed, #6d28d9) !important;
    background-size: 250% auto !important;
    animation: mb-shimmer-btn 5s linear infinite !important;
    color: #fff !important; font-weight: 800 !important; font-size: 14px !important;
    font-family: inherit !important;
    box-shadow: 0 10px 36px rgba(124,58,237,0.5), 0 0 40px rgba(124,58,237,0.15) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.25) !important;
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
        f'<div class="mb-hero-orbit" aria-hidden="true"></div>'
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
