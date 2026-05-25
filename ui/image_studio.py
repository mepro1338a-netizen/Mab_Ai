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
    padding-top: 4px !important;
    padding-bottom: 28px !important;
}
section.main .block-container > div {
    gap: 0.25rem !important;
}
.img-studio {
    margin-bottom: 12px;
    margin-top: 0 !important;
}
.img-topbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px 16px;
    padding: 10px 14px;
    margin-bottom: 10px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(22,24,32,.95), rgba(14,16,22,.98));
    border: 1px solid rgba(255,255,255,.08);
}
.img-topbar-title {
    color: #ffffff !important;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -.3px;
}
.img-topbar-meta {
    color: #94a3b8 !important;
    font-size: 12px;
    font-weight: 600;
}
.img-topbar-meta strong {
    color: #ffffff !important;
    font-weight: 800;
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
    font-size: 13px;
    font-weight: 800;
    margin: 12px 0 2px 0;
}
.img-size-section-sub {
    color: #64748b !important;
    font-size: 11px;
    margin: 0 0 8px 0;
    line-height: 1.4;
}
.img-size-group-title {
    color: #94a3b8 !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin: 10px 0 6px 0;
}
.img-size-btn-wrap {
    margin-bottom: 4px;
}
.img-size-btn-wrap.is-active .stButton > button,
.img-size-btn-wrap.is-active button {
    border: 2px solid rgba(255,255,255,.45) !important;
    background: linear-gradient(135deg, rgba(82,82,88,.98), rgba(52,52,58,.99)) !important;
    color: #ffffff !important;
    box-shadow: 0 0 0 1px rgba(255,255,255,.1), 0 6px 16px rgba(0,0,0,.2) !important;
}
.img-studio .img-size-btn-wrap .stButton > button,
.img-studio .img-size-btn-wrap button {
    min-height: 48px !important;
    padding: 8px 10px !important;
    line-height: 1.3 !important;
    white-space: pre-line !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}
.img-studio .img-size-btn-wrap .stButton > button p,
.img-studio .img-size-btn-wrap button p {
    color: #ffffff !important;
    font-size: 12px !important;
    line-height: 1.3 !important;
}
.img-preset-summary {
    border-radius: 10px;
    padding: 10px 12px;
    margin-top: 8px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.1);
    font-size: 12px;
    color: #94a3b8 !important;
}
.img-preset-summary strong {
    color: #ffffff !important;
}
.img-quality-row {
    margin-top: 8px;
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


def _preset_button_label(p: dict[str, str]) -> str:
    return f"{p['format_name']} · {p['tier']}\n{p['pixels']}"


def _render_size_preset_grid() -> None:
    """Jede Größe = ein Auswahl-Button (ein Klick)."""
    st.session_state.setdefault("image_preset_id", "square_1k")
    active_id = str(st.session_state.image_preset_id)

    for group_title, _icon, preset_ids in PRESET_GROUPS:
        st.markdown(
            f'<div class="img-size-group-title">{html.escape(group_title)}</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(len(preset_ids), gap="small")
        for col, pid in zip(cols, preset_ids):
            p = _PRESET_BY_ID[pid]
            is_active = active_id == pid
            wrap_cls = "img-size-btn-wrap is-active" if is_active else "img-size-btn-wrap"
            with col:
                st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
                if st.button(
                    _preset_button_label(p),
                    key=f"preset_pick_{pid}",
                    width="stretch",
                    type="primary" if is_active else "secondary",
                    help=p.get("hint", ""),
                ):
                    if not is_active:
                        st.session_state.image_preset_id = pid
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


def inject_image_studio_css() -> None:
    inject_css(page_layout_css(1200, 4, 32) + IMAGE_STUDIO_CSS)


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

    preset = _preset_from_session()
    quality = st.session_state.get("image_quality", "standard")
    cost = get_image_cost(quality=quality, size=preset["size"])
    tokens_fmt = f"{tokens_available:,}".replace(",", ".")

    st.markdown(
        f"""
<div class="img-topbar">
    <div class="img-topbar-title">Image Studio</div>
    <div class="img-topbar-meta">
        <strong>{tokens_fmt}</strong> Tokens · diese Generierung <strong>{cost}</strong> Tokens
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.4, 0.75], gap="medium")

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
                height=110,
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
                '<div class="img-size-section-title">Bildgröße</div>'
                '<div class="img-size-section-sub">Format und Auflösung — ein Klick zum Auswählen.</div>',
                unsafe_allow_html=True,
            )
            _render_size_preset_grid()
            preset = _preset_from_session()

            with st.container():
                st.markdown('<div class="img-quality-row">', unsafe_allow_html=True)
                quality = st.radio(
                    "Qualität",
                    options=["standard", "hd"],
                    format_func=_quality_label,
                    horizontal=True,
                    key="image_quality",
                )
                st.markdown("</div>", unsafe_allow_html=True)

            cost = get_image_cost(quality=quality, size=preset["size"])

            st.markdown(
                f'<div class="img-preset-summary">Ausgewählt: <strong>'
                f'{html.escape(preset["format_name"])} · {html.escape(preset["tier"])}</strong> · '
                f'{html.escape(preset["pixels"])} ({html.escape(preset["aspect"])})</div>',
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
