"""Profile page — glassmorphism layout and render helpers."""
from __future__ import annotations

import html

import streamlit as st

from config import DAILY_LIMITS
from database import list_usage, recent_activity
from ui.components import (
    _amount_display,
    _format_payment_date,
    _payment_status_badge,
    _plan_label,
    format_num,
)
from ui.styles import inject_css

_PROFILE_CSS = """
html:has(.mb-prof) {
    --prof-glass-bg: rgba(255, 255, 255, 0.06);
    --prof-glass-panel: rgba(255, 255, 255, 0.04);
    --prof-glass-border: rgba(255, 255, 255, 0.12);
    --prof-glass-border-hover: rgba(139, 92, 246, 0.42);
    --prof-glass-blur: blur(16px);
    --prof-glass-grad: linear-gradient(90deg, rgba(139, 92, 246, 0.65), rgba(99, 102, 241, 0.55));
    --prof-text: #fafafa;
    --prof-muted: #a1a1aa;
    --prof-hint: #71717a;
    --prof-accent: #c4b5fd;
}

.stApp:has(.mb-prof) [data-testid="stAppViewContainer"],
.stApp:has(.mb-prof) section.main,
.stApp:has(.mb-prof) [data-testid="stMain"] {
    position: relative !important;
    background: transparent !important;
}

.prof-ambient {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
    background:
        radial-gradient(ellipse 80% 50% at 15% -10%, rgba(124, 58, 237, 0.14), transparent 58%),
        radial-gradient(ellipse 65% 45% at 88% 8%, rgba(99, 102, 241, 0.1), transparent 55%),
        radial-gradient(ellipse 55% 40% at 50% 100%, rgba(139, 92, 246, 0.08), transparent 60%),
        #09090b;
}
.prof-ambient-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(72px);
    opacity: 0.55;
}
.prof-ambient-glow--violet {
    width: min(520px, 70vw);
    height: min(520px, 70vw);
    top: -12%;
    left: -8%;
    background: rgba(124, 58, 237, 0.22);
}
.prof-ambient-glow--indigo {
    width: min(440px, 60vw);
    height: min(440px, 60vw);
    top: 28%;
    right: -10%;
    background: rgba(99, 102, 241, 0.16);
}

.stApp:has(.mb-prof) section.main .block-container {
    position: relative !important;
    z-index: 1 !important;
    max-width: 920px !important;
    padding-top: 8px !important;
    padding-bottom: 48px !important;
}
.stApp:has(.mb-prof) section.main [data-testid="stVerticalBlock"] {
    gap: 14px !important;
}
.stApp:has(.mb-prof) section.main div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--prof-glass-panel) !important;
    backdrop-filter: var(--prof-glass-blur) !important;
    -webkit-backdrop-filter: var(--prof-glass-blur) !important;
    border: 1px solid var(--prof-glass-border) !important;
    border-radius: 14px !important;
    box-shadow:
        0 10px 36px rgba(0, 0, 0, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
    padding: 4px 2px !important;
}
.stApp:has(.mb-prof) section.main div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(139, 92, 246, 0.22) !important;
}

.prof-head {
    margin: 0 0 18px 0;
    padding: 18px 20px;
    border-radius: 14px;
    border: 1px solid var(--prof-glass-border);
    background: var(--prof-glass-bg);
    backdrop-filter: var(--prof-glass-blur);
    -webkit-backdrop-filter: var(--prof-glass-blur);
    box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.prof-kicker {
    color: rgba(192, 132, 252, 0.95) !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.prof-title {
    color: var(--prof-text) !important;
    font-size: clamp(22px, 3.5vw, 30px);
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 4px 0 0 0;
    line-height: 1.2;
}
.prof-sub {
    color: rgba(148, 163, 184, 0.95) !important;
    font-size: 13px;
    line-height: 1.45;
    margin: 6px 0 0 0;
    max-width: 640px;
}

.prof-stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 6px;
}
@media (max-width: 900px) {
    .prof-stats { grid-template-columns: repeat(2, 1fr); }
}
.prof-stat {
    border-radius: 12px;
    padding: 14px 16px;
    background: var(--prof-glass-bg);
    backdrop-filter: var(--prof-glass-blur);
    -webkit-backdrop-filter: var(--prof-glass-blur);
    border: 1px solid var(--prof-glass-border);
    box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.07);
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
}
.prof-stat:hover {
    border-color: var(--prof-glass-border-hover);
    box-shadow:
        0 10px 28px rgba(0, 0, 0, 0.28),
        0 0 18px rgba(139, 92, 246, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.09);
}
.prof-stat .lbl {
    color: rgba(148, 163, 184, 0.92) !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.prof-stat .val {
    color: var(--prof-text) !important;
    font-size: 20px;
    font-weight: 800;
    margin-top: 4px;
}
.prof-stat .hint {
    color: rgba(100, 116, 139, 0.95) !important;
    font-size: 10px;
    margin-top: 2px;
}

.prof-section {
    color: var(--prof-accent) !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 10px 0;
}
.prof-limit {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 13px;
    color: #cbd5e1 !important;
}
.prof-limit:last-child { border-bottom: none; }

.prof-act-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}
.prof-act {
    border-radius: 10px;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.prof-act .t {
    color: #f1f5f9 !important;
    font-size: 13px;
    font-weight: 700;
}
.prof-act .d {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 2px;
}
.prof-empty {
    color: #64748b !important;
    font-size: 13px;
    padding: 4px 0;
    line-height: 1.45;
}

.prof-pay-wrap { margin-top: 4px; }
.prof-pay-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}
.prof-pay-head .prof-section { margin: 0; }
.prof-pay-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
.prof-pay-table th {
    text-align: left;
    padding: 10px 14px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--prof-hint) !important;
    background: rgba(0, 0, 0, 0.22);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.prof-pay-table td {
    padding: 12px 14px;
    font-size: 13px;
    color: #e4e4e7 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
}
.prof-pay-table tr:last-child td { border-bottom: none; }
.prof-pay-table tr:hover td { background: rgba(124, 58, 237, 0.08); }
.prof-pay-plan { font-weight: 700; color: #f4f4f5 !important; }
.prof-pay-meta { font-size: 11px; color: var(--prof-hint) !important; margin-top: 2px; }
.prof-pay-amt { font-weight: 700; color: var(--prof-text) !important; white-space: nowrap; }
.prof-pay-date { color: #94a3b8 !important; font-size: 12px; white-space: nowrap; }
.prof-pay-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.prof-pay-badge.paid { background: rgba(34, 197, 94, 0.15); color: #4ade80 !important; }
.prof-pay-badge.pending { background: rgba(113, 113, 122, 0.2); color: #a1a1aa !important; }
.prof-pay-badge.created { background: rgba(234, 179, 8, 0.12); color: #facc15 !important; }
.prof-pay-badge.failed { background: rgba(239, 68, 68, 0.12); color: #f87171 !important; }
.prof-pay-empty {
    padding: 28px 20px;
    text-align: center;
    border-radius: 14px;
    border: 1px dashed rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
.prof-pay-empty .t { color: #e4e4e7 !important; font-size: 14px; font-weight: 600; margin: 0 0 6px; }
.prof-pay-empty .d { color: #64748b !important; font-size: 12px; line-height: 1.5; margin: 0; }

.stApp:has(.mb-prof) .st-key-dash_go_home .stButton > button,
.stApp:has(.mb-prof) .st-key-dash_go_home button[data-testid="stBaseButton-secondary"] {
    border-radius: 12px !important;
    min-height: 44px !important;
    border: 1px solid transparent !important;
    background:
        linear-gradient(rgba(139, 92, 246, 0.14), rgba(99, 102, 241, 0.1)) padding-box,
        var(--prof-glass-grad) border-box !important;
    color: var(--prof-text) !important;
    font-weight: 600 !important;
    backdrop-filter: var(--prof-glass-blur) !important;
    -webkit-backdrop-filter: var(--prof-glass-blur) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 8px 24px rgba(0, 0, 0, 0.22) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease !important;
}
.stApp:has(.mb-prof) .st-key-dash_go_home .stButton > button:hover,
.stApp:has(.mb-prof) .st-key-dash_go_home button[data-testid="stBaseButton-secondary"]:hover {
    border-color: transparent !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 0 20px rgba(139, 92, 246, 0.28),
        0 10px 28px rgba(0, 0, 0, 0.28) !important;
    transform: translateY(-1px) !important;
}

.stApp:has(.mb-prof) .st-key-pay_nav_premium .stButton > button,
.stApp:has(.mb-prof) .st-key-pay_nav_premium button[data-testid="stBaseButton-tertiary"] {
    padding: 7px 14px !important;
    border-radius: 999px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #e9d5ff !important;
    background: rgba(124, 58, 237, 0.18) !important;
    border: 1px solid rgba(139, 92, 246, 0.35) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    min-height: 0 !important;
    height: auto !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}
.stApp:has(.mb-prof) .st-key-pay_nav_premium .stButton > button:hover {
    background: rgba(124, 58, 237, 0.3) !important;
    border-color: rgba(139, 92, 246, 0.48) !important;
}

.stApp:has(.mb-prof) [data-testid="stExpander"] {
    border: 1px solid var(--prof-glass-border) !important;
    border-radius: 14px !important;
    background: var(--prof-glass-panel) !important;
    backdrop-filter: var(--prof-glass-blur) !important;
    -webkit-backdrop-filter: var(--prof-glass-blur) !important;
    box-shadow:
        0 8px 28px rgba(0, 0, 0, 0.24),
        inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    overflow: hidden !important;
}
.stApp:has(.mb-prof) [data-testid="stExpander"] summary {
    background: rgba(255, 255, 255, 0.03) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding: 12px 16px !important;
    font-weight: 600 !important;
    color: #e4e4e7 !important;
}
.stApp:has(.mb-prof) [data-testid="stExpander"] summary:hover {
    background: rgba(139, 92, 246, 0.08) !important;
}
.stApp:has(.mb-prof) [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: transparent !important;
    padding: 8px 12px 12px !important;
}
.stApp:has(.mb-prof) [data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.stApp:has(.mb-prof) [data-testid="stDataFrame"] > div {
    background: rgba(0, 0, 0, 0.2) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}

@media (max-width: 768px) {
    .prof-head { padding: 14px 16px; }
    .prof-act-grid { grid-template-columns: 1fr; }
}
"""


def inject_profile_css() -> None:
    inject_css(_PROFILE_CSS)


def render_profile_ambient() -> None:
    st.markdown(
        """<div class="prof-ambient" aria-hidden="true">
<div class="prof-ambient-glow prof-ambient-glow--violet"></div>
<div class="prof-ambient-glow prof-ambient-glow--indigo"></div>
</div>""",
        unsafe_allow_html=True,
    )


def render_profile_header(*, user: str, greeting: str = "") -> None:
    sub = greeting or f"Hallo {html.escape(user)} — Account, Tokens und Limits."
    st.markdown(
        f"""<div class="prof-head">
<div class="prof-kicker">Account</div>
<div class="prof-title">Profil</div>
<p class="prof-sub">{sub}</p>
</div>""",
        unsafe_allow_html=True,
    )


def render_profile_stats(
    *, plan_label: str, tokens: int, football_label: str, tier: str
) -> None:
    addon = (
        "Aktiv"
        if football_label and football_label not in ("—", "Kein Plan", "None", "")
        else "—"
    )
    cards = [
        ("Plan", plan_label, "MaByte Abo"),
        ("Tokens", format_num(tokens), "Guthaben"),
        ("Module", addon, "Erweiterungen"),
        ("Tier", tier, "Feature-Stufe"),
    ]
    inner = "".join(
        f'<div class="prof-stat"><div class="lbl">{html.escape(l)}</div>'
        f'<div class="val">{html.escape(v)}</div>'
        f'<div class="hint">{html.escape(h)}</div></div>'
        for l, v, h in cards
    )
    st.markdown(f'<div class="prof-stats">{inner}</div>', unsafe_allow_html=True)


def render_profile_daily_limits(plan_key: str) -> None:
    limits = DAILY_LIMITS.get(plan_key, DAILY_LIMITS["free"])
    rows = [
        ("Chat", limits.get("chat", 0)),
        ("Code", limits.get("coding", 0)),
        ("Bilder", limits.get("image", 0)),
        ("Shorts", limits.get("reels", 0)),
        ("Video", limits.get("video", 0)),
    ]
    lr = "".join(
        f'<div class="prof-limit"><span>{html.escape(k)}</span>'
        f"<span>{html.escape(str(v))} / Tag</span></div>"
        for k, v in rows
    )
    st.markdown(f'<div class="prof-section">Tageslimits</div>{lr}', unsafe_allow_html=True)


def render_profile_recent_activity(username: str, *, limit: int = 8) -> None:
    items = recent_activity(username=username, limit=limit)
    if not items:
        items = list_usage(username)[:limit]
    st.markdown('<div class="prof-section">Letzte Aktivität</div>', unsafe_allow_html=True)
    if not items:
        st.markdown(
            '<p class="prof-empty">Noch keine Aktivität — starte mit AI Chat oder Creator.</p>',
            unsafe_allow_html=True,
        )
        return
    blocks = []
    for row in items[:limit]:
        tool = str(row.get("tool", "system")).replace("_", " ").title()
        created = str(row.get("created_at", ""))[:16]
        blocks.append(
            f'<div class="prof-act"><div class="t">{html.escape(tool)}</div>'
            f'<div class="d">{html.escape(created)}</div></div>'
        )
    st.markdown(f'<div class="prof-act-grid">{"".join(blocks)}</div>', unsafe_allow_html=True)


def render_profile_payments(username: str, *, purchases: list[dict] | None = None) -> None:
    from database import list_purchases
    from ui.sidebar import navigate_to

    rows = purchases if purchases is not None else list_purchases(username)

    st.markdown('<div class="prof-pay-wrap">', unsafe_allow_html=True)
    head_l, head_r = st.columns([1, 0.35], gap="small")
    with head_l:
        st.markdown('<div class="prof-section">Zahlungen</div>', unsafe_allow_html=True)
    with head_r:
        if st.button("Plan verwalten", key="pay_nav_premium", use_container_width=True, type="tertiary"):
            navigate_to("premium")

    if not rows:
        st.markdown(
            """<div class="prof-pay-empty">
<p class="t">Noch keine Zahlungen</p>
<p class="d">Nach einem Upgrade über Stripe erscheinen deine Rechnungen hier.</p>
</div></div>""",
            unsafe_allow_html=True,
        )
        return

    body: list[str] = []
    for row in rows[:15]:
        plan_key = str(row.get("plan") or row.get("product") or "")
        plan_name = _plan_label(plan_key)
        amount_txt = _amount_display(row, plan_key)
        when = _format_payment_date(str(row.get("created_at") or ""))
        cls, label = _payment_status_badge(row)
        sid = str(row.get("stripe_session_id") or "")[:18]
        meta = f"Stripe · {html.escape(sid)}…" if sid else "MaByte Checkout"
        body.append(
            "<tr>"
            f'<td><div class="prof-pay-plan">{html.escape(plan_name)}</div>'
            f'<div class="prof-pay-meta">{meta}</div></td>'
            f'<td class="prof-pay-amt">{html.escape(amount_txt)}</td>'
            f'<td class="prof-pay-date">{html.escape(when)}</td>'
            f'<td><span class="prof-pay-badge {cls}">{html.escape(label)}</span></td>'
            "</tr>"
        )

    st.markdown(
        f"""<table class="prof-pay-table">
<thead><tr>
<th>Plan</th><th>Betrag</th><th>Datum</th><th>Status</th>
</tr></thead>
<tbody>{"".join(body)}</tbody>
</table></div>""",
        unsafe_allow_html=True,
    )
