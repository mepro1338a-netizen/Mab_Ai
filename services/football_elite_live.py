"""
Elite Live Match Intelligence — aggregate API-Football data + AI synthesis.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from services.football_betting_intel import full_betting_analysis
from services.football_live_intel import live_fixture_snapshot, parse_fixture_statistics
from services.football_odds import parse_fixture_odds_payload, parse_prediction_insights
from services.football_service import FootballAPIError, FootballService, fixture_team_names


def _safe(fn: Callable[[], Any], default: Any = None) -> Any:
    try:
        return fn()
    except Exception:
        return default


def _parse_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for block in rows or []:
        for ev in block.get("events") or []:
            out.append({
                "minute": ev.get("time", {}).get("elapsed"),
                "extra": ev.get("time", {}).get("extra"),
                "team": (ev.get("team") or {}).get("name", ""),
                "player": (ev.get("player") or {}).get("name", ""),
                "assist": (ev.get("assist") or {}).get("name", ""),
                "type": ev.get("type", ""),
                "detail": ev.get("detail", ""),
            })
    out.sort(key=lambda x: (x.get("minute") or 0, x.get("extra") or 0))
    return out


def _parse_lineups(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {"home": [], "away": [], "formations": {}}
    for block in rows or []:
        team = (block.get("team") or {}).get("name") or "Team"
        side = "home" if not result["home"] else "away"
        result["formations"][team] = block.get("formation") or "—"
        starters = []
        for p in block.get("startXI") or []:
            pl = p.get("player") or {}
            starters.append({
                "name": pl.get("name", ""),
                "number": pl.get("number"),
                "pos": pl.get("pos", ""),
            })
        result[side] = starters[:11]
    return result


def _parse_injuries(rows: list[dict[str, Any]], home: str, away: str) -> dict[str, list[dict[str, str]]]:
    bucket: dict[str, list[dict[str, str]]] = {"home": [], "away": [], "unknown": []}
    for row in rows or []:
        player = (row.get("player") or {}).get("name") or "Spieler"
        team = (row.get("team") or {}).get("name") or ""
        reason = row.get("reason") or row.get("type") or "Ausfall"
        entry = {"player": player, "reason": str(reason), "team": team}
        if team == home:
            bucket["home"].append(entry)
        elif team == away:
            bucket["away"].append(entry)
        else:
            bucket["unknown"].append(entry)
    return bucket


def _h2h_summary(rows: list[dict[str, Any]], home: str, away: str) -> dict[str, Any]:
    if not rows:
        return {"total": 0, "home_wins": 0, "away_wins": 0, "draws": 0, "recent": []}
    hw = aw = dr = 0
    recent = []
    for fx in rows[:8]:
        teams = fx.get("teams") or {}
        goals = fx.get("goals") or {}
        h_name = (teams.get("home") or {}).get("name")
        a_name = (teams.get("away") or {}).get("name")
        gh, ga = goals.get("home"), goals.get("away")
        if gh is None or ga is None:
            continue
        try:
            gh_i, ga_i = int(gh), int(ga)
        except (TypeError, ValueError):
            continue
        recent.append(f"{h_name} {gh_i}-{ga_i} {a_name}")
        if h_name == home and a_name == away:
            if gh_i > ga_i:
                hw += 1
            elif gh_i < ga_i:
                aw += 1
            else:
                dr += 1
    return {
        "total": len(rows),
        "home_wins": hw,
        "away_wins": aw,
        "draws": dr,
        "recent": recent[:5],
    }


def _edge_reasons_heuristic(
    home: str,
    away: str,
    momentum: dict,
    prediction: dict,
    stats: dict,
    h2h: dict,
) -> list[dict[str, Any]]:
    reasons = []
    leader = momentum.get("leader")
    if leader and leader != "—":
        reasons.append({
            "team": leader,
            "reason": f"Live-Momentum ({momentum.get('label', '')})",
            "confidence": min(88, 55 + abs(float(momentum.get("score") or 0))),
        })
    hp, ap = prediction.get("home_pct"), prediction.get("away_pct")
    if hp is not None and ap is not None:
        if hp > ap + 5:
            reasons.append({
                "team": home,
                "reason": f"API-Prognose favorisiert Heim ({hp}% vs {ap}%)",
                "confidence": float(hp),
            })
        elif ap > hp + 5:
            reasons.append({
                "team": away,
                "reason": f"API-Prognose favorisiert Auswaerts ({ap}% vs {hp}%)",
                "confidence": float(ap),
            })
    h_stats = (stats or {}).get("home") or {}
    a_stats = (stats or {}).get("away") or {}
    if h_stats.get("shots_on") and a_stats.get("shots_on"):
        if float(h_stats["shots_on"]) > float(a_stats["shots_on"]) + 1:
            reasons.append({
                "team": home,
                "reason": "Mehr Schuesse aufs Tor (Live)",
                "confidence": 62.0,
            })
        elif float(a_stats["shots_on"]) > float(h_stats["shots_on"]) + 1:
            reasons.append({
                "team": away,
                "reason": "Mehr Schuesse aufs Tor (Live)",
                "confidence": 62.0,
            })
    if h2h.get("home_wins", 0) > h2h.get("away_wins", 0) + 1:
        reasons.append({
            "team": home,
            "reason": "Positiver H2H-Verlauf im Datensatz",
            "confidence": 58.0,
        })
    elif h2h.get("away_wins", 0) > h2h.get("home_wins", 0) + 1:
        reasons.append({
            "team": away,
            "reason": "Positiver H2H-Verlauf im Datensatz",
            "confidence": 58.0,
        })
    return reasons[:5]


def _creator_output_heuristic(home: str, away: str, overview: dict) -> dict[str, str]:
    score = overview.get("scoreline", "vs")
    return {
        "tiktok_hook": f"{home} vs {away} — das aendert ALLES gerade ({score})",
        "instagram_caption": f"Live: {home} {score} {away}. Speichern & Meinung in die Kommentare.",
        "youtube_title": f"{home} vs {away} LIVE Breakdown",
        "voiceover": f"Leute, {home} gegen {away} — und das Spiel kippt gerade. Hier ist warum.",
        "hashtags": f"#{home.replace(' ', '')} #{away.replace(' ', '')} #football #live #reels",
        "thumbnail": f"{home.upper()} VS {away.upper()}",
    }


def _final_read_heuristic(home: str, away: str, momentum: dict, events: list) -> dict[str, str]:
    n_goals = sum(1 for e in events if (e.get("type") or "").lower() == "goal")
    return {
        "summary": f"{home} vs {away}: {momentum.get('label', 'Offenes Spiel')} — {n_goals} Tore im Feed.",
        "next_likely": "Naechste Phase: Druck des fuehrenden Teams oder Konter des Underdogs.",
        "creator_angle": f"Reel: Momentum-Wendepunkt bei {momentum.get('leader', 'beiden Teams')}.",
        "risk_warning": "Keine Wettberatung — nur Live-Analyse fuer Creator & Analysten.",
    }


def _ai_enrich(context: str) -> dict[str, Any] | None:
    if not (OPENAI_API_KEY or "").strip():
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist MaByte Elite Football Intelligence. Antworte NUR mit validem JSON. "
                        "Keine Wettempfehlungen. Deutsch. Felder: edge_reasons (array team,reason,confidence), "
                        "key_players (array name,impact,reel_potential), creator (object), "
                        "final_read (object summary,next_likely,creator_angle,risk_warning)."
                    ),
                },
                {"role": "user", "content": context[:12000]},
            ],
            temperature=0.55,
            max_tokens=2200,
        )
        text = (resp.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return None


class EliteLiveIntelEngine:
    """Fetch + merge live fixture intelligence (cache via FootballService)."""

    def __init__(self, service: FootballService | None = None):
        self.service = service or FootballService()

    def fetch_bundle(self, fixture_id: int, *, username: str = "") -> dict[str, Any]:
        fid = int(fixture_id)
        missing: list[str] = []

        fixture_row = _safe(
            lambda: self.service.get_fixture(fid, username=username),
            None,
        )
        if not fixture_row:
            raise FootballAPIError("Spiel nicht gefunden.")

        home, away = fixture_team_names(fixture_row)
        teams = fixture_row.get("teams") or {}
        home_id = (teams.get("home") or {}).get("id")
        away_id = (teams.get("away") or {}).get("id")
        league = fixture_row.get("league") or {}
        snap = live_fixture_snapshot(fixture_row)

        stats_raw = _safe(lambda: self.service.get_fixture_statistics(fid, username=username), [])
        if not stats_raw:
            missing.append("statistics")
        stats = parse_fixture_statistics(stats_raw) if stats_raw else {"home": {}, "away": {}, "momentum": {}}

        events_raw = _safe(lambda: self.service.get_fixture_events(fid, username=username), [])
        if not events_raw:
            missing.append("events")
        events = _parse_events(events_raw)

        lineups_raw = _safe(lambda: self.service.get_fixture_lineups(fid, username=username), [])
        if not lineups_raw:
            missing.append("lineups")
        lineups = _parse_lineups(lineups_raw)

        pred_raw = _safe(lambda: self.service.get_fixture_predictions(fid, username=username), [])
        prediction = parse_prediction_insights(pred_raw[0]) if pred_raw else {}
        if not prediction:
            missing.append("predictions")

        injuries_raw: list[dict] = []
        if home_id:
            injuries_raw.extend(_safe(
                lambda: self.service.get_team_injuries(int(home_id), username=username),
                [],
            ) or [])
        if away_id:
            injuries_raw.extend(_safe(
                lambda: self.service.get_team_injuries(int(away_id), username=username),
                [],
            ) or [])
        injuries = _parse_injuries(injuries_raw, home, away)
        if not any(injuries.values()):
            missing.append("injuries")

        h2h_rows: list = []
        if home_id and away_id:
            h2h_rows = _safe(
                lambda: self.service.get_head_to_head(int(home_id), int(away_id), username=username),
                [],
            ) or []
        h2h = _h2h_summary(h2h_rows, home, away)
        if not h2h_rows:
            missing.append("h2h")

        odds_raw = _safe(lambda: self.service.get_fixture_odds(fid, username=username), [])
        markets = parse_fixture_odds_payload(odds_raw) if odds_raw else []
        if not markets:
            missing.append("odds")

        home_odd = 2.0
        for m in markets:
            if "match winner" in (m.get("market") or "").lower() and "home" in (m.get("selection") or "").lower():
                home_odd = float(m.get("odd") or home_odd)
                break
        ai_prob = float(prediction.get("home_pct") or 50.0)
        odds_intel = full_betting_analysis(home_odd, 10.0, ai_prob, markets=markets if markets else None)

        overview = {
            **snap,
            "league": league.get("name", ""),
            "country": league.get("country", ""),
            "momentum": stats.get("momentum") or {},
            "home_team": home,
            "away_team": away,
        }

        edge_reasons = _edge_reasons_heuristic(
            home, away, overview["momentum"], prediction, stats, h2h,
        )
        creator = _creator_output_heuristic(home, away, overview)
        final_read = _final_read_heuristic(home, away, overview["momentum"], events)

        ctx = json.dumps({
            "overview": overview,
            "stats": stats,
            "prediction": prediction,
            "events": events[-12:],
            "lineups": lineups,
            "injuries": injuries,
            "h2h": h2h,
            "odds_intel": {k: odds_intel.get(k) for k in (
                "implied_probability_pct", "edge_pct", "expected_value",
                "is_value_bet", "risk_level", "value_label",
            )},
        }, ensure_ascii=False)[:12000]

        ai = _ai_enrich(ctx)
        if ai:
            if ai.get("edge_reasons"):
                edge_reasons = ai["edge_reasons"][:5]
            key_players = ai.get("key_players") or []
            creator = {**creator, **(ai.get("creator") or {})}
            final_read = {**final_read, **(ai.get("final_read") or {})}
        else:
            key_players = _key_players_heuristic(lineups, events, home, away)

        tactical = _tactical_read(stats, events)

        return {
            "fixture_id": fid,
            "overview": overview,
            "edge_reasons": edge_reasons,
            "injuries": injuries,
            "tactical": tactical,
            "key_players": key_players,
            "odds_intel": odds_intel,
            "creator": creator,
            "final_read": final_read,
            "events": events,
            "h2h": h2h,
            "form": {
                "home": prediction.get("form_home", ""),
                "away": prediction.get("form_away", ""),
            },
            "prediction": prediction,
            "missing_sections": missing,
            "partial": bool(missing),
        }


def _key_players_heuristic(lineups: dict, events: list, home: str, away: str) -> list[dict[str, str]]:
    scorers = [e.get("player") for e in events if (e.get("type") or "").lower() == "goal" and e.get("player")]
    cards = [e.get("player") for e in events if (e.get("type") or "").lower() == "card" and e.get("player")]
    picks = []
    for name in scorers[:2]:
        picks.append({"name": name, "impact": "Tor-Impact Live", "reel_potential": "Hoch"})
    for name in cards[:1]:
        picks.append({"name": name, "impact": "Disziplin-Risiko", "reel_potential": "Mittel"})
    if not picks:
        for side_key in ("home", "away"):
            for p in (lineups.get(side_key) or [])[:2]:
                picks.append({
                    "name": p.get("name", ""),
                    "impact": f"Starter ({side_key})",
                    "reel_potential": "Beobachten",
                })
    return picks[:5]


def _tactical_read(stats: dict, events: list) -> dict[str, Any]:
    h = stats.get("home") or {}
    a = stats.get("away") or {}
    cards = sum(1 for e in events if (e.get("type") or "").lower() == "card")
    subs = sum(1 for e in events if (e.get("type") or "").lower() == "subst")
    goals = sum(1 for e in events if (e.get("type") or "").lower() == "goal")
    return {
        "possession_home": h.get("possession"),
        "possession_away": a.get("possession"),
        "shots_home": h.get("shots"),
        "shots_away": a.get("shots"),
        "shots_on_home": h.get("shots_on"),
        "shots_on_away": a.get("shots_on"),
        "corners_home": h.get("corners"),
        "corners_away": a.get("corners"),
        "dangerous_home": h.get("dangerous"),
        "dangerous_away": a.get("dangerous"),
        "cards": cards,
        "substitutions": subs,
        "goals": goals,
        "danger_phase": "Hoch" if (h.get("dangerous") or 0) and (a.get("dangerous") or 0) else "Moderat",
    }


def pro_preview_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Reduced intel for Football Pro."""
    return {
        "overview": bundle.get("overview") or {},
        "edge_reasons": (bundle.get("edge_reasons") or [])[:2],
        "tactical": {
            k: bundle.get("tactical", {}).get(k)
            for k in ("possession_home", "possession_away", "shots_on_home", "shots_on_away", "goals")
        },
        "events": (bundle.get("events") or [])[-5:],
        "final_read": {
            "summary": (bundle.get("final_read") or {}).get("summary", ""),
            "risk_warning": "Vollstaendige Elite Live Intelligence — Upgrade auf Football Elite.",
        },
        "is_preview": True,
    }
