"""Minimal pro dashboard shell — Home & Account."""
from __future__ import annotations

import html

import streamlit as st

from config import DAILY_LIMITS
from database import list_usage, recent_activity
from ui.styles import inject_css, page_layout_css

TOPBAR_OFFSET = 92

DASHBOARD_CSS = f"""
.stApp:has(.mb-dash) section.main .block-container {{
    max-width: 1080px !important;
    padding-top: {TOPBAR_OFFSET}px !important;
    padding-bottom: 48px !important;
}}
.stApp:has(.mb-dash) section.main [data-testid="stVerticalBlock"] {{
    gap: 12px !important;
}}
.stApp:has(.mb-dash) section.main div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, .12) !important;
    backdrop-filter: blur(12px);
    padding: 4px 4px !important;
}}

.mb-dash-head {{
    margin: 0 0 16px 0;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(255, 255, 255, .06);
}}
.mb-dash-kicker {{
    color: rgba(192, 132, 252, .9) !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .2em;
    text-transform: uppercase;
}}
.mb-dash-title {{
    color: #f8fafc !important;
    font-size: clamp(22px, 3.5vw, 30px);
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 4px 0 0 0;
    line-height: 1.2;
}}
.mb-dash-sub {{
    color: rgba(148, 163, 184, .95) !important;
    font-size: 13px;
    line-height: 1.45;
    margin: 6px 0 0 0;
    max-width: 640px;
}}

.mb-dash-stats {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 14px;
}}
@media (max-width: 900px) {{
    .mb-dash-stats {{ grid-template-columns: repeat(2, 1fr); }}
}}
.mb-dash-stat {{
    border-radius: 12px;
    padding: 12px 14px;
    background: #18181b;
    border: 1px solid #3f3f46;
}}
.mb-dash-stat .lbl {{
    color: rgba(148, 163, 184, .9) !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
}}
.mb-dash-stat .val {{
    color: #f8fafc !important;
    font-size: 20px;
    font-weight: 800;
    margin-top: 4px;
    letter-spacing: -0.02em;
}}
.mb-dash-stat .hint {{
    color: rgba(100, 116, 139, .95) !important;
    font-size: 10px;
    margin-top: 2px;
}}

.mb-dash-actions {{
    margin-bottom: 16px;
}}

.mb-dash-section {{
    color: rgba(196, 181, 253, .95) !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 0 0 10px 0;
}}

.mb-dash-limit {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, .05);
    font-size: 13px;
    color: #cbd5e1 !important;
}}
.mb-dash-limit:last-child {{ border-bottom: none; padding-bottom: 0; }}
.mb-dash-limit span:last-child {{
    color: #f8fafc !important;
    font-weight: 700;
    font-size: 12px;
}}

.mb-dash-act-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}}
@media (max-width: 700px) {{
    .mb-dash-act-grid {{ grid-template-columns: 1fr; }}
}}
.mb-dash-act {{
    border-radius: 12px;
    padding: 10px 12px;
    background: rgba(8, 10, 22, .4);
    border: 1px solid rgba(255, 255, 255, .05);
}}
.mb-dash-act .t {{
    color: #f1f5f9 !important;
    font-size: 13px;
    font-weight: 700;
}}
.mb-dash-act .d {{
    color: #64748b !important;
    font-size: 11px;
    margin-top: 2px;
}}
.mb-dash-empty {{
    color: #64748b !important;
    font-size: 13px;
    padding: 4px 0;
    line-height: 1.45;
}}
.mb-dash-foot {{
    color: #64748b !important;
    font-size: 12px;
    margin-top: 4px;
    text-align: center;
}}

.stApp:has(.mb-dash) section.main div[class*="st-key-dash_go_"] button {{
    min-height: 42px !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    background: rgba(10, 12, 24, .55) !important;
    border: 1px solid rgba(255, 255, 255, .09) !important;
    color: #e2e8f0 !important;
}}
.stApp:has(.mb-dash) section.main .st-key-dash_go_creator button {{
    background: linear-gradient(135deg, rgba(124, 58, 237, .85), rgba(99, 102, 241, .75)) !important;
    border-color: rgba(168, 85, 247, .35) !important;
    color: #fff !important;
}}
.stApp:has(.mb-dash) section.main div[class*="st-key-dash_ws_"] button:not(:disabled) {{
    min-height: 40px !important;
    font-size: 12px !important;
    background: rgba(10, 12, 24, .5) !important;
    border: 1px solid rgba(255, 255, 255, .08) !important;
    color: #e2e8f0 !important;
}}
.stApp:has(.mb-dash) section.main div[class*="st-key-dash_ws_"] button:disabled {{
    opacity: .45 !important;
}}
"""


WORKSPACE_ROWS = (
    ("Shorts & Video", "reels", "creator"),
    ("AI Chat", "chat", "chat"),
    ("Bilder", "image", "image"),
    ("Code", "coding", "coding"),
    ("Musik", "music", "music"),
    ("Football AI", "football", "football"),
    ("Automation", "automation", "automation_lab"),
    ("Projekte", "projects", "projects"),
)


def inject_dashboard_css() -> None:
    inject_css(page_layout_css(1080, TOPBAR_OFFSET, 48) + DASHBOARD_CSS)


def format_num(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


def nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def render_header(*, user: str, greeting: str = "") -> None:
    sub = greeting or f"Hallo {html.escape(user)} — starte mit Shorts oder wähle einen Workspace."
    st.markdown(
        f"""
<div class="mb-dash-head">
  <div class="mb-dash-kicker">Dashboard</div>
  <div class="mb-dash-title">Willkommen bei MaByte</div>
  <p class="mb-dash-sub">{sub}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(
    *,
    plan_label: str,
    tokens: int,
    football_label: str,
    tier: str,
) -> None:
    addon = "Aktiv" if football_label and football_label not in ("—", "Kein Plan", "None", "") else "—"
    cards = [
        ("Plan", plan_label, "MaByte Abo"),
        ("Tokens", format_num(tokens), "Guthaben"),
        ("Module", addon, "Erweiterungen"),
        ("Tier", tier, "Feature-Stufe"),
    ]
    inner = "".join(
        f'<div class="mb-dash-stat"><div class="lbl">{html.escape(l)}</div>'
        f'<div class="val">{html.escape(v)}</div>'
        f'<div class="hint">{html.escape(h)}</div></div>'
        for l, v, h in cards
    )
    st.markdown(f'<div class="mb-dash-stats">{inner}</div>', unsafe_allow_html=True)


def render_quick_actions() -> None:
    st.markdown('<div class="mb-dash-section">Schnellstart</div>', unsafe_allow_html=True)
    st.markdown('<div class="mb-dash-actions">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Shorts erstellen", key="dash_go_creator", use_container_width=True, type="primary"):
            st.session_state.creator_format = "Shorts"
            nav("creator")
    with c2:
        if st.button("AI Chat", key="dash_go_chat", use_container_width=True):
            nav("chat")
    with c3:
        if st.button("Football AI", key="dash_go_fb", use_container_width=True):
            nav("football")
    with c4:
        if st.button("Premium", key="dash_go_prem", use_container_width=True):
            nav("premium")
    st.markdown("</div>", unsafe_allow_html=True)


def _allowed(features: list, feature: str) -> bool:
    if feature == "projects":
        return True
    return "all" in features or feature in features


def render_workspace_matrix(plan: dict) -> None:
    features = plan.get("features", [])
    st.markdown('<div class="mb-dash-section">Workspaces</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (label, feature, page) in enumerate(WORKSPACE_ROWS):
        ok = _allowed(features, feature)
        with cols[i % 2]:
            btn_label = label if ok else f"{label} · Upgrade"
            if st.button(
                btn_label,
                key=f"dash_ws_{page}",
                use_container_width=True,
                disabled=not ok,
            ):
                if page == "creator":
                    st.session_state.creator_format = "Shorts"
                nav(page)


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
        f'<div class="mb-dash-limit"><span>{html.escape(k)}</span>'
        f"<span>{html.escape(str(v))} / Tag</span></div>"
        for k, v in rows
    )
    st.markdown(
        f'<div class="mb-dash-section">Tageslimits</div>{lr}',
        unsafe_allow_html=True,
    )


def render_recent_activity(username: str, *, limit: int = 8) -> None:
    items = recent_activity(username=username, limit=limit)
    if not items:
        items = list_usage(username)[:limit]
    st.markdown('<div class="mb-dash-section">Letzte Aktivität</div>', unsafe_allow_html=True)
    if not items:
        st.markdown(
            '<p class="mb-dash-empty">Noch keine Aktivität. Nutze <strong>Schnellstart → Shorts erstellen</strong>.</p>',
            unsafe_allow_html=True,
        )
        return
    blocks = []
    for row in items[:limit]:
        tool = str(row.get("tool", "system")).replace("_", " ").title()
        created = str(row.get("created_at", ""))[:16]
        blocks.append(
            f'<div class="mb-dash-act"><div class="t">{html.escape(tool)}</div>'
            f'<div class="d">{html.escape(created)}</div></div>'
        )
    st.markdown(
        f'<div class="mb-dash-act-grid">{"".join(blocks)}</div>',
        unsafe_allow_html=True,
    )
