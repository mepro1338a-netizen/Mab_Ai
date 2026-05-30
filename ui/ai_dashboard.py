"""MaByte AI Dashboard — Mission Control (Home)."""
from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone

import streamlit as st

from config import DAILY_LIMITS, PLANS
from database import (
    failed_jobs_count,
    list_usage,
    recent_activity,
    successful_jobs_count,
    total_tokens_used,
    usage_summary,
    workspace_activity_score,
)
from ui.dashboard_ui import format_num, nav
from ui.styles import inject_css, page_layout_css

TOPBAR_OFFSET = 92

TOOL_LABELS = {
    "chat": "AI Chat",
    "coding": "Code Studio",
    "image": "Image Studio",
    "reels": "Shorts & Reels",
    "video": "Video Engine",
    "music": "Music Studio",
    "football": "Football AI",
    "football_report": "Football Reports",
    "automation": "Automations",
    "automation_job": "Automation Jobs",
    "projects": "Projects",
    "creator": "Creator Studio",
}

AI_MODULES = (
    ("AI Chat", "chat", "chat", "Assistent & Memory"),
    ("Football AI", "football", "football", "Live Center & Analyse"),
    ("Image", "image", "image", "Generative Studio"),
    ("Shorts & Video", "reels", "creator", "Creator Engine"),
    ("Code", "coding", "coding", "Developer OS"),
    ("Music", "music", "music", "Audio Workflows"),
    ("Automations", "automation", "automation_lab", "Agent Chains"),
    ("Projects", "projects", "projects", "Workspace Hub"),
)

QUICK_PROMPTS = (
    ("Content-Idee für Reels", "Gib mir 5 virale Reel-Ideen für meine Nische mit Hook und CTA."),
    ("Code Review", "Reviewe meinen Code: Struktur, Bugs, Performance — kurz und konkret."),
    ("Match-Analyse", "Erkläre taktisch das nächste Top-Spiel: Form, Risiken, Key Players."),
    ("Business Brief", "Erstelle ein Executive Briefing zu meinem aktuellen Projekt in 5 Bulletpoints."),
)

AI_DASH_CSS = f"""
.stApp:has(.mb-ai-dash) section.main .block-container {{
    max-width: 1180px !important;
    padding-top: {TOPBAR_OFFSET}px !important;
    padding-bottom: 52px !important;
}}
.stApp:has(.mb-ai-dash) section.main [data-testid="stVerticalBlock"] {{
    gap: 14px !important;
}}
.stApp:has(.mb-ai-dash) section.main div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: #121218 !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 16px !important;
    box-shadow: 0 12px 40px rgba(0,0,0,.22) !important;
}}

.mb-ai-hero {{
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 4px;
    background:
        radial-gradient(ellipse 80% 60% at 100% 0%, rgba(139,92,246,.22), transparent 55%),
        radial-gradient(ellipse 50% 40% at 0% 100%, rgba(59,130,246,.12), transparent 50%),
        linear-gradient(145deg, #12121a 0%, #0d0d12 100%);
    border: 1px solid rgba(139,92,246,.2);
}}
.mb-ai-kicker {{
    color: #a78bfa !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
}}
.mb-ai-title {{
    color: #fafafa !important;
    font-size: clamp(24px, 3.2vw, 32px);
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 6px 0 0 0;
    line-height: 1.15;
}}
.mb-ai-sub {{
    color: #94a3b8 !important;
    font-size: 13px;
    margin: 8px 0 0 0;
    max-width: 720px;
    line-height: 1.5;
}}
.mb-ai-status-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}}
.mb-ai-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(0,0,0,.25);
    color: #d4d4d8 !important;
}}
.mb-ai-pill.on {{
    border-color: rgba(34,197,94,.35);
    background: rgba(34,197,94,.1);
    color: #86efac !important;
}}
.mb-ai-pill-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px rgba(34,197,94,.6);
}}

.mb-ai-metrics {{
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
    margin: 4px 0 6px 0;
}}
@media (max-width: 1000px) {{
    .mb-ai-metrics {{ grid-template-columns: repeat(2, 1fr); }}
}}
.mb-ai-metric {{
    border-radius: 12px;
    padding: 14px 16px;
    background: #18181f;
    border: 1px solid #2a2a32;
}}
.mb-ai-metric .lbl {{
    color: #71717a !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
}}
.mb-ai-metric .val {{
    color: #fafafa !important;
    font-size: 22px;
    font-weight: 800;
    margin-top: 4px;
    letter-spacing: -0.02em;
}}
.mb-ai-metric .hint {{
    color: #52525b !important;
    font-size: 10px;
    margin-top: 2px;
}}

.mb-ai-section {{
    color: #c4b5fd !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 0 0 10px 0;
}}

.mb-ai-modules {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
}}
@media (max-width: 900px) {{
    .mb-ai-modules {{ grid-template-columns: repeat(2, 1fr); }}
}}
.mb-ai-mod {{
    border-radius: 12px;
    padding: 12px 14px;
    border: 1px solid rgba(255,255,255,.06);
    background: rgba(8,8,14,.5);
    transition: border-color .15s ease;
}}
.mb-ai-mod.on {{
    border-color: rgba(139,92,246,.28);
    background: rgba(139,92,246,.06);
}}
.mb-ai-mod.off {{
    opacity: .72;
}}
.mb-ai-mod .name {{
    color: #f4f4f5 !important;
    font-size: 13px;
    font-weight: 700;
}}
.mb-ai-mod .desc {{
    color: #71717a !important;
    font-size: 10px;
    margin-top: 3px;
    line-height: 1.35;
}}
.mb-ai-mod .st {{
    font-size: 10px;
    font-weight: 800;
    margin-top: 8px;
    letter-spacing: .04em;
}}
.mb-ai-mod.on .st {{ color: #86efac !important; }}
.mb-ai-mod.off .st {{ color: #64748b !important; }}

.mb-ai-usage-bars {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}
.mb-ai-bar-row {{
    display: grid;
    grid-template-columns: 110px 1fr 52px;
    gap: 10px;
    align-items: center;
    font-size: 12px;
    color: #cbd5e1 !important;
}}
.mb-ai-bar-track {{
    height: 8px;
    border-radius: 999px;
    background: rgba(255,255,255,.06);
    overflow: hidden;
}}
.mb-ai-bar-fill {{
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #7c3aed, #6366f1);
    min-width: 4px;
}}
.mb-ai-bar-val {{
    text-align: right;
    color: #a1a1aa !important;
    font-weight: 700;
    font-size: 11px;
}}

.mb-ai-feed {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 320px;
    overflow-y: auto;
}}
.mb-ai-feed-item {{
    border-radius: 10px;
    padding: 10px 12px;
    background: rgba(8,8,14,.45);
    border: 1px solid rgba(255,255,255,.05);
}}
.mb-ai-feed-item .top {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
    align-items: flex-start;
}}
.mb-ai-feed-item .tool {{
    color: #f4f4f5 !important;
    font-size: 13px;
    font-weight: 700;
}}
.mb-ai-feed-item .meta {{
    color: #64748b !important;
    font-size: 10px;
    white-space: nowrap;
}}
.mb-ai-feed-item .prompt {{
    color: #94a3b8 !important;
    font-size: 11px;
    margin-top: 4px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.mb-ai-feed-item .ok {{ color: #86efac !important; }}
.mb-ai-feed-item .fail {{ color: #f87171 !important; }}

.mb-ai-prompt-chip {{
    border-radius: 10px;
    padding: 10px 12px;
    background: rgba(139,92,246,.08);
    border: 1px solid rgba(139,92,246,.2);
    color: #e9d5ff !important;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.35;
    margin-bottom: 6px;
}}
.mb-ai-empty {{
    color: #64748b !important;
    font-size: 13px;
    line-height: 1.45;
}}

.stApp:has(.mb-ai-dash) section.main .st-key-ai_go_primary button {{
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    border-color: rgba(139,92,246,.4) !important;
    color: #fff !important;
    font-weight: 700 !important;
}}
.stApp:has(.mb-ai-dash) section.main div[class*="st-key-ai_go_"] button,
.stApp:has(.mb-ai-dash) section.main div[class*="st-key-ai_mod_"] button,
.stApp:has(.mb-ai-dash) section.main div[class*="st-key-ai_prompt_"] button {{
    min-height: 40px !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}}
.stApp:has(.mb-ai-dash) section.main div[class*="st-key-ai_prompt_"] button {{
    min-height: 56px !important;
    text-align: left !important;
    background: rgba(139,92,246,.1) !important;
    border: 1px solid rgba(139,92,246,.22) !important;
    color: #e9d5ff !important;
}}
"""


def inject_ai_dashboard_css() -> None:
    inject_css(page_layout_css(1180, TOPBAR_OFFSET, 52) + AI_DASH_CSS)


def _allowed(features: list, feature: str) -> bool:
    if feature == "projects":
        return True
    return "all" in features or feature in features


def _tool_label(tool: str) -> str:
    key = (tool or "system").strip().lower()
    return TOOL_LABELS.get(key, key.replace("_", " ").title())


def _usage_today(username: str) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    rows = list_usage(username) or []
    out: list[dict] = []
    for row in rows:
        created = str(row.get("created_at") or "")
        if created >= cutoff:
            out.append(row)
    return out


def _success_rate(username: str) -> int:
    ok = successful_jobs_count(username)
    fail = failed_jobs_count(username)
    total = ok + fail
    if total <= 0:
        return 100
    return int(round(100 * ok / total))


def _tokens_7d(username: str) -> int:
    summary = usage_summary(username=username, days=7) or []
    return sum(int(r.get("total_tokens") or 0) for r in summary)


def _runs_7d(username: str) -> int:
    summary = usage_summary(username=username, days=7) or []
    return sum(int(r.get("runs") or 0) for r in summary)


def render_ai_hero(*, user: str, plan_label: str, tier: str) -> None:
    st.markdown(
        f"""
<div class="mb-ai-hero">
  <div class="mb-ai-kicker">AI Command Center</div>
  <div class="mb-ai-title">Willkommen, {html.escape(user)}</div>
  <p class="mb-ai-sub">
    Dein zentrales MaByte AI Dashboard — Module, Nutzung, Limits und letzte
    Intelligence-Runs auf einen Blick. Plan: <strong>{html.escape(plan_label)}</strong>
    · Tier <strong>{html.escape(tier)}</strong>.
  </p>
  <div class="mb-ai-status-row">
    <span class="mb-ai-pill on"><span class="mb-ai-pill-dot"></span> AI Stack Online</span>
    <span class="mb-ai-pill on">Neural Routing Active</span>
    <span class="mb-ai-pill">Memory Sync Ready</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_metrics(
    *,
    tokens: int,
    tokens_7d: int,
    runs_7d: int,
    score: int,
    success_pct: int,
    jobs: int,
) -> None:
    cards = [
        ("Tokens", format_num(tokens), "Verfügbar"),
        ("7T Verbrauch", format_num(tokens_7d), "Token-Kosten"),
        ("AI Runs (7T)", format_num(runs_7d), "Workflows"),
        ("Erfolgsrate", f"{success_pct}%", f"{format_num(jobs)} Jobs"),
        ("AI Score", f"{score}/100", "Workspace-Aktivität"),
    ]
    inner = "".join(
        f'<div class="mb-ai-metric"><div class="lbl">{html.escape(l)}</div>'
        f'<div class="val">{html.escape(v)}</div>'
        f'<div class="hint">{html.escape(h)}</div></div>'
        for l, v, h in cards
    )
    st.markdown(f'<div class="mb-ai-metrics">{inner}</div>', unsafe_allow_html=True)


def render_ai_modules(plan: dict) -> None:
    features = plan.get("features", [])
    blocks: list[str] = []
    for label, feature, _page, desc in AI_MODULES:
        on = _allowed(features, feature)
        cls = "on" if on else "off"
        st_txt = "Bereit" if on else "Upgrade"
        blocks.append(
            f'<div class="mb-ai-mod {cls}">'
            f'<div class="name">{html.escape(label)}</div>'
            f'<div class="desc">{html.escape(desc)}</div>'
            f'<div class="st">{st_txt}</div></div>'
        )
    st.markdown(
        f'<div class="mb-ai-section">AI Module</div><div class="mb-ai-modules">{"".join(blocks)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mb-ai-section" style="margin-top:12px">Module öffnen</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (label, feature, page, _desc) in enumerate(AI_MODULES):
        ok = _allowed(features, feature)
        with cols[i % 4]:
            btn = f"{label}" if ok else f"{label} · Lock"
            if st.button(btn, key=f"ai_mod_{page}", width="stretch", disabled=not ok):
                if page == "creator":
                    st.session_state.creator_format = "Shorts"
                nav(page)


def render_usage_analytics(username: str) -> None:
    summary = usage_summary(username=username, days=7) or []
    st.markdown('<div class="mb-ai-section">Nutzung nach Tool (7 Tage)</div>', unsafe_allow_html=True)
    if not summary:
        st.markdown(
            '<p class="mb-ai-empty">Noch keine AI-Nutzung in den letzten 7 Tagen. Starte mit AI Chat oder Shorts.</p>',
            unsafe_allow_html=True,
        )
        return
    max_runs = max(int(r.get("runs") or 0) for r in summary) or 1
    bars: list[str] = []
    for row in summary[:8]:
        tool = _tool_label(str(row.get("tool", "")))
        runs = int(row.get("runs") or 0)
        tok = int(row.get("total_tokens") or 0)
        pct = max(4, int(100 * runs / max_runs))
        bars.append(
            f'<div class="mb-ai-bar-row">'
            f'<span>{html.escape(tool)}</span>'
            f'<div class="mb-ai-bar-track"><div class="mb-ai-bar-fill" style="width:{pct}%"></div></div>'
            f'<span class="mb-ai-bar-val">{runs} · {format_num(tok)}</span></div>'
        )
    st.markdown(f'<div class="mb-ai-usage-bars">{"".join(bars)}</div>', unsafe_allow_html=True)


def render_ai_feed(username: str, *, limit: int = 10) -> None:
    items = recent_activity(username=username, limit=limit) or []
    st.markdown('<div class="mb-ai-section">Letzte AI-Aktivität</div>', unsafe_allow_html=True)
    if not items:
        st.markdown(
            '<p class="mb-ai-empty">Keine Runs protokolliert. Nutze Schnellstart oder ein AI-Modul.</p>',
            unsafe_allow_html=True,
        )
        return
    blocks: list[str] = []
    for row in items:
        tool = _tool_label(str(row.get("tool", "")))
        created = str(row.get("created_at", ""))[:16]
        status = str(row.get("status", "")).lower()
        st_cls = "ok" if status in ("success", "charged", "ok") else "fail"
        st_lbl = "OK" if st_cls == "ok" else status.upper() or "—"
        tok = int(row.get("cost_tokens") or 0)
        prompt = str(row.get("prompt") or "")[:120]
        if prompt:
            prompt_html = f'<div class="prompt">{html.escape(prompt)}</div>'
        else:
            prompt_html = ""
        blocks.append(
            f'<div class="mb-ai-feed-item">'
            f'<div class="top"><span class="tool">{html.escape(tool)}</span>'
            f'<span class="meta">{html.escape(created)} · {format_num(tok)} T</span></div>'
            f'{prompt_html}'
            f'<div class="meta {st_cls}" style="margin-top:4px">{html.escape(st_lbl)}</div></div>'
        )
    st.markdown(f'<div class="mb-ai-feed">{"".join(blocks)}</div>', unsafe_allow_html=True)


def render_quick_actions() -> None:
    st.markdown('<div class="mb-ai-section">Schnellstart</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("AI Chat", key="ai_go_primary", width="stretch", type="primary"):
            nav("chat")
    with c2:
        if st.button("Shorts", key="ai_go_creator", width="stretch"):
            st.session_state.creator_format = "Shorts"
            nav("creator")
    with c3:
        if st.button("Football", key="ai_go_fb", width="stretch"):
            nav("football")
    with c4:
        if st.button("Automations", key="ai_go_auto", width="stretch"):
            nav("automation_lab")
    with c5:
        if st.button("Premium", key="ai_go_prem", width="stretch"):
            nav("premium")


def render_prompt_launcher() -> None:
    st.markdown('<div class="mb-ai-section">AI Prompts — direkt in den Chat</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (title, prompt) in enumerate(QUICK_PROMPTS):
        with cols[i % 2]:
            if st.button(title, key=f"ai_prompt_{i}", width="stretch"):
                st.session_state.chat_pending_prompt = prompt
                nav("chat")


def render_daily_limits(plan_key: str) -> None:
    limits = DAILY_LIMITS.get(plan_key, DAILY_LIMITS["free"])
    rows = [
        ("Chat", limits.get("chat", 0)),
        ("Code", limits.get("coding", 0)),
        ("Bilder", limits.get("image", 0)),
        ("Shorts", limits.get("reels", 0)),
        ("Video", limits.get("video", 0)),
    ]
    lr = "".join(
        f'<div class="mb-ai-bar-row" style="grid-template-columns:1fr auto">'
        f'<span>{html.escape(k)}</span><span class="mb-ai-bar-val">{html.escape(str(v))}/Tag</span></div>'
        for k, v in rows
    )
    st.markdown(f'<div class="mb-ai-section">Tageslimits</div>{lr}', unsafe_allow_html=True)


def render_intelligence_panel(
    *,
    username: str,
    fb_label: str,
    latest_tool: str,
    today_runs: int,
) -> None:
    lifetime = total_tokens_used(username)
    st.markdown(
        f"""
<div class="mb-ai-section">Intelligence</div>
<div class="mb-ai-prompt-chip">
  <strong>Football Plan:</strong> {html.escape(fb_label)}<br>
  <strong>Zuletzt:</strong> {html.escape(_tool_label(latest_tool))}<br>
  <strong>Heute:</strong> {today_runs} AI-Runs
</div>
<p class="mb-ai-empty" style="margin-top:8px">
  Lifetime Token-Verbrauch: {format_num(lifetime)} ·
  Öffne Football AI für Live Center & Elite Betting Card.
</p>
        """,
        unsafe_allow_html=True,
    )


def render_ai_dashboard(
    *,
    user: str,
    plan_key: str,
    plan: dict,
    plan_label: str,
    tokens: int,
    fb_label: str,
    tier: str,
) -> None:
    """Full AI Dashboard body (caller sets .mb-ai-dash marker + CSS)."""
    from database import latest_tool_used

    username = user
    score = workspace_activity_score(username)
    jobs = successful_jobs_count(username)
    success_pct = _success_rate(username)
    tokens_7d = _tokens_7d(username)
    runs_7d = _runs_7d(username)
    today = _usage_today(username)
    latest = latest_tool_used(username)

    render_ai_hero(user=user, plan_label=plan_label, tier=tier)
    render_ai_metrics(
        tokens=tokens,
        tokens_7d=tokens_7d,
        runs_7d=runs_7d,
        score=score,
        success_pct=success_pct,
        jobs=jobs,
    )
    render_quick_actions()

    col_mod, col_intel = st.columns([1.55, 1], gap="medium")
    with col_mod:
        with st.container(border=True):
            render_ai_modules(plan)
    with col_intel:
        with st.container(border=True):
            render_intelligence_panel(
                username=username,
                fb_label=fb_label,
                latest_tool=latest,
                today_runs=len(today),
            )

    col_usage, col_feed = st.columns([1, 1.2], gap="medium")
    with col_usage:
        with st.container(border=True):
            render_usage_analytics(username)
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            render_daily_limits(plan_key)
    with col_feed:
        with st.container(border=True):
            render_ai_feed(username)

    render_prompt_launcher()

    st.markdown(
        f'<p class="mb-ai-empty" style="text-align:center;margin-top:8px">'
        f'MaByte AI OS · Score {score}/100 · {format_num(jobs)} erfolgreiche Jobs</p>',
        unsafe_allow_html=True,
    )
