"""Unit tests for match analysis section builder (no API)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.football_live_intel import parse_xg_from_statistics
from services.football_match_intel import build_match_analysis_sections


def test_xg_parser() -> None:
    rows = [
        {
            "team": {"name": "Bayern"},
            "statistics": [{"type": "Expected Goals", "value": "1.42"}],
        },
        {
            "team": {"name": "Dortmund"},
            "statistics": [{"type": "Expected Goals", "value": "0.88"}],
        },
    ]
    xg = parse_xg_from_statistics(rows)
    assert xg is not None
    assert xg["home_xg"] == 1.42
    assert xg["away_xg"] == 0.88
    assert xg["total_xg"] == 2.3


def test_sections_only_real_data() -> None:
    detail = {
        "card": {"home": "A", "away": "B"},
        "prediction_insights": {"home_pct": 55.0, "draw_pct": 25.0, "away_pct": 20.0},
        "home_form": "W W D",
        "away_form": "L D W",
        "h2h": [],
        "home_injuries": [],
        "away_injuries": [],
    }
    intel = {
        "recommendation": {"main_pick": "A gewinnt", "confidence": 62.0},
        "reasons_full": ["Form stark"],
    }
    sections = build_match_analysis_sections(detail, intel)
    assert "prediction" in sections
    assert "confidence" in sections
    assert "form" in sections
    assert "best_bet" in sections
    assert "reasoning" in sections
    assert "h2h" not in sections
    assert "xg" not in sections
    assert "injuries" not in sections


def test_prediction_engine() -> None:
    from services.football_prediction_engine import build_match_prediction

    detail = {
        "card": {"home": "Arsenal", "away": "PSG", "live": False},
        "prediction_insights": {"home_pct": 58.0, "draw_pct": 22.0, "away_pct": 20.0},
        "home_form": "W W W D W",
        "away_form": "L D W L D",
        "home_standing_summary": {"rank": 2, "goals_for": 45, "goals_against": 18, "points": 52, "played": 20},
        "away_standing_summary": {"rank": 4, "goals_for": 38, "goals_against": 25, "points": 44, "played": 20},
        "injuries_parsed": {"available": True, "home_impact": "niedrig", "away_impact": "hoch", "home": [], "away": [{"player": "Defender", "reason": "Suspended"}]},
        "suspensions_parsed": {"available": True, "home": [], "away": [{"player": "Defender", "reason": "Suspended"}]},
        "xg": {"home_xg": 1.8, "away_xg": 1.1},
    }
    pred = build_match_prediction(detail)
    assert pred["outcome"] in ("Heimsieg", "Unentschieden", "Auswärtssieg")
    assert pred["best_bet"]
    assert len(pred["reasons"]) >= 3


def main() -> int:
    test_xg_parser()
    test_sections_only_real_data()
    test_prediction_engine()
    print("OK — football_match_intel tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
