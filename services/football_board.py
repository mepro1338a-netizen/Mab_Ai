"""Betting board — fixtures, odds, signals, match detail (merged board layer)."""
from __future__ import annotations

from typing import Any

from config import (
    FOOTBALL_DEFAULT_SEASON,
    FOOTBALL_UPCOMING_HORIZON_DAYS,
    football_plan_rank,
)
from services.football_loaders import (
    LIVE_STATUSES,
    _local_today_tomorrow,
    dedupe_fixtures,
    fetch_premium_dashboard,
    filter_betting_core_fixtures,
    filter_blocked_fixtures,
    parse_match_card,
    sort_fixtures_by_priority,
)
from services.football_service import FootballAPIError, FootballService, fixture_team_names

# ---------------------------------------------------------------------------
# Region filters (minimal, fixed set)
# ---------------------------------------------------------------------------

REGION_FILTERS: tuple[tuple[str, str], ...] = (
    ("alle", "Alle"),
    ("deutschland", "Deutschland"),
    ("uefa", "UEFA"),
    ("topligen", "Topligen"),
    ("intl", "WM & Euro"),
)

_REGION_IDS: dict[str, frozenset[int]] = {
    "deutschland": frozenset({78, 79, 81}),
    "uefa": frozenset({2, 3, 848}),
    "topligen": frozenset({39, 140, 135, 61}),
    "intl": frozenset({1, 4}),
}

LEAGUE_DISPLAY_ORDER: tuple[int, ...] = (
    78, 79, 81, 2, 3, 848, 39, 140, 135, 61, 1, 4,
)


def filter_fixtures_by_region(
    fixtures: list[dict[str, Any]],
    *,
    region_filter: str,
) -> list[dict[str, Any]]:
    key = (region_filter or "alle").lower().strip()
    if key in ("", "alle"):
        return list(fixtures or [])
    ids = _REGION_IDS.get(key)
    if not ids:
        return list(fixtures or [])
    out: list[dict[str, Any]] = []
    for fx in fixtures or []:
        try:
            lid = int((fx.get("league") or {}).get("id") or 0)
        except (TypeError, ValueError):
            continue
        if lid in ids:
            out.append(fx)
    return out

# ---------------------------------------------------------------------------
# Odds (from football_odds)
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
    """Fetch 1X2 odds via API-Football GET /odds?fixture=ID."""
    try:
        raw = service.get_fixture_odds(int(fixture_id), username=username)
        markets = parse_fixture_odds_payload(raw)
        return extract_1x2_odds(markets)
    except FootballAPIError:
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
    """Analysis only when fixture, teams, (form|standing), and (odds|prediction) exist."""
    if not fixture_id:
        return False
    if not str(home or "").strip() or not str(away or "").strip():
        return False
    form_or_standing = has_standing or has_form or _has_form_data(pred_insights)
    if not form_or_standing:
        return False
    if not (has_odds or _has_prediction_data(pred_insights)):
        return False
    return True


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

    if rank >= 2:
        try:
            pred_rows = service.get_fixture_predictions(fixture_id, username=username)
            detail["predictions"] = pred_rows
            if pred_rows:
                pred_ins = parse_prediction_insights(pred_rows[0])
                detail["prediction_insights"] = pred_ins
        except FootballAPIError:
            detail["missing"].append("predictions")

        # Injuries (on-demand only; can be rate-limited)
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

        o1x2 = get_odds_for_fixture(service, fixture_id, username=username)
        detail["odds"] = o1x2

        hf, af = detail.get("home_form"), detail.get("away_form")
        if (hf and str(hf).strip() != "—") or (af and str(af).strip() != "—"):
            detail["form"] = {"home": hf or "", "away": af or ""}

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
) -> dict[str, Any]:
    # Default premium page-load must do ONE request (premium upcoming, cached).
    # Live fixtures are optional and only loaded when the user opens the Live tab.
    return fetch_premium_dashboard(service, username=username, include_live=include_live)


def _fixture_date(fixture: dict[str, Any]) -> str:
    return parse_match_card(fixture).get("date") or ""


def _is_live(fixture: dict[str, Any]) -> bool:
    st = str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "")
    return st in LIVE_STATUSES


def collect_fixtures_for_filters(
    payload: dict[str, Any],
    *,
    time_filter: str,
    region_filter: str,
) -> list[dict[str, Any]]:
    """Premium fixtures only — strict ID whitelist + minimal region filter."""
    today_s = str(payload.get("today") or payload.get("today_local") or "")

    if time_filter == "live":
        pool = list(payload.get("live_now") or [])
    elif time_filter == "morgen":
        pool = list(payload.get("tomorrow_fixtures") or [])
    elif time_filter == "upcoming":
        pool = list(payload.get("next_matches") or [])
    elif time_filter == "alle":
        pool = dedupe_fixtures(
            list(payload.get("live_now") or [])
            + list(payload.get("next_matches") or payload.get("all_premium") or [])
        )
    else:
        # heute: nur heutige Topspiele (+ laufende)
        pool = list(payload.get("next_matches") or payload.get("all_premium") or [])
        pool = [
            fx
            for fx in pool
            if _is_live(fx) or _fixture_date(fx) == today_s
        ]

    pool = filter_betting_core_fixtures(pool)
    pool = filter_fixtures_by_region(pool, region_filter=region_filter)
    return sort_fixtures_by_priority(pool)


def collect_raw_fixtures_for_filters(
    payload: dict[str, Any],
    *,
    time_filter: str,
) -> list[dict[str, Any]]:
    """All API fixtures for time window — youth/reserve names blocked only."""
    today_s = str(payload.get("today") or payload.get("today_local") or "")
    raw_live = list(payload.get("raw_live") or [])
    raw_today = list(payload.get("raw_today") or [])
    raw_tomorrow = list(payload.get("raw_tomorrow") or [])

    if time_filter == "live":
        pool = raw_live
    elif time_filter == "morgen":
        pool = raw_tomorrow
    elif time_filter == "alle":
        pool = dedupe_fixtures(raw_live + raw_today + raw_tomorrow)
    else:
        pool = dedupe_fixtures(raw_live + raw_today)
        if time_filter == "heute":
            pool = [
                fx
                for fx in pool
                if _is_live(fx) or _fixture_date(fx) == today_s
            ]

    pool = filter_blocked_fixtures(pool)
    return sort_fixtures_by_priority(pool)


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


def load_raw_football_matches(
    payload: dict[str, Any],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    mode: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 48,
) -> dict[str, Any]:
    """Raw API fixtures for today only (fixtures?date=today) — no premium filter."""
    _ = mode
    today_s = str(payload.get("today") or payload.get("today_local") or "") or _local_today_tomorrow()[0]
    # Raw is on-demand (not loaded on page load).
    fixtures = filter_blocked_fixtures(service.get_fixtures_by_date(today_s, username=username))
    fixtures = sort_fixtures_by_priority(fixtures)
    rows = build_raw_board_rows(
        fixtures,
        service,
        username=username,
        session_plan=session_plan,
        cache=cache,
        max_enrich=max_enrich,
    )
    return {
        "fixtures": fixtures[:max_enrich],
        "rows": rows,
        "stage": "raw_all",
        "banner": None,
        "raw_mode": True,
        "pool_key": "raw_api_today",
        "selected_source": "raw_api_today",
        "pools": {"raw": len(fixtures)},
    }


def compute_football_board_metrics(
    payload: dict[str, Any],
    match_result: dict[str, Any],
    *,
    show_raw: bool,
    time_filter: str,
    region_filter: str,
) -> dict[str, Any]:
    """Exact source counts for Football AI board diagnostics."""
    premium_count = int(
        payload.get("premium_count") or len(payload.get("all_premium") or payload.get("next_matches") or [])
    )
    raw_live_count = int(
        payload.get("raw_live_count") or len(payload.get("raw_live") or [])
    )
    raw_today_count = int(
        payload.get("raw_today_count") or len(payload.get("raw_today") or [])
    )
    raw_tomorrow_count = int(
        payload.get("raw_tomorrow_count") or len(payload.get("raw_tomorrow") or [])
    )
    if show_raw:
        raw_today_count = max(
            raw_today_count,
            int((match_result.get("pools") or {}).get("raw") or 0),
        )
    displayed_count = len(match_result.get("rows") or [])
    selected_source = str(
        match_result.get("selected_source")
        or match_result.get("pool_key")
        or match_result.get("stage")
        or ("raw_api_today" if show_raw else "none")
    )
    return {
        "premium_count": premium_count,
        "raw_today_count": raw_today_count,
        "raw_live_count": raw_live_count,
        "raw_tomorrow_count": raw_tomorrow_count,
        "displayed_count": displayed_count,
        "selected_source": selected_source,
        "time_filter": time_filter,
        "region_filter": region_filter,
        "view_mode": "raw_api" if show_raw else "premium",
        "pools": match_result.get("pools") or {},
    }


_FALLBACK_MESSAGES: dict[str, str] = {
    "today_premium_with_odds": "Heute keine Spiele – nächste Topspiele.",
    "tomorrow_premium_with_odds": "Keine Spiele im Filter – nächste Topspiele.",
    "upcoming_premium_with_odds": f"Nächste Topspiele (kommende {FOOTBALL_UPCOMING_HORIZON_DAYS} Tage).",
    "today_premium_schedule": "Heute keine Spiele – nächste Topspiele.",
    "tomorrow_premium_schedule": "Keine Spiele im Filter – nächste Topspiele.",
    "upcoming_premium_schedule": f"Nächste Topspiele (kommende {FOOTBALL_UPCOMING_HORIZON_DAYS} Tage).",
    "live_empty": "Keine Live-Topspiele – nächste Topspiele.",
    "filter_empty_upcoming": (
        "Aktuell keine Spiele im gewählten Filter. Nächste Topspiele werden geladen."
    ),
    "api_plan_no_betting": "Quoten aktuell nicht verfügbar.",
}


def _fallback_chain(
    mode: str,
    *,
    today_empty: bool = False,
    live_empty: bool = True,
) -> list[tuple[str, str, bool]]:
    """Return (stage_id, pool_key, require_odds) in priority order."""
    heute_when_empty = [
        ("upcoming_premium_with_odds", "upcoming", True),
        ("upcoming_premium_schedule", "upcoming", False),
    ]
    heute_default = [
        ("today_premium_with_odds", "today", True),
        ("today_premium_schedule", "today", False),
        ("upcoming_premium_with_odds", "upcoming", True),
        ("upcoming_premium_schedule", "upcoming", False),
    ]
    chains: dict[str, list[tuple[str, str, bool]]] = {
        "upcoming": [
            ("upcoming_premium_with_odds", "upcoming", True),
            ("upcoming_premium_schedule", "upcoming", False),
        ],
        "live": [
            ("live_premium_with_odds", "live", True),
            ("live_premium_schedule", "live", False),
            ("upcoming_premium_with_odds", "upcoming", True),
            ("upcoming_premium_schedule", "upcoming", False),
        ],
        "heute": heute_when_empty if (today_empty and live_empty) else heute_default,
        "morgen": [
            ("tomorrow_premium_with_odds", "tomorrow", True),
            ("today_premium_with_odds", "today", True),
            ("upcoming_premium_with_odds", "upcoming", True),
            ("tomorrow_premium_schedule", "tomorrow", False),
            ("today_premium_schedule", "today", False),
            ("upcoming_premium_schedule", "upcoming", False),
        ],
        "alle": [
            ("live_premium_with_odds", "live", True),
            ("today_premium_with_odds", "today", True),
            ("tomorrow_premium_with_odds", "tomorrow", True),
            ("upcoming_premium_with_odds", "upcoming", True),
            ("today_premium_schedule", "today", False),
            ("tomorrow_premium_schedule", "tomorrow", False),
            ("upcoming_premium_schedule", "upcoming", False),
        ],
    }
    return chains.get((mode or "upcoming").lower(), chains["upcoming"])


def build_board_rows(
    fixtures: list[dict[str, Any]],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 24,
    allow_no_odds: bool = False,
    schedule_only: bool = False,
) -> list[dict[str, Any]]:
    rank = football_plan_rank(session_plan or "none")
    if rank < 2:
        return build_basic_board_rows(fixtures[:max_enrich])

    rows: list[dict[str, Any]] = []
    for fx in fixtures[:max_enrich]:
        rows.append(
            enrich_fixture_row(
                service,
                fx,
                username=username,
                rank=rank,
                cache=cache,
                # Strict: no odds/predictions on page load. Analysis endpoints are on-demand.
                schedule_only=True,
            )
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


def load_football_matches(
    payload: dict[str, Any],
    service: FootballService,
    *,
    username: str,
    session_plan: str,
    mode: str,
    region_filter: str,
    cache: dict[int, dict[str, Any]],
    max_enrich: int = 24,
) -> dict[str, Any]:
    """
    Premium fallback pipeline — never return empty while premium fixtures exist.
    """
    mode = (mode or "upcoming").lower().strip()

    def _build_pools(region: str) -> dict[str, list[dict[str, Any]]]:
        return {
            "live": collect_fixtures_for_filters(payload, time_filter="live", region_filter=region),
            "today": collect_fixtures_for_filters(payload, time_filter="heute", region_filter=region),
            "tomorrow": collect_fixtures_for_filters(payload, time_filter="morgen", region_filter=region),
            "upcoming": collect_fixtures_for_filters(payload, time_filter="upcoming", region_filter=region),
        }

    pools = _build_pools(region_filter)
    region_banner: str | None = None
    if region_filter not in ("", "alle") and not any(pools.values()):
        alt = _build_pools("alle")
        if any(alt.values()):
            pools = alt
            region_banner = "Keine Spiele in dieser Region — alle Top-Ligen."

    today_empty = not pools.get("today")
    live_empty = not pools.get("live")
    chain = _fallback_chain(mode, today_empty=today_empty, live_empty=live_empty)

    enrich_limit = 48 if any(p == "upcoming" for _, p, _ in chain[:3]) else max_enrich

    for stage_id, pool_key, require_odds in chain:
        fixtures = pools.get(pool_key) or []
        if not fixtures:
            continue

        row_limit = enrich_limit if pool_key == "upcoming" else max_enrich
        rows = build_board_rows(
            fixtures,
            service,
            username=username,
            session_plan=session_plan,
            cache=cache,
            max_enrich=row_limit,
            allow_no_odds=True,
            schedule_only=True,
        )
        if not rows:
            continue

        primary_stage = chain[0][0] if chain else ""
        banner = region_banner
        if stage_id != primary_stage:
            banner = banner or _FALLBACK_MESSAGES.get(stage_id)
        if not banner:
            banner = _FALLBACK_MESSAGES.get(stage_id) or _FALLBACK_MESSAGES["api_plan_no_betting"]

        return {
            "fixtures": fixtures[:row_limit],
            "rows": rows,
            "stage": stage_id,
            "banner": banner,
            "pool_key": pool_key,
            "selected_source": pool_key,
            "require_odds": require_odds,
            "pools": {k: len(v) for k, v in pools.items()},
        }

    api_errors = [str(e) for e in (payload.get("errors") or []) if str(e).strip()]
    banner = _FALLBACK_MESSAGES["filter_empty_upcoming"]
    if api_errors:
        banner = api_errors[0]
    elif int(payload.get("premium_count") or 0) <= 0:
        banner = (
            "Keine Topspiele geladen. API-Key oder Saison prüfen — "
            "Bundesliga, UEFA & WM erscheinen nach erfolgreichem Abruf."
        )

    return {
        "fixtures": [],
        "rows": [],
        "stage": "clean_empty_state",
        "banner": banner,
        "pool_key": "",
        "selected_source": "clean_empty_state",
        "require_odds": True,
        "pools": {k: len(v) for k, v in pools.items()},
    }


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
