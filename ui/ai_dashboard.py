"""Backward-compatible shim — use ui.dashboard and ui.components."""
from ui.components import (  # noqa: F401
    format_num,
    inject_dashboard_css,
    nav,
    render_daily_limits,
    render_header,
    render_recent_activity,
    render_stats,
)
from ui.dashboard import render_home  # noqa: F401

__all__ = [
    "format_num",
    "inject_dashboard_css",
    "nav",
    "render_daily_limits",
    "render_header",
    "render_home",
    "render_recent_activity",
    "render_stats",
]
