"""
Reel Studio UI — Dark SaaS, timeline, preview, tabs, premium gates.
"""
from __future__ import annotations

import html
from typing import Callable

import streamlit as st

from services.access_control import can_access_plan_feature, plan_rank
from services.video_render import render_status_label
from ui.styles import inject_css, page_layout_css


# User-facing tiers → MaByte plans
REEL_GATES: dict[str, dict] = {
    "script_basic": {"min_plan": "free", "label": "Script AI (Basis)"},
    "hooks": {"min_plan": "pro", "label": "Hook Generator"},
    "voiceover": {"min_plan": "pro", "label": "Voiceover"},
    "captions": {"min_plan": "pro", "label": "Auto Captions"},
    "clip_builder": {"min_plan": "grand", "label": "Clip Builder"},
    "publish": {"min_plan": "grand", "label": "Publish Center"},
    "full_pipeline": {"min_plan": "elite", "label": "Full Reel Pipeline"},
    "auto_posting": {"min_plan": "elite", "label": "Auto Posting & Automation"},
}


REEL_STUDIO_CSS = """
section.main .block-container {
    padding-top: 4px !important;
    padding-bottom: 24px !important;
    max-width: 1280px !important;
}
.reel-studio { margin-top: 0; }
.reel-topbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px 14px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(18,12,38,.96), rgba(8,6,18,.99));
    border: 1px solid rgba(168,85,247,.22);
}
.reel-topbar-title {
    color: #fff !important;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -.4px;
}
.reel-topbar-meta {
    color: #94a3b8 !important;
    font-size: 12px;
    font-weight: 600;
}
.reel-topbar-meta strong { color: #e9d5ff !important; }
.reel-workspace {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 12px;
    margin-bottom: 10px;
}
@media (max-width: 900px) {
    .reel-workspace { grid-template-columns: 1fr; }
}
.reel-timeline {
    border-radius: 14px;
    padding: 12px 14px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 8px;
}
.reel-timeline-label {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.reel-timeline-track {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 4px;
}
.reel-timeline-clip {
    flex: 0 0 auto;
    min-width: 72px;
    padding: 8px 10px;
    border-radius: 10px;
    background: linear-gradient(145deg, rgba(168,85,247,.25), rgba(59,130,246,.15));
    border: 1px solid rgba(168,85,247,.35);
    color: #f8fafc !important;
    font-size: 11px;
    font-weight: 700;
    text-align: center;
}
.reel-timeline-clip.is-active {
    border-color: rgba(255,255,255,.5);
    box-shadow: 0 0 0 1px rgba(255,255,255,.15);
}
.reel-preview {
    border-radius: 14px;
    padding: 12px;
    background: #0a0a12;
    border: 1px solid rgba(255,255,255,.1);
    aspect-ratio: 9/16;
    max-height: 420px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.reel-preview-phone {
    width: 100%;
    max-width: 220px;
    aspect-ratio: 9/16;
    border-radius: 18px;
    border: 2px solid rgba(255,255,255,.12);
    background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 55%, #020617 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 16px;
    text-align: center;
}
.reel-preview-hook {
    color: #fff !important;
    font-size: 15px;
    font-weight: 800;
    line-height: 1.25;
}
.reel-preview-sub {
    color: #94a3b8 !important;
    font-size: 11px;
    margin-top: 8px;
}
.reel-preview-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
    color: #fff !important;
    background: rgba(168,85,247,.5);
}
.reel-plan-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 800;
    color: #e9d5ff !important;
    background: rgba(168,85,247,.2);
    border: 1px solid rgba(168,85,247,.35);
}
.reel-locked {
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    background: rgba(15,10,30,.6);
    border: 1px dashed rgba(168,85,247,.35);
}
.reel-locked h4 { color: #fff !important; margin: 0 0 8px 0; }
.reel-locked p { color: #94a3b8 !important; font-size: 13px; margin: 0; }
.reel-result {
    border-radius: 12px;
    padding: 12px 14px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.1);
    margin-top: 10px;
    max-height: 360px;
    overflow-y: auto;
}
.reel-result pre, .reel-result code { color: #e2e8f0 !important; }
.reel-progress-wrap {
    margin: 10px 0;
}
.reel-asset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 8px;
    margin-top: 8px;
}
.reel-asset-card {
    border-radius: 12px;
    padding: 12px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
    color: #cbd5e1 !important;
    font-size: 12px;
    font-weight: 700;
}
.reel-studio .stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    flex-wrap: wrap !important;
}
.reel-studio .stTabs [data-baseweb="tab"] {
    background: rgba(168,85,247,.08) !important;
    border-radius: 12px !important;
    color: #e9d5ff !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
}
.reel-studio .stTabs [aria-selected="true"] {
    background: rgba(168,85,247,.28) !important;
    color: #fff !important;
}
@media (max-width: 640px) {
    .reel-topbar-title { font-size: 16px; }
    .reel-preview { max-height: 320px; }
}
"""


def inject_reel_studio_css() -> None:
    inject_css(page_layout_css(1280, 4, 28) + REEL_STUDIO_CSS)


def user_plan_key() -> str:
    return str(st.session_state.get("plan") or "free").lower()


def reel_feature_allowed(feature_key: str, user: dict | None = None) -> bool:
    gate = REEL_GATES.get(feature_key, {"min_plan": "elite"})
    min_plan = gate["min_plan"]
    if user is not None:
        return can_access_plan_feature(user, min_plan)
    return plan_rank(user_plan_key()) >= plan_rank(min_plan)


def render_plan_badge() -> None:
    plan = user_plan_key()
    label = {"free": "Starter", "pro": "Pro", "grand": "Grand", "elite": "Elite"}.get(plan, plan)
    st.markdown(
        f'<span class="reel-plan-pill">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )


def render_locked_feature(feature_key: str) -> None:
    gate = REEL_GATES.get(feature_key, {})
    label = gate.get("label", feature_key)
    min_plan = gate.get("min_plan", "pro")
    st.markdown(
        f"""
<div class="reel-locked">
    <h4>{html.escape(label)}</h4>
    <p>Ab Plan <strong>{html.escape(min_plan.upper())}</strong> — upgrade in Premium.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Zu Premium", key=f"reel_up_{feature_key}", width="stretch"):
        st.session_state.page = "premium"
        st.rerun()


def render_topbar(*, tokens: int, cost_hint: str = "") -> None:
    tokens_fmt = f"{tokens:,}".replace(",", ".")
    cost_line = f" · {html.escape(cost_hint)}" if cost_hint else ""
    st.markdown(
        f"""
<div class="reel-topbar">
    <div class="reel-topbar-title">⚽ Reel Studio</div>
    <div class="reel-topbar-meta">
        <strong>{tokens_fmt}</strong> Tokens{cost_line}
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _timeline_clips() -> list[tuple[str, str]]:
    script = st.session_state.get("reel_last_script", "")
    hook = ""
    if script:
        for line in script.splitlines():
            if "hook" in line.lower() and len(line) < 80:
                hook = line.strip("# ").strip()
                break
    if not hook:
        hook = st.session_state.get("reel_preview_hook", "Dein Hook erscheint hier")
    scenes = st.session_state.get("reel_scenes") or [
        ("Hook", "2s"),
        ("Story", "4s"),
        ("Stat", "3s"),
        ("CTA", "2s"),
    ]
    return [("Hook", hook[:28] or "…")] + [(n, d) for n, d in scenes[:4]]


def render_timeline() -> None:
    clips = _timeline_clips()
    active = int(st.session_state.get("reel_timeline_active", 0))
    items = []
    for i, (name, sub) in enumerate(clips):
        cls = "reel-timeline-clip is-active" if i == active else "reel-timeline-clip"
        items.append(
            f'<div class="{cls}">{html.escape(name)}<br><span style="opacity:.75;font-size:10px">'
            f'{html.escape(str(sub)[:20])}</span></div>'
        )
    st.markdown(
        f"""
<div class="reel-timeline">
    <div class="reel-timeline-label">Timeline</div>
    <div class="reel-timeline-track">{"".join(items)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_preview_player() -> None:
    hook = st.session_state.get("reel_preview_hook", "Viraler Fußball-Hook")
    sub = st.session_state.get("reel_preview_platform", "TikTok · 9:16")
    st.markdown(
        f"""
<div class="reel-preview">
    <span class="reel-preview-badge">PREVIEW</span>
    <div class="reel-preview-phone">
        <div class="reel-preview-hook">{html.escape(hook)}</div>
        <div class="reel-preview-sub">{html.escape(sub)}</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_workspace_header() -> None:
    col_main, col_prev = st.columns([1.5, 0.85], gap="small")
    with col_main:
        render_timeline()
    with col_prev:
        render_preview_player()


def render_ai_result(content: str, *, source: str = "", error: str = "") -> None:
    if error and source == "fallback":
        st.caption(f"Offline-Modus: {error[:120]}")
    if source == "fallback":
        st.info("Demo/Fallback-Ausgabe — OpenAI nicht erreichbar oder Key fehlt.")
    st.markdown(f'<div class="reel-result">', unsafe_allow_html=True)
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)


def render_export_progress(progress: float, label: str) -> None:
    st.markdown('<div class="reel-progress-wrap">', unsafe_allow_html=True)
    st.progress(min(1.0, max(0.0, progress)), text=label)
    st.markdown("</div>", unsafe_allow_html=True)


def render_encoder_status() -> None:
    status = render_status_label()
    st.caption(
        f"Encoder: FFmpeg {status['ffmpeg']} · MoviePy {status['moviepy']}"
    )


def render_football_templates() -> None:
    templates = [
        ("Match Recap", "Tor + Stat + Meinung"),
        ("Transfer Rumor", "Hook → Quelle → Hot Take"),
        ("Lineup Reveal", "Starting XI Spannung"),
        ("Derby Hype", "Emotional + CTA"),
        ("Meme Moment", "Funny Modus"),
    ]
    cards = "".join(
        f'<div class="reel-asset-card">{html.escape(t)}<br><span style="opacity:.7;font-weight:500">'
        f'{html.escape(d)}</span></div>'
        for t, d in templates
    )
    st.markdown(f'<div class="reel-asset-grid">{cards}</div>', unsafe_allow_html=True)


def with_loading(spinner_text: str, fn: Callable[[], None]) -> None:
    try:
        with st.spinner(spinner_text):
            fn()
    except Exception as exc:
        st.error(f"Fehler: {exc}")
