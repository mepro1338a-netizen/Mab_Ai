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
    max-width: 460px !important;
}

.mb-access-wrap [data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;
    max-width: 460px !important;
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
    gap: 5px !important;
    background: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 6px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) inset !important;
}

.mb-mode-switch .stButton > button,
.mb-mode-switch .stButton > button[kind="tertiary"] {
    min-height: 44px !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    background: transparent !important;
    color: #52525b !important;
}

.mb-mode-switch .stButton > button p {
    color: inherit !important;
    font-weight: 600 !important;
}

.mb-mode-login .stButton:first-of-type > button,
.mb-mode-register .stButton:last-of-type > button {
    background: linear-gradient(135deg, #a855f7, #7c3aed) !important;
    color: #fff !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5), 0 0 0 1px rgba(255,255,255,0.1) inset !important;
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
    .mb-auth-lead, .mb-auth-features, .mb-auth-quote, .mb-showcase, .mb-auth-metrics {
        margin-left: auto; margin-right: auto;
    }
    .mb-auth-features { grid-template-columns: 1fr !important; }
    .mb-showcase { height: 160px; }
}
""")
    + """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* —— Atmosphere —— */
.mb-auth-page {
    position: relative;
    width: 100%;
    font-family: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    -webkit-font-smoothing: antialiased;
}

.mb-auth-aurora {
    position: fixed;
    inset: -20% -10%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 42% 38% at 15% 12%, rgba(124, 58, 237, 0.35), transparent 55%),
        radial-gradient(ellipse 35% 30% at 78% 22%, rgba(59, 130, 246, 0.18), transparent 50%),
        radial-gradient(ellipse 50% 40% at 50% 100%, rgba(109, 40, 217, 0.15), transparent 55%);
    animation: mb-aurora-shift 14s ease-in-out infinite alternate;
}

@keyframes mb-aurora-shift {
    0% { transform: translate(0, 0) scale(1); opacity: 0.85; }
    100% { transform: translate(2%, -1.5%) scale(1.03); opacity: 1; }
}

.mb-auth-page::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: linear-gradient(180deg, #050506 0%, #09090b 35%, #0a0a0f 70%, #050506 100%);
}

.mb-auth-page::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.4;
    background-image:
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(ellipse 80% 70% at 40% 30%, black 15%, transparent 70%);
}

/* —— Header —— */
.mb-auth-header {
    position: relative;
    z-index: 2;
    margin: 0 -32px 36px -32px;
    padding: 0 32px;
    border-bottom: 1px solid rgba(167, 139, 250, 0.15);
    background: linear-gradient(180deg, rgba(12, 12, 16, 0.92), rgba(9, 9, 11, 0.75));
    backdrop-filter: blur(20px) saturate(1.4);
    -webkit-backdrop-filter: blur(20px) saturate(1.4);
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.06) inset, 0 12px 40px rgba(0, 0, 0, 0.35);
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
    width: 44px;
    height: 44px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
    color: #fff !important;
    background: linear-gradient(145deg, #e9d5ff, #a855f7 30%, #7c3aed 60%, #5b21b6);
    box-shadow:
        0 0 0 1px rgba(255,255,255,0.15) inset,
        0 8px 28px rgba(124, 58, 237, 0.55),
        0 0 40px rgba(124, 58, 237, 0.25);
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
    font-weight: 700;
    color: #fafafa !important;
    padding: 9px 18px;
    border-radius: 11px;
    background: linear-gradient(135deg, #a855f7, #7c3aed 50%, #6d28d9);
    box-shadow: 0 6px 24px rgba(124, 58, 237, 0.5), 0 0 0 1px rgba(255,255,255,0.12) inset;
    border: 1px solid rgba(255, 255, 255, 0.12);
    letter-spacing: -0.02em;
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
    font-size: clamp(38px, 4.5vw, 56px);
    font-weight: 800;
    letter-spacing: -0.045em;
    line-height: 1.04;
    margin: 0 0 20px 0;
    color: #fafafa !important;
    text-shadow: 0 2px 40px rgba(124, 58, 237, 0.25);
}

.mb-auth-headline .mb-auth-gradient {
    display: block;
    margin-top: 6px;
    background: linear-gradient(100deg, #ffffff 0%, #f0abfc 25%, #c084fc 50%, #8b5cf6 75%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 28px rgba(167, 139, 250, 0.35));
}

.mb-auth-lead {
    font-size: 17px;
    line-height: 1.7;
    color: #d4d4d8 !important;
    margin: 0 0 28px 0;
    max-width: 560px;
}

.mb-auth-lead strong {
    color: #ffffff !important;
    font-weight: 600;
}

/* Showcase — product aura */
.mb-showcase {
    position: relative;
    margin: 0 0 28px 0;
    max-width: 560px;
    height: 200px;
}

.mb-showcase-glow {
    position: absolute;
    inset: 10% 5%;
    background: radial-gradient(ellipse at center, rgba(124, 58, 237, 0.35), transparent 65%);
    filter: blur(24px);
    animation: mb-glow-pulse 5s ease-in-out infinite;
}

@keyframes mb-glow-pulse {
    0%, 100% { opacity: 0.6; transform: scale(0.98); }
    50% { opacity: 1; transform: scale(1.02); }
}

.mb-showcase-window {
    position: relative;
    height: 100%;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: linear-gradient(165deg, rgba(24, 24, 30, 0.95), rgba(9, 9, 12, 0.9));
    box-shadow:
        0 0 0 1px rgba(124, 58, 237, 0.2) inset,
        0 24px 60px rgba(0, 0, 0, 0.55),
        0 0 80px rgba(124, 58, 237, 0.12);
    overflow: hidden;
    backdrop-filter: blur(12px);
}

.mb-showcase-bar {
    display: flex;
    gap: 6px;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(0, 0, 0, 0.25);
}

.mb-showcase-bar span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #3f3f46;
}
.mb-showcase-bar span:first-child { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.4); }
.mb-showcase-bar span:nth-child(2) { background: #eab308; }
.mb-showcase-bar span:nth-child(3) { background: #22c55e; }

.mb-showcase-body {
    padding: 20px 22px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.mb-showcase-line {
    height: 10px;
    border-radius: 6px;
    background: linear-gradient(90deg, rgba(124,58,237,0.5), rgba(63,63,70,0.4));
}
.mb-showcase-line.w80 { width: 80%; }
.mb-showcase-line.w55 { width: 55%; }
.mb-showcase-line.w40 { width: 40%; opacity: 0.6; }

.mb-showcase-chip {
    align-self: flex-start;
    margin-top: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #e9d5ff !important;
    background: linear-gradient(135deg, rgba(124,58,237,0.35), rgba(59,130,246,0.2));
    border: 1px solid rgba(167, 139, 250, 0.4);
    box-shadow: 0 0 24px rgba(124, 58, 237, 0.25);
}

.mb-auth-features {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 24px;
    max-width: 560px;
}

.mb-feat-card {
    position: relative;
    padding: 20px 18px;
    border-radius: 18px;
    text-align: left;
    background: linear-gradient(160deg, rgba(30, 27, 45, 0.9), rgba(12, 12, 16, 0.95));
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
    overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s, box-shadow 0.25s;
}

.mb-feat-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.5), transparent);
}

.mb-feat-card:hover {
    transform: translateY(-3px);
    border-color: rgba(167, 139, 250, 0.35);
    box-shadow: 0 16px 48px rgba(124, 58, 237, 0.2);
}

.mb-feat-card--prime {
    border-color: rgba(124, 58, 237, 0.35);
    background: linear-gradient(160deg, rgba(46, 16, 101, 0.5), rgba(12, 12, 18, 0.95));
}

.mb-feat-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-bottom: 14px;
    background: rgba(124, 58, 237, 0.2);
    border: 1px solid rgba(167, 139, 250, 0.3);
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.2);
}

.mb-feat-title {
    display: block;
    font-size: 15px;
    font-weight: 700;
    color: #fafafa !important;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}

.mb-feat-desc {
    font-size: 12px;
    line-height: 1.5;
    color: #a1a1aa !important;
}

.mb-auth-metrics {
    display: flex;
    gap: 20px;
    margin-bottom: 24px;
    max-width: 560px;
    padding: 16px 20px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(8px);
}

.mb-auth-metrics > div {
    flex: 1;
    text-align: center;
}

.mb-auth-metrics strong {
    display: block;
    font-size: 22px;
    font-weight: 800;
    color: #fafafa !important;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #fff, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.mb-auth-metrics span {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #71717a !important;
}

.mb-auth-quote {
    position: relative;
    padding: 22px 24px 22px 28px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.12), rgba(15, 15, 20, 0.85));
    border: 1px solid rgba(167, 139, 250, 0.25);
    max-width: 560px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3), 0 0 40px rgba(124, 58, 237, 0.08);
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
.mb-access-wrap {
    position: relative;
}

.mb-access-wrap::before {
    content: "";
    position: absolute;
    inset: -20px -10px -10px -10px;
    background: radial-gradient(ellipse at 50% 30%, rgba(124, 58, 237, 0.35), transparent 60%);
    filter: blur(32px);
    z-index: 0;
    pointer-events: none;
    animation: mb-glow-pulse 6s ease-in-out infinite;
}

.mb-access-card {
    position: relative;
    z-index: 1;
    border-radius: 26px;
    padding: 1px;
    background: linear-gradient(
        145deg,
        rgba(196, 181, 253, 0.7),
        rgba(124, 58, 237, 0.4) 35%,
        rgba(59, 130, 246, 0.25) 65%,
        rgba(63, 63, 70, 0.5)
    );
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.08) inset,
        0 40px 100px rgba(0, 0, 0, 0.6),
        0 0 120px rgba(124, 58, 237, 0.2);
}

.mb-access-card-inner {
    border-radius: 25px;
    padding: 32px 30px 28px 30px;
    background: linear-gradient(180deg, rgba(16, 16, 22, 0.97), rgba(8, 8, 10, 0.98));
    backdrop-filter: blur(32px) saturate(1.3);
    -webkit-backdrop-filter: blur(32px) saturate(1.3);
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.06) inset;
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
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin: 0 0 8px 0;
    line-height: 1.1;
}

.mb-panel-head p {
    color: #a1a1aa !important;
    font-size: 14px;
    margin: 0;
    line-height: 1.55;
}

.mb-field-label {
    display: block;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #a1a1aa !important;
    margin: 0 0 8px 4px;
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
    min-height: 52px;
    padding: 0 20px;
    margin-bottom: 14px;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 700;
    text-decoration: none !important;
    color: #fafafa !important;
    background: linear-gradient(180deg, rgba(39, 39, 42, 0.9), rgba(24, 24, 27, 0.95)) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 1px 0 rgba(255,255,255,0.06) inset;
    transition: all 0.2s ease;
}

.mb-login-google:hover {
    background: linear-gradient(180deg, rgba(124, 58, 237, 0.2), rgba(24, 24, 27, 0.95)) !important;
    border-color: rgba(196, 181, 253, 0.5) !important;
    box-shadow: 0 0 40px rgba(124, 58, 237, 0.25), 0 8px 24px rgba(0, 0, 0, 0.35);
    transform: translateY(-1px);
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
    background: rgba(0, 0, 0, 0.55) !important;
    background-color: rgba(0, 0, 0, 0.55) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 16px !important;
    min-height: 52px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) inset !important;
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
    min-height: 54px !important;
    margin-top: 10px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 25%, #7c3aed 60%, #6d28d9 100%) !important;
    color: #fff !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    letter-spacing: -0.02em !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
    box-shadow:
        0 12px 40px rgba(124, 58, 237, 0.55),
        0 0 0 1px rgba(255,255,255,0.1) inset,
        0 0 60px rgba(124, 58, 237, 0.25) !important;
    transition: transform 0.15s ease, box-shadow 0.2s ease !important;
}}

{g} form button:hover {{
    transform: translateY(-1px) !important;
    box-shadow:
        0 16px 48px rgba(124, 58, 237, 0.65),
        0 0 80px rgba(124, 58, 237, 0.3) !important;
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
<div class="mb-auth-aurora" aria-hidden="true"></div>
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
        Die Infrastruktur der nächsten Creator-Generation
    </div>
    <h1 class="mb-auth-headline">
        {name} ist der Grund
        <span class="mb-auth-gradient">für deine neue Zukunft.</span>
    </h1>
    <p class="mb-auth-lead">
        Nicht noch ein Tool — sondern das <strong>Betriebssystem</strong>, auf dem die nächste
        Welle von Creatorn gebaut wird. Video, KI, Bild und Code in einer Engine.
    </p>
    <div class="mb-showcase" aria-hidden="true">
        <div class="mb-showcase-glow"></div>
        <div class="mb-showcase-window">
            <div class="mb-showcase-bar"><span></span><span></span><span></span></div>
            <div class="mb-showcase-body">
                <div class="mb-showcase-line w80"></div>
                <div class="mb-showcase-line w55"></div>
                <div class="mb-showcase-line w40"></div>
                <span class="mb-showcase-chip">KI · Video · Publish · Live</span>
            </div>
        </div>
    </div>
    <div class="mb-auth-features">
        <article class="mb-feat-card mb-feat-card--prime">
            <div class="mb-feat-icon" aria-hidden="true">◆</div>
            <span class="mb-feat-title">All-in-One Engine</span>
            <span class="mb-feat-desc">Eine Plattform statt zehn Abos — alles verbunden.</span>
        </article>
        <article class="mb-feat-card">
            <div class="mb-feat-icon" aria-hidden="true">▶</div>
            <span class="mb-feat-title">Produktions-Flow</span>
            <span class="mb-feat-desc">Von der Idee bis zum Post ohne Kontextwechsel.</span>
        </article>
        <article class="mb-feat-card">
            <div class="mb-feat-icon" aria-hidden="true">✦</div>
            <span class="mb-feat-title">KI-Native</span>
            <span class="mb-feat-desc">Chat, Bild, Musik und Code — integriert, nicht angeflanscht.</span>
        </article>
        <article class="mb-feat-card">
            <div class="mb-feat-icon" aria-hidden="true">◎</div>
            <span class="mb-feat-title">Fair &amp; Skalierbar</span>
            <span class="mb-feat-desc">Professionell für Teams, fair für Einzel-Creator.</span>
        </article>
    </div>
    <div class="mb-auth-metrics">
        <div><strong>1</strong><span>Workspace</span></div>
        <div><strong>∞</strong><span>Produktion</span></div>
        <div><strong>24/7</strong><span>Bereit</span></div>
    </div>
    <blockquote class="mb-auth-quote">
        <p>Die Zukunft gehört denen, die produzieren — nicht denen, die tabben.</p>
        <cite>— {name} Manifest</cite>
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
