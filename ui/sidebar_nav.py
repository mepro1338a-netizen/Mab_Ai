"""
MaByte SaaS OS — zentrale Sidebar-Navigation (via ui.py → render_sidebar).
"""
from __future__ import annotations

# (Sektion, [(Label, page_key), ...]) — Reihenfolge = Priorität für B2B-Nutzer
SIDEBAR_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Platform",
        [
            ("AI Dashboard", "home"),
            ("AI Chat", "chat"),
        ],
    ),
    (
        "Intelligence",
        [
            ("Football AI", "football"),
        ],
    ),
    (
        "Create",
        [
            ("Image", "image"),
            ("Video & Reels", "creator"),
            ("Music", "music"),
            ("Code", "coding"),
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

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "creator",
    "video": "creator",
}
