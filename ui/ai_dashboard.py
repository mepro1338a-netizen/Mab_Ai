"""MaByte Home — Football Intelligence Command Center."""
from __future__ import annotations

import html

import streamlit as st

from config import DAILY_LIMITS
from database import recent_activity, usage_summary
from services.home_football_hub import load_home_football_hub
from ui.dashboard_ui import format_num, nav
from ui.styles import inject_css, page_layout_css

TOPBAR_OFFSET = 92
_ACCENT = "#8b5cf6"

_FB_CC_CSS = f"""
.stApp:has(.mb-fb-cc) section.main .block-container {{
    max-width: 1180px !important;
    padding-top: {TOPBAR_OFFSET}px !important;
    padding-bottom: 48px !important;
    overflow-x: hidden !important;
}}
.stApp:has(.mb-fb-cc) section.main [data-testid="stVerticalBlock"] {{
    gap: 12px !important;
}}
.stApp:has(.mb-fb-cc) section.main div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(24, 24, 27, 0.82) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 20px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28) !important;
    backdrop-filter: blur(14px);
}}

.mb-fb-topbar {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}}
.mb-fb-topbar .logo {{
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 17px;
    color: #fff;
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
}}
.mb-fb-topbar .name {{
    display: block;
    font-size: 18px;
    font-weight: 800;
    color: #fafafa;
}}
.mb-fb-topbar .tag {{
    display: block;
    font-size: 11px;
    color: #a1a1aa;
}}

.mb-fb-welcome {{
    border-radius: 20px;
    padding: 22px 24px;
    margin-bottom: 4px;
    background:
        radial-gradient(ellipse 70% 50% at 100% 0%, rgba(139, 92, 246, 0.22), transparent 55%),
        linear-gradient(145deg, #12121a 0%, #0d0d12 100%);
    border: 1px solid rgba(139, 92, 246, 0.25);
}}
.mb-fb-kicker {{
    color: {_ACCENT} !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}}
.mb-fb-welcome h1 {{
    color: #fafafa !important;
    font-size: clamp(22px, 3vw, 28px);
    font-weight: 800;
    margin: 8px 0 0 0;
    line-height: 1.2;
}}
.mb-fb-welcome p {{
    color: #94a3b8 !important;
    font-size: 13px;
    margin: 8px 0 0 0;
    max-width: 720px;
    line-height: 1.5;
}}
.mb-fb-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}}
.mb-fb-pill {{
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.25);
    color: #d4d4d8 !important;
}}
.mb-fb-pill.live {{
    border-color: rgba(34, 197, 94, 0.35);
    color: #86efac !important;
}}

.mb-fb-section {{
    color: #c4b5fd !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 10px 0;
}}
.mb-fb-empty {{
    color: #71717a !important;
    font-size: 13px;
    line-height: 1.45;
    margin: 0;
}}

.mb-fb-match-hero {{
    border-radius: 16px;
    padding: 16px 18px;
    background: rgba(8, 8, 14, 0.55);
    border: 1px solid rgba(139, 92, 246, 0.2);
}}
.mb-fb-match-hero .liga {{
    color: #a78bfa !important;
    font-size: 11px;
    font-weight: 700;
}}
.mb-fb-match-hero .teams {{
    color: #fafafa !important;
    font-size: 18px;
    font-weight: 800;
    margin: 8px 0 4px 0;
}}
.mb-fb-match-hero .score {{
    color: #86efac !important;
    font-size: 22px;
    font-weight: 800;
}}
.mb-fb-match-hero .meta {{
    color: #71717a !important;
    font-size: 12px;
    margin-top: 6px;
}}

.mb-fb-pick {{
    border-radius: 14px;
    padding: 14px 16px;
    background: rgba(139, 92, 246, 0.08);
    border: 1px solid rgba(139, 92, 246, 0.22);
}}
.mb-fb-pick .match {{
    color: #e9d5ff !important;
    font-size: 12px;
    font-weight: 700;
}}
.mb-fb-pick .tip {{
    color: #fafafa !important;
    font-size: 16px;
    font-weight: 800;
    margin: 6px 0;
}}
.mb-fb-pick .chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}}
.mb-fb-chip {{
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    background: rgba(0, 0, 0, 0.3);
    color: #a1a1aa !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
}}

.mb-fb-injury-list {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.mb-fb-injury-item {{
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(8, 8, 14, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.05);
}}
.mb-fb-injury-item strong {{
    display: block;
    color: #f4f4f5 !important;
    font-size: 12px;
}}
.mb-fb-injury-item span {{
    color: #94a3b8 !important;
    font-size: 11px;
}}

.mb-fb-live-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}}
@media (max-width: 700px) {{
    .mb-fb-live-grid {{ grid-template-columns: 1fr; }}
}}
.mb-fb-live-item {{
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(8, 8, 14, 0.45);
    border: 1px solid rgba(34, 197, 94, 0.15);
}}
.mb-fb-live-item .t {{
    color: #fafafa !important;
    font-size: 12px;
    font-weight: 700;
}}
.mb-fb-live-item .s {{
    color: #86efac !important;
    font-size: 14px;
    font-weight: 800;
    margin-top: 4px;
}}
.mb-fb-live-item .l {{
    color: #71717a !important;
    font-size: 10px;
    margin-top: 2px;
}}

.mb-fb-sub-box {{
    border-radius: 14px;
    padding: 14px 16px;
    background: rgba(8, 8, 14, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.06);
}}
.mb-fb-sub-row {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
    padding: 6px 0;
    font-size: 12px;
    color: #cbd5e1 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}}
.mb-fb-sub-row:last-child {{ border-bottom: none; }}
.mb-fb-sub-row .lbl {{ color: #71717a !important; }}
.mb-fb-sub-row .val {{ color: #fafafa !important; font-weight: 700; }}

.mb-fb-usage-bar {{
    display: grid;
    grid-template-columns: 88px 1fr 48px;
    gap: 8px;
    align-items: center;
    font-size: 11px;
    color: #cbd5e1 !important;
    margin-bottom: 8px;
}}
.mb-fb-bar-track {{
    height: 6px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    overflow: hidden;
}}
.mb-fb-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #8b5cf6, #6366f1);
    border-radius: 999px;
    min-width: 3px;
}}

.mb-fb-feed {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 280px;
    overflow-y: auto;
}}
.mb-fb-feed-item {{
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(8, 8, 14, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
}}
.mb-fb-feed-item .tool {{
    color: #f4f4f5 !important;
    font-size: 12px;
    font-weight: 700;
}}
.mb-fb-feed-item .meta {{
    color: #64748b !important;
    font-size: 10px;
}}

.mb-fb-brand-mini {{
    margin-top: 8px;
}}
.mb-fb-brand-mini .hero {{
    font-size: clamp(20px, 2.5vw, 26px);
    font-weight: 800;
    color: #fafafa !important;
    line-height: 1.2;
    margin: 0 0 8px 0;
}}
.mb-fb-brand-mini .hero span {{
    color: {_ACCENT} !important;
}}
.mb-fb-brand-mini .desc {{
    color: #a1a1aa !important;
    font-size: 13px;
    line-height: 1.5;
    margin: 0 0 14px 0;
}}
.mb-fb-feat-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}}
.mb-fb-feat {{
    padding: 12px;
    border-radius: 12px;
    background: rgba(39, 39, 42, 0.55);
    border: 1px solid #3f3f46;
    font-size: 12px;
    font-weight: 700;
    color: #fafafa !important;
}}

.stApp:has(.mb-fb-cc) section.main .st-key-fb_go_primary button {{
    background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
    color: #fff !important;
    font-weight: 700 !important;
    border: none !important;
}}
.stApp:has(.mb-fb-cc) section.main div[class*="st-key-fb_go_"] button {{
    min-height: 42px !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}}
"""


def inject_ai_dashboard_css() -> None:
    inject_css(page_layout_css(1180, TOPBAR_OFFSET, 48) + _FB_CC_CSS)


def _tool_label(tool: str) -> str:
    key = (tool or "system").strip().lower()
    labels = {
        "chat": "AI Chat",
        "football": "Football AI",
        "football_report": "Football Report",
        "reels": "Creator / Reels",
        "creator": "Creator Studio",
        "coding": "Code Studio",
        "image": "Image Studio",
        "automation": "Automations",
    }
    return labels.get(key, key.replace("_", " ").title())


def _hub_cache_key(username: str, fb_plan: str) -> str:
    return f"{username}|{fb_plan}|v1"


def _get_football_hub(username: str, fb_plan: str) -> dict:
    key = _hub_cache_key(username, fb_plan)
    cached = st.session_state.get("home_fb_hub")
    if isinstance(cached, dict) and cached.get("_key") == key:
        return cached

    with st.spinner("Football Intelligence wird geladen…"):
        hub = load_home_football_hub(username=username, session_plan=fb_plan)
    hub["_key"] = key
    st.session_state.home_fb_hub = hub
    return hub


def render_top_header() -> None:
    from config import APP_NAME

    initial = html.escape(APP_NAME[:1] if APP_NAME else "M")
    name = html.escape(APP_NAME)
    st.markdown(
        f"""
<div class="mb-fb-topbar">
  <span class="logo">{initial}</span>
  <div>
    <span class="name">{name}</span>
    <span class="tag">Enterprise AI Platform</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_header(*, user: str, plan_label: str, fb_label: str, hub: dict) -> None:
    payload = hub.get("payload") or {}
    live_n = len(payload.get("live_now") or [])
    top_n = len(payload.get("top_matches") or [])
    live_cls = " mb-fb-pill live" if live_n else ""
    live_pill = (
        f'<span class="mb-fb-pill{live_cls}">{live_n} Live</span>'
        if live_n
        else ""
    )
    top_pill = (
        f'<span class="mb-fb-pill">{top_n} Top-Spiele heute</span>'
        if top_n
        else ""
    )
    st.markdown(
        f"""
<div class="mb-fb-welcome">
  <div class="mb-fb-kicker">Fußball Intelligence</div>
  <h1>Willkommen zurück, {html.escape(user)}</h1>
  <p>
    Dein tägliches Briefing: Top-Spiele, KI-Tipps und Live-Signale.
  </p>
  <div class="mb-fb-pills">
    <span class="mb-fb-pill">Plan {html.escape(plan_label)}</span>
    <span class="mb-fb-pill">Football {html.escape(fb_label)}</span>
    {live_pill}
    {top_pill}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_actions() -> None:
    st.markdown('<div class="mb-fb-section">Quick Actions</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Football AI", key="fb_go_primary", type="primary", use_container_width=True):
            nav("football")
    with c2:
        if st.button("Live Center", key="fb_go_live", use_container_width=True):
            st.session_state.page = "football"
            st.session_state.fb_mc_include_all = False
            nav("football")
    with c3:
        if st.button("AI Chat", key="fb_go_chat", use_container_width=True):
            nav("chat")
    with c4:
        if st.button("Creator", key="fb_go_creator", use_container_width=True):
            st.session_state.creator_format = "Shorts"
            nav("creator")
    with c5:
        if st.button("Premium", key="fb_go_prem", use_container_width=True):
            nav("premium")


def _match_hero_html(card: dict) -> str:
    live = " · LIVE" if card.get("live") else ""
    return f"""
<div class="mb-fb-match-hero">
  <div class="liga">{html.escape(str(card.get('league') or 'Liga'))}{html.escape(live)}</div>
  <div class="teams">{html.escape(str(card.get('home')))} vs {html.escape(str(card.get('away')))}</div>
  <div class="score">{html.escape(str(card.get('score') or 'vs'))}</div>
  <div class="meta">{html.escape(str(card.get('time') or ''))} · {html.escape(str(card.get('status_label') or ''))}</div>
</div>
"""


def _intel_pick_html(intel: dict, *, title: str) -> str:
    h = intel.get("header") or {}
    rec = intel.get("recommendation") or {}
    val = intel.get("value_quote") or {}
    pick = rec.get("main_pick") or "—"
    conf = rec.get("confidence")
    conf_txt = f"{float(conf):.0f}%" if conf is not None else "—"
    val_txt = str(val.get("verdict") or val.get("label") or "—")
    return f"""
<div class="mb-fb-pick">
  <div class="mb-fb-section" style="margin-bottom:6px">{html.escape(title)}</div>
  <div class="match">{html.escape(str(h.get('home')))} vs {html.escape(str(h.get('away')))}</div>
  <div class="tip">{html.escape(str(pick))}</div>
  <div class="chips">
    <span class="mb-fb-chip">Konfidenz {html.escape(conf_txt)}</span>
    <span class="mb-fb-chip">Risiko {html.escape(str(rec.get('risk') or '—'))}</span>
    <span class="mb-fb-chip">Value {html.escape(val_txt)}</span>
  </div>
</div>
"""


def render_football_command_center(hub: dict, *, fb_plan: str) -> None:
    payload = hub.get("payload") or {}
    rank = int(hub.get("rank") or 0)

    if not payload.get("configured"):
        errs = payload.get("errors") or ["Football API nicht konfiguriert."]
        st.warning(errs[0] if errs else "Football API nicht verfügbar.")
        if st.button("Zu Football AI", key="fb_cc_open", type="primary"):
            nav("football")
        return

    if payload.get("errors"):
        for err in payload["errors"][:2]:
            st.caption(str(err))

    st.markdown('<div class="mb-fb-section">Fußball Kommandozentrale</div>', unsafe_allow_html=True)

    top_card = hub.get("top_card")
    pick_intel = hub.get("pick_intel") if rank >= 2 else None
    best_intel = hub.get("best_intel") if rank >= 2 else None
    injuries = hub.get("injuries") or []
    live_cards = hub.get("live_cards") or []

    row1: list = []
    if top_card:
        row1.append("top")
    if pick_intel:
        row1.append("pick")
    if row1:
        cols = st.columns(len(row1))
        idx = 0
        if "top" in row1:
            with cols[idx]:
                with st.container(border=True):
                    st.markdown('<div class="mb-fb-section">Top-Spiel heute</div>', unsafe_allow_html=True)
                    st.markdown(_match_hero_html(top_card), unsafe_allow_html=True)
                    fid = top_card.get("fixture_id")
                    if fid and st.button("Analyse öffnen", key="fb_top_match", use_container_width=True):
                        st.session_state.page = "football"
                        st.session_state.fb_mc_selected_fixture = int(fid)
                        nav("football")
            idx += 1
        if "pick" in row1:
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(_intel_pick_html(pick_intel, title="KI-Tipp des Tages"), unsafe_allow_html=True)

    row2: list = []
    if best_intel:
        row2.append("bet")
    if injuries:
        row2.append("inj")
    if row2:
        cols = st.columns(len(row2))
        idx = 0
        if "bet" in row2:
            with cols[idx]:
                with st.container(border=True):
                    st.markdown('<div class="mb-fb-section">Beste Wettchance</div>', unsafe_allow_html=True)
                    st.markdown(_intel_pick_html(best_intel, title=""), unsafe_allow_html=True)
            idx += 1
        if "inj" in row2:
            with cols[idx]:
                with st.container(border=True):
                    st.markdown('<div class="mb-fb-section">Verletzungsnews</div>', unsafe_allow_html=True)
                    items = "".join(
                        f'<div class="mb-fb-injury-item"><strong>{html.escape(i["match"])}</strong>'
                        f'<span>{html.escape(i.get("detail") or i["line"])}</span></div>'
                        for i in injuries
                    )
                    st.markdown(f'<div class="mb-fb-injury-list">{items}</div>', unsafe_allow_html=True)

    if live_cards:
        with st.container(border=True):
            st.markdown('<div class="mb-fb-section">Live-Spiele</div>', unsafe_allow_html=True)
            cells = []
            for c in live_cards[:6]:
                extra = ""
                if c.get("live_possession"):
                    extra = f' · {html.escape(str(c.get("live_possession")))}'
                if c.get("live_xg"):
                    extra += f' · xG {html.escape(str(c.get("live_xg")))}'
                cells.append(
                    f'<div class="mb-fb-live-item">'
                    f'<div class="t">{html.escape(str(c.get("home")))} vs {html.escape(str(c.get("away")))}</div>'
                    f'<div class="s">{html.escape(str(c.get("score")))}</div>'
                    f'<div class="l">{html.escape(str(c.get("league")))} · '
                    f'{html.escape(str(c.get("status_label")))}{extra}</div>'
                    f"</div>"
                )
            st.markdown(f'<div class="mb-fb-live-grid">{"".join(cells)}</div>', unsafe_allow_html=True)
            if st.button("Live Center öffnen", key="fb_cc_all_live", use_container_width=True):
                st.session_state.page = "football"
                nav("football")


def render_brand_column() -> None:
    st.markdown(
        """
<div class="mb-fb-brand-mini">
  <p class="hero">One System. <span>Infinite Intelligence.</span></p>
  <p class="desc">Enterprise platform for AI Content, Football Intelligence and Automation.</p>
  <div class="mb-fb-feat-grid">
    <div class="mb-fb-feat">AI Reels Studio</div>
    <div class="mb-fb-feat">Football Intelligence</div>
    <div class="mb-fb-feat">Publishing Engine</div>
    <div class="mb-fb-feat">Team Workspace</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_subscription_overview(*, plan_label: str, tokens: int, fb_label: str, tier: str, plan_key: str) -> None:
    limits = DAILY_LIMITS.get(plan_key, DAILY_LIMITS["free"])
    chat_lim = limits.get("chat", 0)
    rows = [
        ("MaByte Plan", plan_label),
        ("Tier", tier),
        ("Tokens", format_num(tokens)),
        ("Football", fb_label),
        ("Chat / Tag", str(chat_lim)),
    ]
    inner = "".join(
        f'<div class="mb-fb-sub-row"><span class="lbl">{html.escape(a)}</span>'
        f'<span class="val">{html.escape(b)}</span></div>'
        for a, b in rows
    )
    st.markdown(
        f'<div class="mb-fb-section">Abo-Übersicht</div>'
        f'<div class="mb-fb-sub-box">{inner}</div>',
        unsafe_allow_html=True,
    )
    if st.button("Plan upgraden", key="fb_sub_upgrade", use_container_width=True):
        nav("premium")


def render_usage_analytics(username: str) -> None:
    summary = usage_summary(username=username, days=7) or []
    st.markdown('<div class="mb-fb-section">Nutzung (7 Tage)</div>', unsafe_allow_html=True)
    if not summary:
        return
    max_runs = max(int(r.get("runs") or 0) for r in summary) or 1
    bars: list[str] = []
    for row in summary[:6]:
        tool = _tool_label(str(row.get("tool", "")))
        runs = int(row.get("runs") or 0)
        pct = max(4, int(100 * runs / max_runs))
        bars.append(
            f'<div class="mb-fb-usage-bar"><span>{html.escape(tool)}</span>'
            f'<div class="mb-fb-bar-track"><div class="mb-fb-bar-fill" style="width:{pct}%"></div></div>'
            f'<span>{runs}</span></div>'
        )
    st.markdown("".join(bars), unsafe_allow_html=True)


def render_activity_feed(username: str) -> None:
    items = recent_activity(username=username, limit=8) or []
    st.markdown('<div class="mb-fb-section">Aktivitäts-Feed</div>', unsafe_allow_html=True)
    if not items:
        return
    blocks = []
    for row in items:
        tool = _tool_label(str(row.get("tool", "")))
        created = str(row.get("created_at", ""))[:16]
        blocks.append(
            f'<div class="mb-fb-feed-item">'
            f'<div class="tool">{html.escape(tool)}</div>'
            f'<div class="meta">{html.escape(created)}</div></div>'
        )
    st.markdown(f'<div class="mb-fb-feed">{"".join(blocks)}</div>', unsafe_allow_html=True)


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
    """Full home dashboard (caller sets .mb-fb-cc marker + CSS)."""
    username = user
    fb_plan = str(st.session_state.get("football_plan") or "none")
    hub = _get_football_hub(username, fb_plan)

    render_top_header()
    render_welcome_header(user=user, plan_label=plan_label, fb_label=fb_label, hub=hub)
    render_quick_actions()

    brand_col, main_col, side_col = st.columns([0.95, 1.55, 1], gap="medium")

    with brand_col:
        render_brand_column()

    with main_col:
        render_football_command_center(hub, fb_plan=fb_plan)

    with side_col:
        with st.container(border=True):
            render_subscription_overview(
                plan_label=plan_label,
                tokens=tokens,
                fb_label=fb_label,
                tier=tier,
                plan_key=plan_key,
            )
        usage = usage_summary(username=username, days=7) or []
        if usage:
            with st.container(border=True):
                render_usage_analytics(username)
        activity = recent_activity(username=username, limit=8) or []
        if activity:
            with st.container(border=True):
                render_activity_feed(username)

    st.markdown(
        f'<p class="mb-fb-empty" style="text-align:center;margin-top:12px">'
        f'MaByte Football Intelligence · {html.escape(plan_label)} · '
        f'{format_num(tokens)} Tokens verfügbar</p>',
        unsafe_allow_html=True,
    )
