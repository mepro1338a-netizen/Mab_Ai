"""Football AI V2 — match list cards."""
from __future__ import annotations

import html
from typing import Any


def _img(src: str, alt: str, *, cls: str = "fb2-logo") -> str:
    if not src:
        return ""
    return (
        f'<span class="fb2-logo-box">'
        f'<img class="{cls}" src="{html.escape(str(src))}" '
        f'alt="{html.escape(alt)}" loading="lazy" />'
        f"</span>"
    )


def _format_kickoff(card: dict[str, Any]) -> str:
    time_s = str(card.get("time") or "").strip()
    if time_s:
        return time_s
    date_s = str(card.get("date") or "").strip()
    return date_s


def _chip_html(chip: str, *, away: bool = False) -> str:
    empty = " is-empty" if not chip else ""
    side = " away" if away else ""
    text = html.escape(chip) if chip else "&nbsp;"
    return f'<div class="fb2-stand-chip{side}{empty}">{text}</div>'


def _form_html(form: str) -> str:
    empty = " is-empty" if not form else ""
    label = f"Form: {html.escape(form)}" if form else "&nbsp;"
    return f'<div class="fb2-form-line{empty}">{label}</div>'


def _center_block(card: dict[str, Any]) -> str:
    live = bool(card.get("live"))
    finished = bool(card.get("finished"))
    score = str(card.get("score") or "").strip()
    score_disp = html.escape(score.replace(":", " : ") if score else "– : –")

    if live:
        minute = card.get("minute")
        min_html = ""
        if minute is not None:
            try:
                min_html = f'<div class="fb2-minute">{int(minute)}\'</div>'
            except (TypeError, ValueError):
                min_html = '<div class="fb2-minute">LIVE</div>'
        return (
            '<div class="fb2-live-badge">LIVE</div>'
            f"{min_html}"
            f'<div class="fb2-score fb2-score--live">{score_disp}</div>'
        )

    if finished:
        return (
            '<div class="fb2-ft">FT</div>'
            f'<div class="fb2-score fb2-score--ft">{score_disp}</div>'
        )

    kick = _format_kickoff(card)
    if kick:
        return f'<div class="fb2-kickoff">{html.escape(kick)}</div>'
    return '<div class="fb2-kickoff fb2-kickoff--muted">–</div>'


def _team_cell(name: str, logo: str, *, align: str, chip: str, form: str) -> str:
    return f"""
<div class="fb2-team {align}">
  <div class="fb2-team-head">
    {_img(logo, name)}
    <span class="fb2-team-name">{html.escape(name)}</span>
  </div>
  {_chip_html(chip, away=align == "away")}
  {_form_html(form)}
</div>
"""


def match_card_html(row: dict[str, Any]) -> str:
    card = row.get("card") or {}
    home = str(card.get("home") or "Heim")
    away = str(card.get("away") or "Auswärts")
    league = str(card.get("league") or "")
    league_logo = str(card.get("league_logo") or "")

    live = bool(card.get("live"))
    cls = "fb2-match is-live" if live else "fb2-match"
    if card.get("finished"):
        cls += " is-ft"

    league_img = (
        f'<span class="fb2-logo-box fb2-logo-box--sm">'
        f'<img class="fb2-league-logo" src="{html.escape(league_logo)}" '
        f'alt="{html.escape(league)}" loading="lazy" /></span>'
        if league_logo
        else ""
    )
    league_line = (
        f'<span class="fb2-league-meta">{league_img}<span class="lg">{html.escape(league)}</span></span>'
        if league
        else ""
    )

    center = _center_block(card)

    home_chip = str(row.get("home_standing_chip") or "")
    away_chip = str(row.get("away_standing_chip") or "")
    home_form = str(row.get("home_form") or "")
    away_form = str(row.get("away_form") or "")

    quote = str(row.get("quote_label") or "").strip()
    quote_html = (
        f'<span class="fb2-odds">{html.escape(quote)}</span>' if quote else ""
    )

    status_html = ""
    if not live and not card.get("finished") and str(card.get("status") or "") == "NS":
        status_html = '<span class="fb2-status">Geplant</span>'

    return f"""
<div class="{cls}">
  <div class="fb2-match-meta">{league_line}</div>
  <div class="fb2-teams">
    {_team_cell(home, str(card.get("home_logo") or ""), align="home", chip=home_chip, form=home_form)}
    <div class="fb2-mid">{center}</div>
    {_team_cell(away, str(card.get("away_logo") or ""), align="away", chip=away_chip, form=away_form)}
  </div>
  <div class="fb2-row">
    {status_html}
    {quote_html}
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
