"""Backward-compatible shim — use ui.football."""
from ui.football import render_football_betting_board  # noqa: F401

__all__ = ["render_football_betting_board"]
