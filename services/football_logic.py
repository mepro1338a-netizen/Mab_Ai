"""Football business logic — board, loaders, curation."""
from services.football_board import (  # noqa: F401
    build_basic_board_rows,
    fetch_board_payload,
    fetch_match_detail,
    get_odds_for_fixture,
    resolve_football_board,
)
from services.football_loaders import (  # noqa: F401
    curate_feed_fixtures,
    fetch_premium_dashboard,
    filter_premium_fixtures,
    parse_match_card,
)

__all__ = [
    "build_basic_board_rows",
    "curate_feed_fixtures",
    "fetch_board_payload",
    "fetch_match_detail",
    "fetch_premium_dashboard",
    "filter_premium_fixtures",
    "get_odds_for_fixture",
    "parse_match_card",
    "resolve_football_board",
]
