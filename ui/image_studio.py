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
.img-studio {
    margin-bottom: 24px;
}
.img-hero {
    border-radius: 28px;
    padding: 28px 32px 26px 32px;
    margin-bottom: 20px;
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
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -.8px;
    margin-top: 8px;
    line-height: 1.1;
}
.img-sub {
    color: #94a3b8 !important;
    font-size: 15px;
    line-height: 1.55;
    max-width: 720px;
    margin-top: 10px;
}
.img-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 18px;
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
.img-size-hint {
    color: #64748b !important;
    font-size: 12px;
    margin: 8px 0 12px 0;
    line-height: 1.45;
}
.img-preset-summary {
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 8px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.1);
}
.img-preset-summary strong {
    color: #ffffff !important;
}
.img-preset-summary span {
    color: #94a3b8 !important;
    font-size: 13px;
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

# Ein Preset = Format + Auflösung (vereinfachte Auswahl)
IMAGE_SIZE_PRESETS: list[dict[str, str]] = [
    {
        "id": "square_1k",
        "label": "Quadrat · Standard",
        "hint": "Instagram, Avatar, Icons",
        "pixels": "1024 × 1024",
        "aspect": "1:1",
        "size": "1024",
    },
    {
        "id": "square_2k",
        "label": "Quadrat · Groß",
        "hint": "Scharfe Posts & Print",
        "pixels": "2048 × 2048",
        "aspect": "1:1",
        "size": "2048",
    },
    {
        "id": "story_1k",
        "label": "Story · Standard",
        "hint": "TikTok, Reels, Stories",
        "pixels": "1024 × 1820",
        "aspect": "9:16",
        "size": "1024",
    },
    {
        "id": "story_2k",
        "label": "Story · Groß",
        "hint": "Full-HD Stories",
        "pixels": "2048 × 3640",
        "aspect": "9:16",
        "size": "2048",
    },
    {
        "id": "wide_1k",
        "label": "Breit · Standard",
        "hint": "YouTube, Banner, Header",
        "pixels": "1024 × 576",
        "aspect": "16:9",
        "size": "1024",
    },
    {
        "id": "wide_2k",
        "label": "Breit · Groß",
        "hint": "Hero & Web-Banner",
        "pixels": "2048 × 1152",
        "aspect": "16:9",
        "size": "2048",
    },
    {
        "id": "portrait_1k",
        "label": "Hoch · Standard",
        "hint": "Pinterest, Feed, Ads",
        "pixels": "1024 × 1280",
        "aspect": "4:5",
        "size": "1024",
    },
    {
        "id": "portrait_2k",
        "label": "Hoch · Groß",
        "hint": "Große Feed-Visuals",
        "pixels": "2048 × 2560",
        "aspect": "4:5",
        "size": "2048",
    },
    {
        "id": "compact",
        "label": "Kompakt",
        "hint": "Schnelle Previews",
        "pixels": "512 × 512",
        "aspect": "1:1",
        "size": "512",
    },
    {
        "id": "balanced",
        "label": "Mittel",
        "hint": "Balance Qualität/Speed",
        "pixels": "1536 × 1536",
        "aspect": "1:1",
        "size": "1536",
    },
]

_PRESET_BY_ID = {p["id"]: p for p in IMAGE_SIZE_PRESETS}


def _preset_from_session() -> dict[str, str]:
    pid = st.session_state.get("image_preset_id", "square_1k")
    return _PRESET_BY_ID.get(pid) or IMAGE_SIZE_PRESETS[0]


def _format_preset_option(idx: int) -> str:
    p = IMAGE_SIZE_PRESETS[idx]
    return f"{p['label']}  ·  {p['pixels']}"


def _quality_label(q: str) -> str:
    return "HD" if q == "hd" else "Standard"


def inject_image_studio_css() -> None:
    inject_css(page_layout_css(1200, 24, 80) + IMAGE_STUDIO_CSS)


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
        Thumbnails, Covers und Visuals in Minuten — strukturierte Prompts,
        klare Export-Specs, bereit für deine Pipeline.
    </div>
    <div class="img-chip-row">
        <span class="img-chip">Thumbnails</span>
        <span class="img-chip">Cover Art</span>
        <span class="img-chip">Social</span>
        <span class="img-chip">Product</span>
        <span class="img-chip">SaaS UI</span>
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
            '<div class="img-card-title">Creative Brief</div>'
            '<div class="img-card-desc">Beschreibe dein Bild — MaByte liefert Prompt, Palette und Export.</div>',
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

            st.markdown("**Bildgröße**")
            st.markdown(
                '<div class="img-size-hint">Ein Klick — Format und Auflösung sind schon kombiniert.</div>',
                unsafe_allow_html=True,
            )
            preset_ids = [p["id"] for p in IMAGE_SIZE_PRESETS]
            default_idx = preset_ids.index(
                st.session_state.get("image_preset_id", "square_1k")
            ) if st.session_state.get("image_preset_id") in preset_ids else 0

            picked_idx = st.radio(
                "Preset",
                options=list(range(len(IMAGE_SIZE_PRESETS))),
                index=default_idx,
                format_func=_format_preset_option,
                key="image_preset_radio",
                label_visibility="collapsed",
            )
            preset = IMAGE_SIZE_PRESETS[picked_idx]
            st.session_state["image_preset_id"] = preset["id"]

            q1, q2 = st.columns(2)
            with q1:
                quality = st.radio(
                    "Qualität",
                    options=["standard", "hd"],
                    format_func=_quality_label,
                    horizontal=True,
                    key="image_quality",
                )
            with q2:
                cost = get_image_cost(quality=quality, size=preset["size"])
                st.metric("Kosten", f"{cost} Tokens")

            st.markdown(
                f"""
<div class="img-preset-summary">
    <strong>{html.escape(preset["label"])}</strong><br>
    <span>{html.escape(preset["pixels"])} · {html.escape(preset["aspect"])} · {html.escape(preset["hint"])}</span>
</div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="mb-btn-gold">', unsafe_allow_html=True)
        if st.button(
            "Image-Paket generieren",
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
    <div class="img-side-title">Was du erhältst</div>
    <ul class="img-checklist">
        <li>Optimierter EN-Prompt (copy-paste)</li>
        <li>Negative Prompt & Komposition</li>
        <li>Farbpalette & Export-Spec</li>
        <li>3 Varianten-Ideen</li>
    </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="img-side-panel">
    <div class="img-side-title">SaaS Best Practices</div>
    <ul class="img-checklist">
        <li>Text-Safe-Zone für Thumbnails lassen</li>
        <li>Hoher Kontrast für Mobile-Feeds</li>
        <li>Markenfarben im Prompt nennen</li>
        <li>„Groß“ oder Mittel für Hero & Print</li>
    </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
<div class="img-empty">
    <div class="img-empty-title">Noch kein Export</div>
    <div class="img-empty-sub">
        Nach der Generierung erscheint dein Paket hier unten —
        inkl. Download als Markdown.
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )
        plan = html.escape(str(st.session_state.get("plan", "free")))
        st.caption(f"Aktueller Plan: **{plan}** · Image Studio inkl. Token-Abrechnung")

    st.markdown("</div>", unsafe_allow_html=True)
