"""
AI Reels Studio — Premium Creator UI (TikTok, Instagram Reels, YouTube Shorts).
Backend: video_engine, reel_queue, social_oauth (unverändert).
"""
from __future__ import annotations

import html
import uuid
from datetime import datetime, time
from pathlib import Path

import streamlit as st

from database import get_user, save_usage, spend_tokens
from db.reel_jobs import update_reel_job
from db.video_engine import init_video_engine_tables, list_video_jobs
from pricing import GEN_AI, get_reel_video_cost
from services.reel_queue import enqueue_reel, process_reel_queue
from services.social_oauth import SOCIAL_PLATFORMS, connect_auth_url, platform_configured, social_oauth_ready
from services.social_publish import SocialPublishService
from services.video_automation import create_automation_rule
from services.video_engine import can_use_automation, engine_status, get_job_bundle
from services.video_providers import ai_provider_available
from ui.styles import inject_css, page_layout_css

STEPS = ("Idee", "Video erzeugen", "Preview", "Planen", "Posten")

PLATFORMS = (
    ("tiktok", "TikTok", "Vertikal, schnell, Hook in Sekunde 1"),
    ("instagram_reels", "Instagram Reels", "Polished Look, hohe Reichweite"),
    ("youtube_shorts", "YouTube Shorts", "Shorts-Feed, Discovery"),
)

DURATIONS = ((3, "3s", "Ultra-kurz"), (5, "5s", "Standard"), (7, "7s", "Max Impact"))

STYLES = (
    ("viral", "Viral", "Schnelle Hooks, hohe Energie"),
    ("football", "Football Hype", "Stadion, Derby, Emotion"),
    ("cinematic", "Cinematic", "Filmisch, dramatisches Licht"),
    ("news", "News", "Klar, sachlich, Headline-Fokus"),
)

STYLE_PROMPT = {
    "viral": "Viral short-form style, punchy hook, high energy, scroll-stopping.",
    "football": "Football hype, stadium atmosphere, dramatic sports moment.",
    "cinematic": "Cinematic lighting, shallow depth of field, premium film look.",
    "news": "News style, clear subject, professional, informative tone.",
}

REELS_CSS = """
section.main .block-container {
    padding-top: 8px !important;
    max-width: 960px !important;
    padding-bottom: 48px !important;
}
.rs-hero {
    text-align: center;
    padding: 6px 0 14px 0;
}
.rs-hero-title {
    font-size: 44px;
    line-height: 1.05;
    font-weight: 1000;
    letter-spacing: -1.6px;
    margin: 10px 0 8px 0;
    background: linear-gradient(135deg, rgba(255,231,163,.95), rgba(192,132,252,.96), rgba(96,165,250,.95));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.rs-hero-sub {
    color: rgba(148,163,184,.92) !important;
    font-size: 13px;
    margin: 0;
}
.rs-top-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 14px 0 14px 0;
}
.rs-stat {
    border-radius: 18px;
    padding: 14px 16px;
    background:
        radial-gradient(circle at 20% 0%, rgba(168,85,247,.14), transparent 40%),
        linear-gradient(180deg, rgba(12,18,38,.76), rgba(8,10,22,.90));
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 0 30px rgba(124,58,237,.08);
}
.rs-stat-k { color: rgba(148,163,184,.9) !important; font-size: 10px; font-weight: 900; letter-spacing: .18em; text-transform: uppercase; }
.rs-stat-v { margin-top: 8px; color: #ffffff !important; font-weight: 1000; font-size: 18px; }
.rs-stat-s { margin-top: 4px; color: rgba(148,163,184,.9) !important; font-size: 11px; }
.rs-workflow {
    margin-top: 8px;
    padding: 12px 12px;
    border-radius: 18px;
    background: rgba(8,10,20,.45);
    border: 1px solid rgba(255,255,255,.07);
    backdrop-filter: blur(14px);
}
.rs-workflow-label {
    color: rgba(148,163,184,.9) !important;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin: 2px 0 10px 2px;
}
.rs-stepper {
    display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 20px 0;
    padding: 10px; border-radius: 16px;
    background: rgba(15,10,28,.85); border: 1px solid rgba(255,255,255,.06);
}
.rs-step {
    flex: 1; min-width: 72px; text-align: center; padding: 10px 8px;
    border-radius: 12px; font-size: 11px; font-weight: 800; color: #64748b !important;
    border: 1px solid transparent;
}
.rs-step.active {
    color: #fff !important;
    background: linear-gradient(135deg, rgba(124,58,237,.5), rgba(59,130,246,.25));
    border-color: rgba(168,85,247,.45);
    box-shadow: 0 0 24px rgba(124,58,237,.25);
}
.rs-step.done { color: #a78bfa !important; }
.rs-section-title {
    color: #c4b5fd !important; font-size: 11px; font-weight: 800;
    letter-spacing: .16em; text-transform: uppercase; margin: 18px 0 10px 2px;
}
.rs-card-btn button {
    position: relative;
    min-height: 86px !important;
    padding: 14px 14px 12px 14px !important;
    border-radius: 18px !important;
    text-align: left !important;
    background:
        radial-gradient(circle at 30% 10%, rgba(168,85,247,.12), transparent 38%),
        linear-gradient(180deg, rgba(12,18,38,.74), rgba(8,10,22,.90)) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.04) !important;
    transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
.rs-card-btn button * {
    /* Hide Streamlit's default button label to avoid duplicated text */
    opacity: 0 !important;
}
.rs-card-btn button {
    overflow: hidden !important;
}
.rs-card-btn button:focus {
    outline: none !important;
}
.rs-card-btn button:hover {
    transform: translateY(-1px);
    border-color: rgba(168,85,247,.22) !important;
    box-shadow: 0 0 0 1px rgba(168,85,247,.12), 0 0 24px rgba(124,58,237,.12) !important;
}
.rs-card-btn-selected button {
    border-color: rgba(168,85,247,.55) !important;
    box-shadow: 0 0 0 1px rgba(168,85,247,.18), 0 0 30px rgba(124,58,237,.20) !important;
    background:
        radial-gradient(circle at 30% 10%, rgba(168,85,247,.20), transparent 40%),
        linear-gradient(180deg, rgba(18,10,32,.92), rgba(8,10,22,.92)) !important;
}
.rs-card-h1 { color: #ffffff !important; font-weight: 1000; font-size: 14px; line-height: 1.15; }
.rs-card-h2 { color: rgba(148,163,184,.92) !important; font-size: 11px; margin-top: 4px; line-height: 1.3; }
.rs-card-icon {
    width: 28px; height: 28px; border-radius: 12px;
    display: inline-flex; align-items: center; justify-content: center;
    margin-bottom: 8px;
    background: linear-gradient(135deg, rgba(124,58,237,.7), rgba(59,130,246,.35));
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 10px 24px rgba(0,0,0,.22), 0 0 18px rgba(124,58,237,.16);
    color: #ffffff !important;
    font-weight: 1000;
    font-size: 12px;
}
.rs-cost-box {
    padding: 14px 18px; border-radius: 14px; margin: 12px 0 16px 0;
    background: rgba(124,58,237,.12); border: 1px solid rgba(168,85,247,.25);
}
.rs-cost-box strong { color: #e9d5ff !important; }
.rs-empty {
    text-align: center; padding: 36px 20px; border-radius: 18px;
    background: rgba(255,255,255,.03); border: 1px dashed rgba(148,163,184,.25);
}
.rs-empty-title { color: #fff !important; font-size: 17px; font-weight: 800; }
.rs-empty-sub { color: #94a3b8 !important; font-size: 13px; margin-top: 8px; }
.rs-job-card {
    padding: 16px 18px; border-radius: 16px; margin-bottom: 10px;
    background: linear-gradient(135deg, rgba(22,14,38,.95), rgba(12,8,22,.98));
    border: 1px solid rgba(255,255,255,.07);
}
.rs-badge {
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .06em;
}
.rs-badge.rendering { background: rgba(59,130,246,.2); color: #93c5fd !important; }
.rs-badge.ready, .rs-badge.ready_to_publish { background: rgba(34,197,94,.18); color: #86efac !important; }
.rs-badge.failed { background: rgba(239,68,68,.18); color: #fca5a5 !important; }
.rs-badge.queued { background: rgba(251,191,36,.15); color: #fcd34d !important; }
.rs-badge.scheduled { background: rgba(168,85,247,.18); color: #e9d5ff !important; }
.rs-badge.posted { background: rgba(34,211,238,.15); color: #67e8f9 !important; }
.rs-account-card {
    padding: 16px; border-radius: 16px; margin-bottom: 10px;
    background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
}
.st-key-rs_prompt [data-testid="stTextArea"] > label { display: none !important; }
.st-key-rs_prompt [data-testid="stTextArea"] > div,
.st-key-rs_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"] {
    background: linear-gradient(145deg, rgba(49,16,78,.98), rgba(24,10,40,.99)) !important;
    border: 1px solid rgba(168,85,247,.4) !important;
    border-radius: 18px !important;
    box-shadow: inset 0 2px 12px rgba(0,0,0,.25), 0 0 32px rgba(124,58,237,.12) !important;
}
.st-key-rs_prompt textarea {
    background: rgba(8,10,22,.0) !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    font-size: 16px !important; line-height: 1.5 !important;
    min-height: 120px !important;
}
.st-key-rs_prompt [data-baseweb="textarea"] textarea {
    background: transparent !important;
}
.st-key-rs_prompt textarea,
.st-key-rs_prompt [data-testid="stTextArea"] textarea {
    background-color: transparent !important;
}
.st-key-rs_prompt textarea {
    /* Force dark even if parent styling changes */
    caret-color: #f8fafc !important;
}
.st-key-rs_prompt textarea::placeholder {
    color: rgba(248,250,252,.4) !important;
    -webkit-text-fill-color: rgba(248,250,252,.4) !important;
}
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input,
div[data-testid="stTextInput"] input {
    background: rgba(15,10,28,.9) !important;
    color: #f1f5f9 !important;
    border-color: rgba(168,85,247,.25) !important;
}
div[data-testid="stCheckbox"] label,
div[data-testid="stToggle"] label p { color: #e2e8f0 !important; }
@media (max-width: 640px) {
    .rs-step { min-width: 58px; font-size: 10px; padding: 8px 4px; }
    .rs-hero-title { font-size: 28px; letter-spacing: -1px; }
    .rs-top-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
"""


def inject_reels_css() -> None:
    inject_css(page_layout_css(960, 8, 32) + REELS_CSS)


_VALID_DURATIONS = frozenset({3, 5, 7})
_VALID_PLATFORMS = frozenset(p[0] for p in PLATFORMS)
_VALID_STYLES = frozenset(s[0] for s in STYLES)


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_rs_session() -> int:
    """Clamp corrupt Streamlit session values that would crash int() or job lookups."""
    step = _safe_int(st.session_state.get("rs_step"), 0)
    step = max(0, min(step, len(STEPS) - 1))
    st.session_state.rs_step = step

    dur = _safe_int(st.session_state.get("rs_duration"), 5)
    st.session_state.rs_duration = dur if dur in _VALID_DURATIONS else 5

    plat = str(st.session_state.get("rs_platform") or "tiktok")
    st.session_state.rs_platform = plat if plat in _VALID_PLATFORMS else "tiktok"

    style = str(st.session_state.get("rs_style") or "viral")
    st.session_state.rs_style = style if style in _VALID_STYLES else "viral"

    return step


def _output_file_path(job_id: str) -> str:
    bundle = get_job_bundle(job_id) or {}
    return (bundle.get("output") or {}).get("file_path") or ""


def _sync_user(username: str) -> None:
    from ui_core import sync_session_user

    user = get_user(username)
    if user:
        sync_session_user(user)


def _badge(status: str) -> str:
    s = (status or "draft").lower().replace(" ", "_")
    label = {
        "rendering": "Rendering",
        "ready": "Ready",
        "ready_to_publish": "Ready",
        "queued": "In Queue",
        "scheduled": "Scheduled",
        "posted": "Posted",
        "failed": "Failed",
    }.get(s, s)
    cls = s if s in ("rendering", "ready", "ready_to_publish", "failed", "queued", "scheduled", "posted") else "queued"
    return f'<span class="rs-badge {cls}">{html.escape(label)}</span>'


def _connection_summary(username: str) -> tuple[str, str, str]:
    """Returns (css_class, short_label, detail)."""
    try:
        states = SocialPublishService(username).connection_states()
        connected = [s for s in states if s.get("connected")]
        if connected:
            names = ", ".join(s["label"].replace(" Reels", "").replace(" Shorts", "") for s in connected[:3])
            return "ok", f"{len(connected)} verbunden", names
        pending = [s for s in states if s.get("status") == "api_pending"]
        if pending and not any(s.get("status") == "not_configured" for s in states):
            return "warn", "Manuell posten", "Auto-Post nach API-Freigabe"
        return "warn", "Nicht verbunden", "Kanal unter Posten verbinden"
    except Exception:
        return "warn", "Status unbekannt", "Verbindung prüfen"


def _render_header(username: str, tokens: int, user: dict) -> None:
    plan = str(user.get("plan") or "free").upper()
    conn_cls, conn_short, conn_detail = _connection_summary(username)
    ai_ok = engine_status().get("ai_ready", False)
    engine_txt = "Bereit" if ai_ok else "Key fehlt"

    st.markdown(
        f"""
<div class="rs-hero">
  <div class="rs-hero-title">One system. Infinite intelligence.</div>
  <p class="rs-hero-sub">Dein All-in-One AI Studio für Content, Automation & Publishing.</p>
</div>

<div class="rs-top-grid">
  <div class="rs-stat">
    <div class="rs-stat-k">Tokens verfügbar</div>
    <div class="rs-stat-v">{tokens:,}</div>
    <div class="rs-stat-s">Guthaben / Budget</div>
  </div>
  <div class="rs-stat">
    <div class="rs-stat-k">Plan</div>
    <div class="rs-stat-v">{html.escape(plan)}</div>
    <div class="rs-stat-s">Premium Creator Studio</div>
  </div>
  <div class="rs-stat">
    <div class="rs-stat-k">KI Status</div>
    <div class="rs-stat-v">{html.escape(engine_txt)}</div>
    <div class="rs-stat-s">Alle Systeme online</div>
  </div>
  <div class="rs-stat">
    <div class="rs-stat-k">Verbindungen</div>
    <div class="rs-stat-v">{html.escape(conn_short)}</div>
    <div class="rs-stat-s">{html.escape(conn_detail)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_stepper(active: int) -> None:
    parts = []
    for i, name in enumerate(STEPS):
        cls = "rs-step"
        if i == active:
            cls += " active"
        elif i < active:
            cls += " done"
        parts.append(f'<div class="{cls}">{i + 1}. {html.escape(name)}</div>')
    st.markdown(
        f'<div class="rs-workflow"><div class="rs-workflow-label">Workflow: Reel Erstellung</div>'
        f'<div class="rs-stepper">{"".join(parts)}</div></div>',
        unsafe_allow_html=True,
    )


def _full_prompt(base: str, style_key: str) -> str:
    extra = STYLE_PROMPT.get(style_key, "")
    base = (base or "").strip()
    if extra and base:
        return f"{base}. {extra}"
    return base or extra


def _render_card_picker(
    label: str,
    options: tuple,
    session_key: str,
    *,
    value_index: int = 0,
) -> str | int:
    """options: tuple of (id, title, sub). Renders as clickable card-buttons."""
    st.markdown(f'<div class="rs-section-title">{html.escape(label)}</div>', unsafe_allow_html=True)
    if session_key not in st.session_state:
        st.session_state[session_key] = options[value_index][0]

    current = st.session_state[session_key]
    cols = st.columns(min(len(options), 4))
    for i, opt in enumerate(options):
        oid, title, sub = opt[0], opt[1], opt[2]
        is_sel = oid == current
        icon = {
            "tiktok": "TT",
            "instagram_reels": "IG",
            "youtube_shorts": "YT",
            3: "3s",
            5: "5s",
            7: "7s",
            "viral": "V",
            "football": "FB",
            "cinematic": "C",
            "news": "N",
        }.get(oid, "•")

        with cols[i % len(cols)]:
            wrapper_cls = "rs-card-btn rs-card-btn-selected" if is_sel else "rs-card-btn"
            st.markdown(f'<div class="{wrapper_cls}">', unsafe_allow_html=True)
            if st.button(
                " ",
                key=f"rs_pick_{session_key}_{oid}",
                use_container_width=True,
                type="primary" if is_sel else "secondary",
                help=sub,
            ):
                st.session_state[session_key] = oid
                st.rerun()
            st.markdown(
                f'<div style="margin-top:-80px;pointer-events:none;">'
                f'<div class="rs-card-icon">{html.escape(str(icon))}</div>'
                f'<div class="rs-card-h1">{html.escape(title)}</div>'
                f'<div class="rs-card-h2">{html.escape(sub)}</div>'
                f"</div></div>",
                unsafe_allow_html=True,
            )
    return st.session_state[session_key]


def _step_idea(username: str, tokens: int, user: dict, plan: str) -> None:
    notice = st.session_state.pop("social_oauth_notice", None)
    if notice:
        getattr(st, notice[0], st.info)(notice[1])

    c1, c2, c3 = st.columns([1.2, 1.0, 1.2])
    with c1:
        platform = _render_card_picker("Zielplattform", PLATFORMS, "rs_platform", value_index=0)
    with c2:
        duration = _render_card_picker("Länge", DURATIONS, "rs_duration", value_index=1)
    with c3:
        style = _render_card_picker("Stil", (STYLES[0], STYLES[1], STYLES[2]), "rs_style", value_index=0)

    st.markdown('<div class="rs-section-title">Deine Idee</div>', unsafe_allow_html=True)
    prompt = st.text_area(
        "Prompt",
        placeholder="z.B. Derby-Highlight, Tor in der 89. Minute, euphorische Stimmung…",
        key="rs_prompt",
        height=130,
        label_visibility="collapsed",
    )

    auto_meta = st.toggle("Titel, Caption und Hashtags automatisch generieren", value=True, key="rs_auto_meta")

    cost = get_reel_video_cost(int(duration), mode=GEN_AI)
    cost_line = "100 Tokens" if int(duration) >= 7 else "90 Tokens"
    st.markdown(
        f'<div class="rs-cost-box">Kosten: <strong>{cost_line}</strong> '
        f"({cost:,} Tokens) · echte KI-Szene · {int(duration)} Sekunden</div>",
        unsafe_allow_html=True,
    )

    a, b = st.columns([1.0, 1.2])
    with a:
        st.button("Prompt verbessern", use_container_width=True, key="rs_prompt_enhance", type="secondary")
    with b:
        if st.button(
            f"Reel erstellen  •  {cost_line}",
            type="primary",
            use_container_width=True,
            key="rs_create",
        ):
            full_prompt = _full_prompt(prompt, str(style))
            if not full_prompt.strip():
                st.warning("Beschreibe kurz deine Idee.")
                return
            if tokens < cost:
                st.error(f"Nicht genug Tokens ({tokens:,} / {cost:,}).")
                return
            if not ai_provider_available():
                st.error("KI-Video ist auf dem Server noch nicht konfiguriert.")
                return

            charge_id = f"chg_{uuid.uuid4().hex}"
            ok, msg = spend_tokens(username, cost)
            if not ok:
                st.error(msg)
                return
            save_usage(
                username=username,
                tool="reel_video",
                prompt=full_prompt[:1000],
                tokens_used=cost,
                cost_tokens=cost,
                api_provider="video_engine",
                status="charged",
            )
            _sync_user(username)

            job = enqueue_reel(
                username,
                prompt=full_prompt.strip(),
                platform=str(platform),
                duration_sec=int(duration),
                mode=GEN_AI,
                cost_tokens=cost,
                charge_id=charge_id,
                auto_metadata=auto_meta,
            )
            st.session_state.ve_active_job_id = job.get("id")
            st.session_state.rs_step = 1
            st.rerun()


def _progress_for_status(status: str) -> float:
    return {
        "queued": 0.15,
        "rendering": 0.55,
        "ready": 1.0,
        "ready_to_publish": 1.0,
        "scheduled": 1.0,
        "posted": 1.0,
        "failed": 0.0,
    }.get((status or "").lower(), 0.2)


def _step_render(username: str, user: dict, plan: str) -> None:
    jobs = list_video_jobs(username, studio_type="reel", limit=30)
    queued = [j for j in jobs if j.get("status") == "queued"]
    rendering = [j for j in jobs if j.get("status") == "rendering"]

    if queued or rendering:
        st.markdown(
            '<div class="rs-cost-box">Dein Video wird als Job verarbeitet. '
            "Starte die Queue einmal — Rendering dauert etwa 1–3 Minuten.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Rendering starten", type="primary", use_container_width=True, key="rs_run_queue"):
            with st.spinner("MaByte rendert dein Reel…"):
                try:
                    process_reel_queue(username, plan=plan, max_jobs=1)
                except Exception:
                    st.error("Rendering unterbrochen. Bitte erneut versuchen.")
            st.rerun()

    if not jobs:
        st.markdown(
            """
<div class="rs-empty">
    <div class="rs-empty-title">Erstelle dein erstes Reel</div>
    <div class="rs-empty-sub">Gehe zu Schritt 1 Idee und starte mit einem Prompt.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    for job in jobs[:12]:
        jid = job.get("id")
        if not jid:
            continue
        status = job.get("status") or "queued"
        st.markdown(
            f"""
<div class="rs-job-card">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
        {_badge(status)}
        <span style="color:#94a3b8;font-size:12px;">{html.escape(str(job.get("platform", "")))}</span>
    </div>
    <div style="color:#fff;font-weight:700;margin:10px 0 6px 0;font-size:14px;">
        {html.escape(str(job.get("prompt", ""))[:70])}
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if status in ("queued", "rendering"):
            st.progress(_progress_for_status(status))
        if job.get("error_message"):
            st.caption(f"Hinweis: {html.escape(str(job['error_message'])[:180])}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if status == "failed" and st.button("Retry", key=f"rs_retry_{jid}", use_container_width=True):
                update_reel_job(jid, status="queued", error_message="")
                st.rerun()
        with c2:
            if status in ("ready", "ready_to_publish", "posted") and st.button(
                "Preview", key=f"rs_prev_{jid}", use_container_width=True
            ):
                st.session_state.ve_active_job_id = jid
                st.session_state.rs_step = 2
                st.rerun()
        with c3:
            path = _output_file_path(jid)
            if path and Path(path).exists():
                with open(path, "rb") as f:
                    st.download_button(
                        "Download",
                        data=f.read(),
                        file_name=f"mabyte_reel_{jid[:8]}.mp4",
                        mime="video/mp4",
                        key=f"rs_dl_{jid}",
                        use_container_width=True,
                    )


def _step_preview(username: str) -> None:
    job_id = st.session_state.get("ve_active_job_id")
    if not job_id:
        jobs = [j for j in list_video_jobs(username, studio_type="reel", limit=10)
                if j.get("status") in ("ready", "ready_to_publish", "posted")]
        if jobs:
            job_id = jobs[0]["id"]

    if not job_id:
        st.markdown(
            """
<div class="rs-empty">
    <div class="rs-empty-title">Noch keine Vorschau</div>
    <div class="rs-empty-sub">Sobald ein Reel fertig ist, erscheint es hier.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    bundle = get_job_bundle(job_id)
    if not bundle:
        st.warning("Dieses Reel wurde nicht gefunden.")
        return

    st.markdown(_badge(bundle.get("status", "")), unsafe_allow_html=True)
    if bundle.get("title"):
        st.markdown(f"### {html.escape(bundle['title'])}")
    if bundle.get("caption"):
        st.caption(bundle["caption"])

    out = bundle.get("output") or {}
    path = out.get("file_path") or ""
    if path and Path(path).exists() and path.endswith(".mp4"):
        st.video(path)
        with open(path, "rb") as f:
            st.download_button(
                "MP4 herunterladen",
                data=f.read(),
                file_name=f"mabyte_reel_{job_id[:8]}.mp4",
                mime="video/mp4",
                key="rs_download_mp4",
                use_container_width=True,
            )
    else:
        st.info("Video wird noch gerendert oder die Datei ist nicht verfügbar.")

    if st.button("Weiter zu Planen", use_container_width=True, key="rs_to_schedule"):
        st.session_state.rs_step = 3
        st.rerun()


def _step_schedule(username: str, user: dict, plan: str) -> None:
    unlocked = int(user.get("automation_unlocked") or 0) == 1
    if not can_use_automation(plan, bool(unlocked)):
        st.info("Scheduling und Auto-Post sind ab Grand mit Automation Unlock verfügbar.")
        if st.button("Zu Premium", key="rs_up_grand"):
            st.session_state.page = "premium"
            st.rerun()
        return

    job_id = st.session_state.get("ve_active_job_id") or ""
    jobs = [j for j in list_video_jobs(username, studio_type="reel", limit=20)
            if j.get("status") in ("ready", "ready_to_publish")]
    if jobs:
        options = {
            j["id"]: (j.get("prompt") or j["id"])[:50]
            for j in jobs
            if j.get("id")
        }
        if not options:
            st.warning("Keine planbaren Reels gefunden.")
            return
        job_id = st.selectbox(
            "Reel für Planung",
            list(options.keys()),
            format_func=lambda x: options[x],
            index=list(options.keys()).index(job_id) if job_id in options else 0,
            key="rs_sched_job",
        )

    platform = st.session_state.get("rs_platform", "tiktok")
    c1, c2 = st.columns(2)
    with c1:
        sched_date = st.date_input("Datum", value=datetime.now().date(), key="rs_sched_date")
    with c2:
        sched_time = st.time_input("Uhrzeit", value=time(18, 0), key="rs_sched_time")

    dt = datetime.combine(sched_date, sched_time)
    sched_iso = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    auto_post = st.toggle("Automatisch posten wenn fällig", value=False, key="rs_auto_post")
    consent = st.checkbox(
        "Ich bestätige, dass MaByte dieses Video automatisch posten darf.",
        value=False,
        key="rs_publish_consent",
    )

    if st.button("Veröffentlichung planen", type="primary", use_container_width=True, key="rs_save_sched"):
        if auto_post and not consent:
            st.warning("Für Auto-Post brauchst du die Bestätigung unten.")
            return
        svc = SocialPublishService(username)
        if auto_post and not svc.is_connected(platform):
            st.warning("Verbinde zuerst einen Kanal unter Schritt Posten.")
            return
        if job_id:
            post, err = svc.schedule_post(
                job_id=job_id,
                platform=platform,
                scheduled_at=sched_iso,
                auto_post=auto_post,
                user_consent=consent,
            )
            if err:
                st.error(err)
            else:
                st.success("Geplant.")
                st.session_state.rs_step = 4
                st.rerun()
        else:
            post, err = create_automation_rule(
                username,
                plan=plan,
                automation_unlocked=bool(unlocked),
                platform=platform,
                scheduled_at=sched_iso,
                frequency="once",
                prompt_template=st.session_state.get("rs_prompt", ""),
                hashtag_set="",
                auto_caption=True,
                auto_post=auto_post,
                user_consent=consent,
            )
            if err:
                st.error(err)
            else:
                st.success("Automation gespeichert.")
                st.rerun()


def _account_status_ui(status: str) -> tuple[str, str, str]:
    return {
        "connected": ("Verbunden", "ok", "Bereit für Auto-Post"),
        "expired": ("Erneut verbinden", "warn", "Token abgelaufen"),
        "disconnected": ("Nicht verbunden", "draft", "Jetzt verbinden"),
        "api_pending": ("API Review", "warn", "Manueller Export möglich"),
        "not_configured": ("Server Setup", "warn", "Admin: API-Keys in Railway"),
    }.get(status, ("Unbekannt", "draft", ""))


def _render_publish_accounts(username: str) -> None:
    try:
        init_video_engine_tables()
        svc = SocialPublishService(username)
        states = svc.connection_states()
    except Exception as exc:
        st.markdown(
            """
<div class="rs-empty">
    <div class="rs-empty-title">Kanäle momentan nicht ladbar</div>
    <div class="rs-empty-sub">Meist fehlt die Datenbank-Initialisierung oder ein Server-Neustart hilft.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("Details für Support"):
            st.code(str(exc)[:300])
        return

    any_connected = any(s.get("connected") for s in states)
    if not any_connected:
        st.markdown(
            """
<div class="rs-empty">
    <div class="rs-empty-title">Verbinde zuerst einen Kanal</div>
    <div class="rs-empty-sub">Damit aktivierst du Auto-Posting und direktes Veröffentlichen.</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    if not social_oauth_ready():
        st.caption("Hinweis: OAUTH_STATE_SECRET muss in Railway gesetzt sein.")

    for st_info in states:
        pid = st_info["id"]
        label = SOCIAL_PLATFORMS.get(pid, {}).get("label", pid)
        status = st_info["status"]
        title, _, hint = _account_status_ui(status)

        st.markdown(
            f"""
<div class="rs-account-card">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong style="color:#fff;font-size:15px;">{html.escape(label)}</strong>
        <span style="color:#a78bfa;font-size:12px;font-weight:700;">{html.escape(title)}</span>
    </div>
    <div style="color:#94a3b8;font-size:12px;margin-top:6px;">{html.escape(hint)}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st_info.get("account_label") and status == "connected":
            st.caption(f"Kanal: {st_info['account_label']}")

        c1, c2 = st.columns(2)
        with c1:
            url = connect_auth_url(username, pid)
            if status in ("connected", "expired") and url:
                st.link_button("Erneut verbinden", url, use_container_width=True, key=f"rs_oauth_re_{pid}")
            elif platform_configured(pid) and url:
                st.link_button("Verbinden", url, use_container_width=True, key=f"rs_oauth_{pid}")
            else:
                st.button("Verbinden", disabled=True, use_container_width=True, key=f"rs_oauth_dis_{pid}")
        with c2:
            if status == "connected":
                if st.button("Trennen", key=f"rs_disc_{pid}", use_container_width=True):
                    svc.disconnect(pid)
                    st.success("Getrennt.")
                    st.rerun()


def _step_publish(username: str, user: dict) -> None:
    _render_publish_accounts(username)

    st.markdown('<div class="rs-section-title">Jetzt posten</div>', unsafe_allow_html=True)
    job_id = st.session_state.get("ve_active_job_id")
    jobs = [j for j in list_video_jobs(username, studio_type="reel", limit=20)
            if j.get("status") in ("ready", "ready_to_publish")]
    if not job_id and jobs:
        job_id = jobs[0]["id"]

    if not job_id:
        st.markdown(
            """
<div class="rs-empty">
    <div class="rs-empty-title">Kein fertiges Reel</div>
    <div class="rs-empty-sub">Erstelle und rendere zuerst ein Video.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    consent = st.checkbox(
        "Ich bestätige, dass MaByte dieses Video automatisch posten darf.",
        value=False,
        key="rs_post_consent_final",
    )
    if st.button("Jetzt veröffentlichen", type="primary", use_container_width=True, key="rs_post_now"):
        if not consent:
            st.warning("Bitte die Bestätigung aktivieren.")
            return
        svc = SocialPublishService(username)
        with st.spinner("Wird hochgeladen…"):
            ok, msg = svc.publish_job(job_id, user_consent=True)
        if ok:
            st.success(msg)
        else:
            st.error(msg)


def render_reels_studio_premium(
    *,
    username: str,
    tokens: int,
    user: dict,
) -> None:
    """Premium Reels Studio entry."""
    inject_reels_css()
    try:
        init_video_engine_tables()
    except Exception:
        pass

    plan = str(user.get("plan") or "free")
    step = _normalize_rs_session()

    _render_header(username, tokens, user)
    _render_stepper(step)

    if step == 0:
        _step_idea(username, tokens, user, plan)
    elif step == 1:
        _step_render(username, user, plan)
    elif step == 2:
        _step_preview(username)
    elif step == 3:
        _step_schedule(username, user, plan)
    else:
        _step_publish(username, user)
