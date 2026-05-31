"""Elite Betting Intelligence Card UI — minimal decision-first layout."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui.premium_foundation import render_upgrade_card
from ui.styles import inject_css

BETTING_CARD_CSS = """
.fb-bet-card {
    border-radius: 20px;
    padding: 20px 22px;
    margin: 12px 0;
    background: linear-gradient(155deg, rgba(12,18,32,.97), rgba(8,12,24,.99));
    border: 1px solid rgba(168,85,247,.28);
    box-shadow: 0 16px 48px rgba(0,0,0,.35);
}
.fb-bet-card.no-bet {
    border-color: rgba(100,116,139,.35);
}
.fb-bet-match {
    color: #f8fafc !important;
    font-size: 20px;
    font-weight: 900;
    margin: 0 0 4px 0;
}
.fb-bet-meta {
    color: #64748b !important;
    font-size: 12px;
    margin: 0 0 16px 0;
}
.fb-bet-pick {
    font-size: 22px;
    font-weight: 1000;
    color: #ffe7a3 !important;
    margin: 0 0 10px 0;
    line-height: 1.25;
}
.fb-bet-pick.no-bet {
    color: #94a3b8 !important;
    font-size: 18px;
}
.fb-bet-metrics {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 12px 0;
}
.fb-bet-metric {
    padding: 8px 14px;
    border-radius: 10px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(255,255,255,.08);
    min-width: 88px;
}
.fb-bet-metric .k {
    color: #64748b !important;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .1em;
}
.fb-bet-metric .v {
    color: #f0fdf4 !important;
    font-size: 16px;
    font-weight: 900;
    margin-top: 2px;
}
.fb-bet-metric.risk-low .v { color: #86efac !important; }
.fb-bet-metric.risk-mid .v { color: #fde68a !important; }
.fb-bet-metric.risk-high .v { color: #fca5a5 !important; }
.fb-bet-reasons {
    margin: 14px 0 0 0;
    padding: 0;
    list-style: none;
}
.fb-bet-reasons li {
    color: #cbd5e1 !important;
    font-size: 13px;
    padding: 6px 0 6px 14px;
    border-left: 2px solid rgba(34,197,94,.35);
    margin-bottom: 4px;
}
.fb-bet-disclaimer {
    color: #475569 !important;
    font-size: 10px;
    margin-top: 14px;
    line-height: 1.4;
}
.fb-bet-inj {
    margin-top: 12px;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(127,29,29,.12);
    border: 1px solid rgba(248,113,113,.2);
}
.fb-bet-inj h4 {
    color: #fca5a5 !important;
    font-size: 11px;
    margin: 0 0 8px 0;
    text-transform: uppercase;
    letter-spacing: .1em;
}
.fb-bet-inj p {
    color: #e2e8f0 !important;
    font-size: 12px;
    margin: 4px 0;
}
.fb-bet-value {
    margin-top: 14px;
    padding: 14px;
    border-radius: 12px;
    background: rgba(22,101,52,.12);
    border: 1px solid rgba(34,197,94,.25);
}
.fb-bet-value.bad {
    background: rgba(30,27,75,.2);
    border-color: rgba(168,85,247,.2);
}
.fb-bet-prob-bar {
    display: flex;
    gap: 8px;
    margin: 10px 0;
}
.fb-bet-prob {
    flex: 1;
    text-align: center;
    padding: 8px 6px;
    border-radius: 8px;
    background: rgba(0,0,0,.3);
    border: 1px solid rgba(255,255,255,.06);
}
.fb-bet-prob strong {
    display: block;
    color: #f8fafc !important;
    font-size: 15px;
}
.fb-bet-prob span {
    color: #64748b !important;
    font-size: 10px;
}
"""


def inject_betting_card_css() -> None:
    inject_css(BETTING_CARD_CSS)


def _risk_class(risk: str) -> str:
    if risk == "Niedrig":
        return "risk-low"
    if risk == "Hoch":
        return "risk-high"
    return "risk-mid"


def _disclaimer() -> None:
    st.markdown(
        '<p class="fb-bet-disclaimer">'
        "Keine Finanzberatung. Datenbasierte Einschätzung, keine Garantie."
        "</p>",
        unsafe_allow_html=True,
    )


def _render_live_events(detail: dict[str, Any], bundle: dict[str, Any] | None) -> None:
    card = detail.get("card") or {}
    if not card.get("live"):
        return

    lines: list[str] = []
    if bundle:
        mom = (bundle.get("overview") or {}).get("momentum") or {}
        label = mom.get("label") or ""
        leader = mom.get("leader") or ""
        if label:
            lines.append(f"Momentum: {label}" + (f" ({leader})" if leader else ""))

    events = detail.get("events") or []
    shown = 0
    for block in events:
        nested = block.get("events")
        ev_list = nested if nested else ([block] if block.get("type") or block.get("time") else [])
        for ev in ev_list:
            if shown >= 5:
                break
            minute = (ev.get("time") or {}).get("elapsed")
            typ = str(ev.get("type") or "")
            player = (ev.get("player") or {}).get("name") or ""
            detail_txt = ev.get("detail") or ""
            if typ.lower() in ("goal", "card", "subst"):
                lines.append(f"{minute}' {typ} {player} {detail_txt}".strip())
                shown += 1

    if lines:
        st.markdown(
            '<div class="fb-bet-inj" style="border-color:rgba(34,197,94,.25);background:rgba(22,101,52,.12);">'
            '<h4 style="color:#86efac!important;">Live-Analyse</h4>'
            + "".join(f"<p>{html.escape(l)}</p>" for l in lines)
            + "</div>",
            unsafe_allow_html=True,
        )


def render_compact_intelligence_card(
    intel: dict[str, Any],
    detail: dict[str, Any],
    *,
    bundle: dict[str, Any] | None = None,
) -> None:
    """Premium compact card — decision-first, minimal text."""
    inject_betting_card_css()
    h = intel.get("header") or {}
    rec = intel.get("recommendation") or {}
    no_bet = bool(rec.get("no_bet"))
    pick_cls = "fb-bet-pick no-bet" if no_bet else "fb-bet-pick"
    card_cls = "fb-bet-card no-bet" if no_bet else "fb-bet-card"
    status = html.escape(str(h.get("status") or "NS"))
    form = intel.get("form") or {}
    h2h = intel.get("h2h") or ""
    outcome = rec.get("outcome") or ""
    outcome_conf = rec.get("outcome_confidence")
    outcome_line = ""
    if outcome:
        oc = f" · {float(outcome_conf):.0f}%" if outcome_conf is not None else ""
        outcome_line = f'<p style="color:#94a3b8;font-size:13px;margin:0 0 8px 0;">Ergebnis: <strong style="color:#e2e8f0;">{html.escape(str(outcome))}</strong>{oc}</p>'

    st.markdown(
        f"""
<div class="{card_cls}">
    <p class="fb-bet-match">{html.escape(str(h.get('home')))} vs {html.escape(str(h.get('away')))}</p>
    <p class="fb-bet-meta">{html.escape(str(h.get('league')))} · <strong>{html.escape(str(h.get('score')))}</strong> · {html.escape(str(h.get('time') or h.get('date')))} · {status}</p>
    {outcome_line}
    <p class="{pick_cls}">{html.escape(str(rec.get('main_pick', '—')))}</p>
    <div class="fb-bet-metrics">
        <div class="fb-bet-metric"><div class="k">Konfidenz</div><div class="v">{rec.get('confidence', 0):.0f}%</div></div>
        <div class="fb-bet-metric {_risk_class(str(rec.get('risk', 'Mittel')))}"><div class="k">Risiko</div><div class="v">{html.escape(str(rec.get('risk', '—')))}</div></div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    reasons = intel.get("reasons_short") or []
    if reasons:
        items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons[:3])
        st.markdown(f'<ul class="fb-bet-reasons">{items}</ul>', unsafe_allow_html=True)

    meta_lines = []
    if form.get("home") or form.get("away"):
        meta_lines.append(
            f"Form (5): {html.escape(str(form.get('home', '—')))} · {html.escape(str(form.get('away', '—')))}"
        )
    if h2h:
        meta_lines.append(f"H2H: {html.escape(h2h)}")
    if meta_lines:
        st.markdown(
            f'<p style="color:#94a3b8;font-size:12px;margin:8px 0 0 0;">{" · ".join(meta_lines)}</p>',
            unsafe_allow_html=True,
        )

    inj = intel.get("injuries") or {}
    if inj.get("available"):
        st.markdown(
            f'<p style="color:#fca5a5;font-size:12px;margin:6px 0 0 0;">'
            f"Verletzungen: Heim {html.escape(str(inj.get('home_impact')))} · "
            f"Auswärts {html.escape(str(inj.get('away_impact')))}</p>",
            unsafe_allow_html=True,
        )
    _render_live_events(detail, bundle)
    _disclaimer()


def render_starter_fixture_card(detail: dict[str, Any]) -> None:
    card = detail.get("card") or {}
    st.markdown(
        f"""
<div class="fb-bet-card">
    <p class="fb-bet-match">{html.escape(str(card.get('home')))} vs {html.escape(str(card.get('away')))}</p>
    <p class="fb-bet-meta">{html.escape(str(card.get('league')))} · {html.escape(str(card.get('score')))} · {html.escape(str(card.get('time') or card.get('date')))}</p>
    <p style="color:#94a3b8;font-size:13px;margin:0;">Fixtures & Ergebnisse — AI-Tipps ab Football Pro.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    _disclaimer()


def render_pro_preview_card(preview: dict[str, Any]) -> None:
    inject_betting_card_css()
    h = preview.get("header") or {}
    pred = preview.get("prediction") or {}
    st.markdown(
        f"""
<div class="fb-bet-card">
    <p class="fb-bet-match">{html.escape(str(h.get('home')))} vs {html.escape(str(h.get('away')))}</p>
    <p class="fb-bet-meta">{html.escape(str(h.get('league')))} · {html.escape(str(h.get('score')))}</p>
    <p style="color:#86efac;font-size:12px;font-weight:800;margin:0 0 10px 0;">KI-VORSCHAU · PRO</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for i, (lbl, key) in enumerate((("Heim", "home_pct"), ("Remis", "draw_pct"), ("Ausw.", "away_pct"))):
        val = pred.get(key)
        cols[i].markdown(
            f'<div class="fb-bet-prob"><strong>{val:.0f}%</strong><span>{lbl}</span></div>'
            if val is not None
            else f'<div class="fb-bet-prob"><strong>—</strong><span>{lbl}</span></div>',
            unsafe_allow_html=True,
        )
    if pred.get("advice"):
        st.caption(f"API: {pred.get('advice')}")
    reasons = preview.get("reasons_short") or []
    if reasons:
        items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons)
        st.markdown(f'<ul class="fb-bet-reasons">{items}</ul>', unsafe_allow_html=True)
    _disclaimer()


def render_elite_betting_card(
    intel: dict[str, Any],
    *,
    fixture_id: int,
    show_details: bool = False,
) -> None:
    inject_betting_card_css()
    h = intel.get("header") or {}
    rec = intel.get("recommendation") or {}
    no_bet = bool(rec.get("no_bet"))
    pick_cls = "fb-bet-pick no-bet" if no_bet else "fb-bet-pick"
    card_cls = "fb-bet-card no-bet" if no_bet else "fb-bet-card"
    live_badge = " · LIVE" if h.get("live") else ""

    st.markdown(
        f"""
<div class="{card_cls}">
    <p class="fb-bet-match">{html.escape(str(h.get('home')))} vs {html.escape(str(h.get('away')))}</p>
    <p class="fb-bet-meta">{html.escape(str(h.get('league')))}{live_badge} · {html.escape(str(h.get('time') or h.get('date')))} · <strong>{html.escape(str(h.get('score')))}</strong></p>
    <p class="{pick_cls}">{html.escape(str(rec.get('main_pick', '—')))}</p>
    <div class="fb-bet-metrics">
        <div class="fb-bet-metric"><div class="k">Konfidenz</div><div class="v">{rec.get('confidence', 0):.0f}%</div></div>
        <div class="fb-bet-metric {_risk_class(str(rec.get('risk', 'Mittel')))}"><div class="k">Risiko</div><div class="v">{html.escape(str(rec.get('risk', '—')))}</div></div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    reasons = intel.get("reasons_full") if show_details else intel.get("reasons_short") or []
    if reasons:
        items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons)
        st.markdown(f'<ul class="fb-bet-reasons">{items}</ul>', unsafe_allow_html=True)

    if show_details:
        inj = intel.get("injuries") or {}
        if inj.get("available"):
            home_lines = inj.get("home") or []
            away_lines = inj.get("away") or []
            body = ""
            for side, rows, imp in (
                ("Heim", home_lines, inj.get("home_impact")),
                ("Auswärts", away_lines, inj.get("away_impact")),
            ):
                if rows:
                    names = ", ".join(
                        f"{html.escape(r.get('player', ''))} ({html.escape(r.get('reason', ''))})"
                        for r in rows[:4]
                    )
                    body += f"<p><strong>{side}</strong> · Impact {html.escape(str(imp))}: {names}</p>"
            st.markdown(f'<div class="fb-bet-inj"><h4>Verletzungsimpact</h4>{body}</div>', unsafe_allow_html=True)
        elif inj.get("missing"):
            st.caption("Verletzungsdaten derzeit nicht von der API geliefert.")

        gaps = intel.get("data_gaps") or []
        if gaps:
            st.caption(f"Optional nicht geladen: {', '.join(gaps)}")

    _disclaimer()


def render_value_quote_input(
    intel: dict[str, Any],
    *,
    key_prefix: str,
) -> dict[str, Any] | None:
    """Elite value calculator — returns updated value block."""
    pred = intel.get("prediction") or {}
    default_p = float(pred.get("home_pct") or 50.0)
    c1, c2 = st.columns(2)
    with c1:
        odd = st.number_input(
            "Deine Quote",
            min_value=1.01,
            max_value=50.0,
            value=float(st.session_state.get(f"{key_prefix}_odd", 2.1)),
            step=0.01,
            key=f"{key_prefix}_odd_in",
        )
    with c2:
        prob = st.number_input(
            "AI-Wahrscheinlichkeit %",
            min_value=1.0,
            max_value=99.0,
            value=float(st.session_state.get(f"{key_prefix}_prob", default_p)),
            step=0.5,
            key=f"{key_prefix}_prob_in",
        )
    from services.football_odds import calculate_tip_odds

    core = calculate_tip_odds(float(odd), 10.0, float(prob))
    cls = "fb-bet-value" if core["is_value_bet"] else "fb-bet-value bad"
    st.markdown(
        f"""
<div class="{cls}">
    <div style="color:#86efac;font-size:11px;font-weight:800;letter-spacing:.1em;">VALUE-CHECK</div>
    <p style="color:#e2e8f0;font-size:13px;margin:8px 0 0 0;">
        Implizit: <strong>{core['implied_probability_pct']:.1f}%</strong> ·
        AI: <strong>{prob:.1f}%</strong> ·
        Edge: <strong>{core['edge_pct']:+.1f}%</strong> ·
        EV: <strong>{core['expected_value']:+.2f}</strong>
    </p>
    <p style="color:#ffe7a3;font-weight:800;margin:6px 0 0 0;">{html.escape(str(core['value_label']))}</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    return {
        "user_odd": float(odd),
        "implied_pct": core["implied_probability_pct"],
        "ai_pct": float(prob),
        "edge_pct": core["edge_pct"],
        "expected_value": core["expected_value"],
        "verdict": core["value_label"],
        "is_value": core["is_value_bet"],
    }


def render_match_intelligence_section(
    detail: dict[str, Any],
    *,
    fixture_id: int,
    rank: int,
    elite_ok: bool,
    pro_ok: bool,
    open_premium,
    username: str = "",
    session_plan: str = "none",
) -> None:
    """Plan-gated betting intelligence for Live Match Center."""
    if rank < 1:
        return

    if rank == 1:
        render_starter_fixture_card(detail)
        hs = detail.get("home_standing") or {}
        aws = detail.get("away_standing") or {}
        if hs or aws:
            st.caption(
                f"Tabellen: Heim #{hs.get('rank', '—')} · Ausw. #{aws.get('rank', '—')}"
            )
        render_upgrade_card(
            "Pro Match Intelligence",
            "H2H, Form, AI Preview & Predictions ab Football Pro.",
            "football_pro",
            button_key=f"fb_bet_up_{fixture_id}",
            on_upgrade=open_premium,
        )
        return

    from services.football_elite_betting_card import build_betting_intelligence_card, build_pro_preview_card

    bundle = st.session_state.get(f"fb_mc_elite_{fixture_id}")

    from ui.football_match_analysis import render_match_analysis_panel

    if elite_ok:
        intel = detail.get("intel") or build_betting_intelligence_card(detail, bundle=bundle)
        render_compact_intelligence_card(intel, detail, bundle=bundle)
        render_match_analysis_panel(
            detail, intel, live_bundle=bundle, include_reasoning=False
        )
        render_value_quote_input(intel, key_prefix=f"fb_vq_{fixture_id}")

        if detail.get("card", {}).get("live") and not bundle:
            if st.button("Live Momentum laden", key=f"fb_mc_elite_load_{fixture_id}", width="stretch"):
                from services.football_access import can_run_action, consume_action
                from services.football_elite_live import EliteLiveIntelEngine
                from services.football_service import get_football_service

                ok_run, msg = can_run_action(username, "deep_match_analysis", session_plan)
                if not ok_run:
                    st.error(msg)
                else:
                    try:
                        consume_action(username, "deep_match_analysis", session_plan)
                        bundle = EliteLiveIntelEngine(get_football_service()).fetch_bundle(
                            fixture_id,
                            username=username,
                        )
                        st.session_state[f"fb_mc_elite_{fixture_id}"] = bundle
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        plat = st.selectbox(
            "Plattform",
            ["TikTok", "YouTube Shorts", "Instagram Reels"],
            key=f"fb_reel_plat_{fixture_id}",
            label_visibility="collapsed",
        )
        if st.button("Aus Analyse Reel erzeugen", key=f"fb_reel_{fixture_id}", width="stretch"):
            from services.football_creator_bridge import build_reel_template_from_intel

            tpl = build_reel_template_from_intel(detail, intel, platform=plat)
            st.session_state[f"fb_reel_tpl_{fixture_id}"] = tpl
            st.session_state.reel_topic = f"{tpl['home']} vs {tpl['away']}"
            st.session_state.page = "reels"
            st.success(tpl["status_note"])

        tpl = st.session_state.get(f"fb_reel_tpl_{fixture_id}")
        if tpl:
            with st.expander("Reel-Vorlage", expanded=False):
                st.markdown(tpl.get("package", ""))

    elif pro_ok:
        preview = build_pro_preview_card(detail)
        intel = detail.get("intel") or build_betting_intelligence_card(detail)
        render_pro_preview_card(preview)
        render_match_analysis_panel(detail, intel, include_reasoning=True)
        _render_live_events(detail, None)
        render_upgrade_card(
            "Elite Betting Intelligence",
            "Haupttipp, Value-Quote, Live Momentum & Creator Reel Bridge ab Elite.",
            "football_elite",
            button_key=f"fb_bet_elite_{fixture_id}",
            on_upgrade=open_premium,
        )
    else:
        render_starter_fixture_card(detail)
