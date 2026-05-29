"""Premium login shell — HTML + CSS for MaByte auth page."""
from __future__ import annotations

import html

from config import APP_NAME, APP_TAGLINE
from ui.b2b_theme import MB_APP_BACKGROUND, MB_THEME_VARS
from ui_core import WORDMARK


AUTH_PREMIUM_CSS = (
    """
.stApp, [data-testid="stAppViewContainer"] {
    background: """
    + MB_APP_BACKGROUND
    + """ !important;
    background-color: #09090b !important;
}
section.main .block-container,
section.main [data-testid="stVerticalBlock"],
section.main [data-testid="column"],
section.main .element-container {
    visibility: visible !important;
    opacity: 1 !important;
}
.mb-auth-brand {
    padding: 12px 8px 24px 8px;
}
.mb-auth-logo img {
    max-width: 200px;
    display: block;
    margin-bottom: 28px;
    filter: drop-shadow(0 12px 40px rgba(124, 58, 237, .35));
}
.mb-auth-logo-fallback {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #fff;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 28px;
}
.mb-auth-eyebrow {
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .22em;
    text-transform: uppercase;
    margin: 0 0 12px 0;
}
.mb-auth-hero-title {
    font-size: clamp(36px, 4.5vw, 52px);
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -.045em;
    margin: 0 0 14px 0;
    background: linear-gradient(135deg, #fafafa 0%, #e4e4e7 40%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.mb-auth-hero-tagline {
    font-size: clamp(18px, 2vw, 22px);
    font-weight: 600;
    color: #d4d4d8 !important;
    margin: 0 0 16px 0;
    letter-spacing: -.02em;
}
.mb-auth-hero-desc {
    color: #a1a1aa !important;
    font-size: 15px;
    line-height: 1.65;
    max-width: 480px;
    margin: 0 0 24px 0;
}
.mb-auth-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 28px;
}
.mb-auth-pill {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    color: #d4d4d8 !important;
    background: rgba(39, 39, 42, .85);
    border: 1px solid #3f3f46;
}
.mb-auth-features {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 520px;
}
.mb-auth-feature {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, .75);
    border: 1px solid #3f3f46;
}
.mb-auth-feature strong {
    display: block;
    color: #fafafa !important;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 4px;
}
.mb-auth-feature span {
    color: #71717a !important;
    font-size: 12px;
    line-height: 1.4;
}

.mb-auth-card-wrap {
    max-width: 420px;
    margin: 0 auto;
}
.mb-auth-card-hero {
    text-align: center;
    margin-bottom: 20px;
}
.mb-auth-card-hero h1 {
    color: #fafafa !important;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -.03em;
    margin: 0 0 6px 0;
}
.mb-auth-card-hero p {
    color: #a1a1aa !important;
    font-size: 14px;
    margin: 0;
    line-height: 1.45;
}

.mb-auth-google-block {
    margin-bottom: 18px;
}
.mb-auth-google-block .mb-oauth-btn.mb-oauth-google {
    min-height: 52px !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    background: #fafafa !important;
    color: #18181b !important;
    border: 1px solid #e4e4e7 !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, .25), 0 0 0 1px rgba(255, 255, 255, .06) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
.mb-auth-google-block .mb-oauth-btn.mb-oauth-google:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 32px rgba(124, 58, 237, .25) !important;
}
.mb-auth-google-block .mb-oauth-btn.mb-oauth-google .g-icon {
    width: 22px;
    height: 22px;
}
.mb-auth-trust {
    text-align: center;
    color: #71717a !important;
    font-size: 11px;
    margin-top: 10px;
    line-height: 1.5;
}
.mb-auth-trust strong {
    color: #a1a1aa !important;
}

section.main div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(24, 24, 27, .92) !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 20px !important;
    padding: 24px 22px 20px 22px !important;
    box-shadow:
        0 32px 64px rgba(0, 0, 0, .5),
        0 0 0 1px rgba(255, 255, 255, .04) inset !important;
    backdrop-filter: blur(20px);
}

@media (max-width: 900px) {
    .mb-auth-features { grid-template-columns: 1fr; }
    .mb-auth-brand { text-align: center; }
    .mb-auth-logo img, .mb-auth-logo-fallback { margin-left: auto; margin-right: auto; }
    .mb-auth-hero-desc { margin-left: auto; margin-right: auto; }
    .mb-auth-pill-row { justify-content: center; }
}
"""
)


def render_brand_column() -> None:
    """Logo via st.image — avoids 1MB+ inline base64 breaking Streamlit on Railway."""
    import streamlit as st

    st.markdown('<div class="mb-auth-brand">', unsafe_allow_html=True)
    if WORDMARK.exists():
        st.image(str(WORDMARK), width="stretch")
    else:
        st.markdown(
            f'<div class="mb-auth-logo-fallback">{html.escape(APP_NAME[:1])}</div>',
            unsafe_allow_html=True,
        )

    tagline = html.escape(APP_TAGLINE)
    name = html.escape(APP_NAME)
    st.markdown(
        f"""
    <p class="mb-auth-eyebrow">Creator Operating System · B2B Ready</p>
    <h1 class="mb-auth-hero-title">{name}</h1>
    <p class="mb-auth-hero-tagline">{tagline}</p>
    <p class="mb-auth-hero-desc">
        Eine Plattform für Video, Bild, Code und KI-Chat — gebaut für Teams,
        die professionell skalieren wollen. Kein Tool-Zoo. Ein System.
    </p>
    <div class="mb-auth-pill-row">
        <span class="mb-auth-pill">Shorts &amp; Video</span>
        <span class="mb-auth-pill">Image Studio</span>
        <span class="mb-auth-pill">AI Chat</span>
        <span class="mb-auth-pill">Code Studio</span>
    </div>
    <div class="mb-auth-features">
        <div class="mb-auth-feature">
            <strong>Produktions-UI</strong>
            <span>Dunkles Zinc-Design, klare Workspaces, Enterprise-Feeling.</span>
        </div>
        <div class="mb-auth-feature">
            <strong>Token-Billing</strong>
            <span>Transparente Kosten pro Aktion — planbar für Teams.</span>
        </div>
        <div class="mb-auth-feature">
            <strong>Google Sign-In</strong>
            <span>Sicherer OAuth-Login ohne Passwort-Chaos.</span>
        </div>
        <div class="mb-auth-feature">
            <strong>Queue &amp; Publish</strong>
            <span>Reels rendern, planen und veröffentlichen in einem Flow.</span>
        </div>
    </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def card_hero_html() -> str:
    return """
<div class="mb-auth-card-hero">
    <h1>Willkommen zurück</h1>
    <p>Melde dich an und öffne deinen MaByte Workspace.</p>
</div>
"""


def auth_styles_bundle() -> str:
    """Lighter than full app shell — no duplicate mega CSS on login route."""
    return (
        MB_THEME_VARS
        + AUTH_PREMIUM_CSS
        + """
.custom-topbar, #MainMenu, header, footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"] { display: none !important; }
.stApp, [data-testid="stAppViewContainer"] {
    background: """
        + MB_APP_BACKGROUND
        + """ !important;
}
section.main .block-container {
    max-width: 1180px !important;
    padding: 40px 28px 56px 28px !important;
    min-height: 100vh !important;
}
"""
    )
