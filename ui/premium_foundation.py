"""Shared Premium SaaS UI — dark theme, upgrade cards, feature grid."""
from __future__ import annotations

import html

import streamlit as st

from config import FOOTBALL_PLANS, get_football_plan
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css


BETA_GLOBAL_CSS = """
div[data-testid="stAppViewContainer"] > section > div {
    background: transparent !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
}
.stDataFrame, [data-testid="stDataFrame"] {
    border-radius: 16px !important;
}
/* Sidebar nav styled in ui_core.py */
@media (max-width: 768px) {
    .mb-page-hero, .mb-hero {
        padding: 22px 20px !important;
    }
    .mb-hero-title, .mb-title {
        font-size: 32px !important;
    }
    .mb-feature-grid {
        grid-template-columns: 1fr !important;
    }
    section[data-testid="stSidebar"] {
        min-width: 100% !important;
    }
}
"""

PREMIUM_COMPONENT_CSS = """
.mb-page-hero {
    border-radius: 28px;
    padding: 28px 32px;
    margin-bottom: 22px;
    background:
        radial-gradient(circle at 88% 12%, rgba(168,85,247,.22), transparent 34%),
        radial-gradient(circle at 8% 0%, rgba(96,165,250,.14), transparent 32%),
        linear-gradient(135deg, rgba(12,18,42,.96), rgba(8,12,28,.98));
    border: 1px solid rgba(255,231,163,.12);
    box-shadow: 0 24px 60px rgba(0,0,0,.32);
}
.mb-kicker {
    color: #c084fc !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .2em;
    text-transform: uppercase;
}
.mb-hero-title {
    color: #ffe7a3 !important;
    font-size: 34px;
    font-weight: 1000;
    letter-spacing: -1.2px;
    margin-top: 8px;
    line-height: 1.05;
}
.mb-hero-sub {
    color: #94a3b8 !important;
    font-size: 15px;
    line-height: 1.55;
    max-width: 780px;
    margin-top: 10px;
}
.mb-upgrade-card {
    border-radius: 20px;
    padding: 20px 22px;
    margin-bottom: 12px;
    background: linear-gradient(135deg, rgba(30,20,50,.92), rgba(12,10,28,.96));
    border: 1px dashed rgba(255,231,163,.22);
}
.mb-upgrade-card.locked {
    opacity: .92;
}
.mb-upgrade-card h4 {
    color: #ffe7a3 !important;
    margin: 0 0 6px 0;
    font-size: 16px;
    font-weight: 1000;
}
.mb-upgrade-card p {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.5;
    margin: 0 0 10px 0;
}
.mb-upgrade-badge {
    display: inline-flex;
    padding: 5px 11px;
    border-radius: 999px;
    background: linear-gradient(135deg, #4c1d95, #312e81);
    color: #e9d5ff !important;
    font-size: 11px;
    font-weight: 1000;
}
.mb-feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
    margin: 12px 0 18px 0;
}
.mb-feature-chip {
    border-radius: 14px;
    padding: 12px 14px;
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(15,23,42,.65);
}
.mb-feature-chip.ok {
    border-color: rgba(34,197,94,.35);
    background: rgba(6,78,59,.25);
}
.mb-feature-chip.no {
    border-color: rgba(148,163,184,.15);
    background: rgba(15,23,42,.45);
}
.mb-feature-chip .lbl {
    color: #f8fafc !important;
    font-size: 13px;
    font-weight: 800;
}
.mb-feature-chip .st {
    font-size: 11px;
    margin-top: 4px;
    font-weight: 700;
}
.mb-feature-chip.ok .st { color: #86efac !important; }
.mb-feature-chip.no .st { color: #94a3b8 !important; }
.mb-ticket-card {
    border-radius: 22px;
    padding: 22px;
    background: linear-gradient(180deg, rgba(18,10,32,.96), rgba(10,8,20,.98));
    border: 1px solid rgba(255,255,255,.09);
}
.mb-status-badge {
    display: inline-flex;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.mb-badge-open {
    background: rgba(34,197,94,.22);
    color: #86efac !important;
    border: 1px solid rgba(34,197,94,.35);
}
.mb-badge-closed {
    background: rgba(100,116,139,.22);
    color: #cbd5e1 !important;
    border: 1px solid rgba(148,163,184,.28);
}
"""


def premium_foundation_css(
    max_width: int = 1180,
    padding_top: int = 80,
    extra_css: str = "",
) -> None:
    inject_css(
        MB_THEME_VARS
        + page_layout_css(max_width, padding_top, 42)
        + PREMIUM_COMPONENT_CSS
        + BETA_GLOBAL_CSS
        + (extra_css or "")
    )


def inject_beta_global_css() -> None:
    """Shared dark surfaces — call from ui_core.load_css once."""
    inject_css(MB_THEME_VARS + BETA_GLOBAL_CSS)


def render_status_badge(status: str) -> None:
    status = str(status or "open").strip().lower()
    if status == "in_progress":
        css_class = "mb-badge-open"
        label = "In Arbeit"
    elif status == "open":
        css_class = "mb-badge-open"
        label = "Offen"
    elif status == "closed":
        css_class = "mb-badge-closed"
        label = "Geschlossen"
    else:
        css_class = "mb-badge-closed"
        label = status.title()
    st.markdown(
        f'<span class="mb-status-badge {css_class}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, message: str) -> None:
    st.markdown(
        f"""
<div class="mb-upgrade-card">
    <h4>{html.escape(title)}</h4>
    <p>{html.escape(message)}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def stripe_config_status() -> tuple[bool, list[str]]:
    """Checkout needs STRIPE_SECRET_KEY + price IDs (webhook secret is separate service)."""
    import os

    from config import FOOTBALL_PLANS, PLANS

    missing: list[str] = []
    if not os.getenv("STRIPE_SECRET_KEY", "").strip():
        missing.append("STRIPE_SECRET_KEY")
    for _key, plan in {**PLANS, **FOOTBALL_PLANS}.items():
        if _key == "free":
            continue
        env_name = plan.get("stripe_price_env")
        if env_name and not os.getenv(env_name, "").strip():
            missing.append(env_name)
    return len(missing) == 0, missing


def plan_display_name(plan_key: str) -> str:
    if plan_key in FOOTBALL_PLANS:
        return FOOTBALL_PLANS[plan_key].get("label", plan_key)
    cfg = get_football_plan(plan_key)
    return (cfg or {}).get("label", plan_key) if cfg else plan_key


def render_page_hero(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="mb-page-hero">
    <div class="mb-kicker">{html.escape(kicker)}</div>
    <div class="mb-hero-title">{html.escape(title)}</div>
    <div class="mb-hero-sub">{html.escape(subtitle)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_upgrade_card(
    title: str,
    description: str,
    required_plan: str,
    *,
    button_key: str,
    on_upgrade=None,
) -> None:
    badge = plan_display_name(required_plan)
    st.markdown(
        f"""
<div class="mb-upgrade-card locked">
    <h4>{html.escape(title)}</h4>
    <p>{html.escape(description)}</p>
    <span class="mb-upgrade-badge">Ab {html.escape(badge)}</span>
</div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Upgrade auf {badge}", key=button_key, width="stretch"):
        if on_upgrade:
            on_upgrade()
        else:
            st.session_state.page = "premium"
            st.rerun()


def render_feature_chip(label: str, available: bool) -> str:
    state = "ok" if available else "no"
    status = "Inklusive" if available else "Upgrade"
    return f"""
<div class="mb-feature-chip {state}">
    <div class="lbl">{html.escape(label)}</div>
    <div class="st">{status}</div>
</div>
"""


def render_feature_grid(features: list[tuple[str, bool]]) -> None:
    chips = "".join(render_feature_chip(lbl, ok) for lbl, ok in features)
    st.markdown(
        f'<div class="mb-feature-grid">{chips}</div>',
        unsafe_allow_html=True,
    )
