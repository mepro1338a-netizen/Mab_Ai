"""MaByte — flat sidebar navigation (single source of truth)."""
from __future__ import annotations

SIDEBAR_NAV_ITEMS: list[tuple[str, str]] = [
    ("Dashboard", "home"),
    ("Chat", "chat"),
    ("Football AI", "football"),
    ("Image", "image"),
    ("Video", "video"),
    ("Music", "music"),
    ("Code", "coding"),
    ("Projects", "projects"),
    ("Automations", "automation_lab"),
    ("Profile", "dashboard"),
    ("Premium", "premium"),
]

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "video",
    "creator": "video",
    "automations": "automation_lab",
}
