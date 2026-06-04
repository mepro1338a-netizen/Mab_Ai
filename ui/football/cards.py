"""Football AI V2 — match list cards."""
from __future__ import annotations

import html
from typing import Any


def _status_badge(card: dict[str, Any]) -> tuple[str, str]:
    if card.get("live"):
        label = str(card.get("status_label") or "Live")
        return "live", label
    st = str(card.get("status") or "NS")
    if st in ("FT", "AET", "PEN"):
        return "", "Beendet"
    if st == "NS":
        return "", "Geplant"
    return "", str(card.get("status_label") or st)


def match_card_html(row: dict[str, Any]) -> str:
    card = row.get("card") or {}
    home = html.escape(str(card.get("home") or "Heim"))
    away = html.escape(str(card.get("away") or "Auswärts"))
    league = html.escape(str(card.get("league") or ""))
    date = html.escape(str(card.get("date") or ""))
    time_s = html.escape(str(card.get("time") or ""))
    dt_parts = [x for x in (date, time_s) if x]
    dt_line = html.escape(" · ".join(dt_parts)) if dt_parts else ""

    live = bool(card.get("live"))
    cls = "fb2-match is-live" if live else "fb2-match"
    st_cls, st_lbl = _status_badge(card)

    if live:
        mid = f'<div class="fb2-score">{html.escape(str(card.get("score") or "–"))}</div>'
    else:
        mid = '<div class="fb2-vs">vs</div>'

    odds = html.escape(str(row.get("quote_label") or "nicht verfügbar"))
    status_html = (
        f'<span class="fb2-status {st_cls}">{html.escape(st_lbl)}</span>'
        if st_lbl
        else ""
    )

    return f"""
<div class="{cls}">
  <div class="fb2-match-meta">
    <span class="lg">{league}</span>
    {f" · {dt_line}" if dt_line else ""}
  </div>
  <div class="fb2-teams">
    <div class="fb2-team">{home}</div>
    {mid}
    <div class="fb2-team away">{away}</div>
  </div>
  <div class="fb2-row">
    {status_html}
    <span class="fb2-odds">Quote: {odds}</span>
  </div>
</div>
"""


def filter_rows_by_league(rows: list[dict[str, Any]], league_id: int) -> list[dict[str, Any]]:
    if not league_id:
        return rows
    out: list[dict[str, Any]] = []
    for row in rows:
        card = row.get("card") or {}
        try:
            lid = int(card.get("league_id") or 0)
        except (TypeError, ValueError):
            continue
        if lid == league_id:
            out.append(row)
    return out
