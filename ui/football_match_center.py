"""Live Match Center UI — trading-terminal style cards and panels."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from services.football_match_center import parse_match_card
from ui.football_ui import render_standings_table
from ui.styles import inject_css

MATCH_CENTER_CSS = """
.fb-mc-header {
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 16px;
    background:
        radial-gradient(ellipse 70% 80% at 100% 0%, rgba(139,92,246,.18), transparent 55%),
        linear-gradient(135deg, rgba(8,14,24,.98), rgba(6,10,18,.99));
    border: 1px solid rgba(255,255,255,.08);
}
.fb-mc-title {
    color: #fafafa !important;
    font-size: 24px;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.02em;
}
.fb-mc-sub {
    color: #71717a !important;
    font-size: 12px;
    margin: 6px 0 0 0;
    line-height: 1.45;
}
.fb-mc-ticker {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 14px 0 0 0;
}
.fb-mc-stat {
    padding: 8px 14px;
    border-radius: 12px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(134,239,172,.15);
    color: #86efac !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.fb-mc-stat strong {
    color: #f0fdf4 !important;
    font-size: 16px;
    display: block;
    margin-top: 2px;
    letter-spacing: 0;
    text-transform: none;
}
.fb-mc-section {
    margin: 24px 0 10px 0;
    color: #a1a1aa !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
}
.fb-mc-top-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
    margin-bottom: 8px;
}
.fb-mc-top-row .fb-mc-card {
    border-color: rgba(139,92,246,.25);
    background: linear-gradient(145deg, rgba(18,16,32,.97), rgba(10,10,18,.98));
}
.fb-mc-top-row .fb-mc-card.featured {
    border-color: rgba(255,231,163,.35);
    box-shadow: 0 16px 48px rgba(0,0,0,.32);
}
.fb-mc-tip-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 8px;
}
@media (max-width: 960px) {
    .fb-mc-tip-grid { grid-template-columns: 1fr; }
}
.fb-mc-tip-mini {
    border-radius: 16px;
    padding: 16px;
    background: linear-gradient(160deg, rgba(14,18,32,.96), rgba(8,10,20,.98));
    border: 1px solid rgba(139,92,246,.22);
    min-height: 180px;
}
.fb-mc-tip-mini .match {
    color: #f4f4f5 !important;
    font-size: 14px;
    font-weight: 800;
    margin: 0 0 4px 0;
    line-height: 1.3;
}
.fb-mc-tip-mini .liga {
    color: #71717a !important;
    font-size: 10px;
    margin: 0 0 10px 0;
}
.fb-mc-tip-mini .pick {
    color: #fde68a !important;
    font-size: 15px;
    font-weight: 900;
    margin: 0 0 8px 0;
}
.fb-mc-tip-mini .metrics {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 8px 0;
}
.fb-mc-tip-mini .chip {
    padding: 4px 8px;
    border-radius: 6px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(255,255,255,.06);
    color: #d4d4d8 !important;
    font-size: 10px;
    font-weight: 700;
}
.fb-mc-empty-state {
    border-radius: 16px;
    padding: 22px 24px;
    margin: 8px 0 12px 0;
    background: rgba(18,18,24,.85);
    border: 1px solid rgba(255,255,255,.08);
    color: #a1a1aa !important;
    font-size: 14px;
    line-height: 1.5;
}
.fb-mc-empty-state strong {
    color: #fafafa !important;
    display: block;
    margin-bottom: 6px;
    font-size: 15px;
}
.fb-mc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
    margin-bottom: 8px;
}
.fb-mc-grid.featured-first .fb-mc-card.featured {
    grid-column: span 1;
}
@media (min-width: 900px) {
    .fb-mc-grid.featured-first .fb-mc-card.featured {
        grid-column: span 2;
        padding: 20px 22px;
    }
    .fb-mc-grid.featured-first .fb-mc-card.featured .fb-mc-score {
        font-size: 22px;
    }
}
.fb-mc-card {
    border-radius: 16px;
    padding: 12px 14px;
    background: linear-gradient(145deg, rgba(12,18,32,.95), rgba(6,10,22,.98));
    border: 1px solid rgba(255,255,255,.08);
    cursor: default;
}
.fb-mc-card.featured {
    border-color: rgba(255,231,163,.28);
    background: linear-gradient(145deg, rgba(18,24,42,.97), rgba(10,14,28,.98));
    box-shadow: 0 12px 40px rgba(0,0,0,.28);
}
.fb-mc-card.live {
    border-color: rgba(34,197,94,.5);
    box-shadow: 0 0 28px rgba(34,197,94,.15);
}
.fb-mc-card.live.featured {
    border-color: rgba(34,197,94,.65);
    box-shadow: 0 0 36px rgba(34,197,94,.22);
}
.fb-mc-live-stats {
    color: #86efac !important;
    font-size: 11px;
    margin-top: 8px;
    line-height: 1.35;
}
.fb-mc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}
.fb-mc-league-row {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}
.fb-mc-league-logo {
    width: 20px;
    height: 20px;
    object-fit: contain;
    flex-shrink: 0;
}
.fb-mc-league {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.fb-mc-time {
    color: #64748b !important;
    font-size: 11px;
    font-weight: 700;
}
.fb-mc-teams {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 10px;
    align-items: center;
}
.fb-mc-team-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}
.fb-mc-team-cell.away {
    flex-direction: row-reverse;
    text-align: right;
}
.fb-mc-team-logo {
    width: 28px;
    height: 28px;
    object-fit: contain;
    flex-shrink: 0;
}
.fb-mc-team {
    color: #f8fafc !important;
    font-size: 13px;
    font-weight: 800;
    line-height: 1.3;
}
.fb-mc-team.away { text-align: right; }
.fb-mc-score {
    min-width: 72px;
    text-align: center;
    padding: 8px 10px;
    border-radius: 12px;
    background: rgba(0,0,0,.4);
    border: 1px solid rgba(255,231,163,.12);
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
}
.fb-mc-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    gap: 8px;
}
.fb-mc-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.fb-mc-badge.live { background: rgba(34,197,94,.22); color: #86efac !important; }
.fb-mc-badge.ns { background: rgba(100,116,139,.25); color: #cbd5e1 !important; }
.fb-mc-badge.ft { background: rgba(59,130,246,.2); color: #93c5fd !important; }
.fb-mc-badge.ht { background: rgba(234,179,8,.18); color: #fde68a !important; }
.fb-mc-venue {
    color: #475569 !important;
    font-size: 10px;
    text-align: right;
    flex: 1;
}
.fb-mc-cat-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}
.fb-mc-cat {
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid rgba(168,85,247,.25);
    background: rgba(15,23,42,.7);
    color: #cbd5e1 !important;
    font-size: 12px;
    font-weight: 800;
}
.fb-mc-cat.active {
    border-color: rgba(34,197,94,.45);
    background: rgba(22,101,52,.35);
    color: #86efac !important;
}
.fb-mc-detail {
    border-radius: 22px;
    padding: 22px 24px;
    margin-top: 18px;
    background: linear-gradient(160deg, rgba(14,18,36,.96), rgba(8,12,24,.98));
    border: 1px solid rgba(168,85,247,.18);
}
.fb-mc-detail h3 {
    color: #f0fdf4 !important;
    font-size: 18px;
    font-weight: 900;
    margin: 0 0 12px 0;
}
.fb-mc-kv {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
    margin: 12px 0;
}
.fb-mc-kv div {
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(0,0,0,.28);
    border: 1px solid rgba(255,255,255,.06);
}
.fb-mc-kv .lbl { color: #64748b !important; font-size: 10px; font-weight: 800; text-transform: uppercase; }
.fb-mc-kv .val { color: #f8fafc !important; font-size: 14px; font-weight: 800; margin-top: 4px; }
.fb-mc-pro-lock {
    border-radius: 16px;
    padding: 16px 18px;
    margin-top: 12px;
    border: 1px dashed rgba(168,85,247,.35);
    color: #94a3b8 !important;
    font-size: 13px;
}
.fb-mc-empty-premium {
    border-radius: 18px;
    padding: 20px 22px;
    margin: 8px 0 16px 0;
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(100,116,139,.25);
    color: #cbd5e1 !important;
    font-size: 14px;
    line-height: 1.5;
}
.fb-mc-empty-few {
    border-radius: 14px;
    padding: 14px 16px;
    margin: 10px 0 4px 0;
    background: rgba(15, 23, 42, 0.65);
    border: 1px dashed rgba(148, 163, 184, 0.28);
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.45;
}
.fb-mc-empty-few strong { color: #cbd5e1 !important; }
.fb-mc-card-wrap {
    margin-bottom: 4px;
}
@media (max-width: 768px) {
    .fb-mc-grid { grid-template-columns: 1fr; }
    .fb-mc-title { font-size: 22px; }
}
"""


def inject_match_center_css() -> None:
    inject_css(MATCH_CENTER_CSS)


def _badge_class(status: str) -> str:
    if status in ("1H", "2H", "ET", "P", "LIVE", "BT"):
        return "live"
    if status == "HT":
        return "ht"
    if status == "FT":
        return "ft"
    return "ns"


def render_mc_header(*, live_count: int, today_count: int, api_used: int, api_limit: int) -> None:
    st.markdown(
        f"""
<div class="fb-mc-header">
    <h2 class="fb-mc-title">Football AI Intelligence</h2>
    <p class="fb-mc-sub">Premium-first · Bundesliga · UEFA · Topligen · Kein Low-Tier-Rauschen</p>
    <div class="fb-mc-ticker">
        <span class="fb-mc-stat">Live<strong>{live_count}</strong></span>
        <span class="fb-mc-stat">Premium heute<strong>{today_count}</strong></span>
        <span class="fb-mc-stat">API<strong>{api_used:,}/{api_limit:,}</strong></span>
    </div>
</div>
        """.replace(",", "."),
        unsafe_allow_html=True,
    )


def render_section_title(title: str) -> None:
    st.markdown(f'<p class="fb-mc-section">{html.escape(title)}</p>', unsafe_allow_html=True)


def render_few_top_matches_note() -> None:
    st.markdown(
        '<div class="fb-mc-empty-few"><strong>Keine weiteren Topspiele heute.</strong> '
        "Nur ein Premium-Match gelistet — weitere Ligen per Button unten.</div>",
        unsafe_allow_html=True,
    )


def render_empty_top_matches(*, show_intl_hint: bool = False, raw_live: int = 0) -> None:
    extra = ""
    if show_intl_hint and raw_live:
        extra = f" Es laufen {raw_live} Spiele in kleineren Ligen."
    st.markdown(
        f"""
<div class="fb-mc-empty-state">
    <strong>Heute keine Topspiele verfügbar.</strong>
    In Premium-Ligen (Bundesliga, UEFA, Topligen) sind heute keine Partien gelistet.{extra}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_top_matches_row(
    fixtures: list[dict[str, Any]],
    *,
    key_prefix: str = "top",
    selected_fixture: int | None = None,
) -> None:
    if not fixtures:
        return
    cards_html = []
    for fx in fixtures[:5]:
        card = parse_match_card(fx)
        card["featured"] = True
        cards_html.append(_render_match_card_html(card))
    st.markdown(f'<div class="fb-mc-top-row">{"".join(cards_html)}</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(fixtures[:5]), 5))
    for i, fx in enumerate(fixtures[:5]):
        fid = (fx.get("fixture") or {}).get("id")
        if not fid:
            continue
        try:
            fid_int = int(fid)
        except (TypeError, ValueError):
            continue
        with cols[i]:
            btn_type = "primary" if selected_fixture == fid_int else "secondary"
            if st.button("Analyse", key=f"{key_prefix}_sel_{fid_int}", type=btn_type, width="stretch"):
                st.session_state.fb_mc_selected_fixture = fid_int
                st.session_state.pop(f"fb_bet_details_{fid_int}", None)
                st.rerun()


def render_category_chips(categories: dict[str, str], active: str) -> None:
    chips = []
    for key, label in categories.items():
        cls = "fb-mc-cat active" if key == active else "fb-mc-cat"
        chips.append(f'<span class="{cls}">{html.escape(label)}</span>')
    st.markdown(f'<div class="fb-mc-cat-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def _logo_img(url: str, alt: str, css_class: str) -> str:
    if not url:
        return ""
    safe_url = html.escape(str(url), quote=True)
    safe_alt = html.escape(alt)
    return f'<img src="{safe_url}" alt="{safe_alt}" class="{css_class}" loading="lazy" />'


def _render_match_card_html(card: dict[str, Any]) -> str:
    live_cls = " live" if card.get("live") else ""
    featured_cls = " featured" if card.get("featured") else ""
    badge = _badge_class(str(card.get("status") or "NS"))
    venue = card.get("venue") or ""
    city = card.get("city") or ""
    venue_txt = ", ".join(x for x in (venue, city) if x)
    league_logo = _logo_img(str(card.get("league_logo") or ""), "Liga", "fb-mc-league-logo")
    home_logo = _logo_img(str(card.get("home_logo") or ""), "Heim", "fb-mc-team-logo")
    away_logo = _logo_img(str(card.get("away_logo") or ""), "Auswärts", "fb-mc-team-logo")
    live_extra = ""
    if card.get("live"):
        bits = []
        if card.get("live_possession"):
            bits.append(f"Ball {card['live_possession']}")
        if card.get("live_shots"):
            bits.append(f"Schüsse {card['live_shots']}")
        if card.get("live_xg"):
            bits.append(f"xG {card['live_xg']}")
        rc = card.get("red_cards") or {}
        if rc.get("total"):
            bits.append(f"Rot {rc.get('total')}")
        if bits:
            live_extra = f'<div class="fb-mc-live-stats">{html.escape(" · ".join(bits))}</div>'
    return f"""
<div class="fb-mc-card{live_cls}{featured_cls}">
    <div class="fb-mc-card-head">
        <div class="fb-mc-league-row">{league_logo}<span class="fb-mc-league">{html.escape(str(card.get('league') or 'Liga'))}</span></div>
        <span class="fb-mc-time">{html.escape(str(card.get('time') or card.get('date') or ''))}</span>
    </div>
    <div class="fb-mc-teams">
        <div class="fb-mc-team-cell">
            {home_logo}
            <div class="fb-mc-team">{html.escape(str(card.get('home') or ''))}</div>
        </div>
        <div class="fb-mc-score">{html.escape(str(card.get('score') or 'vs'))}</div>
        <div class="fb-mc-team-cell away">
            {away_logo}
            <div class="fb-mc-team away">{html.escape(str(card.get('away') or ''))}</div>
        </div>
    </div>
    <div class="fb-mc-meta">
        <span class="fb-mc-badge {badge}">{html.escape(str(card.get('status_label') or card.get('status') or 'NS'))}</span>
        <span class="fb-mc-venue">{html.escape(venue_txt)}</span>
    </div>
    {live_extra}
</div>
"""


def render_premium_live_empty(*, raw_live_count: int) -> None:
    extra = ""
    if raw_live_count:
        extra = f" ({raw_live_count} Spiele in kleineren Ligen laufen gerade.)"
    st.markdown(
        f"""
<div class="fb-mc-empty-premium">
    <strong>Heute keine Topspiele live.</strong>{extra}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_tip_mini(intel: dict[str, Any], *, fixture_id: int) -> None:
    h = intel.get("header") or {}
    rec = intel.get("recommendation") or {}
    inj = intel.get("injuries") or {}
    pred = intel.get("prediction") or {}
    val = intel.get("value_quote") or {}
    home_f = pred.get("home_pct")
    away_f = pred.get("away_pct")
    form_line = ""
    for r in intel.get("reasons_short") or []:
        if "Form" in r:
            form_line = r
            break
    inj_line = ""
    if inj.get("available"):
        inj_line = f"Verletzungen: H {inj.get('home_impact')} · A {inj.get('away_impact')}"
    val_line = ""
    if val:
        val_line = f"Value: {val.get('verdict', '—')}"
    pick = rec.get("main_pick") or "—"
    conf = rec.get("confidence")
    risk = rec.get("risk") or "—"
    conf_chip = f"Konfidenz {float(conf):.0f}%" if conf is not None else "Konfidenz —"
    st.markdown(
        f"""
<div class="fb-mc-tip-mini">
    <p class="match">{html.escape(str(h.get('home')))} vs {html.escape(str(h.get('away')))}</p>
    <p class="liga">{html.escape(str(h.get('league')))}</p>
    <p class="pick">{html.escape(str(pick))}</p>
    <div class="metrics">
        <span class="chip">{html.escape(conf_chip)}</span>
        <span class="chip">Risiko {html.escape(str(risk))}</span>
        {f'<span class="chip">H {home_f:.0f}%</span>' if home_f is not None else ''}
        {f'<span class="chip">A {away_f:.0f}%</span>' if away_f is not None else ''}
    </div>
    {f'<p style="color:#94a3b8;font-size:11px;margin:6px 0 0 0;">{html.escape(form_line)}</p>' if form_line else ''}
    {f'<p style="color:#fca5a5;font-size:11px;margin:4px 0 0 0;">{html.escape(inj_line)}</p>' if inj_line else ''}
    {f'<p style="color:#86efac;font-size:11px;margin:4px 0 0 0;">{html.escape(val_line)}</p>' if val_line else ''}
</div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Details", key=f"tip_detail_{fixture_id}", width="stretch"):
        st.session_state.fb_mc_selected_fixture = fixture_id
        st.session_state[f"fb_bet_details_{fixture_id}"] = True
        st.rerun()


def render_match_grid(
    fixtures: list[dict[str, Any]],
    *,
    key_prefix: str = "mc",
    selected_fixture: int | None = None,
    max_cards: int = 24,
    enriched_cards: list[dict[str, Any]] | None = None,
) -> None:
    rows = fixtures[:max_cards]
    if not rows:
        return
    card_by_id: dict[int, dict[str, Any]] = {}
    for c in enriched_cards or []:
        try:
            fid = int(c.get("fixture_id") or 0)
        except (TypeError, ValueError):
            continue
        if fid:
            card_by_id[fid] = c
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j >= len(rows):
                break
            fx = rows[i + j]
            fid_raw = (fx.get("fixture") or {}).get("id")
            try:
                fid_int = int(fid_raw) if fid_raw else 0
            except (TypeError, ValueError):
                fid_int = 0
            card = card_by_id.get(fid_int) or parse_match_card(fx)
            fid = card.get("fixture_id")
            if not fid:
                continue
            try:
                fid_int = int(fid)
            except (TypeError, ValueError):
                continue
            with col:
                st.markdown(_render_match_card_html(card), unsafe_allow_html=True)
                btn_type = "primary" if selected_fixture == fid_int else "secondary"
                if st.button(
                    "Analyse",
                    key=f"{key_prefix}_a_{fid_int}",
                    width="stretch",
                    type=btn_type,
                ):
                    st.session_state.fb_mc_selected_fixture = fid_int
                    st.rerun()


def render_match_section(
    title: str,
    fixtures: list[dict[str, Any]],
    *,
    empty: str,
    key_prefix: str = "mc",
    elite_ok: bool = False,
    selected_fixture: int | None = None,
) -> None:
    st.markdown(f'<div class="fb-mc-section">{html.escape(title)}</div>', unsafe_allow_html=True)
    if not fixtures:
        st.markdown(f'<div class="fb-empty">{html.escape(empty)}</div>', unsafe_allow_html=True)
        return

    for fx in fixtures:
        card = parse_match_card(fx)
        fid = card.get("fixture_id")
        if not fid:
            continue
        try:
            fid_int = int(fid)
        except (TypeError, ValueError):
            continue
        st.markdown(_render_match_card_html(card), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "Analyse öffnen",
                key=f"{key_prefix}_analyse_{fid_int}",
                width="stretch",
                type="primary" if selected_fixture == fid_int else "secondary",
            ):
                st.session_state.fb_mc_selected_fixture = fid_int
                st.session_state.fb_mc_detail_pick_idx = fid_int
                st.rerun()
        with c2:
            if elite_ok:
                if st.button(
                    "Elite Insight",
                    key=f"{key_prefix}_elite_{fid_int}",
                    width="stretch",
                ):
                    st.session_state.fb_mc_selected_fixture = fid_int
                    st.session_state.fb_mc_detail_pick_idx = fid_int
                    st.session_state.fb_mc_load_elite = fid_int
                    st.rerun()
            else:
                st.button(
                    "Elite Insight",
                    key=f"{key_prefix}_elite_{fid_int}",
                    width="stretch",
                    disabled=True,
                    help="Football Elite erforderlich",
                )


def _iter_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """API-Football liefert Events flach oder gruppiert unter 'events'."""
    out: list[dict[str, Any]] = []
    for block in rows or []:
        nested = block.get("events")
        if nested:
            out.extend(nested)
        elif block.get("type") or block.get("time"):
            out.append(block)
    return out


def fixture_select_options(fixtures: list[dict[str, Any]]) -> dict[str, int]:
    opts: dict[str, int] = {}
    for fx in fixtures:
        card = parse_match_card(fx)
        fid = card.get("fixture_id")
        if not fid:
            continue
        label = f"{card.get('league')} · {card.get('home')} vs {card.get('away')} ({card.get('status_label')})"
        opts[label] = int(fid)
    return opts


def render_match_detail_panel(detail: dict[str, Any], *, elite_ok: bool, pro_ok: bool = True) -> None:
    if detail.get("error"):
        st.error(str(detail["error"]))
        return
    card = detail.get("card") or {}
    st.markdown(
        f"""
<div class="fb-mc-detail">
    <h3>{html.escape(str(card.get('home')))} vs {html.escape(str(card.get('away')))}</h3>
    <p style="color:#64748b;margin:0 0 12px 0;">{html.escape(str(card.get('league')))} · {html.escape(str(card.get('venue') or ''))}</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    kvs = [
        ("Status", card.get("status_label") or card.get("status")),
        ("Spielstand", card.get("score")),
        ("Datum", card.get("date")),
        ("Anstoß", card.get("time") or "—"),
    ]
    if detail.get("home_form"):
        kvs.append(("Form Heim", detail.get("home_form")))
    if detail.get("away_form"):
        kvs.append(("Form Auswärts", detail.get("away_form")))

    hs = detail.get("home_standing") or {}
    aws = detail.get("away_standing") or {}
    if hs:
        kvs.append(("Tab. Heim", f"#{hs.get('rank')} · {hs.get('points')} Pkt"))
    if aws:
        kvs.append(("Tab. Ausw.", f"#{aws.get('rank')} · {aws.get('points')} Pkt"))

    cells = "".join(
        f'<div><div class="lbl">{html.escape(str(l))}</div><div class="val">{html.escape(str(v))}</div></div>'
        for l, v in kvs
    )
    st.markdown(f'<div class="fb-mc-kv">{cells}</div>', unsafe_allow_html=True)

    if detail.get("standings"):
        with st.expander("Tabellenstand", expanded=False):
            render_standings_table(detail.get("standings") or [], limit=18)

    pred = detail.get("prediction_insights") or {}
    if pred:
        st.markdown("#### AI / API Prognose")
        cols = st.columns(3)
        hp = pred.get("home_pct")
        dp = pred.get("draw_pct")
        ap = pred.get("away_pct")
        cols[0].metric("Heim %", f"{hp:.0f}%" if hp is not None else "—")
        cols[1].metric("Draw %", f"{dp:.0f}%" if dp is not None else "—")
        cols[2].metric("Ausw. %", f"{ap:.0f}%" if ap is not None else "—")
        if pred.get("advice"):
            st.caption(f"API Advice: {pred.get('advice')}")

    if not pro_ok:
        st.markdown(
            '<div class="fb-mc-pro-lock">Lineups, H2H, Events, Verletzungen und Prognosen '
            "ab <strong>Football Pro</strong>.</div>",
            unsafe_allow_html=True,
        )
        return

    if detail.get("lineups"):
        with st.expander("Aufstellungen", expanded=False):
            for block in detail.get("lineups") or []:
                team = (block.get("team") or {}).get("name") or "Team"
                formation = block.get("formation") or "—"
                st.markdown(f"**{team}** ({formation})")
                names = [
                    (p.get("player") or {}).get("name", "")
                    for p in (block.get("startXI") or [])
                ]
                st.caption(", ".join(n for n in names if n))

    if detail.get("home_injuries") or detail.get("away_injuries"):
        with st.expander("Verletzte / Ausfälle", expanded=False):
            for label, key in (("Heim", "home_injuries"), ("Auswärts", "away_injuries")):
                rows = detail.get(key) or []
                if not rows:
                    continue
                st.markdown(f"**{label}**")
                for row in rows[:8]:
                    pl = (row.get("player") or {}).get("name") or "Spieler"
                    reason = row.get("reason") or row.get("type") or "Ausfall"
                    st.caption(f"· {pl} — {reason}")

    if detail.get("h2h"):
        with st.expander("Head-to-Head (letzte Spiele)", expanded=False):
            for fx in (detail.get("h2h") or [])[:5]:
                t = fx.get("teams") or {}
                g = fx.get("goals") or {}
                st.caption(
                    f"{(t.get('home') or {}).get('name')} {g.get('home')}-{g.get('away')} "
                    f"{(t.get('away') or {}).get('name')}"
                )

    if detail.get("events"):
        with st.expander("Live Events", expanded=False):
            for ev in _iter_events(detail.get("events") or []):
                minute = (ev.get("time") or {}).get("elapsed")
                player = (ev.get("player") or {}).get("name") or ""
                typ = ev.get("type") or ""
                detail_txt = ev.get("detail") or ""
                suffix = f" ({detail_txt})" if detail_txt else ""
                st.caption(f"{minute}' {typ}{suffix} — {player}")

    if detail.get("odds") and elite_ok:
        with st.expander("Quoten (Elite)", expanded=False):
            st.json(detail.get("odds"))
    elif detail.get("missing") and "odds" in detail.get("missing"):
        st.caption("Quoten derzeit nicht verfügbar.")

    missing = detail.get("missing") or []
    if missing:
        st.caption(f"Optional nicht geladen: {', '.join(missing)}")

    if not elite_ok:
        st.markdown(
            '<div class="fb-mc-pro-lock">Elite Live Intelligence (Value, Momentum, Tipp-Hinweis) '
            "im Tab <strong>Live Intel</strong> — Football Elite.</div>",
            unsafe_allow_html=True,
        )
