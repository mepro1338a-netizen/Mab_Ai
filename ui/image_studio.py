"""
Image Studio — minimal: prompt + generate + preview.
"""
from __future__ import annotations

import html
import uuid

import streamlit as st

from pricing import get_image_cost
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
.stApp:has(.img-studio) section.main .block-container {
    padding-top: 92px !important;
    padding-bottom: 32px !important;
    max-width: 720px !important;
}
.stApp:has(.img-studio) section.main .block-container > div {
    gap: 0.35rem !important;
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
    color: #fafafa !important;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -.35px;
}
.img-head-meta {
    color: #a1a1aa !important;
    font-size: 12px;
    font-weight: 600;
}
.img-head-meta strong { color: #e4e4e7 !important; }
.img-prompt-label {
    color: #a1a1aa !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 0 0 8px 2px;
}
/* Lila Prompt (Streamlit 1.50: .st-key-image_prompt) */
.st-key-image_prompt [data-testid="stTextArea"] > label,
.st-key-image_prompt [data-testid="stTextArea"] > label p {
    display: none !important;
}
.st-key-image_prompt [data-testid="stTextArea"] > div,
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"],
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="base-input"] {
    background: #27272a !important;
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 14px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04) !important;
    overflow: hidden !important;
}
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within,
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="base-input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, .25) !important;
}
.st-key-image_prompt textarea {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    caret-color: #a78bfa !important;
    padding: 16px 18px !important;
    min-height: 92px !important;
}
.st-key-image_prompt textarea::placeholder {
    color: rgba(255,255,255,.48) !important;
    -webkit-text-fill-color: rgba(255,255,255,.48) !important;
    font-weight: 500 !important;
}
.st-key-image_prompt textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}
.st-key-btn_image .stButton > button {
    min-height: 48px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    background: #7c3aed !important;
    border: 1px solid #6d28d9 !important;
    color: #ffffff !important;
    box-shadow: none !important;
}
.st-key-btn_image .stButton > button:hover {
    background: #6d28d9 !important;
    border-color: #5b21b6 !important;
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
    inject_css(IMAGE_STUDIO_CSS)


def _image_prompt_field(*, placeholder: str, height: int = 100) -> str:
    """Purple prompt bar — scoped via Streamlit key class .st-key-image_prompt."""
    st.markdown('<div class="img-prompt-label">Prompt</div>', unsafe_allow_html=True)
    return st.text_area(
        "Prompt",
        placeholder=placeholder,
        key="image_prompt",
        height=height,
        label_visibility="collapsed",
    )


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

    prompt = _image_prompt_field(
        placeholder="Beschreibe dein Bild — Stil, Farben, Stimmung…",
        height=100,
    )

    hd = st.checkbox("HD (mehr Details)", key="image_hd", value=False)

    gen_clicked = st.button(
        "Bild generieren",
        type="primary",
        key="btn_image",
        width="stretch",
    )
    if gen_clicked:
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
