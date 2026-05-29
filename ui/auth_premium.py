"""MaByte Enterprise Login — Linear / Stripe grade B2B gateway."""
from __future__ import annotations

import html

from config import APP_NAME

_G = ".stApp:has(.mb-auth-page)"


def _s(css: str) -> str:
    return _G + " " + css


# Design tokens — #050816 #0A1024 #7B61FF #A855F7 #5B8CFF
GATE_CSS = (
    """
:root {
    --mb-bg: #050816;
    --mb-bg-2: #0A1024;
    --mb-violet: #7B61FF;
    --mb-purple: #A855F7;
    --mb-blue: #5B8CFF;
    --mb-line: rgba(255, 255, 255, 0.08);
    --mb-glow: 0 0 40px rgba(123, 97, 255, 0.25);
    --mb-radius: 24px;
}
html { color-scheme: dark !important; }
.stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
    --primary-color: #7B61FF !important;
    --background-color: #050816 !important;
    --text-color: #fafafa !important;
}
.stApp:has(.mb-auth-page),
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"],
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"] > section {
    background: var(--mb-bg) !important;
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
"""
+ _s("""
section.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] { gap: 0 !important; }
section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 0 !important;
    min-height: calc(100vh - 140px) !important;
}
[data-testid="column"]:first-child {
    flex: 0 0 55% !important;
    max-width: 55% !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="column"]:last-child {
    flex: 0 0 45% !important;
    max-width: 45% !important;
    padding: 24px 40px 24px 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: visible !important;
}
[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 520px !important;
    gap: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}
[data-testid="column"]:last-child [data-testid="stElementContainer"],
[data-testid="column"]:last-child [data-testid="stMarkdownContainer"],
[data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
@media (max-width: 1024px) {
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        min-height: auto !important;
    }
    [data-testid="column"]:first-child,
    [data-testid="column"]:last-child {
        flex: 1 1 auto !important;
        max-width: 100% !important;
    }
    [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
        max-width: 100% !important;
        padding: 0 20px 32px !important;
    }
    .mb-feat-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .mb-stats-row { flex-wrap: wrap !important; gap: 16px !important; }
}
@media (max-width: 640px) {
    .mb-feat-grid { grid-template-columns: 1fr !important; }
    .mb-topbar { padding: 14px 20px !important; }
    .mb-topbar-claim { display: none !important; }
    .mb-topbar-live { display: none !important; }
    .mb-hero { padding: 16px 20px 24px 20px !important; }
}
""")
+ """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.mb-auth-page {
    position: relative;
    width: 100%;
    min-height: 100vh;
    font-family: "Inter", system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #fafafa;
}

/* ── Background: stadium + space ── */
.mb-auth-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-color: #050816;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% 100%, rgba(123, 97, 255, 0.18), transparent 60%),
        radial-gradient(ellipse 60% 40% at 20% 20%, rgba(168, 85, 247, 0.22), transparent 55%),
        radial-gradient(ellipse 50% 35% at 85% 15%, rgba(91, 140, 255, 0.16), transparent 50%),
        radial-gradient(ellipse 100% 60% at 50% 110%, rgba(10, 16, 36, 0.9), transparent 70%),
        linear-gradient(180deg, #050816 0%, #0A1024 45%, #050816 100%);
}
.mb-auth-bg::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 120% 40% at 50% 95%, rgba(123, 97, 255, 0.12) 0%, transparent 55%),
        url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1920&q=80&auto=format&fit=crop") center bottom / cover no-repeat;
    opacity: 0.35;
    mix-blend-mode: luminosity;
    mask-image: linear-gradient(to top, black 0%, transparent 65%);
    -webkit-mask-image: linear-gradient(to top, black 0%, transparent 65%);
}
.mb-auth-stars {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.4;
    background-image:
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1px 1px at 30% 65%, rgba(255,255,255,0.35), transparent),
        radial-gradient(1px 1px at 55% 15%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 70% 45%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1px 1px at 85% 75%, rgba(255,255,255,0.45), transparent),
        radial-gradient(1px 1px at 92% 30%, rgba(255,255,255,0.35), transparent);
}

/* ── Top bar ── */
.mb-topbar {
    position: relative;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 40px;
    max-width: 100%;
    border-bottom: 1px solid var(--mb-line);
    background: rgba(5, 8, 22, 0.72);
    backdrop-filter: blur(16px);
}
.mb-topbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.mb-topbar-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.mb-topbar-claim {
    font-size: 12px;
    font-weight: 500;
    color: #64748b !important;
    letter-spacing: 0.01em;
}
.mb-logo-mark {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(135deg, #A855F7 0%, #7B61FF 50%, #5B8CFF 100%);
    box-shadow: var(--mb-glow), inset 0 1px 0 rgba(255,255,255,0.2);
}
.mb-topbar-name {
    font-size: 17px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.03em;
}
.mb-topbar-lang {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 500;
    color: #94a3b8 !important;
    padding: 8px 14px;
    border-radius: 10px;
    border: 1px solid var(--mb-line);
    background: rgba(10, 16, 36, 0.6);
    backdrop-filter: blur(12px);
}
.mb-topbar-live {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #86efac !important;
    padding: 8px 14px;
    border-radius: 10px;
    border: 1px solid rgba(34, 197, 94, 0.25);
    background: rgba(34, 197, 94, 0.08);
    margin-left: 10px;
}
.mb-topbar-live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.7);
}
.mb-topbar-actions {
    display: flex;
    align-items: center;
    gap: 0;
}

/* ── Hero left ── */
.mb-hero {
    position: relative;
    z-index: 2;
    padding: 24px 48px 32px 48px;
    max-width: 100%;
    width: 100%;
}
.mb-hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    margin-bottom: 24px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8 !important;
    border: 1px solid var(--mb-line);
    background: rgba(10, 16, 36, 0.55);
    backdrop-filter: blur(12px);
}
.mb-hero-pill-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #7B61FF;
    box-shadow: 0 0 6px rgba(123, 97, 255, 0.8);
}
.mb-hero-title {
    font-size: clamp(36px, 4.5vw, 56px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.08;
    margin: 0 0 20px 0;
    color: #fafafa !important;
}
.mb-hero-title .mb-grad {
    display: block;
    background: linear-gradient(135deg, #A855F7 0%, #7B61FF 45%, #5B8CFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.mb-hero-sub {
    font-size: 16px;
    line-height: 1.7;
    color: #94a3b8 !important;
    margin: 0 0 32px 0;
    max-width: 540px;
}

/* Feature cards — 4 col glass row */
.mb-feat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 28px;
}
.mb-feat-card {
    padding: 18px 16px;
    border-radius: var(--mb-radius);
    background: rgba(10, 16, 36, 0.45);
    border: 1px solid var(--mb-line);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: var(--mb-glow), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
}
.mb-feat-card:hover {
    border-color: rgba(123, 97, 255, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 0 48px rgba(123, 97, 255, 0.3), inset 0 1px 0 rgba(255,255,255,0.06);
}
.mb-feat-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
    background: linear-gradient(135deg, rgba(168,85,247,0.25), rgba(91,140,255,0.15));
    border: 1px solid rgba(123, 97, 255, 0.25);
    font-size: 16px;
    line-height: 1;
}
.mb-feat-title {
    display: block;
    font-size: 13px;
    font-weight: 700;
    color: #fafafa !important;
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}
.mb-feat-desc {
    font-size: 11px;
    color: #64748b !important;
    line-height: 1.45;
}

/* Stats row */
.mb-stats-row {
    display: flex;
    align-items: center;
    gap: 28px;
    flex-wrap: nowrap;
}
.mb-stat {
    display: flex;
    align-items: center;
    gap: 10px;
}
.mb-stat-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    background: rgba(123, 97, 255, 0.12);
    border: 1px solid rgba(123, 97, 255, 0.2);
}
.mb-stat-val {
    display: block;
    font-size: 15px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.02em;
}
.mb-stat-label {
    display: block;
    font-size: 11px;
    color: #64748b !important;
}

/* ── Glass login card ── */
.mb-glass-wrap {
    position: relative;
    z-index: 2;
    width: 100%;
}
.mb-glass-wrap::before {
    content: "";
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    width: 70%;
    height: 80px;
    background: radial-gradient(ellipse, rgba(123, 97, 255, 0.45), transparent 70%);
    filter: blur(24px);
    z-index: -1;
    pointer-events: none;
}
.mb-glass-card {
    border-radius: var(--mb-radius);
    padding: 1px;
    background: linear-gradient(160deg, rgba(168,85,247,0.5), rgba(91,140,255,0.15), rgba(123,97,255,0.3));
    box-shadow: var(--mb-glow), 0 32px 80px rgba(0, 0, 0, 0.55);
    overflow: visible;
}
.mb-glass-inner {
    position: relative;
    border-radius: calc(var(--mb-radius) - 1px);
    padding: 36px 36px 32px 36px;
    background: rgba(10, 16, 36, 0.72);
    backdrop-filter: blur(24px) saturate(1.4);
    -webkit-backdrop-filter: blur(24px) saturate(1.4);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}
.mb-glass-inner::before {
    content: "";
    position: absolute;
    top: 0;
    left: 10%;
    right: 10%;
    height: 2px;
    border-radius: 0 0 4px 4px;
    background: linear-gradient(90deg, transparent, #A855F7, #5B8CFF, transparent);
    box-shadow: 0 0 24px rgba(168, 85, 247, 0.7);
}
.mb-panel-logo {
    width: 48px;
    height: 48px;
    margin: 0 auto 16px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, #A855F7, #7B61FF, #5B8CFF);
    box-shadow: var(--mb-glow);
    font-size: 20px;
    font-weight: 800;
    color: #fff !important;
}
.mb-panel-title {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fafafa !important;
    margin: 0 0 6px 0;
    text-align: center;
}
.mb-panel-sub {
    font-size: 14px;
    color: #64748b !important;
    margin: 0 0 24px 0;
    line-height: 1.45;
    text-align: center;
}

/* Google + divider */
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    min-height: 48px;
    padding: 0 16px;
    margin-bottom: 0;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    color: #fafafa !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid var(--mb-line) !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.mb-login-google:hover {
    border-color: rgba(123, 97, 255, 0.45) !important;
    background: rgba(123, 97, 255, 0.08) !important;
    box-shadow: 0 0 24px rgba(123, 97, 255, 0.2);
}
.mb-login-google.disabled { opacity: 0.4; pointer-events: none; }
.mb-login-google .g-icon { width: 18px; height: 18px; flex-shrink: 0; }
.mb-login-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 20px 0 20px 0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #475569 !important;
}
.mb-login-divider::before,
.mb-login-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--mb-line);
}

/* Form extras row */
.mb-form-extras {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 4px 0 16px 0;
    min-height: 24px;
}
.mb-forgot-link {
    font-size: 13px;
    font-weight: 500;
    color: #7B61FF !important;
    text-decoration: none !important;
    transition: color 0.2s;
}
.mb-forgot-link:hover { color: #A855F7 !important; }

/* Panel switch + foot */
.mb-panel-switch {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    color: #64748b !important;
}
.mb-panel-switch-note {
    display: inline;
    margin-right: 4px;
}

/* Page footer */
.mb-page-foot {
    position: relative;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    padding: 16px 40px 24px 40px;
    font-size: 12px;
    color: #475569 !important;
    border-top: 1px solid var(--mb-line);
    background: rgba(5, 8, 22, 0.85);
    backdrop-filter: blur(12px);
}
.mb-page-foot-links {
    display: flex;
    align-items: center;
    gap: 8px;
}
.mb-page-foot-links a {
    color: #64748b !important;
    text-decoration: none !important;
    transition: color 0.2s;
}
.mb-page-foot-links a:hover { color: #94a3b8 !important; }
.mb-page-foot-sep { color: #334155 !important; }

/* Notices */
.mb-notice {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
}
.mb-notice::before {
    flex-shrink: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    content: "";
}
.mb-notice-error {
    color: #fecaca !important;
    background: rgba(127, 29, 29, 0.35);
    border: 1px solid rgba(248, 113, 113, 0.3);
}
.mb-notice-error::before { background: #f87171; box-shadow: 0 0 8px rgba(248,113,113,0.5); }
.mb-notice-success {
    color: #bbf7d0 !important;
    background: rgba(20, 83, 45, 0.35);
    border: 1px solid rgba(74, 222, 128, 0.3);
}
.mb-notice-success::before { background: #4ade80; box-shadow: 0 0 8px rgba(74,222,128,0.5); }
.mb-notice-info {
    color: #bfdbfe !important;
    background: rgba(30, 58, 138, 0.35);
    border: 1px solid rgba(96, 165, 250, 0.3);
}
.mb-notice-info::before { background: #60a5fa; }
.mb-captcha-label {
    font-size: 12px;
    color: #64748b !important;
    margin: 0 0 8px 0;
}
"""
)


def widget_css() -> str:
    g = _G
    return f"""
{g} [data-testid="stForm"] {{
    border: none !important; padding: 0 !important; background: transparent !important;
}}
{g} [data-testid="stTextInput"] [data-testid="stWidgetLabel"],
{g} [data-testid="stNumberInput"] [data-testid="stWidgetLabel"],
{g} label[data-testid="stWidgetLabel"]:has(+ div [data-baseweb="input"]) {{ display: none !important; }}
{g} [data-testid="stTextInput"],
{g} [data-testid="stNumberInput"] {{ margin-bottom: 14px !important; }}
{g} [data-testid="stTextInput"] > div,
{g} [data-testid="stTextInput"] > div > div,
{g} [data-testid="stTextInput"] fieldset,
{g} [data-testid="stNumberInput"] > div,
{g} [data-testid="stNumberInput"] > div > div {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}}
{g} div[data-baseweb="input"],
{g} [data-testid="stTextInput"] div[data-baseweb="input"],
{g} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: rgba(5, 8, 22, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3) !important;
}}
{g} div[data-baseweb="input"]:focus-within {{
    border-color: rgba(123, 97, 255, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(123, 97, 255, 0.15), 0 0 24px rgba(123, 97, 255, 0.12) !important;
}}
{g} [data-testid="stTextInput"] input,
{g} [data-testid="stNumberInput"] input {{
    background: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    font-family: inherit !important;
    caret-color: #A855F7 !important;
    padding-left: 14px !important;
}}
{g} [data-testid="stTextInput"] input::placeholder {{ color: #475569 !important; opacity: 1 !important; }}
{g} [data-testid="stTextInput"] input:-webkit-autofill,
{g} [data-testid="stTextInput"] input:-webkit-autofill:focus {{
    -webkit-box-shadow: 0 0 0 1000px #050816 inset !important;
    -webkit-text-fill-color: #fafafa !important;
}}
{g} [data-testid="stTextInput"] button {{ color: #64748b !important; background: transparent !important; }}

/* Remember me checkbox */
{g} [data-testid="stCheckbox"] {{
    margin: 0 !important;
    padding: 0 !important;
}}
{g} [data-testid="stCheckbox"] label {{
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 13px !important;
    color: #94a3b8 !important;
    cursor: pointer !important;
}}
{g} [data-testid="stCheckbox"] label span,
{g} [data-testid="stCheckbox"] label p {{
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
{g} [data-testid="stCheckbox"] [data-baseweb="checkbox"] {{
    background: rgba(5, 8, 22, 0.85) !important;
    border-color: rgba(255,255,255,0.12) !important;
}}
{g} [data-testid="stCheckbox"] [data-baseweb="checkbox"]:hover {{
    border-color: rgba(123, 97, 255, 0.45) !important;
}}

/* Extras row layout */
{g} [data-testid="stForm"] [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
    gap: 8px !important;
    margin: 4px 0 18px 0 !important;
}}
{g} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child {{
    flex: 1 !important; max-width: none !important; padding: 0 !important;
    display: flex !important; align-items: center !important;
}}
{g} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child {{
    flex: 0 0 auto !important; max-width: none !important; padding: 0 !important;
    display: flex !important; justify-content: flex-end !important; align-items: center !important;
}}
{g} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child [data-testid="stMarkdownContainer"] {{
    width: auto !important;
}}
{g} .mb-forgot-link {{
    white-space: nowrap !important;
    display: inline-block !important;
}}

/* Primary CTA */
{g} form button,
{g} .stFormSubmitButton button {{
    width: 100% !important;
    min-height: 48px !important;
    margin-top: 0 !important;
    border-radius: 12px !important;
    border: none !important;
    background: linear-gradient(135deg, #A855F7 0%, #7B61FF 50%, #5B8CFF 100%) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    font-family: inherit !important;
    box-shadow: var(--mb-glow), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: box-shadow 0.2s, transform 0.15s !important;
}}
{g} form button:hover {{
    box-shadow: 0 0 48px rgba(123, 97, 255, 0.4), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transform: translateY(-1px) !important;
}}
{g} form button p {{ color: #fff !important; font-weight: 700 !important; }}

/* Mode switch link button */
{g} .mb-panel-switch .stButton > button,
{g} .mb-panel-switch .stButton > button[kind="tertiary"] {{
    display: inline !important;
    width: auto !important;
    min-height: auto !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #7B61FF !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}}
{g} .mb-panel-switch .stButton > button:hover {{
    color: #A855F7 !important;
    background: transparent !important;
    box-shadow: none !important;
    transform: none !important;
}}
{g} .mb-panel-switch .stButton > button p {{
    color: #7B61FF !important;
    font-weight: 600 !important;
}}

{g} [data-testid="stAlert"] {{ display: none !important; }}
{g} [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}

/* Captcha refresh — small icon button */
{g} [data-testid="stForm"] [data-testid="stHorizontalBlock"] .stButton:last-child button {{
    min-height: 48px !important;
    width: 100% !important;
    background: rgba(5, 8, 22, 0.85) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}}
"""


def _logo_mark(initial: str) -> str:
    return f'<div class="mb-logo-mark" aria-hidden="true">{html.escape(initial)}</div>'


def _hex_logo(initial: str) -> str:
    return f'<div class="mb-panel-logo" aria-hidden="true">{html.escape(initial)}</div>'


def page_open_html(mode_class: str = "") -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    extra = html.escape(mode_class)
    return (
        f'<div class="mb-auth-page {extra}">'
        f'<div class="mb-auth-bg" aria-hidden="true"></div>'
        f'<div class="mb-auth-stars" aria-hidden="true"></div>'
        f'<div class="mb-topbar">'
        f'<div class="mb-topbar-brand">{_logo_mark(initial)}'
        f'<div class="mb-topbar-text">'
        f'<span class="mb-topbar-name">{name}</span>'
        f'<span class="mb-topbar-claim">One system. Infinite intelligence.</span>'
        f'</div></div>'
        f'<div class="mb-topbar-actions">'
        f'<span class="mb-topbar-lang">🌐 DE</span>'
        f'<span class="mb-topbar-live">'
        f'<span class="mb-topbar-live-dot"></span>Live</span>'
        f'</div></div>'
    )


def hero_html() -> str:
    return (
        '<div class="mb-hero">'
        '<div class="mb-hero-pill">'
        '<span class="mb-hero-pill-dot"></span>'
        'CREATOR · FOOTBALL · AUTOMATION'
        '</div>'
        '<h1 class="mb-hero-title">'
        'One system.<br>'
        '<span class="mb-grad">Infinite intelligence.</span>'
        '</h1>'
        '<p class="mb-hero-sub">'
        'MaByte vereint Creator AI, Football Intelligence, '
        'Automatisierung und Publishing in einer Plattform.'
        '</p>'
        '<div class="mb-feat-grid">'
        '<div class="mb-feat-card">'
        '<div class="mb-feat-icon" aria-hidden="true">🎬</div>'
        '<span class="mb-feat-title">AI Reels Studio</span>'
        '<span class="mb-feat-desc">Shorts &amp; Video mit KI-Power</span>'
        '</div>'
        '<div class="mb-feat-card">'
        '<div class="mb-feat-icon" aria-hidden="true">⚽</div>'
        '<span class="mb-feat-title">Football Intelligence</span>'
        '<span class="mb-feat-desc">Analyse, Insights &amp; Predictions</span>'
        '</div>'
        '<div class="mb-feat-card">'
        '<div class="mb-feat-icon" aria-hidden="true">🚀</div>'
        '<span class="mb-feat-title">Auto Publishing</span>'
        '<span class="mb-feat-desc">Multi-Plattform in einem Flow</span>'
        '</div>'
        '<div class="mb-feat-card">'
        '<div class="mb-feat-icon" aria-hidden="true">👥</div>'
        '<span class="mb-feat-title">Team Workspaces</span>'
        '<span class="mb-feat-desc">Collaboration für Agenturen</span>'
        '</div>'
        '</div>'
        '<div class="mb-stats-row">'
        '<div class="mb-stat">'
        '<div class="mb-stat-icon" aria-hidden="true">👤</div>'
        '<div><span class="mb-stat-val">10.000+</span>'
        '<span class="mb-stat-label">Creator</span></div>'
        '</div>'
        '<div class="mb-stat">'
        '<div class="mb-stat-icon" aria-hidden="true">▶</div>'
        '<div><span class="mb-stat-val">1 Mio+</span>'
        '<span class="mb-stat-label">Videos erstellt</span></div>'
        '</div>'
        '<div class="mb-stat">'
        '<div class="mb-stat-icon" aria-hidden="true">🏢</div>'
        '<div><span class="mb-stat-val">500+</span>'
        '<span class="mb-stat-label">Teams &amp; Unternehmen</span></div>'
        '</div>'
        '</div>'
        '</div>'
    )


def panel_shell_html(*, register: bool) -> str:
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    if register:
        return (
            '<div class="mb-glass-wrap"><div class="mb-glass-card"><div class="mb-glass-inner">'
            f'{_hex_logo(initial)}'
            '<h2 class="mb-panel-title">Workspace anlegen</h2>'
            '<p class="mb-panel-sub">Erstelle dein Konto und starte in Minuten.</p>'
        )
    return (
        '<div class="mb-glass-wrap"><div class="mb-glass-card"><div class="mb-glass-inner">'
        f'{_hex_logo(initial)}'
        '<h2 class="mb-panel-title">Willkommen zurück</h2>'
        '<p class="mb-panel-sub">Schön, dass du wieder da bist.</p>'
    )


def panel_close_html() -> str:
    return '</div></div></div>'


def forgot_password_html() -> str:
    return (
        '<a class="mb-forgot-link" href="#" '
        'onclick="return false;" title="Passwort-Reset folgt">'
        'Passwort vergessen?'
        '</a>'
    )


def notice_html(level: str, message: str) -> str:
    safe = html.escape(message)
    return f'<div class="mb-notice mb-notice-{html.escape(level)}" role="alert">{safe}</div>'


def page_close_html() -> str:
    year = "2026"
    return (
        '<footer class="mb-page-foot">'
        f'<span>© {year} MaByte GmbH · Alle Rechte vorbehalten.</span>'
        '<div class="mb-page-foot-links">'
        '<a href="#">Datenschutz</a>'
        '<span class="mb-page-foot-sep">|</span>'
        '<a href="#">AGB</a>'
        '<span class="mb-page-foot-sep">|</span>'
        '<a href="#">Impressum</a>'
        '<span class="mb-page-foot-sep">|</span>'
        '<a href="#">Support</a>'
        '</div>'
        '</footer>'
        '</div>'
    )


def auth_styles_bundle() -> str:
    return GATE_CSS + widget_css()
