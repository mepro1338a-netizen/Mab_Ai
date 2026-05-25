"""
Image Studio — SaaS-style workspace UI.
"""
from __future__ import annotations

import html

import streamlit as st

from pricing import get_image_cost
from ui.prompt_ui import prompt_text_area
from ui.styles import inject_css, page_layout_css


IMAGE_STUDIO_CSS = """
/* Weniger Leerraum unter der Topbar (nur Image Studio) */
section.main .block-container {
    padding-top: 8px !important;
    padding-bottom: 36px !important;
}
section.main .block-container > div {
    gap: 0.4rem !important;
}
.img-studio {
    margin-bottom: 16px;
    margin-top: 0 !important;
}
.img-hero {
    border-radius: 20px;
    padding: 18px 22px 16px 22px;
    margin-bottom: 14px;
    background:
        radial-gradient(circle at 92% 8%, rgba(96,165,250,.18), transparent 38%),
        radial-gradient(circle at 6% 0%, rgba(168,85,247,.16), transparent 36%),
        linear-gradient(135deg, rgba(14,18,38,.97), rgba(8,10,24,.99));
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 24px 56px rgba(0,0,0,.28);
}
.img-kicker {
    color: #94a3b8 !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .2em;
    text-transform: uppercase;
}
.img-title {
    color: #ffffff !important;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -.6px;
    margin-top: 6px;
    line-height: 1.15;
}
.img-sub {
    color: #94a3b8 !important;
    font-size: 14px;
    line-height: 1.5;
    max-width: 680px;
    margin-top: 8px;
}
.img-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 12px;
}
.img-chip {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    color: #e2e8f0 !important;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.1);
}
.img-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 18px;
}
@media (max-width: 768px) {
    .img-stat-grid { grid-template-columns: 1fr; }
}
.img-stat {
    border-radius: 18px;
    padding: 16px 18px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
}
.img-stat-lbl {
    color: #94a3b8 !important;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
}
.img-stat-val {
    color: #ffffff !important;
    font-size: 22px;
    font-weight: 800;
    margin-top: 6px;
    line-height: 1.1;
}
.img-stat-sub {
    color: #64748b !important;
    font-size: 12px;
    margin-top: 4px;
}
.img-card {
    border-radius: 22px;
    padding: 22px 24px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 14px;
}
.img-card-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 4px;
}
.img-card-desc {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 14px;
}
.img-side-panel {
    border-radius: 22px;
    padding: 20px 22px;
    background: linear-gradient(160deg, rgba(30,32,40,.6), rgba(18,20,28,.85));
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 14px;
}
.img-side-title {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 12px;
}
.img-checklist {
    margin: 0;
    padding: 0;
    list-style: none;
}
.img-checklist li {
    color: #cbd5e1 !important;
    font-size: 13px;
    line-height: 1.5;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.img-checklist li:last-child { border-bottom: none; }
.img-checklist li::before {
    content: "✓";
    color: #64748b;
    margin-right: 10px;
    font-weight: 800;
}
.img-empty {
    border-radius: 18px;
    padding: 28px 20px;
    text-align: center;
    border: 1px dashed rgba(255,255,255,.12);
    background: rgba(0,0,0,.15);
}
.img-empty-title {
    color: #e2e8f0 !important;
    font-size: 14px;
    font-weight: 700;
}
.img-empty-sub {
    color: #64748b !important;
    font-size: 12px;
    margin-top: 6px;
    line-height: 1.45;
}
.img-studio div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.02) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 22px !important;
    box-shadow: none !important;
}
.img-size-section-title {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 800;
    margin: 16px 0 4px 0;
}
.img-size-section-sub {
    color: #64748b !important;
    font-size: 12px;
    margin: 0 0 12px 0;
    line-height: 1.45;
}
.img-size-group-title {
    color: #cbd5e1 !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin: 14px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.img-size-group-icon {
    color: #94a3b8 !important;
    font-size: 14px;
}
.img-preset-card {
    border-radius: 14px;
    padding: 12px 12px 10px 12px;
    margin-bottom: 6px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    transition: border-color .15s ease, box-shadow .15s ease;
}
.img-preset-card.is-active {
    border-color: rgba(255,255,255,.35) !important;
    background: rgba(255,255,255,.07);
    box-shadow: 0 0 0 1px rgba(255,255,255,.12), 0 8px 24px rgba(0,0,0,.2);
}
.img-preset-tier {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 800;
    line-height: 1.2;
}
.img-preset-px {
    color: #e2e8f0 !important;
    font-size: 13px;
    font-weight: 700;
    margin-top: 4px;
}
.img-preset-hint {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 4px;
    line-height: 1.35;
}
.img-preset-summary {
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 12px;
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.12);
}
.img-preset-summary strong {
    color: #ffffff !important;
    font-size: 14px;
}
.img-preset-summary span {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.45;
}
.img-quality-label {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-bottom: 6px;
}
"""


USE_CASES = [
    ("Thumbnail", "thumbnail"),
    ("Cover Art", "cover"),
    ("Social Post", "social"),
    ("Product Shot", "product"),
    ("App Mockup", "mockup"),
]

STYLE_PRESETS = [
    "SaaS Clean",
    "Cinematic Dark",
    "Neon Tech",
    "Minimal White",
    "Bold Thumbnail",
    "Luxury Brand",
]

# Format + Auflösung als Presets (gruppiert in der UI)
IMAGE_SIZE_PRESETS: list[dict[str, str]] = [
    {"id": "square_1k", "tier": "Standard", "format_name": "Quadrat", "hint": "Instagram & Avatar", "pixels": "1024 × 1024", "aspect": "1:1", "size": "1024"},
    {"id": "square_2k", "tier": "Groß", "format_name": "Quadrat", "hint": "Print & scharfe Posts", "pixels": "2048 × 2048", "aspect": "1:1", "size": "2048"},
    {"id": "compact", "tier": "Kompakt", "format_name": "Quadrat", "hint": "Schnelle Entwürfe", "pixels": "512 × 512", "aspect": "1:1", "size": "512"},
    {"id": "balanced", "tier": "Mittel", "format_name": "Quadrat", "hint": "Beste Balance", "pixels": "1536 × 1536", "aspect": "1:1", "size": "1536"},
    {"id": "story_1k", "tier": "Standard", "format_name": "Story", "hint": "TikTok & Reels", "pixels": "1024 × 1820", "aspect": "9:16", "size": "1024"},
    {"id": "story_2k", "tier": "Groß", "format_name": "Story", "hint": "Full-HD Stories", "pixels": "2048 × 3640", "aspect": "9:16", "size": "2048"},
    {"id": "wide_1k", "tier": "Standard", "format_name": "Breit", "hint": "YouTube & Banner", "pixels": "1024 × 576", "aspect": "16:9", "size": "1024"},
    {"id": "wide_2k", "tier": "Groß", "format_name": "Breit", "hint": "Hero & Web-Header", "pixels": "2048 × 1152", "aspect": "16:9", "size": "2048"},
    {"id": "portrait_1k", "tier": "Standard", "format_name": "Hochformat", "hint": "Pinterest & Ads", "pixels": "1024 × 1280", "aspect": "4:5", "size": "1024"},
    {"id": "portrait_2k", "tier": "Groß", "format_name": "Hochformat", "hint": "Große Feed-Bilder", "pixels": "2048 × 2560", "aspect": "4:5", "size": "2048"},
]

PRESET_GROUPS: list[tuple[str, str, list[str]]] = [
    ("Quadrat · 1:1", "□", ["square_1k", "square_2k", "compact", "balanced"]),
    ("Story · 9:16", "▯", ["story_1k", "story_2k"]),
    ("Breit · 16:9", "▬", ["wide_1k", "wide_2k"]),
    ("Hochformat · 4:5", "▮", ["portrait_1k", "portrait_2k"]),
]

_PRESET_BY_ID = {p["id"]: p for p in IMAGE_SIZE_PRESETS}
for _p in IMAGE_SIZE_PRESETS:
    _p["label"] = f"{_p['format_name']} · {_p['tier']}"


def _preset_from_session() -> dict[str, str]:
    pid = st.session_state.get("image_preset_id", "square_1k")
    return _PRESET_BY_ID.get(pid) or IMAGE_SIZE_PRESETS[0]


def _quality_label(q: str) -> str:
    return "HD · mehr Details" if q == "hd" else "Standard · schnell"


def _render_size_preset_grid() -> None:
    st.session_state.setdefault("image_preset_id", "square_1k")
    active_id = str(st.session_state.image_preset_id)

    for group_title, icon, preset_ids in PRESET_GROUPS:
        st.markdown(
            f'<div class="img-size-group-title">'
            f'<span class="img-size-group-icon">{html.escape(icon)}</span>'
            f'{html.escape(group_title)}</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(len(preset_ids), gap="small")
        for col, pid in zip(cols, preset_ids):
            p = _PRESET_BY_ID[pid]
            is_active = active_id == pid
            active_cls = " is-active" if is_active else ""
            with col:
                st.markdown(
                    f'<div class="img-preset-card{active_cls}">'
                    f'<div class="img-preset-tier">{html.escape(p["tier"])}</div>'
                    f'<div class="img-preset-px">{html.escape(p["pixels"])}</div>'
                    f'<div class="img-preset-hint">{html.escape(p["hint"])}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                btn_label = "✓ Aktiv" if is_active else "Wählen"
                if st.button(btn_label, key=f"preset_pick_{pid}", width="stretch"):
                    st.session_state.image_preset_id = pid
                    st.rerun()


def inject_image_studio_css() -> None:
    inject_css(page_layout_css(1200, 8, 40) + IMAGE_STUDIO_CSS)


def _build_image_prompt(
    prompt: str,
    *,
    use_case: str,
    style: str,
    quality: str,
    size: str,
    aspect: str,
) -> str:
    return f"""
Erstelle ein professionelles IMAGE-STUDIO Paket für MaByte (SaaS-Qualität).

Nutzer-Prompt:
{prompt}

Einstellungen:
- Use Case: {use_case}
- Stil: {style}
- Qualität: {quality}
- Export: {size}px ({aspect})
- Ziel-Pixel: passend zum Preset

Liefere strukturiert:

# Bildkonzept
(Kurz, klar, 2–3 Sätze)

# DALL·E / Midjourney Prompt (EN)
(Ein optimierter Prompt, copy-paste ready)

# Negative Prompt
(was vermieden werden soll)

# Komposition & Layout
(Raster, Fokus, Text-Safe-Zone falls Thumbnail)

# Farbpalette
(3–5 Hex oder Farbnamen)

# Typografie-Hinweis
(nur falls relevant für Thumbnail/Cover)

# Export
(Dateiname-Vorschlag, Format, {size}px Hinweis)

# Varianten
(3 kurze Alternativ-Ideen, je 1 Zeile)

Ton: professionell, SaaS, umsetzbar für Creator & Brands.
"""


def render_image_studio(
    *,
    tokens_available: int,
    on_generate,
) -> None:
    """
    on_generate(prompt: str, cost: int, full_prompt: str) — caller runs run_paid_ai.
    """
    inject_image_studio_css()

    st.markdown('<div class="img-studio">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="img-hero">
    <div class="img-kicker">MaByte Studios · Image</div>
    <div class="img-title">Image Studio</div>
    <div class="img-sub">
        Thumbnails, Cover und Visuals in Minuten — mit fertigen KI-Prompts,
        Farbpalette und Export-Vorgaben für deine Pipeline.
    </div>
    <div class="img-chip-row">
        <span class="img-chip">Thumbnail</span>
        <span class="img-chip">Social</span>
        <span class="img-chip">Story</span>
        <span class="img-chip">Banner</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    preset = _preset_from_session()
    quality = st.session_state.get("image_quality", "standard")
    cost = get_image_cost(quality=quality, size=preset["size"])

    tokens_fmt = f"{tokens_available:,}".replace(",", ".")
    st.markdown(
        f"""
<div class="img-stat-grid">
    <div class="img-stat">
        <div class="img-stat-lbl">Verfügbar</div>
        <div class="img-stat-val">{tokens_fmt}</div>
        <div class="img-stat-sub">Tokens</div>
    </div>
    <div class="img-stat">
        <div class="img-stat-lbl">Diese Generierung</div>
        <div class="img-stat-val">{cost}</div>
        <div class="img-stat-sub">Tokens · live</div>
    </div>
    <div class="img-stat">
        <div class="img-stat-lbl">Output</div>
        <div class="img-stat-val">Paket</div>
        <div class="img-stat-sub">Prompt + Specs</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, 0.85], gap="large")

    with left:
        st.markdown(
            '<div class="img-card-title">Dein Bild</div>'
            '<div class="img-card-desc">Kurz beschreiben — wir liefern Prompt, Stil und Export in einem Paket.</div>',
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            prompt = prompt_text_area(
                placeholder="z.B. SaaS Dashboard Thumbnail, dunkler Hintergrund, lila Akzente, modern…",
                key="image_prompt",
                height=140,
            )

            c1, c2 = st.columns(2)
            with c1:
                use_case_label = st.selectbox(
                    "Verwendung",
                    [u[0] for u in USE_CASES],
                    key="image_use_case_label",
                )
                use_case = dict(USE_CASES).get(use_case_label, "thumbnail")
            with c2:
                style = st.selectbox("Stil", STYLE_PRESETS, key="image_style")

            st.markdown(
                '<div class="img-size-section-title">Format & Auflösung</div>'
                '<div class="img-size-section-sub">Wähle Zielformat und Pixelgröße — alles in einem Schritt.</div>',
                unsafe_allow_html=True,
            )
            _render_size_preset_grid()
            preset = _preset_from_session()

            st.markdown('<div class="img-quality-label">Render-Qualität</div>', unsafe_allow_html=True)
            q1, q2 = st.columns([1.2, 0.8])
            with q1:
                quality = st.radio(
                    "Qualität",
                    options=["standard", "hd"],
                    format_func=_quality_label,
                    horizontal=True,
                    key="image_quality",
                    label_visibility="collapsed",
                )
            with q2:
                cost = get_image_cost(quality=quality, size=preset["size"])
                st.metric("Diese Generierung", f"{cost} Tokens")

            st.markdown(
                f"""
<div class="img-preset-summary">
    <strong>{html.escape(preset["format_name"])} · {html.escape(preset["tier"])}</strong><br>
    <span>{html.escape(preset["pixels"])} · Format {html.escape(preset["aspect"])} · {html.escape(preset["hint"])}</span>
</div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="mb-btn-gold">', unsafe_allow_html=True)
        if st.button(
            "Bild-Paket erstellen",
            width="stretch",
            key="btn_image",
            type="primary",
        ):
            if not (prompt or "").strip():
                st.warning("Bitte kurz beschreiben, welches Bild du brauchst.")
            elif tokens_available < cost:
                st.error(f"Nicht genug Tokens ({tokens_available} / {cost} benötigt).")
            else:
                full = _build_image_prompt(
                    prompt.strip(),
                    use_case=use_case,
                    style=style,
                    quality=quality,
                    size=preset["size"],
                    aspect=preset["aspect"],
                )
                on_generate(prompt.strip(), cost, full)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
<div class="img-side-panel">
    <div class="img-side-title">Dein Paket enthält</div>
    <ul class="img-checklist">
        <li>Fertiger EN-Prompt zum Kopieren</li>
        <li>Negative Prompts & Layout</li>
        <li>Farbpalette & Export-Hinweise</li>
        <li>3 Varianten zum Testen</li>
    </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="img-side-panel">
    <div class="img-side-title">Tipps für starke Visuals</div>
    <ul class="img-checklist">
        <li>Thumbnail: Textfreier Bereich oben</li>
        <li>Story: Kontrast für Mobile</li>
        <li>Markenfarben im Prompt nennen</li>
        <li>Groß = Print & Hero geeignet</li>
    </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
<div class="img-empty">
    <div class="img-empty-title">Bereit zum Erstellen</div>
    <div class="img-empty-sub">
        Nach „Bild-Paket erstellen“ erscheint dein Ergebnis
        unten — inklusive Download.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )
        plan = html.escape(str(st.session_state.get("plan", "free")))
        st.caption(f"Aktueller Plan: **{plan}** · Image Studio inkl. Token-Abrechnung")

    st.markdown("</div>", unsafe_allow_html=True)
