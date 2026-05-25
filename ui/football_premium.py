"""Premium Football UI — glowing cards, pulse, betting intel, dark containers only."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui.styles import inject_css


FOOTBALL_PREMIUM_CSS = """
.fb-premium .stTabs [data-baseweb="tab"] {
    background: rgba(34,197,94,.08) !important;
    border: 1px solid rgba(134,239,172,.12) !important;
    color: #d1fae5 !important;
}
.fb-premium .stTabs [aria-selected="true"] {
    background: rgba(34,197,94,.22) !important;
    box-shadow: 0 0 20px rgba(34,197,94,.15) !important;
}
.fb-premium div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(10,16,28,.96), rgba(6,10,18,.99)) !important;
    border: 1px solid rgba(134,239,172,.12) !important;
    border-radius: 20px !important;
}
.fb-glow-card {
    border-radius: 20px;
    padding: 18px 20px;
    margin-bottom: 12px;
    background: linear-gradient(145deg, rgba(12,20,36,.95), rgba(6,14,10,.98));
    border: 1px solid rgba(134,239,172,.18);
    box-shadow: 0 0 32px rgba(34,197,94,.08), inset 0 1px 0 rgba(255,255,255,.04);
}
.fb-glow-card .title {
    color: #f0fdf4 !important;
    font-size: 15px;
    font-weight: 900;
    margin: 0 0 6px 0;
}
.fb-glow-card .sub {
    color: #64748b !important;
    font-size: 12px;
    line-height: 1.45;
    margin: 0;
}
.fb-metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
    margin: 12px 0;
}
.fb-metric {
    border-radius: 16px;
    padding: 14px;
    background: rgba(0,0,0,.25);
    border: 1px solid rgba(255,255,255,.08);
}
.fb-metric .k {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.fb-metric .v {
    color: #fff !important;
    font-size: 22px;
    font-weight: 900;
    margin-top: 6px;
}
.fb-metric .hint {
    color: #64748b !important;
    font-size: 10px;
    margin-top: 4px;
}
.fb-metric.value .v { color: #4ade80 !important; }
.fb-metric.risk .v { color: #fbbf24 !important; }
.fb-pulse {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(34,197,94,.15);
    border: 1px solid rgba(34,197,94,.35);
    color: #bbf7d0 !important;
    font-size: 11px;
    font-weight: 800;
}
.fb-pulse::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 12px #22c55e;
    animation: fb-pulse-beat 1.4s ease-in-out infinite;
}
@keyframes fb-pulse-beat {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: .5; transform: scale(.85); }
}
.fb-alert {
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,.1);
    background: rgba(15,23,42,.6);
}
.fb-alert.success { border-color: rgba(34,197,94,.35); }
.fb-alert.warn { border-color: rgba(251,191,36,.35); }
.fb-alert .t { color: #f8fafc !important; font-weight: 800; font-size: 13px; }
.fb-alert .d { color: #94a3b8 !important; font-size: 12px; margin-top: 4px; }
.fb-bm-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.fb-bm-table th {
    color: #86efac !important;
    text-align: left;
    padding: 8px;
    border-bottom: 1px solid rgba(255,255,255,.08);
}
.fb-bm-table td {
    color: #e2e8f0 !important;
    padding: 8px;
    border-bottom: 1px solid rgba(255,255,255,.05);
}
.fb-auto-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
}
.fb-auto-card {
    border-radius: 18px;
    padding: 16px;
    background: linear-gradient(160deg, rgba(30,20,50,.7), rgba(10,14,28,.95));
    border: 1px solid rgba(168,85,247,.2);
}
.fb-auto-card h4 {
    color: #e9d5ff !important;
    margin: 0 0 8px 0;
    font-size: 14px;
}
.fb-auto-card p {
    color: #94a3b8 !important;
    font-size: 12px;
    margin: 0;
}
@media (max-width: 640px) {
    .fb-metric-grid { grid-template-columns: repeat(2, 1fr); }
    .fb-auto-grid { grid-template-columns: 1fr; }
}
"""


def inject_football_premium_css() -> None:
    inject_css(FOOTBALL_PREMIUM_CSS)


def render_pulse_live(label: str = "LIVE INTELLIGENCE") -> None:
    st.markdown(
        f'<span class="fb-pulse">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )



def _metric_card(cls: str, key: str, val: str, hint: str = "") -> str:
    hint_html = f'<div class="hint">{html.escape(hint)}</div>' if hint else ""
    return (
        f'<div class="{cls}"><div class="k">{html.escape(key)}</div>'
        f'<div class="v">{html.escape(val)}</div>{hint_html}</div>'
    )


def render_betting_intel_dashboard(analysis: dict[str, Any]) -> None:
    metrics = [
        ("Implizite Wahrscheinlichkeit", f"{analysis.get('implied_probability_pct', 0):.1f}%", ""),
        ("Expected Value", f"{analysis.get('expected_value', 0):+.2f}", "pro Einsatz"),
        ("Edge", f"{analysis.get('edge_pct', 0):+.2f}%", "vs. Markt"),
        ("Confidence", f"{analysis.get('confidence_pct', 0):.0f}%", "Signal"),
        ("Risk Score", f"{analysis.get('risk_score', 0):.0f}", analysis.get("risk_label", "")),
        ("Value", str(analysis.get("value_label", "—")), ""),
    ]
    cards = []
    for k, v, s in metrics:
        cls = "fb-metric"
        if k == "Value" and analysis.get("is_value_bet"):
            cls += " value"
        if k == "Risk Score":
            cls += " risk"
        cards.append(_metric_card(cls, k, v, s))
    st.markdown(f'<div class="fb-metric-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    value_count = int(analysis.get("value_bet_count") or 0)
    if value_count:
        st.markdown(
            f'<div class="fb-glow-card"><div class="title">'
            f'{value_count} Value-Signal(e) im Marktvergleich</div></div>',
            unsafe_allow_html=True,
        )

    comp = analysis.get("bookmaker_comparison") or []
    if comp:
        rows = "".join(
            f"<tr><td>{html.escape(r.get('market',''))}</td>"
            f"<td>{html.escape(r.get('selection',''))}</td>"
            f"<td><strong>{r.get('best_odd',0):.2f}</strong></td>"
            f"<td>{html.escape(r.get('bookmaker',''))}</td>"
            f"<td>{r.get('implied_pct',0):.1f}%</td></tr>"
            for r in comp[:10]
        )
        st.markdown(
            f"""
<div class="fb-glow-card">
    <div class="title">Bookmaker Comparison</div>
    <div class="sub">Beste Quote pro Markt</div>
    <table class="fb-bm-table">
    <thead><tr><th>Markt</th><th>Auswahl</th><th>Quote</th><th>Anbieter</th><th>Impl.</th></tr></thead>
    <tbody>{rows}</tbody>
    </table>
</div>
            """,
            unsafe_allow_html=True,
        )


def render_live_intel_panel(momentum: dict[str, Any], alerts: list[dict[str, Any]]) -> None:
    st.markdown(
        f"""
<div class="fb-glow-card">
    <div class="title">Momentum · {html.escape(str(momentum.get('label', '')))}</div>
    <div class="sub">Leader: {html.escape(str(momentum.get('leader', '—')))} · Score {momentum.get('score', 0)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    for a in alerts[:6]:
        sev = a.get("severity", "info")
        cls = "success" if sev == "success" else ("warn" if sev == "warn" else "")
        st.markdown(
            f"""
<div class="fb-alert {cls}">
    <div class="t">{html.escape(a.get('title', ''))}</div>
    <div class="d">{html.escape(a.get('detail', ''))}</div>
</div>
            """,
            unsafe_allow_html=True,
        )


def render_automation_dashboard(
    workflows: list[dict[str, str]],
    jobs: list[dict[str, Any]],
) -> None:
    cards = "".join(
        f'<div class="fb-auto-card">'
        f'<h4>{html.escape(w.get("title", ""))}</h4>'
        f'<p>{html.escape(w.get("desc", ""))}</p></div>'
        for w in workflows
    )
    st.markdown(f'<div class="fb-auto-grid">{cards}</div>', unsafe_allow_html=True)
    if jobs:
        st.markdown("**Aktive Jobs**")
        for j in jobs[:5]:
            st.caption(f"{j.get('status', '?')} · {j.get('title', '')} · {j.get('created_at', '')[:16]}")


def render_viral_export_bar(club: str, opponent: str, package_text: str) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("→ Reels Studio", key="fb_export_reels", width="stretch"):
            st.session_state.page = "reels"
            st.session_state.reel_topic = f"{club} vs {opponent}"
            st.rerun()
    with c2:
        st.download_button(
            "↓ Paket",
            data=package_text.encode("utf-8"),
            file_name=f"viral_{club}_{opponent}.md",
            mime="text/markdown",
            key="fb_viral_dl",
            width="stretch",
        )
    with c3:
        st.caption("Publish Queue · Elite Automation")
