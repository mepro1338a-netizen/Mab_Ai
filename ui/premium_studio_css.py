"""Premium SaaS UI layer — Creator / Reels Studio."""

PREMIUM_STUDIO_CSS = """
/* Hide duplicate global slogan when Reels studio is active */
.stApp:has(.rs-studio) .custom-topbar {
    display: none !important;
}
.stApp:has(.rs-studio) section.main .block-container {
    padding-top: 18px !important;
}

section.main .block-container {
    max-width: 1040px !important;
    padding-bottom: 44px !important;
}
section.main [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
section.main [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    align-items: stretch !important;
}

/* ── Format segmented ── */
div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-creator_fmt_"]) {
    display: inline-flex !important;
    width: auto !important;
    max-width: fit-content !important;
    gap: 6px !important;
    padding: 5px !important;
    border-radius: 16px !important;
    background: rgba(10, 12, 24, .62) !important;
    border: 1px solid rgba(255, 255, 255, .09) !important;
    backdrop-filter: blur(18px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, .22) !important;
    margin-bottom: 12px !important;
}
div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-creator_fmt_"]) [data-testid="column"] {
    width: auto !important;
    min-width: 108px !important;
    flex: 0 0 auto !important;
}
div[class*="st-key-creator_fmt_"] button {
    min-height: 38px !important;
    padding: 0 18px !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    letter-spacing: -0.02em !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: rgba(148, 163, 184, .95) !important;
    box-shadow: none !important;
}
div[class*="st-key-creator_fmt_"] button:hover {
    color: #fff !important;
    background: rgba(255, 255, 255, .04) !important;
}
div[class*="st-key-creator_fmt_"] button[kind="primary"],
div[class*="st-key-creator_fmt_"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(124, 58, 237, .72), rgba(59, 130, 246, .28)) !important;
    border: 1px solid rgba(168, 85, 247, .35) !important;
    color: #fff !important;
    box-shadow: 0 8px 28px rgba(124, 58, 237, .18) !important;
}

/* ── Workflow step nav ── */
div[class*="st-key-rs_step_nav_"] {
    position: relative;
    z-index: 1;
}
div[class*="st-key-rs_step_nav_"] button {
    min-height: 56px !important;
    padding: 8px 6px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, .08) !important;
    background: rgba(10, 12, 24, .45) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04) !important;
}
div[class*="st-key-rs_step_nav_"] button:hover {
    transform: translateY(-1px);
    border-color: rgba(168, 85, 247, .22) !important;
    box-shadow: 0 10px 28px rgba(0, 0, 0, .2), 0 0 20px rgba(124, 58, 237, .1) !important;
}
div[class*="st-key-rs_step_nav_"] button[kind="primary"],
div[class*="st-key-rs_step_nav_"] [data-testid="stBaseButton-primary"] {
    border-color: rgba(168, 85, 247, .45) !important;
    background: linear-gradient(135deg, rgba(124, 58, 237, .55), rgba(59, 130, 246, .22)) !important;
    box-shadow: 0 0 24px rgba(124, 58, 237, .2), inset 0 1px 0 rgba(255, 255, 255, .06) !important;
}
div[class*="st-key-rs_step_nav_"] button p {
    margin: 0 !important;
    white-space: pre-line !important;
    line-height: 1.25 !important;
    text-align: center !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    color: rgba(148, 163, 184, .95) !important;
}
div[class*="st-key-rs_step_nav_"] button[kind="primary"] p,
div[class*="st-key-rs_step_nav_"] [data-testid="stBaseButton-primary"] p {
    color: #fff !important;
}
div[class*="st-key-rs_step_nav_"] button p::first-line {
    font-size: 12px !important;
    font-weight: 900 !important;
    color: #fff !important;
}

/* ── Selection cards ── */
.rs-picker-row [data-testid="column"] {
    display: flex;
    flex-direction: column;
}
div[class*="st-key-rs_pick_"] button {
    min-height: 104px !important;
    padding: 14px 14px 12px 14px !important;
    border-radius: 18px !important;
    text-align: left !important;
    border: 1px solid rgba(255, 255, 255, .09) !important;
    background:
        radial-gradient(circle at 30% 0%, rgba(168, 85, 247, .08), transparent 42%),
        linear-gradient(180deg, rgba(12, 18, 38, .78), rgba(8, 10, 22, .9)) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04), 0 8px 28px rgba(0, 0, 0, .16) !important;
    transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
}
div[class*="st-key-rs_pick_"] button::before {
    content: "";
    display: block;
    width: 32px;
    height: 32px;
    border-radius: 11px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, .12);
    box-shadow: 0 8px 20px rgba(0, 0, 0, .22);
}
.st-key-rs_pick_rs_platform_tiktok button::before {
    background: linear-gradient(135deg, #25f4ee, #fe2c55 55%, #0f0f0f);
}
.st-key-rs_pick_rs_platform_instagram_reels button::before {
    background: linear-gradient(135deg, #f9ce34, #ee2a7b 45%, #6228d7);
}
.st-key-rs_pick_rs_platform_youtube_shorts button::before {
    background: linear-gradient(135deg, #ff0000, #cc0000);
}
.st-key-rs_pick_rs_duration_3 button::before {
    background: linear-gradient(135deg, rgba(96, 165, 250, .9), rgba(59, 130, 246, .5));
}
.st-key-rs_pick_rs_duration_5 button::before {
    background: linear-gradient(135deg, rgba(168, 85, 247, .9), rgba(124, 58, 237, .5));
}
.st-key-rs_pick_rs_duration_7 button::before {
    background: linear-gradient(135deg, rgba(244, 114, 182, .9), rgba(168, 85, 247, .5));
}
.st-key-rs_pick_rs_style_viral button::before {
    background: linear-gradient(135deg, #fbbf24, #f97316);
}
.st-key-rs_pick_rs_style_football button::before {
    background: linear-gradient(135deg, #22c55e, #15803d);
}
.st-key-rs_pick_rs_style_cinematic button::before {
    background: linear-gradient(135deg, #6366f1, #312e81);
}
div[class*="st-key-rs_pick_"] button:hover {
    transform: translateY(-2px);
    border-color: rgba(168, 85, 247, .28) !important;
    box-shadow: 0 14px 40px rgba(0, 0, 0, .24), 0 0 28px rgba(124, 58, 237, .12) !important;
}
div[class*="st-key-rs_pick_"] button[kind="primary"],
div[class*="st-key-rs_pick_"] [data-testid="stBaseButton-primary"] {
    border-color: rgba(168, 85, 247, .5) !important;
    background:
        radial-gradient(circle at 30% 0%, rgba(168, 85, 247, .18), transparent 45%),
        linear-gradient(180deg, rgba(22, 12, 38, .94), rgba(8, 10, 22, .94)) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, .06),
        0 0 0 1px rgba(168, 85, 247, .2),
        0 16px 48px rgba(124, 58, 237, .18) !important;
}
div[class*="st-key-rs_pick_"] button p {
    margin: 0 !important;
    white-space: pre-line !important;
    text-align: left !important;
    font-size: 11px !important;
    line-height: 1.35 !important;
    color: rgba(148, 163, 184, .95) !important;
}
div[class*="st-key-rs_pick_"] button p::first-line {
    font-size: 14px !important;
    font-weight: 900 !important;
    color: #fff !important;
    letter-spacing: -0.02em;
}

/* Prompt */
.st-key-rs_prompt [data-testid="stTextArea"],
.st-key-rs_prompt [data-testid="stTextArea"] > div,
.st-key-rs_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"],
.st-key-rs_prompt [data-baseweb="textarea"] {
    background: rgba(8, 10, 22, .82) !important;
    background-color: rgba(8, 10, 22, .82) !important;
    border: 1px solid rgba(168, 85, 247, .22) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(20px);
}
.st-key-rs_prompt textarea,
.st-key-rs_prompt [data-testid="stTextArea"] textarea {
    background: transparent !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    min-height: 120px !important;
    font-size: 15px !important;
}
.st-key-rs_prompt textarea::placeholder {
    color: rgba(148, 163, 184, .7) !important;
    -webkit-text-fill-color: rgba(148, 163, 184, .7) !important;
}

.st-key-rs_create button {
    min-height: 50px !important;
    font-size: 14px !important;
    font-weight: 900 !important;
    letter-spacing: -0.02em !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #7c3aed, #a855f7 45%, #6366f1) !important;
    border: 1px solid rgba(255, 255, 255, .14) !important;
    box-shadow: 0 18px 50px rgba(124, 58, 237, .25), 0 0 40px rgba(168, 85, 247, .12) !important;
}
.st-key-rs_create button:hover {
    box-shadow: 0 22px 60px rgba(124, 58, 237, .32), 0 0 48px rgba(168, 85, 247, .16) !important;
}
.st-key-rs_prompt_enhance button {
    min-height: 50px !important;
    border-radius: 16px !important;
    background: rgba(10, 12, 24, .5) !important;
    border: 1px solid rgba(255, 255, 255, .1) !important;
}

.st-key-rs_auto_meta label,
.st-key-rs_publish_consent label,
.st-key-rs_post_consent_final label,
.st-key-rs_auto_post label,
div[data-testid="stToggle"] label {
    color: rgba(226, 232, 240, .9) !important;
    font-size: 13px !important;
}

@media (max-width: 900px) {
    .rs-picker-row [data-testid="column"] { min-width: 100% !important; }
    div[class*="st-key-rs_step_nav_"] button { min-height: 48px !important; }
}
"""
