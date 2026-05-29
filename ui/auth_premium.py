"""Premium auth shell — Linear/Vercel-style login for MaByte."""
from __future__ import annotations

import html

from config import APP_NAME, APP_TAGLINE
from ui.b2b_theme import MB_APP_BACKGROUND, MB_THEME_VARS
from ui_core import WORDMARK


AUTH_PREMIUM_CSS = (
    """
/* ── Page shell ───────────────────────────────────────────── */
.mb-auth-page {
    position: relative;
    min-height: calc(100vh - 80px);
}
.mb-auth-page::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 15% 20%, rgba(124, 58, 237, .12), transparent 55%),
        radial-gradient(ellipse 60% 40% at 85% 75%, rgba(99, 102, 241, .08), transparent 50%),
        """
    + MB_APP_BACKGROUND
    + """;
}
.mb-auth-page::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: .35;
    background-image:
        linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
    background-size: 64px 64px;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, #000 20%, transparent 75%);
}
.stApp, [data-testid="stAppViewContainer"] {
    background: #09090b !important;
    background-color: #09090b !important;
}
section.main .block-container,
section.main [data-testid="stVerticalBlock"],
section.main [data-testid="column"],
section.main .element-container {
    visibility: visible !important;
    opacity: 1 !important;
    position: relative;
    z-index: 1;
}

/* ── Brand column ─────────────────────────────────────────── */
.mb-auth-brand {
    padding: 48px 32px 48px 8px;
    max-width: 540px;
}
.mb-auth-brand-inner {
    position: sticky;
    top: 48px;
}
[data-testid="stImage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 0 32px 0 !important;
}
[data-testid="stImage"] img {
    max-width: 168px !important;
    width: 168px !important;
    height: auto !important;
    display: block !important;
    filter: drop-shadow(0 16px 48px rgba(124, 58, 237, .28));
}
.mb-auth-logo-fallback {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #7c3aed, #6366f1);
    color: #fff;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 32px;
    box-shadow: 0 12px 40px rgba(124, 58, 237, .35);
}
.mb-auth-eyebrow {
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin: 0 0 16px 0;
}
.mb-auth-hero-title {
    font-size: clamp(32px, 3.8vw, 46px);
    line-height: 1.08;
    font-weight: 700;
    letter-spacing: -.04em;
    margin: 0 0 12px 0;
    color: #fafafa !important;
}
.mb-auth-hero-tagline {
    font-size: 17px;
    font-weight: 500;
    color: #a1a1aa !important;
    margin: 0 0 20px 0;
    letter-spacing: -.015em;
    line-height: 1.45;
}
.mb-auth-hero-desc {
    color: #71717a !important;
    font-size: 14px;
    line-height: 1.7;
    max-width: 420px;
    margin: 0 0 36px 0;
}
.mb-auth-stats {
    display: flex;
    flex-direction: column;
    gap: 0;
    max-width: 400px;
    border-top: 1px solid rgba(63, 63, 70, .6);
}
.mb-auth-stat {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 18px 0;
    border-bottom: 1px solid rgba(63, 63, 70, .45);
}
.mb-auth-stat-icon {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    background: rgba(39, 39, 42, .9);
    border: 1px solid rgba(63, 63, 70, .8);
}
.mb-auth-stat strong {
    display: block;
    color: #e4e4e7 !important;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 3px;
    letter-spacing: -.01em;
}
.mb-auth-stat span {
    color: #71717a !important;
    font-size: 12px;
    line-height: 1.5;
}

/* ── Auth panel (right) ───────────────────────────────────── */
.mb-auth-panel-shell {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 120px);
    padding: 24px 0;
}
.mb-auth-panel {
    width: 100%;
    max-width: 400px;
    padding: 36px 32px 28px 32px;
    border-radius: 16px;
    background: rgba(24, 24, 27, .72);
    border: 1px solid rgba(63, 63, 70, .65);
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, .04) inset,
        0 24px 80px rgba(0, 0, 0, .55),
        0 4px 24px rgba(0, 0, 0, .25);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
}
.mb-auth-panel-head {
    margin-bottom: 28px;
}
.mb-auth-panel-head h1 {
    color: #fafafa !important;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -.025em;
    margin: 0 0 6px 0;
    line-height: 1.25;
}
.mb-auth-panel-head p {
    color: #71717a !important;
    font-size: 13px;
    margin: 0;
    line-height: 1.5;
}

/* ── Segmented mode toggle ──────────────────────────────────── */
.mb-auth-page .mb-auth-segment [data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    background: rgba(9, 9, 11, .6) !important;
    border: 1px solid rgba(63, 63, 70, .7) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    margin-bottom: 22px !important;
}
.mb-auth-page .mb-auth-segment .stButton > button,
.mb-auth-page .mb-auth-segment button {
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    background-color: transparent !important;
    color: #71717a !important;
    transition: background .15s ease, color .15s ease !important;
}
.mb-auth-page .mb-auth-segment .stButton > button p,
.mb-auth-page .mb-auth-segment button p {
    color: inherit !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.mb-auth-page .mb-auth-segment .stButton > button[kind="primary"],
.mb-auth-page .mb-auth-segment button[data-testid="stBaseButton-primary"] {
    background: #27272a !important;
    background-color: #27272a !important;
    color: #fafafa !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .3) !important;
}
.mb-auth-page .mb-auth-segment .stButton > button[kind="primary"] p,
.mb-auth-page .mb-auth-segment button[data-testid="stBaseButton-primary"] p {
    color: #fafafa !important;
}
.mb-auth-page .mb-auth-segment .stButton > button[kind="tertiary"],
.mb-auth-page .mb-auth-segment button[data-testid="stBaseButton-tertiary"] {
    background: transparent !important;
    color: #71717a !important;
}
.mb-auth-page .mb-auth-segment .stButton > button:hover,
.mb-auth-page .mb-auth-segment button:hover {
    transform: none !important;
    color: #a1a1aa !important;
    background: rgba(39, 39, 42, .5) !important;
}

/* ── Google OAuth ───────────────────────────────────────────── */
.mb-auth-google-block {
    margin-bottom: 22px;
}
.mb-oauth-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0;
}
.mb-oauth-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    min-height: 44px;
    padding: 0 16px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    border: 1px solid rgba(228, 228, 231, .12);
    transition: background .15s ease, box-shadow .15s ease, transform .12s ease;
    cursor: pointer;
    letter-spacing: -.01em;
}
.mb-oauth-btn:hover {
    transform: translateY(-1px);
}
.mb-oauth-btn.disabled {
    opacity: .4;
    cursor: not-allowed;
    pointer-events: none;
}
.mb-oauth-google {
    background: #fafafa !important;
    color: #18181b !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, .12);
}
.mb-oauth-google:hover {
    background: #ffffff !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, .18);
}
.mb-oauth-google .g-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}
.mb-auth-trust {
    text-align: center;
    color: #52525b !important;
    font-size: 11px;
    margin-top: 10px;
    line-height: 1.45;
    letter-spacing: .01em;
}
.mb-auth-trust strong {
    color: #71717a !important;
    font-weight: 600;
}
.mb-auth-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 20px 0;
    color: #52525b !important;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.mb-auth-divider::before,
.mb-auth-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(63, 63, 70, .8);
}

/* ── Form inputs ───────────────────────────────────────────── */
.mb-auth-page [data-testid="stForm"] {
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.mb-auth-page [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 14px !important;
}
.mb-auth-page [data-testid="stTextInput"] label,
.mb-auth-page [data-testid="stNumberInput"] label,
.mb-auth-page [data-testid="stTextInput"] [data-testid="stWidgetLabel"] p,
.mb-auth-page [data-testid="stNumberInput"] [data-testid="stWidgetLabel"] p {
    color: #a1a1aa !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    margin-bottom: 6px !important;
    letter-spacing: .01em;
}
.mb-auth-page [data-testid="stTextInput"] > div,
.mb-auth-page [data-testid="stNumberInput"] > div,
.mb-auth-page [data-testid="stTextInput"] fieldset,
.mb-auth-page [data-testid="stNumberInput"] fieldset {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
.mb-auth-page [data-testid="stTextInput"] div[data-baseweb="input"],
.mb-auth-page [data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: rgba(9, 9, 11, .65) !important;
    border: 1px solid rgba(63, 63, 70, .85) !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    box-shadow: none !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}
.mb-auth-page [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
.mb-auth-page [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, .18) !important;
}
.mb-auth-page [data-testid="stTextInput"] input,
.mb-auth-page [data-testid="stNumberInput"] input {
    background: transparent !important;
    color: #fafafa !important;
    -webkit-text-fill-color: #fafafa !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    border: none !important;
}
.mb-auth-page [data-testid="stTextInput"] input::placeholder {
    color: #52525b !important;
}
.mb-auth-page [data-testid="stTextInput"] button {
    color: #71717a !important;
    background: transparent !important;
}

/* ── Submit buttons — violet, never Streamlit red ─────────── */
.mb-auth-page .stFormSubmitButton > button,
.mb-auth-page .stFormSubmitButton button,
.mb-auth-page [data-testid="stFormSubmitButton"] > button,
.mb-auth-page [data-testid="stFormSubmitButton"] button,
.mb-auth-page form button[kind="primaryFormSubmit"],
.mb-auth-page form button[data-testid="stBaseButton-primaryFormSubmit"],
.mb-auth-page form button[data-testid="stBaseButton-primary"] {
    min-height: 44px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(109, 40, 217, .5) !important;
    background: linear-gradient(180deg, #7c3aed 0%, #6d28d9 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: -.01em;
    box-shadow: 0 1px 2px rgba(0, 0, 0, .2), 0 4px 16px rgba(124, 58, 237, .25) !important;
    margin-top: 4px !important;
    transition: background .15s ease, box-shadow .15s ease, transform .12s ease !important;
}
.mb-auth-page .stFormSubmitButton > button:hover,
.mb-auth-page form button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%) !important;
    background-color: #8b5cf6 !important;
    box-shadow: 0 4px 20px rgba(124, 58, 237, .35) !important;
    transform: translateY(-1px) !important;
    color: #ffffff !important;
}
.mb-auth-page .stFormSubmitButton > button p,
.mb-auth-page form button[kind="primaryFormSubmit"] p {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Captcha refresh — subtle */
.mb-auth-page .mb-auth-captcha-row [data-testid="stFormSubmitButton"] > button,
.mb-auth-page .mb-auth-captcha-row form button {
    min-height: 44px !important;
    background: rgba(39, 39, 42, .8) !important;
    border: 1px solid rgba(63, 63, 70, .8) !important;
    color: #a1a1aa !important;
    box-shadow: none !important;
}

/* ── Footer & misc ──────────────────────────────────────────── */
.mb-auth-foot {
    text-align: center;
    color: #52525b !important;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid rgba(63, 63, 70, .5);
}
.mb-auth-foot strong {
    color: #71717a !important;
    font-weight: 600;
}
.mb-auth-page [data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid rgba(63, 63, 70, .5) !important;
    border-radius: 10px !important;
    margin-top: 12px !important;
}
.mb-auth-page [data-testid="stExpander"] summary {
    color: #71717a !important;
    font-size: 12px !important;
}
.mb-auth-page .stCaption,
.mb-auth-page [data-testid="stCaptionContainer"] {
    color: #52525b !important;
    font-size: 11px !important;
}
.mb-auth-page [data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 13px !important;
}

/* Hide Streamlit border wrapper if used */
.mb-auth-page div[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

@media (max-width: 900px) {
    .mb-auth-brand {
        padding: 24px 0 8px 0;
        text-align: center;
        max-width: none;
    }
    .mb-auth-brand-inner { position: static; }
    [data-testid="stImage"] img { margin-left: auto !important; margin-right: auto !important; }
    .mb-auth-hero-desc, .mb-auth-stats { margin-left: auto; margin-right: auto; }
    .mb-auth-stat { text-align: left; }
    .mb-auth-panel-shell { min-height: auto; padding: 8px 0 32px 0; }
    .mb-auth-panel { padding: 28px 22px 22px 22px; }
}
"""
)


def render_brand_column() -> None:
    import streamlit as st

    name = html.escape(APP_NAME)
    tagline = html.escape(APP_TAGLINE)

    st.markdown('<div class="mb-auth-brand"><div class="mb-auth-brand-inner">', unsafe_allow_html=True)

    if WORDMARK.exists():
        st.image(str(WORDMARK), width=168)
    else:
        st.markdown(
            f'<div class="mb-auth-logo-fallback">{html.escape(APP_NAME[:1])}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
    <p class="mb-auth-eyebrow">Creator Operating System</p>
    <h1 class="mb-auth-hero-title">{name}</h1>
    <p class="mb-auth-hero-tagline">{tagline}</p>
    <p class="mb-auth-hero-desc">
        Video, Bild, Code und KI-Chat in einer Plattform — für Teams,
        die ohne Tool-Chaos skalieren wollen.
    </p>
    <div class="mb-auth-stats">
        <div class="mb-auth-stat">
            <div class="mb-auth-stat-icon">◈</div>
            <div>
                <strong>Unified Workspace</strong>
                <span>Shorts, Image Studio, Chat und Code — ein Interface.</span>
            </div>
        </div>
        <div class="mb-auth-stat">
            <div class="mb-auth-stat-icon">◎</div>
            <div>
                <strong>Enterprise Session</strong>
                <span>Sichere OAuth-Anmeldung, Token-Billing, Queue-System.</span>
            </div>
        </div>
        <div class="mb-auth-stat">
            <div class="mb-auth-stat-icon">▣</div>
            <div>
                <strong>Production Ready</strong>
                <span>Render, planen und veröffentlichen — direkt aus dem Studio.</span>
            </div>
        </div>
    </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)


def panel_header_html(*, mode: str) -> str:
    if mode == "register":
        return """
<div class="mb-auth-panel-head">
    <h1>Account erstellen</h1>
    <p>Kostenlos starten — Workspace in unter einer Minute.</p>
</div>
"""
    return """
<div class="mb-auth-panel-head">
    <h1>Willkommen zurück</h1>
    <p>Melde dich an und öffne deinen Workspace.</p>
</div>
"""


def auth_styles_bundle() -> str:
    return (
        MB_THEME_VARS
        + AUTH_PREMIUM_CSS
        + """
.custom-topbar, #MainMenu, header, footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"], [data-testid="stHeader"] {
    display: none !important;
}
section.main .block-container {
    max-width: 1080px !important;
    padding: 32px 28px 48px 28px !important;
}
"""
    )
