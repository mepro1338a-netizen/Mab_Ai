"""Match analysis widgets — render only when real data exists."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from services.football_match_intel import build_match_analysis_sections
from ui.football_betting_card import inject_betting_card_css


def _block(title: str, body_html: str) -> None:
    st.markdown(
        f'<div class="fb-bet-inj" style="border-color:rgba(168,85,247,.22);background:rgba(30,27,75,.15);">'
        f'<h4 style="color:#c4b5fd!important;">{html.escape(title)}</h4>{body_html}</div>',
        unsafe_allow_html=True,
    )


def _render_suspensions(susp: dict[str, Any]) -> None:
    body = ""
    for side, rows in (("Heim", susp.get("home") or []), ("Auswärts", susp.get("away") or [])):
        if not rows:
            continue
        names = ", ".join(
            f"{html.escape(str(r.get('player', '')))} ({html.escape(str(r.get('reason', '')))})"
            for r in rows[:6]
        )
        body += f"<p><strong>{side}</strong>: {names}</p>"
    if body:
        _block("Sperren", body)


def _render_league_position(pos: dict[str, Any]) -> None:
    card = pos.get("card") or {}
    hn = html.escape(str(card.get("home") or "Heim"))
    an = html.escape(str(card.get("away") or "Auswärts"))
    hs = pos.get("home") or {}
    aws = pos.get("away") or {}
    body = ""
    if hs.get("rank") is not None:
        body += (
            f"<p><strong>{hn}</strong> #{hs.get('rank')} · "
            f"{hs.get('goals_for', '—')}:{hs.get('goals_against', '—')} · {hs.get('points', '—')} Pkt</p>"
        )
    if aws.get("rank") is not None:
        body += (
            f"<p><strong>{an}</strong> #{aws.get('rank')} · "
            f"{aws.get('goals_for', '—')}:{aws.get('goals_against', '—')} · {aws.get('points', '—')} Pkt</p>"
        )
    if body:
        _block("Tabellenplatz & Tore", body)


def _render_prediction(pred: dict[str, Any], card: dict[str, Any]) -> None:
    cols = st.columns(3)
    for i, (lbl, key) in enumerate((("Heim", "home_pct"), ("Remis", "draw_pct"), ("Ausw.", "away_pct"))):
        val = pred.get(key)
        with cols[i]:
            if val is not None:
                st.markdown(
                    f'<div class="fb-bet-prob"><strong>{float(val):.0f}%</strong><span>{lbl}</span></div>',
                    unsafe_allow_html=True,
                )
    advice = str(pred.get("advice") or "").strip()
    if advice:
        _block("API-Prognose", f"<p>{html.escape(advice[:240])}</p>")


def _render_injuries(inj: dict[str, Any]) -> None:
    body = ""
    for side, rows, imp in (
        ("Heim", inj.get("home") or [], inj.get("home_impact")),
        ("Auswärts", inj.get("away") or [], inj.get("away_impact")),
    ):
        if not rows:
            continue
        if rows and isinstance(rows[0], dict) and rows[0].get("player"):
            names = ", ".join(
                f"{html.escape(str(r.get('player', '')))} ({html.escape(str(r.get('reason', '')))})"
                for r in rows[:6]
            )
        else:
            names = ", ".join(html.escape(str(r)) for r in rows[:6])
        body += f"<p><strong>{side}</strong> · Impact {html.escape(str(imp or '—'))}: {names}</p>"
    if body:
        _block("Verletzungsreport", body)


def _render_form(form: dict[str, Any], card: dict[str, Any]) -> None:
    h = html.escape(str(form.get("home") or "—"))
    a = html.escape(str(form.get("away") or "—"))
    hn = html.escape(str(card.get("home") or "Heim"))
    an = html.escape(str(card.get("away") or "Auswärts"))
    _block("Teamform (5 Spiele)", f"<p><strong>{hn}</strong> {h}</p><p><strong>{an}</strong> {a}</p>")


def _render_h2h(h2h: Any, card: dict[str, Any]) -> None:
    rows = h2h if isinstance(h2h, list) else (h2h.get("rows") or [])
    if not rows:
        return
    lines = []
    for fx in rows[:5]:
        t = fx.get("teams") or {}
        g = fx.get("goals") or {}
        lines.append(
            f"{html.escape((t.get('home') or {}).get('name', '?'))} "
            f"<strong>{g.get('home')}-{g.get('away')}</strong> "
            f"{html.escape((t.get('away') or {}).get('name', '?'))}"
        )
    _block("Direktvergleich", "".join(f"<p>{line}</p>" for line in lines))


def _render_xg(xg: dict[str, Any]) -> None:
    hx, ax = xg.get("home_xg"), xg.get("away_xg")
    if hx is None and ax is None:
        return
    hn = html.escape(str(xg.get("home") or "Heim"))
    an = html.escape(str(xg.get("away") or "Auswärts"))
    body = f"<p><strong>{hn}</strong> xG {hx if hx is not None else '—'} · "
    body += f"<strong>{an}</strong> xG {ax if ax is not None else '—'}</p>"
    if xg.get("total_xg") is not None:
        body += f"<p>Gesamt xG: <strong>{xg['total_xg']}</strong></p>"
    _block("Erwartete Tore (xG)", body)


def _render_live_stats(stats: dict[str, Any]) -> None:
    mom = stats.get("momentum") or {}
    label = mom.get("label") or ""
    leader = mom.get("leader") or ""
    body = ""
    if label:
        body += f"<p>Momentum: <strong>{html.escape(label)}</strong>"
        if leader and leader != "—":
            body += f" ({html.escape(str(leader))})"
        body += "</p>"
    for side in ("home", "away"):
        block = stats.get(side) or {}
        if not block.get("team"):
            continue
        body += (
            f"<p><strong>{html.escape(str(block.get('team')))}</strong>: "
            f"Ball {block.get('possession') or '—'}% · "
            f"Schüsse {block.get('shots_on') or block.get('shots') or '—'} · "
            f"Ecken {block.get('corners') or '—'}</p>"
        )
    if body:
        _block("Live-Statistik", body)


def _render_reasoning(reasons: list[str]) -> None:
    items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons[:8])
    st.markdown(f'<ul class="fb-bet-reasons">{items}</ul>', unsafe_allow_html=True)


def render_match_analysis_panel(
    detail: dict[str, Any],
    intel: dict[str, Any] | None = None,
    *,
    live_bundle: dict[str, Any] | None = None,
    include_reasoning: bool = True,
) -> bool:
    """Render analysis blocks. Returns True if anything was shown."""
    inject_betting_card_css()
    intel = intel or detail.get("intel")
    sections = build_match_analysis_sections(detail, intel, live_bundle=live_bundle)
    if not sections:
        return False

    card = detail.get("card") or {}
    shown = False

    if "prediction" in sections:
        _render_prediction(sections["prediction"], card)
        shown = True

    if "form" in sections:
        _render_form(sections["form"], card)
        shown = True

    if "league_position" in sections:
        _render_league_position(sections["league_position"])
        shown = True

    if "h2h" in sections:
        _render_h2h(sections["h2h"], card)
        shown = True

    if "injuries" in sections:
        _render_injuries(sections["injuries"])
        shown = True

    if "suspensions" in sections:
        _render_suspensions(sections["suspensions"])
        shown = True

    if "xg" in sections:
        _render_xg(sections["xg"])
        shown = True

    if "live_stats" in sections:
        _render_live_stats(sections["live_stats"])
        shown = True

    if include_reasoning and "reasoning" in sections:
        st.markdown(
            '<p style="color:#86efac;font-size:11px;font-weight:800;letter-spacing:.1em;margin:16px 0 8px 0;">'
            "BEGRÜNDUNG</p>",
            unsafe_allow_html=True,
        )
        _render_reasoning(sections["reasoning"])
        shown = True

    return shown
