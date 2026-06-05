"""Football AI V2 — match analysis panel (real API data only)."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from services.football_board import (
    build_betting_signal,
    has_complete_odds,
    parse_match_card,
    win_pcts_from_odds,
)
from ui.football.constants import MSG_NO_ANALYSIS


def _pct_bar(label: str, pct: float | None) -> str:
    if pct is None:
        return ""
    width = max(0, min(100, float(pct)))
    return f"""
<div class="fb2-prob-item">
  <div class="lbl">{html.escape(label)}</div>
  <div class="pct">{width:.0f}%</div>
  <div class="fb2-bar"><span style="width:{width:.0f}%"></span></div>
</div>
"""


def _standing_block(title: str, summary: dict[str, Any] | None) -> str:
    if not summary:
        return f'<div class="fb2-statbox"><div class="t">{html.escape(title)}</div><p>—</p></div>'
    rank = summary.get("rank")
    pts = summary.get("points")
    gf = summary.get("goals_for")
    ga = summary.get("goals_against")
    return f"""
<div class="fb2-statbox">
  <div class="t">{html.escape(title)}</div>
  <div>Platz {html.escape(str(rank or "—"))} · {html.escape(str(pts or "—"))} Pkt</div>
  <div>Tore {html.escape(str(gf or "—"))}:{html.escape(str(ga or "—"))}</div>
</div>
"""


def _injury_list(items: list[dict[str, Any]] | None) -> str:
    if not items:
        return "<li>Keine Meldungen</li>"
    lines: list[str] = []
    for row in items[:8]:
        player = (row.get("player") or {}).get("name") or "—"
        reason = str(row.get("reason") or row.get("type") or "").strip()
        text = f"{player} — {reason}" if reason else str(player)
        lines.append(f"<li>{html.escape(text)}</li>")
    return "".join(lines)


def _h2h_html(fixtures: list[dict[str, Any]] | None) -> str:
    if not fixtures:
        return "<li>Keine H2H-Daten</li>"
    items: list[str] = []
    for fx in fixtures[:5]:
        c = parse_match_card(fx)
        home = c.get("home") or "?"
        away = c.get("away") or "?"
        score = c.get("score") if c.get("live") or c.get("finished") else (c.get("date") or "")
        items.append(
            f"<li>{html.escape(str(home))} {html.escape(str(score))} {html.escape(str(away))}</li>"
        )
    return "".join(items)


def _build_ai_summary(detail: dict[str, Any], signal: dict[str, Any] | None) -> str:
    pred = detail.get("prediction_insights") or {}
    parts: list[str] = []

    overview = str(pred.get("winner_comment") or pred.get("advice") or "").strip()
    if overview:
        parts.append(f"<p><strong>Überblick</strong><br>{html.escape(overview)}</p>")

    fh, fa = pred.get("form_home"), pred.get("form_away")
    card = detail.get("card") or {}
    home = card.get("home") or "Heim"
    away = card.get("away") or "Auswärts"
    if fh or fa:
        parts.append(
            f"<p><strong>Form</strong><br>"
            f"{html.escape(str(home))}: {html.escape(str(fh or '—'))}<br>"
            f"{html.escape(str(away))}: {html.escape(str(fa or '—'))}</p>"
        )

    if signal and not signal.get("no_bet") and signal.get("ai_pick"):
        risk = str(signal.get("risk") or "")
        pick = str(signal.get("ai_pick") or "")
        parts.append(
            f"<p><strong>Risiko</strong><br>{html.escape(risk)}</p>"
            f"<p><strong>Empfehlung</strong><br>{html.escape(pick)} "
            f"<span style='color:#71717a'>(Bildung — keine Wettgarantie)</span></p>"
        )
    elif signal and signal.get("no_bet"):
        parts.append(
            "<p><strong>Empfehlung</strong><br>"
            "Keine klare Empfehlung — Datenlage zu unscharf.</p>"
        )

    reasons = signal.get("reasons") if signal else []
    if reasons:
        bullets = "".join(f"<li>{html.escape(str(r))}</li>" for r in reasons[:3])
        parts.append(f"<p><strong>Stärken / Schwächen</strong></p><ul class='fb2-list'>{bullets}</ul>")

    if not parts:
        return ""
    return f'<div class="fb2-summary">{"".join(parts)}</div>'


def _header_meta(card: dict[str, Any], detail: dict[str, Any]) -> str:
    parts: list[str] = []
    league = str(card.get("league") or "").strip()
    if league:
        parts.append(league)
    venue = str(card.get("venue") or "").strip()
    if not venue:
        venue = str((detail.get("summary") or {}).get("venue") or "").strip()
    if venue:
        parts.append(venue)
    date_s = str(card.get("date") or "").strip()
    time_s = str(card.get("time") or "").strip()
    if date_s:
        parts.append(date_s)
    if time_s:
        parts.append(time_s)
    return " · ".join(parts) if parts else "Spielanalyse"


def render_analysis(detail: dict[str, Any]) -> None:
    card = detail.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    meta = html.escape(_header_meta(card, detail))

    if not detail.get("analysis_available"):
        st.markdown(
            f"""
<div class="fb2-analysis">
  <h2>{home} vs {away}</h2>
  <p class="sub">{meta}</p>
  <div class="fb2-warn">{html.escape(MSG_NO_ANALYSIS)}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    pred = detail.get("prediction_insights") or {}
    odds = detail.get("odds") or {}
    hp, dp, ap = pred.get("home_pct"), pred.get("draw_pct"), pred.get("away_pct")

    if hp is None and has_complete_odds(
        {
            "home_odd": odds.get("home"),
            "draw_odd": odds.get("draw"),
            "away_odd": odds.get("away"),
        }
    ):
        hp, dp, ap = win_pcts_from_odds(
            odds.get("home"), odds.get("draw"), odds.get("away")
        )

    prob_html = ""
    if hp is not None and dp is not None and ap is not None:
        prob_html = (
            '<div class="fb2-block"><h3>Siegwahrscheinlichkeit</h3>'
            f'<div class="fb2-prob">{_pct_bar("Heim", hp)}{_pct_bar("Unentschieden", dp)}{_pct_bar("Auswärts", ap)}</div></div>'
        )

    form_home = detail.get("home_form") or pred.get("form_home") or "—"
    form_away = detail.get("away_form") or pred.get("form_away") or "—"

    h_odd, d_odd, a_odd = odds.get("home"), odds.get("draw"), odds.get("away")
    odds_line = "nicht verfügbar"
    if h_odd and d_odd and a_odd:
        try:
            odds_line = f"1 {float(h_odd):.2f} · X {float(d_odd):.2f} · 2 {float(a_odd):.2f}"
        except (TypeError, ValueError):
            pass

    signal = None
    if has_complete_odds(
        {"home_odd": h_odd, "draw_odd": d_odd, "away_odd": a_odd}
    ):
        signal = build_betting_signal(
            home=str(card.get("home") or ""),
            away=str(card.get("away") or ""),
            home_odd=h_odd,
            draw_odd=d_odd,
            away_odd=a_odd,
            pred_insights=pred if pred else None,
            h2h_support=bool(detail.get("h2h")),
            injury_advantage=bool(
                detail.get("home_injuries") or detail.get("away_injuries")
            ),
        )

    summary_html = _build_ai_summary(detail, signal)

    st.markdown(
        f"""
<div class="fb2-analysis">
  <h2>{home} vs {away}</h2>
  <p class="sub">{meta}</p>
  {prob_html}
  <div class="fb2-block"><h3>Form · Letzte 5</h3>
    <div class="fb2-grid2">
      <div class="fb2-statbox"><div class="t">{home}</div>{html.escape(str(form_home))}</div>
      <div class="fb2-statbox"><div class="t">{away}</div>{html.escape(str(form_away))}</div>
    </div>
  </div>
  <div class="fb2-block"><h3>Tabellenplatz</h3>
    <div class="fb2-grid2">
      {_standing_block(str(card.get("home") or "Heim"), detail.get("home_standing_summary"))}
      {_standing_block(str(card.get("away") or "Auswärts"), detail.get("away_standing_summary"))}
    </div>
  </div>
  <div class="fb2-block"><h3>H2H</h3><ul class="fb2-list">{_h2h_html(detail.get("h2h"))}</ul></div>
  <div class="fb2-block"><h3>Verletzungen</h3>
    <div class="fb2-grid2">
      <div class="fb2-statbox"><div class="t">{home}</div><ul class="fb2-list">{_injury_list(detail.get("home_injuries"))}</ul></div>
      <div class="fb2-statbox"><div class="t">{away}</div><ul class="fb2-list">{_injury_list(detail.get("away_injuries"))}</ul></div>
    </div>
  </div>
  <div class="fb2-block"><h3>Quotenvergleich</h3>
    <div class="fb2-statbox"><div class="t">1X2</div>{html.escape(odds_line)}</div>
  </div>
  <div class="fb2-block"><h3>AI Summary</h3>
    {summary_html or f'<div class="fb2-warn">{html.escape(MSG_NO_ANALYSIS)}</div>'}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
