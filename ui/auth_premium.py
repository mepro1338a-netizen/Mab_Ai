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
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"],
.stApp:has(.mb-auth-page) [data-testid="stAppViewContainer"] > section,
.stApp:has(.mb-auth-page) [data-testid="stMainBlockContainer"],
.stApp:has(.mb-auth-page) [data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
}
"""
+ _s("""
section.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding-top: 52px !important;
    padding-bottom: 44px !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] > [data-testid="stMarkdownContainer"]:first-child {
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}
section.main > div > div > [data-testid="stVerticalBlock"] > [data-testid="stMarkdownContainer"]:last-child {
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}
section.main > div > div > [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 0 !important;
    min-height: 0 !important;
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 0 28px !important;
}
[data-testid="column"]:first-child {
    flex: 0 0 55% !important;
    max-width: 55% !important;
    padding: 0 16px 0 0 !important;
    display: flex !important;
    align-items: flex-start !important;
}
[data-testid="column"]:last-child {
    flex: 0 0 45% !important;
    max-width: 45% !important;
    padding: 0 0 0 8px !important;
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    overflow: visible !important;
}
[data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 440px !important;
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
    section.main > div > div > [data-testid="stVerticalBlock"] {
        padding-top: 52px !important;
        padding-bottom: 32px !important;
    }
    section.main > div > div > [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        padding: 0 20px !important;
    }
    [data-testid="column"]:first-child,
    [data-testid="column"]:last-child {
        flex: 1 1 auto !important;
        max-width: 100% !important;
        padding: 0 !important;
    }
    [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
        max-width: 100% !important;
    }
    .mb-feat-grid { grid-template-columns: repeat(2, 1fr) !important; }
}
@media (max-width: 640px) {
    section.main > div > div > [data-testid="stHorizontalBlock"] { padding: 0 16px !important; }
    .mb-feat-grid { grid-template-columns: 1fr !important; }
    .mb-hero { padding: 4px 0 12px 0 !important; }
    .mb-stats-row { flex-direction: column !important; align-items: flex-start !important; gap: 10px !important; }
    .mb-stat { padding-right: 0 !important; margin-right: 0 !important; border-right: none !important; }
    .mb-glass-inner { padding: 22px 20px 20px 20px !important; }
    .mb-page-foot { flex-direction: column !important; text-align: center !important; }
}
@media (max-height: 860px) {
    .mb-stats-row { display: none !important; }
    .mb-hero-sub { margin-bottom: 14px !important; font-size: 12px !important; line-height: 1.55 !important; }
    .mb-feat-grid { margin-bottom: 12px !important; }
    .mb-hero-title { margin-bottom: 12px !important; font-size: clamp(26px, 3vw, 36px) !important; }
    .mb-glass-inner { padding: 24px 24px 20px 24px !important; }
}
""")
+ """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp:has(.mb-auth-page) {
    font-family: "Inter", system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #fafafa;
}

.mb-auth-page {
    position: absolute;
    width: 0;
    height: 0;
    overflow: hidden;
    pointer-events: none;
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
    opacity: 0.42;
    mix-blend-mode: luminosity;
    mask-image: linear-gradient(to top, black 0%, transparent 72%);
    -webkit-mask-image: linear-gradient(to top, black 0%, transparent 72%);
}
.mb-auth-aurora {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 55% 35% at 72% 8%, rgba(168, 85, 247, 0.28), transparent 60%),
        radial-gradient(ellipse 45% 30% at 15% 12%, rgba(91, 140, 255, 0.18), transparent 55%);
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

/* ── Top bar — fixed, kein Layout-Platz ── */
.mb-topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 52px;
    padding: 0 28px;
    box-sizing: border-box;
    border-bottom: 1px solid var(--mb-line);
    background: rgba(5, 8, 22, 0.88);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
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
.mb-topbar-claim { display: none !important; }
.mb-topbar-live { display: none !important; }
.mb-logo-mark {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(135deg, #A855F7 0%, #7B61FF 50%, #5B8CFF 100%);
    box-shadow: var(--mb-glow), inset 0 1px 0 rgba(255,255,255,0.2);
}
.mb-topbar-name {
    font-size: 15px;
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
    padding: 4px 0 8px 0;
    max-width: 100%;
    width: 100%;
}
.mb-hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    margin-bottom: 14px;
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
    font-size: clamp(28px, 3.2vw, 42px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.08;
    margin: 0 0 12px 0;
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
    font-size: 13px;
    line-height: 1.6;
    color: #94a3b8 !important;
    margin: 0 0 18px 0;
    max-width: 520px;
}

/* Feature cards — 4 col glass row */
.mb-feat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    margin-bottom: 16px;
}
.mb-feat-card {
    padding: 12px 10px;
    border-radius: 14px;
    background: rgba(10, 16, 36, 0.52);
    border: 1px solid var(--mb-line);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
}
.mb-feat-card:hover {
    border-color: rgba(123, 97, 255, 0.32);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(123, 97, 255, 0.14), inset 0 1px 0 rgba(255,255,255,0.06);
}
.mb-feat-icon {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
    background: linear-gradient(135deg, rgba(168,85,247,0.3), rgba(91,140,255,0.18));
    border: 1px solid rgba(123, 97, 255, 0.22);
}
.mb-feat-icon svg {
    width: 14px;
    height: 14px;
    stroke: #c4b5fd;
    fill: none;
    stroke-width: 1.75;
    stroke-linecap: round;
    stroke-linejoin: round;
}
.mb-feat-title {
    display: block;
    font-size: 11px;
    font-weight: 700;
    color: #fafafa !important;
    margin-bottom: 3px;
    letter-spacing: -0.01em;
    line-height: 1.3;
}
.mb-feat-desc {
    font-size: 9px;
    color: #64748b !important;
    line-height: 1.4;
}

/* Stats row */
.mb-stats-row {
    display: flex;
    align-items: center;
    gap: 0;
    flex-wrap: nowrap;
    padding-top: 4px;
}
.mb-stat {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-right: 16px;
    margin-right: 16px;
    border-right: 1px solid var(--mb-line);
}
.mb-stat:last-child {
    padding-right: 0;
    margin-right: 0;
    border-right: none;
}
.mb-stat-icon {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(123, 97, 255, 0.1);
    border: 1px solid rgba(123, 97, 255, 0.18);
    flex-shrink: 0;
}
.mb-stat-icon svg {
    width: 14px;
    height: 14px;
    stroke: #a78bfa;
    fill: none;
    stroke-width: 1.75;
    stroke-linecap: round;
    stroke-linejoin: round;
}
.mb-stat-val {
    display: block;
    font-size: 14px;
    font-weight: 700;
    color: #fafafa !important;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.mb-stat-label {
    display: block;
    font-size: 10px;
    color: #64748b !important;
    line-height: 1.3;
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
    width: 75%;
    height: 64px;
    background: radial-gradient(ellipse, rgba(168, 85, 247, 0.55), rgba(123, 97, 255, 0.2) 45%, transparent 72%);
    filter: blur(32px);
    z-index: -1;
    pointer-events: none;
}
.mb-glass-card {
    border-radius: var(--mb-radius);
    padding: 1px;
    background: linear-gradient(165deg, rgba(168,85,247,0.55) 0%, rgba(91,140,255,0.12) 45%, rgba(123,97,255,0.35) 100%);
    box-shadow: var(--mb-glow), 0 40px 100px rgba(0, 0, 0, 0.6);
    overflow: visible;
}
.mb-glass-inner {
    position: relative;
    border-radius: calc(var(--mb-radius) - 1px);
    padding: 26px 28px 22px 28px;
    background: rgba(8, 12, 28, 0.58);
    backdrop-filter: blur(32px) saturate(1.5);
    -webkit-backdrop-filter: blur(32px) saturate(1.5);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}
.mb-glass-inner::before {
    content: "";
    position: absolute;
    top: 0;
    left: 8%;
    right: 8%;
    height: 3px;
    border-radius: 0 0 6px 6px;
    background: linear-gradient(90deg, transparent, #A855F7 20%, #5B8CFF 80%, transparent);
    box-shadow: 0 0 32px rgba(168, 85, 247, 0.85);
}
.mb-panel-logo {
    width: 40px;
    height: 40px;
    margin: 0 auto 12px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, #A855F7, #7B61FF, #5B8CFF);
    box-shadow: var(--mb-glow);
    font-size: 17px;
    font-weight: 800;
    color: #fff !important;
}
.mb-panel-title {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fafafa !important;
    margin: 0 0 4px 0;
    text-align: center;
}
.mb-panel-sub {
    font-size: 13px;
    color: #64748b !important;
    margin: 0 0 18px 0;
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
    min-height: 44px;
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
    margin: 14px 0 14px 0;
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

/* Panel switch row */
.mb-panel-switch-note {
    display: block;
    margin: 0;
    padding-top: 8px;
    font-size: 14px;
    color: #64748b !important;
    text-align: right;
}

/* Page footer */
.mb-page-foot {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 90;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 28px;
    font-size: 11px;
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
{g} [data-testid="stNumberInput"] {{ margin-bottom: 10px !important; }}
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
    background: rgba(5, 8, 22, 0.88) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.35) !important;
}}
{g} [data-testid="stForm"] [data-testid="stTextInput"]:first-of-type div[data-baseweb="input"] {{
    background: rgba(5, 8, 22, 0.88) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2364748b' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E") no-repeat 14px center / 16px 16px !important;
}}
{g} [data-testid="stForm"] [data-testid="stTextInput"]:nth-of-type(2) div[data-baseweb="input"] {{
    background: rgba(5, 8, 22, 0.88) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2364748b' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E") no-repeat 14px center / 16px 16px !important;
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
    padding-left: 42px !important;
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
{g} form .stFormSubmitButton button {{
    width: 100% !important;
    min-height: 46px !important;
    margin-top: 2px !important;
    border-radius: 12px !important;
    border: none !important;
    background: linear-gradient(90deg, #A855F7 0%, #7B61FF 40%, #5B8CFF 100%) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: -0.01em !important;
    font-family: inherit !important;
    box-shadow: 0 0 40px rgba(123, 97, 255, 0.35), inset 0 1px 0 rgba(255,255,255,0.18) !important;
    transition: box-shadow 0.2s, transform 0.15s, filter 0.2s !important;
}}
{g} form .stFormSubmitButton button:hover {{
    box-shadow: 0 0 52px rgba(123, 97, 255, 0.48), inset 0 1px 0 rgba(255,255,255,0.22) !important;
    transform: translateY(-1px) !important;
    filter: brightness(1.05) !important;
}}
{g} form .stFormSubmitButton button p {{ color: #fff !important; font-weight: 700 !important; }}

/* Mode switch link button */
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) {{
    align-items: center !important;
    margin-top: 20px !important;
    gap: 4px !important;
}}
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) [data-testid="column"]:first-child {{
    flex: 1 !important; max-width: none !important; padding: 0 !important;
}}
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) [data-testid="column"]:last-child {{
    flex: 0 0 auto !important; max-width: none !important; padding: 0 !important;
}}
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton {{
    display: flex !important;
    justify-content: flex-start !important;
    margin: 0 !important;
    width: 100% !important;
}}
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button {{
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
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button:hover {{
    color: #A855F7 !important;
    background: transparent !important;
    box-shadow: none !important;
    transform: none !important;
}}
{g} [data-testid="column"]:last-child [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button p {{
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


# Inline SVG icons — premium, no emoji
_SVG_REELS = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<rect x="2" y="4" width="20" height="16" rx="2"/>'
    '<path d="M10 9l6 3-6 3V9z"/>'
    '</svg>'
)
_SVG_BALL = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/>'
    '<path d="M12 3c2 2.5 2 6.5 0 9M12 3c-2 2.5-2 6.5 0 9M3 12h18"/>'
    '</svg>'
)
_SVG_ROCKET = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>'
    '<path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>'
    '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>'
    '</svg>'
)
_SVG_TEAM = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
    '<circle cx="9" cy="7" r="4"/>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>'
    '</svg>'
)
_SVG_USER = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
    '<circle cx="12" cy="7" r="4"/>'
    '</svg>'
)
_SVG_PLAY = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<polygon points="5 3 19 12 5 21 5 3"/>'
    '</svg>'
)
_SVG_BUILD = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<rect x="4" y="2" width="16" height="20" rx="2"/>'
    '<path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>'
    '</svg>'
)


def _feat_card(icon: str, title: str, desc: str) -> str:
    return (
        f'<div class="mb-feat-card">'
        f'<div class="mb-feat-icon">{icon}</div>'
        f'<span class="mb-feat-title">{html.escape(title)}</span>'
        f'<span class="mb-feat-desc">{desc}</span>'
        f'</div>'
    )


def _stat_item(icon: str, val: str, label: str) -> str:
    return (
        f'<div class="mb-stat">'
        f'<div class="mb-stat-icon">{icon}</div>'
        f'<div><span class="mb-stat-val">{html.escape(val)}</span>'
        f'<span class="mb-stat-label">{label}</span></div>'
        f'</div>'
    )


def page_open_html(mode_class: str = "") -> str:
    name = html.escape(APP_NAME)
    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    extra = html.escape(mode_class)
    return (
        f'<div class="mb-auth-page {extra}"></div>'
        f'<div class="mb-auth-bg" aria-hidden="true"></div>'
        f'<div class="mb-auth-aurora" aria-hidden="true"></div>'
        f'<div class="mb-auth-stars" aria-hidden="true"></div>'
        f'<header class="mb-topbar">'
        f'<div class="mb-topbar-brand">{_logo_mark(initial)}'
        f'<span class="mb-topbar-name">{name}</span></div>'
        f'<div class="mb-topbar-actions">'
        f'<span class="mb-topbar-lang">🌐 DE</span>'
        f'</div></header>'
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
        'MaByte ist dein All-in-One System für AI-gestützte Content Creation, '
        'Football Intelligence und Automatisierung. Für Creator, Teams und '
        'Unternehmen, die skalieren wollen.'
        '</p>'
        '<div class="mb-feat-grid">'
        + _feat_card(_SVG_REELS, "AI Reels Studio", "Shorts &amp; Video mit KI-Power")
        + _feat_card(_SVG_BALL, "Football Intelligence", "Analyse, Insights &amp; Predictions")
        + _feat_card(_SVG_ROCKET, "Auto Publishing", "Multi-Plattform in einem Flow")
        + _feat_card(_SVG_TEAM, "Team Workspaces", "Collaboration für Agenturen")
        + '</div>'
        '<div class="mb-stats-row">'
        + _stat_item(_SVG_USER, "10K+", "Aktive Creator")
        + _stat_item(_SVG_PLAY, "1M+", "Videos erstellt")
        + _stat_item(_SVG_BUILD, "500+", "Teams &amp; Unternehmen")
        + '</div>'
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
        '<p class="mb-panel-sub">Melde dich an, um fortzufahren.</p>'
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
    )


def auth_styles_bundle() -> str:
    return GATE_CSS + widget_css()
