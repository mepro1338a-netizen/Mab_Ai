"""MaByte Enterprise Login — Linear / Stripe grade B2B gateway."""
from __future__ import annotations

import html

from config import APP_NAME

_G = ".stApp"


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
    --mb-radius: 20px;
}
html { color-scheme: dark !important; }
.stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
    --primary-color: #7B61FF !important;
    --background-color: #050816 !important;
    --text-color: #fafafa !important;
}
.stApp,
.stApp [data-testid="stAppViewContainer"],
.stApp [data-testid="stAppViewContainer"] > section,
.stApp [data-testid="stMainBlockContainer"],
.stApp [data-testid="stAppViewBlockContainer"] {
    background: var(--mb-bg) !important;
    color: #fafafa !important;
}
.stApp #MainMenu,
.stApp footer,
.stApp [data-testid="stToolbar"],
.stApp [data-testid="stDecoration"],
.stApp [data-testid="stSidebar"],
.stApp [data-testid="stStatusWidget"],
.stApp [data-testid="stDeployButton"],
.stApp [data-testid="stElementToolbar"],
.stApp [data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}
.stApp [data-testid="stAppViewContainer"],
.stApp [data-testid="stAppViewContainer"] > section,
.stApp [data-testid="stMainBlockContainer"],
.stApp [data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
}
"""
+ """
.stApp [data-testid="stMain"] .block-container,
.stApp [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    padding: 0 !important;
}
.stApp [data-testid="stMain"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
.stApp [data-testid="stMarkdownContainer"]:has(.mb-topbar),
.stApp [data-testid="stMarkdownContainer"]:has(.mb-page-foot) {
    margin: 0 !important;
    padding: 0 !important;
}

/* Auth split layout — Streamlit 1.50: hero + panel are direct stColumn children */
.stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) 520px !important;
    gap: 72px !important;
    align-items: center !important;
    min-height: calc(100vh - 80px) !important;
    max-width: 1440px !important;
    margin: 0 auto !important;
    padding: 80px 72px !important;
    box-sizing: border-box !important;
}
.stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:first-child {
    flex: unset !important;
    max-width: none !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
}
.stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:last-child {
    flex: unset !important;
    max-width: 520px !important;
    width: 100% !important;
    min-width: 0 !important;
    padding: 0 !important;
    justify-self: end !important;
    align-self: center !important;
}

/* Login card — only the Streamlit block that directly wraps the marker */
.stApp .login-card,
.stApp [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .login-card-root),
.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .login-card-root) {
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 520px !important;
    margin: 0 auto !important;
    padding: 48px !important;
    border-radius: 28px !important;
    background: rgba(8, 12, 30, 0.86) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    box-shadow: 0 0 80px rgba(123, 97, 255, 0.28) !important;
    gap: 0 !important;
}
.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .login-card-root) > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.stApp [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .login-card-root) > [data-testid="stElementContainer"],
.stApp [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .login-card-root) > [data-testid="stMarkdownContainer"],
.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .login-card-root) [data-testid="stElementContainer"],
.stApp [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .login-card-root) [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
}

@media (max-width: 1100px) {
    .stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
        grid-template-columns: 1fr !important;
        gap: 40px !important;
        padding: 48px 32px !important;
        min-height: auto !important;
    }
    .stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) > [data-testid="stColumn"]:last-child {
        max-width: 520px !important;
        justify-self: center !important;
    }
    .stApp .mb-feat-grid { grid-template-columns: repeat(2, 1fr) !important; }
}
@media (max-width: 640px) {
    .stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
        padding: 32px 16px !important;
        gap: 32px !important;
    }
    .stApp .login-card,
    .stApp [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .login-card-root),
    .stApp [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .login-card-root) {
        padding: 32px 24px !important;
    }
    .stApp .mb-feat-grid { grid-template-columns: 1fr !important; }
    .stApp .mb-hero { padding: 4px 0 12px 0 !important; }
    .stApp .mb-stats-row { flex-direction: column !important; align-items: flex-start !important; gap: 10px !important; }
    .stApp .mb-stat { padding-right: 0 !important; margin-right: 0 !important; border-right: none !important; }
    .stApp .mb-page-foot { flex-direction: column !important; text-align: center !important; }
}
@media (max-height: 860px) {
    .stApp .mb-stats-row { display: none !important; }
    .stApp .mb-hero-sub { margin-bottom: 14px !important; font-size: 12px !important; line-height: 1.55 !important; }
    .stApp .mb-feat-grid { margin-bottom: 12px !important; }
    .stApp .mb-hero-title { margin-bottom: 12px !important; font-size: clamp(26px, 3vw, 36px) !important; }
    .stApp [data-testid="stHorizontalBlock"]:has(.auth-grid-marker) {
        padding-top: 48px !important;
        padding-bottom: 48px !important;
    }
}
"""
+ """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp {
    font-family: "Inter", system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #fafafa;
}

.mb-auth-page {
    display: none !important;
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

/* ── Top bar — normal document flow ── */
.mb-topbar {
    position: relative;
    z-index: 10;
    width: 100%;
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
    font-size: clamp(24px, 2.5vw, 32px);
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.12;
    margin: 0 0 10px 0;
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
    line-height: 1.55;
    color: #94a3b8 !important;
    margin: 0 0 14px 0;
    max-width: 480px;
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

/* ── Login card header (inside Streamlit column card) ── */
.mb-login-head {
    margin: 0 0 4px 0;
}
.mb-panel-logo {
    width: 40px;
    height: 40px;
    margin: 0 auto 14px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, #A855F7, #7B61FF, #5B8CFF);
    box-shadow: 0 0 24px rgba(123, 97, 255, 0.35);
    font-size: 15px;
    font-weight: 800;
    color: #fff !important;
}
.mb-panel-title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fafafa !important;
    margin: 0 0 3px 0;
    text-align: center;
}
.mb-panel-sub {
    font-size: 13px;
    color: #64748b !important;
    margin: 0 0 20px 0;
    line-height: 1.45;
    text-align: center;
}

/* Google + divider — inside card, above form */
.mb-oauth-zone {
    margin: 0 0 0 0;
    padding: 0;
}
.mb-oauth-label { display: none !important; }
.mb-login-google {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    min-height: 40px;
    padding: 0 14px;
    margin-bottom: 0;
    border-radius: 10px;
    font-size: 13px;
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
    gap: 10px;
    margin: 16px 0;
    font-size: 10px;
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
    card = f'{g} [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .login-card-root)'
    card_wrap = (
        f'{g} [data-testid="stVerticalBlockBorderWrapper"]:has('
        f'> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .login-card-root)'
    )
    return f"""
{card} [data-testid="stForm"],
{card_wrap} [data-testid="stForm"] {{
    border: none !important; padding: 0 !important; background: transparent !important;
}}
{card} [data-testid="stTextInput"] [data-testid="stWidgetLabel"],
{card} [data-testid="stNumberInput"] [data-testid="stWidgetLabel"],
{card_wrap} [data-testid="stTextInput"] [data-testid="stWidgetLabel"],
{card_wrap} [data-testid="stNumberInput"] [data-testid="stWidgetLabel"],
{card} label[data-testid="stWidgetLabel"]:has(+ div [data-baseweb="input"]) {{ display: none !important; }}
{card} [data-testid="stTextInput"],
{card} [data-testid="stNumberInput"],
{card_wrap} [data-testid="stTextInput"],
{card_wrap} [data-testid="stNumberInput"] {{ margin-bottom: 12px !important; }}
{card} > [data-testid="stElementContainer"],
{card} > [data-testid="stMarkdownContainer"],
{card_wrap} > [data-testid="stElementContainer"],
{card_wrap} > [data-testid="stMarkdownContainer"] {{
    margin-bottom: 0 !important;
}}
{card} [data-testid="stTextInput"] > div,
{card} [data-testid="stTextInput"] > div > div,
{card} [data-testid="stTextInput"] fieldset,
{card} [data-testid="stNumberInput"] > div,
{card} [data-testid="stNumberInput"] > div > div,
{card_wrap} [data-testid="stTextInput"] > div,
{card_wrap} [data-testid="stTextInput"] > div > div,
{card_wrap} [data-testid="stNumberInput"] > div,
{card_wrap} [data-testid="stNumberInput"] > div > div {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}}
{card} div[data-baseweb="input"],
{card} [data-testid="stTextInput"] div[data-baseweb="input"],
{card} [data-testid="stNumberInput"] div[data-baseweb="input"],
{card_wrap} div[data-baseweb="input"],
{card_wrap} [data-testid="stTextInput"] div[data-baseweb="input"],
{card_wrap} [data-testid="stNumberInput"] div[data-baseweb="input"] {{
    background: rgba(5, 8, 22, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3) !important;
}}
{card} [data-testid="stForm"] [data-testid="stTextInput"]:first-of-type div[data-baseweb="input"],
{card_wrap} [data-testid="stForm"] [data-testid="stTextInput"]:first-of-type div[data-baseweb="input"] {{
    background: rgba(5, 8, 22, 0.85) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2364748b' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E") no-repeat 14px center / 16px 16px !important;
}}
{card} [data-testid="stForm"] [data-testid="stTextInput"]:nth-of-type(2) div[data-baseweb="input"],
{card_wrap} [data-testid="stForm"] [data-testid="stTextInput"]:nth-of-type(2) div[data-baseweb="input"] {{
    background: rgba(5, 8, 22, 0.85) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2364748b' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E") no-repeat 14px center / 16px 16px !important;
}}
{card} div[data-baseweb="input"]:focus-within,
{card_wrap} div[data-baseweb="input"]:focus-within {{
    border-color: rgba(123, 97, 255, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(123, 97, 255, 0.15), 0 0 24px rgba(123, 97, 255, 0.12) !important;
}}
{card} [data-testid="stTextInput"] input,
{card} [data-testid="stNumberInput"] input,
{card_wrap} [data-testid="stTextInput"] input,
{card_wrap} [data-testid="stNumberInput"] input {{
    background: rgba(5, 8, 22, 0.85) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    font-size: 13px !important;
    font-family: inherit !important;
    caret-color: #A855F7 !important;
    padding-left: 40px !important;
}}
{card} [data-testid="stTextInput"] input::placeholder,
{card_wrap} [data-testid="stTextInput"] input::placeholder {{ color: #475569 !important; opacity: 1 !important; }}
{card} [data-testid="stTextInput"] input:-webkit-autofill,
{card} [data-testid="stTextInput"] input:-webkit-autofill:focus,
{card_wrap} [data-testid="stTextInput"] input:-webkit-autofill,
{card_wrap} [data-testid="stTextInput"] input:-webkit-autofill:focus {{
    -webkit-box-shadow: 0 0 0 1000px #050816 inset !important;
    -webkit-text-fill-color: #fafafa !important;
}}
{card} [data-testid="stTextInput"] button,
{card_wrap} [data-testid="stTextInput"] button {{ color: #64748b !important; background: transparent !important; }}

/* Remember me checkbox */
{card} [data-testid="stCheckbox"],
{card_wrap} [data-testid="stCheckbox"] {{
    margin: 0 !important;
    padding: 0 !important;
}}
{card} [data-testid="stCheckbox"] label,
{card_wrap} [data-testid="stCheckbox"] label {{
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 13px !important;
    color: #94a3b8 !important;
    cursor: pointer !important;
    background: transparent !important;
    background-color: transparent !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
}}
{card} [data-testid="stCheckbox"] label span,
{card} [data-testid="stCheckbox"] label p,
{card_wrap} [data-testid="stCheckbox"] label span,
{card_wrap} [data-testid="stCheckbox"] label p {{
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
{card} [data-testid="stCheckbox"] [data-baseweb="checkbox"],
{card_wrap} [data-testid="stCheckbox"] [data-baseweb="checkbox"] {{
    background: rgba(5, 8, 22, 0.85) !important;
    border-color: rgba(255,255,255,0.12) !important;
}}
{card} [data-testid="stCheckbox"] [data-baseweb="checkbox"]:hover,
{card_wrap} [data-testid="stCheckbox"] [data-baseweb="checkbox"]:hover {{
    border-color: rgba(123, 97, 255, 0.45) !important;
}}

/* Extras row layout */
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"],
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
    gap: 8px !important;
    margin: 0 0 14px 0 !important;
}}
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child,
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child {{
    flex: 1 !important; max-width: none !important; padding: 0 !important;
    display: flex !important; align-items: center !important;
}}
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child,
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {{
    flex: 0 0 auto !important; max-width: none !important; padding: 0 !important;
    display: flex !important; justify-content: flex-end !important; align-items: center !important;
}}
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child [data-testid="stMarkdownContainer"],
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child [data-testid="stMarkdownContainer"] {{
    width: auto !important;
}}
{g} .mb-forgot-link {{
    white-space: nowrap !important;
    display: inline-block !important;
}}

/* Primary CTA — login / register submit */
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button,
{card} [data-testid="stForm"] .stFormSubmitButton button,
{card} [data-testid="stForm"] div.stButton > button,
{card_wrap} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button,
{card_wrap} [data-testid="stForm"] .stFormSubmitButton button,
{card_wrap} [data-testid="stForm"] div.stButton > button,
{card} [data-testid="stFormSubmitButton"] button,
{card} .stFormSubmitButton button,
{card_wrap} [data-testid="stFormSubmitButton"] button,
{card_wrap} .stFormSubmitButton button,
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[kind="secondary"],
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[kind="secondaryFormSubmit"],
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[kind="primary"],
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondary"],
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"],
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondaryFormSubmit"],
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"],
{card} [data-testid="stFormSubmitButton"] button[kind="secondaryFormSubmit"],
{card} [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondaryFormSubmit"] {{
    width: 100% !important;
    height: 58px !important;
    min-height: 58px !important;
    margin-top: 0 !important;
    border-radius: 16px !important;
    border: 0 !important;
    background: linear-gradient(135deg, #a855f7, #3b82f6) !important;
    background-color: transparent !important;
    background-image: linear-gradient(135deg, #a855f7, #3b82f6) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    font-family: inherit !important;
    box-shadow: 0 4px 20px rgba(123, 97, 255, 0.35) !important;
}}
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover,
{card} [data-testid="stForm"] .stFormSubmitButton button:hover,
{card} [data-testid="stFormSubmitButton"] button:hover,
{card_wrap} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover,
{card_wrap} [data-testid="stForm"] .stFormSubmitButton button:hover,
{card_wrap} [data-testid="stFormSubmitButton"] button:hover {{
    filter: brightness(1.06) !important;
    box-shadow: 0 6px 28px rgba(123, 97, 255, 0.45) !important;
}}
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button p,
{card} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button span,
{card} [data-testid="stForm"] .stFormSubmitButton button p,
{card} [data-testid="stForm"] .stFormSubmitButton button span,
{card} [data-testid="stFormSubmitButton"] button p,
{card} [data-testid="stFormSubmitButton"] button span,
{card_wrap} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button p,
{card_wrap} [data-testid="stForm"] [data-testid="stFormSubmitButton"] button span {{
    color: white !important;
    font-weight: 700 !important;
}}

/* Mode switch link button */
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note),
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) {{
    align-items: center !important;
    margin-top: 16px !important;
    gap: 4px !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) [data-testid="stColumn"]:first-child,
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) [data-testid="stColumn"]:first-child {{
    flex: 1 !important; max-width: none !important; padding: 0 !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) [data-testid="stColumn"]:last-child,
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) [data-testid="stColumn"]:last-child {{
    flex: 0 0 auto !important; max-width: none !important; padding: 0 !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton,
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton {{
    display: flex !important;
    justify-content: flex-start !important;
    margin: 0 !important;
    width: 100% !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button,
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button {{
    display: inline !important;
    width: auto !important;
    min-height: auto !important;
    height: auto !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    color: #7B61FF !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button:hover,
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button:hover {{
    color: #A855F7 !important;
    background: transparent !important;
    box-shadow: none !important;
}}
{card} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button p,
{card_wrap} [data-testid="stHorizontalBlock"]:has(.mb-panel-switch-note) .stButton > button p {{
    color: #7B61FF !important;
    font-weight: 600 !important;
}}

{g} [data-testid="stAlert"] {{ display: none !important; }}
{card}, {card_wrap} {{ gap: 0 !important; }}

/* Captcha refresh — small icon button */
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button,
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] .stButton > button,
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button,
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] .stButton > button {{
    min-height: 48px !important;
    height: 48px !important;
    width: 100% !important;
    border-radius: 12px !important;
    background: rgba(5, 8, 22, 0.85) !important;
    background-image: none !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}}
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button p,
{card} [data-testid="stForm"] [data-testid="stHorizontalBlock"] .stButton > button p,
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="stFormSubmitButton"] button p,
{card_wrap} [data-testid="stForm"] [data-testid="stHorizontalBlock"] .stButton > button p {{
    color: #94a3b8 !important;
    font-weight: 600 !important;
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


def auth_grid_marker_html() -> str:
    return '<span class="auth-grid-marker" hidden aria-hidden="true"></span>'


def login_card_marker_html() -> str:
    return '<span class="login-card-root" hidden aria-hidden="true"></span>'


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
            '<div class="mb-login-head">'
            f'{_hex_logo(initial)}'
            '<h2 class="mb-panel-title">Workspace anlegen</h2>'
            '<p class="mb-panel-sub">Erstelle dein Konto und starte in Minuten.</p>'
            '</div>'
        )
    return (
        '<div class="mb-login-head">'
        f'{_hex_logo(initial)}'
        '<h2 class="mb-panel-title">Willkommen zurück</h2>'
        '<p class="mb-panel-sub">Melde dich an, um fortzufahren.</p>'
        '</div>'
    )


def panel_close_html() -> str:
    return ""


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
    return (
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');"
        + GATE_CSS.replace(
            "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');",
            "",
            1,
        )
        + widget_css()
    )
