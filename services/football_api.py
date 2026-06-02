"""Football API layer — thin re-export of football_service."""
from services.football_service import (  # noqa: F401
    FootballAPIError,
    FootballService,
    fixture_label,
    fixture_team_names,
    get_football_service,
)

__all__ = [
    "FootballAPIError",
    "FootballService",
    "fixture_label",
    "fixture_team_names",
    "get_football_service",
]
