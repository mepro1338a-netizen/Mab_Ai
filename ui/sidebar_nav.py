"""
MaByte SaaS OS — zentrale Sidebar-Navigation (via ui.py → render_sidebar).
"""
from __future__ import annotations

# (Sektion, [(Label, page_key), ...])
SIDEBAR_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "MaByte OS",
        [
            ("Home", "home"),
            ("AI Chat", "chat"),
        ],
    ),
    (
        "Creator",
        [
            ("Image", "image"),
            ("Shorts & Video", "creator"),
            ("Music", "music"),
            ("Code", "coding"),
        ],
    ),
    (
        "Intelligence",
        [
            ("Football AI", "football"),
        ],
    ),
    (
        "Workspace",
        [
            ("Projects", "projects"),
            ("Automations", "automation_lab"),
        ],
    ),
    (
        "Account",
        [
            ("Profil & Tokens", "dashboard"),
            ("Premium", "premium"),
            ("Support", "support"),
            ("Code einlösen", "redeem"),
        ],
    ),
]

# Legacy page keys → Creator Studio (Bookmarks / alte Links)
LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "creator",
    "video": "creator",
}
