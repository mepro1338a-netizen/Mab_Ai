"""Betting board — fixtures, odds, signals, match detail (merged board layer)."""
from __future__ import annotations

from typing import Any

from config import (
    FOOTBALL_DEFAULT_SEASON,
    FOOTBALL_TOPSPIELE_LEAGUE_IDS,
    football_plan_rank,
)
from services.football_loaders import (
    FEED_CAP_DEFAULT,
    FEED_CAP_RAW,
    FEED_MIN_SCORE_RAW,
    LIVE_STATUSES,
    curate_feed_fixtures,
    dedupe_fixtures,
    fetch_premium_dashboard,
    filter_blocked_fixtures,
    filter_premium_fixtures,
    parse_match_card,
    sort_fixtures_by_priority,
)
from services.football_service import FootballAPIError, FootballService, fixture_team_names

# ---------------------------------------------------------------------------
# Odds
# ---------------------------------------------------------------------------


def calculate_tip_odds(
    odds: float,
    stake: float,
    win_probability_pct: float,
) -> dict:
    """
    Decimal odds model.
    - odds: decimal quote (e.g. 2.10)
    - stake: amount wagered (analysis only)
    - win_probability_pct: user estimate 0–100
    """
    odds = float(odds)
    stake = max(0.0, float(stake))
    p_user = max(0.0, min(100.0, float(win_probability_pct))) / 100.0

    if odds < 1.01:
        raise ValueError("Quote muss mindestens 1.01 sein (Dezimalformat).")

    implied_pct = (1.0 / odds) * 100.0
    break_even_pct = implied_pct
    profit = stake * (odds - 1.0)
    payout = stake * odds
    expected_value = stake * (p_user * odds - 1.0)
    edge_pct = p_user * 100.0 - implied_pct
    is_value = edge_pct > 1.0

    if odds >= 4.0 or p_user < implied_pct * 0.85:
        risk = "Hoch"
    elif odds >= 2.2 or abs(edge_pct) < 3.0:
        risk = "Mittel"
    else:
        risk = "Niedrig"

    confidence = min(95.0, max(22.0, 48.0 + abs(edge_pct) * 2.4 + (8.0 if is_value else 0.0)))

    bankroll_pct = 0.0
    if edge_pct > 0.5 and odds > 1.01:
        kelly = (p_user * odds - 1.0) / (odds - 1.0)
        bankroll_pct = max(0.0, min(5.0, kelly * 25.0))

    value_label = "Value erkannt" if is_value else "Kein klarer Value"
    if edge_pct > 6:
        value_label = "Starker Value (modell)"
    elif edge_pct < -4:
        value_label = "Markt wirkt teurer"

    return {
        "implied_probability_pct": round(implied_pct, 2),
        "break_even_probability_pct": round(break_even_pct, 2),
        "profit": round(profit, 2),
        "payout": round(payout, 2),
        "expected_value": round(expected_value, 2),
        "edge_pct": round(edge_pct, 2),
        "is_value_bet": is_value,
        "risk_level": risk,
        "confidence_pct": round(confidence, 1),
        "bankroll_stake_pct": round(bankroll_pct, 2),
        "value_label": value_label,
    }


def extract_1x2_odds(markets: list[dict[str, Any]]) -> dict[str, float | None]:
    """Best available 1X2 decimal odds from normalized market rows."""
    home_odd = draw_odd = away_odd = None
    for m in markets or []:
        market = str(m.get("market") or "").lower()
        sel = str(m.get("selection") or "").lower()
        if "match winner" not in market and "1x2" not in market and "winner" not in market:
            continue
        try:
            odd = float(m.get("odd") or 0)
        except (TypeError, ValueError):
            continue
        if odd < 1.01:
            continue
        if sel in ("home", "1"):
            home_odd = home_odd or odd
        elif sel in ("draw", "x"):
            draw_odd = draw_odd or odd
        elif sel in ("away", "2"):
            away_odd = away_odd or odd
    return {"home": home_odd, "draw": draw_odd, "away": away_odd}


def get_odds_for_fixture(
    service: Any,
    fixture_id: int,
    *,
    username: str,
) -> dict[str, float | None]:
    """1X2 odds — not available without api-sports.io (disabled)."""
    _ = fixture_id, username
    if getattr(service, "premium_api_enabled", lambda: False)():
        try:
            raw = service.get_fixture_odds(int(fixture_id), username=username)
            markets = parse_fixture_odds_payload(raw)
            return extract_1x2_odds(markets)
        except FootballAPIError:
            pass
    return {"home": None, "draw": None, "away": None}


def win_pcts_from_odds(
    home_odd: float | None,
    draw_odd: float | None,
    away_odd: float | None,
) -> tuple[float | None, float | None, float | None]:
    """Normalized implied win % from decimal odds."""
    try:
        h = float(home_odd) if home_odd else None
        d = float(draw_odd) if draw_odd else None
        a = float(away_odd) if away_odd else None
    except (TypeError, ValueError):
        return None, None, None
    if not h or not d or not a or h < 1.01 or d < 1.01 or a < 1.01:
        return None, None, None
    hp, dp, ap = 1.0 / h, 1.0 / d, 1.0 / a
    total = hp + dp + ap
    if total <= 0:
        return None, None, None
    return round(hp / total * 100, 1), round(dp / total * 100, 1), round(ap / total * 100, 1)


def parse_fixture_odds_payload(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize API-Football odds into flat market rows."""
    markets: list[dict[str, Any]] = []
    for block in rows or []:
        for bookmaker in block.get("bookmakers") or []:
            bm_name = str(bookmaker.get("name") or "Anbieter")
            for bet in bookmaker.get("bets") or []:
                market = str(bet.get("name") or "Markt")
                for val in bet.get("values") or []:
                    try:
                        odd = float(val.get("odd") or 0)
                    except (TypeError, ValueError):
                        continue
                    if odd < 1.01:
                        continue
                    markets.append({
                        "bookmaker": bm_name,
                        "market": market,
                        "selection": str(val.get("value") or ""),
                        "odd": round(odd, 2),
                        "label": f"{bm_name} · {market} · {val.get('value', '')}",
                    })
    return markets[:48]


def parse_prediction_insights(row: dict[str, Any]) -> dict[str, Any]:
    """Extract win probabilities and advice from predictions API."""
    preds = row.get("predictions") or {}
    percent = preds.get("percent") or {}
    comparison = preds.get("comparison") or {}

    def _pct(key: str) -> float | None:
        raw = percent.get(key)
        if raw is None:
            return None
        s = str(raw).replace("%", "").strip()
        try:
            return float(s)
        except ValueError:
            return None

    home = _pct("home")
    draw = _pct("draw")
    away = _pct("away")

    teams = row.get("teams") or {}
    home_name = (teams.get("home") or {}).get("name") or "Home"
    away_name = (teams.get("away") or {}).get("name") or "Away"

    return {
        "home": home_name,
        "away": away_name,
        "home_pct": home,
        "draw_pct": draw,
        "away_pct": away,
        "advice": str(preds.get("advice") or "").strip(),
        "winner_comment": str((preds.get("winner") or {}).get("comment") or "").strip(),
        "form_home": str((comparison.get("form") or {}).get("home") or ""),
        "form_away": str((comparison.get("form") or {}).get("away") or ""),
    }


def fixture_options_from_list(fixtures: list[dict[str, Any]]) -> dict[str, int]:
    """Build selectbox labels -> fixture id."""
    from services.football_service import fixture_label

    opts: dict[str, int] = {}
    for fx in fixtures or []:
        meta = fx.get("fixture") or {}
        fid = meta.get("id")
        if fid:
            opts[fixture_label(fx)] = int(fid)
    return opts


# ---------------------------------------------------------------------------
# Betting quality (from football_betting_quality — board subset)
# ---------------------------------------------------------------------------


def has_complete_odds(row: dict[str, Any]) -> bool:
    return all(
        row.get(k) is not None and float(row.get(k) or 0) >= 1.01
        for k in ("home_odd", "draw_odd", "away_odd")
    )


def _has_prediction_data(pred_insights: dict[str, Any] | None) -> bool:
    pred = pred_insights or {}
    return pred.get("home_pct") is not None or bool(pred.get("advice"))


def _has_form_data(pred_insights: dict[str, Any] | None) -> bool:
    pred = pred_insights or {}
    return bool(pred.get("form_home") or pred.get("form_away"))


def is_analysis_eligible(
    *,
    fixture_id: int | None,
    home: str,
    away: str,
    pred_insights: dict[str, Any] | None,
    has_odds: bool,
    has_standing: bool = False,
    has_form: bool = False,
) -> bool:
    """Analysis when fixture + teams + at least one of: standing, form, odds, prediction."""
    if not fixture_id:
        return False
    if not str(home or "").strip() or not str(away or "").strip():
        return False
    return bool(
        has_standing
        or has_form
        or _has_form_data(pred_insights)
        or has_odds
        or _has_prediction_data(pred_insights)
    )


def format_standing_chip(summary: dict[str, Any] | None) -> str:
    if not summary:
        return ""
    rank, pts = summary.get("rank"), summary.get("points")
    parts: list[str] = []
    if rank is not None:
        parts.append(f"#{rank}")
    if pts is not None:
        parts.append(f"{pts} Punkte")
    return " · ".join(parts)


def format_form_display(raw: str) -> str:
    s = str(raw or "").strip().upper().replace(" ", "")
    if not s or s == "—":
        return ""
    return " ".join(ch for ch in s if ch in "WDL")


def form_from_standing_row(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    return format_form_display(str(row.get("form") or ""))


def build_league_standings_cache(
    service: FootballService,
    fixtures: list[dict[str, Any]],
    *,
    username: str,
) -> dict[int, list[dict[str, Any]]]:
    """One standings request per league in the fixture pool."""
    from config import FOOTBALL_DEFAULT_SEASON

    leagues: dict[int, int] = {}
    for fx in fixtures or []:
        lid = _fixture_league_id(fx)
        if not lid:
            continue
        season = int((fx.get("league") or {}).get("season") or FOOTBALL_DEFAULT_SEASON)
        leagues[int(lid)] = season

    cache: dict[int, list[dict[str, Any]]] = {}
    for lid, season in leagues.items():
        try:
            cache[lid] = service.get_standings(lid, season=season, username=username)
        except FootballAPIError:
            cache[lid] = []
    return cache


def empty_betting_signal() -> dict[str, Any]:
    return {
        "ai_pick": None,
        "confidence": None,
        "no_bet": True,
        "risk": None,
        "value": False,
        "reasons": [],
        "home_pct": None,
        "draw_pct": None,
        "away_pct": None,
    }


def build_betting_signal(
    *,
    home: str,
    away: str,
    home_odd: float | None,
    draw_odd: float | None,
    away_odd: float | None,
    pred_insights: dict[str, Any] | None,
    is_live: bool = False,
    h2h_support: bool = False,
    injury_advantage: bool = False,
) -> dict[str, Any]:
    """AI pick + confidence from odds and optional API prediction — no odds, no output."""
    pred = pred_insights or {}
    reasons: list[str] = []
    confidence = 50.0
    no_bet = True
    ai_pick = "No Bet"
    risk = "Hoch"
    value = False

    odds_ok = has_complete_odds(
        {"home_odd": home_odd, "draw_odd": draw_odd, "away_odd": away_odd}
    )
    has_form = _has_form_data(pred)
    has_pred = pred.get("home_pct") is not None

    if not odds_ok:
        return empty_betting_signal()

    home_pct, draw_pct, away_pct = win_pcts_from_odds(home_odd, draw_odd, away_odd)

    sides = [
        ("home", float(home_odd), home_pct, home),
        ("draw", float(draw_odd), draw_pct, "Unentschieden"),
        ("away", float(away_odd), away_pct, away),
    ]
    fav_key, fav_odd, fav_pct, fav_name = min(sides, key=lambda x: x[1])

    if not has_form and not has_pred:
        confidence -= 10

    if pred.get("advice"):
        confidence += 10
        reasons.append(str(pred["advice"])[:90])
    if has_form:
        confidence += 10
        fh, fa = pred.get("form_home"), pred.get("form_away")
        reasons.append(f"Form: {home} {fh or '—'} · {away} {fa or '—'}")
    if h2h_support:
        confidence += 10
        reasons.append("H2H stützt den Favoriten")
    if injury_advantage:
        confidence += 10
        reasons.append("Verletzungslage gibt Vorteil")

    margin = max((s[2] or 0) for s in sides) - sorted((s[2] or 0 for s in sides))[-2]
    if fav_odd < 1.70 and (fav_pct or 0) >= 50:
        confidence += 10
        ai_pick = f"{fav_name} Sieg" if fav_key != "draw" else "Unentschieden"
        reasons.append(f"Klarer Favorit {fav_odd:.2f} ({fav_pct:.0f}%)")
    elif fav_odd < 1.85 and (fav_pct or 0) >= 48:
        ai_pick = f"{fav_name} Sieg" if fav_key != "draw" else "Unentschieden"
        reasons.append(f"Markt-Favorit {fav_odd:.2f} ({fav_pct:.0f}%)")
    elif has_pred:
        api_best = max(
            [
                ("home", pred.get("home_pct"), home),
                ("draw", pred.get("draw_pct"), "X"),
                ("away", pred.get("away_pct"), away),
            ],
            key=lambda x: float(x[1] or 0),
        )
        ai_pick = f"{api_best[2]} Sieg" if api_best[0] != "draw" else "Unentschieden"
        reasons.append("API-Prognose")
    else:
        ai_pick = f"{fav_name} Sieg" if fav_key != "draw" else "Unentschieden"
        reasons.append(f"Niedrigste Quote {fav_odd:.2f}")

    if margin >= 12:
        confidence += 5

    confidence = max(35.0, min(92.0, confidence))

    if confidence < 60:
        no_bet = True
        ai_pick = "No Bet"
        risk = "Hoch"
    elif confidence < 70:
        no_bet = False
        risk = "Mittel"
    else:
        no_bet = False
        risk = "Value"
        value = True

    if no_bet:
        risk = "Hoch"

    return {
        "ai_pick": ai_pick,
        "confidence": round(confidence, 1),
        "no_bet": no_bet,
        "risk": risk,
        "value": value,
        "reasons": reasons[:3],
        "home_pct": home_pct,
        "draw_pct": draw_pct,
        "away_pct": away_pct,
    }


def filter_rows_with_odds(
    rows: list[dict[str, Any]],
    *,
    allow_no_odds: bool = False,
) -> list[dict[str, Any]]:
    if allow_no_odds:
        return list(rows or [])
    return [r for r in rows or [] if has_complete_odds(r)]


# ---------------------------------------------------------------------------
# Match detail helpers
# ---------------------------------------------------------------------------


def _fixture_league_id(fixture: dict[str, Any]) -> int | None:
    try:
        return int((fixture.get("league") or {}).get("id") or 0) or None
    except (TypeError, ValueError):
        return None


def _team_standing_row(standings_payload: list[dict[str, Any]], team_id: int) -> dict[str, Any] | None:
    if not standings_payload:
        return None
    try:
        groups = (standings_payload[0].get("league") or {}).get("standings") or []
        rows = groups[0] if groups else []
        for row in rows:
            tid = (row.get("team") or {}).get("id")
            if int(tid) == int(team_id):
                return row
    except (TypeError, ValueError, IndexError):
        return None
    return None


def _standing_summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    all_ = row.get("all") or {}
    goals = all_.get("goals") or {}
    try:
        return {
            "rank": row.get("rank"),
            "points": row.get("points"),
            "played": all_.get("played"),
            "goals_for": goals.get("for"),
            "goals_against": goals.get("against"),
            "goal_diff": row.get("goalsDiff"),
        }
    except (TypeError, ValueError):
        return None


def _form_from_fixtures(fixtures: list[dict[str, Any]], team_id: int) -> str:
    chars: list[str] = []
    for fx in fixtures[:5]:
        teams = fx.get("teams") or {}
        goals = fx.get("goals") or {}
        home = teams.get("home") or {}
        away = teams.get("away") or {}
        try:
            gh, ga = int(goals.get("home")), int(goals.get("away"))
        except (TypeError, ValueError):
            continue
        hid, aid = home.get("id"), away.get("id")
        if int(hid) == int(team_id):
            if gh > ga:
                chars.append("W")
            elif gh < ga:
                chars.append("L")
            else:
                chars.append("D")
        elif int(aid) == int(team_id):
            if ga > gh:
                chars.append("W")
            elif ga < gh:
                chars.append("L")
            else:
                chars.append("D")
    return " ".join(chars) if chars else "—"


def fetch_match_detail(
    service: FootballService,
    fixture_id: int,
    *,
    username: str,
    session_plan: str,
) -> dict[str, Any]:
    """Load match detail for analysis drawer — odds, standings, form, h2h, predictions."""
    rank = football_plan_rank(session_plan or "none")
    detail: dict[str, Any] = {
        "fixture_id": fixture_id,
        "missing": [],
        "plan": session_plan,
    }

    try:
        fixture = service.get_fixture(fixture_id, username=username)
    except FootballAPIError as exc:
        detail["error"] = str(exc)
        return detail
    if not fixture:
        detail["error"] = "Spiel nicht gefunden."
        return detail

    detail["card"] = parse_match_card(fixture)
    home_name, away_name = fixture_team_names(fixture)
    teams = fixture.get("teams") or {}
    home_id = (teams.get("home") or {}).get("id")
    away_id = (teams.get("away") or {}).get("id")
    league_id = _fixture_league_id(fixture)
    season = int((fixture.get("league") or {}).get("season") or FOOTBALL_DEFAULT_SEASON)

    pred_ins: dict[str, Any] = {}

    if rank >= 1:
        detail["summary"] = {
            "home": home_name,
            "away": away_name,
            "league": (fixture.get("league") or {}).get("name") or "",
            "venue": detail["card"].get("venue") or "",
        }
        if league_id:
            try:
                detail["standings"] = service.get_standings(
                    int(league_id), season=season, username=username
                )
            except FootballAPIError:
                detail["missing"].append("standings")
        if home_id:
            detail["home_standing"] = _team_standing_row(
                detail.get("standings") or [], int(home_id)
            )
            detail["home_standing_summary"] = _standing_summary(detail.get("home_standing"))
        if away_id:
            detail["away_standing"] = _team_standing_row(
                detail.get("standings") or [], int(away_id)
            )
            detail["away_standing_summary"] = _standing_summary(detail.get("away_standing"))

    premium_api = getattr(service, "premium_api_enabled", lambda: False)()

    if rank >= 1 and premium_api:
        try:
            detail["odds"] = get_odds_for_fixture(service, fixture_id, username=username)
        except FootballAPIError:
            detail["missing"].append("odds")
    elif rank >= 1:
        detail["odds_unavailable"] = True

    if home_id and away_id and rank >= 1:
        try:
            detail["home_form_fixtures"] = service.get_recent_fixtures(
                int(home_id), last_count=5, username=username
            )
            detail["away_form_fixtures"] = service.get_recent_fixtures(
                int(away_id), last_count=5, username=username
            )
            detail["home_form"] = _form_from_fixtures(
                detail.get("home_form_fixtures") or [], int(home_id)
            )
            detail["away_form"] = _form_from_fixtures(
                detail.get("away_form_fixtures") or [], int(away_id)
            )
        except FootballAPIError:
            detail["missing"].append("form")

        hf, af = detail.get("home_form"), detail.get("away_form")
        if (hf and str(hf).strip() != "—") or (af and str(af).strip() != "—"):
            detail["form"] = {"home": hf or "", "away": af or ""}

    if rank >= 2 and premium_api:
        try:
            pred_rows = service.get_fixture_predictions(fixture_id, username=username)
            detail["predictions"] = pred_rows
            if pred_rows:
                pred_ins = parse_prediction_insights(pred_rows[0])
                detail["prediction_insights"] = pred_ins
        except FootballAPIError:
            detail["missing"].append("predictions")

        for side, tid in (("home_injuries", home_id), ("away_injuries", away_id)):
            if tid:
                try:
                    detail[side] = service.get_team_injuries(int(tid), season=season, username=username)
                except FootballAPIError:
                    detail["missing"].append(side)

        if home_id and away_id:
            try:
                detail["h2h"] = service.get_head_to_head(
                    int(home_id), int(away_id), last_count=5, username=username
                )
            except FootballAPIError:
                detail["missing"].append("h2h")
    elif rank >= 2:
        detail["premium_data_unavailable"] = True

    has_odds = has_complete_odds(
        {
            "home_odd": (detail.get("odds") or {}).get("home"),
            "draw_odd": (detail.get("odds") or {}).get("draw"),
            "away_odd": (detail.get("odds") or {}).get("away"),
        }
    )
    has_standing = bool(
        detail.get("home_standing_summary") or detail.get("away_standing_summary")
    )
    hf = detail.get("home_form")
    af = detail.get("away_form")
    has_form = bool(
        (hf and str(hf).strip() not in ("", "—"))
        or (af and str(af).strip() not in ("", "—"))
    )
    detail["analysis_available"] = is_analysis_eligible(
        fixture_id=int(fixture_id),
        home=home_name,
        away=away_name,
        pred_insights=pred_ins,
        has_odds=has_odds,
        has_standing=has_standing,
        has_form=has_form,
    )

    return detail


# ---------------------------------------------------------------------------
# Board payload & fixture pools
# ---------------------------------------------------------------------------


def fetch_board_payload(
    service: FootballService,
    *,
    username: str,
    include_live: bool = False,
    include_raw: bool = False,
) -> dict[str, Any]:
    return fetch_premium_dashboard(
        service,
        username=username,
        include_live=include_live,
        include_raw=include_raw,
    )


MSG_NO_MATCHES = "Aktuell keine Spiele verfügbar. Bitte später erneut prüfen."


def _empty_topspiele_message(time_filter: str) -> str:
    tf = (time_filter or "heute").lower()
    if tf == "morgen":
        return "Morgen keine Topspiele verfügbar."
    if tf == "live":
        return "Keine Live-Topspiele verfügbar."
    return "Heute keine Topspiele verfügbar."


def _is_topspiele_league(fixture: dict[str, Any]) -> bool:
    try:
        lid = int((fixture.get("league") or {}).get("id") or 0)
    except (TypeError, ValueError):
        return False
    return lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS


def _filter_topspiele_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [fx for fx in fixtures or [] if _is_topspiele_league(fx)]


def _premium_fixtures_for_time(payload: dict[str, Any], time_filter: str) -> list[dict[str, Any]]:
    """Topspiele — strictly FOOTBALL_TOPSPIELE_LEAGUE_IDS only."""
    today_s = str(payload.get("today") or payload.get("today_local") or "")
    tf = (time_filter or "heute").lower()
    if tf == "live":
        pool = list(payload.get("live_now") or [])
    elif tf == "morgen":
        pool = list(payload.get("tomorrow_fixtures") or [])
    else:
        pool = list(payload.get("next_matches") or payload.get("all_premium") or [])
        if tf == "heute":
            pool = [fx for fx in pool if _is_live(fx) or _fixture_date(fx) == today_s]
    pool = _filter_topspiele_fixtures(pool)
    return sort_fixtures_by_priority(pool)[:FEED_CAP_DEFAULT]


def _raw_fixtures_for_time(payload: dict[str, Any], time_filter: str) -> list[dict[str, Any]]:
    today_s = str(payload.get("today") or payload.get("today_local") or "")
    tf = (time_filter or "heute").lower()
    raw_live = list(payload.get("raw_live") or [])
    raw_today = list(payload.get("raw_today") or [])
    raw_tomorrow = list(payload.get("raw_tomorrow") or [])
    if tf == "live":
        pool = raw_live
    elif tf == "morgen":
        pool = raw_tomorrow
    else:
        pool = dedupe_fixtures(raw_live + raw_today)
        if tf == "heute":
            pool = [fx for fx in pool if _is_live(fx) or _fixture_date(fx) == today_s]
    return sort_fixtures_by_priority(filter_blocked_fixtures(pool))


def _log_board_metrics(metrics: dict[str, Any]) -> None:
    try:
        from logger import log_info

        log_info(
            "Football board: "
            f"premium={metrics.get('premium_count')} "
            f"raw={metrics.get('raw_count')} "
            f"displayed={metrics.get('displayed_count')} "
            f"source={metrics.get('source')}",
            category="football",
        )
    except Exception:
        pass


def resolve_football_board(
    payload: dict[str, Any],
    service: FootballService,
    *,
    view_mode: str,
    time_filter: str,
    username: str,
    session_plan: str,
) -> dict[str, Any]:
    """Delegates to services.football_feed (strict Topspiele / raw API)."""
    from services.football_feed import resolve_football_feed

    return resolve_football_feed(
        payload,
        service,
        view_mode=view_mode,
        time_filter=time_filter,
        username=username,
        session_plan=session_plan,
        probe_analysis=str(view_mode).lower() != "raw",
    )


def _fixture_date(fixture: dict[str, Any]) -> str:
    return parse_match_card(fixture).get("date") or ""


def _is_live(fixture: dict[str, Any]) -> bool:
    st = str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "")
    return st in LIVE_STATUSES


def build_raw_board_rows(
    fixtures: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 48,
) -> list[dict[str, Any]]:
    """Minimal rows for raw mode — live scores only, no odds, no AI."""
    _ = service, username, session_plan, cache
    rows: list[dict[str, Any]] = []
    for fx in fixtures[:max_enrich]:
        card = parse_match_card(fx)
        fid = card.get("fixture_id")
        try:
            fid_int = int(fid) if fid is not None else None
        except (TypeError, ValueError):
            fid_int = None

        rows.append(
            {
                "fixture_id": fid_int,
                "card": card,
                "raw_mode": True,
                "analysis_available": False,
                "schedule_only": True,
            }
        )
    return rows


def build_basic_board_rows(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Starter plan — premium fixtures without odds API."""
    rows: list[dict[str, Any]] = []
    for fx in fixtures or []:
        card = parse_match_card(fx)
        rows.append(
            {
                "fixture_id": card.get("fixture_id"),
                "card": card,
                "schedule_only": True,
                "analysis_available": False,
                **empty_betting_signal(),
                "has_odds": False,
                "live_event": "",
                "momentum": "",
            }
        )
    return rows


def enrich_fixture_row(
    service: FootballService,
    fixture: dict[str, Any],
    *,
    username: str,
    rank: int,
    cache: dict[int, dict[str, Any]],
    schedule_only: bool = False,
) -> dict[str, Any]:
    card = parse_match_card(fixture)
    fid = card.get("fixture_id")
    try:
        fid_int = int(fid) if fid is not None else None
    except (TypeError, ValueError):
        fid_int = None

    if fid_int and fid_int in cache and not schedule_only:
        cached = cache[fid_int]
        if cached.get("schedule_only") == schedule_only:
            return cached

    row: dict[str, Any] = {
        "fixture_id": fid_int,
        "card": card,
        "schedule_only": schedule_only,
        "has_odds": False,
        "analysis_available": False,
        "live_event": "",
        "momentum": "",
        **empty_betting_signal(),
    }

    pred_insights: dict[str, Any] = {}
    home_name = str(card.get("home") or "Heim")
    away_name = str(card.get("away") or "Auswärts")
    # Analysis endpoints (odds/predictions/standings/injuries/h2h) are ONLY fetched on click.
    # So: show schedule-only rows on load.
    row["analysis_available"] = False

    if card.get("live"):
        rc = card.get("red_cards") or {}
        if isinstance(rc, dict) and rc.get("total"):
            row["live_event"] = f"Rote Karten: {rc.get('total')}"
        if card.get("live_xg"):
            row["momentum"] = f"xG {card.get('live_xg')}"

    if fid_int:
        cache[fid_int] = row
    return row
