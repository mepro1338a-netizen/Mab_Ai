"""Premium SaaS UI layer — hides default Streamlit chrome on Creator/Reels surfaces."""

PREMIUM_STUDIO_CSS = """
/* ── Scope: main content (Creator / Reels) ── */
section.main .block-container {
    max-width: 1040px !important;
    padding-top: 10px !important;
    padding-bottom: 40px !important;
}
section.main [data-testid="stVerticalBlock"] {
    gap: 12px !important;
}
section.main [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    align-items: stretch !important;
}

/* ── Format segmented (creator_format) ── */
.mb-format-bar {
    display: flex;
    gap: 8px;
    padding: 6px;
    border-radius: 18px;
    background: rgba(10, 12, 24, .55);
    border: 1px solid rgba(255, 255, 255, .08);
    backdrop-filter: blur(16px);
    margin: 0 0 14px 0;
    max-width: 320px;
}
div[class*="st-key-creator_fmt_"] button {
    width: 100% !important;
    min-height: 40px !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
    letter-spacing: -0.01em !important;
    border: 1px solid rgba(255, 255, 255, .08) !important;
    background: rgba(10, 12, 24, .35) !important;
    color: rgba(226, 232, 240, .92) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04) !important;
    transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease, background .14s ease;
}
div[class*="st-key-creator_fmt_"] button:hover {
    transform: translateY(-1px);
    border-color: rgba(168, 85, 247, .22) !important;
    box-shadow: 0 10px 28px rgba(0, 0, 0, .22), 0 0 22px rgba(124, 58, 237, .10) !important;
}
div[class*="st-key-creator_fmt_"] button[kind="primary"],
div[class*="st-key-creator_fmt_"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(124, 58, 237, .55), rgba(59, 130, 246, .22)) !important;
    border-color: rgba(168, 85, 247, .38) !important;
    color: #fff !important;
    box-shadow: 0 14px 40px rgba(124, 58, 237, .16), 0 0 28px rgba(168, 85, 247, .12) !important;
}

/* ── Card pickers (platform / duration / style) ── */
div[class*="st-key-rs_pick_"] button {
    min-height: 96px !important;
    height: auto !important;
    padding: 14px 16px !important;
    border-radius: 18px !important;
    text-align: left !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    background:
        radial-gradient(circle at 30% 0%, rgba(168, 85, 247, .10), transparent 42%),
        linear-gradient(180deg, rgba(12, 18, 38, .72), rgba(8, 10, 22, .88)) !important;
    border: 1px solid rgba(255, 255, 255, .09) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04), 0 10px 30px rgba(0, 0, 0, .18) !important;
    transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease, background .14s ease;
}
div[class*="st-key-rs_pick_"] button:hover {
    transform: translateY(-2px);
    border-color: rgba(168, 85, 247, .24) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05), 0 16px 44px rgba(0, 0, 0, .26), 0 0 28px rgba(124, 58, 237, .12) !important;
}
div[class*="st-key-rs_pick_"] button[kind="primary"],
div[class*="st-key-rs_pick_"] [data-testid="stBaseButton-primary"] {
    border-color: rgba(168, 85, 247, .48) !important;
    background:
        radial-gradient(circle at 30% 0%, rgba(168, 85, 247, .22), transparent 45%),
        linear-gradient(180deg, rgba(22, 12, 38, .92), rgba(8, 10, 22, .92)) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, .06),
        0 0 0 1px rgba(168, 85, 247, .18),
        0 18px 55px rgba(124, 58, 237, .18),
        0 0 36px rgba(168, 85, 247, .14) !important;
}
div[class*="st-key-rs_pick_"] button p {
    white-space: pre-line !important;
    text-align: left !important;
    margin: 0 !important;
    width: 100% !important;
    color: rgba(148, 163, 184, .95) !important;
    font-size: 11px !important;
    line-height: 1.35 !important;
}
div[class*="st-key-rs_pick_"] button p::first-line {
    display: block;
    font-size: 13px !important;
    font-weight: 1000 !important;
    color: #ffffff !important;
    letter-spacing: -0.01em;
    margin-bottom: 2px;
}

/* ── Prompt glass (no white textarea) ── */
.st-key-rs_prompt [data-testid="stTextArea"],
.st-key-rs_prompt [data-testid="stTextArea"] > div,
.st-key-rs_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"],
.st-key-rs_prompt [data-baseweb="textarea"] {
    background: rgba(10, 12, 24, .72) !important;
    background-color: rgba(10, 12, 24, .72) !important;
    border: 1px solid rgba(168, 85, 247, .28) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(18px);
    box-shadow: inset 0 2px 14px rgba(0, 0, 0, .28), 0 0 32px rgba(124, 58, 237, .08) !important;
}
.st-key-rs_prompt textarea,
.st-key-rs_prompt [data-testid="stTextArea"] textarea,
.st-key-rs_prompt [data-baseweb="textarea"] textarea {
    background: transparent !important;
    background-color: transparent !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    caret-color: #f8fafc !important;
    font-size: 15px !important;
    line-height: 1.55 !important;
    min-height: 128px !important;
}
.st-key-rs_prompt textarea::placeholder {
    color: rgba(148, 163, 184, .75) !important;
    -webkit-text-fill-color: rgba(148, 163, 184, .75) !important;
}

.st-key-rs_create button {
    min-height: 48px !important;
    font-weight: 1000 !important;
    letter-spacing: -0.01em !important;
    border-radius: 16px !important;
}
.st-key-rs_prompt_enhance button {
    min-height: 48px !important;
    border-radius: 16px !important;
    background: rgba(10, 12, 24, .45) !important;
}

.st-key-rs_auto_meta label,
.st-key-rs_publish_consent label,
.st-key-rs_post_consent_final label,
.st-key-rs_auto_post label {
    color: rgba(226, 232, 240, .92) !important;
    font-size: 13px !important;
}
"""
