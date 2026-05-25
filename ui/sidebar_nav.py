"""
Central sidebar navigation — same on every page (via ui.py → render_sidebar).
"""
from __future__ import annotations

# (section title, [(label, page_key), ...])
SIDEBAR_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Workspace",
        [
            ("Home", "home"),
            ("Chat", "chat"),
            ("Football", "football"),
            ("Dashboard", "dashboard"),
            ("Projects", "projects"),
            ("Automations", "automation_lab"),
        ],
    ),
    (
        "Studios",
        [
            ("Image", "image"),
            ("Video", "video"),
            ("Reels", "reels"),
            ("Music", "music"),
            ("Code", "coding"),
        ],
    ),
    (
        "Account",
        [
            ("Premium", "premium"),
            ("Redeem", "redeem"),
            ("Support", "support"),
        ],
    ),
]
