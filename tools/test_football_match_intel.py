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


def main() -> int:
    test_xg_parser()
    test_sections_only_real_data()
    print("OK — football_match_intel tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
