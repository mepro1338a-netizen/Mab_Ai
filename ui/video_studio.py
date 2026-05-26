"""
Video Studio — compact professional UI (OpenAI package + optional Replicate clip).
"""
from __future__ import annotations

import html

import streamlit as st

from pricing import get_video_studio_cost
from services.video_studio import api_status
from ui.styles import inject_css, page_layout_css

VIDEO_STUDIO_CSS = """
section.main .block-container {
    padding-top: 4px !important;
    padding-bottom: 24px !important;
    max-width: 760px !important;
}
section.main .block-container > div { gap: 0.25rem !important; }

.vs-head {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px 16px;
    margin-bottom: 12px;
}
.vs-head-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -.3px;
}
.vs-head-sub {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-top: 2px;
}
.vs-token-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}
.vs-token-pill {
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(168,85,247,.12);
    border: 1px solid rgba(168,85,247,.28);
    color: #e9d5ff !important;
    font-size: 12px;
    font-weight: 700;
}
.vs-token-pill strong { color: #ffffff !important; }
.vs-api-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0 0 12px 0;
}
.vs-api-pill {
    font-size: 11px;
    font-weight: 700;
    padding: 5px 10px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,.1);
}
.vs-api-pill.ok {
    color: #86efac !important;
    background: rgba(34,197,94,.12);
    border-color: rgba(34,197,94,.3);
}
.vs-api-pill.off {
    color: #94a3b8 !important;
    background: rgba(255,255,255,.04);
}
.vs-prompt-label {
    color: #c4b5fd !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 0 0 8px 2px;
}
.st-key-vs_topic [data-testid="stTextArea"] > label,
.st-key-vs_topic [data-testid="stTextArea"] > label p { display: none !important; }
.st-key-vs_topic [data-testid="stTextArea"] > div,
.st-key-vs_topic [data-testid="stTextArea"] div[data-baseweb="textarea"],
.st-key-vs_topic [data-testid="stTextArea"] div[data-baseweb="base-input"] {
    background:
        radial-gradient(circle at 10% 0%, rgba(216,180,254,.32), transparent 46%),
        linear-gradient(145deg, rgba(88,28,135,.98), rgba(49,16,78,.99)) !important;
    border: 1px solid rgba(192,132,252,.55) !important;
    border-radius: 20px !important;
    box-shadow: 0 0 44px rgba(168,85,247,.26), inset 0 1px 0 rgba(255,255,255,.08) !important;
    overflow: hidden !important;
}
.st-key-vs_topic textarea {
    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 16px 18px !important;
    min-height: 100px !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-vs_topic textarea::placeholder {
    color: rgba(255,255,255,.48) !important;
    -webkit-text-fill-color: rgba(255,255,255,.48) !important;
}
.vs-opts label,
.vs-opts .stSlider label,
.vs-opts .stCheckbox label,
.vs-opts .stCheckbox label p {
    color: #cbd5e1 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
.vs-opts [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #a855f7 !important;
}
.st-key-vs_platform div[data-baseweb="select"] > div,
.st-key-vs_style div[data-baseweb="select"] > div {
    background: rgba(30,20,50,.95) !important;
    border: 1px solid rgba(168,85,247,.35) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
}
.st-key-btn_video .stButton > button {
    min-height: 50px !important;
    border-radius: 16px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #7c3aed, #a855f7 55%, #c084fc) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,.14) !important;
    box-shadow: 0 0 28px rgba(168,85,247,.38) !important;
}
.st-key-btn_topup .stButton > button,
.st-key-btn_redeem .stButton > button {
    min-height: 36px !important;
    border-radius: 12px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    background: rgba(168,85,247,.12) !important;
    color: #e9d5ff !important;
    border: 1px solid rgba(168,85,247,.35) !important;
}
.vs-topup-hint {
    margin: 10px 0 14px 0;
    padding: 10px 14px;
    border-radius: 14px;
    background: rgba(168,85,247,.08);
    border: 1px solid rgba(168,85,247,.2);
    color: #94a3b8 !important;
    font-size: 12px;
    line-height: 1.45;
}
.vs-topup-hint strong { color: #e9d5ff !important; }
.vs-result {
    margin-top: 16px;
    padding: 14px 16px;
    border-radius: 18px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(168,85,247,.22);
}
.vs-result-title {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 8px;
}
.vs-result-meta {
    color: #64748b !important;
    font-size: 11px;
    margin-bottom: 10px;
}
"""


def inject_video_studio_css() -> None:
    inject_css(page_layout_css(760, 4, 24) + VIDEO_STUDIO_CSS)


def _prompt_field(placeholder: str) -> str:
    st.markdown('<div class="vs-prompt-label">Video-Konzept</div>', unsafe_allow_html=True)
    return st.text_area(
        "Konzept",
        placeholder=placeholder,
        key="vs_topic",
        height=108,
        label_visibility="collapsed",
    )


def render_video_studio(
    *,
    tokens_available: int,
    on_generate,
) -> None:
    inject_video_studio_css()
    status = api_status()
    tokens_fmt = f"{tokens_available:,}".replace(",", ".")

    st.markdown(
        f"""
<div class="vs-head">
    <div>
        <div class="vs-head-title">Video Studio</div>
        <div class="vs-head-sub">Storyboard &amp; Produktionspaket per OpenAI</div>
    </div>
    <div class="vs-token-row">
        <div class="vs-token-pill">Guthaben <strong>{tokens_fmt}</strong> Tokens</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Tokens aufladen", key="btn_topup", width="stretch"):
            st.session_state.page = "premium"
            st.rerun()
    with c2:
        if st.button("Gutschein", key="btn_redeem", width="stretch"):
            st.session_state.page = "redeem"
            st.rerun()

    st.markdown(
        """
<div class="vs-topup-hint">
    <strong>Tokens aufladen:</strong> Sidebar → <strong>Premium</strong> (Stripe-Pläne, 1€ ≈ 100 Tokens)
    oder <strong>Gutschein</strong> unter Account. Server braucht <strong>OPENAI_API_KEY</strong> in Railway.
</div>
        """,
        unsafe_allow_html=True,
    )

    openai_cls = "ok" if status["openai"] else "off"
    rep_cls = "ok" if status["replicate"] else "off"
    openai_txt = "OpenAI verbunden" if status["openai"] else "OpenAI fehlt (Railway)"
    rep_txt = "Replicate Clip bereit" if status["replicate"] else "Clip: Replicate nicht konfiguriert"
    st.markdown(
        f"""
<div class="vs-api-row">
    <span class="vs-api-pill {openai_cls}">{html.escape(openai_txt)}</span>
    <span class="vs-api-pill {rep_cls}">{html.escape(rep_txt)}</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    if not status["openai"]:
        st.warning(
            "OPENAI_API_KEY fehlt auf dem Server. Setze ihn in Railway → Variables, "
            "damit Pakete generiert werden können."
        )

    topic = _prompt_field(
        placeholder="Beschreibe dein Video — Thema, Stimmung, Zielgruppe…",
    )

    st.markdown('<div class="vs-opts">', unsafe_allow_html=True)
    seconds = st.slider("Länge (Sekunden)", 8, 45, value=15, key="vs_seconds")
    o1, o2 = st.columns(2)
    with o1:
        platform = st.selectbox(
            "Plattform",
            ["YouTube", "TikTok", "Instagram", "Website", "Ads"],
            key="vs_platform",
        )
    with o2:
        style = st.selectbox(
            "Stil",
            ["Cinematic", "Documentary", "Premium", "Corporate", "Storytelling"],
            key="vs_style",
        )
    hd = st.checkbox("HD-Paket (detaillierter)", key="vs_hd", value=False)
    if status["replicate"]:
        st.checkbox(
            "Kurz-Clip per Replicate (+Kling/Runway-Modell)",
            key="vs_clip",
            value=False,
            help="Benötigt REPLICATE_API_TOKEN und REPLICATE_VIDEO_MODEL in Railway.",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    want_clip = bool(st.session_state.get("vs_clip") and status["replicate"])
    cost = get_video_studio_cost(
        int(st.session_state.get("vs_seconds", 15)),
        quality="hd" if hd else "standard",
        include_clip=want_clip,
    )
    st.caption(f"Diese Generierung: **{cost}** Tokens · {int(st.session_state.get('vs_seconds', 15))}s")

    if st.button("Video-Paket generieren", type="primary", key="btn_video", width="stretch"):
        if not (topic or "").strip():
            st.warning("Bitte kurz dein Video-Konzept beschreiben.")
        elif not status["openai"]:
            st.error("OpenAI ist nicht konfiguriert — Paket kann nicht erstellt werden.")
        elif tokens_available < cost:
            st.error(f"Nicht genug Tokens ({tokens_available} / {cost}). Aufladen unter Premium.")
        else:
            on_generate(
                topic.strip(),
                cost,
                seconds=int(st.session_state.get("vs_seconds", 15)),
                platform=platform,
                style=style,
                quality="hd" if hd else "standard",
                generate_clip=want_clip,
            )

    _render_result_block()


def _render_result_block() -> None:
    package = st.session_state.get("video_last_package")
    if not package:
        return

    meta = st.session_state.get("video_last_meta") or {}
    topic = html.escape(str(meta.get("prompt", "")))
    clip_url = meta.get("clip_url") or ""

    st.markdown(
        f"""
<div class="vs-result">
    <div class="vs-result-title">Dein Video-Paket</div>
    <div class="vs-result-meta">{topic}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(package)

    clip_bytes = st.session_state.get("video_last_clip_bytes")
    if clip_bytes:
        st.video(clip_bytes)
        st.download_button(
            "MP4 herunterladen",
            data=clip_bytes,
            file_name="mabyte_video_clip.mp4",
            mime="video/mp4",
            key="vs_dl_mp4",
            width="stretch",
        )
    elif clip_url:
        st.markdown(f"[Clip öffnen (extern)]({clip_url})")

    if st.button("Neu starten", key="vs_clear", width="stretch"):
        for k in ("video_last_package", "video_last_meta", "video_last_clip_bytes"):
            st.session_state.pop(k, None)
        st.rerun()
