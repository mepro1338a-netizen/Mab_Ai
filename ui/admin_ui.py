"""Professional Admin Control Panel ÔÇö HTML components."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui.styles import inject_css

ADMIN_UI_CSS = """
.adm-hero {
    border-radius: 28px;
    padding: 28px 32px;
    margin: 0 0 14px 0;
    background:
        radial-gradient(circle at 92% 8%, rgba(239,68,68,.12), transparent 38%),
        radial-gradient(circle at 8% 0%, rgba(168,85,247,.28), transparent 42%),
        linear-gradient(135deg, rgba(10,12,28,.98), rgba(6,8,18,.99));
    border: 1px solid rgba(255,231,163,.12);
    box-shadow: 0 28px 70px rgba(0,0,0,.35);
}
.adm-kicker {
    color: #c084fc !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .28em;
    text-transform: uppercase;
}
.adm-title {
    color: #f8fafc !important;
    font-size: 38px;
    font-weight: 1000;
    letter-spacing: -1.5px;
    margin-top: 8px;
}
.adm-sub {
    color: #94a3b8 !important;
    font-size: 14px;
    margin-top: 10px;
    line-height: 1.55;
}
.adm-pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.adm-pill {
    display: inline-flex;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 1000;
    border: 1px solid rgba(255,255,255,.1);
}
.adm-pill.role { background: linear-gradient(135deg, #4c1d95, #312e81); color: #e9d5ff !important; }
.adm-pill.lvl { background: rgba(34,197,94,.15); color: #86efac !important; border-color: rgba(34,197,94,.3); }
.adm-pill.owner { background: linear-gradient(135deg, #7f1d1d, #991b1b); color: #fecaca !important; }
.adm-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 18px 0;
}
@media (max-width: 1100px) { .adm-kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.adm-kpi {
    border-radius: 18px;
    padding: 16px 18px;
    background: linear-gradient(145deg, rgba(16,18,40,.95), rgba(8,10,22,.98));
    border: 1px solid rgba(168,85,247,.14);
}
.adm-kpi .k {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
}
.adm-kpi .v {
    color: #ffe7a3 !important;
    font-size: 26px;
    font-weight: 1000;
    margin-top: 8px;
}
.adm-kpi .h {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 6px;
}
.adm-kpi.warn { border-color: rgba(239,68,68,.35); }
.adm-kpi.good { border-color: rgba(34,197,94,.3); }
.adm-section {
    border-radius: 22px;
    padding: 20px 22px;
    margin: 0 0 12px 0;
    background: linear-gradient(160deg, rgba(14,16,36,.94), rgba(8,10,24,.98));
    border: 1px solid rgba(168,85,247,.12);
}
.adm-section-title {
    color: #ffe7a3 !important;
    font-size: 16px;
    font-weight: 1000;
    margin-bottom: 4px;
}
.adm-section-sub {
    color: #64748b !important;
    font-size: 12px;
    margin-bottom: 14px;
}
.adm-ticket {
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 10px;
    background: rgba(12,14,32,.8);
    border: 1px solid rgba(255,255,255,.06);
}
.adm-ticket.open { border-left: 3px solid #22c55e; }
.adm-ticket.closed { border-left: 3px solid #64748b; opacity: .85; }
.adm-ticket .subj {
    color: #f8fafc !important;
    font-size: 15px;
    font-weight: 1000;
}
.adm-ticket .meta {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 6px;
}
.adm-ticket .body {
    color: #cbd5e1 !important;
    font-size: 13px;
    line-height: 1.55;
    margin-top: 10px;
}
.adm-user-card {
    border-radius: 20px;
    padding: 18px 20px;
    margin-bottom: 12px;
    background: linear-gradient(145deg, rgba(14,16,34,.92), rgba(8,10,24,.96));
    border: 1px solid rgba(255,255,255,.07);
}
.adm-user-card.banned { border-color: rgba(239,68,68,.4); }
.adm-user-card.staff { border-color: rgba(168,85,247,.35); }
.adm-user-card .uname {
    color: #f0fdf4 !important;
    font-size: 18px;
    font-weight: 1000;
}
.adm-user-card .uemail {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-top: 4px;
}
.adm-chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.adm-chip {
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 900;
    background: rgba(15,23,42,.8);
    color: #cbd5e1 !important;
    border: 1px solid rgba(255,255,255,.08);
}
.adm-chip.plan { color: #ffe7a3 !important; border-color: rgba(255,231,163,.2); }
.adm-chip.fb { color: #86efac !important; border-color: rgba(34,197,94,.25); }
.adm-chip.bad { color: #fca5a5 !important; border-color: rgba(239,68,68,.3); }
.adm-activity {
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 6px;
    background: rgba(8,10,22,.6);
    border: 1px solid rgba(255,255,255,.04);
}
.adm-activity .t { color: #e2e8f0 !important; font-size: 13px; font-weight: 800; }
.adm-activity .d { color: #64748b !important; font-size: 11px; margin-top: 3px; }
.adm-bar-row { margin-bottom: 10px; }
.adm-bar-label {
    display: flex;
    justify-content: space-between;
    color: #94a3b8 !important;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 4px;
}
.adm-bar {
    height: 8px;
    border-radius: 999px;
    background: rgba(255,255,255,.08);
    overflow: hidden;
}
.adm-bar > span {
    display: block;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #7c3aed, #22c55e);
}
.adm-staff-card {
    border-radius: 16px;
    padding: 14px 16px;
    background: rgba(76,29,149,.15);
    border: 1px solid rgba(168,85,247,.2);
    margin-bottom: 8px;
}
.adm-env-ok { color: #86efac !important; }
.adm-env-miss { color: #f87171 !important; }
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 6px !important;
    background: rgba(8,10,22,.7) !important;
    border-radius: 14px !important;
    padding: 6px !important;
}
.adm-user-table {
    border-radius: 16px;
    border: 1px solid rgba(168,85,247,.14);
    background: linear-gradient(160deg, rgba(10,12,28,.92), rgba(6,8,18,.98));
    overflow: hidden;
    margin-top: 8px;
}
.adm-user-table-head {
    display: grid;
    grid-template-columns: 2.3fr 1.05fr 1.05fr 1.15fr 0.85fr 0.75fr 0.55fr;
    gap: 6px;
    padding: 10px 14px;
    background: rgba(8,10,22,.85);
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.adm-user-table-head span {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
}
.adm-user-cell-name {
    color: #f8fafc !important;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.25;
}
.adm-user-cell-email {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 2px;
}
.adm-user-cell-meta {
    color: #475569 !important;
    font-size: 10px;
    margin-top: 3px;
}
.adm-status-pill {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 900;
    border: 1px solid rgba(255,255,255,.08);
}
.adm-status-pill.active { color: #86efac !important; background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.25); }
.adm-status-pill.banned { color: #fca5a5 !important; background: rgba(239,68,68,.12); border-color: rgba(239,68,68,.3); }
.adm-status-pill.staff { color: #e9d5ff !important; background: rgba(168,85,247,.15); border-color: rgba(168,85,247,.25); }
.adm-row-div {
    border: none;
    border-top: 1px solid rgba(255,255,255,.05);
    margin: 0;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.adm-user-table) {
    border-color: rgba(168,85,247,.12) !important;
}
.stApp:has(.adm-hero) div[data-testid="stTabs"] {
    margin-top: 0 !important;
}
.stApp:has(.adm-hero) div[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 4px !important;
}
.stApp:has(.adm-hero) [data-testid="stElementContainer"]:has(.adm-section) {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
.stApp:has(.adm-hero) [data-testid="stElementContainer"]:has(.adm-section-title) {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
.adm-console-wrap {
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 14px;
    background: linear-gradient(160deg, rgba(6,10,8,.96), rgba(4,8,6,.99));
    border: 1px solid rgba(34,197,94,.18);
    box-shadow: inset 0 0 40px rgba(0,0,0,.35);
}
.adm-console-title {
    color: #86efac !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.adm-console-log {
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 12px;
    line-height: 1.55;
    color: #a7f3d0 !important;
    background: rgba(0,0,0,.45);
    border: 1px solid rgba(34,197,94,.12);
    border-radius: 12px;
    padding: 14px 16px;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}
.adm-console-line {
    margin: 0 0 4px 0;
}
.adm-console-line.dim { color: #64748b !important; }
.adm-console-line.warn { color: #fbbf24 !important; }
.adm-console-line.err { color: #f87171 !important; }
.adm-console-kv {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 12px;
}
@media (max-width: 900px) { .adm-console-kv { grid-template-columns: 1fr; } }
.adm-console-kv .item {
    border-radius: 12px;
    padding: 12px 14px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(34,197,94,.1);
}
.adm-console-kv .k {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.adm-console-kv .v {
    color: #ecfdf5 !important;
    font-size: 14px;
    font-weight: 800;
    margin-top: 4px;
    font-family: "Cascadia Code", "Consolas", monospace;
}
.adm-console-section {
    border-radius: 16px;
    padding: 16px 18px;
    margin: 0 0 14px 0;
    background: linear-gradient(160deg, rgba(6,12,10,.92), rgba(4,8,6,.98));
    border: 1px solid rgba(34,197,94,.14);
}
.adm-console-section .st {
    color: #86efac !important;
    font-size: 13px;
    font-weight: 1000;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.adm-console-section .ss {
    color: #64748b !important;
    font-size: 11px;
    margin-bottom: 10px;
}
.adm-filter-bar {
    border-radius: 14px;
    padding: 12px 14px;
    margin: 0 0 12px 0;
    background: rgba(8,10,22,.75);
    border: 1px solid rgba(168,85,247,.1);
}
.adm-filter-bar-label {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.adm-panel-card {
    border-radius: 18px;
    padding: 4px 0 8px 0;
    margin-bottom: 10px;
}
.adm-two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
@media (max-width: 900px) { .adm-two-col { grid-template-columns: 1fr; } }
div[data-testid="stTabs"] [data-baseweb="tab"] {
    font-size: 12px !important;
    font-weight: 800 !important;
    padding: 8px 14px !important;
}
.adm-user-quick {
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 8px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(34,197,94,.12);
}
"""


def inject_admin_ui_css() -> None:
    inject_css(ADMIN_UI_CSS)


def render_hero(role: str, level: int, *, is_owner: bool) -> None:
    owner_pill = '<span class="adm-pill owner">OWNER ACCESS</span>' if is_owner else ""
    st.markdown(
        f"""
<div class="adm-hero">
    <div class="adm-kicker">MaByte · Interne Steuerung</div>
    <div class="adm-title">Admin Control</div>
    <div class="adm-sub">Dashboard für Nutzer, Umsatz, Sicherheit & Support</div>
    <div class="adm-pill-row">
        {owner_pill}
        <span class="adm-pill role">{html.escape(role.upper())}</span>
        <span class="adm-pill lvl">Level {level}</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(metrics: list[tuple[str, str, str, str]]) -> None:
    """(label, value, hint, variant) variant: default|good|warn"""
    cards = []
    for label, value, hint, variant in metrics:
        cls = "adm-kpi"
        if variant == "warn":
            cls += " warn"
        elif variant == "good":
            cls += " good"
        cards.append(
            f'<div class="{cls}"><div class="k">{html.escape(label)}</div>'
            f'<div class="v">{html.escape(value)}</div>'
            f'<div class="h">{html.escape(hint)}</div></div>'
        )
    st.markdown(f'<div class="adm-kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_section(title: str, subtitle: str = "") -> None:
    sub = f'<div class="adm-section-sub">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="adm-section adm-panel-card">'
        f'<div class="adm-section-title">{html.escape(title)}</div>{sub}</div>',
        unsafe_allow_html=True,
    )


def render_filter_bar(label: str = "Filter") -> None:
    st.markdown(
        f'<div class="adm-filter-bar"><div class="adm-filter-bar-label">{html.escape(label)}</div>',
        unsafe_allow_html=True,
    )


def close_filter_bar() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_console_section(title: str, subtitle: str = "") -> None:
    sub = f'<div class="ss">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="adm-console-section"><div class="st">{html.escape(title)}</div>{sub}',
        unsafe_allow_html=True,
    )


def close_console_section() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_distribution_bars(title: str, data: dict[str, Any], *, max_items: int = 8) -> None:
    if not data:
        st.markdown('<div class="adm-section-sub">Keine Daten</div>', unsafe_allow_html=True)
        return
    items = sorted(data.items(), key=lambda x: -int(x[1]))[:max_items]
    top = max(int(v) for _, v in items) or 1
    bars = []
    for name, count in items:
        pct = int((int(count) / top) * 100)
        bars.append(
            f'<div class="adm-bar-row"><div class="adm-bar-label">'
            f'<span>{html.escape(str(name))}</span><span>{int(count)}</span></div>'
            f'<div class="adm-bar"><span style="width:{pct}%"></span></div></div>'
        )
    st.markdown(
        f'<div class="adm-section"><div class="adm-section-title">{html.escape(title)}</div>'
        f'{"".join(bars)}</div>',
        unsafe_allow_html=True,
    )


def render_ticket_card(item: dict) -> str:
    status = str(item.get("status") or "open")
    cls = "open" if status == "open" else "closed"
    return f"""
<div class="adm-ticket {cls}">
    <div class="subj">#{item.get('id')} ┬À {html.escape(str(item.get('subject') or 'Ticket'))}</div>
    <div class="meta">{html.escape(str(item.get('category') or ''))} ┬À {html.escape(str(item.get('username') or ''))} ┬À {html.escape(str(item.get('created_at', ''))[:16])}</div>
    <div class="body">{html.escape(str(item.get('message') or '')[:500])}</div>
</div>
    """


def render_user_header(item: dict) -> str:
    banned = int(item.get("is_banned") or 0) == 1
    role = str(item.get("role") or "user")
    level = int(item.get("admin_level") or 0)
    cls = "adm-user-card"
    if banned:
        cls += " banned"
    elif level >= 1:
        cls += " staff"
    chips = [
        f'<span class="adm-chip plan">{html.escape(str(item.get("plan") or "free"))}</span>',
        f'<span class="adm-chip fb">{html.escape(str(item.get("football_plan") or "none"))}</span>',
        f'<span class="adm-chip">{html.escape(role)} ┬À L{level}</span>',
    ]
    if banned:
        chips.append('<span class="adm-chip bad">GESPERRT</span>')
    return f"""
<div class="{cls}">
    <div class="uname">{html.escape(str(item.get('username') or ''))}</div>
    <div class="uemail">{html.escape(str(item.get('email') or ''))}</div>
    <div class="adm-chip-row">{"".join(chips)}</div>
</div>
    """


USER_TABLE_COLS = [2.3, 1.05, 1.05, 1.15, 0.85, 0.75, 0.55]
USER_TABLE_LABELS = ["Nutzer", "Rolle", "Plan", "Football", "Tokens", "Status", "Aktion"]


def render_user_table_header() -> None:
    cells = "".join(f"<span>{html.escape(label)}</span>" for label in USER_TABLE_LABELS)
    st.markdown(f'<div class="adm-user-table-head">{cells}</div>', unsafe_allow_html=True)


def render_user_name_cell(item: dict) -> None:
    uname = html.escape(str(item.get("username") or ""))
    email = html.escape(str(item.get("email") or ""))
    role = str(item.get("role") or "user")
    level = int(item.get("admin_level") or 0)
    meta = f"{html.escape(role)} · L{level}" if level else html.escape(role)
    st.markdown(
        f'<div class="adm-user-cell-name">{uname}</div>'
        f'<div class="adm-user-cell-email">{email}</div>'
        f'<div class="adm-user-cell-meta">{meta}</div>',
        unsafe_allow_html=True,
    )


def render_user_status_pill(*, banned: bool, is_staff: bool) -> None:
    if banned:
        cls, label = "banned", "Gesperrt"
    elif is_staff:
        cls, label = "staff", "Staff"
    else:
        cls, label = "active", "Aktiv"
    st.markdown(
        f'<span class="adm-status-pill {cls}">{label}</span>',
        unsafe_allow_html=True,
    )


def render_activity_feed(items: list[tuple[str, str]]) -> None:
    if not items:
        st.markdown('<div class="adm-empty">Keine Aktivität</div>', unsafe_allow_html=True)
        return
    blocks = [
        f'<div class="adm-activity"><div class="t">{html.escape(t)}</div>'
        f'<div class="d">{html.escape(d)}</div></div>'
        for t, d in items
    ]
    st.markdown("".join(blocks), unsafe_allow_html=True)


def render_console_kv(items: list[tuple[str, str]]) -> None:
    cells = "".join(
        f'<div class="item"><div class="k">{html.escape(k)}</div>'
        f'<div class="v">{html.escape(v)}</div></div>'
        for k, v in items
    )
    st.markdown(f'<div class="adm-console-kv">{cells}</div>', unsafe_allow_html=True)


def render_console_log(lines: list[tuple[str, str]], *, title: str = "Log") -> None:
    """Render terminal log lines: (css_class, text) where class is dim|warn|err|empty."""
    body = "".join(
        f'<div class="adm-console-line {html.escape(cls)}">{html.escape(text)}</div>'
        for cls, text in lines
    ) or '<div class="adm-console-line dim">Keine Einträge.</div>'
    st.markdown(
        f'<div class="adm-console-wrap"><div class="adm-console-title">{html.escape(title)}</div>'
        f'<div class="adm-console-log">{body}</div></div>',
        unsafe_allow_html=True,
    )
