"""
Image Studio — minimal: prompt + generate + preview.
"""
from __future__ import annotations

import html
import uuid

import streamlit as st

from pricing import get_image_cost
from ui.prompt_ui import inject_ma_prompt_css, prompt_text_area
from ui.styles import inject_css, page_layout_css

# Standard-Export (keine UI-Auswahl) — API waehlt passendes Format
DEFAULT_PRESET: dict[str, str] = {
    "id": "auto",
    "size": "1024",
    "aspect": "1:1",
    "format_name": "Auto",
    "tier": "Standard",
    "pixels": "auto",
}

IMAGE_STUDIO_CSS = """
section.main .block-container {
    padding-top: 4px !important;
    padding-bottom: 20px !important;
    max-width: 720px !important;
}
section.main .block-container > div {
    gap: 0.2rem !important;
}
.img-studio { margin: 0; }
.img-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
}
.img-head-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -.3px;
}
.img-head-meta {
    color: #94a3b8 !important;
    font-size: 12px;
    font-weight: 600;
}
.img-head-meta strong { color: #ffffff !important; }
/* Lila Prompt, weisse Schrift */
.img-studio div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) [data-testid="stTextArea"] > div {
    background:
        radial-gradient(circle at 8% 0%, rgba(216,180,254,.25), transparent 42%),
        linear-gradient(135deg, rgba(88,28,135,.98), rgba(49,16,78,.99)) !important;
    border: 1px solid rgba(192,132,252,.5) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 32px rgba(168,85,247,.22), inset 0 1px 0 rgba(255,255,255,.06) !important;
}
.img-studio div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) textarea {
    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    line-height: 1.45 !important;
    caret-color: #e9d5ff !important;
}
.img-studio div[data-testid="stVerticalBlock"]:has(.mb-prompt-marker) textarea::placeholder {
    color: rgba(255,255,255,.5) !important;
    -webkit-text-fill-color: rgba(255,255,255,.5) !important;
    font-weight: 500 !important;
}
.img-studio label,
.img-studio .stCheckbox label,
.img-studio .stCheckbox label p,
.img-studio .stCheckbox span {
    color: #e2e8f0 !important;
}
.img-studio [data-testid="stAlert"] {
    padding: 10px 12px !important;
    margin: 8px 0 !important;
}
.img-result {
    margin-top: 14px;
    padding: 12px;
    border-radius: 16px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(168,85,247,.2);
}
.img-result-title {
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
}
.img-result-prompt {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-bottom: 10px;
    line-height: 1.4;
}
"""


def inject_image_studio_css() -> None:
    inject_ma_prompt_css()
    inject_css(page_layout_css(720, 4, 24) + IMAGE_STUDIO_CSS)


def render_image_studio(
    *,
    tokens_available: int,
    on_generate,
) -> None:
    inject_image_studio_css()

    preset = DEFAULT_PRESET
    quality = "hd" if st.session_state.get("image_hd") else "standard"
    cost = get_image_cost(quality=quality, size=preset["size"])
    tokens_fmt = f"{tokens_available:,}".replace(",", ".")

    st.markdown('<div class="img-studio">', unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="img-head">
    <div class="img-head-title">Image Studio</div>
    <div class="img-head-meta"><strong>{tokens_fmt}</strong> Tokens · <strong>{cost}</strong> pro Bild</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    prompt = prompt_text_area(
        placeholder="Beschreibe dein Bild…",
        key="image_prompt",
        height=88,
    )

    hd = st.checkbox("HD (mehr Details)", key="image_hd", value=False)

    if st.button("Bild generieren", type="primary", key="btn_image", width="stretch"):
        if not (prompt or "").strip():
            st.warning("Bitte kurz beschreiben, was du sehen willst.")
        elif tokens_available < cost:
            st.error(f"Nicht genug Tokens ({tokens_available} / {cost}).")
        else:
            on_generate(
                prompt.strip(),
                cost,
                preset=preset,
                quality="hd" if hd else "standard",
                style="",
                use_case="",
            )

    _render_image_result_block()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_image_result_block() -> None:
    image_bytes = st.session_state.get("image_last_bytes")
    if not image_bytes:
        return

    meta = st.session_state.get("image_last_meta") or {}
    user_prompt = html.escape(str(meta.get("prompt", "")))

    st.markdown(
        f"""
<div class="img-result">
    <div class="img-result-title">Dein Bild</div>
    <div class="img-result-prompt">{user_prompt}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.image(image_bytes, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "PNG herunterladen",
            data=image_bytes,
            file_name=f"mabyte_{uuid.uuid4().hex[:8]}.png",
            mime="image/png",
            width="stretch",
            key="img_dl_png",
        )
    with c2:
        if st.button("Neu", key="img_clear_result", width="stretch"):
            st.session_state.pop("image_last_bytes", None)
            st.session_state.pop("image_last_meta", None)
            st.rerun()
