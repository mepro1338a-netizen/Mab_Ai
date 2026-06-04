"""Shared MaByte UI helpers — nav, formatting, account dashboard blocks."""
from __future__ import annotations

import html

import streamlit as st

from config import DAILY_LIMITS, FOOTBALL_PLANS, PLANS
from database import list_usage, recent_activity
from ui.styles import inject_css, page_layout_css

_DASH_TOPBAR = 0


def nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def format_num(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


_DASHBOARD_CSS = f"""
.stApp:has(.mb-dash) section.main .block-container {{
    max-width: 1080px !important;
    padding-top: {_DASH_TOPBAR}px !important;
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
.mb-dash-head {{ margin: 0 0 16px 0; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,.06); }}
.mb-dash-kicker {{ color: rgba(192,132,252,.9)!important; font-size:10px; font-weight:800; letter-spacing:.2em; text-transform:uppercase; }}
.mb-dash-title {{ color:#f8fafc!important; font-size:clamp(22px,3.5vw,30px); font-weight:800; letter-spacing:-0.03em; margin:4px 0 0 0; line-height:1.2; }}
.mb-dash-sub {{ color:rgba(148,163,184,.95)!important; font-size:13px; line-height:1.45; margin:6px 0 0 0; max-width:640px; }}
.mb-dash-stats {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-bottom:14px; }}
@media (max-width:900px) {{ .mb-dash-stats {{ grid-template-columns:repeat(2,1fr); }} }}
.mb-dash-stat {{ border-radius:12px; padding:12px 14px; background:#18181b; border:1px solid #3f3f46; }}
.mb-dash-stat .lbl {{ color:rgba(148,163,184,.9)!important; font-size:10px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }}
.mb-dash-stat .val {{ color:#f8fafc!important; font-size:20px; font-weight:800; margin-top:4px; }}
.mb-dash-stat .hint {{ color:rgba(100,116,139,.95)!important; font-size:10px; margin-top:2px; }}
.mb-dash-section {{ color:rgba(196,181,253,.95)!important; font-size:10px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin:0 0 10px 0; }}
.mb-dash-limit {{ display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:13px; color:#cbd5e1!important; }}
.mb-dash-limit:last-child {{ border-bottom:none; }}
.mb-dash-act-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
.mb-dash-act {{ border-radius:12px; padding:10px 12px; background:rgba(8,10,22,.4); border:1px solid rgba(255,255,255,.05); }}
.mb-dash-act .t {{ color:#f1f5f9!important; font-size:13px; font-weight:700; }}
.mb-dash-act .d {{ color:#64748b!important; font-size:11px; margin-top:2px; }}
.mb-dash-empty {{ color:#64748b!important; font-size:13px; padding:4px 0; line-height:1.45; }}
.mb-pay-wrap {{ margin-top:4px; }}
.mb-pay-head {{
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  margin-bottom:14px;flex-wrap:wrap;
}}
.mb-pay-head .mb-dash-section {{ margin:0; }}
.mb-pay-upgrade {{
  display:inline-flex;align-items:center;padding:7px 14px;border-radius:999px;
  font-size:12px;font-weight:600;text-decoration:none!important;
  color:#e9d5ff!important;background:rgba(124,58,237,.2);
  border:1px solid rgba(139,92,246,.35);
}}
.mb-pay-upgrade:hover {{ background:rgba(124,58,237,.32); }}
.mb-pay-table {{
  width:100%;border-collapse:separate;border-spacing:0;
  border-radius:12px;overflow:hidden;
  border:1px solid rgba(255,255,255,.08);
}}
.mb-pay-table th {{
  text-align:left;padding:10px 14px;font-size:10px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:#71717a!important;
  background:rgba(0,0,0,.28);border-bottom:1px solid rgba(255,255,255,.06);
}}
.mb-pay-table td {{
  padding:12px 14px;font-size:13px;color:#e4e4e7!important;
  border-bottom:1px solid rgba(255,255,255,.05);vertical-align:middle;
}}
.mb-pay-table tr:last-child td {{ border-bottom:none; }}
.mb-pay-table tr:hover td {{ background:rgba(124,58,237,.06); }}
.mb-pay-plan {{ font-weight:700;color:#f4f4f5!important; }}
.mb-pay-meta {{ font-size:11px;color:#71717a!important;margin-top:2px; }}
.mb-pay-amt {{ font-weight:700;color:#fafafa!important;white-space:nowrap; }}
.mb-pay-date {{ color:#94a3b8!important;font-size:12px;white-space:nowrap; }}
.mb-pay-badge {{
  display:inline-block;padding:3px 10px;border-radius:999px;
  font-size:10px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
}}
.mb-pay-badge.paid {{ background:rgba(34,197,94,.15);color:#4ade80!important; }}
.mb-pay-badge.pending {{ background:rgba(113,113,122,.2);color:#a1a1aa!important; }}
.mb-pay-badge.created {{ background:rgba(234,179,8,.12);color:#facc15!important; }}
.mb-pay-badge.failed {{ background:rgba(239,68,68,.12);color:#f87171!important; }}
.mb-pay-empty {{
  padding:28px 20px;text-align:center;border-radius:14px;
  border:1px dashed rgba(255,255,255,.1);background:rgba(15,15,18,.5);
}}
.mb-pay-empty .t {{ color:#e4e4e7!important;font-size:14px;font-weight:600;margin:0 0 6px; }}
.mb-pay-empty .d {{ color:#64748b!important;font-size:12px;line-height:1.5;margin:0; }}
"""


def inject_dashboard_css() -> None:
    inject_css(page_layout_css(1080, _DASH_TOPBAR, 48) + _DASHBOARD_CSS)


def render_header(*, user: str, greeting: str = "") -> None:
    sub = greeting or f"Hallo {html.escape(user)} — Account, Tokens und Limits."
    st.markdown(
        f"""
<div class="mb-dash-head">
  <div class="mb-dash-kicker">Account</div>
  <div class="mb-dash-title">Profil</div>
  <p class="mb-dash-sub">{sub}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(*, plan_label: str, tokens: int, football_label: str, tier: str) -> None:
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
    st.markdown(f'<div class="mb-dash-section">Tageslimits</div>{lr}', unsafe_allow_html=True)


def render_recent_activity(username: str, *, limit: int = 8) -> None:
    items = recent_activity(username=username, limit=limit)
    if not items:
        items = list_usage(username)[:limit]
    st.markdown('<div class="mb-dash-section">Letzte Aktivität</div>', unsafe_allow_html=True)
    if not items:
        st.markdown(
            '<p class="mb-dash-empty">Noch keine Aktivität — starte mit AI Chat oder Creator.</p>',
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
    st.markdown(f'<div class="mb-dash-act-grid">{"".join(blocks)}</div>', unsafe_allow_html=True)


def _plan_label(plan_key: str) -> str:
    key = (plan_key or "").strip()
    if key in PLANS:
        return str(PLANS[key].get("label", key))
    if key in FOOTBALL_PLANS:
        return str(FOOTBALL_PLANS[key].get("label", key))
    return key.replace("_", " ").title() if key else "—"


def _plan_price(plan_key: str) -> str:
    key = (plan_key or "").strip()
    meta = PLANS.get(key) or FOOTBALL_PLANS.get(key)
    if not meta:
        return "—"
    price = str(meta.get("price") or "").strip()
    if price:
        return price.split(" / ")[0]
    monthly = meta.get("monthly_price")
    if monthly:
        return f"{float(monthly):.2f} €".replace(".", ",")
    return "—"


def _amount_display(row: dict, plan_key: str) -> str:
    amt = int(row.get("amount") or 0)
    if amt >= 100:
        return f"{amt / 100:.2f} €".replace(".", ",")
    if amt > 0:
        return f"{amt} €"
    return _plan_price(plan_key)


def _format_payment_date(raw: str) -> str:
    s = (raw or "").strip()
    if len(s) >= 16 and "T" in s:
        d, t = s[:10], s[11:16]
        try:
            y, m, day = d.split("-")
            return f"{day}.{m}.{y} · {t}"
        except ValueError:
            pass
    return s[:16] if s else "—"


def _payment_status_badge(row: dict) -> tuple[str, str]:
    status = str(row.get("status") or row.get("payment_status") or "").strip().lower()
    if status in ("paid", "complete", "completed", "succeeded"):
        return "paid", "Bezahlt"
    if status in ("failed", "canceled", "cancelled"):
        return "failed", "Fehlgeschlagen"
    if status in ("created", "open"):
        return "created", "Offen"
    if status in ("pending", "processing"):
        return "pending", "Ausstehend"
    if status:
        return "pending", status.replace("_", " ").title()
    return "pending", "Ausstehend"


def render_payments(username: str, *, purchases: list[dict] | None = None) -> None:
    """Styled payment history for the profile page."""
    from database import list_purchases

    rows = purchases if purchases is not None else list_purchases(username)

    st.markdown(
        """
<div class="mb-pay-wrap">
  <div class="mb-pay-head">
    <div class="mb-dash-section">Zahlungen</div>
    <a class="mb-pay-upgrade" href="?nav=premium">Plan verwalten</a>
  </div>
        """,
        unsafe_allow_html=True,
    )

    if not rows:
        st.markdown(
            """
<div class="mb-pay-empty">
  <p class="t">Noch keine Zahlungen</p>
  <p class="d">Nach einem Upgrade über Stripe erscheinen deine Rechnungen hier.</p>
</div>
</div>
            """,
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
            f'<td><div class="mb-pay-plan">{html.escape(plan_name)}</div>'
            f'<div class="mb-pay-meta">{meta}</div></td>'
            f'<td class="mb-pay-amt">{html.escape(amount_txt)}</td>'
            f'<td class="mb-pay-date">{html.escape(when)}</td>'
            f'<td><span class="mb-pay-badge {cls}">{html.escape(label)}</span></td>'
            "</tr>"
        )

    st.markdown(
        f"""
<table class="mb-pay-table">
  <thead><tr>
    <th>Plan</th><th>Betrag</th><th>Datum</th><th>Status</th>
  </tr></thead>
  <tbody>{"".join(body)}</tbody>
</table>
</div>
        """,
        unsafe_allow_html=True,
    )
