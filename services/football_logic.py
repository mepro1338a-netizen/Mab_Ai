"""Football business logic — feed resolution + board helpers."""
from services.football_board import fetch_match_detail  # noqa: F401
from services.football_feed import (  # noqa: F401
    fetch_board_payload,
    filter_topspiele_fixtures,
    is_topspiele_fixture,
    resolve_all_api_board,
    resolve_football_feed,
    resolve_topspiele_board,
)
from services.football_loaders import parse_match_card  # noqa: F401


def resolve_football_board(
    payload,
    service,
    *,
    view_mode: str,
    time_filter: str,
    username: str,
    session_plan: str,
) -> dict:
    """Compat shim — delegates to football_feed."""
    return resolve_football_feed(
        payload,
        service,
        view_mode=view_mode,
        time_filter=time_filter,
        username=username,
        session_plan=session_plan,
        probe_analysis=str(view_mode).lower() != "raw",
    )


__all__ = [
    "fetch_board_payload",
    "fetch_match_detail",
    "filter_topspiele_fixtures",
    "is_topspiele_fixture",
    "parse_match_card",
    "resolve_all_api_board",
    "resolve_football_board",
    "resolve_football_feed",
    "resolve_topspiele_board",
]
